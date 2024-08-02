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


# Show


def test_show_typical_userflow(capsys):
    cli.build_from_storage()

    cli.add("test task", 55)
    cli.show()

    captured = capsys.readouterr()
    assert "estimate" in captured.out.lower()

    storage = get_storage_json()
    assert os.path.exists(cli.daylist_file)
    assert len(storage["tasks"]) == 1
    clear_storage()


def test_show_builds_list(capsys):
    clear_storage()

    cli.show()

    captured = capsys.readouterr()
    assert "new list" in captured.out.lower()

    assert os.path.exists(cli.daylist_file)
    clear_storage()


# Add


def test_add_without_list():
    clear_storage()
    cli.add("task added to non-list", 15)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 1
    clear_storage()


def test_add():
    # typical flow
    cli.build_from_storage()
    cli.add("task 1", 11)
    cli.add("task 2", 22)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 2

    # check bad userinput
    bad_names = ["", "a" * 250]
    for bad_name in bad_names:
        with pytest.raises(ValueError):
            cli.add(bad_name, 100)

    bad_minutes = [-1, 0, 100000]

    for bad_minutes in bad_minutes:
        with pytest.raises(ValueError):
            cli.add("task is okay", bad_minutes)

    clear_storage()


# Delete


def test_delete_without_list():
    clear_storage()

    with pytest.raises(ValueError):
        cli.delete(1)

    clear_storage()


def test_delete():
    cli.build_from_storage()

    # typical flow
    cli.build_from_storage()
    cli.add("task 1", 11)
    cli.add("task 2", 22)
    cli.delete(2)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 1

    # bad userinput
    bad_numbers = [0, -1]
    for bad_num in bad_numbers:
        with pytest.raises(ValueError):
            cli.delete(bad_num)

    clear_storage()
