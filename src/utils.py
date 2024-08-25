from datetime import date, datetime, timedelta
from functools import reduce


SECONDS_IN_MIN = 60
MINS_IN_HR = 60
SECONDS_IN_HR = SECONDS_IN_MIN * MINS_IN_HR


def deltasum(deltas: list[timedelta]) -> timedelta:
    return reduce(lambda t1, t2: t1 + t2, deltas, timedelta())


def next_midnight() -> datetime:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    return datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
