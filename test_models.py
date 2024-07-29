from src.models import Task


class TestTaskModel:
    # TODO: test custom functions

    def test_interpret_with_seconds(self):
        """Ensure integers on durations are interpreted as seconds"""
        seconds = 100
        task = Task(name="test", duration=seconds)
        assert task.duration.total_seconds() == seconds

    # def test_durationstr():
    # pass


# class TestDaylistModel:
# TODO: test custom functions
#     def test_task_duration():
#         pass

#     def test_is_for_today():
#         pass
