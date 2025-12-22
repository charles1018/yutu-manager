"""測試 yutu 模組"""

import pytest

from yutu_cli.utils.yutu import YutuResult


class TestYutuResult:
    """測試 YutuResult 資料類別"""

    def test_success_result(self):
        """測試成功結果"""
        result = YutuResult(success=True, data={"items": []})
        assert result.success is True
        assert result.data == {"items": []}
        assert result.error is None

    def test_error_result(self):
        """測試錯誤結果"""
        result = YutuResult(success=False, error="API 錯誤")
        assert result.success is False
        assert result.error == "API 錯誤"
        assert result.data is None

    def test_result_with_raw_output(self):
        """測試帶有原始輸出的結果"""
        result = YutuResult(
            success=True,
            data={"items": []},
            raw_output='{"items": []}',
        )
        assert result.raw_output == '{"items": []}'

    def test_default_values(self):
        """測試預設值"""
        result = YutuResult(success=True)
        assert result.data is None
        assert result.error is None
        assert result.raw_output == ""
