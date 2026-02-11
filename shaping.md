# YouTube Music Scraper — Shaping

## Frame

### Problem

- User has a large library of "liked" videos on YouTube, many of which are music
- No easy way to download liked music as MP3 files for offline/local use
- Manually downloading and converting is tedious and error-prone
- Re-running a download process risks duplicating files already on disk

### Outcome

- User can browse their YouTube liked videos in a terminal UI
- User can select which tracks to download as MP3
- Previously downloaded tracks are hidden so nothing is duplicated
- Process is repeatable — future runs only show new likes

---

## Requirements (R)

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | Download YouTube liked videos as MP3 files | Core goal |
| R1 | Authenticate via browser cookies (no OAuth / API keys) | Must-have |
| R2 | TUI displays liked videos for browsing and selection | Must-have |
| R3 | Previously downloaded tracks are hidden from the TUI list | Must-have |
| R4 | Track downloaded video IDs so future runs skip them automatically | Must-have |
| R5 | MP3 files stored in `downloads/` inside the project folder | Must-have |
| R6 | Convert video audio to MP3 format | Must-have |
| R7 | Show download progress in the TUI | Nice-to-have |
| R8 | Handle rate limiting / transient failures gracefully | Nice-to-have |

---

## A: Python + yt-dlp + Textual TUI

User specified this shape during the initial conversation. Single approach — detail below.

### Tech Stack Recommendation

**Python** is the clear best fit:
- **yt-dlp** — battle-tested YouTube scraper/downloader with built-in cookie extraction, MP3 conversion (via ffmpeg), and liked-videos playlist support (`LL` playlist)
- **Textual** — modern Python TUI framework (rich rendering, checkboxes, tables, progress bars)
- **JSON manifest** — simple file-based tracking (same pattern as twitter-bookmarks-scraper)

### Parts

| Part | Mechanism | Flag |
|------|-----------|:----:|
| **A1** | **Cookie auth** — yt-dlp's `--cookies-from-browser` or import a cookies.txt / JSON file exported from browser | |
| **A2** | **Liked videos fetch** — yt-dlp `extract_info()` on the `LL` (Liked Videos) playlist to get video metadata without downloading | |
| **A3** | **Manifest tracker** — JSON file (`downloads/manifest.json`) storing set of downloaded video IDs; loaded on startup, updated after each successful download | |
| **A4** | **TUI browse & select** — Textual app with a table/list of liked videos (title, channel, duration); checkboxes for multi-select; previously downloaded IDs filtered out before display | |
| **A5** | **Download & convert** — yt-dlp with `--extract-audio --audio-format mp3` for selected videos; progress callback wired to TUI progress bar | |
| **A6** | **MP3 file naming** — `{artist} - {title}.mp3` with sanitized filenames; stored in `downloads/` | |

### Key Design Decisions

**Why yt-dlp's `LL` playlist?**
YouTube stores every user's liked videos in a special playlist with ID `LL`. yt-dlp can enumerate this playlist using the user's cookies — no API key needed. This gives us metadata (title, channel, duration, video ID) without downloading anything.

**Why JSON manifest (not filesystem check)?**
- Video IDs are stable identifiers; filenames can change or be ambiguous
- Fast lookup (set membership) vs scanning directory
- Can store additional metadata (download date, original title) if needed later
- Same proven pattern as the twitter-bookmarks-scraper's `manifest.json`

