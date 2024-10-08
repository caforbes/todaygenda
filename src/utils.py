import datetime as dt
import time
from zoneinfo import ZoneInfo
from functools import reduce
import logging
import math
import re


# Time helpers


SECONDS_IN_MIN = 60
MINS_IN_HR = 60
SECONDS_IN_HR = SECONDS_IN_MIN * MINS_IN_HR


def deltasum(deltas: list[dt.timedelta]) -> dt.timedelta:
    return reduce(lambda t1, t2: t1 + t2, deltas, dt.timedelta())


def next_midnight(tz: str | dt.tzinfo = dt.timezone.utc) -> dt.datetime:
    """The next midnight time, given a certain timezone (default: UTC).

    Examples (today is Jan 1, 2024)::

        next_midnight() == 'Jan 2, 2024 00:00:00+00:00'
        next_midnight('utc') == 'Jan 2, 2024 00:00:00+00:00'
        next_midnight(datetime.timezone.utc) == 'Jan 2, 2024 00:00:00+00:00'
        next_midnight('MST') == 'Jan 2, 2024 00:00:00+07:00'
        next_midnight('America/Los Angeles') == 'Jan 2, 2024 00:00:00+07:00'
        next_midnight('system') == 'Jan 2, 2024 00:00:00+05:00' (your system time)
    """
    # convert input to a timezone
    if isinstance(tz, str):
        if tz == "utc":
            tz = dt.timezone.utc
        elif tz == "system":
            tz = system_tz()
        else:
            tz = ZoneInfo(tz)

    # get next midnight at that zone
    midnight = dt.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
    return next_timepoint(midnight)


def system_tz() -> dt.tzinfo:
    system_now = time.localtime()
    return ZoneInfo(system_now.tm_zone)


def next_timepoint(input_time: dt.time) -> dt.datetime:
    """Get the nearest future timestamp of a given time -- HH:MM only."""
    now = dt.datetime.now(dt.timezone.utc)
    new_time = now.replace(
        hour=input_time.hour,
        minute=input_time.minute,
        second=0,
        microsecond=0,
        tzinfo=input_time.tzinfo,
    )
    if now < new_time:
        return new_time
    else:
        return new_time + dt.timedelta(days=1)


# String helpers


PRETTY_DATE_FORMAT = "%a %I:%M %p"


def parse_out_duration(raw_str: str) -> dict[str, str]:
    split_str = [s.strip() for s in raw_str.split("\t", 1)]
    if len(split_str) == 1:
        # duration not found
        return {"str": split_str[0], "dur": ""}
    else:
        return {"str": split_str[0], "dur": split_str[1]}


def duration_from_str(dur_str: str) -> dt.timedelta:
    # grab user input for hours/minutes
    hour_match = re.search(r"([\d\.]+)\s?hr?", dur_str, flags=re.IGNORECASE)
    min_match = re.search(r"([\d\.]+)\s?mi?n?", dur_str, flags=re.IGNORECASE)

    hour_str = hour_match[1] if hour_match else "0"
    min_str = min_match[1] if min_match else "0"

    # convert to duration
    delta = dt.timedelta()
    try:
        delta = dt.timedelta(hours=float(hour_str), minutes=float(min_str))
    except ValueError as e:
        logging.warning(f"Invalid duration string converted to 0: {e}")

    # round up to nearest whole minute
    if delta:
        seconds = math.ceil(delta.total_seconds())  # round up
        next_whole_minute = math.ceil(seconds / SECONDS_IN_MIN)
        delta = dt.timedelta(minutes=next_whole_minute)

    return delta


def duration_to_str(delta: dt.timedelta) -> str:
    seconds = round(delta.total_seconds())
    hours, seconds = seconds // SECONDS_IN_HR, seconds % SECONDS_IN_HR
    minutes, seconds = seconds // SECONDS_IN_MIN, seconds % SECONDS_IN_MIN

    # we throw away the seconds
    if hours and minutes:
        return f"{hours}h{minutes}m"
    elif hours:
        return f"{hours}h"
    elif minutes:
        return f"{minutes}m"
    else:
        return ""
