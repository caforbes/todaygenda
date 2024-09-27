from datetime import datetime, timedelta, timezone
import pytest

from cli.models import TaskCLI, DaylistCLI

TZNOW = datetime.now(timezone.utc)


class TestTaskObject:
    def test_mark_done(self):
        """Mark task as done and update its metadata."""
        task = TaskCLI(title="teststset", estimate=100)
        assert not task.done
        task.mark_done()
        assert task.done
        assert task.created != task.updated


class TestDaylistObject:
    @pytest.fixture()
    @staticmethod
    def initial_tasks() -> list[TaskCLI]:
        tasks = [
            TaskCLI(title="one", estimate=timedelta(minutes=20)),
            TaskCLI(title="two", estimate=timedelta(minutes=20)),
            TaskCLI(title="three", estimate=timedelta(minutes=20)),
        ]
        return tasks

    def test_total_estimate(self):
        task_times = [10, 120]
        tasks = [
            TaskCLI(title="one", estimate=timedelta(seconds=task_times[0])),
            TaskCLI(title="two", estimate=timedelta(seconds=task_times[1])),
        ]
        test_list = DaylistCLI(pending_tasks=tasks)

        # Assert tasks times are summed into the estimate
        assert test_list.total_estimate().total_seconds() == sum(task_times)

    def test_total_estimate_with_done(self):
        task_times = [60, 60]
        tasks = [
            TaskCLI(title="one", estimate=timedelta(seconds=task_times[0])),
            TaskCLI(title="two", estimate=timedelta(seconds=task_times[1])),
        ]
        test_list = DaylistCLI(pending_tasks=tasks)

        # Expect done tasks do not contribute to total estimate
        test_list.complete_task(0)
        task_times.pop(0)
        assert test_list.total_estimate().total_seconds() == sum(task_times)

    @pytest.mark.parametrize(
        "sample_datetime,expected",
        [
            (TZNOW + timedelta(hours=2), False),
            (TZNOW - timedelta(hours=2), True),
            (TZNOW - timedelta(days=1), True),
        ],
    )
    def test_is_expired(self, sample_datetime, expected):
        test_list = DaylistCLI(expiry=sample_datetime)
        assert test_list.is_expired() == expected

    def test_add_task_to_empty(self):
        test_list = DaylistCLI()
        assert len(test_list.pending_tasks) == 0

        test_title = "hello"
        test_delta = timedelta(minutes=30)
        test_list.add_task(title=test_title, estimate=test_delta)
        assert len(test_list.pending_tasks) == 1
        assert test_list.pending_tasks[0].title == test_title

    def test_add_task_to_others(self, initial_tasks):
        test_list = DaylistCLI(pending_tasks=initial_tasks)
        assert len(test_list.pending_tasks) == len(initial_tasks)

        test_title = "hello"
        test_delta = timedelta(minutes=30)
        test_list.add_task(title=test_title, estimate=test_delta)
        assert len(test_list.pending_tasks) == len(initial_tasks) + 1

    def test_remove_task(self, initial_tasks):
        test_list = DaylistCLI(pending_tasks=initial_tasks)

        assert len(test_list.pending_tasks) == len(initial_tasks)
        test_list.remove_task(1)
        assert len(test_list.pending_tasks) == (len(initial_tasks) - 1)
        test_list.remove_task(0)
        assert len(test_list.pending_tasks) == (len(initial_tasks) - 2)

    @pytest.mark.parametrize("bad_index", [100, -1])
    def test_remove_task_bad_index(self, bad_index, initial_tasks):
        test_list = DaylistCLI(pending_tasks=initial_tasks)
        with pytest.raises(IndexError):
            test_list.remove_task(bad_index)

    def test_complete_task(self, initial_tasks):
        test_list = DaylistCLI(pending_tasks=initial_tasks)

        assert len(test_list.pending_tasks) == len(initial_tasks)
        test_list.complete_task(1)
        assert len(test_list.pending_tasks) == (len(initial_tasks) - 1)
        test_list.complete_task(0)
        assert len(test_list.pending_tasks) == (len(initial_tasks) - 2)

    @pytest.mark.parametrize("bad_index", [100, -1])
    def test_complete_task_bad_index(self, bad_index, initial_tasks):
        test_list = DaylistCLI(pending_tasks=initial_tasks)
        with pytest.raises(IndexError):
            test_list.complete_task(bad_index)
