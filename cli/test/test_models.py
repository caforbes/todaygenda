from datetime import datetime, timedelta
import pytest

from cli.models import Daylist, Task, TaskStatus


class TestTaskModel:
    def test_interpret_with_seconds(self):
        """Ensure integers on time estimates are interpreted as seconds"""
        seconds = 100
        task = Task(name="test", estimate=seconds)
        assert task.estimate.total_seconds() == seconds

    @pytest.mark.parametrize("bad_minutes", [0, -1, 100000])
    def test_bad_estimate(self, bad_minutes):
        """Can't create tasks with time estimate of zero or less."""
        with pytest.raises(ValueError):
            Task(name="test", estimate=timedelta(minutes=bad_minutes))

    def test_max_estimate(self):
        """Can't create tasks longer than 24 hours."""
        with pytest.raises(ValueError):
            Task(name="test", estimate=timedelta(days=1))

    @pytest.mark.parametrize("bad_name", ["", "a" * 250])
    def test_bad_name(self, bad_name):
        with pytest.raises(ValueError):
            Task(name=bad_name, estimate=100)

    def test_mark_done(self):
        """Mark task as done and update its metadata"""
        task = Task(name="teststset", estimate=100)
        assert task.status == TaskStatus.PENDING
        task.mark_done()
        assert task.status == TaskStatus.DONE
        assert task.created != task.updated


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

        # Assert tasks times are summed into the estimate
        assert test_list.total_estimate().total_seconds() == sum(task_times)

    def test_total_estimate_with_done(self):
        task_times = [10, 120]
        tasks = self.setup_tasks(durs=task_times)
        test_list = Daylist(tasks=tasks)

        # Expect done tasks do not contribute to total estimate
        tasks[0].mark_done()
        task_times.pop(0)
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

    def test_add_task(self):
        test_list = Daylist()
        tasks = self.setup_tasks()

        for task in tasks:
            test_list.add_task(task)
            assert task in test_list.tasks
        assert len(test_list.tasks) == len(tasks)

    def test_add_task_duplicate(self):
        test_list = Daylist()
        task = Task(name="test task", estimate=20)

        test_list.add_task(task)
        assert task in test_list.tasks
        test_list.add_task(task)
        assert len(test_list.tasks) == 1

    def test_list_tasks(self):
        tasks = self.setup_tasks()
        test_list = Daylist(tasks=tasks)

        tasks[0].mark_done()
        assert len(test_list.done_tasks()) == 1
        assert len(test_list.pending_tasks()) == len(tasks) - 1

    def test_remove_task(self):
        tasks = self.setup_tasks()
        test_list = Daylist(tasks=tasks)

        assert len(test_list.tasks) == len(tasks)
        test_list.remove_task(1)
        assert len(test_list.tasks) == (len(tasks) - 1)
        test_list.remove_task(0)
        assert len(test_list.tasks) == (len(tasks) - 2)

    @pytest.mark.parametrize(
        "bad_index, exception", [(10, IndexError), (-1, ValueError)]
    )
    def test_remove_task_bad_index(self, bad_index, exception):
        test_list = Daylist(tasks=self.setup_tasks())

        with pytest.raises(exception):
            test_list.remove_task(bad_index)

    def test_complete_task(self):
        tasks = self.setup_tasks()
        test_list = Daylist(tasks=tasks)

        assert len(test_list.pending_tasks()) == len(tasks)
        test_list.complete_task(1)
        assert len(test_list.pending_tasks()) == (len(tasks) - 1)
        test_list.complete_task(0)
        assert len(test_list.pending_tasks()) == (len(tasks) - 2)

    @pytest.mark.parametrize(
        "bad_index, exception", [(10, IndexError), (-1, ValueError)]
    )
    def test_complete_task_bad_index(self, bad_index, exception):
        test_list = Daylist(tasks=self.setup_tasks())
        with pytest.raises(exception):
            test_list.complete_task(bad_index)
