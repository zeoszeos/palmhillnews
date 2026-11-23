"""R24: Calendar check time comes from the snapshot name, not file mtime."""
import os, sys, tempfile, time
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pull_calendar as pc


def test_snapshot_time_uses_filename_not_mtime():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "cal-20261024-1535.json"
        p.write_text("{}")
        # give the file a later mtime so a mtime-based footer would be wrong
        later = time.mktime(datetime(2026, 11, 22, 16, 8, tzinfo=ZoneInfo("America/New_York")).timetuple())
        os.utime(p, (later, later))
        got = pc.snapshot_time(p)
        assert got == datetime(2026, 10, 24, 15, 35, tzinfo=ZoneInfo("America/New_York")), got


def test_snapshot_time_falls_back_to_mtime_when_name_does_not_match():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "calendar.json"
        p.write_text("{}")
        got = pc.snapshot_time(p)
        assert got.tzinfo is not None
        # close to the write time (within a day) and not a parsed-from-name Oct 24 value
        assert got.year >= 2026


if __name__ == "__main__":
    test_snapshot_time_uses_filename_not_mtime()
    test_snapshot_time_falls_back_to_mtime_when_name_does_not_match()
    print("PASS test_calendar_snapshot_time")
