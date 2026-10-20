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
import sys; sys.path.insert(0, str(ROOT / "scripts")); import style_rules as _sr
_sr.assert_dyk_items(dyk["items"], dyk.get("dyk_multi_approved"))  # R50
for it in dyk["items"]:
    for p in it["paragraphs"]: assert verbatim(p), ("DYK not verbatim", p[:60])
for p in story["paragraphs"]: assert verbatim(p), ("story not verbatim", p[:60])
T = open(ROOT / "pages/previews/2026-10-18/did-you-know-traffic-rules.html", encoding="utf-8").read()
head = T[:T.index("<main>")]; tail = T[T.index("</main>"):]
LISTEN = re.search(r'<a class="ph-listen"[\s\S]*?</a>', T).group(0)
def page(title, inner, fname):
    h = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)} — Palm Hill Country Club (October 25 preview)</title>", head)
    h = h.replace("unsent Oct 18, 2026 draft", "unsent Oct 25, 2026 draft")
    _sr.assert_no_link_name(inner, fname)  # R52
    out = h + f'<main><div class="hd"><h1 class="ph-section" style="margin:0">{html.escape(title)}</h1>{LISTEN}</div>\n' + inner + tail
    (PV / fname).write_text(out, encoding="utf-8"); return fname
made = []
for it in dyk["items"]:
    ps = "".join(f"<p>{html.escape(p)}</p>" for p in it["paragraphs"])
    if it.get("byline"): ps += f'<p class="dyk-byline">{html.escape(it["byline"])}</p>'
    _src = it.get("source") if it.get("source") and "Palm Hill Link" not in it["source"] else None   # R52 (Steven Oct 20 3:03 PM): no Link name -> no source line
    inner = (f'<div class="content-card">{ps}</div>\n<p class="source" style="font-size:14px;color:#666">' + (f'Source: {html.escape(_src)} · ' if _src else '') +
             f'<a href="/pages/archive/did-you-know.html" style="color:#3A6B1A">Did You Know Archives →</a></p>\n')
    made.append(page("Did You Know? " + it["title_display"], inner, it["preview_page"]))
img = story["photo"]
ps = "\n".join(f"<p>{html.escape(p)}</p>" for p in story["paragraphs"])
inner = (f'<p class="byline">{html.escape(story["date_line"])}</p>\n<p class="byline">{html.escape(story["kicker"])}<br>{html.escape(story["subtitle"])}</p>\n'
         f'<figure style="margin:12px 0"><img src="{img["src"]}" width="{img["w"]}" height="{img["h"]}" alt="{html.escape(img["alt"])}" style="max-width:100%;height:auto"><figcaption>{html.escape(img["caption"])}</figcaption></figure>\n'
         f'<div class="content-card">{ps}</div>\n<p class="source" style="font-size:14px;color:#666">{(html.escape(story["credit_line"]) + " · ") if story.get("credit_line") else ""}'
         f'<a href="/pages/archive/community-stories.html" style="color:#3A6B1A">Story Archives →</a></p>\n')
assert "First published" not in inner, "credit line removed until Steven gives it"
made.append(page(story["title"], inner, story["preview_page"]))
print("\n".join(made))

# ---- Did You Know #3 (Steven Oct 20 2026, t1022u): Dave Bates "another rule" (Sun Oct 18 6:40 AM ET) + the ENTIRE cited rule
# (Section III) verbatim, in a <blockquote> (no nested <div>: dyk_byline_ok reads the first content-card div) from the official club PDF. R31 (his wording), R33 (byline last in the card), R34 (heading + link line to
# the club PDF), R50 (multi-item approval). Guard: every rule sentence must be in the live PDF text layer (pdftotext -raw).
import subprocess, tempfile, urllib.request
d3 = json.load(open(D / "dyk-dave-assessments.json", encoding="utf-8"))
_pdf = urllib.request.urlopen(urllib.request.Request(d3["rule_pdf"], headers={"User-Agent": "PHNEWS/1.0"}), timeout=60)
assert _pdf.status == 200 and "pdf" in _pdf.headers.get("Content-Type", ""), "R34: rules PDF must return 200 application/pdf"
with tempfile.NamedTemporaryFile(suffix=".pdf") as _f:
    _f.write(_pdf.read()); _f.flush()
    _pt = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", _f.name, "-"], capture_output=True, text=True).stdout)
assert d3["rule_heading"] in _pt, "DYK3: rule heading not in official PDF"
for _l, _x in d3["rule_items"]: assert _x in _pt, ("DYK3: rule text not verbatim in official PDF", _x[:60])
_sr.assert_dyk_items([{"id": it["id"], "paragraphs": it["paragraphs"]} for it in dyk["items"]] + [{"id": d3["id"], "paragraphs": d3["email_paragraphs"]}],
                     d3["multi_approved"])  # R50
_U = html.escape(d3["rule_pdf"])
_hd = f'<a class="dyk-rule-heading" href="{_U}" style="color:#3A6B1A">{html.escape(d3["rule_heading"])}</a>'
ps = f'<p><strong>{html.escape(d3["email_paragraphs"][0])}</strong></p>' + "".join(f"<p>{html.escape(p)}</p>" for p in d3["email_paragraphs"][1:])
ps += f'<blockquote class="dyk-full-rule" style="border-left:4px solid #2d5016;padding:4px 0 4px 12px;margin:16px 0"><p><strong>{_hd}</strong></p>'
ps += "".join(f"<p>{html.escape(l)} {html.escape(x)}</p>" for l, x in d3["rule_items"]) + "</blockquote>"
ps += f'<p class="dyk-byline">{html.escape(d3["byline"])}</p>'
inner = (f'<div class="content-card">{ps}</div>\n<p class="dyk-rules-link" style="max-width:38em"><a href="{_U}" style="color:#3A6B1A">{html.escape(d3["rule_pdf_label"])}</a></p>\n'
         f'<p class="source" style="font-size:14px;color:#666">Source: {html.escape(d3["source"])} · <a href="/pages/archive/did-you-know.html" style="color:#3A6B1A">Did You Know Archives →</a></p>\n')
_fn = page("Did You Know? " + d3["title_display"], inner, d3["preview_page"])
_out = (PV / _fn).read_text(encoding="utf-8")
assert _sr.dyk_rule_link_ok(_out), "R34"
assert _sr.dyk_byline_ok(_out, d3["byline"]), "R33"
print(_fn)

for _f in made + [_fn]: _sr.assert_no_link_name((PV / _f).read_text(encoding="utf-8"), _f)  # R52 on every written article/DYK page
