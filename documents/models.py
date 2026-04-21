from django.conf import settings
from django.db import models

from accounts.models import Tenant
from actions.models import ActionItem
from audits.models import Audit
from legal.models import LegalAssessment
from processing.models import ProcessingActivity
from processors.models import Processor


class DocumentFolder(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="document_folders",
    )
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("tenant", "name", "parent")
        verbose_name = "Dokumentenordner"
        verbose_name_plural = "Dokumentenordner"

    def __str__(self):
        if self.parent:
            return f"{self.parent} / {self.name}"
        return self.name


class DocumentLabel(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="document_labels",
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("tenant", "name")
        verbose_name = "Dokumentenlabel"
        verbose_name_plural = "Dokumentenlabels"

    def __str__(self):
        return self.name


class Document(models.Model):
    class DocumentType(models.TextChoices):
        GENERAL = "general", "Allgemeines Dokument"
        AV_CONTRACT = "av_contract", "AV-Vertrag"
        TOM = "tom", "Technische und organisatorische Maßnahmen"
        POLICY = "policy", "Richtlinie"
        REPORT = "report", "Bericht"
        CERTIFICATE = "certificate", "Zertifikat"
        AUDIT_EVIDENCE = "audit_evidence", "Audit-Nachweis"
        OTHER = "other", "Sonstiges"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )

    title = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.GENERAL,
    )
    file = models.FileField(upload_to="documents/")
    version = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, default="N/A")

    folder = models.ForeignKey(
        DocumentFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    labels = models.ManyToManyField(
        DocumentLabel,
        blank=True,
        related_name="documents",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )

    related_processing_activity = models.ForeignKey(
        ProcessingActivity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    related_legal_assessment = models.ForeignKey(
        LegalAssessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    related_processor = models.ForeignKey(
        Processor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    related_audit = models.ForeignKey(
        Audit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    related_action_item = models.ForeignKey(
        ActionItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )

    source_catalog_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Katalog-Stand zum Zeitpunkt der Übernahme",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "title"]
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"

    def __str__(self):
        return self.title