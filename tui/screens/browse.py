from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from scraper.models import Track
from scraper.tracker import ProgressTracker


class BrowseScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "download", "Download"),
        ("a", "select_all", "Select All"),
        ("n", "deselect_all", "Deselect All"),
    ]

    CSS = """
    #info {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
        color: $text-muted;
    }
    #empty-message {
        text-align: center;
        margin-top: 3;
        color: $text-muted;
    }
    #selected-count {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    #download-btn {
        dock: bottom;
        width: 100%;
    }
    """

    def __init__(
        self, tracks: list[Track], already_downloaded: int, tracker: ProgressTracker
    ) -> None:
        super().__init__()
        self.tracks = tracks
        self.already_downloaded = already_downloaded
        self.tracker = tracker
        self.selected: set[str] = set()
        self._track_by_row: dict = {}
        self._check_col = None

    def compose(self) -> ComposeResult:
        yield Header()
        if self.tracks:
            yield DataTable(id="tracks-table", cursor_type="row")
        else:
            yield Label("No new tracks to display.", id="empty-message")
        yield Button("Download Selected", id="download-btn", disabled=True)
        yield Label("0 selected", id="selected-count")
        yield Label(self._info_text(), id="info")
        yield Footer()

    def on_mount(self) -> None:
        self._populate_table()

    def _populate_table(self) -> None:
        if not self.tracks:
            return
        table = self.query_one("#tracks-table", DataTable)
        table.clear(columns=True)
        self._check_col, *_ = table.add_columns("✓", "Title", "Channel", "Duration")
        self._track_by_row = {}
        for track in self.tracks:
            row_key = table.add_row(
                "[ ]", track.title, track.channel, track.duration_str, key=track.video_id
            )
            self._track_by_row[row_key] = track

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#tracks-table", DataTable)
        video_id = str(event.row_key.value)

        if video_id in self.selected:
            self.selected.discard(video_id)
            table.update_cell(event.row_key, self._check_col, "[ ]")
        else:
            self.selected.add(video_id)
            table.update_cell(event.row_key, self._check_col, "[X]")

        count = len(self.selected)
        self.query_one("#selected-count", Label).update(f"{count} selected")
        self.query_one("#download-btn", Button).disabled = count == 0

    def action_quit(self) -> None:
        self.app.exit()

    def action_download(self) -> None:
        if not self.selected:
            return
        selected_tracks = [t for t in self.tracks if t.video_id in self.selected]

        from tui.screens.download import DownloadScreen

        self.app.push_screen(DownloadScreen(selected_tracks, self.tracker))

    def action_select_all(self) -> None:
        if not self.tracks:
            return
        table = self.query_one("#tracks-table", DataTable)
        for track in self.tracks:
            self.selected.add(track.video_id)
            table.update_cell(track.video_id, self._check_col, "[X]")
        self._update_selection_ui()

    def action_deselect_all(self) -> None:
        if not self.tracks:
            return
        table = self.query_one("#tracks-table", DataTable)
        for track in self.tracks:
            self.selected.discard(track.video_id)
            table.update_cell(track.video_id, self._check_col, "[ ]")
        self._update_selection_ui()

    def _update_selection_ui(self) -> None:
        count = len(self.selected)
        self.query_one("#selected-count", Label).update(f"{count} selected")
        self.query_one("#download-btn", Button).disabled = count == 0

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-btn":
            self.action_download()

    def on_screen_resume(self) -> None:
        self.tracks = [t for t in self.tracks if not self.tracker.is_downloaded(t.video_id)]
        self.selected.clear()
        self._populate_table()

        count_label = self.query_one("#selected-count", Label)
        count_label.update("0 selected")
        self.query_one("#download-btn", Button).disabled = True
        self.query_one("#info", Label).update(self._info_text())

        if not self.tracks:
            try:
                self.query_one("#tracks-table", DataTable).remove()
            except Exception:
                pass
            # Check if empty message already exists
            try:
                self.query_one("#empty-message", Label)
            except Exception:
                self.mount(Label("No new tracks to display.", id="empty-message"), before="#download-btn")

    def _info_text(self) -> str:
        new = len(self.tracks)
        already = self.already_downloaded
        if already:
            return f"{new} new tracks ({already} already downloaded)"
        return f"{new} tracks"
