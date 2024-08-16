import json
import os
import pytest

import cli


def get_storage_json() -> dict:
    assert "test" in cli.daylist_file
    with open(cli.daylist_file) as f:
        content = json.load(f)
    return content


@pytest.fixture()
def storage():
    assert "test" in cli.daylist_file
    if os.path.exists(cli.daylist_file):
        os.remove(cli.daylist_file)

    yield

    if os.path.exists(cli.daylist_file):
        os.remove(cli.daylist_file)


# Show


def test_show_typical_userflow(storage, capsys):
    cli.build_from_storage()

    cli.add("test task", 55)
    cli.show()

    captured = capsys.readouterr()
    assert "estimate" in captured.out.lower()

    storage = get_storage_json()
    assert os.path.exists(cli.daylist_file)
    assert len(storage["tasks"]) == 1


def test_show_builds_list(storage, capsys):
    cli.show()

    captured = capsys.readouterr()
    assert "new list" in captured.out.lower()

    assert os.path.exists(cli.daylist_file)


# Add


def test_add_without_list(storage):
    cli.add("task added to non-list", 15)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 1


def test_add(storage):
    # typical flow
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


# Complete


def test_complete(storage):
    # typical flow
    cli.add("task 1", 11)
    cli.add("task 2", 22)
    cli.add("task 3", 33)

    cli.complete(3)
    cli.complete(1)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 3

    # check bad userinput
    with pytest.raises(ValueError):
        cli.complete(200)


# Delete


def test_delete(storage, capsys):
    # typical flow
    cli.add("task 1", 11)
    cli.add("task 2", 22)
    cli.delete(2)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 1

    # check bad userinput
    with pytest.raises(ValueError):
        cli.delete(300)
