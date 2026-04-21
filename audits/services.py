from django.utils import timezone

from actions.models import ActionItem
from processing.models import ProcessingActivity

from .models import (
    ProcedureAuditChecklistResponse,
    ProcedureAuditItem,
    ProcedureAuditNewActivity,
)


OPEN_ACTION_STATUSES = [
    ActionItem.Status.OPEN,
    ActionItem.Status.IN_PROGRESS,
    ActionItem.Status.WAITING,
    ActionItem.Status.FOLLOW_UP,
]


def sync_procedure_audit_items(procedure_audit):
    procedures = ProcessingActivity.objects.filter(
        tenant=procedure_audit.tenant
    ).order_by("title", "id")

    created_items = []

    for procedure in procedures:
        item, created = ProcedureAuditItem.objects.get_or_create(
            audit=procedure_audit,
            processing_activity=procedure,
        )
        if created:
            created_items.append(item)

    return created_items


def _ensure_procedure_audit_action_exists(
    *,
    audit_item,
    title: str,
    description: str,
    priority: str,
    source_area: str,
    target_area: str,
):
    processing = audit_item.processing_activity
    audit = audit_item.audit

    exists = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.AUDIT,
        related_procedure_audit=audit,
        related_processing_activity=processing,
        title=title,
        status__in=OPEN_ACTION_STATUSES,
    ).exists()

    if exists:
        return None

    return ActionItem.objects.create(
        tenant=audit.tenant,
        title=title,
        description=description,
        source_type=ActionItem.SourceType.AUDIT,
        source_area=source_area,
        target_area=target_area,
        audit_section=ActionItem.AuditSection.PROCEDURE_REVIEW,
        related_procedure_audit=audit,
        related_processing_activity=processing,
        responsible_person=processing.responsible_person or "",
        priority=priority,
        status=ActionItem.Status.OPEN,
        notes=(
            f"Automatisch aus verfahrensorientiertem Audit erzeugt: "
            f"{audit.title} ({audit.audit_year})"
        ),
    )


def _ensure_new_activity_audit_action_exists(
    *,
    new_activity,
    title: str,
    description: str,
    priority: str,
):
    audit = new_activity.audit

    exists = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.AUDIT,
        related_procedure_audit=audit,
        title=title,
        status__in=OPEN_ACTION_STATUSES,
    ).exists()

    if exists:
        return None

    return ActionItem.objects.create(
        tenant=audit.tenant,
        title=title,
        description=description,
        source_type=ActionItem.SourceType.AUDIT,
        source_area=ActionItem.Area.AUDIT,
        target_area=ActionItem.Area.PROCESSING,
        audit_section=ActionItem.AuditSection.NEW_ACTIVITIES,
        related_procedure_audit=audit,
        responsible_person=new_activity.contact_person or "",
        priority=priority,
        status=ActionItem.Status.OPEN,
        notes=(
            f"Automatisch aus Meldung neuer Verfahren im Audit erzeugt: "
            f"{audit.title} ({audit.audit_year})"
        ),
    )


def _ensure_checklist_action_exists(
    *,
    procedure_audit,
    response,
    title: str,
    description: str,
    priority: str,
):
    exists = ActionItem.objects.filter(
        source_type=ActionItem.SourceType.AUDIT,
        related_procedure_audit=procedure_audit,
        title=title,
        status__in=OPEN_ACTION_STATUSES,
    ).exists()

    if exists:
        return None

    return ActionItem.objects.create(
        tenant=procedure_audit.tenant,
        title=title,
        description=description,
        source_type=ActionItem.SourceType.AUDIT,
        source_area=ActionItem.Area.AUDIT,
        target_area=ActionItem.Area.AUDIT,
        audit_section=ActionItem.AuditSection.GENERAL_REVIEW,
        related_procedure_audit=procedure_audit,
        responsible_person="",
        priority=priority,
        status=ActionItem.Status.OPEN,
        notes="Automatisch aus allgemeiner Audit-Checkliste erzeugt.",
    )


def _build_audit_item_context_text(audit_item):
    processing = audit_item.processing_activity
    audit = audit_item.audit
    notes = (audit_item.notes or "").strip()

    return (
        f"Verfahren: {processing.title}\n"
        f"Audit: {audit.title} ({audit.audit_year})\n\n"
        f"Hinweise aus dem Audit:\n"
        f"{notes or 'Keine weiteren Hinweise dokumentiert.'}"
    )


