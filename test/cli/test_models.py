from datetime import datetime, timedelta
import pytest

from src.models import TaskStatus
from cli.models import TaskCLI, DaylistCLI


class TestTaskObject:
    def test_mark_done(self):
        """Mark task as done and update its metadata"""
        task = TaskCLI(title="teststset", estimate=100)
        assert task.status == TaskStatus.PENDING
        task.mark_done()
        assert task.status == TaskStatus.DONE
        assert task.created != task.updated


class TestDaylistObject:
    @staticmethod
    def setup_tasks(titles=["task 1", "task 2"], durs=[60, 120]) -> list[TaskCLI]:
        if len(titles) != len(durs):
            raise ValueError("Number of provided titles and estimates don't match")
        tasks = []
        for title, dur in zip(titles, durs):
            tasks.append(TaskCLI(title=title, estimate=dur))

        return tasks

    def test_total_estimate(self):
        task_times = [10, 120]
        tasks = self.setup_tasks(durs=task_times)
        test_list = DaylistCLI(pending_tasks=tasks)

        # Assert tasks times are summed into the estimate
        assert test_list.total_estimate().total_seconds() == sum(task_times)

    def test_total_estimate_with_done(self):
        task_times = [10, 120]
        tasks = self.setup_tasks(durs=task_times)
        test_list = DaylistCLI(pending_tasks=tasks)

        # Expect done tasks do not contribute to total estimate
        test_list.complete_task(0)
        task_times.pop(0)
        assert test_list.total_estimate().total_seconds() == sum(task_times)

    @pytest.mark.parametrize(
        "sample_datetime,expected",
        [
            (datetime.now() + timedelta(hours=2), False),
            (datetime.now() - timedelta(hours=2), True),
            (datetime.now() - timedelta(days=1), True),
        ],
    )
    def test_is_expired(self, sample_datetime, expected):
        test_list = DaylistCLI(expiry=sample_datetime)
        assert test_list.is_expired() == expected

    def test_add_task(self):
        test_list = DaylistCLI()
        assert len(test_list.pending_tasks) == 0

        test_title = "hello"
        test_delta = timedelta(minutes=30)
        test_list.add_task(title=test_title, estimate=test_delta)
        assert len(test_list.pending_tasks) == 1
        assert test_list.pending_tasks[0].title == test_title

    def test_remove_task(self):
        tasks = self.setup_tasks()
        test_list = DaylistCLI(pending_tasks=tasks)

        assert len(test_list.pending_tasks) == len(tasks)
        test_list.remove_task(1)
        assert len(test_list.pending_tasks) == (len(tasks) - 1)
        test_list.remove_task(0)
        assert len(test_list.pending_tasks) == (len(tasks) - 2)

    @pytest.mark.parametrize("bad_index", [10, -1])
    def test_remove_task_bad_index(self, bad_index):
        test_list = DaylistCLI(pending_tasks=self.setup_tasks())
        with pytest.raises(IndexError):
            test_list.remove_task(bad_index)

    def test_complete_task(self):
        tasks = self.setup_tasks()
        test_list = DaylistCLI(pending_tasks=tasks)

        assert len(test_list.pending_tasks) == len(tasks)
        test_list.complete_task(1)
        assert len(test_list.pending_tasks) == (len(tasks) - 1)
        test_list.complete_task(0)
        assert len(test_list.pending_tasks) == (len(tasks) - 2)

    @pytest.mark.parametrize("bad_index", [10, -1])
    def test_complete_task_bad_index(self, bad_index):
        test_list = DaylistCLI(pending_tasks=self.setup_tasks())
        with pytest.raises(IndexError):
            test_list.complete_task(bad_index)
