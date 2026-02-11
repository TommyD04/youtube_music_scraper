from textual.app import App

from tui.screens.loading import LoadingScreen


class MusicScraperApp(App):
    TITLE = "YouTube Music Scraper"

    def __init__(self) -> None:
        super().__init__()
        self.tracker = None

    def on_mount(self) -> None:
        self.push_screen(LoadingScreen())
