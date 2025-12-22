"""播放清單管理功能"""

from typing import Optional

import questionary

from yutu_cli.utils.display import (
    console,
    display_error,
    display_playlist_items,
    display_playlists,
    display_success,
    display_warning,
)
from yutu_cli.utils.youtube_utils import extract_video_id
from yutu_cli.utils.yutu import YutuCLI, get_yutu


def playlist_menu() -> bool:
    """播放清單管理選單
    
    Returns:
        True 繼續主選單，False 結束程式
    """
    yutu = get_yutu()
    
    choices = [
        questionary.Choice("1. 📋 列出我的播放清單", value="list"),
        questionary.Choice("2. 👁️  查看播放清單內容", value="view"),
        questionary.Choice("3. ➕ 新增播放清單", value="create"),
        questionary.Choice("4. ➕ 新增影片到播放清單", value="add_video"),
        questionary.Choice("5. ➖ 從播放清單移除影片", value="remove_video"),
        questionary.Choice("6. 🗑️  刪除播放清單", value="delete"),
        questionary.Choice("0. ⬅️  返回主選單", value="back"),
    ]
    
    while True:
        action = questionary.select(
            "📋 播放清單管理",
            choices=choices,
            instruction="使用 ↑↓ 鍵選擇，Enter 確認",
        ).ask()
        
        if action is None or action == "back":
            return True
        
        if action == "list":
            _list_playlists(yutu)
        elif action == "view":
            _view_playlist(yutu)
        elif action == "create":
            _create_playlist(yutu)
        elif action == "add_video":
            _add_video_to_playlist(yutu)
        elif action == "remove_video":
            _remove_video_from_playlist(yutu)
        elif action == "delete":
            _delete_playlist(yutu)


def _list_playlists(yutu: YutuCLI) -> Optional[list]:
    """列出播放清單並回傳項目列表"""
    with console.status("[cyan]正在載入播放清單...[/cyan]"):
        result = yutu.list_my_playlists()
    
    if not result.success:
        display_error(result.error or "無法取得播放清單")
        return None
    
    display_playlists(result.data)
    # result.data 可能是 dict 或 list
    if isinstance(result.data, list):
        return result.data
    return result.data.get("items", []) if result.data else []


def _select_playlist(yutu: YutuCLI, prompt: str = "選擇播放清單") -> Optional[dict]:
    """讓使用者選擇一個播放清單"""
    items = _list_playlists(yutu)
    if not items:
        return None
    
    choices = [
        questionary.Choice(
            f"{item.get('snippet', {}).get('title', '無標題')} ({item.get('contentDetails', {}).get('itemCount', 0)} 部影片)",
            value=item,
        )
        for item in items
    ]
    choices.append(questionary.Choice("⬅️  取消", value=None))
    
    return questionary.select(prompt, choices=choices).ask()


def _view_playlist(yutu: YutuCLI) -> None:
    """查看播放清單內容"""
    playlist = _select_playlist(yutu, "選擇要查看的播放清單")
    if not playlist:
        return
    
    playlist_id = playlist.get("id")
    playlist_title = playlist.get("snippet", {}).get("title", "")
    
    with console.status(f"[cyan]正在載入「{playlist_title}」...[/cyan]"):
        result = yutu.list_playlist_items(playlist_id)
    
    if not result.success:
        display_error(result.error or "無法取得播放清單內容")
        return
    
    display_playlist_items(result.data, playlist_title)


def _create_playlist(yutu: YutuCLI) -> None:
    """建立新播放清單"""
    title = questionary.text(
        "播放清單標題：",
        validate=lambda x: len(x.strip()) > 0 or "標題不能為空",
    ).ask()
    
    if not title:
        return
    
    description = questionary.text(
        "播放清單描述（可選）：",
    ).ask() or ""
    
    privacy = questionary.select(
        "隱私設定：",
        choices=[
            questionary.Choice("🌐 公開", value="public"),
            questionary.Choice("🔗 不公開（有連結可存取）", value="unlisted"),
            questionary.Choice("🔒 私人", value="private"),
        ],
    ).ask()
    
    if not privacy:
        return
    
    with console.status("[cyan]正在建立播放清單...[/cyan]"):
        result = yutu.create_playlist(title, description, privacy)
    
    if result.success:
        display_success(f"已建立播放清單「{title}」")
    else:
        display_error(result.error or "建立失敗")


