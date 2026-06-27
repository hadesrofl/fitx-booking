import requests
import schedule
import time
import base64
from datetime import datetime, timedelta
from typing import Optional

# ==========================================
# --- KONFIGURATION ---
# ==========================================

# 1. Deine Zugangsdaten (Bitte im Produktivbetrieb sicher speichern!)
AUTH_DATA = {
    "username": "",
    "password": ""
}

# 2. Studio- und Kursinformationen
STUDIO_ID = "1293643060" # FitX Lübeck-St. Lorenz Nord
COURSE_NAME = "functional x"

# 3. API Endpoints
LOGIN_URL = "https://mein.fitx.de/login"
BOOKING_URL = "https://mein.fitx.de/nox/v1/calendar/bookcourse"
COURSE_LIST_URL_TEMPLATE = "https://mein.fitx.de/nox/v2/bookableitems/courses/with-canceled?startDate={date_str}&endDate={date_str}&organizationUnitIds={studio_id}"

# ==========================================
# --- KLASSEN & FUNKTIONEN ---
# ==========================================

import base64

def get_authenticated_session() -> Optional[requests.Session]:
    """Loggt sich mit Basic Auth + JSON Payload ein."""
    session = requests.Session()
    
    # Wir generieren den Basic Auth Header aus deinen Zugangsdaten
    # Format: Base64(username:password)
    user_pass = f"{AUTH_DATA['username']}:{AUTH_DATA['password']}"
    encoded_u_p = base64.b64encode(user_pass.encode()).decode()

    # Wir übernehmen die exakten Header aus deinem Browser-Check
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_u_p}", # <--- DAS war das fehlende Teil!
        "x-tenant": "fitx",
        "x-nox-client-type": "WEB",
        "x-public-facility-group": "FITXDE-7B7DAC63E1744DE797245D6E314CD8F6",
        "Origin": "https://mein.fitx.de",
        "Referer": "https://mein.fitx.de/login"
    })

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sende Login-Request (Hybrid-Auth)...")
    try:
        # Wir senden die Daten exakt so, wie dein Browser es im cURL gemacht hat
        response = session.post(LOGIN_URL, json=AUTH_DATA, timeout=10)
        
        # FitX antwortet bei Erfolg mit 200 OK
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if token:
                # WICHTIG: Nach dem Login wird der Basic-Header durch den Bearer-Token ersetzt
                session.headers.update({"Authorization": f"Bearer {token}"})
                print("✅ Login erfolgreich! Bearer-Token erhalten.")
                return session
        
        print(f"❌ Login fehlgeschlagen. Status: {response.status_code}")
        print(f"   Antwort: {response.text}")
            
    except Exception as e:
        print(f"❌ Unerwarteter Fehler beim Login: {e}")
    
    return None

def find_course_id(session: requests.Session, target_date: datetime, target_time: str) -> Optional[int]:
    """Sucht die Kurs-ID im Kursplan des jeweiligen Tages."""
    date_str = target_date.strftime("%Y-%m-%d")
    url = COURSE_LIST_URL_TEMPLATE.format(date_str=date_str, studio_id=STUDIO_ID)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Lade Kursplan für {date_str}...")
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        courses = response.json()
        
        for course in courses:
            if course.get("name", "").lower() == COURSE_NAME.lower():
                slots = course.get("slots", [])
                if slots and f"T{target_time}" in slots[0].get("startDateTime", ""):
                    course_id = course.get("id")
                    print(f"🎯 Kurs '{COURSE_NAME}' gefunden! ID: {course_id}")
                    return course_id
                    
    except requests.exceptions.RequestException as e:
         print(f"❌ Netzwerkfehler beim Laden des Kursplans: {e}")
    except ValueError:
         print("❌ Fehler beim Parsen des Kursplans (ungültiges JSON).")

    print(f"⚠️ Kurs '{COURSE_NAME}' um {target_time} am {date_str} nicht gefunden.")
    return None

