"""R148: Community Notice event/date lines show a start time only unless Steven approved an end time."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

def _notice_html(pairs):
    body = "".join(
        f'''<td style="font-size:15px;line-height:18px;font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{t}</td>'''
        f'''<div class="ph-notice-date" style="font-size:14px;color:#666666;text-align:left;padding-top:2px;">{d}</div>'''
        for t, d in pairs
    )
    return "Community Notices" + body + "Weekly Manager Update"


CURRENT = [
    ("South Coffee and Christmas Breakfast", "Coffee: Tuesday, December 1, 2026 · Start: 8:00 AM · Place: South Clubhouse"),
    ("Spectrum Fiber Upgrade", "Schedule installation by: December 1, 2026 · Unupgraded accounts disconnected: December 8, 2026 · Call: 855-326-5115"),
    ("Pianist Needed for Cantata Ensemble", "Performance: Sunday, December 6th · Text: 269-317-6890"),
    ("New Valet Trash Service", "Effective: December 1, 2026 · First collection: recycling on December 2nd"),
    ("Palm Hill Annual Golf Cart Parade", "Parade: December 12th, 2026 · Line up: 5:30 PM in front of the North Clubhouse · Ending at South Clubhouse"),
    ("Christmas Golf Cart Route", ""),  # approved No date — no date line
    ("Ladies Christmas Luncheon", "Luncheon: 12/2/26 · The Bayou Club"),
    ("2027 South Rec Club Seeking Officers", "Deadline: December 2, 2026 at the close of the business meeting"),
]


def test_current_nov29_date_lines_pass():
    html = _notice_html([(t, d) for t, d in CURRENT if d])
    # Route has no date line; extractor only sees titles with the bold markup we included
    html = _notice_html(CURRENT)
    assert sr.notice_event_end_time_problems(html, allowed=set()) == []


def test_start_only_passes():
    html = _notice_html([("South Coffee and Christmas Breakfast", "Coffee: Tuesday, December 1, 2026 · Start: 8:00 AM · Place: South Clubhouse")])
    assert sr.notice_event_end_time_problems(html) == []


def test_range_fails():
    html = _notice_html([("South Coffee and Christmas Breakfast", "Coffee: Tuesday, December 1, 2026 · 8:00 AM – 10:00 AM · Place: South Clubhouse")])
    hits = sr.notice_event_end_time_problems(html)
    assert hits and "start–end time range" in hits[0] and "South Coffee and Christmas Breakfast" in hits[0]


def test_shared_ampm_range_fails():
    html = _notice_html([("Senior Empowerment Lunch & Learn", "When: Wednesday, November 4, 10 a.m.–1 p.m. · South Clubhouse")])
    hits = sr.notice_event_end_time_problems(html)
    assert hits and "start–end time range" in hits[0]


def test_ends_at_fails():
    html = _notice_html([("South Coffee and Christmas Breakfast", "Coffee: Tuesday, December 1 · Start: 8:00 AM · Ends at 10:00 AM")])
    hits = sr.notice_event_end_time_problems(html)
    assert hits and "end time" in hits[0]


def test_from_for_duration_fails():
    html = _notice_html([("South Potable Water Shut off", "Shut off: Wednesday, November 4, 2026 from 10:00am for approximately 2 hours")])
    hits = sr.notice_event_end_time_problems(html)
    assert hits and "duration" in hits[0]


def test_ending_at_place_passes():
    html = _notice_html([("Palm Hill Annual Golf Cart Parade", "Parade: December 12th, 2026 · Line up: 5:30 PM in front of the North Clubhouse · Ending at South Clubhouse")])
    assert sr.notice_event_end_time_problems(html) == []


def test_body_deadline_around_10am_is_not_the_date_line():
    date = "Coffee: Tuesday, December 1, 2026 · Start: 8:00 AM · Place: South Clubhouse"
    html = _notice_html([("South Coffee and Christmas Breakfast", date)])
    html = html.replace("Weekly Manager Update", "no later than close of the meeting on Tues. Dec. 1 (around 10am). Weekly Manager Update")
    assert sr.notice_event_end_time_problems(html) == []


def test_allowlist_permits_end_time():
    html = _notice_html([("Named Event", "When: 10 a.m.–1 p.m. · South Clubhouse")])
    assert sr.notice_event_end_time_problems(html, allowed={"Named Event"}) == []
    hits = sr.notice_event_end_time_problems(html, allowed=set())
    assert hits and "Named Event" in hits[0]


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f):
            f()
            print("PASS", n)
