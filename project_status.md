Ich arbeite an einem Django-Projekt namens „PROSSESSOR“.
Es handelt sich um ein mandantenfähiges Datenschutz- und Compliance-Tool mit Fokus auf DSGVO.

WICHTIG:

Arbeite strikt nach meinen Vorgaben
Keine Architekturänderungen ohne Zustimmung
Immer vollständige Dateien liefern (kein Snippet-Flickwerk)
Erst analysieren, dann ändern
AKTUELLER STAND

Das System enthält folgende Kernmodule:

Verarbeitungstätigkeiten (Art. 30 DSGVO)
Rechtsbewertung (Art. 6 / Art. 9 DSGVO)
DSFA-Modul (Art. 35 DSGVO) → gerade neu strukturiert
Maßnahmenmanagement
KI-Unterstützung (Mock + vorbereitet für OpenAI)
DSFA-SYSTEM (AKTUELLER FOKUS)

Die DSFA wurde gerade neu aufgebaut mit:

DPIACheck (Vorprüfung)
Muss-Liste (entscheidend)
Prüfkontext (ehemals Standardfall)
Risikomatrix
Empfehlungssystem
DPIA (eigentliche DSFA)
DPIARisk
DPIAMeasure
WICHTIGE DESIGNREGELN
Muss-Liste = harter Trigger → DSFA erforderlich
Prüfkontext = nur Kontext, KEIN Automatismus
Rechtsbewertung darf DSFA NICHT mehr selbst bestimmen
DSFA ist führend
OFFENE KERNAUFGABE

Wir müssen:

Rechtsbewertung mit DSFA synchronisieren
Kein Widerspruch möglich
Bei Muss-Fall → DSFA zwingend
UI vereinfachen
unnötige Checkboxen entfernen
klare Nutzerführung
Maßnahmenlogik schärfen
fehlende DSFA → Maßnahme
fehlende Begründung → Maßnahme
DEINE AUFGABE

Bitte fordere jetzt folgende Dateien an, bevor du irgendetwas änderst:

dpia/models.py
dpia/views.py
dpia/forms.py
templates/dpia/form.html
legal/models.py
legal/forms.py
legal/views.py
templates/legal/legal_assessment_form.html
actions/services.py

Danach:

analysieren
Inkonsistenzen identifizieren
mir einen strukturierten Plan geben
erst danach Code liefern

WICHTIG:
Ich bin Jurist. Die Lösung muss rechtlich sauber und logisch konsistent sein.