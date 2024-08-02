import json
import os
import pytest

import cli


def get_storage_json() -> dict:
    assert "test" in cli.daylist_file
    with open(cli.daylist_file) as f:
        content = json.load(f)
    return content


def clear_storage() -> None:
    assert "test" in cli.daylist_file
    if os.path.exists(cli.daylist_file):
        os.remove(cli.daylist_file)


# Add


def test_add_without_list():
    clear_storage()
    cli.add("task added to non-list", 15)

    result = get_storage_json()

    assert "tasks" in result
    assert len(result["tasks"]) == 1
    clear_storage()


def test_add_with_list():
    cli.build_from_storage()
    cli.add("task 1", 11)
    cli.add("task 2", 22)

    result = get_storage_json()

    assert "tasks" in result
    assert len(result["tasks"]) == 2
    clear_storage()


@pytest.mark.parametrize("bad_name", ["", "a" * 250])
def test_add_invalid_name(bad_name):
    cli.build_from_storage()

    with pytest.raises(ValueError):
        cli.add(bad_name, 100)

    clear_storage()


@pytest.mark.parametrize("bad_minutes", [-1, 0, 100000])
def test_add_invalid_minutes(bad_minutes):
    cli.build_from_storage()

    with pytest.raises(ValueError):
        cli.add("task is okay", bad_minutes)

    clear_storage()