def _clear_obsolete_procedure_review_actions(audit_item):
    should_clear = (
        audit_item.review_status in [
            ProcedureAuditItem.ReviewStatus.UNCHANGED,
            ProcedureAuditItem.ReviewStatus.DISCONTINUED,
        ]
        and not audit_item.legal_review_required
        and not audit_item.dpia_review_required
        and not audit_item.action_required
    )

    if not should_clear:
        return 0

    return ActionItem.objects.filter(
        related_procedure_audit=audit_item.audit,
        related_processing_activity=audit_item.processing_activity,
        source_type=ActionItem.SourceType.AUDIT,
        audit_section=ActionItem.AuditSection.PROCEDURE_REVIEW,
        status__in=OPEN_ACTION_STATUSES,
    ).update(
        status=ActionItem.Status.IRRELEVANT
    )


def generate_actions_from_procedure_audit(procedure_audit):
    created_actions = []

    audit_items = ProcedureAuditItem.objects.select_related(
        "processing_activity",
        "audit",
    ).filter(audit=procedure_audit)

    for audit_item in audit_items:
        processing = audit_item.processing_activity
        context_text = _build_audit_item_context_text(audit_item)

        review_status = audit_item.review_status
        legal_review_required = audit_item.legal_review_required
        dpia_review_required = audit_item.dpia_review_required
        action_required = audit_item.action_required

        _clear_obsolete_procedure_review_actions(audit_item)

        should_skip_new_actions = (
            review_status in [
                ProcedureAuditItem.ReviewStatus.UNCHANGED,
                ProcedureAuditItem.ReviewStatus.DISCONTINUED,
            ]
            and not legal_review_required
            and not dpia_review_required
            and not action_required
        )

        if should_skip_new_actions:
            continue

        if review_status == ProcedureAuditItem.ReviewStatus.NOT_CHECKED:
            action = _ensure_procedure_audit_action_exists(
                audit_item=audit_item,
                title=f"Verfahren im Audit nachprüfen: {processing.title}",
                description=(
                    "Dieses Verfahren wurde im Audit noch nicht geprüft.\n\n"
                    f"{context_text}"
                ),
                priority=ActionItem.Priority.HIGH,
                source_area=ActionItem.Area.AUDIT,
                target_area=ActionItem.Area.AUDIT,
            )
            if action:
                created_actions.append(action)

        if review_status == ProcedureAuditItem.ReviewStatus.REVIEW_REQUIRED:
            action = _ensure_procedure_audit_action_exists(
                audit_item=audit_item,
                title=f"Verfahren im Audit weiter prüfen: {processing.title}",
                description=(
                    "Im Audit wurde weiterer Prüfbedarf für dieses Verfahren festgestellt.\n\n"
                    f"{context_text}"
                ),
                priority=ActionItem.Priority.HIGH,
                source_area=ActionItem.Area.AUDIT,
                target_area=ActionItem.Area.AUDIT,
            )
            if action:
                created_actions.append(action)

        if legal_review_required:
            action = _ensure_procedure_audit_action_exists(
                audit_item=audit_item,
                title=f"Rechtsbewertung prüfen: {processing.title}",
                description=(
                    "Im verfahrensorientierten Audit wurde festgestellt, dass die "
                    "Rechtsbewertung dieses Verfahrens überprüft oder aktualisiert "
                    "werden sollte.\n\n"
                    f"{context_text}"
                ),
                priority=ActionItem.Priority.HIGH,
                source_area=ActionItem.Area.AUDIT,
                target_area=ActionItem.Area.LEGAL,
            )
            if action:
                created_actions.append(action)

        if dpia_review_required:
            action = _ensure_procedure_audit_action_exists(
                audit_item=audit_item,
                title=f"DSFA prüfen: {processing.title}",
                description=(
                    "Im verfahrensorientierten Audit wurde festgestellt, dass die "
                    "DSFA-Prüfung oder eine bestehende DSFA zu diesem Verfahren "
                    "überprüft werden sollte.\n\n"
                    f"{context_text}"
                ),
                priority=ActionItem.Priority.HIGH,
                source_area=ActionItem.Area.AUDIT,
                target_area=ActionItem.Area.DPIA,
            )
            if action:
                created_actions.append(action)

        if action_required:
            action = _ensure_procedure_audit_action_exists(
                audit_item=audit_item,
                title=f"Audit-Feststellung bearbeiten: {processing.title}",
                description=(
                    "Im verfahrensorientierten Audit wurde eine allgemeine Maßnahme "
                    "für dieses Verfahren als erforderlich dokumentiert.\n\n"
                    f"{context_text}"
                ),
                priority=ActionItem.Priority.MEDIUM,
                source_area=ActionItem.Area.AUDIT,
                target_area=ActionItem.Area.AUDIT,
            )
            if action:
                created_actions.append(action)

    return created_actions


