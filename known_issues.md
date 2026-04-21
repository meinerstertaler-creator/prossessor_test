PROJEKT: Privacy Tool (Django)

Zweck:
Dokumentation bekannter Probleme, technischer Besonderheiten und bewusst akzeptierter Einschränkungen.
Diese Datei dient dazu, Fehler in neuen Chats NICHT neu zu „erfinden“.

--------------------------------------------------
🔴 AKTUELLE BEKANNTE PROBLEME
--------------------------------------------------

1. KI nutzt aktuell Dummy-Daten
Status:
- generate_ai_structured_output() liefert Mock-Daten
Auswirkung:
- keine echte juristische Bewertung
- UI wirkt korrekt, aber Inhalt ist nicht valide
Geplante Lösung:
- OpenAI-Integration

--------------------------------------------------

2. SQLite statt PostgreSQL
Status:
- Entwicklung läuft auf SQLite
Auswirkung:
- nicht produktionsfähig
- mögliche Unterschiede bei Queries/Migrationen
Geplante Lösung:
- Umstellung auf PostgreSQL vor Deployment

--------------------------------------------------

3. Performance bei großen Chats / langen Prozessen
Status:
- lange Verarbeitungsketten (KI + Kontext)
Auswirkung:
- potenziell langsame Views
Geplante Lösung:
- später ggf. Async / Celery

--------------------------------------------------

4. Wissenssystem noch nicht voll integriert
Status:
- knowledge / templates / sources vorhanden
- Nutzung im Prompt nur teilweise
Auswirkung:
- KI nutzt vorhandenes Wissen noch nicht optimal
Geplante Lösung:
- Ausbau Prompt-Integration

--------------------------------------------------

5. UI-Logik (Interessenabwägung) abhängig von Rechtsgrundlage
Status:
- dynamisches JS-Rendering
Auswirkung:
- mögliche Inkonsistenzen bei Formularzuständen
Hinweis:
- Server-seitige Validierung später ergänzen

--------------------------------------------------


--------------------------------------------------
🟡 TECHNISCHE BESONDERHEITEN (KEINE FEHLER)
--------------------------------------------------

1. KI-Architektur ist bewusst modular
- Context → Prompt → Engine → Mapping
- darf NICHT zusammengelegt werden

--------------------------------------------------

2. Mapping ist getrennt von KI
- KI liefert strukturierte Daten
- Mapping schreibt in DB
- keine direkte DB-Schreiblogik in KI

--------------------------------------------------

3. Orchestrierung erfolgt zentral in Views
- z. B. legal_assessment_upsert()
- steuert gesamten Ablauf

--------------------------------------------------

4. AnalyseTexte sind Rohinput für KI
- keine Vorverarbeitung erzwingen
- bewusst „roh“ für juristische Argumentation

--------------------------------------------------


--------------------------------------------------
🟠 HÄUFIGE FEHLERQUELLEN
--------------------------------------------------

1. Änderungen an mehreren Schichten gleichzeitig
Problem:
- führt zu schwer nachvollziehbaren Bugs
Regel:
- immer nur eine Schicht ändern

--------------------------------------------------

2. Unvollständige JSON-Struktur von KI
Problem:
- Mapping bricht oder speichert falsch
Regel:
- KI-Ausgabe strikt validieren

--------------------------------------------------

3. Fehlende oder falsche Feldzuordnung
Problem:
- Daten landen im falschen DB-Feld
Regel:
- Mapping immer explizit prüfen

--------------------------------------------------

4. Änderungen an URLs / Views ohne Templates anzupassen
Problem:
- Broken Links / Reverse Errors

--------------------------------------------------

5. Unterschiedliche Zustände zwischen UI und Backend
Problem:
- JS zeigt Felder, Backend erwartet andere Daten

--------------------------------------------------


--------------------------------------------------
🔵 DEPLOYMENT-BESONDERHEITEN (WICHTIG FÜR RENDER)
--------------------------------------------------

1. SQLite nicht geeignet für Deployment
→ PostgreSQL erforderlich

2. Statische Dateien müssen konfiguriert werden
→ WhiteNoise oder CDN

3. Media-Dateien nicht lokal speichern
→ später externer Storage

