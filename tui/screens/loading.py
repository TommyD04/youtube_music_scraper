import time

from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Label, ProgressBar


class LoadingScreen(Screen):
    CSS = """
    LoadingScreen {
        align: center middle;
    }
    #status {
        text-align: center;
        margin-top: 1;
    }
    ProgressBar {
        width: 50;
        margin-top: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._last_update = 0.0

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Label("Fetching liked videos...", id="status")
            with Center():
                yield ProgressBar(total=100, show_eta=False, id="fetch-progress")

    def on_mount(self) -> None:
        self.run_worker(self._startup, thread=True)

    def _on_fetch_progress(self, current: int, total: int) -> None:
        now = time.monotonic()
        if current == total or now - self._last_update >= 0.25:
            self._last_update = now
            self.app.call_from_thread(self._update_progress, current, total)

    def _update_progress(self, current: int, total: int) -> None:
        self.query_one("#status", Label).update(
            f"Fetching liked videos... {current} / {total}"
        )
        bar = self.query_one("#fetch-progress", ProgressBar)
        bar.update(total=total, progress=current)

    def _show_browse(self, tracks, already_count, tracker) -> None:
        from tui.screens.browse import BrowseScreen

        self.app.tracker = tracker
        self.app.push_screen(BrowseScreen(tracks, already_count, tracker))

    async def _startup(self) -> None:
        from scraper.tracker import ProgressTracker
        from scraper.ytdlp_client import fetch_liked_videos

        tracks = fetch_liked_videos(on_progress=self._on_fetch_progress)

        self.app.call_from_thread(
            self._update_progress, len(tracks), len(tracks)
        )

        tracker = ProgressTracker("downloads")
        tracker.load()

        new_tracks = [t for t in tracks if not tracker.is_downloaded(t.video_id)]
        already_count = len(tracks) - len(new_tracks)

        self.app.call_from_thread(self._show_browse, new_tracks, already_count, tracker)
