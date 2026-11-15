#!/usr/bin/env python3
"""R130: a Community Notice that ran last week is dropped unless it is on the keep-list."""
import json, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

WHITE = '-webkit-text-fill-color:#FFFFFF;">'

def _section(name, titles):
    rows = []
    for t in titles:
        rows.append(
            '<tr><td valign="top" align="left" style="font-size:15px;line-height:18px;'
            f'font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{t}</td></tr>'
        )
    return f'<span style="color:#FFFFFF !important;{WHITE}{name}</span></div><table>{"".join(rows)}</table>'

def _issue_html(notices, next_section="Weekly Manager Update"):
    return (
        "<html><body>"
        + _section("Community Notices", notices)
        + _section(next_section, ["Weekly Manager Update"] if next_section == "Weekly Manager Update" else [])
        + "</body></html>"
    )

def _repo(prev_date, prev_titles, shipped_dates=None):
    d = Path(tempfile.mkdtemp())
    (d / "archive").mkdir()
    (d / "pages" / "archive" / "issues").mkdir(parents=True)
    (d / "pages" / "previews" / "2026-11-15").mkdir(parents=True)
    shipped = shipped_dates or [prev_date]
    (d / "archive" / "sent-issues.json").write_text(
        json.dumps({"issues": [{"date": x, "volume": 1, "number": i + 1, "status": "shipped"} for i, x in enumerate(shipped)]}),
        encoding="utf-8",
    )
    (d / "pages" / "archive" / "issues" / f"{prev_date}.html").write_text(
        _issue_html(prev_titles), encoding="utf-8"
    )
    return d

PREV = [
    "Cornhole Tournament",
    "How to access the Palm Hill Community Channel",
    "Social Shuffle",
    "A convenient way to send holiday cards for Palm Hill residents",
    "2027 South Rec Club Seeking Officers",
    "Swimming Pool Food and Beverage Rules",
    "Shuffleboard Season Reminders",
    "Taste of Golf",
]


def test_repeat_without_keep_list_fails():
    repo = _repo("2026-11-08", PREV)
    html = _issue_html(["Cornhole Tournament", "Singing Ensemble for Christmas Cantata"])
    hits = sr.notice_repeat_from_previous_problems(repo, "2026-11-15", html, keep=[])
    assert any("Cornhole Tournament" in h and "2026-11-08" in h for h in hits), hits
    assert not any("Singing Ensemble for Christmas Cantata" in h for h in hits), hits


def test_keep_list_allows_named_notice():
    repo = _repo("2026-11-08", PREV)
    html = _issue_html([
        "Serving on the Palm Hill Board of Directors",
        "Taste of Golf Instructions",
        "2027 South Rec Club Seeking Officers",
    ])
    hits = sr.notice_repeat_from_previous_problems(
        repo, "2026-11-15", html, keep=["2027 South Rec Club Seeking Officers"]
    )
    assert hits == [], hits


def test_different_title_is_not_a_repeat():
    repo = _repo("2026-11-08", PREV)
    html = _issue_html(["Taste of Golf Instructions"])
    hits = sr.notice_repeat_from_previous_problems(repo, "2026-11-15", html, keep=[])
    assert hits == [], hits


def test_frozen_oct25_nov1_nov8_archive_pages_are_not_flagged():
    """The guard must not break frozen as-sent archive issues, which reused notices week to week."""
    for issue in ("2026-10-25", "2026-11-01", "2026-11-08"):
        page = ROOT / "pages" / "archive" / "issues" / f"{issue}.html"
        assert page.exists(), page
        hits = sr.notice_repeat_from_previous_problems(ROOT, issue, page.read_text(encoding="utf-8"), keep=[])
        assert hits == [], (issue, hits)


def test_extractor_reads_nov8_archive_notices():
    titles = sr.community_notice_titles(
        (ROOT / "pages" / "archive" / "issues" / "2026-11-08.html").read_text(encoding="utf-8")
    )
    assert "2027 South Rec Club Seeking Officers" in titles
    assert "Cornhole Tournament" in titles
    assert "Taste of Golf" in titles
    assert "Weekly Manager Update" not in titles
    assert len(titles) == 13, titles


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:
                failed += 1
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
