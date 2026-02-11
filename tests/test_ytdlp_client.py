from unittest.mock import MagicMock, patch

from scraper.models import Track
from scraper.ytdlp_client import download_track, fetch_liked_videos


def _make_entry(video_id="vid1", title="Test Song", uploader="Test Artist", duration=200):
    return {"id": video_id, "title": title, "uploader": uploader, "duration": duration}


@patch("scraper.ytdlp_client.yt_dlp.YoutubeDL")
def test_parse_playlist_entries(mock_ydl_cls):
    mock_ydl = MagicMock()
    mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.return_value = {
        "entries": [
            _make_entry("v1", "Song A", "Artist A", 180),
            _make_entry("v2", "Song B", "Artist B", 240),
        ]
    }

    tracks = fetch_liked_videos()

    assert len(tracks) == 2
    assert tracks[0] == Track("v1", "Song A", "Artist A", 180)
    assert tracks[1] == Track("v2", "Song B", "Artist B", 240)


@patch("scraper.ytdlp_client.yt_dlp.YoutubeDL")
def test_handles_missing_fields(mock_ydl_cls):
    mock_ydl = MagicMock()
    mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.return_value = {
        "entries": [
            {"id": "v1"},  # missing title, uploader, duration
            {"id": "v2", "channel": "Fallback Channel"},  # channel fallback
        ]
    }

    tracks = fetch_liked_videos()

    assert tracks[0].title == "Unknown"
    assert tracks[0].channel == "Unknown"
    assert tracks[0].duration == 0
    assert tracks[1].channel == "Fallback Channel"


@patch("scraper.ytdlp_client.yt_dlp.YoutubeDL")
def test_empty_playlist(mock_ydl_cls):
    mock_ydl = MagicMock()
    mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.return_value = {"entries": []}

    tracks = fetch_liked_videos()

    assert tracks == []


@patch("scraper.ytdlp_client.yt_dlp.YoutubeDL")
def test_download_track_calls_ydl_correctly(mock_ydl_cls):
    mock_ydl = MagicMock()
    mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)

    download_track("vid1", "Artist", "Title", downloads_dir="dl")

    # Verify constructor was called with correct opts
    opts = mock_ydl_cls.call_args[0][0]
    assert opts["format"] == "bestaudio/best"
    assert opts["cookiesfrombrowser"] == ("chrome",)

    # Verify postprocessor is FFmpegExtractAudio with mp3
    pp = opts["postprocessors"]
    assert len(pp) == 1
    assert pp[0]["key"] == "FFmpegExtractAudio"
    assert pp[0]["preferredcodec"] == "mp3"

    # Verify correct URL was downloaded
    mock_ydl.download.assert_called_once_with(["https://www.youtube.com/watch?v=vid1"])


@patch("scraper.ytdlp_client.yt_dlp.YoutubeDL")
def test_download_track_returns_path(mock_ydl_cls):
    mock_ydl = MagicMock()
    mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)

    result = download_track("vid1", "Artist", "Title", downloads_dir="downloads")

    assert result == "downloads\\Artist - Title.mp3" or result == "downloads/Artist - Title.mp3"
