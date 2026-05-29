from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.tenant_utils import get_effective_tenant
from legal.models import LegalAssessment
from processing.models import ProcessingActivity

from .forms import ActionItemForm
from .models import ActionItem
from .services import generate_actions_from_legal_assessment


OPEN_ACTION_STATUSES = [
    ActionItem.Status.OPEN,
    ActionItem.Status.IN_PROGRESS,
    ActionItem.Status.WAITING,
    ActionItem.Status.FOLLOW_UP,
]

PRIORITY_DUE_DAYS = {
    ActionItem.Priority.HIGH: 7,
    ActionItem.Priority.MEDIUM: 14,
    ActionItem.Priority.LOW: 30,
}


def _automatic_action_due_date(action):
    if action.due_date:
        return action.due_date

    base_date = action.created_at.date()
    days = PRIORITY_DUE_DAYS.get(action.priority, 14)
    return base_date + timedelta(days=days)


def _enrich_action_due_state(action, today=None):
    today = today or timezone.localdate()

    if action.status not in OPEN_ACTION_STATUSES:
        action.auto_due_date = None
        action.is_overdue = False
        action.due_state_label = "—"
        action.due_badge_class = "secondary"
        return action

    due_date = _automatic_action_due_date(action)
    delta_days = (due_date - today).days

    action.auto_due_date = due_date
    action.days_until_due = delta_days
    action.is_overdue = delta_days < 0

    if delta_days < 0:
        action.due_state_label = f"Überfällig seit {abs(delta_days)} Tag(en)"
        action.due_badge_class = "danger"
    elif delta_days == 0:
        action.due_state_label = "Heute fällig"
        action.due_badge_class = "warning"
    elif delta_days <= 14:
        action.due_state_label = f"Fällig in {delta_days} Tag(en)"
        action.due_badge_class = "warning"
    else:
        action.due_state_label = f"Noch {delta_days} Tag(e)"
        action.due_badge_class = "secondary"

    return action


