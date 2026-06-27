import sys

from config import RUN_TEST, STUDIO_ID, COURSE_NAME, AUTH_USERNAME, AUTH_PASSWORD
from repositories.fitx_repository import FitXRepository
from tests.connection_test import run_connection_test
from datetime import datetime, timedelta


def run_instant_booking() -> None:
    """Ermittelt das Ziel-Datum (heute + 3 Tage) und bucht sofort ohne Wartezeit."""
    now = datetime.now()

    target_date = now + timedelta(days=3)
    target_time = now.strftime("%H:%M")

    separator = "=" * 50
    print(f"\n{separator}")
    print("🚀 STARTE SOFORT-BUCHUNG")
    print(f"   Aktuelle Zeit: {now.strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"   Suche Kurs am: {target_date.strftime('%d.%m.%Y')} um {target_time} Uhr")
    print(separator)

    repository = FitXRepository()
    session = repository.authenticate(AUTH_USERNAME, AUTH_PASSWORD)
    if not session:
        return

    course_id = repository.find_course_id(target_date, target_time, STUDIO_ID, COURSE_NAME)
    if not course_id:
        print("❌ Abbruch: Kurs-ID nicht gefunden.")
        return
    repository.execute_booking(course_id)


if __name__ == "__main__":
    if RUN_TEST:
        run_connection_test()
        sys.exit(0)

    run_instant_booking()
