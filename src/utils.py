from datetime import timedelta
import re
import logging


SECONDS_IN_MIN = 60
SECONDS_IN_HR = 60 * 60


def parse_out_duration(raw_str: str) -> dict:
    split_str = [s.strip() for s in raw_str.split("\t", 1)]
    if len(split_str) == 1:
        # duration not found
        return {"str": split_str[0], "dur": ""}
    else:
        return {"str": split_str[0], "dur": split_str[1]}


def duration_str_to_secs(dur_str: str) -> int:
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
        seconds = int(delta.total_seconds())

        is_partial_second = delta.total_seconds() != seconds
        is_partial_minute = bool(seconds % SECONDS_IN_MIN)

        if is_partial_second or is_partial_minute:
            next_whole_minute = seconds // SECONDS_IN_MIN + 1
            delta = timedelta(minutes=next_whole_minute)

    return int(delta.total_seconds())


def duration_secs_to_str(seconds: int) -> str:
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


def total_delta(all_durations: list[int]) -> timedelta:
    total_seconds = sum(all_durations)
    return timedelta(seconds=total_seconds)
