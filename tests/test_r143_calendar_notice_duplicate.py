"""R143: a dated event on the club calendar is not also a Community Notice."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

def _notice_html(title, date_line):
    return (
        "Community Notices"
        f'<td style="font-size:15px;line-height:18px;font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{title}</td>'
        f'<div class="ph-notice-date">{date_line}</div>'
        "Weekly Manager Update"
    )

def test_parse_dates():
    assert sr.r143_parse_dates("Luncheon: 12/2/26 · The Bayou Club") == ["2026-12-02"]
    assert sr.r143_parse_dates("Parade: December 12th, 2026 · Line up: 5:30 PM") == ["2026-12-12"]
    assert sr.r143_parse_dates("Tournament: Saturday, November 28, 2026") == ["2026-11-28"]

def test_names_same_event():
    assert sr.r143_names_same_event("Ladies Christmas Luncheon", "Ladies Christmas Luncheon")
    assert sr.r143_names_same_event("Palm Hill Annual Golf Cart Parade", "Christmas Golf Cart Parade")
    assert not sr.r143_names_same_event("Christmas Golf Cart Route", "Christmas Golf Cart Parade")
    assert sr.r143_names_same_event("Ladies Christmas Luncheon", "Ladies Luncheon")  # token subset; date check is separate

def test_luncheon_not_on_calendar_passes():
    html = _notice_html("Ladies Christmas Luncheon", "Luncheon: 12/2/26 · The Bayou Club")
    events = [
        {"name": "Ladies Luncheon", "date": "2026-12-16", "start": "11:30", "venue": "Off-Site", "status": "CONFIRMED"},
        {"name": "Ladies Luncheon", "date": "2026-11-18", "start": "11:30", "venue": "Off-Site", "status": "CANCELLED"},
    ]
    assert sr.calendar_notice_duplicate_problems(html, events) == []

def test_luncheon_on_calendar_same_date_fails():
    html = _notice_html("Ladies Christmas Luncheon", "Luncheon: 12/2/26 · The Bayou Club")
    events = [{"name": "Ladies Luncheon", "date": "2026-12-02", "start": "11:30", "venue": "Off-Site", "status": "CONFIRMED"}]
    hits = sr.calendar_notice_duplicate_problems(html, events)
    assert hits and "Ladies Christmas Luncheon" in hits[0] and "2026-12-02" in hits[0]

def test_keep_as_notice_allows_parade():
    html = _notice_html("Palm Hill Annual Golf Cart Parade", "Parade: December 12th, 2026")
    events = [{"name": "Christmas Golf Cart Parade", "date": "2026-12-12", "start": "17:30", "venue": "North Clubhouse Parking Lot", "status": "CONFIRMED"}]
    assert sr.calendar_notice_duplicate_problems(html, events)  # would fail without keep
    assert sr.calendar_notice_duplicate_problems(html, events, keep_as_notice={"Palm Hill Annual Golf Cart Parade"}) == []
