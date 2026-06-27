# ADR-008: Kein Logging-Framework

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Python bietet das eingebaute `logging`-Modul für strukturierte Logs mit Levels (DEBUG, INFO, WARNING, ERROR, CRITICAL). Dies wurde nicht verwendet.

## Entscheidung

Alle Ausgaben erfolgen über `print()` mit emoji-basierten Präfixen (`✅`, `❌`, `⚠️`, `🎯`, `🚀`), um den Status jeder Operation visuell zu kennzeichnen. Es wird kein Logging-Framework verwendet.

## Begründung

Das Projekt ist ein kleines, simples Skript, welches lediglich auf die Konsole loggen muss, um es aus dem Docker-Container auslesen zu können. Ein Logging-Framework wäre Overhead und fügt Komplexität hinzu, ohne einen klaren Mehrwert für diesen Anwendungsfall zu bieten. Die emoji-basierten Präfixe machen Logausgaben direkt im Container-Ausgabe lesbar und visuell unterscheidbar (z.B. bei `docker logs`).

## Konsequenzen

- Keine strukturierte Log-Formatierung
- Keine Maschinelle Auswertung von Logs möglich
- Einfache, sofortige Sichtbarkeit der Logausgaben über Docker-Logs oder Cron-Job-Ausgabe
- Emojis sind visuell gut unterscheidbar in `docker logs` und Terminal-Ausgabe
