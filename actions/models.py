from django.db import models

from accounts.models import Tenant
from audits.models import Audit, ProcedureAudit
from legal.models import LegalAssessment
from processing.models import ProcessingActivity
from processors.models import Processor


class ActionItem(models.Model):
    class SourceType(models.TextChoices):
        AUDIT = "audit", "Audit"
        PROCESSING = "processing", "Verarbeitungsvorgang"
        LEGAL_ASSESSMENT = "legal_assessment", "Rechtliche Bewertung"
        DPIA = "dpia", "DSFA"
        PROCESSOR = "processor", "Auftragsverarbeiter"

    class Area(models.TextChoices):
        PROCESSING = "processing", "Verfahren"
        LEGAL = "legal", "Rechtsbewertung"
        DPIA = "dpia", "DSFA"
        AUDIT = "audit", "Audit"
        DOCUMENT = "document", "Dokument"
        REPORT = "report", "Report"
        REQUEST = "request", "Anfrage"
        MANUAL = "manual", "Manuell"
        PROCESSOR = "processor", "Auftragsverarbeiter"

    class Priority(models.TextChoices):
        LOW = "low", "Niedrig"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"

    class Status(models.TextChoices):
        OPEN = "open", "Offen"
        IN_PROGRESS = "in_progress", "In Bearbeitung"
        WAITING = "waiting", "Wartet auf Rückmeldung"
        FOLLOW_UP = "follow_up", "Wiedervorlage"
        COMPLETED = "completed", "Erledigt"
        IRRELEVANT = "irrelevant", "Gegenstandslos"
        DISCARDED = "discarded", "Verworfen"

    class AuditSection(models.TextChoices):
        NONE = "", "Kein Auditabschnitt"
        PROCEDURE_REVIEW = "procedure_review", "Verfahrensprüfung"
        NEW_ACTIVITIES = "new_activities", "Neue Verfahren"
        GENERAL_REVIEW = "general_review", "Allgemeine Prüfung"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField()

    source_type = models.CharField(max_length=30, choices=SourceType.choices)

    source_area = models.CharField(
        max_length=20,
        choices=Area.choices,
        default=Area.PROCESSING,
    )
    target_area = models.CharField(
        max_length=20,
        choices=Area.choices,
        default=Area.PROCESSING,
    )

    audit_section = models.CharField(
        max_length=30,
        choices=AuditSection.choices,
        blank=True,
        default=AuditSection.NONE,
    )

    related_audit = models.ForeignKey(
        Audit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_procedure_audit = models.ForeignKey(
        ProcedureAudit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_processing_activity = models.ForeignKey(
        ProcessingActivity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_legal_assessment = models.ForeignKey(
        LegalAssessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_processor = models.ForeignKey(
        Processor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions",
    )

    responsible_person = models.CharField(max_length=255, blank=True)
    due_date = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    priority = models.CharField(max_length=20, choices=Priority.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    completion_date = models.DateField(null=True, blank=True)
    effectiveness_review = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-priority", "-created_at"]

    @property
    def is_open_status(self):
        return self.status in {
            self.Status.OPEN,
            self.Status.IN_PROGRESS,
            self.Status.WAITING,
            self.Status.FOLLOW_UP,
        }

    def __str__(self):
        return self.title