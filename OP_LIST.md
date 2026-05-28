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

## Maßnahmen – Prioritätenlogik & manuelle Priorisierung
Status: geplant  
Priorität: P1 (vor V1.0, nicht zwingend vor erstem Mandantentest)

Problem:
- Automatisch erzeugte Maßnahmen erhalten derzeit überwiegend Priorität „hoch“.
- Priorisierung ist dadurch fachlich wenig aussagekräftig.
- Admin/Bearbeiter kann Priorität derzeit nicht sauber fachlich korrigieren.

Ziel:
- Juristisch-konservative Prioritätslogik (anwaltlicher Ansatz)
- Differenzierung in:
  - hoch
  - mittel
  - niedrig
- Automatik setzt Erstpriorität fachlich begründet.
- Admin/Bearbeiter darf Priorität manuell ändern.
- Manuell gesetzte Priorität darf nicht bei jeder Neuberechnung überschrieben werden.

Geplante Logik:
- hoch:
  Rechtsgrundlage fehlt, Art. 9 ungeklärt, DSFA erforderlich,
  §203-Verfahren fehlt, Drittlandtransfer ungeklärt,
  TOM/AV-Vertrag fehlt, kritische Compliance-Lücken

- mittel:
  empfohlene DSFA, offene Bewertungen,
  fehlende Ergänzungen mit Risikocharakter,
  offene Prüfungen

- niedrig:
  reine Dokumentation/Vervollständigung,
  Komfort-/Review-Themen

Technische Idee:
- priority_source = auto/manual
  oder
- priority_manually_overridden = True/False

Wichtig:
- Bestehende Maßnahmenlogik nicht beschädigen.
- Keine automatische Rücküberschreibung manueller Prioritäten.

## Maßnahmen – verwaiste Audit-Maßnahmen
Status: offen

Problem:
- Audit-Maßnahmen bleiben bestehen, obwohl zugehörige Audits gelöscht wurden.

Ziel:
- automatische Gegenstandslosstellung
  oder
- Cleanup bei Audit-Löschung

Wichtig:
- keine versehentliche Löschung fachlich relevanter Maßnahmen

Dokumente / Storage
 Render Persistent Disk / Media Storage
Dokumente auf Render dauerhaft verfügbar
keine verlorenen Uploads nach Deploy/Restart
später Hetzner-migrationsfähig
Maßnahmen – Audit Cleanup
 Verwaiste Audit-Maßnahmen
bei Audit-Löschung automatisch gegenstandslos
oder Cleanup-Logik
Tenant Login / Rechte
 Mandantenlogin final prüfen
kein /admin/
direkte Weiterleitung in PROSSESSOR
Staff/Superuser standardmäßig aus
Rechteprüfung stabil
Tabellen Stabilität
 Verfahren-Tabelle final stabilisieren
wie Maßnahmen
Spaltenbreiten sauber
lesbar
Verschieben bleibt erhalten
keine überlappenden Titel/IDs

Maßnahmen – Bearbeitung
 Priorität manuell editierbar
 Status editierbar
 Notizen
 Wiedervorlage
 Automatik überschreibt manuelle Werte nicht
Dokumente – Viewer Konzept
 PDF im Browser
bevorzugt pdf.js
 DOCX/DOC sicher anzeigen
ggf. serverseitig nach PDF
 Downloadzwang vermeiden
Dokumente – Statusautomatik
 automatische Statusänderung
unbearbeitet → in Bearbeitung → final
Druckbarkeit
 Verfahrensübersicht druckbar
 Dokument-/Verfahrensreports sauber
Rollenmodell
 Role-Modell funktional machen
„Mandant“
„Leser“
„Bearbeiter“
„Admin“
aktuell nur Attrappe ohne Wirkung
P2 – Nach Stabilisierung / Nice-to-have
Compliance Dashboard
 Aggregierter Compliance-Status
 Ampellogik (bewusst zurückgestellt)
 offene Maßnahmen Dashboard
