from django.contrib import admin

from .models import AnalyseText, KnowledgeEntry, KnowledgeFolder, TextTemplate, TrustedSource


@admin.register(KnowledgeFolder)
class KnowledgeFolderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sort_order",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = ("sort_order", "name")


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "folder",
        "category",
        "version",
        "is_active",
        "allowed_for_ai",
        "updated_at",
    )
    list_filter = (
        "folder",
        "category",
        "is_active",
        "allowed_for_ai",
        "admin_only",
    )
    search_fields = (
        "title",
        "summary",
        "content",
        "source_note",
    )


@admin.register(TextTemplate)
class TextTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "folder",
        "category",
        "version",
        "is_active",
        "allowed_for_ai",
        "updated_at",
    )
    list_filter = (
        "folder",
        "category",
        "is_active",
        "allowed_for_ai",
        "admin_only",
    )
    search_fields = (
        "title",
        "description",
        "template_text",
    )


@admin.register(TrustedSource)
class TrustedSourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "folder",
        "category",
        "base_url",
        "priority",
        "is_active",
        "allowed_for_ai",
    )
    list_filter = (
        "folder",
        "category",
        "is_active",
        "allowed_for_ai",
        "admin_only",
    )
    search_fields = (
        "title",
        "base_url",
        "description",
    )


@admin.register(AnalyseText)
class AnalyseTextAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "folder",
        "topic",
        "version",
        "is_active",
        "ai_enabled",
        "updated_at",
    )
    list_filter = (
        "folder",
        "topic",
        "is_active",
        "ai_enabled",
    )
    search_fields = (
        "title",
        "description",
        "raw_text",
    )