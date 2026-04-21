from django.db import models
from processing.models import ProcessingActivity


class DPIACheck(models.Model):
    class Mode(models.TextChoices):
        MANDATORY = "mandatory", "Verpflichtend"
        VOLUNTARY = "voluntary", "Freiwillig"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Niedrig"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"

    class MustListCase(models.TextChoices):
        NONE = "", "Kein Muss-Listen-Fall"
        VIDEO_SURVEILLANCE = "video_surveillance", "Systematische Videoüberwachung"
        LOCATION_TRACKING = "location_tracking", "Umfangreiches Standort-/Bewegungstracking"
        PROFILING_SCORING = "profiling_scoring", "Profiling / Scoring mit erheblicher Wirkung"
        EMPLOYEE_MONITORING = "employee_monitoring", "Umfangreiche Beschäftigtenüberwachung"
        SENSITIVE_LARGE_SCALE = "sensitive_large_scale", "Groß angelegte Verarbeitung sensibler Daten"
        BIOMETRIC_ID = "biometric_id", "Biometrische Identifizierung"
        GENETIC_DATA = "genetic_data", "Genetische Daten"
        HEALTH_LARGE_SCALE = "health_large_scale", "Umfangreiche Gesundheitsdaten"
        DATA_MATCHING = "data_matching", "Umfangreiche Datenzusammenführung / Matching"
        VULNERABLE_GROUPS = "vulnerable_groups", "Verarbeitung mit besonders schutzbedürftigen Personen"

    processing_activity = models.OneToOneField(
        ProcessingActivity,
        on_delete=models.CASCADE,
        related_name="dpia_check",
    )

    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.MANDATORY,
    )

    must_list_case = models.CharField(
        max_length=50,
        choices=MustListCase.choices,
        blank=True,
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        blank=True,
    )

    reasoning = models.TextField(blank=True)
    open_points = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["processing_activity__title"]

    def __str__(self):
        return f"DSFA-Prüfung – {self.processing_activity}"

    @property
    def has_must_list_case(self):
        return bool(self.must_list_case)

    @property
    def processing_standard_case_name(self):
        if self.processing_activity.standard_case:
            return self.processing_activity.standard_case.name
        return ""

    @property
    def _has_manual_input(self):
        return any(
            [
                bool(self.must_list_case),
                bool(self.risk_level),
                bool((self.reasoning or "").strip()),
                bool((self.open_points or "").strip()),
                bool(self.completed),
            ]
        )

    @property
    def recommendation(self):
        pa = self.processing_activity
        standard_case = getattr(pa, "standard_case", None)
        standard_case_name = (self.processing_standard_case_name or "").lower()
        standard_risk_hint = getattr(standard_case, "risk_hint", "") if standard_case else ""

        # 1. Muss-Liste = harter Trigger
        if self.must_list_case:
            return "mandatory"

        # 2. Noch nichts dokumentiert / geprüft
        has_any_signal = any(
            [
                bool(standard_case),
                bool(standard_case_name),
                bool(standard_risk_hint),
                self._has_manual_input,
                bool(pa.special_category_data),
                bool(pa.third_country_transfer),
            ]
        )

        text = " ".join(
            [
                pa.title or "",
                pa.purpose or "",
                pa.description or "",
                pa.data_subject_categories or "",
                pa.personal_data_categories or "",
                pa.systems_used or "",
                pa.recipients or "",
                pa.standard_case_note or "",
            ]
        ).lower()

        high_risk_terms = [
            "profiling",
            "scoring",
            "tracking",
            "gps",
            "video",
            "kamera",
            "gesundheit",
            "biometr",
            "genet",
            "überwachung",
        ]
        text_has_high_risk_terms = any(term in text for term in high_risk_terms)

        if not has_any_signal and not text_has_high_risk_terms:
            return "not_checked"

        # 3. Standardfall aus Verfahren = Vorstrukturierung
        # Mittel/Hoch soll mindestens "empfohlen" ergeben, solange keine Gegenentscheidung
        if standard_risk_hint in {"high", "medium"}:
            return "recommended"

        # 4. Verfahrensbezogene Auffanglogik
        score = 0

        if pa.special_category_data:
            score += 2

        if pa.third_country_transfer:
            score += 1

        if text_has_high_risk_terms:
            score += 2

        if len((pa.description or "").strip()) > 400:
            score += 1

        if self.risk_level == self.RiskLevel.HIGH:
            score += 2
        elif self.risk_level == self.RiskLevel.MEDIUM:
            score += 1

        if score >= 4:
            return "mandatory"
        if score >= 2:
            return "recommended"

        # 5. "Nicht erforderlich" nur bei tatsächlich dokumentierter / abgeschlossener Prüfung
        if self.completed or self._has_manual_input:
            return "not_required"

        return "not_checked"

    @property
    def recommendation_label(self):
        return {
            "mandatory": "DSFA erforderlich",
            "recommended": "DSFA empfohlen",
            "not_required": "DSFA nicht erforderlich",
            "not_checked": "DSFA nicht geprüft",
        }[self.recommendation]

    @property
    def recommendation_badge_class(self):
        return {
            "mandatory": "danger",
            "recommended": "warning",
            "not_required": "success",
            "not_checked": "secondary",
        }[self.recommendation]

    @property
    def recommendation_reason(self):
        pa = self.processing_activity
        reasons = []

        if self.must_list_case:
            reasons.append(f"Muss-Listen-Fall: {self.get_must_list_case_display()}.")

        if self.processing_standard_case_name:
            reasons.append(f"Standardfall aus Verfahren: {self.processing_standard_case_name}.")

        if pa.standard_case_note:
            reasons.append("Der Standardfall wurde im Verfahren weiter konkretisiert.")

        if pa.special_category_data:
            reasons.append("Es werden besondere Kategorien personenbezogener Daten verarbeitet.")

        if pa.third_country_transfer:
            reasons.append("Ein Drittlandtransfer ist dokumentiert.")

        if self.recommendation == "not_checked" and not reasons:
            return "Es liegt noch keine dokumentierte DSFA-Prüfung oder Risikoeinstufung vor."

        return " ".join(reasons) if reasons else "Bewertung anhand des dokumentierten Verfahrenskontexts."

    @property
    def auto_reasoning_suggestion(self):
        pa = self.processing_activity
        parts = []

        if self.must_list_case:
            parts.append(f"Muss-Listen-Fall: {self.get_must_list_case_display()}.")

        if self.processing_standard_case_name:
            parts.append(f"Standardfall aus Verfahren: {self.processing_standard_case_name}.")

        if pa.standard_case_note:
            parts.append(f"Konkretisierung Standardfall: {pa.standard_case_note.strip()}")

        if pa.purpose:
            parts.append(f"Zweck der Verarbeitung: {pa.purpose.strip()}")

        if pa.description:
            parts.append(f"Beschreibung der Verarbeitung: {pa.description.strip()}")

        if pa.data_subject_categories:
            parts.append(f"Betroffene Personengruppen: {pa.data_subject_categories.strip()}")

        if pa.personal_data_categories:
            parts.append(f"Verarbeitete Datenkategorien: {pa.personal_data_categories.strip()}")

        if pa.systems_used:
            parts.append(f"Eingesetzte Systeme: {pa.systems_used.strip()}")

        parts.append(f"Vorläufige Bewertung: {self.recommendation_label}.")

        return "\n\n".join(parts)

    @property
    def auto_open_points_suggestion(self):
        if self.recommendation == "mandatory":
            return "Prüfen, ob die DSFA-Durchführung vollständig dokumentiert und freigegeben werden muss."
        if self.recommendation == "recommended":
            return "Prüfen, ob eine vertiefte DSFA-Durchführung erforderlich oder sinnvoll ist."
        return ""


