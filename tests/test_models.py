from scraper.models import Track


def test_duration_str_minutes():
    t = Track(video_id="abc", title="Song", channel="Artist", duration=185)
    assert t.duration_str == "3:05"


def test_duration_str_hours():
    t = Track(video_id="abc", title="Song", channel="Artist", duration=3661)
    assert t.duration_str == "1:01:01"


def test_duration_str_zero():
    t = Track(video_id="abc", title="Song", channel="Artist", duration=0)
    assert t.duration_str == "0:00"


def test_duration_str_exact_minute():
    t = Track(video_id="abc", title="Song", channel="Artist", duration=60)
    assert t.duration_str == "1:00"


def test_duration_str_under_minute():
    t = Track(video_id="abc", title="Song", channel="Artist", duration=9)
    assert t.duration_str == "0:09"
