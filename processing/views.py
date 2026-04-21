from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from actions.models import ActionItem
from core.tenant_utils import get_effective_tenant
from .forms import ProcessingActivityForm
from .models import Department, ProcessingActivity
from .services import (
    archive_processing_activity,
    close_resolved_processing_actions,
    generate_processing_actions,
    reactivate_processing_activity,
)


def _tenant_filtered_processing_queryset(request):
    qs = ProcessingActivity.objects.select_related(
        "department",
        "tenant",
        "standard_case",
        "template_origin",
        "archived_by",
        "legal_record",
        "dpia",
        "dpia_check",
    ).order_by("internal_id", "title")

    active_tenant = get_effective_tenant(request)

    if request.user.is_superuser:
        if active_tenant is None:
            return qs
        return qs.filter(tenant=active_tenant)

    if request.user.tenant_id:
        return qs.filter(tenant=request.user.tenant)

    return qs.none()


def _available_departments_for_request(request, processing_activity=None):
    active_tenant = get_effective_tenant(request)

    if request.user.is_superuser:
        if active_tenant is not None:
            return active_tenant.department_set.all().order_by("name")

        if processing_activity and processing_activity.tenant_id:
            return processing_activity.tenant.department_set.all().order_by("name")

        return Department.objects.select_related("tenant").order_by("name")

    if request.user.tenant_id:
        return request.user.tenant.department_set.all().order_by("name")

    if processing_activity and processing_activity.tenant_id:
        return processing_activity.tenant.department_set.all().order_by("name")

    return Department.objects.none()


def _resolve_tenant_for_request(request):
    active_tenant = get_effective_tenant(request)

    if active_tenant is not None:
        return active_tenant

    if request.user.tenant_id:
        return request.user.tenant

    return None


def _get_template_initial_data(template, request):
    if not template:
        return {}

    initial = {
        "title": template.title,
        "purpose": template.purpose,
        "description": template.description,
        "data_subject_categories": template.data_subject_categories,
        "personal_data_categories": template.personal_data_categories,
        "recipients": template.recipients,
        "retention_period": template.retention_period,
        "tom_summary": template.tom_summary,
    }

    tenant = _resolve_tenant_for_request(request)
    if tenant and template.department:
        department = tenant.department_set.filter(name__iexact=template.department.strip()).first()
        if department:
            initial["department"] = department.pk

    return initial


def _apply_template_to_processing_activity(item, template, request):
    if not template:
        return item

    if not item.title:
        item.title = template.title

    if not item.purpose:
        item.purpose = template.purpose

    if not item.description:
        item.description = template.description

    if not item.data_subject_categories:
        item.data_subject_categories = template.data_subject_categories

    if not item.personal_data_categories:
        item.personal_data_categories = template.personal_data_categories

    if not item.recipients:
        item.recipients = template.recipients

    if not item.retention_period:
        item.retention_period = template.retention_period

    if not item.tom_summary:
        item.tom_summary = template.tom_summary

    if not item.template_origin_id:
        item.template_origin = template

    if not item.department_id and template.department:
        tenant = _resolve_tenant_for_request(request)
        if tenant:
            department = tenant.department_set.filter(name__iexact=template.department.strip()).first()
            if department:
                item.department = department

    return item


def _enrich_processing_item_with_dpia_display(item):
    legal_record = getattr(item, "legal_record", None)
    dpia_check = getattr(item, "dpia_check", None)

    item.dpia_status_label = "DSFA nicht geprüft"
    item.dpia_status_badge_class = "secondary"
    item.dpia_status_detail = ""

    if legal_record and legal_record.no_dpia_check_required_reason:
        item.dpia_status_label = "DSFA nicht erforderlich"
        item.dpia_status_badge_class = "success"
        item.dpia_status_detail = legal_record.get_no_dpia_check_required_reason_display()
        return item

    if dpia_check:
        recommendation = dpia_check.recommendation

        if recommendation == "mandatory":
            item.dpia_status_label = "DSFA erforderlich"
            item.dpia_status_badge_class = "danger"
            item.dpia_status_detail = dpia_check.recommendation_reason
            return item

        if recommendation == "recommended":
            item.dpia_status_label = "DSFA empfohlen"
            item.dpia_status_badge_class = "warning"
            item.dpia_status_detail = dpia_check.recommendation_reason
            return item

        if recommendation == "not_required":
            item.dpia_status_label = "DSFA nicht erforderlich"
            item.dpia_status_badge_class = "success"
            item.dpia_status_detail = "Ergebnis einer dokumentierten DSFA-Prüfung"
            return item

        item.dpia_status_label = "DSFA nicht geprüft"
        item.dpia_status_badge_class = "secondary"
        item.dpia_status_detail = "Es liegt noch keine dokumentierte DSFA-Prüfung vor."
        return item

    item.dpia_status_label = "DSFA nicht geprüft"
    item.dpia_status_badge_class = "secondary"
    item.dpia_status_detail = "Es liegt noch keine dokumentierte DSFA-Prüfung vor."
    return item


