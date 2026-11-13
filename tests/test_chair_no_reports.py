#!/usr/bin/env python3
"""R104b (Steven, Nov 12 2026): an empty Chair Reports section keeps its heading
and the one line "No reports this week." plus the archives link.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

HEAD = ">Committee Chair Reports</span>"
PLACE = "No reports this week."
ARCH = ">Committee Report Archives →</a>"
FULL = ">Read Full Report →</a>"

def _empty():
    return f'<div>{HEAD}<div>{PLACE}</div><a href="x"{ARCH}</div>'

def test_placeholder_ok_when_empty():
    assert sr.chair_empty_section_problem(_empty(), False) == ""

def test_hidden_heading_fails_when_empty():
    why = sr.chair_empty_section_problem("<div>Community Notices</div>", False)
    assert "heading is missing" in why

def test_placeholder_forbidden_when_reports_exist():
    why = sr.chair_empty_section_problem(_empty(), True)
    assert "placeholder" in why

def test_reports_ok_without_placeholder():
    html = f"<div>{HEAD}<div>Communications Committee</div>{FULL}{ARCH}</div>"
    assert sr.chair_empty_section_problem(html, True) == ""

if __name__ == "__main__":
    test_placeholder_ok_when_empty()
    test_hidden_heading_fails_when_empty()
    test_placeholder_forbidden_when_reports_exist()
    test_reports_ok_without_placeholder()
    print("R104b chair-empty tests PASS")
