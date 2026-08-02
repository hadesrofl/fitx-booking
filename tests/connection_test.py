from config import STUDIO_ID, AUTH_USERNAME, AUTH_PASSWORD
from repositories.fitx_repository import FitXRepository
from datetime import datetime

def run_connection_test() -> None:
    """Führt einen sofortigen Test für Login und Kursabfrage durch."""
    print("\n" + "=" * 50)
    print("🛠️ STARTE VERBINDUNGSTEST")
    print("=" * 50)

    print("Schritt 1: Teste Login...")
    repository = FitXRepository()
    session = repository.authenticate(AUTH_USERNAME, AUTH_PASSWORD)
    if not session:
        print("\n❌ VERBINDUNGSTEST FEHLGESCHLAGEN: Login nicht möglich.")
        print("Bitte überprüfe deine E-Mail und dein Passwort in der Konfiguration.")
        return

    print("\n✅ Login erfolgreich. Session-Token ist aktiv.")

    test_date = datetime.now()
    date_str = test_date.strftime("%Y-%m-%d")
    print(f"\nSchritt 2: Teste Kursabfrage für heute ({date_str})...")

    url = FitXRepository.COURSE_LIST_URL_TEMPLATE.format(date_str=date_str, studio_id=STUDIO_ID)
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
    except Exception as e:
        print(f"\n❌ VERBINDUNGSTEST FEHLGESCHLAGEN: Kursplan konnte nicht geladen werden.\nFehler: {e}")
