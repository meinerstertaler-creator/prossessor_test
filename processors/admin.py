from django.contrib import admin

from .models import Processor, ProviderCatalogEntry, ProviderRole


@admin.register(ProviderRole)
class ProviderRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(ProviderCatalogEntry)
class ProviderCatalogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website",
        "standard_av_available",
        "standard_tom_available",
        "is_active",
    )
    search_fields = (
        "name",
        "legal_name",
        "website",
        "notes",
    )
    list_filter = (
        "standard_av_available",
        "standard_tom_available",
        "is_active",
        "roles",
    )
    filter_horizontal = ("roles",)


@admin.register(Processor)
class ProcessorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "status",
        "risk_class",
        "catalog_entry",
        "updated_at",
    )
    search_fields = (
        "name",
        "service_description",
        "contact_person",
        "email",
    )
    list_filter = (
        "status",
        "risk_class",
        "catalog_entry",
        "tenant",
    )
    filter_horizontal = ("provider_roles",)