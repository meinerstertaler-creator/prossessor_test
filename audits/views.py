from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from actions.models import ActionItem
from core.tenant_utils import get_effective_tenant

from .forms import (
    AuditForm,
    AuditResponseForm,
    AuditStartForm,
    ProcedureAuditChecklistResponseForm,
    ProcedureAuditForm,
    ProcedureAuditItemForm,
    ProcedureAuditNewActivityForm,
)
from .models import (
    Audit,
    AuditQuestion,
    AuditResponse,
    ProcedureAudit,
    ProcedureAuditChecklistResponse,
    ProcedureAuditItem,
)
from .services import (
    build_current_open_items_snapshot,
    build_preliminary_audit_summary,
    build_preliminary_open_items_snapshot,
    build_procedure_audit_statistics,
    can_final_complete,
    can_preliminary_complete,
    can_procedure_review_final_complete,
    generate_actions_from_new_activities,
    generate_actions_from_procedure_audit,
    generate_actions_from_procedure_audit_checklist,
    get_open_audit_actions,
    mark_checklist_review_completed,
    mark_final_completed,
    mark_new_activities_review_completed,
    mark_preliminary_completed,
    mark_procedure_review_completed,
    mark_procedure_review_final_completed,
    sync_procedure_audit_items,
)


def _get_request_tenant(request):
    active_tenant = get_effective_tenant(request)

    if active_tenant is not None:
        return active_tenant

    if request.user.tenant_id:
        return request.user.tenant

    return None


def _tenant_filtered_audit_queryset(request):
    qs = Audit.objects.select_related("processor").order_by("-audit_year", "processor__name")
    active_tenant = get_effective_tenant(request)

    if request.user.is_superuser:
        if active_tenant is None:
            return qs
        return qs.filter(tenant=active_tenant)

    if request.user.tenant_id:
        return qs.filter(tenant=request.user.tenant)

    return qs.none()


def _tenant_filtered_procedure_audit_queryset(request, *, include_archived=False):
    qs = ProcedureAudit.objects.select_related("tenant").order_by("-audit_year", "-created_at", "title")

    if not include_archived:
        qs = qs.filter(is_archived=False)

    active_tenant = get_effective_tenant(request)

    if request.user.is_superuser:
        if active_tenant is None:
            return qs
        return qs.filter(tenant=active_tenant)

    if request.user.tenant_id:
        return qs.filter(tenant=request.user.tenant)

    return qs.none()


@login_required
def audit_dashboard(request):
    procedure_items = _tenant_filtered_procedure_audit_queryset(request)[:10]
    special_items = _tenant_filtered_audit_queryset(request)[:10]

    if request.method == "POST":
        form = AuditStartForm(request.POST)
        if form.is_valid():
            audit_kind = form.cleaned_data["audit_kind"]

            if audit_kind == "procedure_annual":
                return redirect("/audits/procedure/create/?audit_type=annual")
            if audit_kind == "procedure_event_based":
                return redirect("/audits/procedure/create/?audit_type=event_based")
            if audit_kind == "procedure_follow_up":
                return redirect("/audits/procedure/create/?audit_type=follow_up")
            if audit_kind == "special_processor":
                return redirect("/audits/special/create/?audit_type=annual")
    else:
        form = AuditStartForm(initial={"audit_kind": "procedure_annual"})

    return render(
        request,
        "audits/dashboard.html",
        {
            "form": form,
            "procedure_items": procedure_items,
            "special_items": special_items,
        },
    )


@login_required
def audit_list(request):
    items = _tenant_filtered_audit_queryset(request)
    return render(request, "audits/list.html", {"items": items})


@login_required
def audit_create(request):
    initial = {}
    requested_type = request.GET.get("audit_type")
    if requested_type in {
        Audit.AuditType.ANNUAL,
        Audit.AuditType.EVENT_BASED,
        Audit.AuditType.FOLLOW_UP,
    }:
        initial["audit_type"] = requested_type

    if "audit_year" not in initial:
        initial["audit_year"] = date.today().year

    if request.method == "POST":
        form = AuditForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)

            active_tenant = get_effective_tenant(request)
            if active_tenant is not None:
                item.tenant = active_tenant
            elif request.user.tenant_id:
                item.tenant = request.user.tenant

            item.save()
            messages.success(request, "Das Spezialaudit wurde erfolgreich angelegt.")
            return redirect("audit_detail", pk=item.pk)
    else:
        form = AuditForm(initial=initial)

    return render(
        request,
        "audits/form.html",
        {
            "form": form,
            "page_title": "Neues Spezialaudit",
            "submit_label": "Speichern",
        },
    )


