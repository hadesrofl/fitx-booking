import requests
import base64
import time
from datetime import datetime
from typing import Optional


class FitXRepository:
    LOGIN_URL = "https://mein.fitx.de/login"
    BOOKING_URL = "https://mein.fitx.de/nox/v1/calendar/bookcourse"
    COURSE_LIST_URL_TEMPLATE = (
        "https://mein.fitx.de/nox/v2/bookableitems/courses/with-canceled"
        "?startDate={date_str}&endDate={date_str}"
        "&organizationUnitIds={studio_id}"
    )

    def __init__(self) -> None:
        self.session = requests.Session()
        self._setup_default_headers()

    def _setup_default_headers(self) -> None:
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/147.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "x-tenant": "fitx",
            "x-nox-client-type": "WEB",
            "x-public-facility-group": "FITXDE-7B7DAC63E1744DE797245D6E314CD8F6",
            "Origin": "https://mein.fitx.de",
            "Referer": "https://mein.fitx.de/login",
        })

    def authenticate(
        self, username: str, password: str
    ) -> Optional[requests.Session]:
        """Loggt sich mit Basic Auth + JSON Payload ein.
        
        Hinweis: Authentifizierung wird bereits in config.py validiert
        (FITX_USERNAME/FITX_PASSWORD müssen als Environment-Variablen gesetzt sein).
        Diese Prüfung dient nur als defensive Layer für direkte Aufrufe von außen.
        """
        if not username or not password:
            print("❌ Fehler: FITX_USERNAME oder FITX_PASSWORD ist nicht gesetzt!")
            return None

        user_pass = f"{username}:{password}"
        encoded = base64.b64encode(user_pass.encode()).decode()
        self.session.headers["Authorization"] = f"Basic {encoded}"

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sende Login-Request...")
        try:
            response = self.session.post(self.LOGIN_URL, json={"username": username, "password": password}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.session.headers["Authorization"] = f"Bearer {token}"
                    print("✅ Login erfolgreich! Bearer-Token erhalten.")
                    return self.session
            print(f"❌ Login fehlgeschlagen. Status: {response.status_code}\nAntwort: {response.text}")
        except Exception as e:
            print(f"❌ Unerwarteter Fehler beim Login: {e}")
        return None

    def find_course_id(
        self,
        target_date: datetime,
        target_time: str,
        studio_id: str,
        course_name: str = "functional x",
    ) -> Optional[int]:
        """Sucht die Kurs-ID im Kursplan des jeweiligen Tages."""
        date_str = target_date.strftime("%Y-%m-%d")
        url = self.COURSE_LIST_URL_TEMPLATE.format(date_str=date_str, studio_id=studio_id)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Lade Kursplan für {date_str}...")
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            courses = response.json()

            if not isinstance(courses, list):
                print("❌ Fehler: Kursplan-Antwort hat kein Listenformat.")
                return None

            for course in courses:
                if course.get("name", "").lower() == course_name.lower():
                    slots = course.get("slots", [])
                    if slots and f"T{target_time}" in slots[0].get("startDateTime", ""):
                        course_id = course.get("id")
                        print(f"🎯 Kurs '{course_name}' gefunden! ID: {course_id}")
                        return course_id

        except requests.exceptions.RequestException as e:
            print(f"❌ Netzwerkfehler beim Laden des Kursplans: {e}")
        except ValueError:
            print("❌ Fehler beim Parsen des Kursplans (ungültiges JSON).")

        print(f"⚠️ Kurs '{course_name}' um {target_time} am {date_str} nicht gefunden.")
        return None

    def execute_booking(self, course_id: int) -> bool:
        """Führt den POST-Request zur Buchung aus (mit Retry-Logik)."""
        payload = {
            "courseAppointmentId": course_id,
            "expectedCustomerStatus": "BOOKED",
        }

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starte Buchungs-Request für ID {course_id}...")
        for attempt in range(1, 12):
            try:
                response = self.session.post(self.BOOKING_URL, json=payload, timeout=5)

                if response.status_code in (200, 201):
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
