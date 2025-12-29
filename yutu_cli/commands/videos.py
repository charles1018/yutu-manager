"""影片管理功能"""

from typing import Optional

import questionary
from rich.panel import Panel

from yutu_cli.utils.display import (
    console,
    display_error,
    display_search_results,
    display_success,
    display_warning,
    format_count,
    format_date,
    format_duration,
)
from yutu_cli.utils.youtube_utils import extract_video_id
from yutu_cli.utils.yutu import YutuCLI, get_yutu


def video_menu() -> bool:
    """影片管理選單

    Returns:
        True 繼續主選單，False 結束程式
    """
    yutu = get_yutu()

    choices = [
        questionary.Choice("📋 列出我的影片", value="list", shortcut_key="1"),
        questionary.Choice("🔍 查看影片詳情", value="details", shortcut_key="2"),
        questionary.Choice("✏️  編輯影片資訊", value="update", shortcut_key="3"),
        questionary.Choice("👍 評分影片", value="rate", shortcut_key="4"),
        questionary.Choice("🗑️  刪除影片", value="delete", shortcut_key="5"),
        questionary.Choice("⬅️  返回主選單", value="back", shortcut_key="0"),
    ]

    while True:
        action = questionary.select(
            "🎥 影片管理",
            choices=choices,
            instruction="輸入數字或使用 ↑↓ 選擇，Enter 確認",
            use_shortcuts=True,
        ).ask()

        if action is None or action == "back":
            return True

        if action == "list":
            _list_my_videos(yutu)
        elif action == "details":
            _view_video_details(yutu)
        elif action == "update":
            _update_video(yutu)
        elif action == "rate":
            _rate_video(yutu)
        elif action == "delete":
            _delete_video(yutu)


def _list_my_videos(yutu: YutuCLI, max_results: Optional[int] = 50) -> Optional[list]:
    """列出我的影片"""
    with console.status("[cyan]正在載入影片...[/cyan]"):
        result = yutu.list_my_videos(max_results=max_results)
    
    if not result.success:
        display_error(result.error or "無法取得影片列表")
        return None
    
    display_search_results(result.data)
    if isinstance(result.data, list):
        return result.data
    return result.data.get("items", []) if result.data else []


