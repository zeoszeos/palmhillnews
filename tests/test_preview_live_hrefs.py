"""R115 / R115b: the nested live preview gets absolute page URLs; every live preview from Nov 1 on is checked;
the R96 local review copy and Oct 25 sync stay byte copies."""
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



def _stamp(html, cal="Calendar check - November 8, 3:58 PM", mast="3:58 PM"):
    return f'<p class="ph-cal-check">{cal}</p><span style="white-space:nowrap;">{mast}</span>' + html


def test_check_scans_every_nov1_plus_preview_not_just_the_issue():
    """R115b: a clean November 8 check still fails if the committed November 1 preview has relative hrefs."""
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        repo = t / "repo"
        # October 25 may keep relative sibling hrefs (byte copy); the scan must ignore it.
        (repo / "pages/previews/2026-10-25").mkdir(parents=True)
        (repo / "pages/previews/2026-10-25/PHNEWS-2026-10-25-preview.html").write_text(
            _stamp('<a href="story.html">More</a>', "Calendar check - October 25, 3:35 PM", "3:35 PM"),
            encoding="utf-8",
        )
        (repo / "pages/previews/2026-11-01").mkdir(parents=True)
        (repo / "pages/2026-11-01-all-events-by-date.html").parent.mkdir(parents=True, exist_ok=True)
        (repo / "pages/2026-11-01-all-events-by-date.html").write_text("<p>ok</p>", encoding="utf-8")
        (repo / "pages/previews/2026-11-01/PHNEWS-2026-11-01-preview.html").write_text(
            _stamp(
                '<a href="2026-11-01-all-events-by-date.html">See the All Events List</a>',
                "Calendar check - November 1, 12:00 PM",
                "12:00 PM",
            ),
            encoding="utf-8",
        )
        (repo / "pages/previews/2026-11-08").mkdir(parents=True)
        (repo / "pages/story.html").write_text("<p>ok</p>", encoding="utf-8")
        (repo / "pages/previews/2026-11-08/PHNEWS-2026-11-08-preview.html").write_text(
            _stamp(f'<a href="{PAGE}story.html">More</a>'),
            encoding="utf-8",
        )
        work = t / "work"
        work.mkdir()
        fails, _ = s.check("2026-11-08", work, repo)
        r115 = [f for f in fails if f.startswith("R115")]
        assert r115, fails
        assert "2026-11-01" in r115[0] and "relative" in r115[0], r115
        # After the same rewrite used on the committed November 1 preview, the scan passes.
        nov1 = repo / "pages/previews/2026-11-01/PHNEWS-2026-11-01-preview.html"
        nov1.write_text(s.absolutize_live_preview(nov1.read_text(encoding="utf-8")), encoding="utf-8")
        fails, _ = s.check("2026-11-08", work, repo)
        assert [f for f in fails if f.startswith("R115")] == []
        assert s.relative_page_hrefs(nov1.read_text(encoding="utf-8")) == []


def test_check_fails_when_absolute_page_target_is_missing():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        repo = t / "repo"
        (repo / "pages/previews/2026-11-08").mkdir(parents=True)
        (repo / "pages/previews/2026-11-08/PHNEWS-2026-11-08-preview.html").write_text(
            _stamp(f'<a href="{PAGE}missing-page.html">More</a>'),
            encoding="utf-8",
        )
        fails, _ = s.check("2026-11-08", t / "work", repo)
        r115 = [f for f in fails if f.startswith("R115")]
        assert r115 and "no file under pages/" in r115[0] and "missing-page.html" in r115[0], r115


def test_committed_nov1_and_nov8_live_previews_are_absolute_and_resolve():
    """Lock the files on disk: November 1 and November 8 must stay clean after the R115b rewrite."""
    repo = Path(__file__).resolve().parents[1]
    fails = s.check_live_preview_hrefs(repo)
    assert fails == [], fails
    for issue in ("2026-11-01", "2026-11-08"):
        text = (repo / f"pages/previews/{issue}/PHNEWS-{issue}-preview.html").read_text(encoding="utf-8")
        assert s.relative_page_hrefs(text) == []
        assert s.missing_page_targets(text, repo) == []

if __name__ == "__main__":
    test_absolutize_matches_send_shape()
    test_oct25_sync_is_byte_copy_and_local_file_stays()
    test_check_scans_every_nov1_plus_preview_not_just_the_issue()
    test_check_fails_when_absolute_page_target_is_missing()
    test_committed_nov1_and_nov8_live_previews_are_absolute_and_resolve()
    print("preview live href tests OK")
