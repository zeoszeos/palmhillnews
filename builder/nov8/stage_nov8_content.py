"""Nov 8, 2026 content staging (R73). Check-driven and repeatable.
1) Community Story (R45/R83, Steven Nov 6, 2026): Tom Palladino, Palm Hill Link November 2026 pp 10-11,
   full length, verbatim from builder/nov8/data/community-story-tom-palladino.json.
   Page 10 is image-only in the PDF; those paragraphs are checked against the verified scan transcription.
   Page 11 paragraphs are checked against pdftotext (link-2026-11-p11-raw.txt).
   Writes the live story page + its listen page from the Marge Taylor shell, the same way Nov 1 wrote Katra Peck.
2) Did You Know (R88): the Sunshine Directors box from page 10, in the published Did You Know shell.
3) Runs builder/core/stage_check.py for 2026-11-08 (FOUND / MISSING / STALE). Never invents content.
Usage: python3 builder/nov8/stage_nov8_content.py"""
import json, re, html, pathlib, runpy, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "builder/nov8/data"
sys.path.insert(0, str(ROOT / "scripts")); import style_rules as _sr
import page_listen as _pl
story = json.load(open(D / "community-story-tom-palladino.json", encoding="utf-8"))
def norm(t): return re.sub(r"\s+", " ", t).strip()
P10 = norm((D / "link-2026-11-p10-transcription.txt").read_text(encoding="utf-8"))
P11 = norm(re.sub(r"PALM HILL LINK\s+NOVEMBER, 2026\s+S\s*\d*", " ", (D / "link-2026-11-p11-raw.txt").read_text(encoding="utf-8")))
# page 10 is the opening four paragraphs (image transcription); the rest is page 11 (PDF text layer)
for i, p in enumerate(story["paragraphs"]):
    assert isinstance(p, str)
    src = P10 if i < 4 else P11
    assert norm(p) in src, ("R83: story not verbatim", i, p[:70])
assert story["paragraphs"][0].startswith("I") and "I want to discover" in story["paragraphs"][0]
assert "I wanted to discover" not in story["paragraphs"][0]
_last = story["paragraphs"][3]
assert "to it.\u201d" in _last and "things.\u201d" in _last and "I want to discover" not in _last, "R83: page 10 closing quotes not as printed"
assert any(p.startswith(story["teaser_candidate"]) for p in story["paragraphs"]), "R18: teaser must open a story paragraph"
assert story["credit_line"] == "First published in the Palm Hill Link, November 2026"
LIVE, LST = story["live_page_planned"], story["listen_page"]
def _page(T):
    h = html.escape(story["title"])
    _ph = story["photo"]
    assert _ph["src"].startswith("https://palmhillnews.vercel.app/assets/") and _ph["alt"].strip() and (ROOT / "public" / _ph["src"].split("vercel.app/", 1)[1]).exists(), "R84: portrait needs an absolute URL, alt text and the file in public/"
    _top = f'<figure><img src="{_ph["src"]}" width="{_ph["w"]}" height="{_ph["h"]}" alt="{html.escape(_ph["alt"])}"><figcaption>{html.escape(_ph["caption"])}</figcaption></figure>\n'
    main = ('<main>' + _top + '<article>\n' + "\n".join(f"<p>{html.escape(p, quote=False)}</p>" for p in story["paragraphs"])
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
    return out
for f, t in {LIVE: "pages/2026-09-marge-taylor-love-of-the-game.html", LST: "pages/2026-09-listen-marge-taylor-story.html"}.items():
    (ROOT / "pages" / f).write_text(_page((ROOT / t).read_text(encoding="utf-8")), encoding="utf-8"); print("wrote pages/" + f)
# R88: Sunshine Directors Did You Know, in the published Oct 25 Did You Know shell (archive nav, Listen, R49 reader).
_dnj = re.search(r'^DYK_NEW_JSON = (.+?)(?:\s+#.*)?$', (ROOT / "builder/issues/2026-11-08.py").read_text(encoding="utf-8"), re.M).group(1)
DN = json.load(open(ROOT / eval(_dnj), encoding="utf-8")) if eval(_dnj) else {"items": []}
_TPL = (ROOT / "pages/2026-10-25-did-you-know-spectrum-music-channels.html").read_text(encoding="utf-8")
for it in DN["items"]:
    assert _sr.dyk_new_item_teaser_ok(it), ("R118/R39: main teaser must be the printed semicolon sentence plus the email line, or verbatim body sentences", it["id"])
    assert "North Clubhouse Library" not in " ".join(it["paragraphs"])
    assert not re.search(r"\d{3}-\d{3}-\d{4}", " ".join(it["paragraphs"])), "R88: no retyped phone number in a DYK body"
    ps = "".join(f"<p>{html.escape(p)}</p>" for p in it["paragraphs"])
    if it.get("byline"): ps += f'<p class="dyk-byline">{html.escape(it["byline"])}</p>'
    t = "Did You Know? " + it["title_display"]
    out = re.sub(r"<title>.*?</title>", lambda m: f"<title>{html.escape(t)} — Palm Hill Country Club</title>", _TPL, count=1)
    out = re.sub(r'(<h1 class="ph-section" style="margin:0">).*?(</h1>)', lambda m: m.group(1) + html.escape(t) + m.group(2), out, count=1)
    out = re.sub(r'<div class="content-card">[\s\S]*?</div>\n', lambda m: f'<div class="content-card">{ps}</div>\n', out, count=1)
    assert "music channels" not in out.lower() and out.count('class="ph-listen"') == 1
    out = _pl.upgrade(out)  # R76: a Nov 8 page uses the v2 listen block
    f = DN["page_prefix"] + it["preview_page"]
    _sr.assert_no_link_name(out, f)  # R52: no Palm Hill Link name on a Did You Know page
    assert _sr.dyk_byline_ok(out, it["byline"]), "R33: byline is the last paragraph of the card"
    (ROOT / "pages" / f).write_text(out, encoding="utf-8"); print("wrote pages/" + f)
if "--story-only" not in sys.argv:
    CORE = ROOT / "builder/core"
    sys.argv = [str(CORE / "stage_check.py"), "--issue", "2026-11-08"]
    runpy.run_path(str(CORE / "stage_check.py"), run_name="__main__")
