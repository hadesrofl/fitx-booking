# ADR-002: Repository Pattern für API-Interaktion

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

HTTP-Calls und Response-Parsing waren ursprünglich direkt im Hauptskript verteilt.

## Entscheidung

Alle FITX-API-Interaktionen wurden in `FitXRepository` (in `repositories/fitx_repository.py`) encapsuliert. Jede öffentliche Methode entspricht einem REST-Endpoint (`authenticate`, `find_course_id`, `execute_booking`).

## Begründung

Trennung von Transport-Schicht und Business-Layer vereinfacht Testing, Wartung und potenziellen Exchange gegen eine andere API-Version.

## Konsequenzen

`main.py` kennt keine HTTP-Details mehr; der Repository ist die einzige Schnittstelle zum externen System. Neue Entwickler können sich schnell orientieren: Nur ein Modul kümmert sich um FITX.
