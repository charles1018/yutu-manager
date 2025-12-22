"""yutu CLI 包裝器 - 執行 yutu 命令並解析輸出"""

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Optional

from yutu_cli.config import get_config


@dataclass
class YutuResult:
    """yutu 命令執行結果"""
    success: bool
    data: Optional[dict | list] = None
    error: Optional[str] = None
    raw_output: str = ""


class YutuCLI:
    """yutu CLI 包裝器"""
    
    def __init__(self):
        self.config = get_config()
    
    def _build_command(
        self,
        resource: str,
        action: str,
        *,
        output_format: str = "json",
        max_results: Optional[int] = None,
        **kwargs,
    ) -> list[str]:
        """建構 yutu 命令"""
        cmd = [str(self.config.cli_path), resource, action]
        
        # 加入輸出格式
        cmd.extend(["--output", output_format])
        
        # 加入 maxResults（預設使用 0 取得所有結果）
        if max_results is not None:
            cmd.extend(["--maxResults", str(max_results)])
        elif self.config.max_results_default == 0:
            cmd.extend(["--maxResults", "0"])
        
        # 加入其他參數
        param_aliases: dict[str, str] = {}
        if resource == "search" and action == "list":
            # yutu 搜尋參數使用 --types（複數）而非 --type
            param_aliases["type"] = "types"
        for key, value in kwargs.items():
            if value is None:
                continue
            # 將 snake_case 轉換為 kebab-case（例如 max_results -> max-results）
            param_name = param_aliases.get(key, key).replace("_", "-")
            if isinstance(value, bool):
                if value:
                    cmd.extend([f"--{param_name}", "true"])
            else:
                cmd.extend([f"--{param_name}", str(value)])
        
        return cmd
    
    def run(
        self,
        resource: str,
        action: str,
        *,
        output_format: str = "json",
        max_results: Optional[int] = None,
        **kwargs,
    ) -> YutuResult:
        """執行 yutu 命令
        
        Args:
            resource: 資源類型（playlist, video, search 等）
            action: 動作（list, insert, delete 等）
            output_format: 輸出格式（json, yaml）
            max_results: 最大結果數（None 使用設定預設值）
            **kwargs: 其他參數
        
        Returns:
            YutuResult 物件
        """
        cmd = self._build_command(
            resource, action,
            output_format=output_format,
            max_results=max_results,
            **kwargs,
        )
        
        try:
            # 合併環境變數（確保繼承父程序環境變數）
            env = {**os.environ, **self.config.get_env_dict()}

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=120,  # 2 分鐘超時
            )
            
            if result.returncode != 0:
                return YutuResult(
                    success=False,
                    error=result.stderr or f"命令執行失敗（退出碼：{result.returncode}）",
                    raw_output=result.stdout,
                )
            
            # 解析 JSON 輸出
            if output_format == "json" and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    return YutuResult(
                        success=True,
                        data=data,
                        raw_output=result.stdout,
                    )
                except json.JSONDecodeError as e:
                    return YutuResult(
                        success=False,
                        error=f"JSON 解析錯誤: {e}",
                        raw_output=result.stdout,
                    )
            
            return YutuResult(
                success=True,
                raw_output=result.stdout,
            )
            
        except subprocess.TimeoutExpired:
            return YutuResult(
                success=False,
                error="命令執行超時（超過 120 秒）",
            )
        except FileNotFoundError:
            return YutuResult(
                success=False,
                error=f"找不到 yutu CLI: {self.config.cli_path}",
            )
        except Exception as e:
            return YutuResult(
                success=False,
                error=f"執行錯誤: {e}",
            )
    
    # === 便捷方法 ===
    
    def list_my_playlists(self, max_results: Optional[int] = None) -> YutuResult:
        """列出我的播放清單"""
        return self.run(
            "playlist", "list",
            mine=True,
            parts="snippet,contentDetails,status",
            max_results=max_results,
        )
    
    def list_playlist_items(
        self, playlist_id: str, max_results: Optional[int] = None
    ) -> YutuResult:
        """列出播放清單中的影片"""
        return self.run(
            "playlistItem", "list",
            playlistId=playlist_id,
            max_results=max_results,
        )
    
    def add_to_playlist(self, playlist_id: str, video_id: str) -> YutuResult:
        """新增影片到播放清單"""
        return self.run(
            "playlistItem", "insert",
            playlistId=playlist_id,
            videoId=video_id,
        )
    
    def remove_from_playlist(self, playlist_item_id: str) -> YutuResult:
        """從播放清單移除影片（注意：使用 playlistItem ID，不是 video ID）"""
        return self.run("playlistItem", "delete", ids=playlist_item_id)
    
    def search_videos(
        self,
        query: str,
        *,
        max_results: Optional[int] = None,
        order: str = "relevance",
    ) -> YutuResult:
        """搜尋影片"""
        return self.run(
            "search", "list",
            q=query,
            types="video",
            order=order,
            max_results=max_results,
        )
    
    def get_video_details(self, video_ids: str | list[str]) -> YutuResult:
        """取得影片詳情"""
        if isinstance(video_ids, list):
            video_ids = ",".join(video_ids)
        return self.run(
            "video", "list",
            ids=video_ids,
            parts="snippet,statistics,contentDetails,status",
        )
    
    def list_my_videos(self, max_results: Optional[int] = None) -> YutuResult:
        """列出我的影片"""
        return self.run(
            "search", "list",
            forMine=True,
            types="video",
            max_results=max_results,
        )
    
    def get_my_channel(self) -> YutuResult:
        """取得我的頻道資訊"""
        return self.run(
            "channel", "list",
            mine=True,
            parts="snippet,statistics",
        )
    
    def create_playlist(
        self, title: str, description: str = "", privacy: str = "private"
    ) -> YutuResult:
        """建立播放清單"""
        return self.run(
            "playlist", "insert",
            title=title,
            description=description,
            privacy=privacy,
        )
    
    def delete_playlist(self, playlist_id: str) -> YutuResult:
        """刪除播放清單"""
        return self.run("playlist", "delete", id=playlist_id)


# 全域實例
_yutu: Optional[YutuCLI] = None


def get_yutu() -> YutuCLI:
    """取得 YutuCLI 實例（單例模式）"""
    global _yutu
    if _yutu is None:
        _yutu = YutuCLI()
    return _yutu
