from django import forms
from .models import AnalyseText


class AnalyseTextForm(forms.ModelForm):
    class Meta:
        model = AnalyseText
        fields = [
            "title",
            "topic",
            "description",
            "raw_text",
            "ai_enabled",
            "is_active",
            "version",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "raw_text": forms.Textarea(attrs={"rows": 18}),
        }
        labels = {
            "title": "Titel",
            "topic": "Thema",
            "description": "Kurzbeschreibung",
            "raw_text": "Rohtext",
            "ai_enabled": "Für KI freigegeben",
            "is_active": "Aktiv",
            "version": "Version / Stand",
        }