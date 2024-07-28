import pytest

import src.utils as main


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
    result = main.parse_out_duration(raw)
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
        ("1.5m", 2),
        ("1.5h 30m", 120),
    ],
)
def test_duration_str_to_secs(raw, expected_m):
    result = main.duration_str_to_secs(raw)
    assert isinstance(result, int)
    assert result == expected_m * 60


@pytest.mark.parametrize(
    "raw",
    ["0m", "0h", "0h0m", "", "1.5.1.5h", "h"],
)
def test_duration_str_to_secs_none(raw):
    result = main.duration_str_to_secs(raw)
    assert isinstance(result, int)
    assert result == 0


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
def test_duration_secs_to_str(seconds, expected_label):
    result = main.duration_secs_to_str(seconds)
    assert isinstance(result, str)
    assert result == expected_label
