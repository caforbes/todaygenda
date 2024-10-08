from datetime import datetime, timedelta, timezone
import pytest

from src.models import Daylist, Task


class TestTaskModel:
    def test_interpret_with_seconds(self):
        """Ensure integers on time estimates are interpreted as seconds."""
        seconds = 100
        task = Task(id=1, title="test", estimate=seconds)
        assert task.estimate.total_seconds() == seconds

    @pytest.mark.parametrize("bad_minutes", [0, -1, 100000])
    def test_bad_estimate(self, bad_minutes):
        """Can't create tasks with time estimate of zero or less."""
        with pytest.raises(ValueError):
            Task(id=1, title="test", estimate=timedelta(minutes=bad_minutes))

    def test_max_estimate(self):
        """Can't create tasks longer than 24 hours."""
        with pytest.raises(ValueError):
            Task(id=1, title="test", estimate=timedelta(days=1))

    @pytest.mark.parametrize("bad_title", ["", "a" * 250])
    def test_bad_title(self, bad_title):
        with pytest.raises(ValueError):
            Task(id=1, title=bad_title, estimate=100)


class TestDaylistModel:
    def test_expiry_good(self):
        # providing a valid expiry date
        daylist = Daylist(
            id=1, expiry=datetime.now(timezone.utc).replace(microsecond=0)
        )
        assert daylist.id == 1

    def test_expiry_past_24h(self):
        # providing a far future expiry date is illegal
        with pytest.raises(ValueError):
            Daylist(id=1, expiry=datetime.now(timezone.utc) + timedelta(days=10))