def generate_actions_from_new_activities(procedure_audit):
    created_actions = []

    new_activities = ProcedureAuditNewActivity.objects.filter(
        audit=procedure_audit,
        requires_follow_up=True,
    ).order_by("title", "id")

    for new_activity in new_activities:
        action = _ensure_new_activity_audit_action_exists(
            new_activity=new_activity,
            title=f"Neues Verfahren prüfen: {new_activity.title}",
            description=(
                "Im Audit wurde ein bislang nicht erfasstes mögliches neues Verfahren gemeldet.\n\n"
                "Vor einer Anlage ist zu prüfen, ob tatsächlich ein eigenständiges "
                "Verfahren vorliegt und welche Folgeprüfungen erforderlich sind "
                "(z. B. Organisation, Datenfluss, AV/AVV, Rechtsgrundlage, DSFA-Bedarf).\n\n"
                f"Bezeichnung: {new_activity.title}\n"
                f"Fachbereich: {new_activity.department_hint or '—'}\n"
                f"Ansprechpartner: {new_activity.contact_person or '—'}\n"
                f"Bereits produktiv: {'Ja' if new_activity.is_already_active else 'Nein'}\n\n"
                f"Kurzbeschreibung:\n{new_activity.description or '—'}\n\n"
                f"Weitere Hinweise:\n{new_activity.notes or '—'}"
            ),
            priority=ActionItem.Priority.HIGH,
        )
        if action:
            created_actions.append(action)

    return created_actions


def generate_actions_from_procedure_audit_checklist(procedure_audit):
    created_actions = []

    responses = ProcedureAuditChecklistResponse.objects.select_related(
        "question",
        "procedure_audit",
    ).filter(
        procedure_audit=procedure_audit,
        action_required=True,
    )

    for response in responses:
        title = f"Audit-Checkliste bearbeiten: {response.question.question_text[:80]}"

        action = _ensure_checklist_action_exists(
            procedure_audit=procedure_audit,
            response=response,
            title=title,
            description=(
                "Automatisch aus Abschnitt 3 – Allgemeine Audit-Checkliste erzeugt.\n\n"
                f"Frage: {response.question.question_text}\n"
                f"Bewertung: {response.get_rating_display() or '—'}\n"
                f"Kommentar: {response.comment or '—'}\n"
                f"Nachweis vorhanden: {'Ja' if response.evidence_available else 'Nein'}"
            ),
            priority=ActionItem.Priority.MEDIUM,
        )
        if action:
            created_actions.append(action)

    return created_actions


def get_open_audit_actions(procedure_audit):
    return ActionItem.objects.filter(
        related_procedure_audit=procedure_audit,
        status__in=OPEN_ACTION_STATUSES,
    )


def get_open_procedure_review_actions(procedure_audit):
    return ActionItem.objects.filter(
        related_procedure_audit=procedure_audit,
        audit_section=ActionItem.AuditSection.PROCEDURE_REVIEW,
        status__in=OPEN_ACTION_STATUSES,
    )


def get_open_new_activities_actions(procedure_audit):
    return ActionItem.objects.filter(
        related_procedure_audit=procedure_audit,
        audit_section=ActionItem.AuditSection.NEW_ACTIVITIES,
        status__in=OPEN_ACTION_STATUSES,
    )


def get_open_checklist_actions(procedure_audit):
    return ActionItem.objects.filter(
        related_procedure_audit=procedure_audit,
        audit_section=ActionItem.AuditSection.GENERAL_REVIEW,
        status__in=OPEN_ACTION_STATUSES,
    )


def build_procedure_audit_statistics(procedure_audit):
    items = ProcedureAuditItem.objects.filter(audit=procedure_audit)
    new_activities = ProcedureAuditNewActivity.objects.filter(audit=procedure_audit)
    checklist_responses = ProcedureAuditChecklistResponse.objects.filter(procedure_audit=procedure_audit)

    return {
        "procedures_total": items.count(),
        "procedures_not_checked": items.filter(
            review_status=ProcedureAuditItem.ReviewStatus.NOT_CHECKED
        ).count(),
        "procedures_unchanged": items.filter(
            review_status=ProcedureAuditItem.ReviewStatus.UNCHANGED
        ).count(),
        "procedures_changed": items.filter(
            review_status=ProcedureAuditItem.ReviewStatus.CHANGED
        ).count(),
        "procedures_review_required": items.filter(
            review_status=ProcedureAuditItem.ReviewStatus.REVIEW_REQUIRED
        ).count(),
        "procedures_discontinued": items.filter(
            review_status=ProcedureAuditItem.ReviewStatus.DISCONTINUED
        ).count(),
        "new_activities_total": new_activities.count(),
        "new_activities_follow_up_count": new_activities.filter(requires_follow_up=True).count(),
        "checklist_questions_answered": checklist_responses.exclude(rating="").count(),
        "checklist_actions_required_count": checklist_responses.filter(action_required=True).count(),
        "open_audit_actions_count": get_open_audit_actions(procedure_audit).count(),
        "open_procedure_review_actions_count": get_open_procedure_review_actions(procedure_audit).count(),
        "open_new_activities_actions_count": get_open_new_activities_actions(procedure_audit).count(),
        "open_checklist_actions_count": get_open_checklist_actions(procedure_audit).count(),
    }


