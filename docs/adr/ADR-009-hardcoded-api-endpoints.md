# ADR-009: FITX API Endpoints als hardkodierter Code

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Alle FITX REST-API URLs (`LOGIN_URL`, `BOOKING_URL`, `COURSE_LIST_URL_TEMPLATE`) sind als Klassenkonstanten in `FitXRepository` fest im Code definiert. Im Gegensatz zu Studio-ID und Kursname sind diese nicht über Environment Variables konfigurierbar.

## Entscheidung

Die API-URLs bleiben hardcoded im Sourcecode, nicht externalisiert. Nur STUDIO_ID und COURSE_NAME werden über Environment-Variablen gesteuert.

## Begründung

Eine Veränderung der FITX-API-Endpoints durch FitX bedeutet typischerweise gleichzeitig eine API-Version oder ein breaking Change. Daher wäre eine Code-Änderung eh notwendig. Eine Konfiguration über Environment Variables würde keinen Mehrwert bieten, da die Endpoint-Härtung ohnehin keine Flexibilität für den Betrieb bringt — sondern nur ein falsches Gefühl der Konfigurierbarkeit erzeugt.

## Konsequenzen

- Bei API-Breakages durch FITX muss die Sourcecode geändert werden
- Keine Runtime-Konfiguration des APIs-Base-URL möglich (z.B. für Staging-Umgebungen)
- Die Endpoints sind explizit dokumentiert als Klassenkonstanten und damit leicht auffindbar
