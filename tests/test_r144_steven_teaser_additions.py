"""R144: Steven-supplied teaser additions stay recorded and do not rewrite the source."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

TITLE = "Spectrum Fiber Upgrade"
SOURCE = "Palm Hill has upgraded its Spectrum service to a Fiber solution"
ADDITION = "Schedule installation by December 1, 2026."
TEASER = SOURCE + ". " + ADDITION
REC = {TITLE: {"source": SOURCE, "addition": ADDITION, "by": "Steven Leonowicz, Nov 23 2026: 2:05 AM ET keep-list; later approved schedule-by-December-1 framing (source wording)"}}

def _notice_html(title, teaser, date_line="Schedule installation by: December 1, 2026"):
    return (
        "Community Notices"
        f'<td style="font-size:15px;line-height:18px;font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{title}</td>'
        f'<div class="ph-notice-date">{date_line}</div>'
        f'<div style="font-size:15px;color:#333333;margin-top:3px;">{teaser} <a href="https://example/page.html">More →</a></div>'
        "Weekly Manager Update"
    )

def test_recorded_addition_passes():
    assert sr.steven_teaser_addition_problems({TITLE: TEASER}, REC, {TITLE: SOURCE}) == []

def test_missing_addition_fails():
    hits = sr.steven_teaser_addition_problems({TITLE: SOURCE}, REC)
    assert hits and ADDITION in hits[0]

def test_rewritten_source_fails():
    bad = "Palm Hill has upgraded its fiber service. Schedule installation by December 1, 2026."
    hits = sr.steven_teaser_addition_problems({TITLE: bad}, REC)
    assert any("source sentence is missing or rewritten" in h for h in hits)

def test_addition_on_unlabeled_page_fails():
    hits = sr.steven_teaser_addition_problems({TITLE: TEASER}, REC, {TITLE: SOURCE + " " + ADDITION})
    assert hits and "source notice page" in hits[0]

def test_incomplete_record_fails():
    hits = sr.steven_teaser_addition_problems({TITLE: TEASER}, {TITLE: {"addition": ADDITION}})
    assert hits and "must record" in hits[0]

def test_teaser_from_html():
    html = _notice_html(TITLE, TEASER)
    assert sr.r144_teaser_from_html(html, TITLE) == TEASER

def test_nov29_keep_list_exact():
    parts = []
    for title in sr.R144_NOV29_NOTICES:
        parts.append(_notice_html(title, "teaser text"))
    html = "Community Notices" + "".join(parts[i].split("Community Notices")[1].split("Weekly Manager Update")[0] for i in range(len(parts))) + "Weekly Manager Update"
    # simpler: one section with all seven titles
    body = "".join(
        f'<td style="font-size:15px;line-height:18px;font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{t}</td>'
        f'<div class="ph-notice-date">d</div>'
        for t in sr.R144_NOV29_NOTICES
    )
    html = "Community Notices" + body + "Weekly Manager Update"
    assert sr.r144_keep_list_problems("2026-11-29", html) == []
    assert sr.r144_keep_list_problems("2026-11-22", html) == []
    missing = "Community Notices" + body.replace("2027 South Rec Club Seeking Officers", "") + "Weekly Manager Update"
    hits = sr.r144_keep_list_problems("2026-11-29", missing)
    assert hits and "expected exactly" in hits[0]