@login_required
def processing_list(request):
    items = _tenant_filtered_processing_queryset(request)

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    department = request.GET.get("department", "").strip()
    review_status = request.GET.get("review_status", "").strip()
    third_party = request.GET.get("third_party", "").strip()
    reminder = request.GET.get("reminder", "").strip()

    if search:
        items = items.filter(title__icontains=search) | items.filter(internal_id__icontains=search)

    if status:
        items = items.filter(status=status)

    if department:
        items = items.filter(department_id=department)

    if review_status:
        items = items.filter(review_status=review_status)

    if third_party == "yes":
        items = items.filter(third_party_info_required=True)

    if reminder == "due":
        items = items.filter(reminder_due_at__isnull=False)

    items = list(items)
    for item in items:
        _enrich_processing_item_with_dpia_display(item)

    context = {
        "items": items,
        "search": search,
        "status": status,
        "department": department,
        "review_status": review_status,
        "third_party": third_party,
        "reminder": reminder,
        "status_choices": ProcessingActivity.Status.choices,
        "review_status_choices": ProcessingActivity.ReviewStatus.choices,
        "departments": _available_departments_for_request(request),
    }
    return render(request, "processing/list.html", context)


@login_required
def processing_create(request):
    department_queryset = _available_departments_for_request(request)

    if request.method == "POST":
        form = ProcessingActivityForm(request.POST, show_template_field=True)
        form.fields["department"].queryset = department_queryset

        selected_template = None
        if "template_source" in form.fields:
            selected_template = form.fields["template_source"].queryset.filter(
                pk=request.POST.get("template_source")
            ).first()

        if request.POST.get("load_template") == "1":
            template_initial = _get_template_initial_data(selected_template, request)
            preserved_values = request.POST.copy()

            for field_name, field_value in template_initial.items():
                if not preserved_values.get(field_name):
                    preserved_values[field_name] = field_value

            form = ProcessingActivityForm(
                preserved_values,
                show_template_field=True,
            )
            form.fields["department"].queryset = department_queryset

            if selected_template and "template_source" in form.fields:
                form.fields["template_source"].initial = selected_template.pk

            messages.success(request, "Die Verfahrensvorlage wurde in das Formular übernommen.")

            return render(
                request,
                "processing/form.html",
                {
                    "form": form,
                    "page_title": "Neues Verfahren",
                    "submit_label": "Speichern",
                    "is_create_view": True,
                    "department_choices_available": department_queryset.exists(),
                },
            )

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.updated_by = request.user

            active_tenant = _resolve_tenant_for_request(request)
            if active_tenant is not None:
                item.tenant = active_tenant

            selected_template = form.cleaned_data.get("template_source")
            item = _apply_template_to_processing_activity(item, selected_template, request)

            if not item.tenant_id and item.department_id and item.department.tenant_id:
                item.tenant = item.department.tenant

            item.save()
            action_result = generate_processing_actions(item)
            close_resolved_processing_actions(item)

            messages.success(request, "Das Verfahren wurde erfolgreich angelegt.")

            if action_result["created_titles"]:
                messages.info(
                    request,
                    "Neue Maßnahme(n) hinzugefügt: " + ", ".join(action_result["created_titles"])
                )

            if action_result["updated_titles"]:
                messages.info(
                    request,
                    "Bestehende Maßnahme(n) aktualisiert: " + ", ".join(action_result["updated_titles"])
                )

            return redirect("processing_detail", pk=item.pk)
    else:
        form = ProcessingActivityForm(show_template_field=True)
        form.fields["department"].queryset = department_queryset

    return render(
        request,
        "processing/form.html",
        {
            "form": form,
            "page_title": "Neues Verfahren",
            "submit_label": "Speichern",
            "is_create_view": True,
            "department_choices_available": department_queryset.exists(),
        },
    )


