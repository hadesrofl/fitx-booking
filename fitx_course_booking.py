import os
import sys
import requests
import base64
import time
from datetime import datetime, timedelta
from typing import Optional

# ==========================================
# --- KONFIGURATION (Environment Variables) ---
# ==========================================

# Schalter für den Verbindungstest ("true" / "false")
RUN_TEST = os.environ.get("RUN_TEST", "false").lower() == "true"

AUTH_DATA = {
    "username": os.environ.get("FITX_USERNAME", ""),
    "password": os.environ.get("FITX_PASSWORD", "")
}

STUDIO_ID = os.environ.get("FITX_STUDIO_ID", "1293643060") 
COURSE_NAME = os.environ.get("FITX_COURSE_NAME", "functional x")

# 3. API Endpoints
LOGIN_URL = "https://mein.fitx.de/login"
BOOKING_URL = "https://mein.fitx.de/nox/v1/calendar/bookcourse"
COURSE_LIST_URL_TEMPLATE = "https://mein.fitx.de/nox/v2/bookableitems/courses/with-canceled?startDate={date_str}&endDate={date_str}&organizationUnitIds={studio_id}"

# ==========================================
# --- CORE-FUNKTIONEN ---
# ==========================================

def get_authenticated_session() -> Optional[requests.Session]:
    """Loggt sich mit Basic Auth + JSON Payload ein."""
    if not AUTH_DATA["username"] or not AUTH_DATA["password"]:
        print("❌ Fehler: FITX_USERNAME oder FITX_PASSWORD ist nicht gesetzt!")
        return None

    session = requests.Session()
    user_pass = f"{AUTH_DATA['username']}:{AUTH_DATA['password']}"
    encoded_u_p = base64.b64encode(user_pass.encode()).decode()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_u_p}",
        "x-tenant": "fitx",
        "x-nox-client-type": "WEB",
        "x-public-facility-group": "FITXDE-7B7DAC63E1744DE797245D6E314CD8F6",
        "Origin": "https://mein.fitx.de",
        "Referer": "https://mein.fitx.de/login"
    })

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sende Login-Request...")
    try:
        response = session.post(LOGIN_URL, json=AUTH_DATA, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
                print("✅ Login erfolgreich! Bearer-Token erhalten.")
                return session
        print(f"❌ Login fehlgeschlagen. Status: {response.status_code}\nAntwort: {response.text}")
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
        
        if not isinstance(courses, list):
            print("❌ Fehler: Kursplan-Antwort hat kein Listenformat.")
            return None
        
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
# --- DYNAMISCHE BUCHUNGS-LOGIK ---
# ==========================================

def run_instant_booking():
    """Ermittelt das Ziel-Datum (heute + 3 Tage) und bucht sofort ohne Wartezeit."""
    now = datetime.now()
    
    # FitX schaltet Kurse exakt 3 Tage (72 Stunden) vorher frei.
    # Daher wird der Kurs für in 3 Tagen gesucht.
    target_date = now + timedelta(days=3)
    target_time = now.strftime("%H:%M") 
    
    print(f"\n{'='*50}")
    print(f"🚀 STARTE SOFORT-BUCHUNG")
    print(f"   Aktuelle Zeit: {now.strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"   Suche Kurs am: {target_date.strftime('%d.%m.%Y')} um {target_time} Uhr")
    print(f"{'='*50}")
    
    session = get_authenticated_session()
    if not session:
        return

    course_id = find_course_id(session, target_date, target_time)
    if not course_id:
        print("❌ Abbruch: Kurs-ID nicht gefunden.")
        return
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
    
    test_date = datetime.now()
    date_str = test_date.strftime("%Y-%m-%d")
    print(f"\nSchritt 2: Teste Kursabfrage für heute ({date_str})...")
    
    url = COURSE_LIST_URL_TEMPLATE.format(date_str=date_str, studio_id=STUDIO_ID)
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        courses = response.json()
        
        print(f"✅ Kursplan erfolgreich geladen! Gefundene Kurse heute: {len(courses)}")
        print("Stichprobe der ersten 3 Kurse heute:")
        for course in courses[:3]:
            name = course.get("name", "Unbekannt")
            slots = course.get("slots", [])
            start_time = slots[0].get("startDateTime", "Unbekannte Zeit")[11:16] if slots else "??:??"
            print(f"   - {start_time} Uhr: {name}")
            
        print("\n🎉 VERBINDUNGSTEST ERFOLGREICH BESTANDEN!")
    except requests.exceptions.RequestException as e:
         print(f"\n❌ VERBINDUNGSTEST FEHLGESCHLAGEN: Kursplan konnte nicht geladen werden.\nFehler: {e}")

# ==========================================
# --- HAUPTPROGRAMM ---
# ==========================================

if __name__ == "__main__":
    if RUN_TEST:
        run_connection_test()
        sys.exit(0)
        
    run_instant_booking()
