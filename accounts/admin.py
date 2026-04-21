from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import CompanyProfile, Role, Tenant, User
from processing.models import ProcessingTemplate, TenantProcessingTemplateSetting
from processing.services import sync_tenant_processing_templates


class TenantAdminForm(forms.ModelForm):
    standard_templates_general = forms.MultipleChoiceField(
        required=False,
        label="Allgemeine Standardverfahren",
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        help_text=(
            "Diese allgemeinen Standardverfahren gelten grundsätzlich für den Mandanten. "
            "Häkchen entfernen, wenn ein Verfahren ausnahmsweise nicht gelten soll."
        ),
    )

    standard_templates_special = forms.MultipleChoiceField(
        required=False,
        label="Spezielle Standardverfahren",
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        help_text=(
            "Spezielle oder zusätzliche Standardverfahren. "
            "Auch diese sind standardmäßig vorausgewählt und können abgewählt werden."
        ),
    )

    class Meta:
        model = Tenant
        fields = (
            "name",
            "description",
            "is_active",
            "standard_templates_general",
            "standard_templates_special",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        general_templates = list(
            ProcessingTemplate.objects.filter(
                is_active=True,
                template_group=ProcessingTemplate.TemplateGroup.GENERAL,
            ).order_by("title")
        )
        special_templates = list(
            ProcessingTemplate.objects.filter(is_active=True)
            .exclude(template_group=ProcessingTemplate.TemplateGroup.GENERAL)
            .order_by("template_group", "title")
        )

        self.fields["standard_templates_general"].choices = [
            (str(template.pk), template.title) for template in general_templates
        ]
        self.fields["standard_templates_special"].choices = [
            (
                str(template.pk),
                f"{template.get_template_group_display()} – {template.title}",
            )
            for template in special_templates
        ]

        settings_map = {}
        if self.instance and self.instance.pk:
            settings_map = {
                setting.template_id: setting.is_enabled
                for setting in TenantProcessingTemplateSetting.objects.filter(tenant=self.instance)
            }

        def is_enabled_for_template(template):
            return settings_map.get(template.pk, True)

        self.fields["standard_templates_general"].initial = [
            str(template.pk)
            for template in general_templates
            if is_enabled_for_template(template)
        ]
        self.fields["standard_templates_special"].initial = [
            str(template.pk)
            for template in special_templates
            if is_enabled_for_template(template)
        ]

    def save_template_settings(self, tenant):
        general_ids = set(self.cleaned_data.get("standard_templates_general", []))
        special_ids = set(self.cleaned_data.get("standard_templates_special", []))
        selected_ids = general_ids.union(special_ids)

        all_active_templates = ProcessingTemplate.objects.filter(is_active=True)

        for template in all_active_templates:
            is_enabled = str(template.pk) in selected_ids

            setting, _created = TenantProcessingTemplateSetting.objects.get_or_create(
                tenant=tenant,
                template=template,
                defaults={"is_enabled": is_enabled},
            )

            if setting.is_enabled != is_enabled:
                setting.is_enabled = is_enabled
                setting.save(update_fields=["is_enabled", "updated_at"])


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    form = TenantAdminForm
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    fieldsets = (
        (
            "Mandant",
            {
                "fields": ("name", "description", "is_active"),
            },
        ),
        (
            "Allgemeine Standardverfahren",
            {
                "fields": ("standard_templates_general",),
            },
        ),
        (
            "Spezielle Standardverfahren",
            {
                "fields": ("standard_templates_special",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        form.save_template_settings(obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        tenant = form.instance
        sync_tenant_processing_templates(
            tenant=tenant,
            user=request.user,
        )

        self.message_user(
            request,
            "Standardverfahren wurden gespeichert und für den Mandanten synchronisiert.",
            level=messages.SUCCESS,
        )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "tenant", "role", "is_staff", "is_active")
    list_filter = ("tenant", "role", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Mandantenbezug",
            {
                "fields": ("tenant", "role"),
            },
        ),
    )

    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            "Mandantenbezug",
            {
                "fields": ("tenant", "role"),
            },
        ),
    )


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "tenant",
        "legal_form",
        "industry",
        "employee_count",
        "part_of_group",
    )
    list_filter = (
        "part_of_group",
        "uses_temporary_workers",
        "uses_freelancers",
        "internal_reporting_channel",
        "manages_patents",
        "manages_licenses",
    )
    search_fields = (
        "company_name",
        "industry",
    )