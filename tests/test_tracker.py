import json
import os

from scraper.tracker import ProgressTracker


def test_load_nonexistent_manifest(tmp_path):
    tracker = ProgressTracker(str(tmp_path / "downloads"))
    tracker.load()
    assert not tracker.is_downloaded("anything")


def test_save_and_load_roundtrip(tmp_path):
    downloads = str(tmp_path / "downloads")
    tracker = ProgressTracker(downloads)
    tracker.load()
    tracker.mark_downloaded("vid1")
    tracker.mark_downloaded("vid2")
    tracker.save()

    tracker2 = ProgressTracker(downloads)
    tracker2.load()
    assert tracker2.is_downloaded("vid1")
    assert tracker2.is_downloaded("vid2")
    assert not tracker2.is_downloaded("vid3")


def test_is_downloaded(tmp_path):
    tracker = ProgressTracker(str(tmp_path / "downloads"))
    tracker.load()
    assert not tracker.is_downloaded("vid1")
    tracker.mark_downloaded("vid1")
    assert tracker.is_downloaded("vid1")
    assert not tracker.is_downloaded("vid2")


def test_creates_downloads_dir(tmp_path):
    downloads = str(tmp_path / "new_dir")
    assert not os.path.exists(downloads)
    ProgressTracker(downloads)
    assert os.path.isdir(downloads)


def test_manifest_json_format(tmp_path):
    downloads = str(tmp_path / "downloads")
    tracker = ProgressTracker(downloads)
    tracker.load()
    tracker.mark_downloaded("b_vid")
    tracker.mark_downloaded("a_vid")
    tracker.save()

    with open(os.path.join(downloads, "manifest.json")) as f:
        data = json.load(f)
    assert data["downloaded"] == ["a_vid", "b_vid"]  # sorted
