from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from processing.models import ProcessingActivity


@login_required
def reports_home(request):
    return render(request, "reports/index.html")


@login_required
def processing_report(request):
    items = ProcessingActivity.objects.select_related("department").order_by("internal_id")

    status = request.GET.get("status", "").strip()
    if status:
        items = items.filter(status=status)

    context = {
        "items": items,
        "status": status,
        "status_choices": ProcessingActivity.Status.choices,
    }
    return render(request, "reports/processing_report.html", context)