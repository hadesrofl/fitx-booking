from typing import TypedDict

from .bookable_from import BookableFrom


class ScheduleEntry(TypedDict):
    name: str
    day: str
    time: str
    bookable_from: BookableFrom
