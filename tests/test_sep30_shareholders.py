#!/usr/bin/env python3
"""R120 (Steven, Nov 7 2026): the September 30 shareholders report stays off the November 8 main page.

The guard fails if that card returns. A page that is not the November 8 newsletter is out of scope,
including the report page itself.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

CARD = ('<span style="color:#FFFFFF;">Monthly Shareholders Report</span>'
        '<a href="https://palmhillnews.vercel.app/pages/2026-09-30-shareholders-report.html">HTML Report →</a>')
NOV8 = "<title>PHNEWS November 8, 2026 — DRAFT (not sent)</title>" + CARD
CLEAN = "<title>PHNEWS November 8, 2026 — DRAFT (not sent)</title><p>Weekly Manager Update</p>"
OTHER = "<title>PHNEWS October 25, 2026</title>" + CARD

def test_guard():
    assert sr.sep30_shareholders_main_problem(NOV8)
    assert sr.sep30_shareholders_main_problem(CLEAN) == ""
    assert sr.sep30_shareholders_main_problem(OTHER) == ""
    assert sr.sep30_report_page_ok(ROOT)

def test_nov8_pages_when_present():
    for rel in ("pages/previews/2026-11-08/PHNEWS-2026-11-08-preview.html",
                "pages/previews/2026-11-08/PHNEWS-2026-11-08-SEND.html"):
        p = ROOT / rel
        if not p.exists(): continue
        why = sr.sep30_shareholders_main_problem(p.read_text(encoding="utf-8"))
        assert why == "", f"{rel}: {why}"

if __name__ == "__main__":
    test_guard(); test_nov8_pages_when_present()
    print("R120 September shareholders tests PASS")
