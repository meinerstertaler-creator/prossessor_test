from django.contrib.auth.models import AbstractUser
from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.tenant:
            return f"{self.username} ({self.tenant})"
        return self.username


class CompanyProfile(models.Model):
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name="company_profile",
    )

    company_name = models.CharField(max_length=255)
    legal_form = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=255, blank=True)

    part_of_group = models.BooleanField(default=False)
    group_details = models.TextField(blank=True)

    employee_count = models.PositiveIntegerField(null=True, blank=True)

    uses_temporary_workers = models.BooleanField(default=False)
    uses_freelancers = models.BooleanField(default=False)

    internal_reporting_channel = models.BooleanField(
        default=False,
        help_text="Interner Meldekanal / Hinweisgebersystem vorhanden",
    )

    manages_patents = models.BooleanField(default=False)
    manages_licenses = models.BooleanField(default=False)

    ai_context_notes = models.TextField(
        blank=True,
        help_text="Freitext für mandantenspezifische Besonderheiten, die später von der KI berücksichtigt werden dürfen.",
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Unternehmensprofil"
        verbose_name_plural = "Unternehmensprofile"
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name