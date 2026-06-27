# FitX Course Booking

Automatisiert die Buchung von Kursen beim Fitnessstudiokettenanbieter FITX.

## Schnellstart

### 1. Environment-Variablen konfigurieren

Erstelle eine `.env` Datei im Root-Verzeichnis:

```env
FITX_USERNAME=dein_fitx_username
FITX_PASSWORD=dein_fitx_password
FITX_STUDIO_ID=<deine_studio_id>
FITX_COURSE_NAME=functional x
RUN_TEST=false
```

### 2. Docker-Compose starten

Standard-Ausführung (Sofortbuchung):

```bash
docker compose up fitx-booker
```

Test-Modus (verifiziert die Verbindung zu FITX):

```bash
RUN_TEST=true docker compose up fitx-booker
```

## Environment Variablen

| Variable | Beschreibung | Standardwert |
|----------|-------------|--------------|
| `FITX_USERNAME` | Dein FITX Login-Benutzername | (erforderlich) |
| `FITX_PASSWORD` | Dein FITX Login-Passwort | (erforderlich) |
| `FITX_STUDIO_ID` | ID des gewünschten Studios | (erforderlich) |
| `FITX_COURSE_NAME` | Name des zu buchenden Kurses | `functional x` |
| `RUN_TEST` | Verbindungstest ausführen statt Buchung | `false` |

## Docker-Image bauen und starten

Das Docker-Image wird automatisch beim Starten von `docker compose up` gebaut. Alternativ kannst du es manuell bauen:

```bash
docker build -t fitx-booker .
docker run --env-file .env fitx-booker
```
