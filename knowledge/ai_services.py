from dataclasses import dataclass, field
from typing import Any

from accounts.models import CompanyProfile, Tenant
from dpia.models import DPIA
from legal.models import LegalAssessment
from processing.models import ProcessingActivity

from .models import (
    AnalyseText,
    AnalyseTextTopic,
    KnowledgeEntry,
    TextTemplate,
    TrustedSource,
)


TOPIC_TO_ANALYSE_TEXT = {
    "legitimate_interest": AnalyseTextTopic.LEGITIMATE_INTEREST,
    "dpia": AnalyseTextTopic.DPIA,
    "legal_assessment": AnalyseTextTopic.LEGAL_ASSESSMENT,
    "template": AnalyseTextTopic.TEMPLATE,
    "general": AnalyseTextTopic.GENERAL,
}


TOPIC_LABELS = {
    "legitimate_interest": "Interessenabwägung",
    "dpia": "DSFA",
    "legal_assessment": "Rechtsbewertung",
    "template": "Mustertext",
    "general": "Allgemein",
}


@dataclass
class AIContextBundle:
    topic: str
    topic_label: str
    tenant: Tenant | None = None
    company_profile: CompanyProfile | None = None
    processing_activity: ProcessingActivity | None = None
    legal_assessment: LegalAssessment | None = None
    dpia: DPIA | None = None
    analyse_texts: list[AnalyseText] = field(default_factory=list)
    knowledge_entries: list[KnowledgeEntry] = field(default_factory=list)
    text_templates: list[TextTemplate] = field(default_factory=list)
    trusted_sources: list[TrustedSource] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "topic_label": self.topic_label,
            "tenant": self.tenant,
            "company_profile": self.company_profile,
            "processing_activity": self.processing_activity,
            "legal_assessment": self.legal_assessment,
            "dpia": self.dpia,
            "analyse_texts": self.analyse_texts,
            "knowledge_entries": self.knowledge_entries,
            "text_templates": self.text_templates,
            "trusted_sources": self.trusted_sources,
        }


def get_company_profile_context(tenant: Tenant | None) -> CompanyProfile | None:
    if tenant is None:
        return None

    try:
        return CompanyProfile.objects.get(tenant=tenant)
    except CompanyProfile.DoesNotExist:
        return None


def get_analysis_texts_for_topic(topic: str) -> list[AnalyseText]:
    analyse_topic = TOPIC_TO_ANALYSE_TEXT.get(topic, AnalyseTextTopic.GENERAL)

    return list(
        AnalyseText.objects.filter(
            topic=analyse_topic,
            is_active=True,
            ai_enabled=True,
        ).order_by("title")
    )


def get_knowledge_entries_for_topic(topic: str) -> list[KnowledgeEntry]:
    qs = KnowledgeEntry.objects.filter(
        is_active=True,
        allowed_for_ai=True,
    ).order_by("category", "title")

    if topic == "dpia":
        qs = qs.filter(category__in=["dpia_guidance", "assessment_scheme", "general"])
    elif topic in ["legitimate_interest", "legal_assessment"]:
        qs = qs.filter(category__in=["legal_guidance", "assessment_scheme", "general"])
    else:
        qs = qs.filter(category__in=["general", "internal_policy", "assessment_scheme"])

    return list(qs)


def get_text_templates_for_topic(topic: str) -> list[TextTemplate]:
    qs = TextTemplate.objects.filter(
        is_active=True,
        allowed_for_ai=True,
    ).order_by("category", "title")

    if topic == "dpia":
        qs = qs.filter(category__in=["dpia", "general"])
    else:
        qs = qs.filter(category="general")

    return list(qs)


def get_trusted_sources_for_topic(topic: str) -> list[TrustedSource]:
    qs = TrustedSource.objects.filter(
        is_active=True,
        allowed_for_ai=True,
    ).order_by("priority", "title")

    return list(qs)


