from django.db import models

from accounts.models import Tenant
from processing.models import ProcessingActivity
from processors.models import Processor


class AuditQuestion(models.Model):
    class Category(models.TextChoices):
        CONTRACTUAL = "contractual", "Vertragslage"
        TOM = "tom", "TOM"
        SUBPROCESSORS = "subprocessors", "Unterauftragsverarbeiter"
        PRIVACY_ORGANISATION = "privacy_organisation", "Datenschutzorganisation"
        THIRD_COUNTRY = "third_country", "Drittlandtransfer"
        EVIDENCE = "evidence", "Nachweise"

    category = models.CharField(max_length=50, choices=Category.choices)
    question_text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "sort_order", "id"]

    def __str__(self):
        return self.question_text[:80]


class Audit(models.Model):
    class AuditType(models.TextChoices):
        ANNUAL = "annual", "Jahresaudit"
        EVENT_BASED = "event_based", "Anlassprüfung"
        FOLLOW_UP = "follow_up", "Nachprüfung"

    class Status(models.TextChoices):
        PLANNED = "planned", "Geplant"
        REQUESTED = "requested", "Angefordert"
        IN_PROGRESS = "in_progress", "In Bearbeitung"
        EVALUATED = "evaluated", "Bewertet"
        COMPLETED = "completed", "Abgeschlossen"

    class OverallResult(models.TextChoices):
        NO_FINDINGS = "no_findings", "Unauffällig"
        FINDINGS = "findings", "Mit Feststellungen"
        CRITICAL = "critical", "Kritisch"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    processor = models.ForeignKey(Processor, on_delete=models.CASCADE, related_name="audits")
    audit_year = models.PositiveIntegerField()
    audit_type = models.CharField(max_length=30, choices=AuditType.choices)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PLANNED)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    auditor_name = models.CharField(max_length=255, blank=True)
    overall_result = models.CharField(max_length=30, choices=OverallResult.choices, blank=True)
    summary = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    next_review_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["processor", "audit_year", "audit_type"],
                name="unique_audit_per_processor_year_type",
            )
        ]
        ordering = ["-audit_year", "processor__name"]

    def __str__(self):
        return f"{self.processor} - {self.audit_year} - {self.get_audit_type_display()}"


class AuditResponse(models.Model):
    class Rating(models.TextChoices):
        FULFILLED = "fulfilled", "Erfüllt"
        PARTIALLY_FULFILLED = "partially_fulfilled", "Teilweise erfüllt"
        NOT_FULFILLED = "not_fulfilled", "Nicht erfüllt"
        NOT_APPLICABLE = "not_applicable", "Nicht anwendbar"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(AuditQuestion, on_delete=models.CASCADE)
    rating = models.CharField(max_length=30, choices=Rating.choices, blank=True)
    comment = models.TextField(blank=True)
    evidence_available = models.BooleanField(default=False, verbose_name="Nachweis vorhanden")
    action_required = models.BooleanField(default=False, verbose_name="Maßnahme erforderlich")

    class Meta:
        unique_together = ("audit", "question")
        ordering = ["question__category", "question__sort_order", "question__id"]

    def __str__(self):
        return f"Antwort zu {self.question}"


class ProcedureAudit(models.Model):
    class AuditType(models.TextChoices):
        ANNUAL = "annual", "Jährliches Datenschutzaudit"
        EVENT_BASED = "event_based", "Anlassbezogenes Audit"
        FOLLOW_UP = "follow_up", "Nachaudit / Follow-up"

    class Status(models.TextChoices):
        PLANNED = "planned", "Geplant"
        IN_PROGRESS = "in_progress", "In Bearbeitung"
        PRELIMINARY_COMPLETED = "preliminary_completed", "Vorläufig abgeschlossen"
        COMPLETED = "completed", "Abgeschlossen"
        ARCHIVED = "archived", "Archiviert"

    class ExecutionType(models.TextChoices):
        ON_SITE = "on_site", "Vor Ort"
        VIDEO = "video", "Videokonferenz"
        HYBRID = "hybrid", "Hybrid"
        DOCUMENT_REVIEW = "document_review", "Dokumentenprüfung"

    class OverallResult(models.TextChoices):
        NO_FINDINGS = "no_findings", "Unauffällig"
        FINDINGS = "findings", "Mit Feststellungen"
        CRITICAL = "critical", "Kritisch"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="procedure_audits")
    title = models.CharField(max_length=255)
    audit_year = models.PositiveIntegerField()
    audit_type = models.CharField(max_length=30, choices=AuditType.choices)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PLANNED)

    audit_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    execution_type = models.CharField(
        max_length=30,
        choices=ExecutionType.choices,
        default=ExecutionType.ON_SITE,
    )
    auditor_name = models.CharField(max_length=255, blank=True)
    participants = models.TextField(blank=True)

    overall_result = models.CharField(max_length=30, choices=OverallResult.choices, blank=True)
    summary = models.TextField(blank=True)
    training_recommendations = models.TextField(blank=True)
    auditor_report_note = models.TextField(blank=True, verbose_name="Freitext Auditor für Bericht")

    new_procedures_reported = models.BooleanField(default=False)
    organisational_changes_reported = models.BooleanField(default=False)

    procedure_review_completed_at = models.DateTimeField(null=True, blank=True)
    procedure_review_final_completed_at = models.DateTimeField(null=True, blank=True)
    new_activities_review_completed_at = models.DateTimeField(null=True, blank=True)
    checklist_review_completed_at = models.DateTimeField(null=True, blank=True)

    preliminary_completed_at = models.DateTimeField(null=True, blank=True)
    final_completed_at = models.DateTimeField(null=True, blank=True)

    preliminary_report_summary = models.TextField(blank=True)
    preliminary_statistics_snapshot = models.JSONField(default=dict, blank=True)
    preliminary_open_items_snapshot = models.JSONField(default=list, blank=True)

    report_file = models.FileField(
        upload_to="reports/audits/",
        null=True,
        blank=True,
        verbose_name="Gespeicherte Berichtdatei",
    )
    report_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Bericht erzeugt am",
    )

    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-audit_year", "-created_at", "title"]

    def __str__(self):
        return f"{self.title} ({self.audit_year})"

    @property
    def has_new_procedures(self):
        return self.new_activities.exists()


