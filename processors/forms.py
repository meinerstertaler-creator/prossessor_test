from django import forms
from .models import Processor, ProviderCatalogEntry, ProviderRole


class ProcessorForm(forms.ModelForm):
    class Meta:
        model = Processor
        fields = [
            "catalog_entry",
            "name",
            "service_description",
            "status",
            "contact_person",
            "email",
            "phone",
            "address",
            "department",
            "provider_roles",
            "custom_provider_role",
            "data_categories",
            "data_subject_groups",
            "server_locations",
            "third_country_transfer",
            "third_country_description",
            "subprocessors_used",
            "av_contract_exists",
            "contract_valid_from",
            "contract_valid_until",
            "tom_exists",
            "certifications",
            "risk_class",
            "last_audit_date",
            "next_audit_date",
            "notes",
        ]
        widgets = {
            "catalog_entry": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "service_description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "provider_roles": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
            "custom_provider_role": forms.TextInput(attrs={"class": "form-control"}),
            "data_categories": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "data_subject_groups": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "server_locations": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "third_country_transfer": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "third_country_description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "subprocessors_used": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "av_contract_exists": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "contract_valid_from": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "contract_valid_until": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "tom_exists": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "certifications": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "risk_class": forms.Select(attrs={"class": "form-select"}),
            "last_audit_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "next_audit_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["catalog_entry"].queryset = ProviderCatalogEntry.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["provider_roles"].queryset = ProviderRole.objects.filter(
            is_active=True
        ).order_by("name")

        self.fields["catalog_entry"].required = False
        self.fields["provider_roles"].required = False

    def clean(self):
        cleaned_data = super().clean()

        third_country_transfer = cleaned_data.get("third_country_transfer")
        third_country_description = cleaned_data.get("third_country_description")

        if third_country_transfer and not third_country_description:
            self.add_error(
                "third_country_description",
                "Bitte den Drittlandtransfer näher beschreiben.",
            )

        return cleaned_data