import json
import tempfile
import unittest
from pathlib import Path

from ScheduleLoader import load_schedule_map
from models import BOOKABLE_FROM_KEY, DAY_KEY, NAME_KEY, TIME_KEY


class TestScheduleLoader(unittest.TestCase):
    def test_load_schedule_map_parses_valid_schedule_file(self) -> None:
        schedule_data = [
            {
                NAME_KEY: "functional x",
                DAY_KEY: "thursday",
                TIME_KEY: "08:00",
                BOOKABLE_FROM_KEY: {
                    DAY_KEY: "monday",
                    TIME_KEY: "07:45",
                },
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            schedule_file = Path(temp_dir) / "schedule.json"
            schedule_file.write_text(json.dumps(schedule_data), encoding="utf-8")

            schedule_map = load_schedule_map(str(schedule_file))

        self.assertEqual(1, len(schedule_map))
        self.assertEqual("functional x", schedule_map[0][NAME_KEY])
        self.assertEqual("thursday", schedule_map[0][DAY_KEY])
        self.assertEqual("08:00", schedule_map[0][TIME_KEY])
        self.assertEqual("monday", schedule_map[0][BOOKABLE_FROM_KEY][DAY_KEY])
        self.assertEqual("07:45", schedule_map[0][BOOKABLE_FROM_KEY][TIME_KEY])


if __name__ == "__main__":
    unittest.main()
