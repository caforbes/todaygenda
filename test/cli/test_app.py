import json
import os
import pytest

import cli.app as app
from db.local import LOCAL_FILE


@pytest.fixture()
def storage():
    assert "test" in LOCAL_FILE
    if os.path.exists(LOCAL_FILE):
        os.remove(LOCAL_FILE)

    yield LOCAL_FILE

    if os.path.exists(LOCAL_FILE):
        os.remove(LOCAL_FILE)


def get_json_content(json_path) -> dict:
    assert "test" in LOCAL_FILE
    assert os.path.exists(LOCAL_FILE)
    with open(json_path) as f:
        content = json.load(f)
    return content


# Show


def test_typical_userflow(storage, capsys):
    app.add("test task", 55)

    # storage location is created and updated
    assert os.path.exists(storage)
    storage_content = get_json_content(storage)
    assert len(storage_content["pending_tasks"]) == 1

    app.show()
    captured = capsys.readouterr()

    # command displays and storage contents are updated
    assert "estimate" in captured.out.lower()


def test_show_builds_list(storage, capsys):
    app.show()

    captured = capsys.readouterr()
    assert "new list" in captured.out.lower()

    assert os.path.exists(storage)


# Add


def test_add(storage):
    # typical flow
    app.add("task 1", 11)
    app.add("task 2", 22)

    storage_content = get_json_content(storage)

    assert len(storage_content["pending_tasks"]) == 2
    assert len(storage_content["done_tasks"]) == 0

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

    storage_content = get_json_content(storage)
    assert len(storage_content["pending_tasks"]) == 3

    app.complete(3)
    app.complete(1)

    storage_content = get_json_content(storage)

    assert len(storage_content["pending_tasks"]) == 1
    assert len(storage_content["done_tasks"]) == 2

    # check bad userinput
    with pytest.raises(ValueError):
        app.complete(200)


# Delete


def test_delete(storage, capsys):
    # typical flow
    app.add("task 1", 11)
    app.add("task 2", 22)
    app.delete(2)

    storage_content = get_json_content(storage)

    assert len(storage_content["pending_tasks"]) == 1
    assert len(storage_content["done_tasks"]) == 0

    # check bad userinput
    with pytest.raises(IndexError):
        app.delete(300)