@login_required
def audit_detail(request, pk):
    item = get_object_or_404(_tenant_filtered_audit_queryset(request), pk=pk)
    return render(request, "audits/detail.html", {"item": item})


@login_required
def audit_edit(request, pk):
    item = get_object_or_404(_tenant_filtered_audit_queryset(request), pk=pk)

    if request.method == "POST":
        form = AuditForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            if not item.tenant_id:
                active_tenant = get_effective_tenant(request)
                if active_tenant is not None:
                    item.tenant = active_tenant
                elif request.user.tenant_id:
                    item.tenant = request.user.tenant
            item.save()
            messages.success(request, "Das Spezialaudit wurde erfolgreich aktualisiert.")
            return redirect("audit_detail", pk=item.pk)
    else:
        form = AuditForm(instance=item)

    return render(
        request,
        "audits/form.html",
        {
            "form": form,
            "page_title": f"Spezialaudit bearbeiten: {item.processor.name} / {item.audit_year}",
            "submit_label": "Änderungen speichern",
            "item": item,
        },
    )


@login_required
def audit_responses(request, pk):
    audit = get_object_or_404(_tenant_filtered_audit_queryset(request), pk=pk)

    questions = AuditQuestion.objects.filter(is_active=True).order_by("category", "sort_order", "id")

    response_items = []
    for question in questions:
        response, _ = AuditResponse.objects.get_or_create(
            audit=audit,
            question=question,
            defaults={"tenant": audit.tenant},
        )
        if audit.tenant_id and not response.tenant_id:
            response.tenant = audit.tenant
            response.save()

        response_items.append(
            {
                "question": question,
                "form": AuditResponseForm(prefix=str(question.id), instance=response),
                "response": response,
            }
        )

    if request.method == "POST":
        forms_valid = True
        response_items = []

        for question in questions:
            response, _ = AuditResponse.objects.get_or_create(
                audit=audit,
                question=question,
                defaults={"tenant": audit.tenant},
            )

            form = AuditResponseForm(
                request.POST,
                prefix=str(question.id),
                instance=response,
            )

            if form.is_valid():
                saved = form.save(commit=False)
                if audit.tenant_id and not saved.tenant_id:
                    saved.tenant = audit.tenant
                saved.save()
            else:
                forms_valid = False

            response_items.append(
                {
                    "question": question,
                    "form": form,
                    "response": response,
                }
            )

        if forms_valid:
            messages.success(request, "Die Auditbewertungen wurden erfolgreich gespeichert.")
            return redirect("audit_responses", pk=audit.pk)

    return render(
        request,
        "audits/responses.html",
        {
            "audit": audit,
            "response_items": response_items,
        },
    )


@login_required
def create_actions_from_audit(request, pk):
    audit = get_object_or_404(_tenant_filtered_audit_queryset(request), pk=pk)

    responses = AuditResponse.objects.select_related("question").filter(
        audit=audit,
        action_required=True,
    )

    created_count = 0

    fallback_due_date = (
        audit.next_review_date
        or audit.due_date
        or audit.start_date
        or date.today()
    )

    for response in responses:
        title = f"Auditmaßnahme {audit.processor.name}: {response.question.question_text[:80]}"

        exists = ActionItem.objects.filter(
            source_type=ActionItem.SourceType.AUDIT,
            related_audit=audit,
            title=title,
        ).exists()

        if not exists:
            ActionItem.objects.create(
                tenant=audit.tenant,
                title=title,
                description=(
                    f"Automatisch erzeugte Maßnahme aus dem Audit {audit.audit_year} "
                    f"für den Auftragsverarbeiter {audit.processor.name}.\n\n"
                    f"Frage: {response.question.question_text}\n\n"
                    f"Kommentar: {response.comment or '—'}"
                ),
                source_type=ActionItem.SourceType.AUDIT,
                source_area=ActionItem.Area.AUDIT,
                target_area=ActionItem.Area.AUDIT,
                related_audit=audit,
                responsible_person="",
                due_date=fallback_due_date,
                priority=ActionItem.Priority.MEDIUM,
                status=ActionItem.Status.OPEN,
                notes="Automatisch aus Auditbewertung erzeugt.",
            )
            created_count += 1

    if created_count:
        messages.success(request, f"{created_count} Maßnahme(n) wurden aus dem Audit erzeugt.")
    else:
        messages.info(
            request,
            "Es wurden keine neuen Maßnahmen erzeugt. Entweder war nichts markiert oder die Maßnahmen existieren bereits.",
        )

    return redirect("audit_responses", pk=audit.pk)


