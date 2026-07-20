from django import forms

from .models import (
    ProcessingActivity,
    ProcessingRetentionAssignment,
    ProcessingStandardCase,
    ProcessingStorageAssignment,
    ProcessingTemplate,
    RetentionDataObject,
    RetentionStorageSystem,
    TenantProcessingTemplateSetting,
)


class ProcessingTemplateChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.department:
            return f"{obj.get_template_group_display()} – {obj.title} ({obj.department})"
        return f"{obj.get_template_group_display()} – {obj.title}"


class ProcessingStandardCaseChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        parts = [obj.name]

        if obj.category:
            parts.append(obj.get_category_display())

        if obj.risk_hint:
            parts.append(f"Risiko: {obj.get_risk_hint_display()}")

        return " | ".join(parts)


class ProcessingActivityForm(forms.ModelForm):
    template_source = ProcessingTemplateChoiceField(
        queryset=ProcessingTemplate.objects.none(),
        required=False,
        label="Allgemeine Verfahrensvorlage",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    standard_case = ProcessingStandardCaseChoiceField(
        queryset=ProcessingStandardCase.objects.none(),
        required=False,
        label="DSFA-Standardfall",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    retention_data_objects = forms.ModelMultipleChoiceField(
        queryset=RetentionDataObject.objects.none(),
        required=False,
        label="Aufbewahrungstatbestände",
        help_text=(
            "Wählen Sie die im Verfahren vorkommenden Aufbewahrungstatbestände aus. "
            "Die zugehörigen typischen Datenkategorien und Fristen werden später "
            "für das Löschkonzept ausgewertet."
        ),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"}
        ),
    )

    storage_systems = forms.ModelMultipleChoiceField(
        queryset=RetentionStorageSystem.objects.none(),
        required=False,
        label="Löschorte / Systeme",
        help_text=(
            "Wählen Sie die bekannten Löschorte oder Systeme aus. "
            "Ist nur ein generischer Löschort bekannt, kann z. B. "
            "'E-Mail-System' statt eines konkreten Produkts gewählt werden."
        ),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"}
        ),
    )

    reminder_due_at = forms.DateTimeField(
        required=False,
        label="Erinnerung fällig am",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )

    class Meta:
        model = ProcessingActivity
        fields = [
            "internal_id",
            "title",
            "department",
            "standard_case",
            "standard_case_note",
            "purpose",
            "description",
            "status",
            "review_status",
            "responsible_person",
            "systems_used",
            "data_subject_categories",
            "personal_data_categories",
            "special_category_data",
            "special_category_description",
            "recipients",
            "third_country_transfer",
            "third_country_description",
            "retention_period",
            "tom_summary",
            "third_party_info_required",
            "contact_person",
            "contact_email",
            "reminder_due_at",
            "notes",
        ]
        labels = {
            "internal_id": "Interne ID",
            "title": "Bezeichnung des Verfahrens",
            "department": "Fachbereich",
            "standard_case_note": "Konkretisierung DSFA-Standardfall",
            "purpose": "Zweck der Verarbeitung",
            "description": "Beschreibung",
            "status": "Status",
            "review_status": "Bewertungsstatus",
            "responsible_person": "Verantwortliche Person",
            "systems_used": "Eingesetzte Systeme / Software",
            "data_subject_categories": "Betroffene Personen",
            "personal_data_categories": "Kategorien personenbezogener Daten",
            "special_category_data": "Besondere Kategorien personenbezogener Daten",
            "special_category_description": "Beschreibung besonderer Daten",
            "recipients": "Empfänger / Empfängerkategorien",
            "third_country_transfer": "Drittlandtransfer",
            "third_country_description": "Beschreibung Drittlandtransfer",
            "retention_period": "Lösch- / Aufbewahrungsfrist",
            "tom_summary": "Technische und organisatorische Maßnahmen (TOM)",
            "third_party_info_required": "Drittinformationen erforderlich",
            "contact_person": "Ansprechpartner",
            "contact_email": "E-Mail Ansprechpartner",
            "notes": "Notizen",
        }
        widgets = {
            "internal_id": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "purpose": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "standard_case_note": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "systems_used": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "data_subject_categories": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "personal_data_categories": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "special_category_description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "recipients": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "third_country_description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "retention_period": forms.TextInput(attrs={"class": "form-control"}),
            "tom_summary": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "review_status": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "responsible_person": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control"}),
            "special_category_data": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "third_country_transfer": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "third_party_info_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        show_template_field = kwargs.pop("show_template_field", False)
        tenant = kwargs.pop("tenant", None)
        super().__init__(*args, **kwargs)

        self.show_template_field = show_template_field
        self.tenant = tenant

        self.fields["department"].empty_label = "Bitte Fachbereich auswählen"

        self.fields["standard_case"].queryset = (
            ProcessingStandardCase.objects.filter(is_active=True).order_by("sort_order", "name")
        )
        self.fields["standard_case"].empty_label = "Kein DSFA-Standardfall ausgewählt"

        self.fields["retention_data_objects"].queryset = (
            RetentionDataObject.objects.filter(is_active=True)
            .order_by("sort_order", "name")
        )
        self.fields["storage_systems"].queryset = (
            RetentionStorageSystem.objects.filter(is_active=True)
            .order_by("sort_order", "name")
        )

        if self.instance and self.instance.pk:
            self.initial["retention_data_objects"] = (
                self.instance.retention_assignments.filter(is_active=True)
                .values_list("data_object_id", flat=True)
            )
            self.initial["storage_systems"] = (
                self.instance.storage_assignments.filter(is_active=True)
                .values_list("storage_system_id", flat=True)
            )

        template_queryset = ProcessingTemplate.objects.filter(is_active=True)

        if tenant is not None:
            disabled_template_ids = TenantProcessingTemplateSetting.objects.filter(
                tenant=tenant,
                is_enabled=False,
            ).values_list("template_id", flat=True)

            template_queryset = template_queryset.exclude(pk__in=disabled_template_ids)

        self.fields["template_source"].queryset = template_queryset.order_by("template_group", "title")
        self.fields["template_source"].empty_label = "Keine Vorlage verwenden"

        if not self.show_template_field:
            self.fields.pop("template_source")

        if self.instance and self.instance.pk and self.instance.reminder_due_at:
            self.initial["reminder_due_at"] = self.instance.reminder_due_at.strftime("%Y-%m-%dT%H:%M")

    def save_retention_selections(self, processing_activity):
        """
        Speichert die beiden Mehrfachauswahlen nach dem Speichern des Verfahrens.

        Die Zuordnungstabellen bleiben interne Technik und werden nicht
        eigenständig im Admin gepflegt.
        """
        if not processing_activity or not processing_activity.pk:
            raise ValueError(
                "Das Verfahren muss vor den Aufbewahrungstatbeständen "
                "und Löschorten gespeichert werden."
            )

        selected_data_objects = self.cleaned_data.get("retention_data_objects")
        selected_storage_systems = self.cleaned_data.get("storage_systems")

        selected_data_object_ids = set()
        if selected_data_objects is not None:
            selected_data_object_ids = set(
                selected_data_objects.values_list("pk", flat=True)
            )

        selected_storage_system_ids = set()
        if selected_storage_systems is not None:
            selected_storage_system_ids = set(
                selected_storage_systems.values_list("pk", flat=True)
            )

        existing_retention_assignments = {
            assignment.data_object_id: assignment
            for assignment in processing_activity.retention_assignments.all()
        }

        for data_object_id, assignment in existing_retention_assignments.items():
            should_be_active = data_object_id in selected_data_object_ids
            if assignment.is_active != should_be_active:
                assignment.is_active = should_be_active
                assignment.save(update_fields=["is_active", "updated_at"])

        for data_object in selected_data_objects or []:
            if data_object.pk not in existing_retention_assignments:
                ProcessingRetentionAssignment.objects.create(
                    processing_activity=processing_activity,
                    data_object=data_object,
                    is_active=True,
                )

        existing_storage_assignments = {
            assignment.storage_system_id: assignment
            for assignment in processing_activity.storage_assignments.all()
        }

        for storage_system_id, assignment in existing_storage_assignments.items():
            should_be_active = storage_system_id in selected_storage_system_ids
            if assignment.is_active != should_be_active:
                assignment.is_active = should_be_active
                assignment.save(update_fields=["is_active", "updated_at"])

        for storage_system in selected_storage_systems or []:
            if storage_system.pk not in existing_storage_assignments:
                ProcessingStorageAssignment.objects.create(
                    processing_activity=processing_activity,
                    storage_system=storage_system,
                    is_active=True,
                )

    def clean(self):
        cleaned_data = super().clean()

        third_party_info_required = cleaned_data.get("third_party_info_required")
        contact_email = cleaned_data.get("contact_email")

        if third_party_info_required and not contact_email:
            self.add_error(
                "contact_email",
                "Bitte eine E-Mail-Adresse angeben, wenn Drittinformationen erforderlich sind.",
            )

        return cleaned_data