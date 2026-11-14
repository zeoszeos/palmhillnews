#!/usr/bin/env python3
"""R126 (Steven, Nov 13 2026 9:16 PM ET): summary intro, then the official regulation once; no repeat."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

RULE = ("All homes and homesites must be maintained in a clean, orderly, and well-kept condition. "
        "This includes, but is not limited to, the exterior appearance of the home, general upkeep, necessary repairs, "
        "painting, grounds maintenance, and pest control. If a home or homesite is found to be in a state of disrepair "
        "or neglect, management reserves the right pursuant to Paragraph 22 of the Master Form Exclusive Right of "
        "Possession Agreement to require the shareholder to take corrective action. Should the shareholder fail to do "
        "so in a timely manner, management may perform the necessary work or engage third party contractors to complete "
        "the required maintenance or repairs. The shareholder will be responsible for the reasonable costs incurred. "
        "When park personnel perform such services, a service fee of $50 per hour, per worker, shall be charged with "
        "a one hour minimum per occurrence.")
NOTE = "You'll notice this is just one of many regulations for care and maintenance.  Go to the full document to learn more care and maintenance points"
ITEM = {
    "intro": ("Homes and homesites must be maintained in a clean, orderly, and well-kept condition. "
              "If a home or homesite is found to be in a state of disrepair or neglect, the shareholder "
              "may be required to take corrective action and will be responsible for the reasonable costs incurred."),
    "highlights": [
        ["What must be kept up", "the exterior appearance of the home, general upkeep, necessary repairs, painting, grounds maintenance, and pest control."],
        ["Corrective action", "management may require the shareholder to take corrective action pursuant to Paragraph 22 of the Master Form Exclusive Right of Possession Agreement."],
        ["If it is not done in a timely manner", "management may perform the necessary work or engage third party contractors, and the shareholder will be responsible for the reasonable costs incurred."],
        ["Park personnel fee", "$50 per hour, per worker, with a one hour minimum per occurrence."],
    ],
    "rule_heading": "VI. HOMESITES AND CARE & MAINTENANCE OF PREMISES",
    "rule_items": [["G.", RULE]],
    "rule_pdf": "https://www.palmhillcountryclub.net/example.pdf",
    "byline": "Dave Bates, Board VP",
    "closing_note": NOTE,
}

def _page(card, extra=""):
    return ('<div class="content-card">' + card + '</div>\n' + extra +
            '<p class="dyk-rules-link"><a href="https://www.palmhillcountryclub.net/example.pdf">Rules PDF →</a></p>')

def test_duplicate_rule_is_caught():
    # The Nov 15 bug: Dave's email quote of G. plus the official blockquote.
    bad = _page(f"<p>G. {RULE}</p><blockquote class=\"dyk-full-rule\"><p><strong>G.</strong> {RULE}</p></blockquote>")
    hits = sr.repeated_regulation_problems(bad)
    assert hits, "the official G. paragraph printed twice must fail"

def test_short_repeated_labels_are_ok():
    # Flyer transcriptions repeat short lines (a date, a title); those are not a regulation repeat.
    html = _page("<p>December 12th, 2026</p><p>December 12th, 2026</p>")
    assert sr.repeated_regulation_problems(html) == []

def test_r126_layout_once():
    card, note = sr.rules_dyk_r126_parts(ITEM)
    html = _page(card, note)
    assert sr.repeated_regulation_problems(html) == []
    assert sr.rules_dyk_r126_problems(html, ITEM) == ""
    assert html.count("dyk-full-rule") == 1
    assert "just one of many regulations for care and maintenance" in html
    assert "dyk-dave-note" in html
    assert html.find("dyk-dave-note") < html.find("dyk-rules-link")
    assert html.find("dyk-rule-intro") < html.find("dyk-full-rule")
    # The closing note is not in the intro.
    intro = html[html.find("dyk-rule-intro"):html.find("dyk-full-rule")]
    assert "You'll notice" not in intro

def test_invented_fee_is_rejected():
    bad = dict(ITEM, intro=ITEM["intro"] + " The fee is $99.")
    try:
        sr.rules_dyk_r126_parts(bad)
    except ValueError as e:
        assert "99" in str(e)
    else:
        raise AssertionError("an invented fee must be rejected")

def test_note_merged_into_intro_fails():
    card, note = sr.rules_dyk_r126_parts(ITEM)
    # Force the note into the intro paragraph as well.
    html = _page(card.replace("</p>", " " + NOTE + "</p>", 1), note)
    why = sr.rules_dyk_r126_problems(html, ITEM)
    assert why, why

if __name__ == "__main__":
    test_duplicate_rule_is_caught()
    test_short_repeated_labels_are_ok()
    test_r126_layout_once()
    test_invented_fee_is_rejected()
    test_note_merged_into_intro_fails()
    print("PASS test_r126_no_repeated_regulation")
