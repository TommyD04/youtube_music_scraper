import json
import os


class ProgressTracker:
    def __init__(self, downloads_dir: str):
        os.makedirs(downloads_dir, exist_ok=True)
        self._path = os.path.join(downloads_dir, "manifest.json")
        self._downloaded_ids: set[str] = set()

    def load(self):
        if os.path.isfile(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._downloaded_ids = set(data.get("downloaded", []))
        else:
            self._downloaded_ids = set()

    def is_downloaded(self, video_id: str) -> bool:
        return video_id in self._downloaded_ids

    def mark_downloaded(self, video_id: str):
        self._downloaded_ids.add(video_id)

    def save(self):
        data = {"downloaded": sorted(self._downloaded_ids)}
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
