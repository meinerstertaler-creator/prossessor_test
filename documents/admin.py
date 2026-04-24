from django.contrib import admin

from .models import Document, DocumentFolder, DocumentLabel


@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "parent",
        "is_active",
        "created_at",
    )
    list_filter = (
        "tenant",
        "is_active",
    )
    search_fields = (
        "name",
        "tenant__name",
    )
    ordering = ("tenant__name", "name")


@admin.register(DocumentLabel)
class DocumentLabelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "is_active",
        "created_at",
    )
    list_filter = (
        "tenant",
        "is_active",
    )
    search_fields = (
        "name",
        "tenant__name",
    )
    ordering = ("tenant__name", "name")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "tenant",
        "document_type",
        "origin",
        "document_status",
        "source_text_template",
        "related_processing_activity",
        "related_processor",
        "version",
        "updated_at",
    )

    list_filter = (
        "tenant",
        "document_type",
        "origin",
        "document_status",
        "folder",
        "related_processing_activity",
        "related_processor",
        "related_audit",
        "related_legal_assessment",
    )

    search_fields = (
        "title",
        "description",
        "version",
        "tenant__name",
        "folder__name",
        "source_text_template__title",
        "related_processing_activity__title",
        "related_processor__name",
    )

    raw_id_fields = (
        "tenant",
        "folder",
        "uploaded_by",
        "source_text_template",
        "related_processing_activity",
        "related_legal_assessment",
        "related_processor",
        "related_audit",
        "related_action_item",
    )

    filter_horizontal = ("labels",)

    ordering = ("-updated_at", "-created_at", "title")

    readonly_fields = (
        "created_at",
        "updated_at",
        "source_catalog_updated_at",
    )

    fieldsets = (
        (
            "Grunddaten",
            {
                "fields": (
                    "tenant",
                    "title",
                    "document_type",
                    "file",
                    "version",
                    "description",
                )
            },
        ),
        (
            "Herkunft und Bearbeitungsstand",
            {
                "fields": (
                    "origin",
                    "document_status",
                    "source_text_template",
                    "source_catalog_updated_at",
                )
            },
        ),
        (
            "Ordnung",
            {
                "fields": (
                    "folder",
                    "labels",
                )
            },
        ),
        (
            "Verknüpfungen",
            {
                "fields": (
                    "related_processing_activity",
                    "related_legal_assessment",
                    "related_processor",
                    "related_audit",
                    "related_action_item",
                )
            },
        ),
        (
            "Technische Angaben",
            {
                "fields": (
                    "uploaded_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )