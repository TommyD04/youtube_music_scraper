from textual.app import ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ProgressBar

from scraper.models import Track
from scraper.tracker import ProgressTracker
from scraper.ytdlp_client import download_track


class DownloadScreen(Screen):
    BINDINGS = [("escape", "go_back", "Back")]

    CSS = """
    #current-track {
        margin: 1 2;
    }
    #progress-label {
        margin: 0 2;
    }
    #track-progress-label {
        margin: 0 2;
        color: $text-muted;
    }
    #error-log {
        margin: 1 2;
        color: $error;
    }
    ProgressBar {
        margin: 1 2;
    }
    """

    def __init__(self, tracks: list[Track], tracker: ProgressTracker) -> None:
        super().__init__()
        self.tracks = tracks
        self.tracker = tracker
        self._done = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Starting downloads...", id="current-track")
        yield Label(f"0 / {len(self.tracks)}", id="progress-label")
        yield ProgressBar(total=len(self.tracks), show_eta=False, id="batch-progress")
        yield Label("Track progress:", id="track-progress-label")
        yield ProgressBar(total=100, show_eta=False, id="track-progress")
        yield Label("", id="error-log")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._download_batch, thread=True)

    def _progress_hook(self, d: dict) -> None:
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                pct = min(downloaded * 100 / total, 100)
            else:
                pct = 0
            self.call_from_thread(self._update_track_progress, pct)
        elif d.get("status") == "finished":
            self.call_from_thread(self._update_track_progress, 100)

    def _update_track_progress(self, pct: float) -> None:
        self.query_one("#track-progress", ProgressBar).update(progress=pct)

    def _download_batch(self) -> None:
        total = len(self.tracks)
        errors: list[str] = []

        for i, track in enumerate(self.tracks):
            self.call_from_thread(self._update_track_label, track.title, i, total)
            self.call_from_thread(self._update_track_progress, 0)

            try:
                download_track(
                    track.video_id,
                    track.channel,
                    track.title,
                    progress_hook=self._progress_hook,
                )
                self.tracker.mark_downloaded(track.video_id)
                self.tracker.save()
            except Exception as e:
                errors.append(f"{track.title}: {e}")
                error_label = self.query_one("#error-log", Label)
                error_label.update("\n".join(errors))

            self.query_one("#batch-progress", ProgressBar).update(progress=i + 1)

        progress_label = self.query_one("#progress-label", Label)
        progress_label.update(f"{total} / {total}")

        current_label = self.query_one("#current-track", Label)
        if errors:
            current_label.update(
                f"Done! {total - len(errors)} succeeded, {len(errors)} failed. Press any key to go back."
            )
        else:
            current_label.update("All downloads complete! Press any key to go back.")

        self._done = True

    def _update_track_label(self, title: str, index: int, total: int) -> None:
        self.query_one("#current-track", Label).update(f"Downloading: {title}")
        self.query_one("#progress-label", Label).update(f"{index} / {total}")

    def on_key(self, event: Key) -> None:
        if self._done:
            event.prevent_default()
            self.app.pop_screen()

    def action_go_back(self) -> None:
        self.app.pop_screen()
