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
FITX_SCHEDULE_FILE=./schedule.json
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
| `FITX_SCHEDULE_FILE` | Pfad zu einer JSON-Datei mit Schedule-Einträgen | (optional) |
| `RUN_TEST` | Verbindungstest ausführen statt Buchung | `false` |

## Schedule-JSON (empfohlen)

Wenn `FITX_SCHEDULE_FILE` gesetzt ist, wird die Buchung über diese Datei gesteuert.  
Die Datei muss ein JSON-Array im folgenden Format enthalten:
Für `day` und `bookable_from.day` sind nur englische Tagesnamen erlaubt (`monday` bis `sunday`).

```json
[
  {
    "name": "functional x",
    "day": "thursday",
    "time": "08:00",
    "bookable_from": {
      "day": "monday",
      "time": "07:45"
    }
  }
]
```

Verhalten:
- Es werden pro Lauf alle Einträge verarbeitet, deren `bookable_from.day` dem heutigen Wochentag entspricht.
- Falls ein Eintrag erst später am selben Tag buchbar wird (`bookable_from.time`), wartet das Skript bis zu diesem Zeitpunkt.
- Nach der Verarbeitung aller fälligen Einträge endet das Skript.
- Wenn `FITX_SCHEDULE_FILE` **nicht** gesetzt ist, läuft weiterhin die bisherige Sofortbuchung (`FITX_COURSE_NAME`).

## Docker-Image bauen und starten

Das Docker-Image wird automatisch beim Starten von `docker compose up` gebaut. Alternativ kannst du es manuell bauen:

```bash
docker build -t fitx-booker .
docker run --env-file .env fitx-booker
```

### Docker Run mit Schedule-Datei per Volume

Lege deine `schedule.json` lokal ab (z. B. im Ordner `./config`) und mounte diesen Ordner in den Container.  
Setze `FITX_SCHEDULE_FILE` auf den **Container-Pfad**:

```bash
docker run --rm \
  --env-file .env \
  -e FITX_SCHEDULE_FILE=/data/schedule.json \
  -v "$(pwd)/config:/data:ro" \
  fitx-booker
```