def execute_booking(session: requests.Session, course_id: int) -> bool:
    """Führt den POST-Request zur Buchung aus (mit Retry-Logik)."""
    payload = {
        "courseAppointmentId": course_id,
        "expectedCustomerStatus": "BOOKED"
    }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starte Buchungs-Request für ID {course_id}...")
    
    for attempt in range(1, 6):
        try:
            response = session.post(BOOKING_URL, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                print(f"🎉 ERFOLG! Kurs wurde gebucht (Versuch {attempt}).")
                return True
            elif response.status_code == 409:
                 print("❌ Buchung abgelehnt (Vermutlich schon voll oder bereits gebucht).")
                 return False
            else:
                print(f"⚠️ Versuch {attempt} fehlgeschlagen (Status {response.status_code})")
                time.sleep(0.3)
                
        except requests.exceptions.RequestException as e:
             print(f"⚠️ Netzwerkfehler bei Versuch {attempt}: {e}")
             time.sleep(0.3)
             
    print("❌ Alle Buchungsversuche fehlgeschlagen.")
    return False

# ==========================================
# --- JOB-LOGIK ---
# ==========================================

def job_prepare_and_book(target_time: str, target_day_name: str, days_ahead: int):
    """
    Kombinierter Job: Meldet sich an, sucht die ID und wartet auf die 
    Ziel-Stunde (z.B. 18:00:00 oder 16:00:00).
    """
    print(f"\n{'='*50}")
    print(f"🚀 BEREITE BUCHUNG VOR: {target_day_name} {target_time} Uhr")
    print(f"{'='*50}")
    
    session = get_authenticated_session()
    if not session:
        return

    # Ziel-Datum für den Kurs berechnen
    target_date = datetime.now() + timedelta(days=days_ahead)
    
    # 1. Kurs-ID suchen
    course_id = find_course_id(session, target_date, target_time)
    
    if not course_id:
        print("❌ Abbruch: Kurs-ID nicht gefunden.")
        return

    # --- VERBESSERTE WARTE-LOGIK ---
    # Wir extrahieren die Ziel-Stunde (z.B. 16 oder 18) aus target_time
    target_hour = int(target_time.split(":")[0])
    
    print(f"⏳ Warte auf den Moment der Freischaltung um exakt {target_hour}:00:00 Uhr...")
    
    while True:
        now = datetime.now()
        
        # Wir brechen erst ab, wenn die aktuelle Stunde der Zielstunde entspricht 
        # UND die Minute 0 erreicht ist UND die Sekunde 0 erreicht ist.
        if now.hour == target_hour and now.minute == 0 and now.second == 0:
            break
            
        # Kleiner Sicherheits-Check: Falls wir aus irgendeinem Grund 
        # schon NACH der Zielzeit sind (z.B. 16:00:01), auch abbrechen.
        if now.hour == target_hour and (now.minute > 0 or now.second > 0):
            break
            
        time.sleep(0.05) # Sehr kurze Intervalle (50ms) für maximale Präzision

    # 3. Buchung ausführen
    execute_booking(session, course_id)

# ==========================================
# --- TEST-METHODE ---
# ==========================================

def run_connection_test():
    """Führt einen sofortigen Test für Login und Kursabfrage durch."""
    print("\n" + "="*50)
    print("🛠️ STARTE VERBINDUNGSTEST")
    print("="*50)
    
    print("Schritt 1: Teste Login...")
    session = get_authenticated_session()
    
    if not session:
        print("\n❌ VERBINDUNGSTEST FEHLGESCHLAGEN: Login nicht möglich.")
        print("Bitte überprüfe deine E-Mail und dein Passwort in der Konfiguration.")
        return

    print("\n✅ Login erfolgreich. Session-Token ist aktiv.")
    
    # Wir testen die Abfrage für HEUTE, um zu sehen, ob die Kurs-API antwortet.
    test_date = datetime.now()
    date_str = test_date.strftime("%Y-%m-%d")
    print(f"\nSchritt 2: Teste Kursabfrage für heute ({date_str})...")
    
    url = COURSE_LIST_URL_TEMPLATE.format(date_str=date_str, studio_id=STUDIO_ID)
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        courses = response.json()
        
        print(f"✅ Kursplan erfolgreich geladen! Gefundene Kurse heute: {len(courses)}")
        
        # Zeige zur Kontrolle die ersten 3 Kurse von heute an
        print("   Stichprobe der ersten 3 Kurse heute:")
        for i, course in enumerate(courses[:3]):
            name = course.get("name", "Unbekannt")
            slots = course.get("slots", [])
            start_time = slots[0].get("startDateTime", "Unbekannte Zeit")[11:16] if slots else "??:??"
            print(f"   - {start_time} Uhr: {name}")
            
        print("\n🎉 VERBINDUNGSTEST ERFOLGREICH BESTANDEN!")
        print("Du kannst den Bot nun im Scheduler-Modus laufen lassen.")
        
    except requests.exceptions.RequestException as e:
         print(f"\n❌ VERBINDUNGSTEST FEHLGESCHLAGEN: Kursplan konnte nicht geladen werden.")
         print(f"Fehler: {e}")

# ==========================================
# --- HAUPTPROGRAMM ---
# ==========================================

if __name__ == "__main__":
        print(f"\n🤖 FitX-Bot gestartet am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"📅 Warte auf Vorbereitungs-Termine für '{COURSE_NAME}'...")
        print("   - Jeden Samstag um 17:59 Uhr (Bucht für Dienstag 18:00 Uhr)")
        print("   - Jeden Dienstag um 15:59 Uhr (Bucht für Freitag 16:00 Uhr)\n")
        
        schedule.every().saturday.at("17:59").do(job_prepare_and_book, target_time="18:00:00", target_day_name="Dienstag", days_ahead=3)
        schedule.every().tuesday.at("15:59").do(job_prepare_and_book, target_time="16:00:00", target_day_name="Freitag", days_ahead=3)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1) 
        except KeyboardInterrupt:
            print("\n🛑 Bot manuell beendet.")
    else:
        print("Ungültige Eingabe. Programm beendet.")