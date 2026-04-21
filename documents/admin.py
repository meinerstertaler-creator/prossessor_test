from django.contrib import admin

from .models import Document, DocumentFolder, DocumentLabel


@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "parent", "is_active", "created_at")
    list_filter = ("tenant", "is_active")
    search_fields = ("name",)


@admin.register(DocumentLabel)
class DocumentLabelAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "is_active", "created_at")
    list_filter = ("tenant", "is_active")
    search_fields = ("name",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "document_type",
        "tenant",
        "folder",
        "uploaded_by",
        "created_at",
    )
    list_filter = (
        "document_type",
        "tenant",
        "folder",
        "labels",
    )
    search_fields = (
        "title",
        "description",
        "version",
    )
    filter_horizontal = ("labels",)