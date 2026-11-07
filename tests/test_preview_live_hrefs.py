"""R115: the nested live preview gets absolute page URLs; the R96 local review copy and Oct 25 sync stay byte copies."""
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import check_preview_send_stamp as s

PAGE = s.PAGE
SAMPLE = (
    '<a href="2026-11-06-weekly-manager-update.html">Read Full Update →</a>'
    '<a href="2026-11-06-weekly-manager-update.html?listen=1">Listen</a>'
    '<a href="2026-11-08-all-events-by-date.html">See the All Events List</a>'
    '<a href="2026-11-21-thanksgiving-friendsgiving-dance.html">More →</a>'
    '<a href="archive/community-stories.html">Story Archives →</a>'
    '<a href="tel:+15188662079">518-866-2079</a>'
    '<a href="https://www.palmhillcountryclub.net/calendar-1/">Calendar</a>'
    '<a href="https://palmhillnews.vercel.app/pages/archive/main.html">Archives</a>'
    '<script>var href = "keep.html";</script>'
)

def test_absolutize_matches_send_shape():
    out = s.absolutize_live_preview(SAMPLE)
    assert s.relative_page_hrefs(out) == []
    for name in (
        "2026-11-06-weekly-manager-update.html",
        "2026-11-06-weekly-manager-update.html?listen=1",
        "2026-11-08-all-events-by-date.html",
        "2026-11-21-thanksgiving-friendsgiving-dance.html",
        "archive/community-stories.html",
    ):
        assert f'href="{PAGE}{name}"' in out
        assert f'href="{name}"' not in out
    assert 'href="tel:+15188662079"' in out
    assert 'href="https://www.palmhillcountryclub.net/calendar-1/"' in out
    assert 'href="https://palmhillnews.vercel.app/pages/archive/main.html"' in out
    assert '<script>var href = "keep.html";</script>' in out
    assert s.absolutize_live_preview(out) == out

def test_oct25_sync_is_byte_copy_and_local_file_stays():
    body = b'<p class="ph-cal-check">Calendar check - October 25, 3:35 PM</p><a href="story.html">More</a>'
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        local = t / "local" / "PHNEWS-2026-10-25-preview.html"
        local.parent.mkdir()
        local.write_bytes(body)
        repo = t / "repo"
        (repo / "pages/previews/2026-10-25").mkdir(parents=True)
        dst = s.sync(local, repo, "2026-10-25")
        assert dst.read_bytes() == body == local.read_bytes()
        (repo / "pages/previews/2026-11-08").mkdir(parents=True)
        live = s.sync(local, repo, "2026-11-08")
        assert local.read_bytes() == body
        text = live.read_text(encoding="utf-8")
        assert 'href="story.html"' not in text
        assert f'href="{PAGE}story.html"' in text
        assert s.relative_page_hrefs(text) == []

if __name__ == "__main__":
    test_absolutize_matches_send_shape()
    test_oct25_sync_is_byte_copy_and_local_file_stays()
    print("preview live href tests OK")