@login_required
def procedure_audit_list(request):
    items = _tenant_filtered_procedure_audit_queryset(request)
    return render(request, "audits/procedure_audit_list.html", {"items": items})


@login_required
def procedure_audit_create(request):
    tenant = _get_request_tenant(request)
    if tenant is None:
        messages.error(
            request,
            "Ein verfahrensorientiertes Audit kann nur mit ausgewähltem Mandanten angelegt werden.",
        )
        return redirect("audit_dashboard")

    initial = {
        "audit_year": date.today().year,
        "audit_type": ProcedureAudit.AuditType.ANNUAL,
        "status": ProcedureAudit.Status.PLANNED,
    }
    requested_type = request.GET.get("audit_type")
    if requested_type in {
        ProcedureAudit.AuditType.ANNUAL,
        ProcedureAudit.AuditType.EVENT_BASED,
        ProcedureAudit.AuditType.FOLLOW_UP,
    }:
        initial["audit_type"] = requested_type

    if request.method == "POST":
        form = ProcedureAuditForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.tenant = tenant
            item.save()
            sync_procedure_audit_items(item)
            messages.success(request, "Das Audit wurde angelegt.")
            return redirect("procedure_audit_detail", pk=item.pk)
    else:
        form = ProcedureAuditForm(initial=initial)

    return render(
        request,
        "audits/procedure_audit_form.html",
        {
            "form": form,
            "page_title": "Audit anlegen",
            "submit_label": "Audit anlegen",
            "tenant": tenant,
        },
    )


@login_required
def procedure_audit_detail(request, pk):
    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    sync_procedure_audit_items(audit)

    stats = build_procedure_audit_statistics(audit)
    live_open_items = build_current_open_items_snapshot(audit)
    preliminary_summary_preview = build_preliminary_audit_summary(audit)
    preliminary_open_items_preview = build_preliminary_open_items_snapshot(audit)

    return render(
        request,
        "audits/procedure_audit_detail.html",
        {
            "item": audit,
            "audit": audit,
            "stats": stats,
            "live_open_items": live_open_items,
            "can_preliminary_complete": can_preliminary_complete(audit),
            "can_procedure_review_final_complete": can_procedure_review_final_complete(audit),
            "can_final_complete": can_final_complete(audit),
            "preliminary_summary_preview": preliminary_summary_preview,
            "preliminary_open_items_preview": preliminary_open_items_preview,
            "preliminary_snapshot_stats": audit.preliminary_statistics_snapshot or {},
            "preliminary_snapshot_open_items": audit.preliminary_open_items_snapshot or [],
            "open_audit_actions": get_open_audit_actions(audit),
            "checklist_questions_count": AuditQuestion.objects.filter(is_active=True).count(),
        },
    )


@login_required
def procedure_audit_edit(request, pk):
    item = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    if request.method == "POST":
        form = ProcedureAuditForm(request.POST, instance=item)
        if form.is_valid():
            saved = form.save()
            sync_procedure_audit_items(saved)
            messages.success(request, "Der Auditrahmen wurde aktualisiert.")
            return redirect("procedure_audit_detail", pk=saved.pk)
    else:
        form = ProcedureAuditForm(instance=item)

    return render(
        request,
        "audits/procedure_audit_form.html",
        {
            "form": form,
            "page_title": "Auditrahmen bearbeiten",
            "submit_label": "Auditrahmen speichern",
            "item": item,
            "tenant": item.tenant,
        },
    )


@login_required
def procedure_audit_items(request, pk):
    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    sync_procedure_audit_items(audit)

    items = list(
        audit.items.select_related("processing_activity").order_by(
            "processing_activity__title",
            "processing_activity__id",
        )
    )

    item_forms = []

    if request.method == "POST":
        forms_valid = True

        for audit_item in items:
            form = ProcedureAuditItemForm(
                request.POST,
                prefix=str(audit_item.id),
                instance=audit_item,
            )

            if form.is_valid():
                form.save()
            else:
                forms_valid = False

            item_forms.append(
                {
                    "audit_item": audit_item,
                    "form": form,
                }
            )

        if forms_valid:
            created_actions = generate_actions_from_procedure_audit(audit)

            if created_actions:
                messages.success(
                    request,
                    f"Die Verfahrensprüfung wurde gespeichert. {len(created_actions)} Maßnahme(n) wurden automatisch erzeugt.",
                )
            else:
                messages.success(
                    request,
                    "Die Verfahrensprüfung wurde gespeichert. Es waren keine neuen Maßnahmen anzulegen.",
                )

            return redirect("procedure_audit_items", pk=audit.pk)

    else:
        for audit_item in items:
            item_forms.append(
                {
                    "audit_item": audit_item,
                    "form": ProcedureAuditItemForm(
                        prefix=str(audit_item.id),
                        instance=audit_item,
                    ),
                }
            )

    return render(
        request,
        "audits/procedure_audit_items.html",
        {
            "audit": audit,
            "item_forms": item_forms,
            "stats": build_procedure_audit_statistics(audit),
            "live_open_items": build_current_open_items_snapshot(audit),
        },
    )


