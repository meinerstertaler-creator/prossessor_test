# PROSSESSOR – Architektur

## Systemname
Produktname: PROSSESSOR  
Interner Projektname im Code: privacy_tool

---

## Ziel des Systems

PROSSESSOR ist ein mandantenfähiges Datenschutz- und Compliance-System auf Django-Basis.

Zentrale Funktionen:
- Verzeichnis von Verarbeitungstätigkeiten
- juristische Bewertung von Verarbeitungen
- Verwaltung von Auftragsverarbeitern
- Dokumentenverwaltung
- Audits
- Maßnahmenmanagement
- Reporting

---

## Technologiestack

- Django
- SQLite in der Entwicklung
- Bootstrap-basiertes Frontend
- Custom User Model: `accounts.User`

---

## Projektstruktur

- `config` – Projektkonfiguration
- `core` – Dashboard, gemeinsame Utilities, Context Processor
- `accounts` – User, Tenant, Mandantenstruktur
- `processing` – Verarbeitungstätigkeiten
- `legal` – Rechtsbewertung
- `documents` – Dokumente
- `processors` – Auftragsverarbeiter / Dienstleister
- `audits` – Audits / Prüfungen
- `actions` – Maßnahmen
- `reports` – Berichte / Exporte

---

## Routing

- `/` → `core`
- `/accounts/` → Auth
- `/processing/` → Verarbeitung
- `/processors/` → Dienstleister
- `/audits/` → Audits
- `/actions/` → Maßnahmen
- `/documents/` → Dokumente
- `/reports/` → Berichte
- `/legal/` → Rechtsbewertung

---

## Zentrale Architekturidee

Technisch getrennte Apps, fachlich später im Menü gruppierbar.

Beispiel einer späteren Menüstruktur:
- Organisation
- Verarbeitungen
- Dienstleister
- Compliance
- Dokumente
- Berichte

Die App-Grenzen müssen nicht der Menüstruktur entsprechen.

---

## Bisher bekannte Modelle und Beziehungen

### accounts

#### Tenant
Repräsentiert einen Mandanten / ein Unternehmen.

Wichtige Felder:
- name
- description
- is_active
- created_at
- updated_at

#### Role
Rollenmodell für Benutzerrechte.

Beispiele:
- Admin
- Datenschutzbeauftragter
- Sachbearbeiter
- Mandant

#### User
Custom User Model basierend auf Django `AbstractUser`.

Zusätzliche Felder:
- role (FK → Role)
- tenant (FK → Tenant)
- created_at
- updated_at

Beziehungen:

Tenant  
└── User  
  └── Role

### processing
- `Department`
- `ProcessingActivity`
- `ProcessingTemplate`

### legal
- `LegalAssessment`

### Bekannte Beziehung
- `ProcessingActivity` → `OneToOne` → `LegalAssessment`

---

## Mandantenlogik

Die Mandantenlogik wird über `core.tenant_utils` gesteuert.

Zentrale Funktion:

get_effective_tenant(request)

Logik:

1. Nicht eingeloggte Benutzer  
→ kein Mandant

2. Normale Benutzer  
→ immer der dem Benutzer zugewiesene Tenant

3. Superuser  
→ aktiver Mandant aus der Session

Session-Key:
active_tenant_id

Sonderfall:
Wenn kein aktiver Mandant gesetzt ist, kann der Superuser alle Mandanten sehen.

Diese Logik wird in Views verwendet, um Querysets mandantenbezogen zu filtern.

---
### Template-Kontext

Der Context Processor `tenant_switcher` stellt Mandanteninformationen in allen Templates bereit.

Er liefert:

- active_tenant
- all_tenants

Logik:

Nicht eingeloggte Benutzer:
active_tenant = None

Normale Benutzer:
active_tenant = request.user.tenant

Superuser:
active_tenant = aktueller Mandant aus Session
all_tenants = Liste aller aktiven Mandanten

Damit kann im UI ein Mandanten-Switcher für Superuser dargestellt werden.

## KI-Kontextquellen

### Für KI zugelassen
1. Unternehmens-Stammdaten
2. freies KI-Kontextfeld in den Stammdaten
3. lokale Wissensbasis
4. Mustertexte

### Für KI derzeit nicht zugelassen
1. Mandantendokumente
2. individuelle verfahrensbezogene Unterlagen
3. konkrete Akteninhalte

---

## Geplante fachliche Erweiterungen

### Unternehmensprofil
Je Mandant sollen Stammdaten gepflegt werden, z. B.:
- Rechtsform
- Konzernverhältnisse
- Mitarbeiterzahl
- Einsatz von Leiharbeitnehmern
- Einsatz von Freelancern
- interner Meldekanal
- Verwaltung von Patenten / Lizenzen
- individuelles KI-Kontextfeld

### Dokumentenarchitektur
Geplante Unterscheidung:
- Wissensbasis
- Mustertexte
- Mandantendokumente

