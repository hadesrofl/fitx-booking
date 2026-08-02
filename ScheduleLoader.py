import json
import re
import sys
from pathlib import Path

from models import BOOKABLE_FROM_KEY, DAY_KEY, NAME_KEY, TIME_KEY, WEEKDAY_INDEX, ScheduleEntry

_VALID_WEEKDAYS = set(WEEKDAY_INDEX.keys())

_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _normalize_weekday(value: str, field_name: str) -> str:
    normalized = value.strip().lower()
    if normalized not in _VALID_WEEKDAYS:
        print(
            f"❌ Fehler: Ungültiger Wochentag für '{field_name}': '{value}'. "
            "Erlaubt: monday, tuesday, wednesday, thursday, friday, saturday, sunday"
        )
        sys.exit(1)
    return normalized


def _validate_time(value: str, field_name: str) -> str:
    normalized = value.strip()
    if _TIME_PATTERN.fullmatch(normalized) is None:
        print(f"❌ Fehler: Ungültiges Zeitformat für '{field_name}': '{value}' (erwartet HH:MM)")
        sys.exit(1)
    return normalized


def _validate_schedule_item(raw_item: object, index: int) -> ScheduleEntry:
    if not isinstance(raw_item, dict):
        print(f"❌ Fehler: schedule[{index}] muss ein Objekt sein.")
        sys.exit(1)

    name = raw_item.get(NAME_KEY)
    day = raw_item.get(DAY_KEY)
    time_value = raw_item.get(TIME_KEY)
    bookable_from = raw_item.get(BOOKABLE_FROM_KEY)

    if not isinstance(name, str) or not name.strip():
        print(f"❌ Fehler: schedule[{index}].{NAME_KEY} muss ein nicht-leerer String sein.")
        sys.exit(1)
    if not isinstance(day, str):
        print(f"❌ Fehler: schedule[{index}].{DAY_KEY} muss ein String sein.")
        sys.exit(1)
    if not isinstance(time_value, str):
        print(f"❌ Fehler: schedule[{index}].{TIME_KEY} muss ein String im Format HH:MM sein.")
        sys.exit(1)
    if not isinstance(bookable_from, dict):
        print(f"❌ Fehler: schedule[{index}].{BOOKABLE_FROM_KEY} muss ein Objekt sein.")
        sys.exit(1)

    bookable_day = bookable_from.get(DAY_KEY)
    bookable_time = bookable_from.get(TIME_KEY)

    if not isinstance(bookable_day, str):
        print(f"❌ Fehler: schedule[{index}].{BOOKABLE_FROM_KEY}.{DAY_KEY} muss ein String sein.")
        sys.exit(1)
    if not isinstance(bookable_time, str):
        print(f"❌ Fehler: schedule[{index}].{BOOKABLE_FROM_KEY}.{TIME_KEY} muss ein String im Format HH:MM sein.")
        sys.exit(1)

    return {
        NAME_KEY: name.strip(),
        DAY_KEY: _normalize_weekday(day, f"schedule[{index}].{DAY_KEY}"),
        TIME_KEY: _validate_time(time_value, f"schedule[{index}].{TIME_KEY}"),
        BOOKABLE_FROM_KEY: {
            DAY_KEY: _normalize_weekday(bookable_day, f"schedule[{index}].{BOOKABLE_FROM_KEY}.{DAY_KEY}"),
            TIME_KEY: _validate_time(bookable_time, f"schedule[{index}].{BOOKABLE_FROM_KEY}.{TIME_KEY}"),
        },
    }


def load_schedule_map(schedule_file: str) -> list[ScheduleEntry]:
    if not schedule_file:
        return []

    schedule_path = Path(schedule_file).expanduser()
    if not schedule_path.is_file():
        print(f"❌ Fehler: FITX_SCHEDULE_FILE wurde nicht gefunden: {schedule_path}")
        sys.exit(1)

    try:
        content = schedule_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"❌ Fehler: FITX_SCHEDULE_FILE konnte nicht gelesen werden: {exc}")
        sys.exit(1)

    try:
        raw_schedule = json.loads(content)
    except json.JSONDecodeError as exc:
        print(f"❌ Fehler: FITX_SCHEDULE_FILE enthält ungültiges JSON: {exc}")
        sys.exit(1)

    if not isinstance(raw_schedule, list):
        print("❌ Fehler: FITX_SCHEDULE_FILE muss ein JSON-Array enthalten.")
        sys.exit(1)

    validated_schedule: list[ScheduleEntry] = []
    for index, item in enumerate(raw_schedule):
        validated_schedule.append(_validate_schedule_item(item, index))

    return validated_schedule
