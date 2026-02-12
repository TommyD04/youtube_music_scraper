import os
import re
from collections.abc import Callable

import yt_dlp

from scraper.filename import sanitize_filename
from scraper.models import Track

LIKED_VIDEOS_URL = "https://www.youtube.com/playlist?list=LL"
DEFAULT_COOKIE_FILE = "cookies.txt"
_JS_RUNTIMES = {"node": {}}

_ITEM_PROGRESS_RE = re.compile(r"Downloading item (\d+) of (\d+)")


class _FetchLogger:
    """Captures yt-dlp log messages and relays playlist fetch progress."""

    def __init__(self, on_progress: Callable[[int, int], None] | None = None):
        self._on_progress = on_progress

    def debug(self, msg: str) -> None:
        if self._on_progress:
            m = _ITEM_PROGRESS_RE.search(msg)
            if m:
                self._on_progress(int(m.group(1)), int(m.group(2)))

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        pass


def fetch_liked_videos(
    cookie_file: str = DEFAULT_COOKIE_FILE,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[Track]:
    """Fetch liked videos metadata using yt-dlp with cookie file auth."""
    ydl_opts = {
        "cookiefile": cookie_file,
        "extract_flat": "in_playlist",
        "js_runtimes": _JS_RUNTIMES,
        "logger": _FetchLogger(on_progress),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(LIKED_VIDEOS_URL, download=False)

    tracks = []
    for entry in info.get("entries", []):
        tracks.append(
            Track(
                video_id=entry["id"],
                title=entry.get("title", "Unknown"),
                channel=entry.get("uploader", entry.get("channel", "Unknown")),
                duration=entry.get("duration") or 0,
            )
        )
    return tracks


def download_track(
    video_id: str,
    artist: str,
    title: str,
    downloads_dir: str = "downloads",
    cookie_file: str = DEFAULT_COOKIE_FILE,
    progress_hook: Callable | None = None,
) -> str:
    """Download a YouTube video as MP3. Returns the output filepath."""
    filename = sanitize_filename(artist, title)
    # yt-dlp adds the extension via postprocessor, so strip .mp3 from outtmpl
    stem = filename.removesuffix(".mp3")
    output_path = os.path.join(downloads_dir, stem)

    ydl_opts = {
        "cookiefile": cookie_file,
        "js_runtimes": _JS_RUNTIMES,
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
    }

    if progress_hook is not None:
        ydl_opts["progress_hooks"] = [progress_hook]

    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return os.path.join(downloads_dir, filename)
