from datetime import timedelta
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from actions.models import ActionItem
from legal.models import LegalAssessment
from processing.models import ProcessingActivity
from processors.models import Processor

from .tenant_utils import get_effective_tenant


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
    processor_qs = Processor.objects.all()

    tenant = get_effective_tenant(request)

    if tenant:
        processing_qs = processing_qs.filter(tenant=tenant)
        actions_qs = actions_qs.filter(tenant=tenant)
        legal_qs = legal_qs.filter(tenant=tenant)
        processor_qs = processor_qs.filter(tenant=tenant)

    dpia_required_count = 0
    for item in processing_qs.select_related("dpia_check"):
        dpia_check = getattr(item, "dpia_check", None)
        if dpia_check and dpia_check.recommendation in {"mandatory", "recommended"}:
            dpia_required_count += 1

    open_actions_qs = actions_qs.filter(status__in=OPEN_ACTION_STATUSES)

    today = timezone.localdate()
    open_actions = list(
        open_actions_qs.select_related(
            "related_processing_activity",
            "related_legal_assessment",
            "related_legal_assessment__processing_activity",
        ).order_by("-created_at")
    )

    for action in open_actions:
        _enrich_action_due_state(action, today=today)

    overdue_actions = [action for action in open_actions if action.is_overdue]
    overdue_actions.sort(key=lambda action: (action.auto_due_date, action.get_priority_display(), action.title))

    context = {
        "processing_count": processing_qs.count(),
        "processor_count": processor_qs.count(),
        "processing_open_count": processing_qs.filter(review_completed_at__isnull=True).count(),
        "dpia_required_count": dpia_required_count,
        "third_info_required_count": processing_qs.filter(third_party_info_required=True).count(),
        "open_actions_count": open_actions_qs.count(),
        "overdue_actions_count": len(overdue_actions),
        "overdue_actions": overdue_actions[:10],
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