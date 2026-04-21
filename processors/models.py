from django.db import models

from accounts.models import Tenant
from processing.models import Department


class ProviderRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Anbieterrolle"
        verbose_name_plural = "Anbieterrollen"

    def __str__(self):
        return self.name


class ProviderCatalogEntry(models.Model):
    name = models.CharField(max_length=255, unique=True)
    legal_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    default_contact_person = models.CharField(max_length=255, blank=True)
    default_contact_email = models.EmailField(blank=True)
    standard_av_available = models.BooleanField(default=False)
    standard_tom_available = models.BooleanField(default=False)

    standard_av_file = models.FileField(
        upload_to="catalog/av/",
        blank=True,
        null=True,
        verbose_name="Standard-AV (Datei)",
    )
    standard_tom_file = models.FileField(
        upload_to="catalog/tom/",
        blank=True,
        null=True,
        verbose_name="Standard-TOM (Datei)",
    )

    notes = models.TextField(blank=True)
    roles = models.ManyToManyField(
        ProviderRole,
        blank=True,
        related_name="catalog_entries",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Anbieterkatalogeintrag"
        verbose_name_plural = "Anbieterkatalogeinträge"

    def __str__(self):
        return self.name


class Processor(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        UNDER_REVIEW = "under_review", "In Prüfung"
        ENDED = "ended", "Beendet"

    class RiskClass(models.TextChoices):
        LOW = "low", "Niedrig"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    catalog_entry = models.ForeignKey(
        ProviderCatalogEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processors",
        verbose_name="Bekannter Anbieter",
    )

    name = models.CharField(max_length=255)
    service_description = models.TextField()
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ACTIVE)

    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    provider_roles = models.ManyToManyField(
        ProviderRole,
        blank=True,
        related_name="processors",
        verbose_name="AV-Rollen",
    )
    custom_provider_role = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Eigene / abweichende Rolle",
        help_text="Zusätzliche freie Rollenbezeichnung, falls keine Standardrolle passt.",
    )

    data_categories = models.TextField(blank=True)
    data_subject_groups = models.TextField(blank=True)
    server_locations = models.TextField(blank=True)

    third_country_transfer = models.BooleanField(default=False)
    third_country_description = models.TextField(blank=True)

    subprocessors_used = models.BooleanField(default=False)

    av_contract_exists = models.BooleanField(default=False)
    contract_valid_from = models.DateField(null=True, blank=True)
    contract_valid_until = models.DateField(null=True, blank=True)

    tom_exists = models.BooleanField(default=False)
    certifications = models.TextField(blank=True)

    risk_class = models.CharField(
        max_length=20,
        choices=RiskClass.choices,
        default=RiskClass.MEDIUM,
    )

    last_audit_date = models.DateField(null=True, blank=True)
    next_audit_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Auftragsverarbeiter"
        verbose_name_plural = "Auftragsverarbeiter"

    def __str__(self):
        return self.name