def _view_video_details(yutu: YutuCLI) -> None:
    """查看影片詳情"""
    video_id = questionary.text(
        "輸入影片 ID 或 YouTube 網址（留空返回）：",
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
    
    if isinstance(result.data, list):
        items = result.data
    else:
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


def _update_video(yutu: YutuCLI) -> None:
    """編輯影片資訊"""
    video_input = questionary.text(
        "輸入影片 ID 或 YouTube 網址（留空返回）：",
    ).ask()

    if not video_input:
        return

    video_id = extract_video_id(video_input.strip())

    # 先取得現有影片資訊
    with console.status("[cyan]正在載入影片資訊...[/cyan]"):
        result = yutu.get_video_details(video_id)

    if not result.success:
        display_error(result.error or "無法取得影片資訊")
        return

    items = result.data if isinstance(result.data, list) else result.data.get("items", [])
    if not items:
        display_error("找不到此影片")
        return

    video = items[0]
    snippet = video.get("snippet", {})
    status = video.get("status", {})

    current_title = snippet.get("title", "")
    current_description = snippet.get("description", "")
    current_tags = snippet.get("tags", [])
    current_privacy = status.get("privacyStatus", "private")

    console.print(f"\n[cyan]目前標題：[/cyan]{current_title}")
    console.print(f"[cyan]目前隱私：[/cyan]{current_privacy}")

    # 選擇要編輯的項目
    edit_choices = [
        questionary.Choice("📝 編輯標題", value="title", shortcut_key="1"),
        questionary.Choice("📄 編輯描述", value="description", shortcut_key="2"),
        questionary.Choice("🏷️  編輯標籤", value="tags", shortcut_key="3"),
        questionary.Choice("🔒 變更隱私狀態", value="privacy", shortcut_key="4"),
        questionary.Choice("⬅️  取消", value="cancel", shortcut_key="0"),
    ]

    edit_action = questionary.select(
        "選擇要編輯的項目：",
        choices=edit_choices,
        instruction="輸入數字或使用 ↑↓ 選擇",
        use_shortcuts=True,
    ).ask()

    if not edit_action or edit_action == "cancel":
        return

    new_title = None
    new_description = None
    new_tags = None
    new_privacy = None

    if edit_action == "title":
        new_title = questionary.text(
            "輸入新標題：",
            default=current_title,
            validate=lambda x: len(x.strip()) > 0 or "標題不能為空",
        ).ask()
        if not new_title or new_title == current_title:
            console.print("[yellow]標題未變更[/yellow]")
            return

    elif edit_action == "description":
        console.print("[dim]（輸入新描述，按 Enter 兩次結束）[/dim]")
        new_description = questionary.text(
            "輸入新描述：",
            default=current_description,
            multiline=True,
        ).ask()
        if new_description is None:
            return

    elif edit_action == "tags":
        current_tags_str = ", ".join(current_tags) if current_tags else ""
        console.print(f"[dim]目前標籤：{current_tags_str or '（無）'}[/dim]")
        tags_input = questionary.text(
            "輸入新標籤（以逗號分隔）：",
            default=current_tags_str,
        ).ask()
        if tags_input is None:
            return
        new_tags = [t.strip() for t in tags_input.split(",") if t.strip()]

    elif edit_action == "privacy":
        privacy_choices = [
            questionary.Choice("🌐 公開 (public)", value="public"),
            questionary.Choice("🔗 不公開 (unlisted)", value="unlisted"),
            questionary.Choice("🔒 私人 (private)", value="private"),
        ]
        new_privacy = questionary.select(
            "選擇隱私狀態：",
            choices=privacy_choices,
            default=current_privacy,
        ).ask()
        if not new_privacy or new_privacy == current_privacy:
            console.print("[yellow]隱私狀態未變更[/yellow]")
            return

    # 確認更新
    confirm = questionary.confirm("確定要更新影片嗎？").ask()
    if not confirm:
        console.print("[yellow]已取消更新[/yellow]")
        return

    # 執行更新
    with console.status("[cyan]正在更新影片...[/cyan]"):
        result = yutu.update_video(
            video_id,
            title=new_title,
            description=new_description,
            tags=new_tags,
            privacy=new_privacy,
        )

    if result.success:
        display_success("影片已更新！")
    else:
        display_error(result.error or "更新失敗")


def _delete_video(yutu: YutuCLI) -> None:
    """刪除影片"""
    video_input = questionary.text(
        "輸入要刪除的影片 ID 或 YouTube 網址（留空返回）：",
    ).ask()

    if not video_input:
        return

    video_id = extract_video_id(video_input.strip())

    # 先取得影片資訊以確認
    with console.status("[cyan]正在載入影片資訊...[/cyan]"):
        result = yutu.get_video_details(video_id)

    if not result.success:
        display_error(result.error or "無法取得影片資訊")
        return

    items = result.data if isinstance(result.data, list) else result.data.get("items", [])
    if not items:
        display_error("找不到此影片")
        return

    video = items[0]
    title = video.get("snippet", {}).get("title", "未知標題")

    # 顯示警告並確認
    display_warning(f"即將刪除影片：[bold]{title}[/bold]")
    console.print("[red]⚠️  此操作無法復原！[/red]\n")

    # 要求輸入 "DELETE" 確認
    confirm_text = questionary.text(
        "輸入 DELETE 確認刪除：",
    ).ask()

    if confirm_text != "DELETE":
        console.print("[yellow]已取消刪除[/yellow]")
        return

    # 執行刪除
    with console.status("[cyan]正在刪除影片...[/cyan]"):
        result = yutu.delete_video(video_id)

    if result.success:
        display_success(f"影片 [bold]{title}[/bold] 已刪除！")
    else:
        display_error(result.error or "刪除失敗")


def _rate_video(yutu: YutuCLI) -> None:
    """評分影片"""
    video_input = questionary.text(
        "輸入影片 ID 或 YouTube 網址（留空返回）：",
    ).ask()

    if not video_input:
        return

    video_id = extract_video_id(video_input.strip())

    # 取得目前評分狀態
    with console.status("[cyan]正在取得評分狀態...[/cyan]"):
        rating_result = yutu.get_video_rating(video_id)

    current_rating = "none"
    if rating_result.success and rating_result.data:
        items = rating_result.data if isinstance(rating_result.data, list) else rating_result.data.get("items", [])
        if items:
            current_rating = items[0].get("rating", "none")

    rating_display = {
        "like": "[green]👍 已按讚[/green]",
        "dislike": "[red]👎 已按倒讚[/red]",
        "none": "[dim]無評分[/dim]",
    }.get(current_rating, current_rating)

    console.print(f"\n目前評分狀態：{rating_display}\n")

    # 選擇評分操作
    rating_choices = [
        questionary.Choice("👍 按讚 (like)", value="like", shortcut_key="1"),
        questionary.Choice("👎 倒讚 (dislike)", value="dislike", shortcut_key="2"),
        questionary.Choice("❌ 移除評分 (none)", value="none", shortcut_key="3"),
        questionary.Choice("⬅️  取消", value="cancel", shortcut_key="0"),
    ]

    new_rating = questionary.select(
        "選擇評分操作：",
        choices=rating_choices,
        instruction="輸入數字或使用 ↑↓ 選擇",
        use_shortcuts=True,
    ).ask()

    if not new_rating or new_rating == "cancel":
        return

    if new_rating == current_rating:
        console.print("[yellow]評分狀態未變更[/yellow]")
        return

    # 執行評分
    with console.status("[cyan]正在更新評分...[/cyan]"):
        result = yutu.rate_video(video_id, new_rating)

    if result.success:
        action_text = {"like": "已按讚", "dislike": "已按倒讚", "none": "已移除評分"}.get(
            new_rating, new_rating
        )
        display_success(f"{action_text}！")
    else:
        display_error(result.error or "評分失敗")
