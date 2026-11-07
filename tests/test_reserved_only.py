#!/usr/bin/env python3
"""R119 (Steven, Nov 7 2026): a title that is only "Reserved" is a placeholder.

The guard fails when a reserved-only title is rendered, and it does not flag a longer
title that merely contains the word.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

ROW = '<td style="font-weight:bold;color:#333333;text-align:left;padding-right:10px;">Reserved</td>'
LIST = '<div class="ph-row-title">11:00 AM · Reserved</div>'
HEAD = '<h2 class="gx-h">Reserved<span class="n">(1)</span></h2>'
LONGER = "<p>Friday morning slot is reserved; league starts Nov 6.</p>"
BOOK = '<td style="font-weight:bold;color:#333333;text-align:left;padding-right:10px;">Bookclub Activity</td>'

def test_name():
    assert sr.reserved_only_name("Reserved")
    assert sr.reserved_only_name("  RESERVED. ")
    assert sr.reserved_only_name("(reserved)")
    assert not sr.reserved_only_name("Friday morning slot is reserved")
    assert not sr.reserved_only_name("Bookclub Activity")
    assert not sr.reserved_only_name("Book Club Lunch at Irish Pub")
    assert not sr.reserved_only_name("")

def test_guard_fails_when_present():
    hits = sr.reserved_only_hits(ROW + LIST + HEAD + LONGER)
    assert hits == ["Reserved", "11:00 AM · Reserved", "Reserved"], hits
    assert sr.reserved_only_hits(LONGER + BOOK) == []

def test_nov8_pages_when_present():
    """After the November 8 rebuild, the rendered issue has no reserved-only row.
    Skipped only when this checkout has not built that issue yet."""
    names = [
        "pages/previews/2026-11-08/PHNEWS-2026-11-08-preview.html",
        "pages/previews/2026-11-08/PHNEWS-2026-11-08-SEND.html",
    ]
    names += [f"pages/2026-11-08-{kind}-by-{sort}.html"
              for kind in ("all-events", "recurring-activities")
              for sort in ("date", "name", "location")]
    for rel in names:
        p = ROOT / rel
        if not p.exists(): continue
        hits = sr.reserved_only_hits(p.read_text(encoding="utf-8"))
        assert hits == [], f"{rel}: {hits}"

if __name__ == "__main__":
    test_name(); test_guard_fails_when_present(); test_nov8_pages_when_present()
    print("R119 reserved-only tests PASS")
