import json
import os
import pytest

import cli.app as app
from db.local import LOCAL_FILE


def get_storage_json() -> dict:
    assert "test" in LOCAL_FILE
    with open(LOCAL_FILE) as f:
        content = json.load(f)
    return content


@pytest.fixture()
def storage():
    assert "test" in LOCAL_FILE
    if os.path.exists(LOCAL_FILE):
        os.remove(LOCAL_FILE)

    yield

    if os.path.exists(LOCAL_FILE):
        os.remove(LOCAL_FILE)


# Show


def test_show_typical_userflow(storage, capsys):
    app.build_from_storage()

    app.add("test task", 55)
    app.show()

    captured = capsys.readouterr()
    assert "estimate" in captured.out.lower()

    storage = get_storage_json()
    assert os.path.exists(LOCAL_FILE)
    assert len(storage["tasks"]) == 1


def test_show_builds_list(storage, capsys):
    app.show()

    captured = capsys.readouterr()
    assert "new list" in captured.out.lower()

    assert os.path.exists(LOCAL_FILE)


# Add


def test_add_without_list(storage):
    app.add("task added to non-list", 15)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 1


def test_add(storage):
    # typical flow
    app.add("task 1", 11)
    app.add("task 2", 22)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 2

    # check bad userinput
    bad_names = ["", "a" * 250]
    for bad_name in bad_names:
        with pytest.raises(ValueError):
            app.add(bad_name, 100)

    bad_minutes = [-1, 0, 100000]

    for bad_minutes in bad_minutes:
        with pytest.raises(ValueError):
            app.add("task is okay", bad_minutes)


# Complete


def test_complete(storage):
    # typical flow
    app.add("task 1", 11)
    app.add("task 2", 22)
    app.add("task 3", 33)

    app.complete(3)
    app.complete(1)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 3

    # check bad userinput
    with pytest.raises(ValueError):
        app.complete(200)


# Delete


def test_delete(storage, capsys):
    # typical flow
    app.add("task 1", 11)
    app.add("task 2", 22)
    app.delete(2)

    storage = get_storage_json()

    assert "tasks" in storage
    assert len(storage["tasks"]) == 1

    # check bad userinput
    with pytest.raises(ValueError):
        app.delete(300)
