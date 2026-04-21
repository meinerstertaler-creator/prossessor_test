from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DPIA, DPIARisk, DPIAMeasure


class DPIARiskInline(admin.TabularInline):
    model = DPIARisk
    extra = 0


class DPIAMeasureInline(admin.TabularInline):
    model = DPIAMeasure
    extra = 0


@admin.register(DPIA)
class DPIAAdmin(admin.ModelAdmin):
    list_display = (
        "processing_activity",
        "residual_risk",
        "approved",
        "updated_at",
    )

    inlines = [
        DPIARiskInline,
        DPIAMeasureInline,
    ]


@admin.register(DPIARisk)
class DPIARiskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "probability",
        "impact",
        "residual_risk",
    )


@admin.register(DPIAMeasure)
class DPIAMeasureAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "implemented",
        "responsible_person",
        "due_date",
    )