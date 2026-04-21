from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from audits.models import ProcedureAudit
from core.tenant_utils import get_effective_tenant
from processing.models import ProcessingActivity

from .forms import ProcedureAuditReportNoteForm
from .services import (
    build_procedure_audit_report_context,
    generate_and_store_procedure_audit_report,
)


def _tenant_filtered_procedure_audit_queryset(request):
    qs = ProcedureAudit.objects.select_related("tenant").order_by("-audit_year", "-created_at", "title")
    active_tenant = get_effective_tenant(request)

    if request.user.is_superuser:
        if active_tenant is None:
            return qs
        return qs.filter(tenant=active_tenant)

    if request.user.tenant_id:
        return qs.filter(tenant=request.user.tenant)

    return qs.none()


@login_required
def reports_home(request):
    return render(request, "reports/index.html")


@login_required
def processing_report(request):
    active_tenant = get_effective_tenant(request)

    items = ProcessingActivity.objects.select_related("department").order_by("internal_id")

    if request.user.is_superuser:
        if active_tenant is not None:
            items = items.filter(tenant=active_tenant)
    elif request.user.tenant_id:
        items = items.filter(tenant=request.user.tenant)
    else:
        items = items.none()

    status = request.GET.get("status", "").strip()
    if status:
        items = items.filter(status=status)

    context = {
        "items": items,
        "status": status,
        "status_choices": ProcessingActivity.Status.choices,
        "active_tenant": active_tenant,
    }
    return render(request, "reports/processing_report.html", context)


@login_required
def procedure_audit_report_list(request):
    items = _tenant_filtered_procedure_audit_queryset(request)
    return render(
        request,
        "reports/procedure_audit_report_list.html",
        {
            "items": items,
        },
    )


@login_required
def procedure_audit_report(request, pk):
    audit = get_object_or_404(_tenant_filtered_procedure_audit_queryset(request), pk=pk)

    if request.method == "POST":
        form = ProcedureAuditReportNoteForm(request.POST)
        if form.is_valid():
            audit.auditor_report_note = form.cleaned_data["auditor_report_note"]
            audit.save(update_fields=["auditor_report_note", "updated_at"])
            generate_and_store_procedure_audit_report(audit)
            messages.success(request, "Bericht und Auditor-Freitext wurden gespeichert.")
            return redirect("procedure_audit_report", pk=audit.pk)
    else:
        form = ProcedureAuditReportNoteForm(
            initial={"auditor_report_note": audit.auditor_report_note}
        )

    context = build_procedure_audit_report_context(audit)
    context["form"] = form
    return render(request, "reports/audit_report_detail.html", context)


@login_required
def procedure_audit_report_generate(request, pk):
    if request.method != "POST":
        return redirect("procedure_audit_report", pk=pk)

    audit = get_object_or_404(_tenant_filtered_procedure_audit_queryset(request), pk=pk)
    generate_and_store_procedure_audit_report(audit)
    messages.success(request, "Die Berichtdatei wurde erzeugt.")
    return redirect("procedure_audit_report", pk=audit.pk)