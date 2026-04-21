from django.db import models
from accounts.models import Tenant
from processing.models import ProcessingActivity


class LegalAssessment(models.Model):
    class LegalBasis(models.TextChoices):
        CONSENT = "consent", "Art. 6 Abs. 1 lit. a DSGVO – Einwilligung"
        CONTRACT = "contract", "Art. 6 Abs. 1 lit. b DSGVO – Vertrag / vorvertragliche Maßnahmen"
        LEGAL_OBLIGATION = "legal_obligation", "Art. 6 Abs. 1 lit. c DSGVO – Rechtliche Verpflichtung"
        VITAL_INTERESTS = "vital_interests", "Art. 6 Abs. 1 lit. d DSGVO – Lebenswichtige Interessen"
        PUBLIC_TASK = "public_task", "Art. 6 Abs. 1 lit. e DSGVO – Öffentliche Aufgabe"
        LEGITIMATE_INTERESTS = "legitimate_interests", "Art. 6 Abs. 1 lit. f DSGVO – Berechtigtes Interesse"

    class SpecialLegalBasis(models.TextChoices):
        NONE = "", "Keine"
        EMPLOYMENT = "employment", "Art. 9 Abs. 2 lit. b DSGVO – Arbeitsrecht / Sozialrecht"
        VITAL = "vital", "Art. 9 Abs. 2 lit. c DSGVO – Lebenswichtige Interessen"
        LEGAL_CLAIMS = "legal_claims", "Art. 9 Abs. 2 lit. f DSGVO – Rechtsansprüche"
        MEDICAL = "medical", "Art. 9 Abs. 2 lit. h DSGVO – Medizinische Behandlung"
        PUBLIC_HEALTH = "public_health", "Art. 9 Abs. 2 lit. i DSGVO – Öffentliches Gesundheitsinteresse"
        EXPLICIT_CONSENT = "explicit_consent", "Art. 9 Abs. 2 lit. a DSGVO – Ausdrückliche Einwilligung"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Niedrig"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"

    class LegitimateInterestOutcome(models.TextChoices):
        CONTROLLER = "controller", "Interessen des Verantwortlichen überwiegen"
        BALANCED = "balanced", "Abwägung ausgeglichen / vertretbar"
        DATA_SUBJECT = "data_subject", "Interessen der betroffenen Person überwiegen"

    class NoDPIACheckReason(models.TextChoices):
        NONE = "", "Bitte auswählen"
        NOT_RELEVANT_AS_SUCH = "not_relevant_as_such", "Verfahren als solches nicht DSFA-relevant"
        NOT_RELEVANT_BY_DISCRETION = "not_relevant_by_discretion", "Verfahren nach ausgeübtem Ermessen nicht DSFA-relevant"
        NO_HIGH_RISK = "no_high_risk", "Kein hohes Risiko für Rechte und Freiheiten erkennbar"
        NO_MUST_LIST_CASE = "no_must_list_case", "Kein Muss-Listen-Fall / kein typischer Hochrisikofall"
        OTHER = "other", "Sonstiger Grund"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    processing_activity = models.OneToOneField(
        ProcessingActivity,
        on_delete=models.CASCADE,
        related_name="legal_record",
    )

    legal_basis = models.CharField(
        max_length=50,
        choices=LegalBasis.choices,
        blank=True,
    )
    special_legal_basis = models.CharField(
        max_length=50,
        choices=SpecialLegalBasis.choices,
        blank=True,
    )

    professional_secrecy = models.BooleanField(
        default=False,
        help_text="Berufsgeheimnis / § 203 StGB relevant",
    )
    section_203_process_implemented = models.BooleanField(
        default=False,
        help_text="203er Verfahren für dieses Verfahren implementiert und dokumentiert",
    )

    legitimate_interest_test = models.BooleanField(
        default=False,
        help_text="Interessenabwägung durchgeführt",
    )

    legitimate_interest_purpose = models.TextField(
        blank=True,
        help_text="Welches berechtigte Interesse verfolgt der Verantwortliche?",
    )
    data_subject_impact = models.TextField(
        blank=True,
        help_text="Welche Auswirkungen oder Risiken bestehen für die betroffene Person?",
    )
    safeguards = models.TextField(
        blank=True,
        help_text="Welche Schutzmaßnahmen sprechen zugunsten der Zulässigkeit?",
    )
    legitimate_interest_outcome = models.CharField(
        max_length=30,
        choices=LegitimateInterestOutcome.choices,
        blank=True,
    )
    legitimate_interest_reasoning = models.TextField(
        blank=True,
        help_text="Zusammenfassende Begründung der Interessenabwägung.",
    )
    legitimate_interest_completed = models.BooleanField(
        default=False,
        help_text="Interessenabwägung inhaltlich abgeschlossen.",
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        blank=True,
    )

    no_dpia_check_required_reason = models.CharField(
        max_length=50,
        choices=NoDPIACheckReason.choices,
        blank=True,
        help_text="Dokumentation, warum kein gesonderter DSFA-Check erforderlich ist.",
    )
    no_dpia_check_required_note = models.TextField(
        blank=True,
        help_text="Ergänzende Begründung, insbesondere bei 'Sonstiger Grund'.",
    )

    legal_assessment_text = models.TextField(
        blank=True,
        help_text="Juristische Bewertung / Begründung",
    )
    open_issues = models.TextField(
        blank=True,
        help_text="Offene Rechtsfragen / Klärungspunkte",
    )

    ai_prompt = models.TextField(blank=True)
    ai_suggestion = models.TextField(blank=True)
    ai_prompt_version = models.CharField(max_length=50, blank=True, default="v1")
    ai_last_generated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["processing_activity__title"]

    def __str__(self):
        return f"Rechtliche Bewertung – {self.processing_activity.title}"

    @property
    def dpia_check_result(self):
        if self.no_dpia_check_required_reason:
            return "not_required"

        dpia_check = getattr(self.processing_activity, "dpia_check", None)
        if dpia_check:
            return dpia_check.recommendation
        return ""

    @property
    def dpia_check_result_label(self):
        if self.no_dpia_check_required_reason:
            return "Kein DSFA-Check erforderlich"

        dpia_check = getattr(self.processing_activity, "dpia_check", None)
        if dpia_check:
            return dpia_check.recommendation_label
        return "Noch nicht geprüft"

    @property
    def dpia_check_result_badge_class(self):
        if self.no_dpia_check_required_reason:
            return "success"

        dpia_check = getattr(self.processing_activity, "dpia_check", None)
        if dpia_check:
            return dpia_check.recommendation_badge_class
        return "secondary"

    @property
    def has_dpia_result_or_reason(self):
        return bool(self.dpia_check_result or self.no_dpia_check_required_reason)