def _add_video_to_playlist(yutu: YutuCLI) -> None:
    """新增影片到播放清單"""
    playlist = _select_playlist(yutu, "選擇目標播放清單")
    if not playlist:
        return
    
    video_id = questionary.text(
        "輸入影片 ID 或 YouTube 網址：",
        validate=lambda x: len(x.strip()) > 0 or "請輸入影片 ID",
    ).ask()
    
    if not video_id:
        return
    
    # 從網址提取 video ID
    video_id = extract_video_id(video_id.strip())
    playlist_id = playlist.get("id")
    playlist_title = playlist.get("snippet", {}).get("title", "")
    
    with console.status("[cyan]正在新增影片...[/cyan]"):
        result = yutu.add_to_playlist(playlist_id, video_id)
    
    if result.success:
        display_success(f"已將影片新增至「{playlist_title}」")
    else:
        display_error(result.error or "新增失敗")


def _remove_video_from_playlist(yutu: YutuCLI) -> None:
    """從播放清單移除影片"""
    playlist = _select_playlist(yutu, "選擇播放清單")
    if not playlist:
        return
    
    playlist_id = playlist.get("id")
    playlist_title = playlist.get("snippet", {}).get("title", "")
    
    # 取得播放清單項目
    with console.status(f"[cyan]正在載入「{playlist_title}」...[/cyan]"):
        result = yutu.list_playlist_items(playlist_id)
    
    if not result.success:
        display_error(result.error or "無法取得播放清單內容")
        return
    
    # result.data 可能是 dict 或 list
    if isinstance(result.data, list):
        items = result.data
    else:
        items = result.data.get("items", []) if result.data else []
    if not items:
        display_warning("播放清單是空的")
        return
    
    # 讓使用者選擇要移除的影片
    choices = [
        questionary.Choice(
            f"{item.get('snippet', {}).get('title', '無標題')}",
            value=item,
        )
        for item in items
    ]
    choices.append(questionary.Choice("⬅️  取消", value=None))
    
    selected = questionary.select("選擇要移除的影片", choices=choices).ask()
    if not selected:
        return
    
    video_title = selected.get("snippet", {}).get("title", "")
    playlist_item_id = selected.get("id")  # 注意：這是 playlistItem ID
    
    # 確認刪除
    confirm = questionary.confirm(
        f"確定要從「{playlist_title}」移除「{video_title}」嗎？",
        default=False,
    ).ask()
    
    if not confirm:
        return
    
    with console.status("[cyan]正在移除影片...[/cyan]"):
        result = yutu.remove_from_playlist(playlist_item_id)
    
    if result.success:
        display_success(f"已從「{playlist_title}」移除「{video_title}」")
    else:
        display_error(result.error or "移除失敗")


def _delete_playlist(yutu: YutuCLI) -> None:
    """刪除播放清單"""
    playlist = _select_playlist(yutu, "選擇要刪除的播放清單")
    if not playlist:
        return
    
    playlist_title = playlist.get("snippet", {}).get("title", "")
    playlist_id = playlist.get("id")
    video_count = playlist.get("contentDetails", {}).get("itemCount", 0)
    
    # 確認刪除
    display_warning(f"將刪除「{playlist_title}」（包含 {video_count} 部影片）")
    confirm = questionary.confirm(
        "確定要刪除嗎？此操作無法復原！",
        default=False,
    ).ask()
    
    if not confirm:
        return
    
    with console.status("[cyan]正在刪除播放清單...[/cyan]"):
        result = yutu.delete_playlist(playlist_id)
    
    if result.success:
        display_success(f"已刪除播放清單「{playlist_title}」")
    else:
        display_error(result.error or "刪除失敗")
