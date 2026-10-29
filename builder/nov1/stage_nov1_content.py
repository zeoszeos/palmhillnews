"""Nov 1, 2026 content staging (R73, coding batch 6). Check-driven and repeatable.
1) Community Story (R45/R83, Steven Oct 26 2026 12:19 PM): Katra Peck (Palm Hill Link, February 2026, pp 4-5), full length,
   verbatim from builder/nov1/data/community-story-katra-peck.json. Guard: every paragraph is verbatim in the PDF text layer
   (link-2026-02-p4-p5-raw.txt, after whitespace normalisation, drop cap, caption run-in and page footers removed). Writes the
   live story page + its listen page in the standard Community Stories shell (published Marge Taylor page = template), the
   same way the Oct 25 Joe Clay story was built (builder/oct25/stage_oct25_content.py).
2) Runs builder/core/stage_check.py for 2026-11-01 (FOUND / MISSING / STALE). Never invents content.
Usage: python3 builder/nov1/stage_nov1_content.py"""
import json, re, html, pathlib, runpy, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "builder/nov1/data"
sys.path.insert(0, str(ROOT / "scripts")); import style_rules as _sr
story = json.load(open(D / "community-story-katra-peck.json", encoding="utf-8"))
def norm(t): return re.sub(r"\s+", " ", t).strip()
_raw = (D / "link-2026-02-p4-p5-raw.txt").read_text(encoding="utf-8")
_raw = re.sub(r"\n Katra Peck and (Indian Rocks Beach)", r" \1", _raw).replace("\nVictoria Richards\n", "\n")   # caption run-in (p4)
_raw = re.sub(r"PALM HILL LINK\s+FEBRUARY, 2026\s+S\s*\d*", " ", _raw).replace("P     alm", "Palm")              # footers, drop cap
SRC = norm(re.sub(r"\n\s*4\n", "\n", _raw))
for p in story["paragraphs"]:
    if isinstance(p, str): assert norm(p) in SRC, ("R83: story not verbatim", p[:60])
    elif "h2" in p: assert p["print"] in SRC and p["h2"].upper() == p["print"], ("R83: second head not as printed", p)
for f in story["figures"].values(): assert norm(f["caption"]) in SRC or f["caption"] == "Katra Peck and Victoria Richards", f["caption"]
assert any(isinstance(p, str) and p.startswith(story["teaser_candidate"]) for p in story["paragraphs"]), "R18: teaser must open a story paragraph"
LIVE, LST = story["live_page_planned"], story["listen_page"]
def _fig(f):
    ims = f["images"]
    if len(ims) == 1:
        i = ims[0]; return (f'<figure style="max-width:{min(360, 2 * i["w"])}px"><img src="{i["src"]}" width="{i["w"]}" height="{i["h"]}" alt="{html.escape(i["alt"])}">'
                            f'<figcaption>{html.escape(f["caption"])}</figcaption></figure>')
    row = "".join(f'<img src="{i["src"]}" width="{i["w"]}" height="{i["h"]}" alt="{html.escape(i["alt"])}" style="flex:{i["w"]/i["h"]:.4f} 1 0;min-width:0;border-radius:6px">' for i in ims)
    return (f'<figure style="max-width:720px"><div style="display:flex;gap:6px;align-items:flex-start">{row}</div>'
            f'<figcaption>{html.escape(f["caption"])}</figcaption></figure>')
def _item(p):
    if isinstance(p, str): return f"<p>{html.escape(p, quote=False)}</p>"
    if "h2" in p: return f"<h2>{html.escape(p['h2'])}</h2>"
    return _fig(story["figures"][p["figure"]])
def _page(T):
    h = html.escape(story["title"])
    _ph = story.get("photo"); _k = story.get("kicker")
    _top = (f'<figure><img src="{_ph["src"]}" width="{_ph["w"]}" height="{_ph["h"]}" alt="{html.escape(_ph["alt"])}"><figcaption>{html.escape(_ph["caption"])}</figcaption></figure>\n' if _ph else "")
    if _ph: assert _ph["src"].startswith("https://palmhillnews.vercel.app/assets/") and _ph["alt"].strip() and (ROOT / "public" / _ph["src"].split("vercel.app/", 1)[1]).exists(), "R84: cover photo needs an absolute URL, alt text and the file in public/"
    main = (f'<main><p class="byline">' + (f'{html.escape(_k)}<br>' if _k else "") + f'{html.escape(story["byline"])}</p>\n' + _top + '<article>\n' + "\n".join(_item(p) for p in story["paragraphs"])
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
# 3) R88 (Steven Oct 29 2026 11:11 AM): new Did You Know item(s) -> final page pages/<prefix><page>, in the published Oct 25
#    Did You Know shell (pages/2026-10-25-did-you-know-spectrum-music-channels.html = template: archive nav, Listen, R49 reader).
#    Same inner markup as builder/oct25/stage_oct25_content.py (content card, byline, Did You Know Archives line). Template untouched.
DN = json.load(open(D / "dyk-spectrum-unplugging.json", encoding="utf-8"))
_TPL = (ROOT / "pages/2026-10-25-did-you-know-spectrum-music-channels.html").read_text(encoding="utf-8")
for it in DN["items"]:
    assert _sr.dyk_summary_ok(it["teaser"], it["paragraphs"]), ("R88/R39: teaser must be verbatim body sentence(s)", it["id"])
    assert not re.search(r"\d{3}-\d{3}-\d{4}", " ".join(it["paragraphs"])), "R88: no retyped phone number in a DYK body"
    ps = "".join(f"<p>{html.escape(p)}</p>" for p in it["paragraphs"])
    if it.get("byline"): ps += f'<p class="dyk-byline">{html.escape(it["byline"])}</p>'
    t = "Did You Know? " + it["title_display"]
    out = re.sub(r"<title>.*?</title>", lambda m: f"<title>{html.escape(t)} — Palm Hill Country Club</title>", _TPL, count=1)
    out = re.sub(r'(<h1 class="ph-section" style="margin:0">).*?(</h1>)', lambda m: m.group(1) + html.escape(t) + m.group(2), out, count=1)
    out = re.sub(r'<div class="content-card">[\s\S]*?</div>\n', lambda m: f'<div class="content-card">{ps}</div>\n', out, count=1)
    assert "music channels" not in out.lower() and out.count('class="ph-listen"') == 1
    f = DN["page_prefix"] + it["preview_page"]
    _sr.assert_no_link_name(out, f)  # R52
    (ROOT / "pages" / f).write_text(out, encoding="utf-8"); print("wrote pages/" + f)
if "--story-only" not in sys.argv:
    CORE = ROOT / "builder/core"
    sys.argv = [str(CORE / "stage_check.py"), "--issue", "2026-11-01"]
    runpy.run_path(str(CORE / "stage_check.py"), run_name="__main__")
