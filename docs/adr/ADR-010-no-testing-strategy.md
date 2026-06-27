# ADR-010: Keine Test-Strategie

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Es existiert nur ein einziger Integrationstest (`tests/connection_test.py`), der Login und Kursliste prüft, aber keine Unit-Tests für die Domain-Logik vorhanden sind.

## Entscheidung

Keine Test-Strategie wird eingeführt. Der bestehende Connection-Test reicht aus, um die API-Konnektivität zu verifizieren.

## Begründung

Wegen der geringen Größe / Komplexität des Skripts ist eine umfassende Test-Strategie Overhead. Die Buchungslogik ist trivial (HTTP POST mit Payload), die Kurs-Suche basiert auf string-Matching und ist nicht komplex genug für Unit-Tests.

## Konsequenzen

- Nur ein einfacher Connection-Test bleibt bestehen
- Domain-Logik wird nicht automatisiert getestet
- Geringere Sicherheit bei zukünftigen Refactorings der Buchungslogik
- Aber: schnellerer Entwicklungszyklus ohne Test-Hygiene-Overhead
