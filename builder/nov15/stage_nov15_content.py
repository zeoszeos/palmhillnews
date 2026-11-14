"""Nov 15, 2026 content staging (R73). Check-driven and repeatable. DRAFT: both picks pending Steven.
1) Community Story (R45/R83, Steven Nov 12 2026 2:06 PM: a story from the most recent Link, not Tom Palladino, Story of the
   Month format): "Serving on the Palm Hill Board of Directors", Carolyn Story, Palm Hill Link November 2026 p 36. Full
   length, verbatim from builder/nov15/data/community-story-serving-on-the-board.json, checked against pdftotext
   (link-2026-11-p36-raw.txt). Story + listen pages from the Marge Taylor shell, the same way Nov 8 wrote Tom Palladino (no photo).
2) Did You Know (R88, Steven Nov 12 2026 2:06 PM: one of Dave Bates's rules emails not used before, his exact wording, link the
   rule): Rule VI.G (email 'Rule VI', Nov 9), in the Oct 25 Rules Did You Know shell (R126: summary intro and highlights, the official rule once,
   Dave's closing note verbatim after the regulation next to the official PDF link, byline last in the card). The rule text is checked against the PDF text (data/rules-2026-09-30.txt: Section VI, pdftotext of the club PDF).
3) Runs builder/core/stage_check.py for 2026-11-15 (FOUND / MISSING / STALE). Never invents content.
Usage: python3 builder/nov15/stage_nov15_content.py"""
import json, re, html, pathlib, runpy, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "builder/nov15/data"
sys.path.insert(0, str(ROOT / "scripts")); import style_rules as _sr
import page_listen as _pl
story = json.load(open(D / "community-story-serving-on-the-board.json", encoding="utf-8"))
def norm(t): return re.sub(r"\s+", " ", t).strip()
_raw = (D / "link-2026-11-p36-raw.txt").read_text(encoding="utf-8")
_raw = re.sub(r"\d+\s+PALM HILL LINK\s+NOVEMBER, 2026\s+S\s*", " ", _raw)
_raw = re.sub(r"\nA\nWritten by Carolyn Story\n\s*board member", "\nWritten by Carolyn Story\nA board member", _raw)   # drop cap A
SRC = norm(re.sub(r"^\s*(\d\.)\s+", r"\1 ", _raw, flags=re.M))
for i, p in enumerate(story["paragraphs"]):
    assert norm(p) in SRC, ("R83: story not verbatim", i, p[:70])
assert any(p.startswith(story["teaser_candidate"]) for p in story["paragraphs"]), "R18: teaser must open a story paragraph"
assert story["credit_line"] == "First published in the Palm Hill Link, November 2026"
LIVE, LST = story["live_page_planned"], story["listen_page"]
def _page(T):
    h = html.escape(story["title"])
    main = ('<main>' + '<article>\n' + "\n".join(f"<p>{html.escape(p, quote=False)}</p>" for p in story["paragraphs"])
            + f'\n</article>\n<p class="source">{html.escape(story["credit_line"])}</p>\n</main>')
    out = re.sub(r"<title>Listen: .*?</title>", f"<title>Listen: {h} — Palm Hill Community Stories</title>", T, count=1)
    out = re.sub(r"<title>(?!Listen: ).*?</title>", f"<title>{h} — Palm Hill Community Stories</title>", out, count=1)
    out = re.sub(r"<h1>.*?</h1>", f"<h1>{h}</h1>", out, count=1)
    out = re.sub(r"<main>[\s\S]*?</main>", lambda m: main, out, count=1)
    out = (out.replace("2026-09-listen-marge-taylor-story.html", LST).replace("2026-09-marge-taylor-love-of-the-game.html", LIVE)
              .replace("Sep 1, 2026", story["date_line"]).replace("September 1, 2026", story["date_long"]))
    assert "Marge" not in out and "<article>" in out
    assert not re.search(r"\b(test|review|dry run)\b", out.split("<main>")[1].split("</main>")[0], re.I), "R83: test/review text in story"
    _sr.assert_no_link_name(out, LIVE, credit_line=story["credit_line"])   # R52 + R83 credit-line exception
    return _pl.upgrade(_pl.add(out))  # R76/R85d: add/keep the v2 Listen block on the story and listen pages
for f, t in {LIVE: "pages/2026-09-marge-taylor-love-of-the-game.html", LST: "pages/2026-09-listen-marge-taylor-story.html"}.items():
    (ROOT / "pages" / f).write_text(_page((ROOT / t).read_text(encoding="utf-8")), encoding="utf-8"); print("wrote pages/" + f)
# R88: Dave's Rule VI Did You Know, in the Oct 25 Rules Did You Know shell (Assessments Due To The Corporation page).
DN = json.load(open(D / "dyk-dave-rule-vi-homesites.json", encoding="utf-8"))
RULES = norm((D / "rules-2026-09-30.txt").read_text(encoding="utf-8"))
_TPL = (ROOT / "pages/2026-10-25-did-you-know-assessments-due-to-the-corporation.html").read_text(encoding="utf-8")
for it in DN["items"]:
    assert _sr.dyk_new_item_teaser_ok(it), ("R39: main teaser must be verbatim body sentences", it["id"])
    for _l, _t in it["rule_items"]: assert norm(_t) in RULES, ("R39: rule text not verbatim from the Rules PDF", _l)
    assert norm(it["paragraphs"][1][3:]) in RULES, "Dave's G. paragraph is the official rule word for word"
    assert it["closing_note"] == it["paragraphs"][2], "R126: closing note is Dave's email wording, verbatim"
    # R126: summary intro + highlights, then the official rule once. Dave's closing note stays
    # verbatim once after the regulation, next to the Rules PDF link (not merged into the summary).
    ps, _note = _sr.rules_dyk_r126_parts(it)
    t = "Did You Know? " + it["title_display"]
    out = re.sub(r"<title>.*?</title>", lambda m: f"<title>{html.escape(t)} — Palm Hill Country Club</title>", _TPL, count=1)
    out = re.sub(r'(<h1 class="ph-section" style="margin:0">).*?(</h1>)', lambda m: m.group(1) + html.escape(t) + m.group(2), out, count=1)
    out = re.sub(r'<div class="content-card">[\s\S]*?</div>\n', lambda m: f'<div class="content-card">{ps}</div>\n', out, count=1)
    if _note:
        if "dyk-dave-note" not in out:
            out = out.replace('<p class="dyk-rules-link"', _note + '<p class="dyk-rules-link"', 1)
        assert "dyk-dave-note" in out and out.find("dyk-dave-note") < out.find("dyk-rules-link")
    _why = _sr.rules_dyk_r126_problems(out, it)
    assert not _why, "R126: " + _why
    assert "Assessments" not in out and "ASSESSMENTS" not in out and out.count('class="ph-listen"') == 1
    out = _pl.upgrade(out)  # R76: a Nov 15 page uses the v2 listen block
    f = DN["page_prefix"] + it["preview_page"]
    _sr.assert_no_link_name(out, f)  # R52
    assert _sr.dyk_byline_ok(out, it["byline"]), "R33: byline is the last paragraph of the card"
    assert _sr.dyk_rule_link_ok(out), "R34: official Rules and Regulations PDF is linked after the card and from the rule heading"
    (ROOT / "pages" / f).write_text(out, encoding="utf-8"); print("wrote pages/" + f)
if "--story-only" not in sys.argv:
    CORE = ROOT / "builder/core"
    sys.argv = [str(CORE / "stage_check.py"), "--issue", "2026-11-15"]
    runpy.run_path(str(CORE / "stage_check.py"), run_name="__main__")
