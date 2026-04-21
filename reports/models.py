from django.db import models

from accounts.models import Tenant
from audits.models import ProcedureAudit


class AuditReport(models.Model):
    class ReportType(models.TextChoices):
        PRELIMINARY = "preliminary", "Vorläufig"
        FINAL = "final", "Final"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="audit_reports",
    )
    procedure_audit = models.ForeignKey(
        ProcedureAudit,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.PRELIMINARY,
    )
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)

    statistics_snapshot = models.JSONField(default=dict, blank=True)
    actions_snapshot = models.JSONField(default=list, blank=True)

    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-generated_at", "-id"]

    def __str__(self):
        return self.title