from datetime import datetime, timedelta
from functools import reduce


SECONDS_IN_MIN = 60
MINS_IN_HR = 60
SECONDS_IN_HR = SECONDS_IN_MIN * MINS_IN_HR


def deltasum(deltas: list[timedelta]) -> timedelta:
    return reduce(lambda t1, t2: t1 + t2, deltas, timedelta())


def next_midnight() -> datetime:
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight + timedelta(days=1)
