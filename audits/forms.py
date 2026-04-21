from django import forms

from .models import (
    Audit,
    AuditResponse,
    ProcedureAudit,
    ProcedureAuditChecklistResponse,
    ProcedureAuditItem,
    ProcedureAuditNewActivity,
)


class AuditStartForm(forms.Form):
    AUDIT_KIND_CHOICES = [
        ("procedure_annual", "Jährliches Datenschutzaudit"),
        ("procedure_event_based", "Anlassbezogenes Audit"),
        ("procedure_follow_up", "Nachaudit / Follow-up"),
        ("special_processor", "Spezialaudit Auftragsverarbeiter"),
    ]

    audit_kind = forms.ChoiceField(
        choices=AUDIT_KIND_CHOICES,
        label="Auditart",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            "processor",
            "audit_year",
            "audit_type",
            "status",
            "start_date",
            "due_date",
            "completion_date",
            "auditor_name",
            "overall_result",
            "summary",
            "follow_up_required",
            "next_review_date",
        ]
        widgets = {
            "processor": forms.Select(attrs={"class": "form-select"}),
            "audit_year": forms.NumberInput(attrs={"class": "form-control"}),
            "audit_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "completion_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "auditor_name": forms.TextInput(attrs={"class": "form-control"}),
            "overall_result": forms.Select(attrs={"class": "form-select"}),
            "summary": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "follow_up_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "next_review_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class AuditResponseForm(forms.ModelForm):
    class Meta:
        model = AuditResponse
        fields = ["rating", "comment", "evidence_available", "action_required"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "evidence_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "action_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProcedureAuditForm(forms.ModelForm):
    class Meta:
        model = ProcedureAudit
        fields = [
            "title",
            "audit_year",
            "audit_type",
            "status",
            "audit_date",
            "execution_type",
            "start_date",
            "end_date",
            "auditor_name",
            "participants",
            "summary",
            "training_recommendations",
            "overall_result",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "audit_year": forms.NumberInput(attrs={"class": "form-control"}),
            "audit_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "audit_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "execution_type": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "auditor_name": forms.TextInput(attrs={"class": "form-control"}),
            "participants": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "summary": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "training_recommendations": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "overall_result": forms.Select(attrs={"class": "form-select"}),
        }


class ProcedureAuditItemForm(forms.ModelForm):
    class Meta:
        model = ProcedureAuditItem
        fields = [
            "review_status",
            "notes",
            "legal_review_required",
            "dpia_review_required",
            "action_required",
        ]
        widgets = {
            "review_status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "legal_review_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "dpia_review_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "action_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProcedureAuditNewActivityForm(forms.ModelForm):
    class Meta:
        model = ProcedureAuditNewActivity
        fields = [
            "title",
            "department_hint",
            "contact_person",
            "description",
            "is_already_active",
            "requires_follow_up",
            "notes",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "department_hint": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "is_already_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "requires_follow_up": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class ProcedureAuditChecklistResponseForm(forms.ModelForm):
    class Meta:
        model = ProcedureAuditChecklistResponse
        fields = ["rating", "comment", "evidence_available", "action_required"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "evidence_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "action_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }