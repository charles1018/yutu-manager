"""頻道資訊功能"""

import questionary
from rich.console import Console

from yutu_cli.utils.display import display_channel_info, display_error
from yutu_cli.utils.yutu import get_yutu

console = Console()


def channel_menu() -> bool:
    """頻道資訊選單
    
    Returns:
        True 繼續主選單，False 結束程式
    """
    yutu = get_yutu()
    
    choices = [
        questionary.Choice("1. 📊 查看我的頻道", value="view"),
        questionary.Choice("0. ⬅️  返回主選單", value="back"),
    ]
    
    while True:
        action = questionary.select(
            "📺 頻道資訊",
            choices=choices,
            instruction="使用 ↑↓ 鍵選擇，Enter 確認",
        ).ask()
        
        if action is None or action == "back":
            return True
        
        if action == "view":
            _view_my_channel(yutu)


def _view_my_channel(yutu) -> None:
    """查看我的頻道資訊"""
    with console.status("[cyan]正在載入頻道資訊...[/cyan]"):
        result = yutu.get_my_channel()
    
    if not result.success:
        display_error(result.error or "無法取得頻道資訊")
        return
    
    display_channel_info(result.data)
