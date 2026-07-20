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
    Aufbewahrungstatbestand für das automatische Löschkonzept.

    Fachliche Idee:
    Nicht einzelne technische Datenarten wie "Namensdaten" bestimmen die Frist,
    sondern der rechtliche/fachliche Aufbewahrungstatbestand, z. B.:

    - Rechnung
    - Handelsbrief
    - Zivilvertrag
    - Lohnabrechnung
    - Zeiterfassung MiLoG
    - Patientenakte
    - Mandatsakte
    - Bewerbungsunterlagen

    Die typischen personenbezogenen Daten dieses Tatbestands werden später
    in die Datenkategorien des Verfahrens übernommen und können dort durch
    den Datenschutzbeauftragten ergänzt werden.

    Wichtig:
    Löschorte/Systeme enthalten keine Fristenlogik. Sie beschreiben nur,
    wo die jeweiligen Unterlagen/Daten später gelöscht oder geprüft werden müssen.
    """

    class PeriodUnit(models.TextChoices):
        IMMEDIATE = "immediate", "unverzüglich"
        DAYS = "days", "Tage"
        WEEKS = "weeks", "Wochen"
        MONTHS = "months", "Monate"
        YEARS = "years", "Jahre"
        CHECK = "check", "prüfen"

    class ReviewStatus(models.TextChoices):
        AUTOMATIC = "automatic", "automatisch anwendbar"
        CHECK = "check", "fachlich prüfen"
        LEGAL_REVIEW = "legal_review", "juristisch / Audit prüfen"

    name = models.CharField(
        "Aufbewahrungstatbestand",
        max_length=255,
        unique=True,
    )

    description = models.TextField(
        "Beschreibung",
        blank=True,
        help_text="Fachliche Beschreibung des Aufbewahrungstatbestands.",
    )

    typical_personal_data_categories = models.TextField(
        "Typische personenbezogene Daten",
        blank=True,
        help_text=(
            "Typische pbD / Datenkategorien, z. B. Namensdaten, Kontaktdaten, "
            "Rechnungsdaten, Beschäftigtendaten. Diese Angaben können später "
            "in das Verfahren übernommen und dort ergänzt werden."
        ),
    )

    retention_period_value = models.PositiveIntegerField(
        "Standardfrist",
        null=True,
        blank=True,
        help_text="Zahl der Frist, z. B. 3, 6 oder 10. Leer bei 'prüfen' oder 'unverzüglich'.",
    )

    retention_period_unit = models.CharField(
        "Fristeinheit",
        max_length=30,
        choices=PeriodUnit.choices,
        default=PeriodUnit.CHECK,
    )

    retention_trigger = models.CharField(
        "Fristbeginn / Auslöser",
        max_length=255,
        blank=True,
        help_text="Startzeitpunkt der Frist, z. B. Jahresende, Vertragsende, Ausscheiden, Behandlungsende.",
    )

    legal_basis = models.CharField(
        "Rechtsgrundlage / Quelle",
        max_length=255,
        blank=True,
        help_text="Rechtsgrundlage oder interner Quellenhinweis, z. B. HGB, AO, BGB, MiLoG, BRAO.",
    )

    review_status = models.CharField(
        "Prüfstatus",
        max_length=30,
        choices=ReviewStatus.choices,
        default=ReviewStatus.CHECK,
        help_text="Gibt an, ob der Tatbestand automatisch nutzbar ist oder fachlich/juristisch geprüft werden muss.",
    )

    review_note = models.TextField(
        "Prüfhinweis",
        blank=True,
        help_text="Hinweis für DSB, Audit, Revision oder WP, z. B. Vertragsende prüfen, Handelsbriefe abgrenzen.",
    )

    typical_storage_locations = models.TextField(
        "Typische Löschorte",
        blank=True,
        help_text=(
            "Optionale Orientierung aus der Stammdaten-/Excel-Liste, z. B. E-Mail-System, "
            "DMS, ERP, Papierakte. Die konkreten Löschorte werden später im Verfahren ausgewählt."
        ),
    )

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Aufbewahrungstatbestand"
        verbose_name_plural = "Aufbewahrungstatbestände"

    def __str__(self):
        return self.name

    @property
    def retention_display(self):
        if self.retention_period_unit == self.PeriodUnit.IMMEDIATE:
            return "unverzüglich"
        if self.retention_period_unit == self.PeriodUnit.CHECK:
            return "prüfen"
        if self.retention_period_value is None:
            return self.get_retention_period_unit_display()
        return f"{self.retention_period_value} {self.get_retention_period_unit_display()}"


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
        verbose_name = "Löschort / System"
        verbose_name_plural = "Löschorte / Systeme"

    def __str__(self):
        return self.name



class ProcessingRetentionAssignment(models.Model):
    """
    Zuordnung eines Aufbewahrungstatbestands zu einem Verfahren.

    Der Aufbewahrungstatbestand bestimmt Frist, Fristbeginn,
    Rechtsgrundlage, typische personenbezogene Daten und Prüfhinweise.
    Löschorte/Systeme werden davon getrennt dem Verfahren zugeordnet.
    """

    processing_activity = models.ForeignKey(
        ProcessingActivity,
        on_delete=models.CASCADE,
        related_name="retention_assignments",
        verbose_name="Verfahren",
    )

    data_object = models.ForeignKey(
        RetentionDataObject,
        on_delete=models.PROTECT,
        related_name="processing_assignments",
        verbose_name="Aufbewahrungstatbestand",
    )

    custom_note = models.TextField(
        "Hinweis zum Verfahren",
        blank=True,
        help_text="Optionale Konkretisierung oder Abweichung im konkreten Verfahren.",
    )

    is_active = models.BooleanField("aktiv", default=True)
    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("processing_activity", "data_object")
        ordering = ["processing_activity", "sort_order", "data_object__name"]
        verbose_name = "Aufbewahrungstatbestand im Verfahren"
        verbose_name_plural = "Aufbewahrungstatbestände in Verfahren"

    def __str__(self):
        return f"{self.processing_activity} – {self.data_object}"


class ProcessingStorageAssignment(models.Model):
    """
    Zuordnung eines Löschorts / Systems zu einem Verfahren.

    Der Löschort beeinflusst nicht die Aufbewahrungsfrist.
    Er dokumentiert nur, wo im Verfahren gespeichert und später
    gelöscht oder auf Löschung geprüft werden muss.
    """

    processing_activity = models.ForeignKey(
        ProcessingActivity,
        on_delete=models.CASCADE,
        related_name="storage_assignments",
        verbose_name="Verfahren",
    )

    storage_system = models.ForeignKey(
        RetentionStorageSystem,
        on_delete=models.PROTECT,
        related_name="processing_assignments",
        verbose_name="Löschort / System",
    )

    custom_note = models.CharField(
        "Ergänzende Bezeichnung / Hinweis",
        max_length=255,
        blank=True,
        help_text=(
            "Optionaler Freitext, z. B. konkrete Produktbezeichnung, "
            "Servername, Archivraum oder sonstige Konkretisierung."
        ),
    )

    is_active = models.BooleanField("aktiv", default=True)
    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("processing_activity", "storage_system")
        ordering = ["processing_activity", "sort_order", "storage_system__name"]
        verbose_name = "Löschort / System im Verfahren"
        verbose_name_plural = "Löschorte / Systeme in Verfahren"

    def __str__(self):
        label = f"{self.processing_activity} – {self.storage_system}"
        if self.custom_note:
            return f"{label} ({self.custom_note})"
        return label
