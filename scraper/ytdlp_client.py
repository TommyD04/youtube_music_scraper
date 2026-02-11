import os

import yt_dlp

from scraper.filename import sanitize_filename
from scraper.models import Track

LIKED_VIDEOS_URL = "https://www.youtube.com/playlist?list=LL"


def fetch_liked_videos(browser: str = "chrome") -> list[Track]:
    """Fetch liked videos metadata using yt-dlp with browser cookie auth."""
    ydl_opts = {
        "cookiesfrombrowser": (browser,),
        "extract_flat": "in_playlist",
        "quiet": True,
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
    browser: str = "chrome",
) -> str:
    """Download a YouTube video as MP3. Returns the output filepath."""
    filename = sanitize_filename(artist, title)
    # yt-dlp adds the extension via postprocessor, so strip .mp3 from outtmpl
    stem = filename.removesuffix(".mp3")
    output_path = os.path.join(downloads_dir, stem)

    ydl_opts = {
        "cookiesfrombrowser": (browser,),
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

    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return os.path.join(downloads_dir, filename)
