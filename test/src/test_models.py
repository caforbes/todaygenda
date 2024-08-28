from datetime import datetime, timedelta
import pytest

from src.models import Daylist, Task


class TestTaskModel:
    def test_interpret_with_seconds(self):
        """Ensure integers on time estimates are interpreted as seconds."""
        seconds = 100
        task = Task(title="test", estimate=seconds)
        assert task.estimate.total_seconds() == seconds

    @pytest.mark.parametrize("bad_minutes", [0, -1, 100000])
    def test_bad_estimate(self, bad_minutes):
        """Can't create tasks with time estimate of zero or less."""
        with pytest.raises(ValueError):
            Task(title="test", estimate=timedelta(minutes=bad_minutes))

    def test_max_estimate(self):
        """Can't create tasks longer than 24 hours."""
        with pytest.raises(ValueError):
            Task(title="test", estimate=timedelta(days=1))

    @pytest.mark.parametrize("bad_title", ["", "a" * 250])
    def test_bad_title(self, bad_title):
        with pytest.raises(ValueError):
            Task(title=bad_title, estimate=100)


class TestDaylistModel:
    def test_expiry_past_24h(self):
        # providing a far future expiry date is illegal
        with pytest.raises(ValueError):
            Daylist(expiry=datetime.now() + timedelta(days=10))
