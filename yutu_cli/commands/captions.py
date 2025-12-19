"""字幕管理功能（佔位）"""

import questionary
from rich.console import Console

from yutu_cli.utils.display import display_warning

console = Console()


def captions_menu() -> bool:
    """字幕管理選單
    
    Returns:
        True 繼續主選單，False 結束程式
    """
    display_warning("字幕管理功能即將推出！")
    
    questionary.press_any_key_to_continue("按任意鍵返回...").ask()
    
    return True