def build_current_open_items_snapshot(procedure_audit):
    snapshot = []

    for action in get_open_audit_actions(procedure_audit).order_by("title", "id"):
        if action.audit_section == ActionItem.AuditSection.PROCEDURE_REVIEW:
            area = "procedure_review"
        elif action.audit_section == ActionItem.AuditSection.NEW_ACTIVITIES:
            area = "new_activities"
        elif action.audit_section == ActionItem.AuditSection.GENERAL_REVIEW:
            area = "general_review"
        else:
            area = "audit_actions"

        snapshot.append({
            "area": area,
            "type": "open_action",
            "label": f"{action.title} ({action.get_status_display()})",
        })

    return snapshot


def build_preliminary_open_items_snapshot(procedure_audit):
    items = ProcedureAuditItem.objects.select_related("processing_activity").filter(audit=procedure_audit)
    new_activities = ProcedureAuditNewActivity.objects.filter(audit=procedure_audit).order_by("title", "id")
    checklist_responses = ProcedureAuditChecklistResponse.objects.select_related("question").filter(
        procedure_audit=procedure_audit
    )
    open_actions = get_open_audit_actions(procedure_audit).order_by("title", "id")

    snapshot = []

    for audit_item in items:
        title = audit_item.processing_activity.title

        if audit_item.review_status == ProcedureAuditItem.ReviewStatus.NOT_CHECKED:
            snapshot.append({
                "area": "procedure_review",
                "type": "not_checked",
                "label": f"{title}: noch nicht geprüft",
            })

        if audit_item.review_status == ProcedureAuditItem.ReviewStatus.REVIEW_REQUIRED:
            snapshot.append({
                "area": "procedure_review",
                "type": "review_required",
                "label": f"{title}: weiterer Prüfbedarf",
            })

        if audit_item.legal_review_required:
            snapshot.append({
                "area": "procedure_review",
                "type": "legal_review_required",
                "label": f"{title}: Rechtsbewertung prüfen",
            })

        if audit_item.dpia_review_required:
            snapshot.append({
                "area": "procedure_review",
                "type": "dpia_review_required",
                "label": f"{title}: DSFA prüfen",
            })

        if audit_item.action_required:
            snapshot.append({
                "area": "procedure_review",
                "type": "action_required",
                "label": f"{title}: allgemeine Maßnahme erforderlich",
            })

    for new_activity in new_activities:
        if new_activity.requires_follow_up:
            snapshot.append({
                "area": "new_activities",
                "type": "follow_up_required",
                "label": f"{new_activity.title}: weitere Prüfung / Nachbearbeitung erforderlich",
            })

    for response in checklist_responses:
        if response.action_required:
            snapshot.append({
                "area": "general_review",
                "type": "checklist_action_required",
                "label": f"Checkliste: {response.question.question_text[:100]}",
            })

    for action in open_actions:
        snapshot.append({
            "area": "audit_actions",
            "type": "open_action",
            "label": f"{action.title} ({action.get_status_display()})",
        })

    return snapshot


