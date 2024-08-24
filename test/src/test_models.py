from datetime import timedelta
import pytest

from src.models import Task


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
