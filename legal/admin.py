from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import LegalAssessment


@admin.register(LegalAssessment)
class LegalAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "processing_activity",
        "tenant",
        "legal_basis",
        "risk_level",
        "dpia_status_display",
        "updated_at",
    )
    list_filter = (
        "legal_basis",
        "special_legal_basis",
        "risk_level",
        "no_dpia_check_required_reason",
    )
    search_fields = (
        "processing_activity__title",
        "processing_activity__internal_id",
        "legal_assessment_text",
        "open_issues",
    )
    readonly_fields = ("processing_link",)

    def dpia_status_display(self, obj):
        dpia_check = getattr(obj.processing_activity, "dpia_check", None)

        if dpia_check:
            return dpia_check.recommendation_label

        if obj.no_dpia_check_required_reason:
            return "Kein DSFA-Check erforderlich"

        return "Noch nicht geprüft"

    dpia_status_display.short_description = "DSFA-Status"

    def processing_link(self, obj):
        url = reverse("processing_detail", args=[obj.processing_activity.pk])
        return format_html('<a href="{}">Verfahren öffnen</a>', url)

    processing_link.short_description = "Verfahren"