### Berechtigungslogik
- Admin-only
- tenant-sichtbar
- später ggf. objektbezogene Sichtbarkeit

---

## UI-Grundsätze

Geplant:
- Branding unter dem Namen `PROSSESSOR`
- einheitliche `base.html`
- Anzeige „Logged in as …“
- responsives Layout
- keine horizontal überlaufenden Inhalte

---

## Entwicklungsprinzip

Ab jetzt paketweises Vorgehen:
1. Ziel definieren
2. betroffene Dateien benennen
3. Änderungen gezielt umsetzen
4. testen
5. erst dann nächstes Paket
# Architektur – Fortschreibung

## Stand der Architektur

PROSSESSOR basiert auf einer modularen Django-Architektur mit klar getrennten Fachbereichen.

Aktive Kernmodule:

- accounts
- core
- processing
- legal
- dpia
- actions
- audits
- reports
- documents (im Ausbau)

## Architekturprinzipien

### 1. Mandantenfähigkeit
Die Anwendung ist tenantbezogen aufgebaut. Datenzugriffe werden tenantbezogen gefiltert, Superuser können tenantübergreifend arbeiten.

### 2. Fachmodulorientierung
Die Kernbereiche werden in getrennten Apps entwickelt, um Fachlogik, Templates, Views und Modelle sauber voneinander zu trennen.

### 3. Maßnahmen als zentrales Bindeglied
`ActionItem` fungiert als zentrales Modul für Folgeaufgaben aus verschiedenen Fachbereichen:

- Verfahren
- Rechtsbewertung
- DSFA
- Audit

### 4. Reporting als Querschnitt
Das Reportmodul bündelt strukturierte Ausgaben der Fachmodule. Berichte sollen nicht isoliert, sondern auf Basis der Moduldaten erzeugt werden.

---

## Auditarchitektur – aktueller Stand

### Aktuelle Modelle
Es bestehen derzeit zwei technische Auditmodelle:

#### `Audit`
Historisch für Spezialaudits, insbesondere auftragsverarbeiterbezogene Prüfungen.

#### `ProcedureAudit`
Verfahrensorientiertes Hauptaudit mit mehrstufigem Auditablauf.

### Bewertung
Fachlich gehören beide zu derselben Auditdomäne, sind technisch aber derzeit getrennt modelliert.

Dies wird aktuell bewusst nicht zurückgebaut, um V1 stabil zu halten.

---

## Hauptaudit – aktuelle Struktur

Das verfahrensorientierte Audit (`ProcedureAudit`) besteht aktuell aus:

### Abschnitt 1
Verfahrensprüfung

### Abschnitt 2
Neue Verfahren

### Abschnitt 3
Allgemeine Audit-Checkliste

### Abschluss
- vorläufiger Auditabschluss
- Endabschluss / Jahresaudit beenden
- Bericht / Reporting

---

## Checklistenarchitektur – aktueller Stand

### Aktuell
- `AuditQuestion` dient als Fragenpool
- für Spezialaudits existiert `AuditResponse`
- für Hauptaudits wurde eine eigene Checklistenantwortlogik ergänzt

### Bewertung
Technisch ist dies ein Übergangszustand. Fachlich soll mittelfristig eine einheitliche auditbezogene Checklistenarchitektur entstehen.

### Zielbild V2
- zentraler Fragenpool
- auditbezogene Instanziierung von Checklisten
- keine dauerhafte doppelte Checklistenlogik
- spätere KI-gestützte Vorschläge

---

## Dokumentenarchitektur – geplanter nächster Schritt

Das Dokumentenmodul wird als nächster Schwerpunkt entwickelt.

### Ziel
Mandantenfähige Dokumentenverwaltung mit klarer Rechte- und Ordnerstruktur.

### Geplante Grundlogik
- Ordner
- Dokumente
- Mandantenbezug
- optionaler Auftragsverarbeiterbezug
- Sichtbarkeitslogik nach Dokumentart

### Geplante Rechte
- Muster: global sichtbar
- tenantbezogene Dokumente: nur für den jeweiligen Tenant sichtbar
- AV-Verträge: tenantbezogen und optional AV-bezogen
- Admin: Vollzugriff

---

## KI-/Vorschlagsarchitektur – Zielperspektive

Langfristig soll PROSSESSOR audit- und compliancebezogene Vorschläge aus mehreren Quellen ableiten können.

### Geplante Quellen
- Fragenpool / Musterchecklisten
- Fachartikel
- DIN-/ISO-orientierte Vorgaben
- Mandantendokumente
- AV-Verträge
- TOM-Dokumentationen

### Geplante Ergebnisse
- Auditfragen
- Prüfschwerpunkte
- Maßnahmenvorschläge
- Hinweise auf Dokumentationslücken

Dies ist ausdrücklich ein geplanter Ausbau nach Stabilisierung der Grundfunktionen.