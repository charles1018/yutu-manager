"""測試 youtube_utils 模組"""

import pytest

from yutu_cli.utils.youtube_utils import extract_video_id


class TestExtractVideoId:
    """測試 extract_video_id 函式"""

    def test_raw_id(self):
        """測試直接傳入影片 ID"""
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_watch_url(self):
        """測試標準 watch 網址"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_watch_url_with_params(self):
        """測試帶有額外參數的 watch 網址"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxxxxxxx"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self):
        """測試短網址 youtu.be"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url_with_params(self):
        """測試帶參數的短網址"""
        url = "https://youtu.be/dQw4w9WgXcQ?t=120"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        """測試嵌入網址"""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_unrecognized_format(self):
        """測試無法辨識的格式，應回傳原字串"""
        unknown = "some_random_string"
        assert extract_video_id(unknown) == unknown

    def test_id_with_special_chars(self):
        """測試含有特殊字元的 ID（- 和 _）"""
        video_id = "abc-_123XYZ"
        assert extract_video_id(video_id) == video_id
