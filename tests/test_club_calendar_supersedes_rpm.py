#!/usr/bin/env python3
"""R122 (Steven, Nov 12 2026): Tony's club calendar always supersedes the RPM calendar.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

CLUB = [
    {"name": "Board of Directors Meeting", "date": "2026-11-20", "time": "13:00", "status": "CONFIRMED"},
    {"name": "Communications Committee", "date": "2026-12-04", "time": "09:00", "status": "CONFIRMED"},
]
RPM = [
    {"name": "Board of Directors Meeting", "date": "2026-11-25", "time": "13:00"},
    {"name": "Communications Committee", "date": "2026-12-14", "time": "10:00"},
]

def _row(title, when):
    return (f'<td style="font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{title}</td>'
            f"<div>{when}</div>")

def _page(board="Friday, Nov 20, 2026 1:00 PM", comms="Friday, Dec 4, 2026 9:00 AM"):
    return (">Committee &amp; Board Meeting Schedules</span><table>"
            + _row("Board of Directors Meeting", board)
            + _row("Communications Committee", comms)
            + "</table>")

def test_club_dates_pass_when_rpm_differs():
    assert sr.club_calendar_supersedes_rpm_problems(_page(), CLUB, RPM) == []

def test_printed_rpm_board_date_fails():
    hits = sr.club_calendar_supersedes_rpm_problems(_page(board="Wednesday, Nov 25, 2026 1:00 PM"), CLUB, RPM)
    assert any("RPM date" in h and "2026-11-25" in h for h in hits), hits

def test_printed_rpm_comms_date_fails():
    hits = sr.club_calendar_supersedes_rpm_problems(_page(comms="Monday, Dec 14, 2026 10:00 AM"), CLUB, RPM)
    assert any("RPM date" in h and "2026-12-14" in h for h in hits), hits

def test_override_from_rpm_fails():
    hits = sr.club_calendar_supersedes_rpm_problems(
        _page(), CLUB, RPM, overrides={"Board of Directors Meeting": "November 25, 2026"})
    assert any("MTG_OVERRIDE" in h for h in hits), hits

def test_matching_rpm_is_ok():
    rpm = [{"name": "Board of Directors Meeting", "date": "2026-11-20", "time": "13:00"}]
    assert sr.club_calendar_supersedes_rpm_problems(_page(), CLUB, rpm) == []

if __name__ == "__main__":
    test_club_dates_pass_when_rpm_differs()
    test_printed_rpm_board_date_fails()
    test_printed_rpm_comms_date_fails()
    test_override_from_rpm_fails()
    test_matching_rpm_is_ok()
    print("R122 club-calendar-supersedes-RPM tests PASS")