@login_required
def procedure_audit_items_complete(request, pk):
    if request.method != "POST":
        return redirect("procedure_audit_items", pk=pk)

    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    sync_procedure_audit_items(audit)
    generate_actions_from_procedure_audit(audit)

    unchecked_exists = audit.items.filter(
        review_status=ProcedureAuditItem.ReviewStatus.NOT_CHECKED
    ).exists()

    if unchecked_exists:
        messages.error(
            request,
            "Die Verfahrensprüfung kann erst vorläufig abgeschlossen werden, wenn kein Verfahren mehr auf „Noch nicht geprüft“ steht.",
        )
        return redirect("procedure_audit_items", pk=audit.pk)

    mark_procedure_review_completed(audit)
    messages.success(request, "Die Verfahrensprüfung wurde vorläufig abgeschlossen.")
    return redirect("procedure_audit_detail", pk=audit.pk)


@login_required
def procedure_review_final_complete(request, pk):
    if request.method != "POST":
        return redirect("procedure_audit_detail", pk=pk)

    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    if audit.procedure_review_completed_at is None:
        messages.error(
            request,
            "Der Abschnitt „Verfahren“ kann erst endgültig abgeschlossen werden, wenn er zuvor vorläufig abgeschlossen wurde.",
        )
        return redirect("procedure_audit_detail", pk=audit.pk)

    if not can_procedure_review_final_complete(audit):
        messages.error(
            request,
            "Der Abschnitt „Verfahren“ kann nicht endgültig abgeschlossen werden, solange noch offene Maßnahmen aus der Verfahrensprüfung bestehen.",
        )
        return redirect("procedure_audit_detail", pk=audit.pk)

    mark_procedure_review_final_completed(audit)
    messages.success(request, "Der Abschnitt „Verfahren“ wurde endgültig abgeschlossen.")
    return redirect("procedure_audit_detail", pk=audit.pk)


@login_required
def procedure_audit_new_activities(request, pk):
    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    return render(
        request,
        "audits/procedure_audit_new_activities.html",
        {
            "audit": audit,
            "items": audit.new_activities.all(),
            "stats": build_procedure_audit_statistics(audit),
        },
    )


@login_required
def procedure_audit_new_activity_create(request, pk):
    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    if request.method == "POST":
        form = ProcedureAuditNewActivityForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.audit = audit
            item.tenant = audit.tenant
            item.save()

            if audit.new_activities.exists():
                audit.new_procedures_reported = True
                audit.save(update_fields=["new_procedures_reported", "updated_at"])

            created_actions = generate_actions_from_new_activities(audit)

            if created_actions:
                messages.success(
                    request,
                    f"Das neue Verfahren wurde erfasst. {len(created_actions)} Maßnahme(n) wurden automatisch erzeugt.",
                )
            else:
                messages.success(request, "Das neue Verfahren wurde erfasst.")

            return redirect("procedure_audit_new_activities", pk=audit.pk)
    else:
        form = ProcedureAuditNewActivityForm()

    return render(
        request,
        "audits/procedure_audit_new_activity_form.html",
        {
            "audit": audit,
            "form": form,
            "page_title": "Neues Verfahren im Audit erfassen",
            "submit_label": "Verfahren erfassen",
        },
    )


@login_required
def procedure_audit_new_activities_complete(request, pk):
    if request.method != "POST":
        return redirect("procedure_audit_new_activities", pk=pk)

    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    generate_actions_from_new_activities(audit)
    mark_new_activities_review_completed(audit)

    messages.success(
        request,
        "Der Abschnitt „Neue Verfahren“ wurde vorläufig abgeschlossen.",
    )
    return redirect("procedure_audit_detail", pk=audit.pk)


