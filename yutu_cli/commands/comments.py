"""留言管理功能（佔位）"""

import questionary
from rich.console import Console

from yutu_cli.utils.display import display_warning

console = Console()


def comments_menu() -> bool:
    """留言管理選單
    
    Returns:
        True 繼續主選單，False 結束程式
    """
    display_warning("留言管理功能即將推出！")
    
    questionary.press_any_key_to_continue("按任意鍵返回...").ask()
    
    return True
