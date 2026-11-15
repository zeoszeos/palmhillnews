#!/usr/bin/env python3
"""R133: no Sent-date line under a notice title; the Sent date is in smaller print (16px; body 18px)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import notice_page as npg
import style_rules as sr

SENT = "Tuesday, Nov 10, 2026, 12:20 PM ET"
OLD = ('<div class="hd"><h1 class="ph-section" style="margin:0">Taste of Golf Instructions</h1><a class="ph-listen" href="#">Listen</a></div>\n'
       f'<p class="ph-meta">{SENT}</p>\n'
       '<div class="ph-row ph-alt"><div class="ph-detail"><strong>Subject:</strong> Taste of Golf Instructions<br>'
       f'<strong>From:</strong> Palm Hill Webmaster<br><strong>Sent:</strong> {SENT}</div></div>\n'
       '<div class="ph-row"><div class="ph-detail">These are the initial instructions for all participants of Taste of Golf.</div></div>')
MEETING = ('<h1 class="ph-section">Golf Committee</h1>\n<p class="ph-meta">Tuesday, Oct 13, 2026 • 2:00 PM • South Clubhouse Boardroom</p>\n'
           '<div class="ph-row ph-alt"><div class="ph-detail"><strong>Subject:</strong> Golf Committee<br><strong>From:</strong> Palm Hill Webmaster<br>'
           '<strong>Sent:</strong> Thursday, Oct 8, 2026, 5:39 PM ET</div></div>')


def test_old_page_is_caught():
    hits = npg.sent_date_problems(OLD)
    assert any("smaller" in h for h in hits) and any("event date" in h for h in hits)


def test_fix_drops_date_line_and_shrinks_sent_date():
    f = npg.fix_sent_date(OLD)
    assert npg.sent_date_problems(f) == []
    assert '<p class="ph-meta">' not in f
    assert f'<strong>Sent:</strong> <span class="ph-sent-date" style="{npg.SENT_DATE_STYLE}">{SENT}</span>' in f
    assert "Taste of Golf Instructions</h1>" in f and ">Listen</a>" in f
    assert "These are the initial instructions" in f
    assert npg.fix_sent_date(f) == f


def test_meeting_date_line_is_kept():
    f = npg.fix_sent_date(MEETING)
    assert '<p class="ph-meta">Tuesday, Oct 13, 2026 • 2:00 PM • South Clubhouse Boardroom</p>' in f
    assert npg.sent_date_problems(f) == []


def test_template_renders_new_format():
    html = npg.render("Taste of Golf Instructions", SENT, [("p", "These are the initial instructions for all participants of Taste of Golf.")])
    assert npg.sent_date_problems(html) == []
    assert '<p class="ph-meta">' not in html
    assert "font-size:16px" in npg.SENT_DATE_STYLE


def test_pages_without_sent_box_are_skipped():
    assert npg.sent_date_problems("<h1>x</h1><p class=\"ph-meta\">Monday</p>") == []
    assert npg.fix_sent_date("<p>x</p>") == "<p>x</p>"


def test_live_notice_pages_pass():
    assert sr.notice_sent_date_problems(ROOT) == []


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except Exception as e:
                failed += 1; print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
