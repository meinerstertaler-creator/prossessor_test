from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import Tenant


class Department(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProcessingStandardCase(models.Model):
    class Category(models.TextChoices):
        GENERAL = "general", "Allgemein"
        HR = "hr", "Personal / Organisation"
        CORE_PROCESS = "core_process", "Fachprozess / Kerntätigkeit"
        COMMUNICATION = "communication", "Kommunikation / Zusammenarbeit"
        IT_SECURITY = "it_security", "IT / Sicherheit"
        MONITORING = "monitoring", "Überwachung / Tracking"
        DATA_TRANSFER = "data_transfer", "Datenflüsse / Externe"
        ANALYTICS = "analytics", "Analyse / Bewertung"
        SPECIAL = "special", "Spezialfall"

    class RiskHint(models.TextChoices):
        LOW = "low", "Eher niedrig"
        MEDIUM = "medium", "Eher mittel"
        HIGH = "high", "Eher hoch"

    name = models.CharField(max_length=255, unique=True)

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.GENERAL,
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    is_general = models.BooleanField(
        default=True,
        help_text="Allgemeiner Standardfall, der branchenübergreifend angezeigt werden kann.",
    )
    applies_to_legal = models.BooleanField(default=False)
    applies_to_medical = models.BooleanField(default=False)
    applies_to_industry = models.BooleanField(default=False)

    risk_hint = models.CharField(
        max_length=20,
        choices=RiskHint.choices,
        blank=True,
        help_text="Unverbindliche Risikotendenz für die erste Einordnung.",
    )

    dsfa_relevance_note = models.TextField(
        blank=True,
        help_text="Interner Hinweis zur DSFA-Relevanz oder typischen Einordnung.",
    )

    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Standardfall"
        verbose_name_plural = "Standardfälle"

    def __str__(self):
        return self.name


class ProcessingTemplate(models.Model):
    class TemplateGroup(models.TextChoices):
        GENERAL = "general", "Allgemein"
        MEDICAL = "medical", "Arztpraxis"
        LEGAL = "legal", "Rechtsanwaltskanzlei"

    title = models.CharField(max_length=255)

    template_group = models.CharField(
        max_length=20,
        choices=TemplateGroup.choices,
        default=TemplateGroup.GENERAL,
    )

    department = models.CharField(max_length=255, blank=True)
    purpose = models.TextField(blank=True)
    description = models.TextField(blank=True)

    data_subject_categories = models.TextField(blank=True)
    personal_data_categories = models.TextField(blank=True)

    recipients = models.TextField(blank=True)

    retention_period = models.CharField(max_length=255, blank=True)

    tom_summary = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["template_group", "title"]
        verbose_name = "Verfahrensvorlage"
        verbose_name_plural = "Verfahrensvorlagen"

    def __str__(self):
        return f"{self.get_template_group_display()} - {self.title}"


class ProcessingActivity(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        REVIEW = "review", "In Prüfung"
        ARCHIVED = "archived", "Archiviert"

    class ReviewStatus(models.TextChoices):
        NOT_STARTED = "not_started", "Noch nicht bewertet"
        IN_PROGRESS = "in_progress", "Bewertung begonnen"
        COMPLETED = "completed", "Abgeschlossen"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    internal_id = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=255)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    standard_case = models.ForeignKey(
        ProcessingStandardCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processing_activities",
    )
    standard_case_note = models.TextField(
        blank=True,
        help_text="Optionale Konkretisierung oder Ergänzung zum gewählten Standardfall.",
    )

    template_origin = models.ForeignKey(
        ProcessingTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="originated_processing_activities",
        help_text="Optionale Herkunft aus einer Verfahrensvorlage.",
    )

    purpose = models.TextField(blank=True)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    responsible_person = models.CharField(max_length=255, blank=True)

    systems_used = models.TextField(blank=True)

    data_subject_categories = models.TextField(blank=True)
    personal_data_categories = models.TextField(blank=True)

    special_category_data = models.BooleanField(default=False)
    special_category_description = models.TextField(blank=True)

    recipients = models.TextField(blank=True)

    third_country_transfer = models.BooleanField(default=False)
    third_country_description = models.TextField(blank=True)

    retention_period = models.CharField(max_length=255, blank=True)

    tom_summary = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processing_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processing_updated",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processing_archived",
    )

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.NOT_STARTED,
    )

    review_started_at = models.DateTimeField(null=True, blank=True)
    review_completed_at = models.DateTimeField(null=True, blank=True)

    third_party_info_required = models.BooleanField(default=False)
    third_party_info_requested_at = models.DateTimeField(null=True, blank=True)

    reminder_due_at = models.DateTimeField(null=True, blank=True)

    contact_person = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["internal_id", "title"]

    def __str__(self):
        return f"{self.internal_id} - {self.title}" if self.internal_id else self.title

    @property
    def is_reminder_due(self):
        return (
            self.review_status != self.ReviewStatus.COMPLETED
            and self.reminder_due_at is not None
            and self.reminder_due_at <= timezone.now()
        )

    @property
    def status_badge_class(self):
        if self.review_status == self.ReviewStatus.COMPLETED:
            return "success"
        if self.review_status == self.ReviewStatus.IN_PROGRESS:
            return "warning"
        return "secondary"

    @property
    def dpia_required(self):
        dpia_check = getattr(self, "dpia_check", None)
        if dpia_check:
            return dpia_check.recommendation in {"mandatory", "recommended"}
        return False

    @property
    def dpia_completed(self):
        dpia = getattr(self, "dpia", None)
        if not dpia:
            return False
        return bool(dpia.approved)

    def save(self, *args, **kwargs):
        now = timezone.now()

        if self.review_status == self.ReviewStatus.IN_PROGRESS and not self.review_started_at:
            self.review_started_at = now

        if self.review_status == self.ReviewStatus.COMPLETED:
            if not self.review_started_at:
                self.review_started_at = now
            if not self.review_completed_at:
                self.review_completed_at = now
        else:
            self.review_completed_at = None

        if not self.third_party_info_required:
            self.third_party_info_requested_at = None

        if self.status == self.Status.ARCHIVED and not self.archived_at:
            self.archived_at = now
        elif self.status != self.Status.ARCHIVED:
            self.archived_at = None
            self.archived_by = None

        super().save(*args, **kwargs)

        if not self.internal_id and self.pk:
            generated_internal_id = f"VVT-{self.pk:04d}"
            type(self).objects.filter(pk=self.pk).update(internal_id=generated_internal_id)
            self.internal_id = generated_internal_id


