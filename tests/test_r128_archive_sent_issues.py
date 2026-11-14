#!/usr/bin/env python3
"""R128: every shipped issue older than the current week must be in the archive index."""
import json, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

def _repo(listed, shipped, current="2026-11-15", pages=None):
    d = Path(tempfile.mkdtemp())
    (d / "archive").mkdir()
    (d / "pages" / "archive" / "issues").mkdir(parents=True)
    (d / "pages" / "previews" / current).mkdir(parents=True)
    (d / "archive" / "sent-issues.json").write_text(json.dumps({"issues": shipped}), encoding="utf-8")
    (d / "archive" / "archive-items.json").write_text(json.dumps({"issues": [{"date": x} for x in listed]}), encoding="utf-8")
    (d / "pages" / "archive" / "archive-index.json").write_text(
        json.dumps({"issues": [{"date": x} for x in listed]}), encoding="utf-8")
    (d / "pages" / "archive" / "index.html").write_text(
        "".join(f'<a href="issues/{x}.html">{x}</a>' for x in listed), encoding="utf-8")
    for x in (pages if pages is not None else listed):
        (d / "pages" / "archive" / "issues" / f"{x}.html").write_text("<html></html>", encoding="utf-8")
    return d

def test_missing_shipped_issue_fails():
    shipped = [
        {"date": "2026-10-25", "volume": 1, "number": 15, "status": "shipped"},
        {"date": "2026-11-08", "volume": 1, "number": 17, "status": "shipped"},
    ]
    repo = _repo(["2026-11-08"], shipped, pages=["2026-11-08"])
    hits = sr.archive_missing_sent_problems(repo, "2026-11-15")
    assert any("2026-10-25" in h and "missing from the archive index" in h for h in hits), hits

def test_missing_frozen_page_fails():
    shipped = [{"date": "2026-11-08", "volume": 1, "number": 17, "status": "shipped"}]
    repo = _repo(["2026-11-08"], shipped, pages=[])
    hits = sr.archive_missing_sent_problems(repo, "2026-11-15")
    assert any("2026-11-08" in h and "frozen archive issue page" in h for h in hits), hits

def test_current_week_is_not_required():
    shipped = [
        {"date": "2026-11-08", "volume": 1, "number": 17, "status": "shipped"},
        {"date": "2026-11-15", "volume": 1, "number": 18, "status": "shipped"},
    ]
    repo = _repo(["2026-11-08"], shipped, pages=["2026-11-08"])
    # Even if someone marked Nov 15 shipped too early, R128 does not require it in the archive this week.
    assert sr.archive_missing_sent_problems(repo, "2026-11-15") == []

def test_complete_archive_passes():
    shipped = [
        {"date": "2026-10-25", "volume": 1, "number": 15, "status": "shipped"},
        {"date": "2026-11-01", "volume": 1, "number": 16, "status": "shipped"},
        {"date": "2026-11-08", "volume": 1, "number": 17, "status": "shipped"},
    ]
    listed = [i["date"] for i in shipped]
    repo = _repo(listed, shipped, pages=listed)
    assert sr.archive_missing_sent_problems(repo, "2026-11-15") == []
