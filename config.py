import os
import sys
from ScheduleLoader import load_schedule_map


RUN_TEST = os.environ.get("RUN_TEST", "false").lower() == "true"

AUTH_USERNAME = os.environ.get("FITX_USERNAME", "").strip()
AUTH_PASSWORD = os.environ.get("FITX_PASSWORD", "").strip()

STUDIO_ID = os.environ.get("FITX_STUDIO_ID", "").strip()

_missing = []
if not AUTH_USERNAME:
    _missing.append("FITX_USERNAME")
if not AUTH_PASSWORD:
    _missing.append("FITX_PASSWORD")
if not STUDIO_ID:
    _missing.append("FITX_STUDIO_ID")

if _missing:
    if len(_missing) == 1:
        print(f"❌ Fehler: {_missing[0]} ist nicht gesetzt!")
    else:
        print(f'❌ Fehler: {" oder ".join(_missing)} sind nicht gesetzt!')
    sys.exit(1)

COURSE_NAME = os.environ.get("FITX_COURSE_NAME", "functional x")
FITX_SCHEDULE_FILE = os.environ.get("FITX_SCHEDULE_FILE", "").strip()
SCHEDULE_MAP = load_schedule_map(FITX_SCHEDULE_FILE)
