"""搜尋功能"""

from typing import Optional

import questionary

from yutu_cli.utils.display import console, display_error, display_search_results
from yutu_cli.utils.yutu import YutuCLI, get_yutu


def search_menu() -> bool:
    """搜尋選單
    
    Returns:
        True 繼續主選單，False 結束程式
    """
    yutu = get_yutu()
    
    choices = [
        questionary.Choice("1. 🔍 搜尋影片", value="video"),
        questionary.Choice("2. 📋 搜尋播放清單", value="playlist"),
        questionary.Choice("3. 📺 搜尋頻道", value="channel"),
        questionary.Choice("0. ⬅️  返回主選單", value="back"),
    ]
    
    while True:
        action = questionary.select(
            "🔍 搜尋 YouTube",
            choices=choices,
            instruction="使用 ↑↓ 鍵選擇，Enter 確認",
        ).ask()
        
        if action is None or action == "back":
            return True
        
        if action in ("video", "playlist", "channel"):
            _search(yutu, search_type=action)


def _search(yutu: YutuCLI, search_type: str = "video") -> None:
    """執行搜尋"""
    type_names = {
        "video": "影片",
        "playlist": "播放清單",
        "channel": "頻道",
    }
    
    query = questionary.text(
        f"搜尋{type_names.get(search_type, '')}關鍵字：",
        validate=lambda x: len(x.strip()) > 0 or "請輸入關鍵字",
    ).ask()
    
    if not query:
        return
    
    # 排序選項
    order = questionary.select(
        "排序方式：",
        choices=[
            questionary.Choice("相關性", value="relevance"),
            questionary.Choice("發布日期（最新）", value="date"),
            questionary.Choice("觀看次數", value="viewCount"),
            questionary.Choice("評分", value="rating"),
        ],
        default="relevance",
    ).ask()
    
    if not order:
        return
    
    # 最大結果數
    max_results = questionary.select(
        "結果數量：",
        choices=[
            questionary.Choice("10", value=10),
            questionary.Choice("25", value=25),
            questionary.Choice("50", value=50),
            questionary.Choice("全部", value=0),
        ],
        default=25,
    ).ask()
    
    if max_results is None:
        return
    
    with console.status(f"[cyan]正在搜尋「{query}」...[/cyan]"):
        result = yutu.run(
            "search", "list",
            q=query,
            type=search_type,
            order=order,
            max_results=max_results if max_results > 0 else None,
        )
    
    if not result.success:
        display_error(result.error or "搜尋失敗")
        return
    
    display_search_results(result.data)
