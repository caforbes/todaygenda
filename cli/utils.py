from datetime import timedelta
from math import ceil
import re
import logging

from src.utils import *


PRETTY_DATE_FORMAT = "%a %I:%M %p"


def parse_out_duration(raw_str: str) -> dict:
    split_str = [s.strip() for s in raw_str.split("\t", 1)]
    if len(split_str) == 1:
        # duration not found
        return {"str": split_str[0], "dur": ""}
    else:
        return {"str": split_str[0], "dur": split_str[1]}


def duration_from_str(dur_str: str) -> timedelta:
    # grab user input for hours/minutes
    hour_match = re.search(r"([\d\.]+)\s?hr?", dur_str, flags=re.IGNORECASE)
    min_match = re.search(r"([\d\.]+)\s?mi?n?", dur_str, flags=re.IGNORECASE)

    hour_str = hour_match[1] if hour_match else "0"
    min_str = min_match[1] if min_match else "0"

    # convert to duration
    delta = timedelta()
    try:
        delta = timedelta(hours=float(hour_str), minutes=float(min_str))
    except ValueError as e:
        logging.warning(f"Invalid duration string converted to 0: {e}")

    # round up to nearest whole minute
    if delta:
        seconds = ceil(delta.total_seconds())  # round up
        next_whole_minute = ceil(seconds / SECONDS_IN_MIN)
        delta = timedelta(minutes=next_whole_minute)

    return delta


def duration_to_str(delta: timedelta) -> str:
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