@login_required
def procedure_audit_checklist(request, pk):
    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    questions = AuditQuestion.objects.filter(is_active=True).order_by(
        "category",
        "sort_order",
        "id",
    )

    response_items = []

    if request.method == "POST":
        forms_valid = True

        for question in questions:
            response, _ = ProcedureAuditChecklistResponse.objects.get_or_create(
                procedure_audit=audit,
                question=question,
                defaults={"tenant": audit.tenant},
            )

            form = ProcedureAuditChecklistResponseForm(
                request.POST,
                prefix=str(question.id),
                instance=response,
            )

            if form.is_valid():
                saved = form.save(commit=False)
                if audit.tenant_id and not saved.tenant_id:
                    saved.tenant = audit.tenant
                saved.procedure_audit = audit
                saved.question = question
                saved.save()
            else:
                forms_valid = False

            response_items.append(
                {
                    "question": question,
                    "form": form,
                    "response": response,
                }
            )

        if forms_valid:
            created_actions = generate_actions_from_procedure_audit_checklist(audit)

            if created_actions:
                messages.success(
                    request,
                    f"Die allgemeine Audit-Checkliste wurde gespeichert. "
                    f"{len(created_actions)} Maßnahme(n) wurden automatisch erzeugt.",
                )
            else:
                messages.success(
                    request,
                    "Die allgemeine Audit-Checkliste wurde gespeichert. "
                    "Es waren keine neuen Maßnahmen anzulegen.",
                )

            return redirect("procedure_audit_checklist", pk=audit.pk)

    else:
        for question in questions:
            response, _ = ProcedureAuditChecklistResponse.objects.get_or_create(
                procedure_audit=audit,
                question=question,
                defaults={"tenant": audit.tenant},
            )

            response_items.append(
                {
                    "question": question,
                    "form": ProcedureAuditChecklistResponseForm(
                        prefix=str(question.id),
                        instance=response,
                    ),
                    "response": response,
                }
            )

    return render(
        request,
        "audits/procedure_audit_checklist.html",
        {
            "audit": audit,
            "response_items": response_items,
        },
    )


@login_required
def procedure_audit_checklist_complete(request, pk):
    if request.method != "POST":
        return redirect("procedure_audit_checklist", pk=pk)

    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    questions_count = AuditQuestion.objects.filter(is_active=True).count()
    responses_count = ProcedureAuditChecklistResponse.objects.filter(
        procedure_audit=audit,
        question__is_active=True,
    ).exclude(rating="").count()

    if questions_count and responses_count < questions_count:
        messages.error(
            request,
            "Die allgemeine Audit-Checkliste kann erst abgeschlossen werden, "
            "wenn alle aktiven Fragen bewertet wurden.",
        )
        return redirect("procedure_audit_checklist", pk=audit.pk)

    generate_actions_from_procedure_audit_checklist(audit)
    mark_checklist_review_completed(audit)

    messages.success(
        request,
        "Der Abschnitt „Allgemeine Audit-Checkliste“ wurde vorläufig abgeschlossen.",
    )
    return redirect("procedure_audit_detail", pk=audit.pk)


@login_required
def procedure_audit_preliminary_complete(request, pk):
    if request.method != "POST":
        return redirect("procedure_audit_detail", pk=pk)

    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    generate_actions_from_procedure_audit(audit)
    generate_actions_from_new_activities(audit)
    generate_actions_from_procedure_audit_checklist(audit)

    if not can_preliminary_complete(audit):
        messages.error(
            request,
            "Das Audit kann erst vorläufig abgeschlossen werden, wenn Verfahrensprüfung, Abschnitt „Neue Verfahren“ und Checkliste vorläufig abgeschlossen sind.",
        )
        return redirect("procedure_audit_detail", pk=audit.pk)

    mark_preliminary_completed(audit)
    messages.success(request, "Das Audit wurde vorläufig abgeschlossen.")
    return redirect("procedure_audit_detail", pk=audit.pk)


@login_required
def procedure_audit_final_complete(request, pk):
    if request.method != "POST":
        return redirect("procedure_audit_detail", pk=pk)

    audit = get_object_or_404(
        _tenant_filtered_procedure_audit_queryset(request, include_archived=True),
        pk=pk,
    )

    if audit.preliminary_completed_at is None:
        messages.error(
            request,
            "Das Audit kann erst beendet werden, wenn es zuvor vorläufig abgeschlossen wurde.",
        )
        return redirect("procedure_audit_detail", pk=audit.pk)

    if not can_final_complete(audit):
        messages.error(
            request,
            "Das Jahresaudit kann nicht beendet werden, solange noch auditbezogene Maßnahmen offen sind.",
        )
        return redirect("procedure_audit_detail", pk=audit.pk)

    mark_final_completed(audit)
    messages.success(request, f"Das Jahresaudit {audit.audit_year} wurde beendet.")
    return redirect("procedure_audit_detail", pk=audit.pk)