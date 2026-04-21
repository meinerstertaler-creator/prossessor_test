from django import forms
from .models import ActionItem


class ActionItemForm(forms.ModelForm):
    class Meta:
        model = ActionItem
        fields = [
            "title",
            "description",
            "source_type",
            "related_audit",
            "related_processing_activity",
            "related_legal_assessment",
            "responsible_person",
            "due_date",
            "follow_up_date",
            "priority",
            "status",
            "completion_date",
            "effectiveness_review",
            "notes",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "effectiveness_review": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "follow_up_date": forms.DateInput(attrs={"type": "date"}),
            "completion_date": forms.DateInput(attrs={"type": "date"}),
        }