class TenantProcessingTemplateSetting(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="template_settings",
    )

    template = models.ForeignKey(
        ProcessingTemplate,
        on_delete=models.CASCADE,
        related_name="tenant_settings",
    )

    is_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tenant", "template")
        ordering = ["template__title"]
        verbose_name = "Mandanten-Vorlagensteuerung"
        verbose_name_plural = "Mandanten-Vorlagensteuerungen"

    def __str__(self):
        status = "aktiv" if self.is_enabled else "deaktiviert"
        return f"{self.tenant.name} - {self.template.title} ({status})"

# ---------------------------------------------------------------------------
# Löschkonzept / Retention Pilot V1
# ---------------------------------------------------------------------------
# Vorsichtiger Pilot:
# - keine bestehenden Felder werden entfernt
# - bestehende Freitexte bleiben erhalten
# - neue strukturierte Stammdaten für Löschobjekte, Systeme und Regeln
# - Verfahren bleiben Ausgangspunkt der Zuordnung
# ---------------------------------------------------------------------------


class RetentionDataObject(models.Model):
    """
    Strukturierter Katalog der Datenobjekte/Löschobjekte.

    Pilot-Beispiele:
    - E-Mail Handelsbrief
    - Rechnung
    - Softwareeintrag
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Löschobjekt"
        verbose_name_plural = "Löschobjekte"

    def __str__(self):
        return self.name


class RetentionStorageSystem(models.Model):
    """
    Strukturierter Katalog der Systeme / Speicherorte / Datenträger.

    Pilot-Beispiele:
    - Outlook / Exchange
    - DATEV
    - RA-MICRO
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    default_deletion_location = models.CharField(
        "Standard-Umsetzungshinweis",
        max_length=255,
        blank=True,
        help_text="Optionaler Standardhinweis zur praktischen Löschroutine in diesem System, z. B. Postfachregel, Archivroutine, Backup-Rotation.",
    )

    default_information_owner = models.CharField(
        max_length=255,
        blank=True,
        help_text="Typische Rolle, z. B. Verwaltung, Buchhaltung, Mandatsverantwortlicher.",
    )

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Speicherort / System"
        verbose_name_plural = "Speicherorte / Systeme"

    def __str__(self):
        return self.name


class RetentionRule(models.Model):
    """
    Standard-Löschregel.

    Logik:
        Löschobjekt + System/Speicherort -> Frist, Trigger, Rechtsgrund, Löschort

    Pilot-Beispiel:
        E-Mail Handelsbrief + Outlook / Exchange
        -> 6 Jahre, HGB, Postfach/Archiv
    """

    class PeriodUnit(models.TextChoices):
        IMMEDIATE = "immediate", "unverzüglich"
        DAYS = "days", "Tage"
        WEEKS = "weeks", "Wochen"
        MONTHS = "months", "Monate"
        YEARS = "years", "Jahre"
        CHECK = "check", "prüfen"

    data_object = models.ForeignKey(
        RetentionDataObject,
        on_delete=models.CASCADE,
        related_name="retention_rules",
    )

    storage_system = models.ForeignKey(
        RetentionStorageSystem,
        on_delete=models.CASCADE,
        related_name="retention_rules",
    )

    retention_period_value = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Zahl der Frist, z. B. 6 oder 10. Leer bei 'unverzüglich' oder 'prüfen'.",
    )

    retention_period_unit = models.CharField(
        max_length=30,
        choices=PeriodUnit.choices,
        default=PeriodUnit.CHECK,
    )

    trigger = models.CharField(
        max_length=255,
        blank=True,
        help_text="Startzeitpunkt der Frist, z. B. Jahresende, Vertragsende, Zweckfortfall.",
    )

    legal_basis = models.CharField(
        max_length=255,
        blank=True,
        help_text="Rechtsgrund / Hinweis, z. B. HGB, AO, BRAO, DSGVO.",
    )

    deletion_location = models.CharField(
        "Umsetzungshinweis / Löschroutine",
        max_length=255,
        blank=True,
        help_text="Optionaler Hinweis zur praktischen Umsetzung, z. B. Postfachregel, Archivroutine, Backup-Rotation. Der eigentliche Speicherort ist das ausgewählte System.",
    )

    information_owner_role = models.CharField(
        max_length=255,
        blank=True,
        help_text="Typischer Informationsinhaber / zuständige Rolle.",
    )

    requires_review = models.BooleanField(
        default=False,
        help_text="Markiert Regeln, die fachlich geprüft werden müssen.",
    )

    is_active = models.BooleanField(default=True)
    note = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("data_object", "storage_system")
        ordering = ["sort_order", "data_object__name", "storage_system__name"]
        verbose_name = "Löschregel"
        verbose_name_plural = "Löschregeln"

    def __str__(self):
        return f"{self.data_object} / {self.storage_system}"

    @property
    def retention_display(self):
        if self.retention_period_unit == self.PeriodUnit.IMMEDIATE:
            return "unverzüglich"
        if self.retention_period_unit == self.PeriodUnit.CHECK:
            return "prüfen"
        if self.retention_period_value is None:
            return self.get_retention_period_unit_display()
        return f"{self.retention_period_value} {self.get_retention_period_unit_display()}"


class ProcessingRetentionAssignment(models.Model):
    """
    Konkrete Zuordnung im Verfahren.

    Verfahren -> Löschobjekt -> System/Speicherort -> automatisch gefundene Löschregel

    Diese Tabelle ist später Grundlage für:
    - Löschübersicht
    - Report
    - Statusanzeige im Verfahren
    """

    class Status(models.TextChoices):
        COMPLETE = "complete", "Vollständig"
        CHECK = "check", "Prüfen"
        INCOMPLETE = "incomplete", "Unvollständig"
        NOT_APPLICABLE = "not_applicable", "Nicht einschlägig"

    processing_activity = models.ForeignKey(
        ProcessingActivity,
        on_delete=models.CASCADE,
        related_name="retention_assignments",
    )

    data_object = models.ForeignKey(
        RetentionDataObject,
        on_delete=models.PROTECT,
        related_name="processing_assignments",
    )

    storage_system = models.ForeignKey(
        RetentionStorageSystem,
        on_delete=models.PROTECT,
        related_name="processing_assignments",
    )

    applied_rule = models.ForeignKey(
        RetentionRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processing_assignments",
        help_text="Automatisch passende oder manuell gewählte Löschregel.",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.INCOMPLETE,
    )

    custom_note = models.TextField(
        blank=True,
        help_text="Hinweis oder Abweichung im konkreten Verfahren.",
    )

    na_reason = models.TextField(
        blank=True,
        help_text="Begründung, wenn kein Löschkonzept erforderlich ist.",
    )

    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("processing_activity", "data_object", "storage_system")
        ordering = ["processing_activity", "sort_order", "data_object__name"]
        verbose_name = "Löschzuordnung im Verfahren"
        verbose_name_plural = "Löschzuordnungen in Verfahren"

    def __str__(self):
        return f"{self.processing_activity} – {self.data_object} / {self.storage_system}"

    def save(self, *args, **kwargs):
        if not self.applied_rule_id and self.data_object_id and self.storage_system_id:
            self.applied_rule = RetentionRule.objects.filter(
                data_object=self.data_object,
                storage_system=self.storage_system,
                is_active=True,
            ).first()

        if self.status != self.Status.NOT_APPLICABLE:
            if self.applied_rule_id:
                self.status = self.Status.CHECK if self.applied_rule.requires_review else self.Status.COMPLETE
            else:
                self.status = self.Status.INCOMPLETE

        super().save(*args, **kwargs)

