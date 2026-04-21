from django.utils import timezone


PROMPT_VERSION = "v1"


def build_legal_prompt(processing):
    return f"""
Du bist ein juristisch arbeitender Datenschutz-Assistent.
Erstelle einen kompakten, vorsichtigen Vorschlag für die datenschutzrechtliche Bewertung.

Verarbeitungstätigkeit:
- Titel: {processing.title}
- Fachbereich: {processing.department or ""}
- Zweck: {processing.purpose or ""}
- Beschreibung: {processing.description or ""}
- Verantwortliche Person: {processing.responsible_person or ""}
- Systeme: {processing.systems_used or ""}
- Betroffene Personen: {processing.data_subject_categories or ""}
- Datenkategorien: {processing.personal_data_categories or ""}
- Besondere Kategorien personenbezogener Daten: {"Ja" if processing.special_category_data else "Nein"}
- Beschreibung besonderer Daten: {processing.special_category_description or ""}
- Empfänger: {processing.recipients or ""}
- Drittlandtransfer: {"Ja" if processing.third_country_transfer else "Nein"}
- Beschreibung Drittlandtransfer: {processing.third_country_description or ""}
- Aufbewahrungsfrist: {processing.retention_period or ""}
- TOM: {processing.tom_summary or ""}
- Notizen: {processing.notes or ""}

Aufgabe:
1. Schlage eine mögliche Rechtsgrundlage nach Art. 6 DSGVO vor.
2. Prüfe, ob Art. 9 DSGVO relevant sein könnte.
3. Gib einen Hinweis, ob Berufsgeheimnis / § 203 StGB relevant sein könnte.
4. Gib eine vorläufige Risikoeinschätzung.
5. Gib einen Hinweis, ob DSFA-Bedarf naheliegen könnte.
6. Formuliere eine vorsichtige juristische Begründung.
7. Formuliere offene Klärungspunkte.

Wichtig:
- Keine endgültige Entscheidung treffen.
- Formuliere als Entwurf für den Datenschutzbeauftragten.
""".strip()


def generate_local_legal_suggestion(processing):
    """
    Übergangslösung ohne externe KI:
    Es wird ein strukturierter juristischer Entwurf erzeugt.
    Diese Funktion kann später durch einen API-Aufruf ersetzt werden.
    """
    title = (processing.title or "").lower()
    purpose = (processing.purpose or "").lower()
    categories = (processing.personal_data_categories or "").lower()
    dept = str(processing.department or "").lower()

    legal_basis = ""
    special_basis = ""
    professional_secrecy = False
    dpia_required = False
    risk_level = "medium"
    reasoning = []
    open_points = []

    # Heuristiken
    if any(word in title + " " + purpose for word in ["bewerb", "personal", "lohn", "gehalt", "beschäftig"]):
        legal_basis = "legal_obligation"
        reasoning.append("Naheliegend ist eine Verarbeitung zur Erfüllung arbeits- und sozialrechtlicher Pflichten bzw. zur Durchführung des Beschäftigungsverhältnisses.")
    elif any(word in title + " " + purpose for word in ["kunde", "mandat", "vertrag", "abrechnung", "bestellung", "shop"]):
        legal_basis = "contract"
        reasoning.append("Naheliegend ist eine Verarbeitung zur Vertragsanbahnung, Vertragsdurchführung oder Abrechnung.")
    elif any(word in title + " " + purpose for word in ["marketing", "newsletter"]):
        legal_basis = "legitimate_interests"
        reasoning.append("Naheliegend ist eine Prüfung berechtigter Interessen; bei werblichen Maßnahmen kann zusätzlich eine Einwilligung relevant sein.")
        open_points.append("Prüfen, ob für einzelne Kommunikationswege eine Einwilligung erforderlich ist.")
    else:
        legal_basis = "legitimate_interests"
        reasoning.append("Vorläufig erscheint eine Einordnung über berechtigte Interessen prüfungsbedürftig.")

    if processing.special_category_data or any(word in categories for word in ["gesund", "patient", "diagnos", "befund"]):
        special_basis = "medical"
        risk_level = "high"
        dpia_required = True
        reasoning.append("Es sprechen Anhaltspunkte für besondere Kategorien personenbezogener Daten im Sinne des Art. 9 DSGVO.")
        open_points.append("Prüfen, welche konkrete Sonderrechtsgrundlage des Art. 9 Abs. 2 DSGVO einschlägig ist.")

    if any(word in title + " " + dept for word in ["mandat", "kanzlei", "rechts", "anwalt", "bea"]):
        professional_secrecy = True
        reasoning.append("Es bestehen Anhaltspunkte für eine besondere Vertraulichkeit und mögliche Relevanz von Berufsgeheimnis bzw. § 203 StGB.")
        open_points.append("Prüfen, ob besondere Verschwiegenheitspflichten und Mandatsgeheimnis betroffen sind.")

    if any(word in title + " " + dept for word in ["patient", "praxis", "behandlung", "labor", "medizin"]):
        professional_secrecy = True
        reasoning.append("Es bestehen Anhaltspunkte für medizinische Verschwiegenheitspflichten.")
        open_points.append("Prüfen, ob Gesundheitsdaten umfassend verarbeitet werden und ob erhöhte Schutzmaßnahmen erforderlich sind.")

    if processing.third_country_transfer:
        risk_level = "high" if risk_level != "high" else risk_level
        open_points.append("Prüfen, auf welcher Grundlage der Drittlandtransfer erfolgt und ob geeignete Garantien vorliegen.")

    if "ki" in title or "ki" in purpose or "ai" in title or "ai" in purpose:
        dpia_required = True
        risk_level = "high"
        reasoning.append("Bei KI-gestützten Verfahren kann ein erhöhtes Risiko bestehen.")
        open_points.append("Prüfen, ob automatisierte Bewertungen, Profiling oder umfangreiche Analysen vorliegen.")

    suggestion = f"""
Vorgeschlagene Rechtsgrundlage Art. 6 DSGVO:
- {legal_basis or "offen"}

Vorgeschlagene Rechtsgrundlage Art. 9 DSGVO:
- {special_basis or "keine offensichtliche Sonderrechtsgrundlage"}

Berufsgeheimnis / § 203 StGB:
- {"Ja" if professional_secrecy else "Derzeit nicht naheliegend"}

Vorläufige Risikoeinstufung:
- {risk_level}

DSFA-Hinweis:
- {"DSFA-Bedarf erscheint möglich" if dpia_required else "DSFA-Bedarf erscheint derzeit nicht zwingend, sollte aber im Einzelfall geprüft werden"}

Juristische Begründung:
- {" ".join(reasoning) if reasoning else "Es ist eine einzelfallbezogene juristische Prüfung erforderlich."}

Offene Klärungspunkte:
- {"; ".join(open_points) if open_points else "Keine besonderen offenen Punkte aus der Erstprüfung erkennbar."}
""".strip()

    return {
        "legal_basis": legal_basis,
        "special_legal_basis": special_basis,
        "professional_secrecy": professional_secrecy,
        "dpia_required": dpia_required,
        "risk_level": risk_level,
        "legal_assessment_text": " ".join(reasoning),
        "open_issues": "\n".join(f"- {point}" for point in open_points) if open_points else "",
        "ai_suggestion": suggestion,
        "ai_prompt_version": PROMPT_VERSION,
        "ai_last_generated_at": timezone.now(),
    }