#!/usr/bin/env python3
"""R139 (Steven, Nov 19 2026): a club-calendar and RPM pair matches when date and start
time agree; end times are ignored (Note 1 of the Nov 4 report to Tony).
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import meeting_conflict_report as mcr

# Same date and start, different end (the Dec 8 Golf case from the Nov 18 report)
GOLF_CAL = dict(
    committee="Golf", name="Golf Committee Meeting", cal_date="2026-12-08",
    cal_time="14:00", cal_end="15:30", recurring=False, agenda=[],
    rpm=[dict(date="2026-12-08", time="14:00", end="16:00", recurring=False, rpm_name="Golf Committee")],
    override=None, note=None, diffs=[], refs=[],
)
# Same date, different start (should still be a mismatch)
GOLF_START = dict(GOLF_CAL, cal_time="14:00", rpm=[dict(date="2026-12-08", time="15:00", end="16:00", recurring=False)])
# Different date, same start
COMMS = dict(
    committee="Communications", name="Communications Committee", cal_date="2026-12-04",
    cal_time="09:00", cal_end="11:00", recurring=False, agenda=[],
    rpm=[dict(date="2026-12-14", time="09:00", end="11:00", recurring=False, rpm_name="Communications Committee")],
    override=None, note=None, diffs=[], refs=[],
)
# Different date and start
COMMS_BOTH = dict(
    COMMS, rpm=[dict(date="2026-12-14", time="10:00", end="12:00", recurring=False, rpm_name="Communications Committee")],
)

def _R(row):
    return dict(issue="2026-11-22", rows=[row], moved=[], comm={"Golf": "Golf", "Communications": "Communications"}, rpm_fetched="test")


def test_helper_ignores_end_only():
    dd, td = mcr.rpm_date_or_start_differs("2026-12-08", "14:00", "2026-12-08", "14:00")
    assert (dd, td) == (False, False)
    dd, td = mcr.rpm_date_or_start_differs("2026-12-08", "14:00", "2026-12-08", "15:00")
    assert (dd, td) == (False, True)
    dd, td = mcr.rpm_date_or_start_differs("2026-12-04", "09:00", "2026-12-14", "09:00")
    assert (dd, td) == (True, False)
    dd, td = mcr.rpm_date_or_start_differs("2026-12-04", "09:00", "2026-12-14", "10:00")
    assert (dd, td) == (True, True)


def test_end_time_only_is_a_match():
    rows = mcr.tony_rows(_R(GOLF_CAL))
    assert rows == [], f"end-time-only difference was flagged as a mismatch: {rows}"


def test_start_time_difference_is_rpm_time():
    rows = mcr.tony_rows(_R(GOLF_START))
    assert len(rows) == 1 and rows[0]["mismatch"] == "RPM time", rows


def test_date_difference_is_rpm_day():
    rows = mcr.tony_rows(_R(COMMS))
    assert len(rows) == 1 and rows[0]["mismatch"] == "RPM day", rows


def test_date_and_start_difference_is_rpm_day_and_time():
    rows = mcr.tony_rows(_R(COMMS_BOTH))
    assert len(rows) == 1 and rows[0]["mismatch"] == "RPM day and time", rows


def test_source_does_not_compare_end_time_tuples():
    src = (ROOT / "scripts" / "meeting_conflict_report.py").read_text(encoding="utf-8")
    forbidden = '(r["cal_time"], r.get("cal_end")) != (p.get("time"), p.get("end"))'
    assert forbidden not in src, "old end-time tuple compare is still in meeting_conflict_report.py"
    assert "rpm_date_or_start_differs" in src
    assert "R139" in src


if __name__ == "__main__":
    test_helper_ignores_end_only()
    test_end_time_only_is_a_match()
    test_start_time_difference_is_rpm_time()
    test_date_difference_is_rpm_day()
    test_date_and_start_difference_is_rpm_day_and_time()
    test_source_does_not_compare_end_time_tuples()
    print("R139 ignore-end-times tests PASS")
