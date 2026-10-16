from unittest.mock import patch

from src.core.base.funcs import get_random_number


def test_get_random_number_is_six_digits():
    for _ in range(1000):
        assert 100_000 <= get_random_number() <= 999_999


@patch("src.core.base.funcs.secrets.randbelow")
def test_get_random_number_uses_secrets(mock_randbelow):
    mock_randbelow.return_value = 899_999

    assert get_random_number() == 999_999
    mock_randbelow.assert_called_once_with(900_000)
