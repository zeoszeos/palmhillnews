"""R141: full Fed Up Trash Valet source details run as a Community Notice."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

PAGE = (
    "<h1>New Valet Trash Service</h1>"
    "<p>Effective December 1, 2026, Palm Hill will begin a new valet trash and recycling service with Fed Up Trash Valet LLC. Please review the details below.</p>"
    "<li>Trash: Mondays and Thursdays for the ENTIRE community (You will now have two days of collection from your home!)</li>"
    "<li>Recycling: Wednesdays for the ENTIRE community</li>"
    "<li>Collection takes place between 8:00 a.m. and 4:00 p.m. on service days.</li>"
    "<li>Place your trash or recycling bags on the sidewalk or at the end of your driveway by 8:00 a.m. on collection days.</li>"
    "<p>There is no collection on New Year's Eve and Day, Easter, Memorial Day, July 4th, Labor Day, Thanksgiving, or Christmas Eve and Day. If a scheduled pickup falls on one of these holidays, collection will take place the following day.</p>"
    "<p>Clear bags are still required for recycling.</p>"
)

ISSUE = (
    '<h2>Community Notices</h2>'
    '<div>New Valet Trash Service</div>'
    '<div style="margin-top:3px;">Effective December 1, 2026, Palm Hill will begin a new valet trash and recycling service with Fed Up Trash Valet LLC. The first collection will be the recycling on December 2nd. '
    f'<a href="https://palmhillnews.vercel.app/pages/{sr.VALET_NOTICE_PAGE}">More →</a></div>'
    '<div>Meetings this month</div>'
)

def test_missing_notice_fails_and_complete_copy_passes():
    hits = sr.valet_notice_problems("<h2>Community Notices</h2><div>Other</div>", "")
    assert any("missing" in h.lower() or "Missing" in h or "VALET" in h.upper() or "New Valet" in h for h in hits)
    assert sr.valet_notice_problems(ISSUE, PAGE) == []

def test_copy_page_missing_holiday_sentence_fails():
    bad = PAGE.replace("There is no collection on New Year's Eve and Day, Easter, Memorial Day, July 4th, Labor Day, Thanksgiving, or Christmas Eve and Day. If a scheduled pickup falls on one of these holidays, collection will take place the following day.", "")
    hits = sr.valet_notice_problems(ISSUE, bad)
    assert any("Holiday" in h or "New Year" in h or "missing source wording" in h for h in hits)
