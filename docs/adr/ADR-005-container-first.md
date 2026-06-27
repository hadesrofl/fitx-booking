# ADR-005: Container-first Deployment

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Das Projekt hatte keine Containerisierung und lief lokal als Python-Script.

## Entscheidung

Primäres Deployment-Target ist Docker mit `docker-compose.yml` und GitHub Actions für GHCR Publish (Multi-Arch: `linux/amd64`, `linux/arm64`).

## Begründung

Konsistente Umgebung, keine lokalen Abhängigkeiten, skalierbare Trigger-Mechanismen (CronJob, Webhook).

## Konsequenzen

- Lokale Python-Laufzeit ist optional
- CI/CD beschränkt sich auf Build-and-Push (keine Tests im CI)
- Die App ist platform-unabhängig deploybar
