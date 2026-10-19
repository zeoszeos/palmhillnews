"""Oct 25, 2026 content staging: two Did You Know items (Palm Hill Link, Oct 2026 p.4) and the
Joe Clay Community Story (Link Oct 2026 cover + pp.2, 4). Source wording only: PDF line breaks rejoined,
ligature extraction glitches fixed (PDF "Ï" glyph = "fi": difficulties, efficiently); no words changed.
Writes unlisted preview pages (noindex) under pages/previews/2026-10-25/. Does NOT touch the issue or archives;
the Oct 25 builder reads data/*.json (DYK_ITEMS newest first, R31; Community Stories R45)."""
import json, re, html, pathlib, unicodedata
ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "builder/oct25/data"; PV = ROOT / "pages/previews/2026-10-25"
dyk = json.load(open(D / "dyk-link-oct2026-spectrum.json", encoding="utf-8"))
story = json.load(open(D / "community-story-joe-clay.json", encoding="utf-8"))
src_raw = open(D / "link-2026-10-p2-p4-raw.txt", encoding="utf-8").read()
def norm(t): return re.sub(r"\s+", " ", t.replace("Ï", "fi").replace("ﬁ","fi").replace("ﬃ","ffi")).strip()
SRC = norm(re.sub(r"continued on page 4\s*2\s*PALM HILL LINK\s*OCTOBER, 2026\s*S\s*", "", src_raw))  # drop the page-jump block
# guard: every paragraph must appear verbatim (after whitespace/ligature normalisation) in the PDF text layer,
# allowing for the drop-cap first letter which the PDF prints separately.
def verbatim(p):
    t = norm(p)
    if t in SRC or t[1:] in SRC: return True
    # paragraphs that cross the p.2 -> p.4 jump: every sentence must still be verbatim
    return all(x in SRC or x[1:] in SRC for x in re.split(r"(?<=[.!?])\s+", t) if x)
for it in dyk["items"]:
    for p in it["paragraphs"]: assert verbatim(p), ("DYK not verbatim", p[:60])
for p in story["paragraphs"]: assert verbatim(p), ("story not verbatim", p[:60])
T = open(ROOT / "pages/previews/2026-10-18/did-you-know-traffic-rules.html", encoding="utf-8").read()
head = T[:T.index("<main>")]; tail = T[T.index("</main>"):]
LISTEN = re.search(r'<a class="ph-listen"[\s\S]*?</a>', T).group(0)
def page(title, inner, fname):
    h = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)} — Palm Hill Country Club (October 25 preview)</title>", head)
    h = h.replace("unsent Oct 18, 2026 draft", "unsent Oct 25, 2026 draft")
    out = h + f'<main><div class="hd"><h1 class="ph-section" style="margin:0">{html.escape(title)}</h1>{LISTEN}</div>\n' + inner + tail
    (PV / fname).write_text(out, encoding="utf-8"); return fname
made = []
for it in dyk["items"]:
    ps = "".join(f"<p>{html.escape(p)}</p>" for p in it["paragraphs"])
    if it.get("byline"): ps += f'<p class="dyk-byline">{html.escape(it["byline"])}</p>'
    inner = (f'<div class="content-card">{ps}</div>\n<p class="source" style="font-size:14px;color:#666">Source: {html.escape(it["source"])} · '
             f'<a href="/pages/archive/did-you-know.html" style="color:#3A6B1A">Did You Know Archives →</a></p>\n')
    made.append(page("Did You Know? " + it["title_display"], inner, it["preview_page"]))
img = story["photo"]
ps = "\n".join(f"<p>{html.escape(p)}</p>" for p in story["paragraphs"])
inner = (f'<p class="byline">{html.escape(story["kicker"])}<br>{html.escape(story["subtitle"])}</p>\n'
         f'<figure style="margin:12px 0"><img src="{img["src"]}" width="{img["w"]}" height="{img["h"]}" alt="{html.escape(img["alt"])}" style="max-width:100%;height:auto"><figcaption>{html.escape(img["caption"])}</figcaption></figure>\n'
         f'<div class="content-card">{ps}</div>\n<p class="source" style="font-size:14px;color:#666">{html.escape(story["credit_line"])} · '
         f'<a href="/pages/archive/community-stories.html" style="color:#3A6B1A">Story Archives →</a></p>\n')
made.append(page(story["title"], inner, story["preview_page"]))
print("\n".join(made))
