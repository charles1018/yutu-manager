"""YouTube 相關工具函式"""

import re


def extract_video_id(url_or_id: str) -> str:
    """從 YouTube 網址提取影片 ID

    Args:
        url_or_id: YouTube 影片網址或 ID

    Returns:
        影片 ID（11 字元）

    Examples:
        >>> extract_video_id("dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    # 如果已經是 ID（11 字元且不含斜線）
    if len(url_or_id) == 11 and "/" not in url_or_id:
        return url_or_id

    # 嘗試從網址提取
    patterns = [
        r"(?:v=|\/)([\w-]{11})(?:\?|&|$)",  # watch?v= 或 /xxxxx
        r"youtu\.be\/([\w-]{11})",           # youtu.be/
        r"embed\/([\w-]{11})",               # embed/
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # 無法識別，原樣回傳
    return url_or_id
