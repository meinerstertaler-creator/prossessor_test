from django import forms
from .models import LegalAssessment


class LegalAssessmentForm(forms.ModelForm):
    class Meta:
        model = LegalAssessment
        fields = [
            "legal_basis",
            "special_legal_basis",
            "professional_secrecy",
            "section_203_process_implemented",
            "legitimate_interest_test",
            "legitimate_interest_purpose",
            "data_subject_impact",
            "safeguards",
            "legitimate_interest_outcome",
            "legitimate_interest_reasoning",
            "legitimate_interest_completed",
            "risk_level",
            "no_dpia_check_required_reason",
            "no_dpia_check_required_note",
            "legal_assessment_text",
            "open_issues",
            "ai_prompt",
            "ai_suggestion",
        ]
        widgets = {
            "legal_basis": forms.Select(attrs={"class": "form-select"}),
            "special_legal_basis": forms.Select(attrs={"class": "form-select"}),
            "risk_level": forms.Select(attrs={"class": "form-select"}),
            "legitimate_interest_outcome": forms.Select(attrs={"class": "form-select"}),
            "no_dpia_check_required_reason": forms.Select(attrs={"class": "form-select"}),
            "professional_secrecy": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "section_203_process_implemented": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "legitimate_interest_test": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "legitimate_interest_completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "legal_assessment_text": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "open_issues": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "ai_prompt": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "ai_suggestion": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "legitimate_interest_purpose": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "data_subject_impact": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "safeguards": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "legitimate_interest_reasoning": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "no_dpia_check_required_note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "legal_basis": "Art. 6 DSGVO",
            "special_legal_basis": "Art. 9 DSGVO",
            "professional_secrecy": "Berufsgeheimnis / § 203 StGB",
            "section_203_process_implemented": "203er Verfahren implementiert",
            "legitimate_interest_test": "Interessenabwägung durchgeführt",
            "legitimate_interest_purpose": "Berechtigtes Interesse des Verantwortlichen",
            "data_subject_impact": "Auswirkungen auf die betroffene Person",
            "safeguards": "Schutzmaßnahmen / mildernde Umstände",
            "legitimate_interest_outcome": "Ergebnis der Abwägung",
            "legitimate_interest_reasoning": "Begründung der Interessenabwägung",
            "legitimate_interest_completed": "Interessenabwägung abgeschlossen",
            "risk_level": "Risikoeinstufung",
            "no_dpia_check_required_reason": "Kein DSFA-Check erforderlich",
            "no_dpia_check_required_note": "Ergänzende Begründung",
            "legal_assessment_text": "Bewertung",
            "open_issues": "Offene Punkte",
            "ai_prompt": "Prompt",
            "ai_suggestion": "KI-Vorschlag",
        }

    def __init__(self, *args, **kwargs):
        self.processing_activity = kwargs.pop("processing_activity", None)
        super().__init__(*args, **kwargs)

        dpia_check = getattr(self.processing_activity, "dpia_check", None)

        if dpia_check and dpia_check.has_must_list_case:
            self.fields["no_dpia_check_required_reason"].disabled = True
            self.fields["no_dpia_check_required_note"].disabled = True

    def clean(self):
        cleaned_data = super().clean()

        no_dpia_check_required_reason = cleaned_data.get("no_dpia_check_required_reason")
        no_dpia_check_required_note = (cleaned_data.get("no_dpia_check_required_note") or "").strip()
        professional_secrecy = cleaned_data.get("professional_secrecy")
        section_203_process_implemented = cleaned_data.get("section_203_process_implemented")

        dpia_check = getattr(self.processing_activity, "dpia_check", None)

        if dpia_check and dpia_check.has_must_list_case:
            if no_dpia_check_required_reason or no_dpia_check_required_note:
                raise forms.ValidationError(
                    "Bei einem Muss-Listen-Fall ist ein Verzicht auf die DSFA rechtlich ausgeschlossen."
                )

            cleaned_data["no_dpia_check_required_reason"] = ""
            cleaned_data["no_dpia_check_required_note"] = ""
            return cleaned_data

        if (
            no_dpia_check_required_reason == LegalAssessment.NoDPIACheckReason.OTHER
            and not no_dpia_check_required_note
        ):
            self.add_error(
                "no_dpia_check_required_note",
                "Bitte eine Begründung angeben, wenn 'Sonstiger Grund' gewählt wird.",
            )

        if not professional_secrecy and section_203_process_implemented:
            self.add_error(
                "section_203_process_implemented",
                "Das 203er Verfahren kann nur markiert werden, wenn Berufsgeheimnis / § 203 StGB relevant ist.",
            )

        return cleaned_data