@login_required
def processing_detail(request, pk):
    item = get_object_or_404(_tenant_filtered_processing_queryset(request), pk=pk)
    _enrich_processing_item_with_dpia_display(item)

    open_actions = (
        ActionItem.objects.filter(
            related_processing_activity=item,
            status__in=[
                ActionItem.Status.OPEN,
                ActionItem.Status.IN_PROGRESS,
                ActionItem.Status.WAITING,
                ActionItem.Status.FOLLOW_UP,
            ],
        )
        .annotate(
            priority_sort=Case(
                When(priority=ActionItem.Priority.HIGH, then=Value(0)),
                When(priority=ActionItem.Priority.MEDIUM, then=Value(1)),
                When(priority=ActionItem.Priority.LOW, then=Value(2)),
                default=Value(9),
                output_field=IntegerField(),
            ),
            due_date_is_null=Case(
                When(due_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        .order_by("priority_sort", "due_date_is_null", "due_date", "title")
    )

    open_action_count = open_actions.count()

    review_completed = item.review_status == item.ReviewStatus.COMPLETED
    review_in_progress = item.review_status == item.ReviewStatus.IN_PROGRESS

    procedure_is_complete = (
        item.status != item.Status.ARCHIVED
        and open_action_count == 0
        and review_completed
        and (
            item.dpia_status_label in [
                "DSFA durchgeführt",
                "DSFA nicht erforderlich",
            ]
        )
        and not item.third_party_info_required
    )

    return render(
        request,
        "processing/detail.html",
        {
            "item": item,
            "open_actions": open_actions,
            "open_action_count": open_action_count,
            "review_completed": review_completed,
            "review_in_progress": review_in_progress,
            "procedure_is_complete": procedure_is_complete,
        },
    )


@login_required
def processing_edit(request, pk):
    item = get_object_or_404(_tenant_filtered_processing_queryset(request), pk=pk)
    department_queryset = _available_departments_for_request(request, processing_activity=item)

    if request.method == "POST":
        if request.POST.get("mark_third_party_requested") == "1":
            item.third_party_info_requested_at = timezone.now()
            item.updated_by = request.user
            item.save(update_fields=["third_party_info_requested_at", "updated_by", "updated_at"])
            messages.success(request, "Drittinformationen wurden als angefordert markiert.")
            return redirect("processing_edit", pk=item.pk)

        form = ProcessingActivityForm(request.POST, instance=item, show_template_field=False)
        form.fields["department"].queryset = department_queryset

        if form.is_valid():
            item = form.save(commit=False)
            item.updated_by = request.user

            if not item.tenant_id:
                active_tenant = _resolve_tenant_for_request(request)
                if active_tenant is not None:
                    item.tenant = active_tenant
                elif item.department_id and item.department.tenant_id:
                    item.tenant = item.department.tenant

            item.save()
            action_result = generate_processing_actions(item)
            close_resolved_processing_actions(item)

            messages.success(request, "Das Verfahren wurde erfolgreich aktualisiert.")

            if action_result["created_titles"]:
                messages.info(
                    request,
                    "Neue Maßnahme(n) hinzugefügt: " + ", ".join(action_result["created_titles"])
                )

            if action_result["updated_titles"]:
                messages.info(
                    request,
                    "Bestehende Maßnahme(n) aktualisiert: " + ", ".join(action_result["updated_titles"])
                )

            return redirect("processing_edit", pk=item.pk)
    else:
        form = ProcessingActivityForm(instance=item, show_template_field=False)
        form.fields["department"].queryset = department_queryset

    return render(
        request,
        "processing/form.html",
        {
            "form": form,
            "page_title": "Verfahren bearbeiten",
            "submit_label": "Speichern",
            "item": item,
            "is_create_view": False,
            "department_choices_available": department_queryset.exists(),
        },
    )


@login_required
def processing_archive(request, pk):
    item = get_object_or_404(_tenant_filtered_processing_queryset(request), pk=pk)

    if request.method == "POST":
        archive_processing_activity(
            processing_activity=item,
            user=request.user,
        )
        messages.success(request, "Das Verfahren wurde archiviert.")

    return redirect("processing_list")


@login_required
def processing_reactivate(request, pk):
    item = get_object_or_404(_tenant_filtered_processing_queryset(request), pk=pk)

    if request.method == "POST":
        reactivate_processing_activity(
            processing_activity=item,
            user=request.user,
        )
        messages.success(request, "Das Verfahren wurde reaktiviert.")

    return redirect("processing_list")


@login_required
def processing_mark_third_party_requested(request, pk):
    item = get_object_or_404(_tenant_filtered_processing_queryset(request), pk=pk)

    if request.method == "POST":
        item.third_party_info_requested_at = timezone.now()
        item.updated_by = request.user
        item.save(update_fields=["third_party_info_requested_at", "updated_by", "updated_at"])
        messages.success(request, "Drittinformationen wurden als angefordert markiert.")

    return redirect("processing_edit", pk=item.pk)