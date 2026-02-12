# YouTube Music Scraper

A terminal UI for downloading your YouTube liked videos as MP3 files. Built with Python, yt-dlp, and Textual.

## Prerequisites

1. **Python 3.10+**

2. **ffmpeg** — required for converting audio to MP3

   ```
   winget install Gyan.FFmpeg
   ```

   Restart your terminal after installing, then verify:

   ```
   ffmpeg -version
   ```

3. **Node.js** — required by yt-dlp to solve YouTube's JavaScript challenges

   ```
   winget install OpenJS.NodeJS.LTS
   ```

4. **A YouTube cookies.txt file** — the app uses a Netscape-format cookie file for authentication. To export one:
   1. Install the [Cookie-Editor](https://cookie-editor.com/) browser extension
   2. Go to [youtube.com](https://www.youtube.com) and make sure you're logged in
   3. Open Cookie-Editor, click **Export**, and select **Netscape HTTP Cookie File** format
   4. Save the file as `cookies.txt` in the project root

## Setup

```bash
git clone https://github.com/TommyD04/youtube_music_scraper.git
cd youtube_music_scraper
pip install -r requirements.txt
```

Place your exported `cookies.txt` in the project root before running.

## Usage

```bash
python app.py
```

On launch, the app fetches your liked videos from YouTube and displays any that haven't been downloaded yet. Select tracks, then press `d` to download.

### Key Bindings

| Key | Action |
|-----|--------|
| `Enter` | Toggle track selection |
| `a` | Select all tracks |
| `n` | Deselect all tracks |
| `d` | Download selected tracks |
| `q` | Quit |

After downloads complete, press any key to return to the track list.

## Downloads & Deduplication

- MP3 files are saved to `downloads/` in the project folder
- `downloads/manifest.json` tracks which videos have been downloaded — future runs automatically hide those tracks
- Do not delete `manifest.json` unless you want to re-download everything

## Troubleshooting

### "Requested format is not available"

YouTube requires yt-dlp to solve JavaScript signature challenges to access audio streams. If you see this error:

1. Make sure **Node.js** is installed (`node --version`)
2. Make sure **yt-dlp-ejs** is installed (`pip install yt-dlp-ejs`) — this provides the challenge solver scripts that yt-dlp needs alongside the JS runtime

### "Authenticating" or fetch seems stuck

Fetching the liked videos playlist is slow for large libraries. With 500+ liked videos, expect 1-2 minutes. The progress bar shows how many tracks have been fetched.

### Cookies expire

YouTube cookies last weeks to months. If the app starts failing with authentication errors, re-export your `cookies.txt` using Cookie-Editor.

## Running Tests

```bash
pytest tests/
```
