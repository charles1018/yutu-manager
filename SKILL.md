---
name: yutu-manager
description: "Manage YouTube channel using yutu CLI. Use when user asks to: (1) List or manage playlists, (2) List videos in a playlist, (3) Add/remove videos from playlists, (4) Upload or manage videos, (5) Search YouTube, (6) Manage comments, captions, or channel settings. Trigger phrases include YouTube, playlist, my channel, my videos, yutu."
---

# yutu YouTube Manager

Manage YouTube channels via the `yutu` CLI tool.

## Critical: Getting Complete Results

**Always use `--maxResults 0` to get ALL items.** Without this flag, yutu uses a default limit.

```bash
# CORRECT - gets all 208 videos in playlist
yutu playlistItem list --playlistId "PLxxx" --maxResults 0 --output json

# WRONG - only gets default number of items
yutu playlistItem list --playlistId "PLxxx" --output json
```

## Output Formatting

yutu outputs JSON by default. Pipe to the formatter for human-readable lists:

```bash
yutu <command> --output json | python3 /path/to/yutu-manager/scripts/format_output.py [type]
```

> **Note**: Replace `/path/to/yutu-manager` with the actual installation path.

Types: `playlists`, `videos`, `playlistItems`, `search`, `channels`, `comments`, `captions`, `auto`

### Formatter Options

| Option | Description |
|--------|-------------|
| `-s, --simple` | **完整標題輸出**：只顯示完整標題和 YouTube 連結，不截斷 |
| `-o FILE, --output FILE` | 輸出到檔案而非終端 |
| `-f FILE, --file FILE` | 從檔案讀取 JSON 而非 stdin |

### Complete List Output (推薦用於大量影片)

當播放清單有大量影片時，使用 `--simple` 獲取完整標題：

```bash
# 終端顯示完整標題
yutu playlistItem list --playlistId "PLxxx" --maxResults 0 --output json | python3 format_output.py -s

# 儲存到檔案（推薦）
yutu playlistItem list --playlistId "PLxxx" --maxResults 0 --output json | python3 format_output.py -s -o playlist.txt
```

## Common Tasks

### List My Playlists

```bash
yutu playlist list --mine true --maxResults 0 --output json | python3 format_output.py playlists
```

### List ALL Videos in a Playlist

```bash
yutu playlistItem list --playlistId "PLxxxxxxxxxx" --maxResults 0 --output json | python3 format_output.py playlistItems
```

### Add Video to Playlist

```bash
yutu playlistItem insert --playlistId "PLxxxxxxxxxx" --videoId "xxxxxxxxxxx"
```

### Remove Video from Playlist

```bash
# Get playlistItem ID first:
yutu playlistItem list --playlistId "PLxxxxxxxxxx" --maxResults 0 --output json

# Delete by playlistItem ID (not video ID):
yutu playlistItem delete --ids "UExxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Delete multiple items at once:
yutu playlistItem delete --ids "ID1,ID2,ID3"
```

### Reorder Video in Playlist

```bash
yutu playlistItem update --id "UExxxxxxxxxxxxxxxxxxxxxxxxxxx" --position 0
```

### Search Videos

```bash
yutu search list --q "keyword" --maxResults 0 --output json | python3 format_output.py search
```

Filter options: `--type video`, `--order date|rating|viewCount|relevance`

### List My Videos

```bash
yutu search list --forMine true --type video --maxResults 0 --output json | python3 format_output.py search
```

### Get Video Details

```bash
yutu video list --ids "id1,id2" --parts snippet,statistics,contentDetails --output json | python3 format_output.py videos
```

### Upload Video

```bash
yutu video insert --file video.mp4 --title "Title" --description "Description" --categoryId 22 --privacy public --tags "tag1,tag2"
```

Required: `--file`, `--categoryId`, `--privacy` (public/private/unlisted)

### Update Video

```bash
yutu video update --id "xxxxxxxxxxx" --title "New Title" --description "New description"
```

### Delete Video

```bash
yutu video delete --id "xxxxxxxxxxx"
```

### Create Playlist

```bash
yutu playlist insert --title "Playlist Name" --description "Description" --privacy public
```

### Delete Playlist

```bash
yutu playlist delete --id "PLxxxxxxxxxx"
```

## Channel Management

```bash
# Get channel info
yutu channel list --mine true --parts snippet,statistics --output json | python3 format_output.py channels

# Update channel
yutu channel update --id "UCxxxxxxxxxx" --description "New description"
```

## Comments

```bash
# List comments on a video
yutu commentThread list --videoId "xxxxxxxxxxx" --maxResults 0 --output json | python3 format_output.py comments

# Post comment
yutu commentThread insert --videoId "xxxxxxxxxxx" --text "Comment text"

# Reply to comment
yutu comment insert --parentId "comment_id" --text "Reply text"
```

## Captions

```bash
# List captions
yutu caption list --videoId "xxxxxxxxxxx" --output json | python3 format_output.py captions

# Upload caption
yutu caption insert --videoId "xxxxxxxxxxx" --file captions.srt --language en --name "English"

# Download caption
yutu caption download --id "caption_id" --tfmt srt
```

## Tips

1. **Always use `--maxResults 0`** for complete results.

2. **Quota Management**: YouTube API has daily limits. Writes cost 50 units, reads cost 1-2 units.

3. **Parts Parameter**: Use `--parts` to request only needed data:
   - `snippet`: Basic info (title, description)
   - `statistics`: View/like counts
   - `contentDetails`: Duration, video IDs

4. **JSONPath Filtering**: Use `--jsonpath` for custom filtering:
   ```bash
   yutu playlist list --mine true --jsonpath "$.items[*].snippet.title"
   ```

## Environment Variables

**Required** - add to `~/.bashrc`:
```bash
export YUTU_ROOT="$HOME/.config/yutu"
export YUTU_CREDENTIAL="$HOME/.config/yutu/client_secret.json"
export YUTU_CACHE_TOKEN="$HOME/.config/yutu/youtube.token.json"
```

**IMPORTANT**: When running yutu commands in scripts, you may need to specify full paths:
```bash
YUTU_ROOT="$HOME/.config/yutu" YUTU_CREDENTIAL="$HOME/.config/yutu/client_secret.json" YUTU_CACHE_TOKEN="$HOME/.config/yutu/youtube.token.json" yutu <command>
```

First-time auth:
```bash
yutu auth --credential client_secret.json --cacheToken youtube.token.json
```