class DPIA(models.Model):
    processing_activity = models.OneToOneField(
        ProcessingActivity,
        on_delete=models.CASCADE,
        related_name="dpia",
    )

    description = models.TextField(
        blank=True,
        help_text="Beschreibung der Verarbeitung für die DSFA",
    )

    necessity_assessment = models.TextField(
        blank=True,
        help_text="Bewertung der Notwendigkeit und Verhältnismäßigkeit",
    )

    result_summary = models.TextField(
        blank=True,
        help_text="Zusammenfassung der DSFA",
    )

    residual_risk = models.CharField(
        max_length=50,
        blank=True,
        help_text="Restrisiko (niedrig / mittel / hoch)",
    )

    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["processing_activity__title"]

    def __str__(self):
        return f"DSFA zu {self.processing_activity}"


class DPIARisk(models.Model):
    class Probability(models.TextChoices):
        LOW = "low", "Niedrig"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"

    class Impact(models.TextChoices):
        LOW = "low", "Niedrig"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"

    dpia = models.ForeignKey(
        DPIA,
        on_delete=models.CASCADE,
        related_name="risks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    probability = models.CharField(
        max_length=20,
        choices=Probability.choices,
        default=Probability.MEDIUM,
    )

    impact = models.CharField(
        max_length=20,
        choices=Impact.choices,
        default=Impact.MEDIUM,
    )

    mitigation_measures = models.TextField(
        blank=True,
        help_text="Maßnahmen zur Risikominderung",
    )

    residual_risk = models.CharField(
        max_length=50,
        blank=True,
        help_text="Restrisiko nach Maßnahmen",
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class DPIAMeasure(models.Model):
    dpia = models.ForeignKey(
        DPIA,
        on_delete=models.CASCADE,
        related_name="measures",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    implemented = models.BooleanField(default=False)

    responsible_person = models.CharField(
        max_length=255,
        blank=True,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title