# Datenschutz-Tool V1 – Django-Startprojekt

Dieses Paket ist eine erste lauffähige Basis für die lokale Entwicklung unter Windows und Linux.

## Schnellstart

1. Virtuelle Umgebung anlegen
2. Abhängigkeiten installieren
3. `.env.example` nach `.env` kopieren
4. Migrationen ausführen
5. Seed-Daten anlegen
6. Superuser erstellen
7. Server starten

## Beispiel

```bash
python -m venv .venv
source .venv/bin/activate   # Linux
# oder .venv\Scripts\activate unter Windows
pip install -r requirements.txt
cp .env.example .env        # unter Windows per Explorer oder copy
python manage.py makemigrations
python manage.py migrate
python manage.py seed_initial_data
python manage.py createsuperuser
python manage.py runserver
```

Danach im Browser öffnen:

- http://127.0.0.1:8000/

## Enthaltene Basisfunktionen

- Login
- Dashboard
- Fachbereiche
- Verarbeitungsvorgänge
- rechtliche Bewertungen
- Auftragsverarbeiter
- Audits
- Maßnahmen
- Dokumente
- Reports als Platzhalter

## Hinweise

- Die Listen- und Detailseiten sind als Grundgerüst angelegt.
- Formulare und Exporte können als nächster Schritt ergänzt werden.
- SQLite ist für V1 lokal vorgesehen.
