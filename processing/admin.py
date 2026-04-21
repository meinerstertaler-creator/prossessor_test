from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import (
    Department,
    ProcessingActivity,
    ProcessingStandardCase,
    ProcessingTemplate,
)


def _parse_bulk_template_line(line: str):
    """
    Erlaubte Formate pro Zeile:
    1) Titel
    2) gruppe|Titel
    3) gruppe|Fachbereich|Titel
    """
    raw = (line or "").strip()
    if not raw:
        return None

    parts = [part.strip() for part in raw.split("|")]

    allowed_groups = {
        ProcessingTemplate.TemplateGroup.GENERAL,
        ProcessingTemplate.TemplateGroup.LEGAL,
        ProcessingTemplate.TemplateGroup.MEDICAL,
    }

    if len(parts) == 1:
        return {
            "template_group": ProcessingTemplate.TemplateGroup.GENERAL,
            "department": "",
            "title": parts[0],
        }

    if len(parts) == 2:
        template_group, title = parts
        if template_group not in allowed_groups:
            raise ValueError(
                f"Unbekannte Gruppe '{template_group}'. Erlaubt sind: general, legal, medical."
            )
        if not title:
            raise ValueError("Der Titel darf nicht leer sein.")
        return {
            "template_group": template_group,
            "department": "",
            "title": title,
        }

    if len(parts) == 3:
        template_group, department, title = parts
        if template_group not in allowed_groups:
            raise ValueError(
                f"Unbekannte Gruppe '{template_group}'. Erlaubt sind: general, legal, medical."
            )
        if not title:
            raise ValueError("Der Titel darf nicht leer sein.")
        return {
            "template_group": template_group,
            "department": department,
            "title": title,
        }

    raise ValueError(
        "Ungültiges Format. Erlaubt sind: 'Titel', 'gruppe|Titel' oder 'gruppe|Fachbereich|Titel'."
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(ProcessingStandardCase)
class ProcessingStandardCaseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "risk_hint",
        "is_active",
        "is_general",
        "applies_to_legal",
        "applies_to_medical",
        "applies_to_industry",
    )
    list_filter = (
        "category",
        "risk_hint",
        "is_active",
        "is_general",
        "applies_to_legal",
        "applies_to_medical",
        "applies_to_industry",
    )
    search_fields = ("name", "description", "dsfa_relevance_note")
    ordering = ("name",)


@admin.register(ProcessingTemplate)
class ProcessingTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "template_group", "department", "is_active", "created_at")
    list_filter = ("template_group", "is_active")
    search_fields = (
        "title",
        "department",
        "purpose",
        "description",
        "data_subject_categories",
        "personal_data_categories",
        "recipients",
        "retention_period",
        "tom_summary",
    )
    ordering = ("template_group", "title")
    change_list_template = "admin/processing/processingtemplate/change_list.html"

    fieldsets = (
        (
            "Grunddaten",
            {
                "fields": (
                    "title",
                    "template_group",
                    "department",
                    "is_active",
                )
            },
        ),
        (
            "Inhaltliche Angaben",
            {
                "fields": (
                    "purpose",
                    "description",
                    "data_subject_categories",
                    "personal_data_categories",
                    "recipients",
                    "retention_period",
                    "tom_summary",
                )
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "bulk-create/",
                self.admin_site.admin_view(self.bulk_create_view),
                name="processing_processingtemplate_bulk_create",
            ),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Verfahrensvorlagen mehrfach anlegen",
        }

        if request.method == "POST":
            raw_input = request.POST.get("bulk_templates", "")
            default_group = request.POST.get(
                "default_group",
                ProcessingTemplate.TemplateGroup.GENERAL,
            ).strip()
            default_department = request.POST.get("default_department", "").strip()
            apply_defaults = request.POST.get("apply_defaults") == "1"

            lines = [line for line in raw_input.splitlines() if line.strip()]

            created_count = 0
            existing_count = 0
            error_messages = []

            for index, line in enumerate(lines, start=1):
                try:
                    parsed = _parse_bulk_template_line(line)

                    if parsed is None:
                        continue

                    if len([part.strip() for part in line.split("|")]) == 1 and apply_defaults:
                        parsed["template_group"] = (
                            default_group or ProcessingTemplate.TemplateGroup.GENERAL
                        )
                        if default_department:
                            parsed["department"] = default_department

                    _, created = ProcessingTemplate.objects.get_or_create(
                        title=parsed["title"],
                        template_group=parsed["template_group"],
                        defaults={
                            "department": parsed["department"],
                            "purpose": "",
                            "description": "",
                            "data_subject_categories": "",
                            "personal_data_categories": "",
                            "recipients": "",
                            "retention_period": "",
                            "tom_summary": "",
                            "is_active": True,
                        },
                    )

                    if created:
                        created_count += 1
                    else:
                        existing_count += 1

                except ValueError as exc:
                    error_messages.append(f"Zeile {index}: {exc}")
                except Exception as exc:
                    error_messages.append(f"Zeile {index}: Unerwarteter Fehler: {exc}")

            if error_messages:
                for message in error_messages:
                    self.message_user(request, message, level=messages.ERROR)

            if created_count:
                self.message_user(
                    request,
                    f"{created_count} Verfahrensvorlage(n) wurden neu angelegt.",
                    level=messages.SUCCESS,
                )

            if existing_count:
                self.message_user(
                    request,
                    f"{existing_count} Eintrag/Einträge waren bereits vorhanden und wurden nicht doppelt angelegt.",
                    level=messages.INFO,
                )

            if not error_messages and (created_count or existing_count):
                changelist_url = reverse("admin:processing_processingtemplate_changelist")
                return HttpResponseRedirect(changelist_url)

            context["raw_input"] = raw_input
            context["default_group"] = default_group
            context["default_department"] = default_department
            context["apply_defaults"] = apply_defaults
            return render(
                request,
                "admin/processing/processingtemplate/bulk_create.html",
                context,
            )

        context["raw_input"] = ""
        context["default_group"] = ProcessingTemplate.TemplateGroup.GENERAL
        context["default_department"] = ""
        context["apply_defaults"] = True
        return render(
            request,
            "admin/processing/processingtemplate/bulk_create.html",
            context,
        )


@admin.register(ProcessingActivity)
class ProcessingActivityAdmin(admin.ModelAdmin):
    list_display = (
        "internal_id",
        "title",
        "department",
        "template_origin",
        "standard_case",
        "status",
        "dpia_required",
        "legal_assessment_link",
        "created_at",
    )
    list_filter = (
        "status",
        "special_category_data",
        "department",
        "standard_case",
        "template_origin",
    )
    search_fields = ("internal_id", "title", "purpose", "description")
    ordering = ("internal_id", "title")

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk:
            return ("legal_assessment_link",)
        return ()

    def legal_assessment_link(self, obj):
        if not obj or not obj.pk:
            return "Erst nach dem Speichern verfügbar"
        url = reverse("legal_assessment_edit", args=[obj.pk])
        return format_html('<a href="{}">Rechtsbewertung öffnen</a>', url)

    legal_assessment_link.short_description = "Rechtsbewertung"