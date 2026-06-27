# ADR-003: Drei-Modul-Architektur

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Alle Logik befand sich ursprünglich in einer Datei (`fitx_course_booking.py`, 256 Zeilen).

## Entscheidung

Trennung in drei Module:

| Datei | Verantwortung |
|-------|-------------|
| `main.py` (40 Zeilen) | Entry-Point, Orchestrierung, Execution-Flow |
| `config.py` (8 Zeilen) | Environment Variable Loading |
| `repositories/fitx_repository.py` (125 Zeilen) | FITX API Client, Auth, HTTP |

## Begründung

Eine Datei pro Verantwortungsgebiet. `main.py` bleibt mit 40 Zeilen extrem schlank und dient als "Glue Code".

## Konsequenzen

- Keine zentralen Konfig-Objekte mehr, alle Config-Werte auf Modulebene
- Klare Trennung von Orchestrierung, Konfiguration und Domain-Logik
- Neue Entwickler können sich schnell in der Ordnerstruktur orientieren
