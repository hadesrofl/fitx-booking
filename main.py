import sys
import time
from datetime import datetime, timedelta

from config import RUN_TEST, STUDIO_ID, COURSE_NAME, AUTH_USERNAME, AUTH_PASSWORD, SCHEDULE_MAP
from models import BOOKABLE_FROM_KEY, DAY_KEY, NAME_KEY, TIME_KEY, WEEKDAY_INDEX, ScheduleEntry
from repositories.fitx_repository import FitXRepository
from tests.connection_test import run_connection_test


def _to_minutes(time_value: str) -> int:
    hours_str, minutes_str = time_value.split(":")
    return int(hours_str) * 60 + int(minutes_str)


def _resolve_target_date(now: datetime, target_day: str) -> datetime:
    target_index = WEEKDAY_INDEX[target_day]
    delta_days = (target_index - now.weekday()) % 7
    return now + timedelta(days=delta_days)


def _schedule_entries_for_today(now: datetime) -> list[ScheduleEntry]:
    now_weekday = now.strftime("%A").lower()

    due: list[ScheduleEntry] = []
    for entry in SCHEDULE_MAP:
        booking_window = entry[BOOKABLE_FROM_KEY]
        if booking_window[DAY_KEY] != now_weekday:
            continue
        due.append(entry)
    return sorted(due, key=lambda item: _to_minutes(item[BOOKABLE_FROM_KEY][TIME_KEY]))


def run_schedule_booking() -> None:
    """Bucht alle Kurse, die für den aktuellen Booking-Tag fällig sind, und beendet danach den Lauf."""
    now = datetime.now()
    today_entries = _schedule_entries_for_today(now)

    separator = "=" * 50
    print(f"\n{separator}")
    print("📅 STARTE SCHEDULE-BUCHUNG")
    print(f"   Aktuelle Zeit: {now.strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"   Einträge für heutigen Booking-Tag: {len(today_entries)}")
    print(separator)

    if not today_entries:
        print("ℹ️ Keine Schedule-Einträge für den aktuellen Booking-Tag.")
        return

    repository = FitXRepository()
    session = repository.authenticate(AUTH_USERNAME, AUTH_PASSWORD)
    if not session:
        return

    for entry in today_entries:
        current_time = datetime.now()
        booking_minutes = _to_minutes(entry[BOOKABLE_FROM_KEY][TIME_KEY])
        current_minutes = current_time.hour * 60 + current_time.minute
        if booking_minutes > current_minutes:
            wait_seconds = (booking_minutes - current_minutes) * 60 - current_time.second
            if wait_seconds > 0:
                print(
                    f"\n⏳ Warte bis {entry[BOOKABLE_FROM_KEY][TIME_KEY]} für '{entry[NAME_KEY]}' "
                    f"({wait_seconds} Sekunden)..."
                )
                time.sleep(wait_seconds)

        target_date = _resolve_target_date(datetime.now(), entry[DAY_KEY])
        target_time = entry[TIME_KEY]
        course_name = entry[NAME_KEY]

        print(f"\n➡️ Verarbeite: '{course_name}'")
        print(f"   Kurs-Tag: {entry[DAY_KEY]} | Kurs-Zeit: {target_time}")
        print(f"   Ziel-Datum: {target_date.strftime('%d.%m.%Y')}")

        course_id = repository.find_course_id(target_date, target_time, STUDIO_ID, course_name)
        if not course_id:
            print(f"⚠️ Überspringe '{course_name}', da keine Kurs-ID gefunden wurde.")
            continue
        repository.execute_booking(course_id)


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

    if SCHEDULE_MAP:
        run_schedule_booking()
    else:
        run_instant_booking()