**Why Textual?**
- Rich widget library (DataTable, Checkbox, ProgressBar, Header/Footer)
- Async-native (works well with yt-dlp's progress hooks)
- Modern look with minimal code
- Active maintenance and good docs

---

## Fit Check (R × A)

| Req | Requirement | Status | A |
|-----|-------------|--------|---|
| R0 | Download YouTube liked videos as MP3 files | Core goal | ✅ |
| R1 | Authenticate via browser cookies (no OAuth / API keys) | Must-have | ✅ |
| R2 | TUI displays liked videos for browsing and selection | Must-have | ✅ |
| R3 | Previously downloaded tracks are hidden from the TUI list | Must-have | ✅ |
| R4 | Track downloaded video IDs so future runs skip them automatically | Must-have | ✅ |
| R5 | MP3 files stored in `downloads/` inside the project folder | Must-have | ✅ |
| R6 | Convert video audio to MP3 format | Must-have | ✅ |
| R7 | Show download progress in the TUI | Nice-to-have | ✅ |
| R8 | Handle rate limiting / transient failures gracefully | Nice-to-have | ✅ |

**Notes:**
- R1: yt-dlp has native `--cookies-from-browser` support (Chrome, Firefox, Edge, etc.) — extracts cookies directly, no export step needed
- R6: yt-dlp + ffmpeg handles conversion natively via `--extract-audio --audio-format mp3`
- R7: yt-dlp provides progress hooks that can drive a Textual ProgressBar
- R8: yt-dlp has built-in retry logic; we add per-video error handling so one failure doesn't abort the batch

---

## Core Flow

```
1. Launch TUI
2. Extract cookies (yt-dlp --cookies-from-browser or cookies file)
3. Fetch liked videos metadata from LL playlist
4. Load manifest.json → get set of already-downloaded IDs
5. Filter out downloaded IDs → display remaining in TUI table
6. User browses, selects tracks via checkboxes
7. User confirms → download & convert selected tracks
8. For each track: download → convert to MP3 → save to downloads/ → update manifest
9. TUI shows progress bar per track + overall progress
10. Done → return to browse view (list now shorter)
```

---

## Dependencies

| Dependency | Purpose | Notes |
|------------|---------|-------|
| **yt-dlp** | YouTube scraping, downloading, audio extraction | Python package, actively maintained |
| **ffmpeg** | Audio conversion (yt-dlp shells out to it) | Must be installed on system PATH — **setup step required** |
| **textual** | TUI framework | Python package |

---

## Breadboard

### Places

| # | Place | Description |
|---|-------|-------------|
| P1 | TUI: Loading Screen | Initial screen during auth + fetch |
| P2 | TUI: Browse & Select | Main screen — table of liked videos with checkboxes |
| P3 | TUI: Downloading | Progress view during download/convert |
| P4 | Backend | Auth, yt-dlp operations, manifest I/O |

### UI Affordances

| # | Place | Affordance | Control | Wires Out | Returns To |
|---|-------|------------|---------|-----------|------------|
| U1 | P1 | Loading spinner + status text | render | — | — |
| U2 | P2 | Track table (title, channel, duration) | render | — | — |
| U3 | P2 | Row checkbox (per track) | click | toggles selection | — |
| U4 | P2 | Select All / Deselect All | click | → toggles all checkboxes | — |
| U5 | P2 | "Download Selected" button | click | → N8 | — |
| U6 | P2 | Selected count label | render | — | — |
| U7 | P2 | "Quit" button / key binding | click | exits app | — |
| U8 | P3 | Current track label | render | — | — |
| U9 | P3 | Per-track progress bar | render | — | — |
| U10 | P3 | Overall progress (X of Y) | render | — | — |
| U11 | P3 | Error/skip messages | render | — | — |
| U12 | P3 | "Done — press any key" prompt | click | → P2 | — |

### Code Affordances

| # | Place | Affordance | Control | Wires Out | Returns To |
|---|-------|------------|---------|-----------|------------|
| N1 | P4 | `extract_cookies(browser="chrome")` | call | — | → N2 |
| N2 | P4 | `fetch_liked_videos(cookies)` — yt-dlp `extract_info()` on LL playlist | call | — | → N4 |
| N3 | P4 | `load_manifest()` — read `downloads/manifest.json` | call | — | → S1 |
| N4 | P4 | `filter_new_tracks(videos, manifest)` — remove already-downloaded IDs | call | — | → P2 (U2) |
| N5 | P4 | `save_manifest(manifest)` — write updated manifest to disk | call | → S1 | — |
| N6 | P4 | `download_track(video_id, cookies)` — yt-dlp `--extract-audio --audio-format mp3` | call | → S2, → N5 | → N7 |
| N7 | P4 | `progress_hook(d)` — yt-dlp progress callback | call | — | → U9, U10 |
| N8 | P4 | `download_batch(selected_ids)` — loop over selected, call N6 per track | call | → N6 | → U8, U10, U11 |
| N9 | P4 | `sanitize_filename(artist, title)` — build safe MP3 filename | call | — | → N6 |
| N10 | P1 | `startup_sequence()` — orchestrates N1 → N2 → N3 → N4 → navigate to P2 | call | → N1, N2, N3, N4, → P2 | → U1 |

### Data Stores

| # | Place | Store | Description |
|---|-------|-------|-------------|
| S1 | P4 | `manifest.json` | `{ "downloaded": ["video_id_1", ...] }` |
| S2 | P4 | `downloads/` folder | MP3 files on disk |

---

## Slices

### Slice Summary

| # | Slice | Parts | Demo |
|---|-------|-------|------|
| V1 | Fetch & display liked videos | A1, A2, A3, A4 | "Launch app, see liked videos in a table" |
| V2 | Select & download | A4, A5, A6 | "Check tracks, hit download, MP3s appear" |
| V3 | Progress & polish | A5 (progress) | "Watch progress bars, return to browse view" |

### V1: Fetch & Display Liked Videos

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| U1 | Loading spinner + status | render | — | — |
| U2 | Track table (title, channel, duration) | render | — | — |
| N1 | `extract_cookies()` | call | — | → N2 |
| N2 | `fetch_liked_videos()` | call | — | → N4 |
| N3 | `load_manifest()` | call | — | → S1 |
| N4 | `filter_new_tracks()` | call | — | → U2 |
| N10 | `startup_sequence()` | call | → N1, N2, N3, N4 | → U1 |
| S1 | `manifest.json` | store | — | → N4 |

*Demo: "Launch the app, it authenticates with Chrome cookies, fetches your liked videos, and shows them in a table — minus anything already downloaded."*

### V2: Select & Download

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| U3 | Row checkbox | click | toggles selection | — |
| U5 | "Download Selected" button | click | → N8 | — |
| U6 | Selected count label | render | — | — |
| U8 | Current track label | render | — | — |
| U10 | Overall progress (X of Y) | render | — | — |
| U11 | Error/skip messages | render | — | — |
| N5 | `save_manifest()` | call | → S1 | — |
| N6 | `download_track()` | call | → S2, → N5 | — |
| N8 | `download_batch()` | call | → N6 | → U8, U10, U11 |
| N9 | `sanitize_filename()` | call | — | → N6 |
| S2 | `downloads/` folder | store | — | — |

*Demo: "Check three tracks, hit Download, MP3 files appear in downloads/, manifest updated."*

### V3: Progress & Polish

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| U4 | Select All / Deselect All | click | → toggles all | — |
| U7 | Quit button / key binding | click | exits app | — |
| U9 | Per-track progress bar | render | — | — |
| U12 | "Done — press any key" prompt | click | → P2 | — |
| N7 | `progress_hook()` | call | — | → U9 |

*Demo: "Watch real-time progress bars during download, see 'Done' message, press key to return to browse view with downloaded tracks removed."*

---

## Setup Prerequisites

1. **Install ffmpeg** — required for MP3 conversion. yt-dlp shells out to ffmpeg for audio extraction.
   - Windows: `winget install ffmpeg` or download from https://ffmpeg.org/download.html and add to PATH
   - Verify: `ffmpeg -version`
2. **Install Python dependencies** — `pip install yt-dlp textual`
