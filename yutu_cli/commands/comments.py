"""留言管理功能"""

from typing import Optional

import questionary

from yutu_cli.utils.display import (
    console,
    display_comment_detail,
    display_comments,
    display_error,
    display_success,
    display_warning,
    truncate,
)
from yutu_cli.utils.yutu import YutuCLI, get_yutu


def comments_menu() -> bool:
    """留言管理選單

    Returns:
        True 繼續主選單，False 結束程式
    """
    yutu = get_yutu()

    choices = [
        questionary.Choice("📋 列出影片評論", value="list", shortcut_key="1"),
        questionary.Choice("💬 回覆評論", value="reply", shortcut_key="2"),
        questionary.Choice("🗑️  刪除評論", value="delete", shortcut_key="3"),
        questionary.Choice("✅ 審核評論", value="moderate", shortcut_key="4"),
        questionary.Choice("⬅️  返回主選單", value="back", shortcut_key="0"),
    ]

    while True:
        action = questionary.select(
            "💬 留言管理",
            choices=choices,
            instruction="輸入數字或使用 ↑↓ 選擇，Enter 確認",
            use_shortcuts=True,
        ).ask()

        if action is None or action == "back":
            return True

        if action == "list":
            _list_video_comments(yutu)
        elif action == "reply":
            _reply_to_comment(yutu)
        elif action == "delete":
            _delete_comment(yutu)
        elif action == "moderate":
            _moderate_comment(yutu)


def _select_my_video(yutu: YutuCLI, prompt: str = "選擇影片") -> Optional[dict]:
    """讓使用者選擇自己的一部影片

    Args:
        yutu: YutuCLI 實例
        prompt: 提示文字

    Returns:
        選中的影片資料，或 None
    """
    with console.status("[cyan]正在載入影片列表...[/cyan]"):
        result = yutu.list_my_videos(max_results=50)

    if not result.success:
        display_error(result.error or "無法取得影片列表")
        return None

    items = result.data if isinstance(result.data, list) else result.data.get("items", [])
    if not items:
        display_warning("沒有找到任何影片")
        return None

    choices = [
        questionary.Choice(
            truncate(item.get("snippet", {}).get("title", "無標題"), 60),
            value=item,
        )
        for item in items
    ]
    choices.append(questionary.Choice("⬅️  取消", value=None))

    return questionary.select(prompt, choices=choices).ask()


def _get_video_id_from_selection(video: dict) -> str:
    """從搜尋結果中提取 video ID

    Args:
        video: 搜尋結果項目

    Returns:
        影片 ID
    """
    # 搜尋結果的 ID 結構：{"kind": "youtube#video", "videoId": "xxx"}
    id_info = video.get("id", {})
    if isinstance(id_info, dict):
        return id_info.get("videoId", "")
    return str(id_info)


def _select_comment(
    yutu: YutuCLI, video_id: str, video_title: str
) -> Optional[dict]:
    """讓使用者選擇一則評論

    Args:
        yutu: YutuCLI 實例
        video_id: 影片 ID
        video_title: 影片標題

    Returns:
        選中的評論串資料，或 None
    """
    with console.status(f"[cyan]正在載入「{video_title}」的評論...[/cyan]"):
        result = yutu.list_comment_threads(video_id)

    if not result.success:
        display_error(result.error or "無法取得評論")
        return None

    items = result.data if isinstance(result.data, list) else result.data.get("items", [])
    if not items:
        display_warning("此影片沒有評論")
        return None

    display_comments(result.data, video_title)

    choices = [
        questionary.Choice(
            f"{truncate(item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {}).get('authorDisplayName', ''), 15)} - "
            f"{truncate(item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {}).get('textDisplay', ''), 40)}",
            value=item,
        )
        for item in items
    ]
    choices.append(questionary.Choice("⬅️  取消", value=None))

    return questionary.select("選擇評論", choices=choices).ask()


def _get_my_channel_id(yutu: YutuCLI) -> Optional[str]:
    """取得我的頻道 ID

    Args:
        yutu: YutuCLI 實例

    Returns:
        頻道 ID，或 None
    """
    result = yutu.get_my_channel()
    if not result.success:
        return None

    items = result.data if isinstance(result.data, list) else result.data.get("items", [])
    if items:
        return items[0].get("id")
    return None


