"""R150: calendar-sourced event locations use the club calendar wording (display map), not a conflicting email/verbal name."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

def _row(title, loc, date_line):
    return (
        f'''<td valign="top" align="left" style="font-size:15px;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">{title}</td>'''
        f'''<td valign="top" align="right" style="font-size:14px;color:#666666;text-align:right;padding-top:1px;">{loc}</td></tr>'''
        f'''<tr><td valign="top" align="left" colspan="2" style="font-size:14px;color:#666666;text-align:left;padding-top:2px;padding-right:10px;">{date_line}</td></tr>'''
    )

def _html(title="Fireside Chat", loc="North Clubhouse", date_line="Wednesday, Dec 2, 2026 • 7:00 PM"):
    return (
        "><span>Events - This Week</span>"
        + _row(title, loc, date_line)
        + "><span>Community Notices</span>"
    )

EVENTS = [{"name": "Fireside Chat", "date": "2026-12-02", "venue": "North Main Hall", "status": "CONFIRMED"}]


def test_display_map_north_main_hall():
    assert sr.calendar_display_venue("North Main Hall") == "North Clubhouse"
    assert sr.calendar_display_venue("South Main Hall") == "South Clubhouse"
    assert sr.calendar_display_venue("Pro Shop") == "Pro Shop"


def test_calendar_wording_passes():
    assert sr.calendar_location_problems(_html(), EVENTS) == []


def test_email_wording_fails():
    # Tony said "North Main Hall"; the calendar display wording is "North Clubhouse".
    html = _html(loc="North Main Hall")
    hits = sr.calendar_location_problems(html, EVENTS)
    assert hits and "North Main Hall" in hits[0] and "North Clubhouse" in hits[0]


def test_wrong_building_fails():
    hits = sr.calendar_location_problems(_html(loc="South Clubhouse"), EVENTS)
    assert hits and "South Clubhouse" in hits[0]


def test_override_allows_different_wording():
    html = _html(loc="North Main Hall")
    assert sr.calendar_location_problems(html, EVENTS, overrides={"Fireside Chat": "North Main Hall"}) == []
    assert sr.calendar_location_problems(html, EVENTS, overrides={("Fireside Chat", "2026-12-02"): "North Main Hall"}) == []


def test_unmapped_venue_passthrough():
    ev = [{"name": "Free Golf Lessons", "date": "2026-12-06", "venue": "Pro Shop", "status": "CONFIRMED"}]
    html = _html("Free Golf Lessons", "Pro Shop", "Sunday, Dec 6, 2026 • 10:00 AM")
    assert sr.calendar_location_problems(html, ev) == []


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f):
            f()
            print("PASS", n)
