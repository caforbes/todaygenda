from src.utils import next_midnight


def test_next_midnight():
    result = next_midnight()
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