def infer_tenant(
    *,
    tenant: Tenant | None = None,
    processing_activity: ProcessingActivity | None = None,
    legal_assessment: LegalAssessment | None = None,
    dpia: DPIA | None = None,
) -> Tenant | None:
    if tenant is not None:
        return tenant

    if processing_activity is not None and getattr(processing_activity, "tenant", None):
        return processing_activity.tenant

    if legal_assessment is not None and getattr(legal_assessment, "tenant", None):
        return legal_assessment.tenant

    if dpia is not None and getattr(dpia.processing_activity, "tenant", None):
        return dpia.processing_activity.tenant

    return None


def build_ai_context_bundle(
    *,
    topic: str,
    tenant: Tenant | None = None,
    processing_activity: ProcessingActivity | None = None,
    legal_assessment: LegalAssessment | None = None,
    dpia: DPIA | None = None,
) -> AIContextBundle:
    resolved_tenant = infer_tenant(
        tenant=tenant,
        processing_activity=processing_activity,
        legal_assessment=legal_assessment,
        dpia=dpia,
    )

    return AIContextBundle(
        topic=topic,
        topic_label=TOPIC_LABELS.get(topic, "Allgemein"),
        tenant=resolved_tenant,
        company_profile=get_company_profile_context(resolved_tenant),
        processing_activity=processing_activity,
        legal_assessment=legal_assessment,
        dpia=dpia,
        analyse_texts=get_analysis_texts_for_topic(topic),
        knowledge_entries=get_knowledge_entries_for_topic(topic),
        text_templates=get_text_templates_for_topic(topic),
        trusted_sources=get_trusted_sources_for_topic(topic),
    )

def build_context_text(bundle: AIContextBundle) -> str:
    sections = []

    p = getattr(bundle, "processing_activity", None)
    l = getattr(bundle, "legal_assessment", None)

    if p:
        processing_lines = [
            "## Verarbeitungsvorgang",
            f"- Titel: {(p.title or '—').strip()}",
            f"- Zweck: {(p.purpose or '—').strip()}",
            f"- Beschreibung: {(p.description or '—').strip()}",
            f"- Betroffene Personen: {(p.data_subject_categories or '—').strip()}",
            f"- Datenkategorien: {(p.personal_data_categories or '—').strip()}",
            f"- Systeme: {(p.systems_used or '—').strip()}",
        ]
        sections.append("\n".join(processing_lines))

    if l:
        dpia_required = False
        dpia_status_label = "Noch nicht geprüft"

        processing = getattr(l, "processing_activity", None)
        if processing:
            dpia_required = bool(getattr(processing, "dpia_required", False))

            dpia_check = getattr(processing, "dpia_check", None)
            if dpia_check:
                dpia_status_label = dpia_check.recommendation_label

        legal_lines = [
            "## Rechtliche Bewertung",
            f"- Art. 6 DSGVO: {l.get_legal_basis_display() if l.legal_basis else '—'}",
            f"- Art. 9 DSGVO: {l.get_special_legal_basis_display() if l.special_legal_basis else '—'}",
            f"- DSFA erforderlich: {'Ja' if dpia_required else 'Nein'}",
            f"- DSFA-Status: {dpia_status_label}",
            f"- Bewertung: {(l.legal_assessment_text or '—').strip()}",
        ]
        sections.append("\n".join(legal_lines))

    return "\n\n".join(sections)

def build_ai_prompt_stub(
    *,
    topic: str,
    target_label: str,
    tenant: Tenant | None = None,
    processing_activity: ProcessingActivity | None = None,
    legal_assessment: LegalAssessment | None = None,
    dpia: DPIA | None = None,
) -> str:
    bundle = build_ai_context_bundle(
        topic=topic,
        tenant=tenant,
        processing_activity=processing_activity,
        legal_assessment=legal_assessment,
        dpia=dpia,
    )
    context_text = build_context_text(bundle)

    return (
        f"Erstelle einen juristisch strukturierten Vorschlag für das Feld '{target_label}'.\n"
        f"Thema: {bundle.topic_label}.\n"
        "Nutze ausschließlich den bereitgestellten internen Kontext, die freigegebenen Rohtexte, "
        "die Wissensbasis, die Mustertexte, die freigegebenen Quellen und die Stammdaten.\n"
        "Wenn Informationen fehlen, weise knapp darauf hin.\n\n"
        "KONTEXT:\n"
        f"{context_text}"
    )