# 🎬 Yutu Manager

互動式 YouTube 頻道管理工具 - [yutu](https://github.com/eat-pray-ai/yutu) CLI 的友善介面。

## ✨ 功能

- 📋 **播放清單管理** - 建立、刪除、查看播放清單，新增/移除影片
- 🎥 **影片管理** - 列出、查看影片詳情
- 🔍 **搜尋** - 搜尋影片、播放清單、頻道
- 📺 **頻道資訊** - 查看頻道統計資料
- 💬 **留言管理** - 即將推出
- 📝 **字幕管理** - 即將推出

## 📦 安裝

### 前置需求

- [uv](https://github.com/astral-sh/uv) - Python 套件管理器
- [yutu](https://github.com/eat-pray-ai/yutu) - YouTube CLI 工具（需先完成 OAuth 認證）

### 安裝步驟

```bash
cd ~/dev/tools/claude/yutu-manager
uv sync
```

## 🚀 使用方法

```bash
# 啟動互動式介面
uv run yutu-manager

# 查看版本
uv run yutu-manager --version
```

### 全域安裝（可選）

```bash
uv tool install -e ~/dev/tools/claude/yutu-manager

# 之後可直接執行
yutu-manager
```

## ⚙️ 環境變數

確保 `~/.bashrc` 有以下設定：

```bash
export YUTU_ROOT="$HOME/.config/yutu"
export YUTU_CREDENTIAL="$HOME/.config/yutu/client_secret.json"
export YUTU_CACHE_TOKEN="$HOME/.config/yutu/youtube.token.json"
```

## 📁 專案結構

```
yutu-manager/
├── pyproject.toml          # 專案配置（uv + hatchling）
├── SKILL.md                # Claude Code 技能定義
├── scripts/
│   └── format_output.py    # yutu 輸出格式化腳本
└── yutu_cli/               # 互動式 CLI 套件
    ├── app.py              # 主應用程式
    ├── config.py           # 設定管理
    ├── commands/           # 功能模組
    │   ├── playlists.py    # 播放清單
    │   ├── videos.py       # 影片管理
    │   ├── search.py       # 搜尋
    │   └── channel.py      # 頻道資訊
    └── utils/
        ├── yutu.py         # yutu CLI 包裝器
        └── display.py      # 美化輸出
```

## 📖 截圖

```
🎬 Yutu Manager v0.1.0
YouTube 頻道管理工具 - 互動式 CLI
═══════════════════════════════════

🎬 請選擇功能
 ▸ 📋 播放清單管理
   🎥 影片管理
   🔍 搜尋 YouTube
   📺 頻道資訊
   💬 留言管理
   📝 字幕管理
   ──────────────
   🚪 離開
```

## 📄 授權

MIT License
