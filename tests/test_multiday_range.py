#!/usr/bin/env python3
"""R124 (Steven, Nov 13 2026): "Let's combine the individual dates for the 9 day cruise to a range"."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

def ev(name, d, start="08:00", place="Ship", venue="Off-Site", status="CONFIRMED"):
    return {"name": name, "date": d, "start": start, "place": place, "venue": venue, "status": status}

CRUISE = [ev("Cruise", "2026-12-07", "10:00")] + [ev("Cruise", f"2026-12-{d:02d}") for d in range(8, 17)]
WEEKDAY = [ev("Tennis", f"2026-11-{d:02d}", "09:00", "", "South Courts") for d in (9, 10, 11, 12, 13, 16, 17)]
CAL = CRUISE + WEEKDAY + [ev("Cruise", "2026-12-07", "08:00", "", status="RESCHEDULED")]

def test_runs():
    r = sr.multiday_runs(CAL)
    assert list(r) == [("Cruise", "Off-Site", "Ship")], r
    x = r[("Cruise", "Off-Site", "Ship")]
    assert (x["start"], x["end"], x["days"], x["first_start"]) == ("2026-12-07", "2026-12-16", 10, "10:00")

def test_collapse_and_label():
    window = [e for e in CRUISE + WEEKDAY if e["date"] <= "2026-12-14"]
    out = sr.collapse_multiday(window, CAL)
    cr = [e for e in out if e["name"] == "Cruise"]
    assert len(cr) == 1 and cr[0]["range_end"] == "2026-12-16" and cr[0]["range_first_start"] == "10:00"
    assert len([e for e in out if e["name"] == "Tennis"]) == 7
    assert sr.range_label("2026-12-07", "2026-12-16") == "Monday, Dec 7 \u2013 Wednesday, Dec 16, 2026"
    assert sr.range_label("2026-12-30", "2027-01-02") == "Wednesday, Dec 30, 2026 \u2013 Saturday, Jan 2, 2027"

def test_guard():
    w = ("2026-11-15", "2026-12-14")
    bad = "".join(f'<div class="ph-row-title">Cruise</div><div>Dec {d}</div>' for d in range(7, 15))
    assert sr.multiday_range_problems(bad, CAL, w)
    bad_name = '<h2 class="gx-h">Cruise<span class="n">(8)</span></h2>'
    assert sr.multiday_range_problems(bad_name, CAL, w)
    good_name = '<h2 class="gx-h">Cruise<span class="n">(1)</span></h2><div>Monday, Dec 7 \u2013 Wednesday, Dec 16 \u2022 Starts 10:00 AM</div>'
    assert sr.multiday_range_problems(good_name, CAL, w) == []
    good_date = '<h2 class="gx-h">Monday, December 7 \u2013 Wednesday, December 16, 2026<span class="n">(1)</span></h2><div>Starts 10:00 AM \u00b7 Cruise</div>'
    assert sr.multiday_range_problems(good_date, CAL, w) == []

if __name__ == "__main__":
    test_runs(); test_collapse_and_label(); test_guard(); print("PASS test_multiday_range")
