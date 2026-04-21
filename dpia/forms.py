from django import forms
from .models import DPIA, DPIACheck, DPIARisk, DPIAMeasure


class DPIACheckForm(forms.ModelForm):
    class Meta:
        model = DPIACheck
        fields = [
            "mode",
            "must_list_case",
            "risk_level",
            "reasoning",
            "open_points",
            "completed",
        ]
        widgets = {
            "mode": forms.Select(attrs={"class": "form-select"}),
            "must_list_case": forms.Select(attrs={"class": "form-select"}),
            "risk_level": forms.Select(attrs={"class": "form-select"}),
            "reasoning": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "open_points": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "mode": "Modus",
            "must_list_case": "Muss-Listen-Fall",
            "risk_level": "Bewertung",
            "reasoning": "Begründung",
            "open_points": "Offene Punkte",
            "completed": "Prüfung abgeschlossen",
        }


class DPIAForm(forms.ModelForm):
    class Meta:
        model = DPIA
        fields = [
            "description",
            "necessity_assessment",
            "result_summary",
            "residual_risk",
            "approved",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "necessity_assessment": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "result_summary": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "residual_risk": forms.TextInput(attrs={"class": "form-control"}),
            "approved": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "description": "Beschreibung der Verarbeitung für die DSFA",
            "necessity_assessment": "Bewertung von Notwendigkeit und Verhältnismäßigkeit",
            "result_summary": "Zusammenfassung / Ergebnis",
            "residual_risk": "Restrisiko",
            "approved": "DSFA freigegeben",
        }


class DPIARiskForm(forms.ModelForm):
    class Meta:
        model = DPIARisk
        fields = [
            "title",
            "description",
            "probability",
            "impact",
            "mitigation_measures",
            "residual_risk",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "probability": forms.Select(attrs={"class": "form-select"}),
            "impact": forms.Select(attrs={"class": "form-select"}),
            "mitigation_measures": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "residual_risk": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Risiko",
            "description": "Beschreibung",
            "probability": "Eintrittswahrscheinlichkeit",
            "impact": "Schadenshöhe",
            "mitigation_measures": "Maßnahmen zur Risikominderung",
            "residual_risk": "Restrisiko",
        }


class DPIAMeasureForm(forms.ModelForm):
    class Meta:
        model = DPIAMeasure
        fields = [
            "title",
            "description",
            "implemented",
            "responsible_person",
            "due_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "implemented": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "responsible_person": forms.TextInput(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
        labels = {
            "title": "Maßnahme",
            "description": "Beschreibung",
            "implemented": "Umgesetzt",
            "responsible_person": "Verantwortliche Person",
            "due_date": "Fällig bis",
        }