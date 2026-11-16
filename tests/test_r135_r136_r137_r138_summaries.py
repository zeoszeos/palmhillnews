#!/usr/bin/env python3
"""R135 / R136 / R137 / R138 (Steven, Nov 16 2026 ~5:30-5:38 PM ET):
six-point summaries, every decision is a rule plus a guard, pictures in the main-page summary cell,
and the Nov 22 North Clubhouse Bazaar R18 exemption."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

HEAD = '-webkit-text-fill-color:#FFFFFF;">%s</span>'
TITLE = 'font-weight:bold;color:#333333;text-align:left;padding-right:8px;">%s</span>'
MAST = "Sunday, November 22, 2026"


def _issue(body, date=MAST, sections=None):
    parts = [date]
    if sections is None:
        sections = [("Community Notices", body)]
    for heading, cell in sections:
        parts.append(HEAD % heading)
        parts.append("<table><tr><td>" + cell + "</td></tr></table>")
    return "\n".join(parts)


def _cell(title, teaser, href, extra=""):
    return (TITLE % title) + teaser + f'<a href="{href}">More →</a>' + extra


def test_r135_fails_only_when_source_has_the_point(tmp_path):
    repo = tmp_path
    (repo / "pages").mkdir()
    (repo / "pages" / "picnic.html").write_text(
        "<p>The picnic is Saturday, December 5 at 9:00 a.m. in the North Clubhouse because neighbors asked.</p>"
    )
    href = "https://palmhillnews.vercel.app/pages/picnic.html"
    # missing date, time, and place that the source has -> fail
    html = _issue(_cell("Picnic", "Come if you can.", href))
    fails, warns = sr.summary_six_point_report(html, repo)
    assert any("date" in f for f in fails)
    assert any("time" in f for f in fails)
    assert any("place" in f for f in fails)
    # complete summary -> no fail
    html_ok = _issue(_cell("Picnic", "Saturday, December 5 at 9:00 a.m. in the North Clubhouse.", href))
    fails_ok, _ = sr.summary_six_point_report(html_ok, repo)
    assert fails_ok == []
    # why cue in the source is a warning only
    assert any("why" in w for w in warns)


def test_r135_does_not_fail_for_a_point_the_source_lacks(tmp_path):
    repo = tmp_path
    (repo / "pages").mkdir()
    (repo / "pages" / "note.html").write_text("<p>The club thanks volunteers who helped this week.</p>")
    href = "https://palmhillnews.vercel.app/pages/note.html"
    html = _issue(_cell("Thank you", "The club thanks volunteers who helped this week.", href))
    fails, warns = sr.summary_six_point_report(html, repo)
    assert fails == []
    assert warns == []


def test_r135_skips_items_without_a_resolvable_page():
    html = _issue(TITLE % "Orphan" + "Saturday, December 5 at 9:00 a.m. in the North Clubhouse.")
    assert sr.summary_six_point_problems(html, None) == []


def test_r137_requires_absolute_url_and_alt_in_the_summary_cell(tmp_path):
    repo = tmp_path
    (repo / "pages").mkdir()
    (repo / "pages" / "parade.html").write_text(
        '<p>Parade</p><img src="https://example.com/flyers/parade-flyer.png" alt="Parade flyer">'
    )
    href = "https://palmhillnews.vercel.app/pages/parade.html"
    # missing from the summary cell
    html = _issue(_cell("Parade", "Join the parade Saturday, December 5.", href))
    misses = sr.summary_picture_problems(html, repo)
    assert any("parade-flyer.png" in f and "not in the main-page summary cell" in f for f in misses)
    # present but relative and no alt
    html_bad = _issue(_cell("Parade", "Join the parade Saturday, December 5.", href,
                            extra='<img src="/assets/parade-flyer.png">'))
    bad = sr.summary_picture_problems(html_bad, repo)
    assert any("absolute palmhillnews.vercel.app" in f for f in bad)
    assert any("no alt text" in f for f in bad)
    # good
    html_ok = _issue(_cell("Parade", "Join the parade Saturday, December 5.", href,
                           extra='<img src="https://palmhillnews.vercel.app/assets/parade-flyer.png" alt="Parade flyer" width="80">'))
    assert sr.summary_picture_problems(html_ok, repo) == []


def test_r137_ignores_chrome_icons(tmp_path):
    repo = tmp_path
    (repo / "pages").mkdir()
    (repo / "pages" / "story.html").write_text(
        '<p>A story.</p><img src="https://palmhillnews.vercel.app/assets/images/phnews/v4/speaker-read-aloud-green-gold-48-v1.png" width="24" alt="">'
    )
    href = "https://palmhillnews.vercel.app/pages/story.html"
    html = _issue(_cell("A story", "Residents share a memory from years ago.", href))
    assert sr.summary_picture_problems(html, repo) == []


def test_r136_current_style_rules_have_guards():
    hits = sr.style_rules_row_guard_problems(ROOT)
    assert hits == [], hits


def test_r136_flags_a_row_with_no_guard(tmp_path):
    (tmp_path / "STYLE-RULES.md").write_text(
        "# PHNEWS Style Rules (locked format)\n\n"
        "| # | Rule | Enforced in |\n| --- | --- | --- |\n"
        "| R999 | **A decision with no guard at all** (test only). |  |\n"
    )
    hits = sr.style_rules_row_guard_problems(tmp_path)
    assert hits and "R999" in hits[0]


def test_r136_accepts_guard_embedded_in_rule_text(tmp_path):
    (tmp_path / "STYLE-RULES.md").write_text(
        "# PHNEWS Style Rules (locked format)\n\n"
        "| # | Rule | Enforced in |\n| --- | --- | --- |\n"
        "| R87 | Something. Guard: visual_regression.py |  |\n"
        "| R12 | Content decisions. | builder content |\n"
    )
    assert sr.style_rules_row_guard_problems(tmp_path) == []


def test_r138_exemption_is_narrow():
    assert sr.r138_bazaar_r18_exempt("North Clubhouse Bazaar", "Events - Next Week", "2026-11-22")
    # same title, wrong issue
    assert not sr.r138_bazaar_r18_exempt("North Clubhouse Bazaar", "Events - Next Week", "2026-11-15")
    # same issue, wrong title
    assert not sr.r138_bazaar_r18_exempt("Decorating the South Clubhouse", "Events - Next Week", "2026-11-22")
    # same title and issue, wrong section
    assert not sr.r138_bazaar_r18_exempt("North Clubhouse Bazaar", "Events - This Week", "2026-11-22")
    # exact title required (no prefix match on a longer different event)
    assert not sr.r138_bazaar_r18_exempt("North Clubhouse Bazaar Extra", "Events - Next Week", "2026-11-22")


def test_issue_iso_and_from_dates():
    assert sr.issue_iso_from_html("Sunday, November 15, 2026") == "2026-11-15"
    assert sr.issue_iso_from_html("Sunday, November 22, 2026") == "2026-11-22"
    assert sr.R135_FROM == "2026-11-22"
    assert sr.R137_FROM == "2026-11-22"
    assert sr.R138_ISSUE == "2026-11-22"
    assert sr.R138_TITLE == "North Clubhouse Bazaar"



def test_iter_items_includes_nested_event_date_line():
    """Event cards put the title in an inner row and the date line in the next inner row; both count as the summary."""
    cell = (
        '<table><tr><td style="font-size:15px;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">North Clubhouse Bazaar</td>'
        '<td>North Clubhouse</td></tr>'
        '<tr><td colspan="2">Saturday, Dec 5, 2026 • 9:00 AM</td></tr></table>'
        '<div>Rent a table for $20 to sell your goods, 9 a.m. to 1 p.m.</div>'
    )
    html = _issue("", sections=[("Events - Next Week", cell)])
    items = [it for it in sr.iter_main_page_items(html) if it["title"] == "North Clubhouse Bazaar"]
    assert items, "bazaar card not found"
    sm = items[0]["summary_text"]
    assert "Dec 5" in sm or "December 5" in sm
    assert "9:00" in sm
    assert "Rent a table" in sm
    assert "North Clubhouse" in sm



def test_r135_ignores_sent_header_stamps_and_accepts_numeric_dates(tmp_path):
    repo = tmp_path
    (repo / "pages").mkdir()
    (repo / "pages" / "lunch.html").write_text(
        "<p>Listen Monday, Nov 9, 2026, 2:58 PM ET Subject: December 2, 2026 Ladies Luncheon "
        "From: Webmaster Sent: Monday, Nov 9, 2026, 2:58 PM ET If you would like to purchase tickets.</p>"
    )
    href = "https://palmhillnews.vercel.app/pages/lunch.html"
    html = _issue(_cell("Ladies Luncheon", "Luncheon: 12/2/26 at The Bayou Club.", href))
    fails, _ = sr.summary_six_point_report(html, repo)
    assert fails == [], fails


def test_r135_skips_place_check_on_community_stories(tmp_path):
    repo = tmp_path
    (repo / "pages").mkdir()
    (repo / "pages" / "story.html").write_text(
        "<p>Forty years ago this month, on November 7, 1986, the State declared a cooperative. "
        "Ten years ago a program was held at the North Clubhouse.</p>"
    )
    href = "https://palmhillnews.vercel.app/pages/story.html"
    cell = _cell("Way Back When", "Forty years ago this month, on November 7, 1986, the State declared a cooperative.", href)
    html = _issue("", sections=[("Community Stories", cell)])
    fails, _ = sr.summary_six_point_report(html, repo)
    assert fails == [], fails


if __name__ == "__main__":
    import inspect, tempfile
    failed = 0
    for name, fn in list(globals().items()):
        if not (name.startswith("test_") and callable(fn)):
            continue
        try:
            if "tmp_path" in inspect.signature(fn).parameters:
                with tempfile.TemporaryDirectory() as d:
                    fn(Path(d))
            else:
                fn()
            print(f"PASS {name}")
        except Exception as e:
            failed += 1
            print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
