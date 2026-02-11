import re
import uuid


def sanitize_filename(artist: str, title: str) -> str:
    """Create a safe MP3 filename from artist and title."""
    raw = f"{artist} - {title}"

    # Strip characters illegal on Windows and control chars
    raw = re.sub(r'[<>:"/\\|?*]', "", raw)
    raw = re.sub(r"[\x00-\x1f]", "", raw)

    # Collapse whitespace
    raw = re.sub(r"\s+", " ", raw).strip()

    # Strip leading/trailing dots and dashes
    raw = raw.strip(".- ")

    # Truncate (leave room for .mp3)
    max_stem = 200 - 4  # 4 for ".mp3"
    raw = raw[:max_stem].rstrip()

    if not raw:
        raw = uuid.uuid4().hex

    return f"{raw}.mp3"
