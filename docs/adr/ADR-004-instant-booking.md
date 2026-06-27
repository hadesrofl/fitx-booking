# ADR-004: Instant Booking statt Cron-Scheduler

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Das ursprüngliche Skript nutzte die `schedule` Library mit zwei täglichen Jobs (`Saturday 17:59`, `Tuesday 15:59`). Die Kursfreigabe wurde in Millisekunden nach dem Release-Zeitpunkt ausgelöst — das Script startete once und wartete im Prozess.

## Entscheidung

Scheduler-Logik wurde vollständig entfernt. Das aktuelle Skript berechnet `today + 3 days` und bucht sofort, wenn ein passender Kurs gefunden wird. Der Scheduler liegt nun bei externen Trigger-Mechanismen (Docker-Cron, Kubernetes CronJob).

## Begründung

- Container/One-shot-Execution passt nicht zu einem In-Prozess-Scheduler
- Die "Warten bis exakt Release-Zeit"-Strategie war fragil (Netzwerk-Timing, Prozess-Suspension)
- Instant Booking ist einfacher und zuverlässiger für Docker/Cron-Job Deployment

## Konsequenzen

- Der `schedule` Dependency wurde entfernt. Das Script muss nicht mehr als langlaufender Prozess laufen.
- Externe Trigger übernehmen das Timing — das Projekt wird zum reinen "Booker", der sofort reagiert, sobald er gestartet wird.