def _list_video_comments(yutu: YutuCLI) -> None:
    """列出影片的評論"""
    video = _select_my_video(yutu, "選擇要查看評論的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    with console.status(f"[cyan]正在載入「{video_title}」的評論...[/cyan]"):
        result = yutu.list_comment_threads(video_id)

    if not result.success:
        display_error(result.error or "無法取得評論")
        return

    items = result.data if isinstance(result.data, list) else result.data.get("items", [])
    display_comments(result.data, video_title)

    if not items:
        return

    # 詢問是否查看詳情
    view_detail = questionary.confirm(
        "是否查看評論詳情？",
        default=False,
    ).ask()

    if view_detail:
        choices = [
            questionary.Choice(
                f"{truncate(item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {}).get('authorDisplayName', ''), 15)} - "
                f"{truncate(item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {}).get('textDisplay', ''), 30)}",
                value=item,
            )
            for item in items
        ]
        choices.append(questionary.Choice("⬅️  取消", value=None))

        selected = questionary.select("選擇要查看的評論", choices=choices).ask()
        if selected:
            display_comment_detail(selected)


def _reply_to_comment(yutu: YutuCLI) -> None:
    """回覆評論"""
    video = _select_my_video(yutu, "選擇要回覆評論的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    comment = _select_comment(yutu, video_id, video_title)
    if not comment:
        return

    # 顯示評論內容
    display_comment_detail(comment, include_replies=True)

    # 取得父評論 ID
    top_comment = comment.get("snippet", {}).get("topLevelComment", {})
    parent_id = top_comment.get("id")

    # 輸入回覆內容
    reply_text = questionary.text(
        "輸入回覆內容：",
        validate=lambda x: len(x.strip()) > 0 or "回覆不能為空",
    ).ask()

    if not reply_text:
        return

    # 取得頻道 ID
    with console.status("[cyan]正在準備回覆...[/cyan]"):
        channel_id = _get_my_channel_id(yutu)

    if not channel_id:
        display_error("無法取得頻道 ID")
        return

    # 確認送出
    confirm = questionary.confirm(
        "確定要發送回覆嗎？（消耗 50 API 配額）",
        default=True,
    ).ask()

    if not confirm:
        return

    with console.status("[cyan]正在發送回覆...[/cyan]"):
        result = yutu.reply_to_comment(video_id, parent_id, reply_text, channel_id)

    if result.success:
        display_success("回覆已發送！")
    else:
        display_error(result.error or "發送失敗")


def _delete_comment(yutu: YutuCLI) -> None:
    """刪除評論"""
    video = _select_my_video(yutu, "選擇要刪除評論的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    comment = _select_comment(yutu, video_id, video_title)
    if not comment:
        return

    # 顯示評論內容
    display_comment_detail(comment, include_replies=False)

    # 取得評論 ID
    top_comment = comment.get("snippet", {}).get("topLevelComment", {})
    comment_id = top_comment.get("id")
    author = top_comment.get("snippet", {}).get("authorDisplayName", "")

    # 確認刪除
    display_warning("刪除評論後無法復原！")
    confirm = questionary.confirm(
        f"確定要刪除 {author} 的評論嗎？",
        default=False,
    ).ask()

    if not confirm:
        return

    with console.status("[cyan]正在刪除評論...[/cyan]"):
        result = yutu.delete_comment(comment_id)

    if result.success:
        display_success("評論已刪除！")
    else:
        display_error(result.error or "刪除失敗")


def _moderate_comment(yutu: YutuCLI) -> None:
    """審核評論"""
    video = _select_my_video(yutu, "選擇要審核評論的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    comment = _select_comment(yutu, video_id, video_title)
    if not comment:
        return

    # 顯示評論內容
    display_comment_detail(comment, include_replies=False)

    # 取得評論 ID
    top_comment = comment.get("snippet", {}).get("topLevelComment", {})
    comment_id = top_comment.get("id")

    # 選擇審核狀態
    status = questionary.select(
        "選擇審核動作：",
        choices=[
            questionary.Choice("✅ 核准發布", value="published"),
            questionary.Choice("⏸️  保留審核", value="heldForReview"),
            questionary.Choice("❌ 拒絕", value="rejected"),
        ],
    ).ask()

    if not status:
        return

    # 是否封鎖作者（僅拒絕時可選）
    ban_author = False
    if status == "rejected":
        ban_author = questionary.confirm(
            "是否同時封鎖此作者？",
            default=False,
        ).ask()

    # 確認
    status_names = {
        "published": "發布",
        "heldForReview": "保留審核",
        "rejected": "拒絕",
    }
    confirm = questionary.confirm(
        f"確定要將評論設為「{status_names[status]}」嗎？",
        default=True,
    ).ask()

    if not confirm:
        return

    with console.status("[cyan]正在更新審核狀態...[/cyan]"):
        result = yutu.set_comment_moderation_status(comment_id, status, ban_author)

    if result.success:
        display_success(f"已將評論設為「{status_names[status]}」")
    else:
        display_error(result.error or "更新失敗")
