from django.core.management.base import BaseCommand
from processing.models import ProcessingStandardCase


STANDARD_CASES = [
    # =========================
    # ALLGEMEIN
    # =========================
    {
        "name": "Zeiterfassung",
        "category": ProcessingStandardCase.Category.HR,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Erfassung und Verwaltung von Arbeitszeiten, Anwesenheiten oder Abwesenheiten.",
        "dsfa_relevance_note": "Regelmäßig keine automatische DSFA-Pflicht; Relevanz steigt bei Auswertungen mit Kontrollcharakter.",
    },
    {
        "name": "Auswertung technischer Protokolle",
        "category": ProcessingStandardCase.Category.IT_SECURITY,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Auswertung von Logfiles, Systemprotokollen oder technischen Nutzungsdaten.",
        "dsfa_relevance_note": "DSFA-Relevanz steigt bei personenbezogener Verhaltens- oder Leistungsauswertung.",
    },
    {
        "name": "Nutzung von Cloud-Diensten",
        "category": ProcessingStandardCase.Category.IT_SECURITY,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Nutzung externer Cloud-Dienste zur Datenverarbeitung oder Zusammenarbeit.",
        "dsfa_relevance_note": "DSFA-Relevanz kann bei sensiblen Daten, großem Umfang oder Drittlandtransfer steigen.",
    },
    {
        "name": "Homeofficeverfahren",
        "category": ProcessingStandardCase.Category.HR,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.LOW,
        "description": "Organisation und datenschutzrechtliche Absicherung von Homeoffice-Arbeitsplätzen.",
        "dsfa_relevance_note": "Regelmäßig keine DSFA-Pflicht, außer bei zusätzlicher Überwachungs- oder Kontrolltechnik.",
    },
    {
        "name": "BYOD-Verfahren",
        "category": ProcessingStandardCase.Category.IT_SECURITY,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Nutzung privater Endgeräte für betriebliche Zwecke.",
        "dsfa_relevance_note": "DSFA-Relevanz steigt bei umfangreicher technischer Kontrolle oder sensiblen Daten.",
    },
    {
        "name": "Überlassung Mobiltelefon",
        "category": ProcessingStandardCase.Category.HR,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.LOW,
        "description": "Bereitstellung mobiler Endgeräte an Beschäftigte.",
        "dsfa_relevance_note": "Regelmäßig niedrige DSFA-Relevanz, außer bei Tracking oder tiefer Nutzungsüberwachung.",
    },
    {
        "name": "Überlassung Notebook/PC",
        "category": ProcessingStandardCase.Category.HR,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.LOW,
        "description": "Bereitstellung von Notebooks oder PCs an Beschäftigte.",
        "dsfa_relevance_note": "Regelmäßig niedrige DSFA-Relevanz; Bewertung hängt von Monitoring und Datenumfang ab.",
    },
    {
        "name": "Übermittlung an externe Dienstleister",
        "category": ProcessingStandardCase.Category.DATA_TRANSFER,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Weitergabe personenbezogener Daten an externe Dienstleister oder Auftragsverarbeiter.",
        "dsfa_relevance_note": "DSFA-Relevanz steigt bei sensiblen Daten, großem Umfang oder Drittlandtransfer.",
    },
    {
        "name": "Stellvertretungsverfahren",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.LOW,
        "description": "Regelung des Zugriffs und der Vertretung bei Abwesenheiten oder Rollenwechseln.",
        "dsfa_relevance_note": "Regelmäßig keine DSFA-Pflicht, außer bei besonderem Datenzugriff oder großem Umfang.",
    },
    {
        "name": "Software im Betrieb",
        "category": ProcessingStandardCase.Category.IT_SECURITY,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Einführung oder Nutzung betrieblicher Software mit Personenbezug.",
        "dsfa_relevance_note": "DSFA-Relevanz hängt stark von Funktion, Datenumfang und Kontrollmöglichkeiten ab.",
    },
    {
        "name": "Elektronisches Konferenzsystem",
        "category": ProcessingStandardCase.Category.COMMUNICATION,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Elektronische Konferenz-, Meeting- oder Collaboration-Systeme.",
        "dsfa_relevance_note": "DSFA-Relevanz steigt bei Aufzeichnung, Auswertung oder sensiblen Inhalten.",
    },
    {
        "name": "Konzerndatenaustausch",
        "category": ProcessingStandardCase.Category.DATA_TRANSFER,
        "is_general": True,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Übermittlung personenbezogener Daten innerhalb einer Unternehmensgruppe.",
        "dsfa_relevance_note": "DSFA-Relevanz steigt bei großem Umfang, sensiblen Daten oder Drittlandbezug.",
    },

    # =========================
    # ÜBERWACHUNG / TRACKING
    # =========================
    {
        "name": "Videoaußenüberwachung",
        "category": ProcessingStandardCase.Category.MONITORING,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Videoüberwachung im Außenbereich, z. B. Gelände, Einfahrten oder Zugänge.",
        "dsfa_relevance_note": "Erhöhte DSFA-Relevanz; Muss-Liste gesondert prüfen.",
    },
    {
        "name": "Videoeinzelraumüberwachung",
        "category": ProcessingStandardCase.Category.MONITORING,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Videoüberwachung einzelner Innenräume.",
        "dsfa_relevance_note": "Erhöhte DSFA-Relevanz; Beschäftigtenbezug und Eingriffsintensität gesondert prüfen.",
    },
    {
        "name": "GPS-Tracking",
        "category": ProcessingStandardCase.Category.MONITORING,
        "is_general": True,
        "applies_to_legal": True,
        "applies_to_medical": True,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Ortung oder Nachverfolgung von Personen, Fahrzeugen oder Geräten.",
        "dsfa_relevance_note": "Regelmäßig erhöhte DSFA-Relevanz, insbesondere bei Beschäftigtenbezug oder lückenlosem Tracking.",
    },

    # =========================
    # KANZLEI
    # =========================
    {
        "name": "Mandantenverwaltung",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": False,
        "applies_to_legal": True,
        "applies_to_medical": False,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Verwaltung von Mandantenstammdaten, Akten und zugehörigen Informationen.",
        "dsfa_relevance_note": "Regelmäßig keine automatische DSFA-Pflicht; Relevanz steigt bei sensiblen Daten oder großem Umfang.",
    },
    {
        "name": "Fristen- und Terminverwaltung",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": False,
        "applies_to_legal": True,
        "applies_to_medical": False,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.LOW,
        "description": "Verwaltung von Fristen, Terminen und Wiedervorlagen in der Kanzlei.",
        "dsfa_relevance_note": "Regelmäßig niedrige DSFA-Relevanz.",
    },
    {
        "name": "Elektronische Aktenführung Kanzlei",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": False,
        "applies_to_legal": True,
        "applies_to_medical": False,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Digitale Aktenführung und Dokumentenverwaltung in der Kanzlei.",
        "dsfa_relevance_note": "Relevanz steigt bei sensiblen Inhalten, Massenverfahren oder KI-gestützter Auswertung.",
    },
    {
        "name": "Kommunikation mit Mandanten",
        "category": ProcessingStandardCase.Category.COMMUNICATION,
        "is_general": False,
        "applies_to_legal": True,
        "applies_to_medical": False,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Kommunikation mit Mandanten per E-Mail, Portalen, Messaging oder Videotools.",
        "dsfa_relevance_note": "Relevanz steigt bei sensiblen Daten, Aufzeichnungen oder Cloud-Einsatz.",
    },
    {
        "name": "beA- / Behördenkommunikation",
        "category": ProcessingStandardCase.Category.COMMUNICATION,
        "is_general": False,
        "applies_to_legal": True,
        "applies_to_medical": False,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Elektronische Kommunikation mit Gerichten, Behörden oder über das beA.",
        "dsfa_relevance_note": "Regelmäßig keine automatische DSFA-Pflicht, aber hohe Sensibilität der Inhalte.",
    },

    # =========================
    # ARZTPRAXIS
    # =========================
    {
        "name": "Patientenverwaltung",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": True,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Verwaltung von Patientendaten, Terminen und Behandlungsinformationen.",
        "dsfa_relevance_note": "Hohe DSFA-Relevanz wegen Gesundheitsdaten.",
    },
    {
        "name": "Behandlungsdokumentation",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": True,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Dokumentation medizinischer Behandlungen, Diagnosen und Verläufe.",
        "dsfa_relevance_note": "Gesundheitsdaten mit regelmäßig erhöhter DSFA-Relevanz.",
    },
    {
        "name": "Terminverwaltung Praxis",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": True,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Praxisbezogene Termin- und Ressourcenverwaltung.",
        "dsfa_relevance_note": "Relevanz steigt bei Verknüpfung mit Gesundheitsdaten oder automatisierter Auswertung.",
    },
    {
        "name": "Abrechnung mit Krankenkassen",
        "category": ProcessingStandardCase.Category.DATA_TRANSFER,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": True,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Abrechnungsprozesse mit Krankenkassen oder Abrechnungsstellen.",
        "dsfa_relevance_note": "Relevanz steigt wegen Gesundheitsbezug und externen Übermittlungen.",
    },
    {
        "name": "Labordaten / externe Diagnostik",
        "category": ProcessingStandardCase.Category.DATA_TRANSFER,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": True,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Übermittlung und Verarbeitung von Labor- oder Diagnostikdaten.",
        "dsfa_relevance_note": "Häufig hohe DSFA-Relevanz wegen Gesundheitsdaten und externer Einbindung.",
    },
    {
        "name": "Telemedizin / Videosprechstunde",
        "category": ProcessingStandardCase.Category.COMMUNICATION,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": True,
        "applies_to_industry": False,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Durchführung von Videosprechstunden oder telemedizinischen Leistungen.",
        "dsfa_relevance_note": "Erhöhte DSFA-Relevanz wegen Gesundheitsdaten und Kommunikationssystemen.",
    },

    # =========================
    # PRODUZIERENDES GEWERBE
    # =========================
    {
        "name": "Betriebliches Sicherheitsverfahren",
        "category": ProcessingStandardCase.Category.IT_SECURITY,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Sicherheits- oder Notfallverfahren mit Personenbezug, z. B. Zutritt, Vorfallmanagement oder Werkschutz.",
        "dsfa_relevance_note": "DSFA-Relevanz steigt bei Video, Tracking oder Verhaltenskontrolle.",
    },
    {
        "name": "Zutrittskontrolle / Werkschutz",
        "category": ProcessingStandardCase.Category.MONITORING,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Zutrittskontrolle zu Werksgeländen, Gebäuden oder Sicherheitsbereichen.",
        "dsfa_relevance_note": "Relevanz steigt bei biometrischen Systemen oder Bewegungsprofilen.",
    },
    {
        "name": "Schichtplanung",
        "category": ProcessingStandardCase.Category.HR,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.LOW,
        "description": "Planung und Steuerung von Schichten und Einsatzzeiten.",
        "dsfa_relevance_note": "Regelmäßig niedrige DSFA-Relevanz, außer bei tiefer Auswertung oder Leistungsüberwachung.",
    },
    {
        "name": "Qualitätssicherung mit Personenbezug",
        "category": ProcessingStandardCase.Category.CORE_PROCESS,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.MEDIUM,
        "description": "Qualitätssicherungsprozesse mit Bezug zu Beschäftigten oder personenbezogenen Leistungsdaten.",
        "dsfa_relevance_note": "Relevanz steigt bei Auswertungen mit Kontroll- oder Rankingcharakter.",
    },
    {
        "name": "Produktionsmonitoring Mitarbeiter",
        "category": ProcessingStandardCase.Category.MONITORING,
        "is_general": False,
        "applies_to_legal": False,
        "applies_to_medical": False,
        "applies_to_industry": True,
        "risk_hint": ProcessingStandardCase.RiskHint.HIGH,
        "description": "Überwachung oder Auswertung produktionsbezogener Mitarbeiterdaten.",
        "dsfa_relevance_note": "Regelmäßig hohe DSFA-Relevanz bei Verhaltens- oder Leistungskontrolle.",
    },
]


class Command(BaseCommand):
    help = "Seed Standardfälle für Verfahren"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Löscht alle bestehenden Standardfälle und legt sie neu an.",
        )

    def handle(self, *args, **options):
        reset = options["reset"]

        if reset:
            self.stdout.write("Lösche bestehende Standardfälle ...")
            ProcessingStandardCase.objects.all().delete()

        created = 0
        updated = 0

        for index, case in enumerate(STANDARD_CASES, start=1):
            _, was_created = ProcessingStandardCase.objects.update_or_create(
                name=case["name"],
                defaults={
                    "category": case["category"],
                    "description": case.get("description", ""),
                    "is_active": True,
                    "is_general": case.get("is_general", True),
                    "applies_to_legal": case.get("applies_to_legal", False),
                    "applies_to_medical": case.get("applies_to_medical", False),
                    "applies_to_industry": case.get("applies_to_industry", False),
                    "risk_hint": case.get("risk_hint", ""),
                    "dsfa_relevance_note": case.get("dsfa_relevance_note", ""),
                    "sort_order": index * 10,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Standardfälle verarbeitet: {created} erstellt, {updated} aktualisiert."
            )
        )