"""字幕管理功能"""

import os
from pathlib import Path
from typing import Optional

import questionary

from yutu_cli.utils.display import (
    console,
    display_captions,
    display_error,
    display_success,
    display_warning,
    format_language_name,
    truncate,
)
from yutu_cli.utils.yutu import YutuCLI, get_yutu


def captions_menu() -> bool:
    """字幕管理選單

    Returns:
        True 繼續主選單，False 結束程式
    """
    yutu = get_yutu()

    choices = [
        questionary.Choice("📋 列出影片字幕", value="list", shortcut_key="1"),
        questionary.Choice("📥 下載字幕", value="download", shortcut_key="2"),
        questionary.Choice("📤 上傳字幕", value="upload", shortcut_key="3"),
        questionary.Choice("🗑️  刪除字幕", value="delete", shortcut_key="4"),
        questionary.Choice("⬅️  返回主選單", value="back", shortcut_key="0"),
    ]

    while True:
        action = questionary.select(
            "📝 字幕管理",
            choices=choices,
            instruction="輸入數字或使用 ↑↓ 選擇，Enter 確認",
            use_shortcuts=True,
        ).ask()

        if action is None or action == "back":
            return True

        if action == "list":
            _list_video_captions(yutu)
        elif action == "download":
            _download_caption(yutu)
        elif action == "upload":
            _upload_caption(yutu)
        elif action == "delete":
            _delete_caption(yutu)


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


def _select_caption(
    yutu: YutuCLI, video_id: str, video_title: str
) -> Optional[dict]:
    """讓使用者選擇一個字幕軌道

    Args:
        yutu: YutuCLI 實例
        video_id: 影片 ID
        video_title: 影片標題

    Returns:
        選中的字幕資料，或 None
    """
    with console.status(f"[cyan]正在載入「{video_title}」的字幕...[/cyan]"):
        result = yutu.list_captions(video_id)

    if not result.success:
        display_error(result.error or "無法取得字幕")
        return None

    items = result.data if isinstance(result.data, list) else result.data.get("items", [])
    if not items:
        display_warning("此影片沒有字幕")
        return None

    display_captions(result.data, video_title)

    choices = [
        questionary.Choice(
            f"{format_language_name(item.get('snippet', {}).get('language', ''))} - "
            f"{item.get('snippet', {}).get('name', '') or '（預設）'}",
            value=item,
        )
        for item in items
    ]
    choices.append(questionary.Choice("⬅️  取消", value=None))

    return questionary.select("選擇字幕軌道", choices=choices).ask()


