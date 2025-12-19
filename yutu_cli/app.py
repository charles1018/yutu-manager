"""主應用程式 - 互動式選單"""

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from yutu_cli import __version__
from yutu_cli.commands.captions import captions_menu
from yutu_cli.commands.channel import channel_menu
from yutu_cli.commands.comments import comments_menu
from yutu_cli.commands.playlists import playlist_menu
from yutu_cli.commands.search import search_menu
from yutu_cli.commands.videos import video_menu
from yutu_cli.config import get_config
from yutu_cli.utils.display import display_error, display_warning

console = Console()


def show_banner() -> None:
    """顯示歡迎橫幅"""
    banner = Text()
    banner.append("🎬 ", style="bold")
    banner.append("Yutu Manager", style="bold cyan")
    banner.append(f" v{__version__}", style="dim")
    banner.append("\n")
    banner.append("YouTube 頻道管理工具 - 互動式 CLI", style="dim")
    
    console.print(Panel(banner, border_style="cyan", padding=(0, 2)))


def check_config() -> bool:
    """檢查設定是否正確"""
    config = get_config()
    errors = config.validate_paths()
    
    if errors:
        for error in errors:
            display_error(error)
        
        console.print("\n[dim]請確認以下環境變數設定正確：[/dim]")
        console.print("[dim]  YUTU_CLI_PATH - yutu 執行檔路徑[/dim]")
        console.print("[dim]  YUTU_ROOT - yutu 配置目錄[/dim]")
        console.print("[dim]  YUTU_CREDENTIAL - OAuth 憑證檔案[/dim]")
        return False
    
    return True


def run_interactive() -> None:
    """執行互動式介面"""
    show_banner()
    
    # 檢查設定
    if not check_config():
        display_warning("設定有誤，部分功能可能無法正常運作")
    
    console.print()
    
    # 主選單選項
    menu_choices = [
        questionary.Choice("📋 播放清單管理", value="playlists"),
        questionary.Choice("🎥 影片管理", value="videos"),
        questionary.Choice("🔍 搜尋 YouTube", value="search"),
        questionary.Choice("📺 頻道資訊", value="channel"),
        questionary.Choice("💬 留言管理", value="comments"),
        questionary.Choice("📝 字幕管理", value="captions"),
        questionary.Separator(),
        questionary.Choice("🚪 離開", value="exit"),
    ]
    
    # 功能對應
    handlers = {
        "playlists": playlist_menu,
        "videos": video_menu,
        "search": search_menu,
        "channel": channel_menu,
        "comments": comments_menu,
        "captions": captions_menu,
    }
    
    # 主迴圈
    while True:
        try:
            choice = questionary.select(
                "請選擇功能",
                choices=menu_choices,
                instruction="使用 ↑↓ 鍵選擇，Enter 確認",
                qmark="🎬",
            ).ask()
            
            if choice is None or choice == "exit":
                console.print("\n[cyan]感謝使用 Yutu Manager，再見！👋[/cyan]\n")
                break
            
            handler = handlers.get(choice)
            if handler:
                console.print()  # 空行
                continue_running = handler()
                console.print()  # 空行
                
                if not continue_running:
                    break
        
        except KeyboardInterrupt:
            console.print("\n\n[cyan]感謝使用 Yutu Manager，再見！👋[/cyan]\n")
            break
        except Exception as e:
            display_error(f"發生錯誤：{e}")