def _apply_sorting(qs, request):
    sort = request.GET.get("sort", "status_open_priority")

    qs = qs.annotate(
        status_group_sort=Case(
            When(status__in=OPEN_ACTION_STATUSES, then=Value(0)),
            When(status=ActionItem.Status.COMPLETED, then=Value(1)),
            When(status=ActionItem.Status.IRRELEVANT, then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        ),
        priority_sort=Case(
            When(priority=ActionItem.Priority.HIGH, then=Value(0)),
            When(priority=ActionItem.Priority.MEDIUM, then=Value(1)),
            When(priority=ActionItem.Priority.LOW, then=Value(2)),
            default=Value(9),
            output_field=IntegerField(),
        ),
    )

    if sort == "created_asc":
        return qs.order_by("status_group_sort", "created_at")

    if sort == "created_desc":
        return qs.order_by("status_group_sort", "-created_at")

    if sort == "updated_asc":
        return qs.order_by("status_group_sort", "updated_at")

    if sort == "updated_desc":
        return qs.order_by("status_group_sort", "-updated_at")

    if sort == "priority":
        return qs.order_by("status_group_sort", "priority_sort", "-created_at")

    if sort == "processing":
        return qs.order_by(
            "status_group_sort",
            "related_processing_activity__title",
            "priority_sort",
            "-updated_at",
            "-created_at",
        )

    if sort == "status_open_priority":
        return qs.order_by("status_group_sort", "priority_sort", "-updated_at", "-created_at")

    return qs.order_by("status_group_sort", "priority_sort", "-updated_at", "-created_at")


def _tenant_filtered_action_queryset(request):
    qs = ActionItem.objects.select_related(
        "tenant",
        "related_audit",
        "related_audit__processor",
        "related_procedure_audit",
        "related_procedure_audit__tenant",
        "related_processing_activity",
        "related_legal_assessment",
        "related_legal_assessment__processing_activity",
    )

    active_tenant = get_effective_tenant(request)

    if request.user.is_superuser:
        if active_tenant is not None:
            qs = qs.filter(tenant=active_tenant)
    else:
        if request.user.tenant_id:
            qs = qs.filter(tenant=request.user.tenant)
        else:
            qs = qs.none()

    return qs


def _resolve_action_target_area(item):
    """
    Maßgeblich ist zuerst der explizit gesetzte target_area-Wert.
    Nur wenn der nicht sinnvoll gesetzt ist, wird aus Relationen abgeleitet.
    """

    if item.target_area in {
        ActionItem.Area.AUDIT,
        ActionItem.Area.PROCESSING,
        ActionItem.Area.LEGAL,
        ActionItem.Area.DPIA,
        ActionItem.Area.DOCUMENT,
        ActionItem.Area.REPORT,
        ActionItem.Area.REQUEST,
        ActionItem.Area.MANUAL,
    }:
        return item.target_area

    if item.related_audit or item.related_procedure_audit:
        return ActionItem.Area.AUDIT

    if item.related_legal_assessment:
        return ActionItem.Area.LEGAL

    if item.related_processing_activity:
        return ActionItem.Area.PROCESSING

    return ActionItem.Area.MANUAL


def _get_processing_pk_for_action(item):
    if item.related_processing_activity:
        return item.related_processing_activity.pk

    if item.related_legal_assessment and item.related_legal_assessment.processing_activity_id:
        return item.related_legal_assessment.processing_activity.pk

    return None


def _get_action_button_label(item):
    target_area = _resolve_action_target_area(item)

    if (
        item.related_procedure_audit
        and not item.related_processing_activity
        and target_area == ActionItem.Area.PROCESSING
    ):
        return "Neues Verfahren prüfen"

    if target_area == ActionItem.Area.AUDIT:
        return "Audit bearbeiten"

    if target_area == ActionItem.Area.PROCESSING:
        return "Verfahren prüfen"

    if target_area == ActionItem.Area.LEGAL:
        return "Rechtsbewertung prüfen"

    if target_area == ActionItem.Area.DPIA:
        return "DSFA prüfen"

    if target_area == ActionItem.Area.DOCUMENT:
        return "Dokument öffnen"

    if target_area == ActionItem.Area.REPORT:
        return "Report öffnen"

    return "Bearbeiten"


def _get_status_badge_class(item):
    if item.status == ActionItem.Status.OPEN:
        return "danger"
    if item.status == ActionItem.Status.IN_PROGRESS:
        return "warning"
    if item.status == ActionItem.Status.WAITING:
        return "info"
    if item.status == ActionItem.Status.FOLLOW_UP:
        return "secondary"
    if item.status == ActionItem.Status.COMPLETED:
        return "success"
    if item.status == ActionItem.Status.IRRELEVANT:
        return "secondary"
    if item.status == ActionItem.Status.DISCARDED:
        return "dark"
    return "secondary"


def _build_source_display(item):
    if item.related_audit:
        return f"Spezialaudit – {item.related_audit.processor.name} / {item.related_audit.audit_year}"

    if item.related_procedure_audit:
        if item.related_processing_activity:
            return (
                f"Hauptaudit – {item.related_procedure_audit.title} / "
                f"{item.related_procedure_audit.audit_year} / "
                f"Verfahren: {item.related_processing_activity.title}"
            )
        return (
            f"Hauptaudit – {item.related_procedure_audit.title} / "
            f"{item.related_procedure_audit.audit_year} / "
            f"Neues, noch nicht angelegtes Verfahren"
        )

    if item.related_legal_assessment:
        return f"Rechtliche Bewertung – {item.related_legal_assessment.processing_activity.title}"

    if item.related_processing_activity:
        return f"Verarbeitung – {item.related_processing_activity.title}"

    return item.get_source_type_display()


def _build_context_hint(item):
    hints = []

    if item.tenant:
        hints.append(f"Mandant: {item.tenant.name}")

    if item.related_procedure_audit:
        hints.append(f"Audit: {item.related_procedure_audit.title} ({item.related_procedure_audit.audit_year})")

        if item.related_processing_activity:
            hints.append(f"Verfahren: {item.related_processing_activity.title}")
        else:
            hints.append("Bezug: neu gemeldetes, noch nicht angelegtes Verfahren")

    elif item.related_audit:
        hints.append(f"Spezialaudit: {item.related_audit.processor.name} ({item.related_audit.audit_year})")

    elif item.related_processing_activity:
        hints.append(f"Verfahren: {item.related_processing_activity.title}")

    elif item.related_legal_assessment and item.related_legal_assessment.processing_activity_id:
        hints.append(f"Verfahren: {item.related_legal_assessment.processing_activity.title}")

    return " | ".join(hints)



@login_required
def action_list(request):
    show_history = request.GET.get("show_history") == "1"
    processing_id = request.GET.get("processing_id", "").strip()
    overdue_filter = request.GET.get("overdue", "").strip()
    priority_filter = request.GET.get("priority", "").strip()
    selected_processing = None

    qs = _tenant_filtered_action_queryset(request)

    if processing_id:
        selected_processing = get_object_or_404(ProcessingActivity, pk=processing_id)
        qs = qs.filter(
            Q(related_processing_activity_id=processing_id)
            | Q(related_legal_assessment__processing_activity_id=processing_id)
        )

    if priority_filter:
        qs = qs.filter(priority=priority_filter)

    if not show_history or overdue_filter == "1":
        qs = qs.filter(status__in=OPEN_ACTION_STATUSES)

    qs = _apply_sorting(qs, request)
    items = list(qs)

    today = timezone.localdate()
    for item in items:
        _enrich_action_due_state(item, today=today)
        item.resolved_target_area = _resolve_action_target_area(item)
        item.action_button_label = _get_action_button_label(item)
        item.status_badge_class = _get_status_badge_class(item)
        item.source_display = _build_source_display(item)
        item.context_hint = _build_context_hint(item)
        item.belongs_to_archived_processing = bool(
            item.related_processing_activity
            and item.related_processing_activity.status == "archived"
        )

    if overdue_filter == "1":
        items = [item for item in items if item.is_overdue]
        items.sort(key=lambda item: (item.auto_due_date, item.get_priority_display(), item.title))

    return render(
        request,
        "actions/list.html",
        {
            "items": items,
            "current_sort": request.GET.get("sort", "status_open_priority"),
            "show_history": show_history,
            "processing_id": processing_id,
            "selected_processing": selected_processing,
            "overdue_filter": overdue_filter,
            "priority_filter": priority_filter,
            "priority_choices": ActionItem.Priority.choices,
        },
    )


@login_required
def action_create(request):
    if request.method == "POST":
        form = ActionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)

            active_tenant = get_effective_tenant(request)
            if active_tenant is not None:
                item.tenant = active_tenant
            elif request.user.tenant_id:
                item.tenant = request.user.tenant

            item.save()
            messages.success(request, "Die Maßnahme wurde erfolgreich angelegt.")
            return redirect("action_detail", pk=item.pk)
    else:
        form = ActionItemForm()

    return render(
        request,
        "actions/form.html",
        {
            "form": form,
            "page_title": "Neue Maßnahme",
            "submit_label": "Speichern",
        },
    )


