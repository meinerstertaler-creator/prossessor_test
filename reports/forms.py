from django import forms


class ProcedureAuditReportNoteForm(forms.Form):
    auditor_report_note = forms.CharField(
        required=False,
        label="Freitext des Auditors",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": (
                    "Hier kann der Auditor eine freie Einordnung, "
                    "Bewertung oder einen Abschlussvermerk ergänzen."
                ),
            }
        ),
    )