Dokumentenbearbeitung
 echter Writer/Viewer
 sichere Bearbeitung
 ggf. PDF-first Workflow
Secure Transfer
 verschlüsselter Dokumentenversand
 Upload bereits verschlüsselt
 kein klassisches Mailsystem
 Render/Hetzner-tauglich
Standardfälle / Templates
 Standardfälle sauber tenantbezogen auswählbar
Admin UX
 AuditQuestions vs AuditResponses verständlicher
 Rollen-/Permission-Modell transparenter
KI
 KI strikt getrennt halten
 tenantisolierte Wissensbasis
 Dokumentenvorschläge


## KI – Auditfragen & Verfahren intelligent erweitern (Admin-Service)
Status: geplant  
Priorität: P1 (nach Stabilisierung, vor größerem KI-Ausbau)

Ziel:
- Nicht immer dieselben Audits und Standardverfahren.
- Neue fachliche Ideen, Risiken und aktuelle Entwicklungen strukturiert einbringen.
- Admin-Servicefunktion, keine Mandantenfunktion.

Grundsatz:
- KI prüft Audits zunächst NICHT automatisch.
- KI bewertet keine Mandantenantworten.
- KI ersetzt keine juristische Prüfung.
- KI liefert ausschließlich Vorschläge.
- Admin entscheidet über Übernahme.

Sicherheits-/Datenschutzvorgaben:
- Keine automatische Verarbeitung von Echtdaten.
- Kein Zugriff auf:
  - Namen
  - Beschäftigtendaten
  - Patientendaten
  - Mandantendokumente
  - konkrete Verfahrensinhalte
- KI arbeitet anonymisiert, kategoriebasiert und admingeführt.
- Keine automatische Änderung von Mandantendaten.

### 1. KI-Vorschläge für neue Auditfragen
Admin-Ebene

Input:
- Branche
- Unternehmensprofil
- bestehende Verfahren
- vorhandene Auditfragen
- bekannte Risiken
- technische Umgebung

Ziel:
- fehlende Prüffelder erkennen
- neue Themen ergänzen
- Auditqualität erhöhen
- branchenspezifische Risiken berücksichtigen

Beispiele:
- KI-Nutzung im Unternehmen
- private Endgeräte / BYOD
- Homeoffice
- GPS/Tracking
- Cloudspeicher
- Videokonferenzen
- Schatten-IT
- Social Media / Recruiting

Ergebnis:
- Vorschlagsliste
- Admin entscheidet über Übernahme in Auditkatalog

---

### 2. KI-Vorschläge für fehlende Verfahren
Admin-Ebene

Ziel:
- typische, oft vergessene Verarbeitungsvorgänge erkennen

Beispiel:
Vorhanden:
- Lohnbuchhaltung
- Bewerbermanagement
- Website
- CRM

KI schlägt vor:
- Newsletter
- Zeiterfassung
- Supportsystem
- Videoüberwachung
- Mobile Geräteverwaltung
- KI-Systeme
- Cloudspeicher
- Bewerberpool

Wichtig:
- Nur Vorschlag
- Keine automatische Anlage

---

### 3. KI-Quellen-/Innovationsbot
(Admin-Service)

Ziel:
- neue Auditideen und Datenschutzentwicklungen einbringen

Mögliche Quellen:
- Datenschutzkonferenz (DSK)
- Aufsichtsbehörden
- EDPB
- LfDI
- technische Entwicklungen
- neue Compliance-Risiken

Funktion:
- Vorschläge für:
  - neue Auditfragen
  - neue Verfahren
  - neue Risiken
  - neue Prüfschwerpunkte

Beispiel:
„Neue Auditfrage empfohlen:
Werden Mitarbeitende beim Einsatz generativer KI geschult?“

---

Zukunftsidee (später):
- lernender Audit-/Verfahrenskatalog
- Admin entscheidet immer final
- keine automatische Rechtsanwendung