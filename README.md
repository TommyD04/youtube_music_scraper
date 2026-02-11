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

3. **Google Chrome with an active YouTube login** — the app reads cookies directly from Chrome for authentication. No API keys or OAuth setup required. Chrome must be closed when launching the app (yt-dlp needs exclusive access to the cookie database).

## Setup

```bash
git clone https://github.com/TommyD04/youtube_music_scraper.git
cd youtube_music_scraper
pip install -r requirements.txt
```

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

## Running Tests

```bash
pytest tests/
```
