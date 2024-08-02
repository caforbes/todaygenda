from datetime import datetime, timedelta
import pytest

from src.models import Daylist, Task


class TestTaskModel:
    def test_interpret_with_seconds(self):
        """Ensure integers on time estimates are interpreted as seconds"""
        seconds = 100
        task = Task(name="test", estimate=seconds)
        assert task.estimate.total_seconds() == seconds

    @pytest.mark.parametrize("too_small", [0, -1])
    def test_min_estimate(self, too_small):
        """Can't create tasks with time estimate of zero or less."""
        with pytest.raises(ValueError):
            Task(name="test", estimate=timedelta(minutes=too_small))

    def test_max_estimate(self):
        """Can't create tasks longer than 24 hours."""
        with pytest.raises(ValueError):
            Task(name="test", estimate=timedelta(days=1))


class TestDaylistModel:
    now = datetime.today()

    @staticmethod
    def setup_tasks(names=["task 1", "task 2"], durs=[60, 120]) -> list[Task]:
        if len(names) != len(durs):
            raise ValueError("Number of provided names and estimates don't match")
        tasks = []
        for name, dur in zip(names, durs):
            tasks.append(Task(name=name, estimate=dur))

        return tasks

    def test_total_estimate(self):
        task_times = [10, 120]
        tasks = self.setup_tasks(durs=task_times)
        test_list = Daylist(tasks=tasks)

        assert test_list.total_estimate().total_seconds() == sum(task_times)

    @pytest.mark.parametrize(
        "sample_datetime,expected",
        [
            (now, True),
            (now + timedelta(days=1), False),
            (now + timedelta(days=-1), False),
        ],
    )
    def test_is_for_today(self, sample_datetime, expected):
        test_list = Daylist(created=sample_datetime)
        assert test_list.is_for_today() == expected
