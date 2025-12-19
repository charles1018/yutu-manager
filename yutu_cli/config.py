"""設定管理模組 - 處理環境變數和使用者偏好"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class YutuConfig(BaseSettings):
    """Yutu Manager 設定"""
    
    model_config = SettingsConfigDict(
        env_prefix="YUTU_",
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # yutu CLI 路徑
    cli_path: Path = Field(
        default=Path("/usr/local/bin/yutu"),
        description="yutu CLI 執行檔路徑",
    )
    
    # yutu 配置路徑
    root: Path = Field(
        default=Path.home() / ".config" / "yutu",
        description="yutu 配置根目錄",
    )
    
    credential: Optional[Path] = Field(
        default=None,
        description="OAuth 憑證檔案路徑",
    )
    
    cache_token: Optional[Path] = Field(
        default=None,
        description="Token 快取檔案路徑",
    )
    
    # 顯示設定
    max_results_default: int = Field(
        default=0,
        description="預設最大結果數（0 表示無限制）",
    )
    
    @property
    def credential_path(self) -> Path:
        """取得憑證檔案路徑"""
        return self.credential or self.root / "client_secret.json"
    
    @property
    def token_path(self) -> Path:
        """取得 token 快取路徑"""
        return self.cache_token or self.root / "youtube.token.json"
    
    def get_env_dict(self) -> dict[str, str]:
        """取得執行 yutu 時需要的環境變數"""
        return {
            "YUTU_ROOT": str(self.root),
            "YUTU_CREDENTIAL": str(self.credential_path),
            "YUTU_CACHE_TOKEN": str(self.token_path),
        }
    
    def validate_paths(self) -> list[str]:
        """驗證必要檔案是否存在，回傳錯誤訊息列表"""
        errors = []
        
        if not self.cli_path.exists():
            errors.append(f"找不到 yutu CLI: {self.cli_path}")
        
        if not self.credential_path.exists():
            errors.append(f"找不到憑證檔案: {self.credential_path}")
        
        return errors


# 全域設定實例
_config: Optional[YutuConfig] = None


def get_config() -> YutuConfig:
    """取得設定實例（單例模式）"""
    global _config
    if _config is None:
        _config = YutuConfig()
    return _config


def reset_config() -> None:
    """重設設定實例（用於測試）"""
    global _config
    _config = None
