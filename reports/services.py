from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.template.loader import render_to_string
from django.utils import timezone

from actions.models import ActionItem
from audits.services import (
    build_current_open_items_snapshot,
    build_procedure_audit_statistics,
)


def _safe_path_component(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip())
    return cleaned.strip("_") or "unbekannt"


def _build_procedure_audit_conclusion(audit, stats, open_actions_count):
    parts = [
        f"Im Audit wurden insgesamt {stats['procedures_total']} Verfahren betrachtet.",
        f"Davon wurden {stats['procedures_unchanged']} als unverändert, "
        f"{stats['procedures_changed']} als geändert und "
        f"{stats['procedures_review_required']} mit weiterem Prüfbedarf eingeordnet.",
    ]

    if stats["new_activities_total"]:
        parts.append(
            f"Zusätzlich wurden {stats['new_activities_total']} neue Verfahren im Auditkontext dokumentiert."
        )
    else:
        parts.append("Es wurden keine neuen Verfahren im Auditkontext dokumentiert.")

    if open_actions_count == 0:
        parts.append("Zum Zeitpunkt der Berichtserzeugung bestehen keine offenen auditbezogenen Maßnahmen.")
    else:
        parts.append(
            f"Zum Zeitpunkt der Berichtserzeugung bestehen noch {open_actions_count} offene auditbezogene Maßnahmen."
        )

    if audit.final_completed_at:
        parts.append(f"Das Jahresaudit {audit.audit_year} wurde bereits beendet.")
    elif audit.preliminary_completed_at:
        parts.append("Das Audit ist vorläufig abgeschlossen.")
    else:
        parts.append("Das Audit befindet sich noch in Bearbeitung.")

    return " ".join(parts)


def build_procedure_audit_report_context(audit):
    stats = build_procedure_audit_statistics(audit)
    current_open_items = build_current_open_items_snapshot(audit)

    procedure_items = audit.items.select_related("processing_activity").order_by(
        "processing_activity__title",
        "processing_activity__id",
    )
    new_activities = audit.new_activities.all().order_by("title", "id")

    all_actions = ActionItem.objects.filter(
        related_procedure_audit=audit
    ).order_by("status", "priority", "title")

    open_actions = all_actions.filter(
        status__in=[
            ActionItem.Status.OPEN,
            ActionItem.Status.IN_PROGRESS,
            ActionItem.Status.WAITING,
            ActionItem.Status.FOLLOW_UP,
        ]
    )
    completed_actions = all_actions.filter(status=ActionItem.Status.COMPLETED)
    irrelevant_actions = all_actions.filter(status=ActionItem.Status.IRRELEVANT)

    conclusion = _build_procedure_audit_conclusion(
        audit=audit,
        stats=stats,
        open_actions_count=open_actions.count(),
    )

    return {
        "audit": audit,
        "stats": stats,
        "procedure_items": procedure_items,
        "new_activities": new_activities,
        "open_actions": open_actions,
        "completed_actions": completed_actions,
        "irrelevant_actions": irrelevant_actions,
        "current_open_items": current_open_items,
        "conclusion": conclusion,
    }


def generate_and_store_procedure_audit_report(audit):
    context = build_procedure_audit_report_context(audit)
    html = render_to_string("reports/procedure_audit_report_file.html", context)

    tenant_part = _safe_path_component(audit.tenant.name)
    year_part = str(audit.audit_year)
    filename = f"jahresaudit_{audit.audit_year}_{audit.pk}.html"

    relative_dir = Path("reports") / "audits" / tenant_part / year_part
    absolute_dir = Path(settings.MEDIA_ROOT) / relative_dir
    absolute_dir.mkdir(parents=True, exist_ok=True)

    absolute_path = absolute_dir / filename
    absolute_path.write_text(html, encoding="utf-8")

    relative_file_path = relative_dir / filename

    if audit.report_file:
        try:
            audit.report_file.delete(save=False)
        except Exception:
            pass

    with absolute_path.open("rb") as fh:
        audit.report_file.save(str(relative_file_path), File(fh), save=False)

    audit.report_generated_at = timezone.now()
    audit.save(update_fields=["report_file", "report_generated_at", "updated_at"])

    return audit