def build_preliminary_audit_summary(procedure_audit):
    stats = build_procedure_audit_statistics(procedure_audit)
    open_items = build_preliminary_open_items_snapshot(procedure_audit)

    lines = [
        f"Vorläufiger Auditabschluss: {procedure_audit.title} ({procedure_audit.audit_year})",
        "",
        "Abschnittsstatus:",
        f"- Verfahrensprüfung: {'vorläufig abgeschlossen' if procedure_audit.procedure_review_completed_at else 'offen'}",
        f"- Neue Verfahren: {'vorläufig abgeschlossen' if procedure_audit.new_activities_review_completed_at else 'offen'}",
        f"- Allgemeine Audit-Checkliste: {'vorläufig abgeschlossen' if procedure_audit.checklist_review_completed_at else 'offen'}",
        "",
        "Statistische Einordnung:",
        f"- Verfahren gesamt: {stats['procedures_total']}",
        f"- Noch nicht geprüft: {stats['procedures_not_checked']}",
        f"- Unverändert: {stats['procedures_unchanged']}",
        f"- Geändert: {stats['procedures_changed']}",
        f"- Weiterer Prüfbedarf: {stats['procedures_review_required']}",
        f"- Nicht mehr genutzt: {stats['procedures_discontinued']}",
        f"- Neue Verfahren: {stats['new_activities_total']}",
        f"- Neue Verfahren mit Follow-up: {stats['new_activities_follow_up_count']}",
        f"- Beantwortete Checklistenfragen: {stats['checklist_questions_answered']}",
        f"- Checklisten-Maßnahmen: {stats['checklist_actions_required_count']}",
        f"- Offene auditbezogene Maßnahmen: {stats['open_audit_actions_count']}",
        "",
        "Inhalt des vorläufig abgeschlossenen Audits:",
    ]

    if open_items:
        for item in open_items:
            lines.append(f"- {item['label']}")
    else:
        lines.append("- Keine offenen Punkte dokumentiert.")

    return "\n".join(lines)


def can_preliminary_complete(procedure_audit):
    return (
        procedure_audit.procedure_review_completed_at is not None
        and procedure_audit.new_activities_review_completed_at is not None
        and procedure_audit.checklist_review_completed_at is not None
    )


def can_procedure_review_final_complete(procedure_audit):
    return (
        procedure_audit.procedure_review_completed_at is not None
        and get_open_procedure_review_actions(procedure_audit).count() == 0
    )


def can_final_complete(procedure_audit):
    return (
        procedure_audit.preliminary_completed_at is not None
        and get_open_audit_actions(procedure_audit).count() == 0
    )


def mark_procedure_review_completed(procedure_audit):
    procedure_audit.procedure_review_completed_at = timezone.now()

    if procedure_audit.status == procedure_audit.Status.PLANNED:
        procedure_audit.status = procedure_audit.Status.IN_PROGRESS
        procedure_audit.save(
            update_fields=["procedure_review_completed_at", "status", "updated_at"]
        )
    else:
        procedure_audit.save(update_fields=["procedure_review_completed_at", "updated_at"])


def mark_procedure_review_final_completed(procedure_audit):
    procedure_audit.procedure_review_final_completed_at = timezone.now()
    procedure_audit.save(
        update_fields=[
            "procedure_review_final_completed_at",
            "updated_at",
        ]
    )


def mark_new_activities_review_completed(procedure_audit):
    procedure_audit.new_activities_review_completed_at = timezone.now()

    if procedure_audit.status == procedure_audit.Status.PLANNED:
        procedure_audit.status = procedure_audit.Status.IN_PROGRESS
        procedure_audit.save(
            update_fields=["new_activities_review_completed_at", "status", "updated_at"]
        )
    else:
        procedure_audit.save(update_fields=["new_activities_review_completed_at", "updated_at"])


def mark_checklist_review_completed(procedure_audit):
    procedure_audit.checklist_review_completed_at = timezone.now()

    if procedure_audit.status == procedure_audit.Status.PLANNED:
        procedure_audit.status = procedure_audit.Status.IN_PROGRESS
        procedure_audit.save(
            update_fields=["checklist_review_completed_at", "status", "updated_at"]
        )
    else:
        procedure_audit.save(update_fields=["checklist_review_completed_at", "updated_at"])


def mark_preliminary_completed(procedure_audit):
    stats = build_procedure_audit_statistics(procedure_audit)
    open_items = build_preliminary_open_items_snapshot(procedure_audit)
    summary = build_preliminary_audit_summary(procedure_audit)

    procedure_audit.preliminary_completed_at = timezone.now()
    procedure_audit.preliminary_report_summary = summary
    procedure_audit.preliminary_statistics_snapshot = stats
    procedure_audit.preliminary_open_items_snapshot = open_items
    procedure_audit.status = procedure_audit.Status.PRELIMINARY_COMPLETED
    procedure_audit.save(
        update_fields=[
            "preliminary_completed_at",
            "preliminary_report_summary",
            "preliminary_statistics_snapshot",
            "preliminary_open_items_snapshot",
            "status",
            "updated_at",
        ]
    )


def mark_final_completed(procedure_audit):
    procedure_audit.final_completed_at = timezone.now()
    procedure_audit.status = procedure_audit.Status.COMPLETED
    procedure_audit.save(
        update_fields=[
            "final_completed_at",
            "status",
            "updated_at",
        ]
    )