4. DEBUG muss deaktiviert werden

5. ALLOWED_HOSTS korrekt setzen

--------------------------------------------------


--------------------------------------------------
🟢 BEWUSSTE DESIGNENTSCHEIDUNGEN
--------------------------------------------------

- KI generisch (nicht nur Interessenabwägung)
- strukturierte Ausgabe statt Freitext
- Trennung von:
  → Logik
  → KI
  → Mapping
  → UI

--------------------------------------------------
# KNOWN ISSUES

## 1. DSFA / Rechtsbewertung Inkonsistenz

* aktuell teilweise doppelte Logik
* Muss-Fall nicht überall erzwungen

---

## 2. UI-Komplexität

* zu viele Checkboxen
* unklare Nutzerführung

---

## 3. Migrationen

* mehrfach angepasst
* Risiko inkonsistenter DB-Struktur

---

## 4. KI-System

* aktuell Mock
* noch keine echte Bewertung

---

## 5. Maßnahmenlogik

* teilweise redundant
* noch nicht vollständig regelbasiert

---

## 6. Performance (zukünftig)

* SQLite aktuell
* PostgreSQL geplant

---

## 7. Architektur-Risiko

* viele schnelle Änderungen
  → Gefahr von Inkonsistenzen
# Known Issues – PROSSESSOR

## 1. Audit-Checkliste fachlich noch nicht ausgereift

Die allgemeine Audit-Checkliste im Hauptaudit ist technisch eingebunden, fachlich aber noch nicht abschließend konsolidiert.

### Stand
- Die Checkliste ist im verfahrensorientierten Audit als eigener Abschnitt eingebunden.
- Fragen werden aus `AuditQuestion` bezogen.
- Antworten und Maßnahmenlogik sind technisch vorhanden.

### Problem
- Die Checklistenarchitektur ist noch nicht das endgültige Zielmodell.
- Es bestehen historisch zwei getrennte technische Auditmodelle:
  - `Audit` für Spezialaudit
  - `ProcedureAudit` für verfahrensorientiertes Hauptaudit
- Dadurch existieren derzeit auch noch zwei getrennte technische Checklistenpfade.

### Bewertung
Dies ist kein Blocking-Issue für V1, aber ein bewusst offener Architekturpunkt für V2.

### Zielbild V2
- einheitliche auditbezogene Checklistenlogik
- zentraler Fragenpool
- auditbezogene Instanziierung von Checklisten
- später KI-gestützte Vorschläge aus Dokumenten, Musterchecklisten und Fachquellen

---

## 2. Auditbericht aktuell nur einfach umgesetzt

### Stand
- Ein einfacher Auditbericht ist im Reportbereich vorhanden.
- Der Auditor kann einen Freitext ergänzen.
- Die Berichtslogik ist funktional, aber noch nicht final ausgebaut.

### Offene Punkte
- PDF-Ausgabe noch nicht final angebunden
- Dateistruktur / Berichtsablage noch nicht vollständig finalisiert
- später Monatsprotokoll bzw. Aktivitätsreport denkbar

---

## 3. Dokumentenmodul noch nicht fertiggestellt

### Stand
- Dokumentenmodul ist als nächster Entwicklungsschritt vorgesehen
- konkrete Rechte- und Ordnerlogik noch nicht final implementiert

### Ziel
- Muster für alle sichtbar
- AV-Verträge nur tenantbezogen sichtbar
- Admin sieht und bearbeitet alles

---

## 4. UI noch nicht vereinheitlicht

### Stand
Einzelne Module sind funktional, aber nicht abschließend im Gesamtdesign harmonisiert.

### Wichtig
Aktuell werden bewusst keine isolierten Einzel-Designentscheidungen vorgezogen, bevor die Kernmodule technisch stabil fertiggestellt sind.

---

## 5. Audit-/Checklistenarchitektur als geplanter V2-Punkt

### Problem
Die historische Trennung zwischen Spezialaudit und Hauptaudit ist technisch noch sichtbar.

### Entscheidung
Kein Rückbau im laufenden V1, sondern:
- V1 stabilisieren
- V2 kontrolliert beginnen
- Altlogik nicht weiter ausbauen