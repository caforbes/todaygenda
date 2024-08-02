from datetime import datetime, timedelta
import pytest

from src.models import Daylist, Task


class TestTaskModel:
    def test_interpret_with_seconds(self):
        """Ensure integers on durations are interpreted as seconds"""
        seconds = 100
        task = Task(name="test", duration=seconds)
        assert task.duration.total_seconds() == seconds

    def test_max_duration(self):
        """Can't create tasks longer than 24 hours."""
        with pytest.raises(ValueError):
            Task(name="test", duration=timedelta(days=1))


class TestDaylistModel:
    now = datetime.today()

    @staticmethod
    def setup_tasks(names=["task 1", "task 2"], durs=[60, 120]) -> list[Task]:
        if len(names) != len(durs):
            raise ValueError("Number of names and durations don't match")
        tasks = []
        for name, dur in zip(names, durs):
            tasks.append(Task(name=name, duration=dur))

        return tasks

    def test_task_duration(self):
        task_times = [0, 120]
        tasks = self.setup_tasks(durs=task_times)
        test_list = Daylist(tasks=tasks)

        assert test_list.task_duration().total_seconds() == sum(task_times)

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
