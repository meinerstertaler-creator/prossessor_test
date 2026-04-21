from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from actions.models import ActionItem
from legal.models import LegalAssessment
from processing.models import ProcessingActivity

from .tenant_utils import get_effective_tenant


def _get_post_switch_redirect(request):
    referer = request.META.get("HTTP_REFERER", "")
    parsed = urlparse(referer)
    path = parsed.path or ""

    redirect_map = [
        ("/audits/procedure/", "/audits/procedure/"),
        ("/audits/special/", "/audits/special/"),
        ("/audits/", "/audits/"),
        ("/actions/", "/actions/"),
        ("/processing/", "/processing/"),
        ("/processors/", "/processors/"),
        ("/documents/", "/documents/"),
        ("/reports/", "/reports/"),
        ("/legal/", "/legal/"),
        ("/dpia/", "/dpia/"),
        ("/knowledge/", "/knowledge/"),
        ("/core/", "/core/"),
    ]

    for prefix, target in redirect_map:
        if path.startswith(prefix):
            return target

    return "/core/"


@login_required
def dashboard(request):
    processing_qs = ProcessingActivity.objects.all()
    actions_qs = ActionItem.objects.all()
    legal_qs = LegalAssessment.objects.all()

    tenant = get_effective_tenant(request)

    if tenant:
        processing_qs = processing_qs.filter(tenant=tenant)
        actions_qs = actions_qs.filter(tenant=tenant)
        legal_qs = legal_qs.filter(tenant=tenant)

    dpia_required_count = 0
    for item in processing_qs.select_related("dpia_check"):
        dpia_check = getattr(item, "dpia_check", None)
        if dpia_check and dpia_check.recommendation in {"mandatory", "recommended"}:
            dpia_required_count += 1

    context = {
        "processing_count": processing_qs.count(),
        "processing_open_count": processing_qs.filter(review_completed_at__isnull=True).count(),
        "dpia_required_count": dpia_required_count,
        "third_info_required_count": processing_qs.filter(third_party_info_required=True).count(),
        "actions_open_count": actions_qs.filter(
            status__in=[
                ActionItem.Status.OPEN,
                ActionItem.Status.IN_PROGRESS,
                ActionItem.Status.WAITING,
                ActionItem.Status.FOLLOW_UP,
            ]
        ).count(),
        "lia_open_count": legal_qs.filter(
            legal_basis=LegalAssessment.LegalBasis.LEGITIMATE_INTERESTS,
            legitimate_interest_completed=False,
        ).count(),
        "recent_processing": processing_qs.order_by("-updated_at")[:10],
        "recent_actions": actions_qs.order_by("-created_at")[:10],
    }

    return render(request, "core/dashboard.html", context)


@login_required
def set_active_tenant(request):
    if request.method != "POST":
        return redirect("core:dashboard")

    if not request.user.is_superuser:
        messages.error(request, "Mandantenauswahl nur für Admins möglich.")
        return redirect("core:dashboard")

    tenant_id = request.POST.get("tenant_id")

    if tenant_id:
        request.session["active_tenant_id"] = tenant_id
        messages.success(request, "Mandant gewechselt.")
    else:
        request.session.pop("active_tenant_id", None)
        messages.success(request, "Mandantenfilter aufgehoben.")

    return redirect(_get_post_switch_redirect(request))