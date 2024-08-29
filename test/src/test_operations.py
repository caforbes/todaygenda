import pytest
from datetime import datetime, timedelta

from src.models import Daylist, Task, TaskStatus
from src.operations import build_agenda

TWENTY_M = timedelta(minutes=20)


@pytest.fixture()
def empty_list() -> Daylist:
    """A list with no tasks, expires in 4h."""
    expiry = datetime.now() + timedelta(hours=4)
    return Daylist(id=0, expiry=expiry)


@pytest.fixture()
def list_with_tasks() -> Daylist:
    """A list with 1h of pending tasks, 1h of done tasks, expires in 4h."""
    todos = [
        Task(id=0, title="one", estimate=TWENTY_M),
        Task(id=0, title="two", estimate=TWENTY_M),
        Task(id=0, title="three", estimate=TWENTY_M),
    ]
    done_tasks = [
        Task(id=0, title="done item one", estimate=TWENTY_M, status=TaskStatus.DONE),
        Task(id=0, title="done item two", estimate=TWENTY_M, status=TaskStatus.DONE),
        Task(id=0, title="done item three", estimate=TWENTY_M, status=TaskStatus.DONE),
    ]
    expiry = datetime.now() + timedelta(hours=4)
    return Daylist(id=0, pending_tasks=todos, done_tasks=done_tasks, expiry=expiry)


# build agenda


def test_agenda_empty_list(empty_list):
    agenda = build_agenda(empty_list)

    # agenda has no items
    assert len(agenda.timeline) == 0
    # finish time should be within a minute of exact now
    assert agenda.finish <= datetime.now()
    assert agenda.finish > datetime.now() - timedelta(minutes=1)
    # no warning
    assert agenda.past_expiry is False


def test_agenda_done_tasks_only(list_with_tasks):
    list_with_tasks.pending_tasks = []

    agenda = build_agenda(list_with_tasks)

    # agenda has no items
    assert len(agenda.timeline) == 0
    # finish time should be within a minute of exact now
    assert agenda.finish <= datetime.now()
    assert agenda.finish > datetime.now() - timedelta(minutes=1)
    # no warning
    assert agenda.past_expiry is False


def test_agenda_pending_tasks(list_with_tasks):
    agenda = build_agenda(list_with_tasks)
    todos = list_with_tasks.pending_tasks

    # agenda items are the pending tasks only
    assert len(agenda.timeline) == len(todos)
    # finish time is final task endtime
    assert agenda.finish == agenda.timeline[-1].end
    # finish time is within a minute after total task time
    total_duration = TWENTY_M * len(todos)
    assert agenda.finish <= datetime.now() + total_duration
    assert agenda.finish > datetime.now() + total_duration - timedelta(minutes=1)
    # no warning
    assert agenda.past_expiry is False


def test_agenda_exceeds_expiry(list_with_tasks):
    list_with_tasks.expiry = datetime.now() + timedelta(minutes=10)

    agenda = build_agenda(list_with_tasks)
    todos = list_with_tasks.pending_tasks

    # agenda items are the pending tasks only
    assert len(agenda.timeline) == len(todos)
    # finish time is final task endtime
    assert agenda.finish == agenda.timeline[-1].end
    # finish time is within a minute after total task time
    total_duration = TWENTY_M * len(todos)
    assert agenda.finish <= datetime.now() + total_duration
    assert agenda.finish > datetime.now() + total_duration - timedelta(minutes=1)
    # warning due to exceeding expiry time
    assert agenda.past_expiry is True
