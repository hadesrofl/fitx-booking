# ADR-006: Minimal Dependencies

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Python-Projekte neigen dazu, Frameworks und viele Third-Party-Libraries einzubinden.

## Entscheidung

Nur zwei Dependencies: `requests` (ohne Version-Pinning in requirements.txt), Standard Library (`base64`, `datetime`, `os`, `sys`). Kein FastAPI, kein Flask, kein asyncio, kein typing-overhead.

## Begründung

Das Projekt ist ein einfaches HTTP-Client Script — kein Framework nötig. Weniger Third-Party-Code = weniger Angriffsfläche, schnellere Builds, einfachere Wartung.

## Konsequenzen

- Kein async/await trotz potenziell besserer Performance
- Einfachere Installation und Deployment
- Potenzielle Anfälligkeit gegenüber API-Breakages von FITX ohne Type-Safety
