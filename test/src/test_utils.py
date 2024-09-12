from datetime import datetime, time, timedelta, timezone
import pytest

import src.utils as utils


def test_next_midnight_default():
    result = utils.next_midnight()
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.tzinfo == timezone.utc


@pytest.mark.parametrize("zone_param", ["utc", timezone.utc])
def test_next_midnight_utc(zone_param):
    result = utils.next_midnight(zone_param)
    assert result.tzinfo == timezone.utc
    assert result.hour == 0
    assert result.minute == 0


@pytest.mark.parametrize("zone_param", ["MST", "America/Phoenix"])
def test_next_midnight_custom(zone_param):
    result = utils.next_midnight(zone_param)
    assert result.isoformat().endswith("00:00:00-07:00")


def test_next_midnight_system():
    result = utils.next_midnight("system")
    assert result.tzinfo is not None


@pytest.mark.parametrize(
    "time_str, hrs, mins, tz_str",
    [
        ("04:04:04+04", 4, 4, "+04:00"),
        ("05:05:05+05", 5, 5, "+05:00"),
        ("06:06:06:123456+06", 6, 6, "+06:00"),
    ],
)
def test_next_timepoint(time_str, hrs, mins, tz_str):
    now = datetime.now(timezone.utc)
    tm = time.fromisoformat(time_str)
    result = utils.next_timepoint(tm)

    assert result > now
    assert result < (now + timedelta(days=1))

    assert result.year == now.year
    assert result.hour == hrs
    assert result.minute == mins
    assert result.second == 0
    assert result.microsecond == 0
    assert result.isoformat().endswith(tz_str)


@pytest.mark.parametrize(
    "list_of_seconds,total_seconds",
    [
        ([], 0),
        ([0, 0, 0], 0),
        ([1], 1),
        ([1, 2, 3], 6),
    ],
)
def test_deltasum(list_of_seconds, total_seconds):
    list_of_deltas = [timedelta(seconds=sec) for sec in list_of_seconds]
    assert utils.deltasum(list_of_deltas) == timedelta(seconds=total_seconds)


@pytest.mark.parametrize(
    "raw,expected_str,expected_dur",
    [
        ("task", "task", ""),
        ("task\t1m", "task", "1m"),
        ("task\t1h1m", "task", "1h1m"),
        (" task  \t 1m ", "task", "1m"),
        ("my task", "my task", ""),
        ("my task\t1m", "my task", "1m"),
        ("my task\t1h1m", "my task", "1h1m"),
        (" my task  \t 1m ", "my task", "1m"),
    ],
)
def test_parse_duration_str(raw, expected_str, expected_dur):
    result = utils.parse_out_duration(raw)
    assert result["str"] == expected_str
    assert result["dur"] == expected_dur


@pytest.mark.parametrize(
    "raw,expected_m",
    [
        ("1m", 1),
        ("1h", 60),
        ("1 h", 60),
        ("1H", 60),
        ("1hr", 60),
        ("1h1m", 61),
        ("1m1h", 61),
        ("1h 1m", 61),
        ("1.5h", 90),
        ("1.1m", 2),
        ("1.5m", 2),
        ("1.5h 30m", 120),
    ],
)
def test_duration_from_str(raw, expected_m):
    result = utils.duration_from_str(raw)
    assert isinstance(result, timedelta)
    assert result == timedelta(minutes=expected_m)


@pytest.mark.parametrize(
    "raw",
    ["0m", "0h", "0h0m", "", "1.5.1.5h", "h"],
)
def test_duration_from_str_none(raw):
    result = utils.duration_from_str(raw)
    assert isinstance(result, timedelta)
    assert result == timedelta()


@pytest.mark.parametrize(
    "seconds,expected_label",
    [
        (0, ""),
        (1, ""),  # we don't expect partial minute values
        (60, "1m"),
        (90, "1m"),  # we don't expect partial minute values
        (1200, "20m"),
        (3600, "1h"),
        (3660, "1h1m"),
        (36000, "10h"),
    ],
)
def test_duration_to_str(seconds, expected_label):
    result = utils.duration_to_str(timedelta(seconds=seconds))
    assert isinstance(result, str)
    assert result == expected_label
