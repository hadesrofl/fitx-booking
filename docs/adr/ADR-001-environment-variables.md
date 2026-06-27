# ADR-001: Environment Variables statt hardkodierter Credentials

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Das Projekt war ursprünglich ein einzelnes Skript mit hardcoded Credentials in Python-Dictionaries direkt im Sourcecode (`AUTH_DATA = {"username": "", "password": ""}`).

## Entscheidung

Alle konfigurierbaren Werte werden über Environment Variables gelesen mittels `os.environ.get()`. Sensitive Daten (Usernam/Password) und Tuning-Parameter (Studio-ID, Kursname) sind vollständig externalisiert.

## Begründung

Secrets gehören nicht in den Sourcecode. Environment Variables folgen dem 12-Factor App Konzept und erlauben konfigurationsfreie Deployments in Containern ohne Code-Änderungen.

## Konsequenzen

Jede Änderung an Parametern (Studio, Kursname) erfordert keinen Code-Change mehr. `.env` Dateien oder Container-Envs werden zum Standardweg für die Konfiguration.