@login_required
def action_detail(request, pk):
    item = get_object_or_404(_tenant_filtered_action_queryset(request), pk=pk)
    item.resolved_target_area = _resolve_action_target_area(item)
    item.source_display = _build_source_display(item)
    item.context_hint = _build_context_hint(item)
    return render(request, "actions/detail.html", {"item": item})


@login_required
def action_edit(request, pk):
    item = get_object_or_404(_tenant_filtered_action_queryset(request), pk=pk)
    target_area = _resolve_action_target_area(item)

    if target_area == ActionItem.Area.AUDIT:
        if item.related_procedure_audit:
            return redirect("procedure_audit_detail", pk=item.related_procedure_audit.pk)
        if item.related_audit:
            return redirect("audit_edit", pk=item.related_audit.pk)

    processing_pk = _get_processing_pk_for_action(item)

    if (
        item.related_procedure_audit
        and not item.related_processing_activity
        and target_area == ActionItem.Area.PROCESSING
    ):
        return redirect("procedure_audit_detail", pk=item.related_procedure_audit.pk)

    if target_area == ActionItem.Area.PROCESSING and processing_pk:
        return redirect("processing_edit", pk=processing_pk)

    if target_area == ActionItem.Area.LEGAL and processing_pk:
        return redirect("legal_assessment_edit", processing_id=processing_pk)

    if target_area == ActionItem.Area.DPIA and processing_pk:
        return redirect("dpia:dpia_detail", processing_id=processing_pk)

    if request.method == "POST":
        form = ActionItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)

            if not item.tenant_id:
                active_tenant = get_effective_tenant(request)
                if active_tenant is not None:
                    item.tenant = active_tenant
                elif request.user.tenant_id:
                    item.tenant = request.user.tenant

            item.save()
            messages.success(request, "Die Maßnahme wurde erfolgreich aktualisiert.")
            return redirect("action_detail", pk=item.pk)
    else:
        form = ActionItemForm(instance=item)

    return render(
        request,
        "actions/form.html",
        {
            "form": form,
            "page_title": f"Maßnahme bearbeiten: {item.title}",
            "submit_label": "Änderungen speichern",
            "item": item,
        },
    )


@login_required
def generate_actions_from_legal_assessment_view(request, pk):
    legal_assessment = get_object_or_404(LegalAssessment, pk=pk)

    actions = generate_actions_from_legal_assessment(legal_assessment)

    if actions:
        messages.success(
            request,
            f"{len(actions)} Maßnahme(n) wurden automatisch erstellt."
        )
    else:
        messages.info(
            request,
            "Es wurden keine neuen Maßnahmen erstellt."
        )

    return redirect("action_list")
