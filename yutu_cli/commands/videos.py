"""影片管理功能"""

from typing import Optional

import questionary
from rich.console import Console
from rich.panel import Panel

from yutu_cli.utils.display import (
    display_error,
    display_search_results,
    display_success,
    display_videos,
    format_count,
    format_date,
    format_duration,
)
from yutu_cli.utils.youtube_utils import extract_video_id
from yutu_cli.utils.yutu import YutuCLI, get_yutu

console = Console()


def video_menu() -> bool:
    """影片管理選單
    
    Returns:
        True 繼續主選單，False 結束程式
    """
    yutu = get_yutu()
    
    choices = [
        questionary.Choice("1. 📋 列出我的影片", value="list"),
        questionary.Choice("2. 🔍 查看影片詳情", value="details"),
        questionary.Choice("0. ⬅️  返回主選單", value="back"),
    ]
    
    while True:
        action = questionary.select(
            "🎥 影片管理",
            choices=choices,
            instruction="使用 ↑↓ 鍵選擇，Enter 確認",
        ).ask()
        
        if action is None or action == "back":
            return True
        
        if action == "list":
            _list_my_videos(yutu)
        elif action == "details":
            _view_video_details(yutu)


def _list_my_videos(yutu: YutuCLI, max_results: Optional[int] = 50) -> Optional[list]:
    """列出我的影片"""
    with console.status("[cyan]正在載入影片...[/cyan]"):
        result = yutu.list_my_videos(max_results=max_results)
    
    if not result.success:
        display_error(result.error or "無法取得影片列表")
        return None
    
    display_search_results(result.data)
    return result.data.get("items", []) if result.data else []


def _view_video_details(yutu: YutuCLI) -> None:
    """查看影片詳情"""
    video_id = questionary.text(
        "輸入影片 ID 或 YouTube 網址：",
        validate=lambda x: len(x.strip()) > 0 or "請輸入影片 ID",
    ).ask()
    
    if not video_id:
        return
    
    # 從網址提取 video ID
    video_id = extract_video_id(video_id.strip())
    
    with console.status("[cyan]正在載入影片詳情...[/cyan]"):
        result = yutu.get_video_details(video_id)
    
    if not result.success:
        display_error(result.error or "無法取得影片詳情")
        return
    
    items = result.data.get("items", []) if result.data else []
    if not items:
        display_error("找不到此影片")
        return
    
    video = items[0]
    snippet = video.get("snippet", {})
    stats = video.get("statistics", {})
    content = video.get("contentDetails", {})
    status = video.get("status", {})
    
    # 格式化資訊
    title = snippet.get("title", "無標題")
    description = snippet.get("description", "")[:500]
    channel = snippet.get("channelTitle", "")
    published = format_date(snippet.get("publishedAt", ""))
    
    views = format_count(stats.get("viewCount"))
    likes = format_count(stats.get("likeCount"))
    comments_count = format_count(stats.get("commentCount"))
    
    duration = format_duration(content.get("duration"))
    definition = content.get("definition", "").upper()
    
    privacy = status.get("privacyStatus", "")
    privacy_display = {
        "public": "[green]公開[/green]",
        "unlisted": "[yellow]不公開[/yellow]",
        "private": "[red]私人[/red]",
    }.get(privacy, privacy)
    
    video_url = f"https://youtu.be/{video.get('id', '')}"
    
    panel_content = f"""[bold cyan]{title}[/bold cyan]
[dim]{video_url}[/dim]

📊 [bold]統計資料[/bold]
├─ 觀看次數：[green]{views}[/green]
├─ 讚數：[magenta]{likes}[/magenta]
└─ 留言數：[blue]{comments_count}[/blue]

🎬 [bold]影片資訊[/bold]
├─ 時長：{duration}
├─ 畫質：{definition}
├─ 隱私狀態：{privacy_display}
├─ 發布日期：{published}
└─ 頻道：{channel}

📝 [bold]描述[/bold]
{description or '（無描述）'}
"""
    console.print(Panel(panel_content, title="🎥 影片詳情", border_style="cyan"))
