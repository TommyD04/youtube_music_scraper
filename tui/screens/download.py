from textual.app import ComposeResult
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
        yield ProgressBar(total=len(self.tracks), show_eta=False)
        yield Label("", id="error-log")
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._download_batch, thread=True)

    def _download_batch(self) -> None:
        total = len(self.tracks)
        errors: list[str] = []

        for i, track in enumerate(self.tracks):
            current_label = self.query_one("#current-track", Label)
            current_label.update(f"Downloading: {track.title}")
            progress_label = self.query_one("#progress-label", Label)
            progress_label.update(f"{i} / {total}")

            try:
                download_track(track.video_id, track.channel, track.title)
                self.tracker.mark_downloaded(track.video_id)
                self.tracker.save()
            except Exception as e:
                errors.append(f"{track.title}: {e}")
                error_label = self.query_one("#error-log", Label)
                error_label.update("\n".join(errors))

            self.query_one(ProgressBar).update(progress=i + 1)

        progress_label = self.query_one("#progress-label", Label)
        progress_label.update(f"{total} / {total}")

        current_label = self.query_one("#current-track", Label)
        if errors:
            current_label.update(
                f"Done! {total - len(errors)} succeeded, {len(errors)} failed. Press Escape to go back."
            )
        else:
            current_label.update("All downloads complete! Press Escape to go back.")

        self._done = True

    def action_go_back(self) -> None:
        self.app.pop_screen()
