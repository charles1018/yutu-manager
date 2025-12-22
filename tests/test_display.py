"""測試 display 模組"""

import pytest

from yutu_cli.utils.display import format_count, format_date, format_duration, truncate


class TestFormatCount:
    """測試 format_count 函式"""

    def test_zero(self):
        assert format_count(0) == "0"

    def test_none(self):
        assert format_count(None) == "0"

    def test_small_number(self):
        assert format_count(999) == "999"

    def test_thousands(self):
        assert format_count(1500) == "1.5K"
        assert format_count(1000) == "1.0K"

    def test_millions(self):
        assert format_count(1500000) == "1.5M"
        assert format_count(1000000) == "1.0M"

    def test_string_input(self):
        assert format_count("1500") == "1.5K"


class TestFormatDuration:
    """測試 format_duration 函式"""

    def test_empty(self):
        assert format_duration(None) == ""
        assert format_duration("") == ""

    def test_seconds_only(self):
        assert format_duration("PT30S") == "0:30"

    def test_minutes_seconds(self):
        assert format_duration("PT5M30S") == "5:30"

    def test_hours_minutes_seconds(self):
        assert format_duration("PT1H2M3S") == "1:02:03"

    def test_hours_only(self):
        assert format_duration("PT2H") == "2:00:00"

    def test_invalid_format(self):
        # 應該回傳原始字串而非崩潰
        result = format_duration("invalid")
        assert isinstance(result, str)


class TestFormatDate:
    """測試 format_date 函式"""

    def test_empty(self):
        assert format_date(None) == ""
        assert format_date("") == ""

    def test_iso_format(self):
        assert format_date("2024-01-15T10:30:00Z") == "2024-01-15"

    def test_short_string(self):
        result = format_date("2024")
        assert result == "2024"


class TestTruncate:
    """測試 truncate 函式"""

    def test_empty(self):
        assert truncate(None) == ""
        assert truncate("") == ""

    def test_short_text(self):
        assert truncate("Hello") == "Hello"

    def test_exact_length(self):
        text = "a" * 60
        assert truncate(text) == text

    def test_long_text(self):
        text = "a" * 100
        result = truncate(text, max_len=60)
        assert len(result) == 60
        assert result.endswith("...")

    def test_newlines_replaced(self):
        assert truncate("Hello\nWorld") == "Hello World"