def _list_video_captions(yutu: YutuCLI) -> None:
    """列出影片的字幕"""
    video = _select_my_video(yutu, "選擇要查看字幕的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    with console.status(f"[cyan]正在載入「{video_title}」的字幕...[/cyan]"):
        result = yutu.list_captions(video_id)

    if not result.success:
        display_error(result.error or "無法取得字幕")
        return

    display_captions(result.data, video_title)


def _download_caption(yutu: YutuCLI) -> None:
    """下載字幕"""
    video = _select_my_video(yutu, "選擇要下載字幕的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    caption = _select_caption(yutu, video_id, video_title)
    if not caption:
        return

    caption_id = caption.get("id", "")
    lang_code = caption.get("snippet", {}).get("language", "unknown")

    # 選擇格式
    fmt = questionary.select(
        "選擇下載格式：",
        choices=[
            questionary.Choice("SRT（最常用）", value="srt"),
            questionary.Choice("VTT（WebVTT）", value="vtt"),
            questionary.Choice("SBV（YouTube 格式）", value="sbv"),
        ],
    ).ask()

    if not fmt:
        return

    # 選擇是否翻譯
    translate = questionary.confirm(
        "是否翻譯成其他語言？",
        default=False,
    ).ask()

    tlang = None
    if translate:
        tlang = questionary.text(
            "輸入目標語言代碼（如 en, ja, zh-TW）：",
            validate=lambda x: len(x.strip()) >= 2 or "請輸入有效的語言代碼",
        ).ask()

    # 設定檔案路徑
    default_filename = f"{video_title[:30]}_{lang_code}.{fmt}"
    # 清理檔名中的非法字元
    default_filename = "".join(c for c in default_filename if c not in r'<>:"/\|?*')

    file_path = questionary.text(
        "儲存檔名：",
        default=default_filename,
    ).ask()

    if not file_path:
        return

    # 確保使用絕對路徑
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)

    with console.status("[cyan]正在下載字幕...[/cyan]"):
        result = yutu.download_caption(caption_id, file_path, fmt, tlang)

    if result.success:
        display_success(f"字幕已下載至：{file_path}")
    else:
        display_error(result.error or "下載失敗")


def _upload_caption(yutu: YutuCLI) -> None:
    """上傳字幕"""
    display_warning("上傳字幕將消耗 400 API 配額，請謹慎使用！")

    video = _select_my_video(yutu, "選擇要上傳字幕的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    # 輸入字幕檔案路徑
    file_path = questionary.path(
        "選擇字幕檔案（支援 SRT/VTT/SBV）：",
        validate=lambda x: Path(x).exists() or "檔案不存在",
    ).ask()

    if not file_path:
        return

    # 驗證副檔名
    ext = Path(file_path).suffix.lower()
    if ext not in [".srt", ".vtt", ".sbv"]:
        display_error("不支援的檔案格式，請使用 SRT、VTT 或 SBV 格式")
        return

    # 選擇語言
    lang_choices = [
        questionary.Choice("繁體中文 (zh-TW)", value="zh-TW"),
        questionary.Choice("英文 (en)", value="en"),
        questionary.Choice("日文 (ja)", value="ja"),
        questionary.Choice("韓文 (ko)", value="ko"),
        questionary.Choice("簡體中文 (zh-CN)", value="zh-CN"),
        questionary.Choice("其他...", value="other"),
    ]

    language = questionary.select(
        "選擇字幕語言：",
        choices=lang_choices,
    ).ask()

    if not language:
        return

    if language == "other":
        language = questionary.text(
            "輸入語言代碼（如 es, fr, de）：",
            validate=lambda x: len(x.strip()) >= 2 or "請輸入有效的語言代碼",
        ).ask()
        if not language:
            return

    # 字幕名稱（可選）
    name = questionary.text(
        "字幕名稱（可留空使用預設）：",
    ).ask()

    # 是否為草稿
    is_draft = questionary.confirm(
        "是否設為草稿？（草稿不會公開顯示）",
        default=False,
    ).ask()

    # 確認
    console.print("\n[bold]準備上傳字幕[/bold]")
    console.print(f"  影片：{video_title}")
    console.print(f"  檔案：{file_path}")
    console.print(f"  語言：{format_language_name(language)} ({language})")
    if name:
        console.print(f"  名稱：{name}")
    console.print(f"  狀態：{'草稿' if is_draft else '已發布'}")
    console.print()

    confirm = questionary.confirm(
        "確定要上傳嗎？（消耗 400 API 配額）",
        default=False,
    ).ask()

    if not confirm:
        return

    with console.status("[cyan]正在上傳字幕...[/cyan]"):
        result = yutu.insert_caption(video_id, file_path, language, name or "", is_draft)

    if result.success:
        display_success("字幕已上傳成功！")
    else:
        display_error(result.error or "上傳失敗")


def _delete_caption(yutu: YutuCLI) -> None:
    """刪除字幕"""
    video = _select_my_video(yutu, "選擇要刪除字幕的影片")
    if not video:
        return

    video_id = _get_video_id_from_selection(video)
    video_title = video.get("snippet", {}).get("title", "")

    caption = _select_caption(yutu, video_id, video_title)
    if not caption:
        return

    caption_id = caption.get("id", "")
    lang_code = caption.get("snippet", {}).get("language", "")
    caption_name = caption.get("snippet", {}).get("name", "") or "（預設）"

    # 確認刪除
    display_warning("刪除字幕後無法復原！")
    confirm = questionary.confirm(
        f"確定要刪除 {format_language_name(lang_code)} - {caption_name} 嗎？",
        default=False,
    ).ask()

    if not confirm:
        return

    with console.status("[cyan]正在刪除字幕...[/cyan]"):
        result = yutu.delete_caption(caption_id)

    if result.success:
        display_success("字幕已刪除！")
    else:
        display_error(result.error or "刪除失敗")
