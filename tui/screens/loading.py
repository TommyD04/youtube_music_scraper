from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Label, LoadingIndicator


class LoadingScreen(Screen):
    CSS = """
    LoadingScreen {
        align: center middle;
    }
    #status {
        text-align: center;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield LoadingIndicator()
            with Center():
                yield Label("Fetching liked videos...", id="status")

    def on_mount(self) -> None:
        self.run_worker(self._startup, thread=True)

    async def _startup(self) -> None:
        from scraper.tracker import ProgressTracker
        from scraper.ytdlp_client import fetch_liked_videos
        from tui.screens.browse import BrowseScreen

        status = self.query_one("#status", Label)

        status.update("Authenticating with Chrome cookies...")
        tracks = fetch_liked_videos()

        status.update(f"Loaded {len(tracks)} liked videos. Checking downloads...")
        tracker = ProgressTracker("downloads")
        tracker.load()

        new_tracks = [t for t in tracks if not tracker.is_downloaded(t.video_id)]
        already_count = len(tracks) - len(new_tracks)

        self.app.tracker = tracker
        self.app.push_screen(BrowseScreen(new_tracks, already_count, tracker))
