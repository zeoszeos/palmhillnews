#!/usr/bin/env python3
"""R127: archive index must not list an unsent issue or the current week's issue."""
import json, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

def _repo(issues_items, index_dates, shipped, current="2026-11-15"):
    d = Path(tempfile.mkdtemp())
    (d / "archive").mkdir()
    (d / "pages" / "archive" / "issues").mkdir(parents=True)
    (d / "pages" / "previews" / current).mkdir(parents=True)
    (d / "archive" / "sent-issues.json").write_text(json.dumps({"issues": shipped}), encoding="utf-8")
    (d / "archive" / "archive-items.json").write_text(json.dumps({"issues": issues_items}), encoding="utf-8")
    (d / "pages" / "archive" / "archive-index.json").write_text(
        json.dumps({"issues": [{"date": x} for x in index_dates]}), encoding="utf-8")
    (d / "pages" / "archive" / "index.html").write_text(
        "".join(f'<a href="issues/{x}.html">{x}</a>' for x in index_dates), encoding="utf-8")
    return d

def test_current_week_in_archive_fails():
    shipped = [{"date": "2026-11-15", "volume": 1, "number": 18, "status": "shipped"}]
    repo = _repo([{"date": "2026-11-15"}], ["2026-11-15"], shipped, current="2026-11-15")
    hits = sr.archive_unsent_or_current_week_problems(repo, "2026-11-15")
    assert any("2026-11-15" in h and "current week" in h for h in hits), hits

def test_unsent_in_archive_fails():
    shipped = [{"date": "2026-11-08", "volume": 1, "number": 17, "status": "shipped"}]
    repo = _repo([{"date": "2026-11-15"}], ["2026-11-15"], shipped, current="2026-11-15")
    hits = sr.archive_unsent_or_current_week_problems(repo, "2026-11-15")
    assert any("not marked shipped" in h for h in hits), hits

def test_prior_shipped_issue_is_ok():
    shipped = [{"date": "2026-11-08", "volume": 1, "number": 17, "status": "shipped"}]
    repo = _repo([{"date": "2026-11-08"}], ["2026-11-08"], shipped, current="2026-11-15")
    assert sr.archive_unsent_or_current_week_problems(repo, "2026-11-15") == []
