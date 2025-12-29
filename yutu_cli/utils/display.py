"""顯示輔助模組 - 使用 rich 美化輸出"""

from datetime import datetime
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def format_count(count: int | str | None) -> str:
    """格式化數字（加上 K/M 後綴）"""
    if not count:
        return "0"
    count = int(count)
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def format_duration(duration: str | None) -> str:
    """將 ISO 8601 時長轉換為人類可讀格式

    Args:
        duration: ISO 8601 時長格式（例如 PT1H2M3S）

    Returns:
        人類可讀格式（例如 1:02:03）
    """
    if not duration:
        return ""

    try:
        # PT1H2M3S -> 1:02:03
        duration = duration.replace("PT", "")
        hours = minutes = seconds = 0
        if "H" in duration:
            h, duration = duration.split("H")
            hours = int(h)
        if "M" in duration:
            m, duration = duration.split("M")
            minutes = int(m)
        if "S" in duration:
            seconds = int(duration.replace("S", ""))
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    except (ValueError, AttributeError):
        # 無法解析時回傳原始字串
        return str(duration) if duration else ""


def format_date(date_str: str | None) -> str:
    """格式化日期"""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return date_str[:10] if len(date_str) >= 10 else date_str


def truncate(text: str | None, max_len: int = 60) -> str:
    """截斷過長文字"""
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def display_playlists(data: dict | list) -> None:
    """顯示播放清單列表"""
    items = data if isinstance(data, list) else data.get("items", [])
    
    if not items:
        console.print("[yellow]找不到任何播放清單[/yellow]")
        return
    
    table = Table(
        title=f"📋 播放清單（共 {len(items)} 個）",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("標題", style="bold")
    table.add_column("影片數", justify="right", style="green")
    table.add_column("隱私狀態", justify="center")
    table.add_column("ID", style="dim")
    
    for i, item in enumerate(items, 1):
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        status = item.get("status", {})
        
        title = snippet.get("title", "無標題")
        video_count = str(content.get("itemCount", 0))
        privacy = status.get("privacyStatus", "unknown")
        playlist_id = item.get("id", "")
        
        # 隱私狀態顏色
        privacy_style = {
            "public": "[green]公開[/green]",
            "unlisted": "[yellow]不公開[/yellow]",
            "private": "[red]私人[/red]",
        }.get(privacy, privacy)
        
        table.add_row(str(i), title, video_count, privacy_style, playlist_id)
    
    console.print(table)


def display_playlist_items(data: dict | list, playlist_title: str = "") -> None:
    """顯示播放清單中的影片"""
    items = data if isinstance(data, list) else data.get("items", [])
    
    if not items:
        console.print("[yellow]播放清單中沒有影片[/yellow]")
        return
    
    title = f"🎥 {playlist_title}" if playlist_title else "🎥 播放清單內容"
    table = Table(
        title=f"{title}（共 {len(items)} 部影片）",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("標題", style="bold", max_width=50)
    table.add_column("頻道", style="dim")
    table.add_column("發布日期", justify="center")
    table.add_column("Video ID", style="dim")
    
    for i, item in enumerate(items, 1):
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        
        title = truncate(snippet.get("title", "無標題"), 50)
        channel = truncate(snippet.get("videoOwnerChannelTitle", ""), 20)
        video_id = content.get("videoId", snippet.get("resourceId", {}).get("videoId", ""))
        published = format_date(content.get("videoPublishedAt", ""))
        
        table.add_row(str(i), title, channel, published, video_id)
    
    console.print(table)


def display_videos(data: dict | list) -> None:
    """顯示影片列表"""
    items = data if isinstance(data, list) else data.get("items", [])
    
    if not items:
        console.print("[yellow]找不到任何影片[/yellow]")
        return
    
    table = Table(
        title=f"🎬 影片（共 {len(items)} 部）",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("標題", style="bold", max_width=45)
    table.add_column("觀看次數", justify="right", style="green")
    table.add_column("讚數", justify="right", style="magenta")
    table.add_column("時長", justify="center")
    table.add_column("發布日期", justify="center")
    
    for i, item in enumerate(items, 1):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        
        title = truncate(snippet.get("title", "無標題"), 45)
        views = format_count(stats.get("viewCount"))
        likes = format_count(stats.get("likeCount"))
        duration = format_duration(content.get("duration"))
        published = format_date(snippet.get("publishedAt", ""))
        
        table.add_row(str(i), title, views, likes, duration, published)
    
    console.print(table)


def display_search_results(data: dict | list) -> None:
    """顯示搜尋結果"""
    items = data if isinstance(data, list) else data.get("items", [])
    
    if not items:
        console.print("[yellow]找不到符合的結果[/yellow]")
        return
    
    page_info = data.get("pageInfo", {}) if isinstance(data, dict) else {}
    total = page_info.get("totalResults", len(items))
    
    table = Table(
        title=f"🔍 搜尋結果（顯示 {len(items)} / 共 {total} 項）",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("類型", justify="center", width=8)
    table.add_column("標題", style="bold", max_width=45)
    table.add_column("頻道", style="dim")
    table.add_column("發布日期", justify="center")
    table.add_column("ID", style="dim")
    
    for i, item in enumerate(items, 1):
        snippet = item.get("snippet", {})
        id_info = item.get("id", {})
        
        kind = id_info.get("kind", "").replace("youtube#", "")
        resource_id = (
            id_info.get("videoId")
            or id_info.get("playlistId")
            or id_info.get("channelId")
            or ""
        )
        title = truncate(snippet.get("title", "無標題"), 45)
        channel = truncate(snippet.get("channelTitle", ""), 20)
        published = format_date(snippet.get("publishedAt", ""))
        
        # 類型樣式
        kind_style = {
            "video": "[green]影片[/green]",
            "playlist": "[blue]清單[/blue]",
            "channel": "[yellow]頻道[/yellow]",
        }.get(kind, kind)
        
        table.add_row(str(i), kind_style, title, channel, published, resource_id)
    
    console.print(table)


def display_channel_info(data: dict | list) -> None:
    """顯示頻道資訊"""
    items = data if isinstance(data, list) else data.get("items", [])
    
    if not items:
        console.print("[yellow]找不到頻道資訊[/yellow]")
        return
    
    channel = items[0]
    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})
    
    title = snippet.get("title", "無標題")
    description = snippet.get("description", "")
    subs = format_count(stats.get("subscriberCount"))
    videos = format_count(stats.get("videoCount"))
    views = format_count(stats.get("viewCount"))
    channel_id = channel.get("id", "")
    
    panel_content = f"""[bold cyan]{title}[/bold cyan]
[dim]ID: {channel_id}[/dim]

📊 [bold]統計資料[/bold]
├─ 訂閱數：[green]{subs}[/green]
├─ 影片數：[blue]{videos}[/blue]
└─ 總觀看次數：[magenta]{views}[/magenta]

📝 [bold]簡介[/bold]
{truncate(description, 200) or '（無簡介）'}
"""
    console.print(Panel(panel_content, title="📺 我的頻道", border_style="cyan"))


def display_error(message: str) -> None:
    """顯示錯誤訊息"""
    console.print(Panel(f"[red]{message}[/red]", title="❌ 錯誤", border_style="red"))


def display_success(message: str) -> None:
    """顯示成功訊息"""
    console.print(Panel(f"[green]{message}[/green]", title="✅ 成功", border_style="green"))


def display_warning(message: str) -> None:
    """顯示警告訊息"""
    console.print(Panel(f"[yellow]{message}[/yellow]", title="⚠️ 警告", border_style="yellow"))


def format_moderation_status(status: str) -> str:
    """格式化審核狀態顯示

    Args:
        status: 審核狀態（published/heldForReview/rejected/likelySpam）

    Returns:
        帶樣式的狀態文字
    """
    status_styles = {
        "published": "[green]已發布[/green]",
        "heldForReview": "[yellow]待審核[/yellow]",
        "rejected": "[red]已拒絕[/red]",
        "likelySpam": "[red]疑似垃圾[/red]",
    }
    return status_styles.get(status, status)


def display_comments(data: dict | list, video_title: str = "") -> None:
    """顯示評論列表

    Args:
        data: 評論串資料（來自 commentThread list）
        video_title: 影片標題（用於表格標題）
    """
    items = data if isinstance(data, list) else data.get("items", [])

    if not items:
        console.print("[yellow]此影片沒有評論[/yellow]")
        return

    title = f"💬 {video_title}" if video_title else "💬 評論列表"
    table = Table(
        title=f"{title}（共 {len(items)} 則）",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("用戶", style="bold", width=15)
    table.add_column("評論內容", max_width=45)
    table.add_column("👍", justify="right", style="magenta", width=6)
    table.add_column("回覆", justify="right", style="blue", width=6)
    table.add_column("日期", justify="center", width=10)

    for i, item in enumerate(items, 1):
        snippet = item.get("snippet", {})
        top_comment = snippet.get("topLevelComment", {}).get("snippet", {})

        author = truncate(top_comment.get("authorDisplayName", ""), 15)
        text = truncate(top_comment.get("textDisplay", ""), 45)
        likes = format_count(top_comment.get("likeCount", 0))
        reply_count = str(snippet.get("totalReplyCount", 0))
        published = format_date(top_comment.get("publishedAt", ""))

        table.add_row(str(i), author, text, likes, reply_count, published)

    console.print(table)


def display_comment_detail(comment: dict, include_replies: bool = True) -> None:
    """顯示單則評論詳情（含回覆）

    Args:
        comment: 評論串資料
        include_replies: 是否顯示回覆
    """
    snippet = comment.get("snippet", {})
    top_comment = snippet.get("topLevelComment", {}).get("snippet", {})
    replies = comment.get("replies", {}).get("comments", [])

    author = top_comment.get("authorDisplayName", "匿名")
    text = top_comment.get("textDisplay", "")
    likes = format_count(top_comment.get("likeCount", 0))
    published = format_date(top_comment.get("publishedAt", ""))
    reply_count = snippet.get("totalReplyCount", 0)

    content = f"""[bold cyan]{author}[/bold cyan] · {published}
{text}

👍 [magenta]{likes}[/magenta]  💬 [blue]{reply_count} 則回覆[/blue]
"""

    if include_replies and replies:
        content += "\n[bold]─── 回覆 ───[/bold]\n"
        for reply in replies[:5]:  # 最多顯示 5 則
            r_snippet = reply.get("snippet", {})
            r_author = r_snippet.get("authorDisplayName", "")
            r_text = truncate(r_snippet.get("textDisplay", ""), 60)
            r_date = format_date(r_snippet.get("publishedAt", ""))
            content += f"\n[dim]{r_author}[/dim] · {r_date}\n{r_text}\n"

        if reply_count > 5:
            content += f"\n[dim]...還有 {reply_count - 5} 則回覆[/dim]"

    console.print(Panel(content, title="💬 評論詳情", border_style="cyan"))
