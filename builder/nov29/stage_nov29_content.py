"""Nov 29, 2026 content staging (R73). Check-driven and repeatable.
1) Community Story (R45/R83/R84; Steven Nov 23 2026, t1863u: '1 pls'): 'Smiling @ the Ladies Luncheon',
   Palm Hill Link November 2026, cover photo and story on pages 2 and 4. Full length, verbatim from
   builder/nov29/data/community-story-smiling-ladies-luncheon.json, checked against pdftotext -layout of
   Link-2026-11.pdf (link-2026-11-p2-p4-raw.txt) and the page images. Story + listen pages from the Marge
   Taylor shell, the same way Nov 22 wrote Way Back When and Nov 1 wrote Katra Peck (R84 cover photo at
   the top; no byline is printed). Pages 2 and 4 have no inside photos.
2) Runs builder/core/stage_check.py for 2026-11-29 (FOUND / MISSING / STALE) unless --story-only.
   Never invents content.
Usage: python3 builder/nov29/stage_nov29_content.py [--story-only]"""
import json, re, html, pathlib, runpy, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "builder/nov29/data"
sys.path.insert(0, str(ROOT / "scripts")); import style_rules as _sr
import page_listen as _pl
story = json.load(open(D / "community-story-smiling-ladies-luncheon.json", encoding="utf-8"))

def norm(t):
    return re.sub(r"\s+", " ", t).strip()

_raw = (D / "link-2026-11-p2-p4-raw.txt").read_text(encoding="utf-8")
_raw = re.sub(r"continued on page 4", " ", _raw)
_raw = re.sub(r"PALM HILL LINK\s+NOVEMBER, 2026\s+S", " ", _raw)
# Page 2 drop cap: the V sits on the second line, so the text layer reads "you'll \n V be fine."
_raw = re.sub(r"(you’ll)\s+V\s+(be fine)", r"\1 \2", _raw)
SRC = norm(_raw)

def verbatim(p):
    t = norm(p)
    # drop cap V on page 2 is printed separately from 'olunteering'
    return t in SRC or t[1:] in SRC or all(
        x in SRC or x[1:] in SRC for x in re.split(r"(?<=[.!?])\s+", t) if x
    )

for i, p in enumerate(story["paragraphs"]):
    assert verbatim(p), ("R83: story not verbatim", i, p[:80])
assert story["title_print"] in _raw, "printed title missing from the Link text layer"
assert any(p.startswith(story["teaser_candidate"]) for p in story["paragraphs"]), "R18: teaser must open a story paragraph"
assert story["credit_line"] == "First published in the Palm Hill Link, November 2026"
assert story["byline"] is None, "no byline is printed; do not invent an author"
LIVE, LST = story["live_page_planned"], story["listen_page"]

def _page(T):
    h = html.escape(story["title"])
    _ph = story.get("photo")
    _k = story.get("kicker")
    _top = ""
    if _ph:
        _top = (
            f'<figure><img src="{_ph["src"]}" width="{_ph["w"]}" height="{_ph["h"]}" '
            f'alt="{html.escape(_ph["alt"])}"><figcaption>{html.escape(_ph["caption"])}</figcaption></figure>\n'
        )
        _pf = ROOT / "public" / _ph["src"].split("vercel.app/", 1)[1]
        assert _ph["src"].startswith("https://palmhillnews.vercel.app/assets/") and _ph["alt"].strip() and _pf.exists(), \
            "R84: cover photo needs an absolute URL, alt text and the file in public/"
    _by = f'<p class="byline">{html.escape(_k)}</p>\n' if _k else ""
    assert story.get("byline") in (None, ""), "do not print an invented author"
    main = (
        f"<main>{_by}{_top}<article>\n"
        + "\n".join(f"<p>{html.escape(p, quote=False)}</p>" for p in story["paragraphs"])
        + f'\n</article>\n<p class="source">{html.escape(story["credit_line"])}</p>\n</main>'
    )
    out = re.sub(r"<title>Listen: .*?</title>", f"<title>Listen: {h} — Palm Hill Community Stories</title>", T, count=1)
    out = re.sub(r"<title>(?!Listen: ).*?</title>", f"<title>{h} — Palm Hill Community Stories</title>", out, count=1)
    out = re.sub(r"<h1>.*?</h1>", f"<h1>{h}</h1>", out, count=1)
    out = re.sub(r"<main>[\s\S]*?</main>", lambda m: main, out, count=1)
    out = (out.replace("2026-09-listen-marge-taylor-story.html", LST)
              .replace("2026-09-marge-taylor-love-of-the-game.html", LIVE)
              .replace("Sep 1, 2026", story["date_line"])
              .replace("September 1, 2026", story["date_long"]))
    assert "Marge" not in out and "<article>" in out
    assert not re.search(r"\b(test|review|dry run)\b", out.split("<main>")[1].split("</main>")[0], re.I), \
        "R83: test/review text in story"
    _sr.assert_no_link_name(out, LIVE, credit_line=story["credit_line"])  # R52 + R83 credit-line exception
    return _pl.upgrade(_pl.add(out))  # R76/R85d: add/keep the v2 Listen block

for f, t in {LIVE: "pages/2026-09-marge-taylor-love-of-the-game.html",
             LST: "pages/2026-09-listen-marge-taylor-story.html"}.items():
    (ROOT / "pages" / f).write_text(_page((ROOT / t).read_text(encoding="utf-8")), encoding="utf-8")
    print("wrote pages/" + f)

if "--story-only" not in sys.argv:
    CORE = ROOT / "builder/core"
    sys.argv = [str(CORE / "stage_check.py"), "--issue", "2026-11-29"]
    runpy.run_path(str(CORE / "stage_check.py"), run_name="__main__")
