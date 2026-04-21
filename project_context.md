PROJEKT: Privacy Tool (Django Datenschutz-Compliance-Software)

🎯 Ziel
Webanwendung für datenschutzrechtliche Compliance in Kanzleien, insbesondere:
- Verarbeitungstätigkeiten (Art. 30 DSGVO)
- Rechtsgrundlagenprüfung (Art. 6, 9 DSGVO)
- Interessenabwägung (Art. 6 Abs. 1 lit. f DSGVO)
- Datenschutz-Folgenabschätzung (Art. 35 DSGVO)
- KI-gestützte juristische Unterstützung

Ziel ist eine skalierbare, mandantenfähige Software.

🧱 Architektur (wichtig – darf NICHT ohne Rücksprache geändert werden)

Apps:
- processing → Verarbeitungsvorgänge
- legal → Rechtsbewertungen / Interessenabwägung
- dpia → DSFA
- knowledge → Wissensbasis / AnalyseTexte
- actions → Maßnahmen / Aufgaben

🧠 KI-Architektur (zentrale Systemlogik)

Die KI ist modular aufgebaut und MUSS so erhalten bleiben:

1. Context Builder
Funktion: build_ai_context_bundle()
→ sammelt:
- Verarbeitungsvorgang
- Rechtsbewertung
- AnalyseTexte
- Wissensdaten
- Templates
- Quellen

2. Prompt Builder
Funktion: build_ai_prompt_stub()
→ erstellt strukturierten Prompt aus Kontext + Rohtexten

3. KI-Engine
Funktion: generate_ai_structured_output()
→ aktuell Dummy
→ soll durch OpenAI ersetzt werden

4. Mapping Layer
Funktion: apply_ai_result_to_assessment()
→ überträgt strukturierte KI-Ausgabe in Datenbankfelder

5. Orchestrierung (View)
Funktion: legal_assessment_upsert()
→ steuert Formular, KI, Mapping, Speicherung

⚠️ Wichtige Designprinzipien

- KI arbeitet strukturiert (JSON), nicht nur Text
- KI ist generisch nutzbar (nicht nur Interessenabwägung)
- AnalyseTexte werden aktiv im Prompt verwendet
- System kombiniert:
  → juristische Bewertung
  → Strukturierung
  → Aufgabenlogik (Compliance)

⚖️ Compliance-Logik

Funktion: generate_legal_assessment_actions()

Erzeugt automatisch Aufgaben bei:
- fehlender Rechtsgrundlage
- fehlender Interessenabwägung
- DSFA-Pflicht
- Drittlandtransfer

🖥️ UI-Logik

- Interessenabwägung wird dynamisch angezeigt
- nur bei Art. 6 Abs. 1 lit. f DSGVO sichtbar
- KI-Button füllt Formularfelder direkt

🗄️ Technik

- Django
- aktuell SQLite
- Ziel: PostgreSQL
- Deployment geplant über Render → später VPS (Hetzner/IONOS)

❗ Grenzen (sehr wichtig)

- Keine Änderung der KI-Architektur ohne Rücksprache
- Keine Vermischung von View / KI / Mapping
- Keine „Monolithen“ bauen – Modularität erhalten

PROJECT CONTEXT – PROSSESSOR
Ziel des Systems

Aufbau eines mandantenfähigen Datenschutz- und Compliance-Tools für Kanzleien und Unternehmen.

Fokus:

DSGVO-Compliance
strukturierte Rechtsbewertung
skalierbares Wissenssystem
KI-Unterstützung
Grundprinzip

Das System soll nicht nur dokumentieren, sondern:
→ den Nutzer führen

Kernidee
Strukturierte Eingabe
Automatische Bewertung
KI-gestützte Vorschläge
Maßnahmenmanagement
Besonderheit

Das System wächst mit:

Wissensdatenbank
KI-Vorschläge
Nutzerentscheidungen
Zielbild
Vollautomatisierte Compliance-Unterstützung
Reduktion juristischer Routinearbeit
skalierbare Kanzleilösung
Aktueller Fokus

DSFA-System als Herzstück für Risikobewertung
# PROSSESSOR – Projektkontext

## Projektziel

PROSSESSOR ist eine mandantenfähige Django-Webanwendung für Datenschutz- und Compliance-Organisation in Unternehmen und Kanzleiumfeld.

Der Schwerpunkt liegt auf einer strukturierten, nachvollziehbaren und rechtlich orientierten Bearbeitung von Datenschutz- und Auditprozessen.

## Kernmodule

### 1. Verfahren
Erfassung und Pflege von Verarbeitungsvorgängen im Sinne von Art. 30 DSGVO.

### 2. Rechtliche Bewertung
Prüfung von Rechtsgrundlagen, Interessenabwägung und weiteren datenschutzrechtlichen Zulässigkeitsfragen.

### 3. DSFA
Prüfung, Dokumentation und Maßnahmenbearbeitung im Zusammenhang mit Datenschutz-Folgenabschätzungen.

### 4. Maßnahmen
Zentrale Aufgaben- und Maßnahmensteuerung mit Statuslogik, Historie und Bezug auf die Fachmodule.

### 5. Audits
Auditmodul mit Schwerpunkt auf verfahrensorientierten Audits, neuen Verfahren, allgemeiner Audit-Checkliste und Berichtserstellung.

### 6. Dokumente
Eigenes Dokumentenmodul für Vorlagen, Muster, AV-Verträge, Richtlinien und weitere compliance-relevante Dokumente. Dieses Modul ist der nächste Entwicklungsschritt.

## Aktueller Entwicklungsstand

Das Auditmodul ist technisch weit fortgeschritten und für V1 grundsätzlich funktionsfähig. Es umfasst derzeit:

- Auditrahmen
- Verfahrensprüfung
- neue Verfahren
- allgemeine Audit-Checkliste
- Maßnahmenableitung
- vorläufigen Auditabschluss
- Endabschluss / Jahresaudit beenden
- einfachen Auditbericht im Reportbereich

Die Audit-Checkliste ist fachlich noch nicht endgültig ausgereift und wird bewusst als offener Punkt behandelt.

## Nächster Entwicklungsschritt

Priorität hat nun das Dokumentenmodul. Ziel ist eine stabile, nachvollziehbare und mandantenfähige Dokumentenverwaltung mit Rechtestruktur.

Geplante Grundfunktionen:

- Ordner anlegen
- Dokumente hochladen
- Dokumente Ordnern zuordnen
- Dokumente Mandanten und optional Auftragsverarbeitern zuordnen
- Rechtekonzept für Muster, tenantbezogene Dokumente und Admin-Sicht

## Fachliche Zielperspektive

Langfristig soll PROSSESSOR dokumenten- und regelbasiert KI-gestützte Vorschläge für:

- Auditfragen
- Maßnahmen
- Prüfhinweise
- Strukturverbesserungen

erstellen können.

Dabei sollen u. a. folgende Quellen nutzbar gemacht werden:

- Musterchecklisten
- vom Nutzer gelieferte Fachartikel
- DIN-/ISO-orientierte Vorgaben
- Mandantendokumente
- AV-Verträge
- Richtlinien
- TOM-Dokumentationen

## Entwicklungsprinzip

Die Entwicklung soll kontrolliert und stabil erfolgen:

- keine unnötigen Architekturwechsel im laufenden Modul
- zuerst Funktionsfähigkeit, dann UI-Vereinheitlichung
- Designentscheidungen erst nach technischer Stabilisierung der Kernmodule
- V1 vor allem stabil, nachvollziehbar und demo-fähig