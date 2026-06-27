# ADR-007: Linearer Retry ohne Exponential Backoff

**Datum:** 27.06.2026  
**Status:** angenommen  

## Kontext

Beim konkurrierenden Kursbuchungs-Szenario müssen Buchungsversuche ggf. mehrmals wiederholt werden.

## Entscheidung

Linearer Retry (5 Versuche, 300ms delay zwischen jedem Versuch), kein exponentielles Backoff. HTTP-Statuscode 409 (schon voll) führt zum sofortigen Abbruch ohne weitere Versuche.

## Begründung

Kursfreigabe ist ein einmaliger Moment — keine Notwendigkeit für komplexe Backoff-Strategien. Das One-shot Script hat kein Problem mit kurzen Ineffizienzen bei längeren Ausfällen.

## Konsequenzen

- Bei kurzzeitigen Netzwerkproblemen robust
- Bei langen Ausnahmen ineffizient (aber unkritisch wegen der Oneshot-Natur)
- Einfachere Debugging-Möglichkeit durch gleichmäßige Timing-Logik
