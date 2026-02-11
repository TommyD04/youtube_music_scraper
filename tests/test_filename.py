from scraper.filename import sanitize_filename


def test_basic_format():
    assert sanitize_filename("Artist", "Title") == "Artist - Title.mp3"


def test_strips_illegal_chars():
    result = sanitize_filename('Art<ist>', 'Ti:tle"/\\|?*')
    assert "<" not in result
    assert ">" not in result
    assert ":" not in result
    assert '"' not in result
    assert "/" not in result
    assert "\\" not in result
    assert "|" not in result
    assert "?" not in result
    assert "*" not in result
    assert result.endswith(".mp3")


def test_collapses_whitespace():
    result = sanitize_filename("Some   Artist", "Some   Title")
    assert "  " not in result
    assert result == "Some Artist - Some Title.mp3"


def test_empty_inputs():
    result = sanitize_filename("", "")
    assert result.endswith(".mp3")
    # Should be a UUID hex (32 chars) + .mp3
    assert len(result) == 36


def test_truncation():
    long_artist = "A" * 200
    long_title = "B" * 200
    result = sanitize_filename(long_artist, long_title)
    assert len(result) <= 200


def test_strips_dots():
    result = sanitize_filename("...Artist...", "...Title...")
    assert not result.startswith(".")
    # The .mp3 extension is expected at the end
    stem = result.removesuffix(".mp3")
    assert not stem.startswith(".")
    assert not stem.endswith(".")


def test_control_chars_stripped():
    result = sanitize_filename("Art\x00ist", "Ti\x1ftle")
    assert "\x00" not in result
    assert "\x1f" not in result
    assert result == "Artist - Title.mp3"