class ProcedureAuditItem(models.Model):
    class ReviewStatus(models.TextChoices):
        NOT_CHECKED = "not_checked", "Noch nicht geprüft"
        UNCHANGED = "unchanged", "Unverändert"
        CHANGED = "changed", "Geändert"
        REVIEW_REQUIRED = "review_required", "Weiterer Prüfbedarf"
        DISCONTINUED = "discontinued", "Nicht mehr genutzt"

    audit = models.ForeignKey(
        ProcedureAudit,
        on_delete=models.CASCADE,
        related_name="items",
    )
    processing_activity = models.ForeignKey(
        ProcessingActivity,
        on_delete=models.CASCADE,
        related_name="procedure_audit_items",
    )

    review_status = models.CharField(
        max_length=30,
        choices=ReviewStatus.choices,
        default=ReviewStatus.NOT_CHECKED,
    )
    notes = models.TextField(blank=True)

    legal_review_required = models.BooleanField(
        default=False,
        verbose_name="Rechtsbewertung prüfen",
    )
    dpia_review_required = models.BooleanField(
        default=False,
        verbose_name="DSFA prüfen",
    )
    action_required = models.BooleanField(
        default=False,
        verbose_name="Maßnahme erforderlich",
    )

    class Meta:
        unique_together = ("audit", "processing_activity")
        ordering = ["processing_activity__title", "processing_activity__id"]

    def __str__(self):
        return f"{self.audit} - {self.processing_activity}"


class ProcedureAuditNewActivity(models.Model):
    audit = models.ForeignKey(
        ProcedureAudit,
        on_delete=models.CASCADE,
        related_name="new_activities",
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    title = models.CharField(max_length=255, verbose_name="Bezeichnung des neuen Verfahrens")
    department_hint = models.CharField(max_length=255, blank=True, verbose_name="Fachbereich / Bereich")
    contact_person = models.CharField(max_length=255, blank=True, verbose_name="Ansprechpartner")
    description = models.TextField(blank=True, verbose_name="Kurzbeschreibung")
    is_already_active = models.BooleanField(default=False, verbose_name="Bereits produktiv im Einsatz")
    requires_follow_up = models.BooleanField(default=True, verbose_name="Weitere Prüfung / Nachbearbeitung erforderlich")
    notes = models.TextField(blank=True, verbose_name="Weitere Hinweise")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title", "id"]

    def __str__(self):
        return self.title


class ProcedureAuditChecklistResponse(models.Model):
    class Rating(models.TextChoices):
        FULFILLED = "fulfilled", "Erfüllt"
        PARTIALLY_FULFILLED = "partially_fulfilled", "Teilweise erfüllt"
        NOT_FULFILLED = "not_fulfilled", "Nicht erfüllt"
        NOT_APPLICABLE = "not_applicable", "Nicht anwendbar"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    procedure_audit = models.ForeignKey(
        ProcedureAudit,
        on_delete=models.CASCADE,
        related_name="checklist_responses",
    )
    question = models.ForeignKey(AuditQuestion, on_delete=models.CASCADE)
    rating = models.CharField(max_length=30, choices=Rating.choices, blank=True)
    comment = models.TextField(blank=True)
    evidence_available = models.BooleanField(default=False, verbose_name="Nachweis vorhanden")
    action_required = models.BooleanField(default=False, verbose_name="Maßnahme erforderlich")

    class Meta:
        unique_together = ("procedure_audit", "question")
        ordering = ["question__category", "question__sort_order", "question__id"]

    def __str__(self):
        return f"Checklistenantwort zu {self.question}"