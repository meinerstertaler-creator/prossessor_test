# Architekturentscheidungen – PROSSESSOR

Diese Datei dokumentiert stabile Architekturentscheidungen und konzeptionelle Leitlinien.
Sie darf nicht automatisch überschrieben werden und dient der konsistenten Weiterentwicklung über mehrere Entwicklungsphasen hinweg.

--------------------------------------------------
🟠 AD-001: Maßnahmen müssen konkret referenzierbar sein
--------------------------------------------------

Status:
- Maßnahmen werden aktuell automatisch aus fachlichen Regeln erzeugt
- Zuordnung zu Verarbeitung und Rechtsbewertung funktioniert
- Inhalte sind teilweise noch zu allgemein

Problem:
Für das geplante Mandanten-Historienprotokoll müssen Maßnahmen auch nach Erledigung oder Löschung nachvollziehbar bleiben.

Aktuell fehlt teilweise ein konkreter Bezug zu:
- einzelnen Feldern
- konkreten Bearbeitungsschritten
- konkreten fachlichen Ursachen

Ziel:
Maßnahmen müssen eindeutig referenzierbar sein.

Beispiele (Soll-Zustand):
- „Feld Zweck der Verarbeitung ausfüllen“
- „Feld Drittlandtransferbeschreibung ergänzen“
- „Rechtsbewertung ergänzen“
- „DSFA durchführen“

Technische Zielstruktur:
- reference_type (z. B. field_missing, workflow_step)
- reference_field (z. B. purpose, legal_assessment_text)
- reference_label (z. B. „Zweck der Verarbeitung“)

Konsequenzen:
- Maßnahmen sind nicht nur Text, sondern strukturiert auswertbar
- Grundlage für:
  - Historienprotokoll
  - UI-Navigation („zum Feld springen“)
  - KI-Verbesserung

--------------------------------------------------
🟠 AD-002: Keine Löschung erledigter Maßnahmen vor Referenzierung
--------------------------------------------------

Status:
- Maßnahmen können aktuell automatisch erledigt werden
- Löschlogik ist noch nicht implementiert

Problem:
Ohne konkrete Referenz sind gelöschte Maßnahmen später nicht nachvollziehbar.

Entscheidung:
Eine automatische Löschung erledigter Maßnahmen wird vorerst NICHT umgesetzt.

Begründung:
Zuerst müssen Maßnahmen ausreichend konkret referenzierbar sein.

Erst danach:
1. Historienprotokoll implementieren
2. Entscheidung:
   - Löschung
   - oder Archivierung

Geplante Erweiterung:
- Löschlogik (z. B. nach 30 Tagen)
- Speicherung im Mandanten-Historienprotokoll

Priorität:
mittel
Maßnahmen-Navigation später verfeinern:
Der Bearbeiten-Einstieg aus der Maßnahmenliste führt derzeit bewusst auf den zentralen Vorgangsbildschirm. Später kann geprüft werden, ob abhängig von der Maßnahmenquelle direkt in den fachlich spezifischen Editor verzweigt werden soll (z. B. Rechtsbewertung, DSFA oder Vorgang bearbeiten). Der Punkt wird vorerst zurückgestellt, da der aktuelle Workflow ausreichend nutzbar ist und die direkte Quellnavigation technisch und konzeptionell aufwendiger ist.
Priorität: mittel
# Open Points – PROSSESSOR

## A. Dokumentenmodul – nächster Hauptschritt

### 1. Fachmodell klären
- Welche Dokumentarten gibt es?
- Welche Ordnerstruktur wird benötigt?
- Wie werden Muster, AV-Verträge und sonstige Dokumente unterschieden?

### 2. Rechtekonzept umsetzen
- Muster: für alle sichtbar
- tenantbezogene Dokumente: nur für den jeweiligen Tenant sichtbar
- AV-Verträge: zusätzlich optional an Auftragsverarbeiter koppelbar
- Admin: vollständige Sicht- und Bearbeitungsrechte

### 3. Grundfunktionen
- Ordner anlegen
- Dokument hochladen
- Dokument einem Ordner zuordnen
- Dokument Mandant zuordnen
- Dokument optional Auftragsverarbeiter zuordnen
- Liste / Detail / Download

---

## B. Auditmodul – Stabilisierung nachziehen

### 1. Vollständigen Testpfad durchspielen
- Audit anlegen
- Verfahren prüfen
- neue Verfahren erfassen
- Checkliste ausfüllen
- Maßnahmen erzeugen
- vorläufig abschließen
- endgültig abschließen / Jahresaudit beenden

### 2. Maßnahmenlogik prüfen
- `Unverändert` darf nicht blockieren
- offene Maßnahmen müssen korrekt gezählt werden
- gegenstandslose Maßnahmen dürfen Abschluss nicht blockieren

### 3. Bericht testen
- Bericht im Reportbereich öffnen
- Freitext speichern
- Bericht konsistent mit Auditstatus prüfen

---

## C. V2-Vorbereitung Audit

### 1. Einheitliche Checklistenarchitektur
- `AuditQuestion` als Fragenpool verstehen
- auditbezogene Checklisteninstanz statt modellgetrennter Logik

### 2. Dokumentenbezug vorbereiten
Späterer Ausbau:
- Dokumente analysieren
- Vorschläge für Auditfragen erzeugen
- Musterchecklisten und DIN-/ISO-orientierte Kriterien einbinden

---

## D. Reports – spätere Ausbaustufen
- PDF-Ausgabe
- Berichtsdateien sauber ablegen
- Monatsprotokoll / Aktivitätsübersicht
- zentrale Reportübersicht je Mandant

---

## E. UI / Design – später einheitlich harmonisieren
- Kartenlayout vereinheitlichen
- Moduldesign angleichen
- keine Vorab-Einzelentscheidungen vor technischer Stabilisierung

##f  KI-gestützte Dokumentenauswertung bei Auftragsverarbeitern
AV-Verträge und TOM sollen später durch die KI ausgewertet werden.
Relevante Inhalte sollen als Kurzzusammenfassung in die Felder des Auftragsverarbeiters übernommen oder zur Übernahme vorgeschlagen werden.
Bei Upload eines ersetzenden oder neueren Dokuments soll ein Warnhinweis erscheinen, dass die Angaben zur Datenverarbeitung zu prüfen bzw. zu aktualisieren sind. Zudem soll einen automatsierte Maßnahme aufgenommen werden, die auf den AV verweist

