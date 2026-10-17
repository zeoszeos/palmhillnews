#!/usr/bin/env python3
"""PHNEWS format guard: per-section screenshots (desktop 1280 + mobile 390@2x) vs an approved golden set,
plus rule checks from STYLE-RULES.md. Run by the builder on Friday/Saturday builds.

  python scripts/visual_regression.py PAGE.html|URL --golden tests/golden/format-locked-2026-10-18 [--capture] [--out DIR]

--capture  write the golden set (do this only after Steven approves the look).
Exit 0 = clean, 1 = rule failures, 2 = visual diffs only (report lists them; review, don't auto-fail the build).
Needs: /workspace/.venv-vr (python -m venv; pip install playwright pillow numpy; playwright install chromium).
"""
import sys, os, re, json, argparse, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_rules import title_month_violations
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import numpy as np

VIEWS = {"desktop": dict(viewport={"width": 1280, "height": 900}, device_scale_factor=1),
         "mobile": dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)}
PIXEL_TOL = 0.004   # >0.4% of pixels changed (after per-pixel tolerance) = visual diff
HEIGHT_TOL = 6      # px height change allowed (e.g. a one-line text edit)
# Dynamic text masked before screenshots so routine content refreshes don't flag (build stamp).
MASK_JS = r"""() => { for (const el of document.querySelectorAll('body *')) {
  if (el.children.length === 0 && /\b\d{1,2}:\d{2}\s?[AP]M\b/.test(el.textContent) && /Updated|Built|as of/i.test(el.textContent)) el.style.visibility = 'hidden'; } }"""
SECTIONS_JS = r"""() => { // section = green header bar (#2D5016) down to the next bar; 'masthead' = top to first bar
  const bars = [...document.querySelectorAll('div,td,table,h2')].filter(e => getComputedStyle(e).backgroundColor === 'rgb(45, 80, 22)'
      && e.innerText.trim().length > 2 && e.getBoundingClientRect().height < 140)
    .filter((e, i, arr) => !arr.some(o => o !== e && o.contains(e) === false && e.contains(o)));
  const ys = []; const out = [];
  for (const e of bars) { const r = e.getBoundingClientRect(); const y = r.top + scrollY; if (ys.some(v => Math.abs(v - y) < 20)) continue; ys.push(y); out.push({title: e.innerText.split('\n')[0].trim(), y}); }
  out.sort((a, b) => a.y - b.y); const H = document.documentElement.scrollHeight, W = document.documentElement.clientWidth;
  const res = [{i: 0, title: 'masthead', x: 0, y: 0, w: W, h: out.length ? out[0].y : H}];
  out.forEach((o, k) => res.push({i: k + 1, title: o.title, x: 0, y: o.y, w: W, h: (k + 1 < out.length ? out[k + 1].y : H) - o.y}));
  return res; }"""
LISTEN_JS = r"""() => [...document.querySelectorAll('a')].filter(a => a.textContent.trim() === 'Listen').map(a => {
  const r = a.getBoundingClientRect(), cs = getComputedStyle(a); const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4;
  let box = a.closest('table') || a.parentElement; const br = box.getBoundingClientRect();
  return {ws: cs.whiteSpace, h: r.height, lh, inset: Math.round(br.right - r.right), href: a.href}; })"""

SUMMARY_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summary_lines.js')).read()

def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:50] or "section"

def rule_checks(html, page):
    fails = []
    for ln, t in title_month_violations(html): fails.append(f"R3 abbreviated month in title/heading line {ln}: {t}")
    if not re.search(r"(Sunday|Saturday|Monday|Tuesday|Wednesday|Thursday|Friday), (January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", html):
        fails.append("R2 masthead weekday + full date missing (e.g. 'Sunday, October 18, 2026')")
    # R24: resident-facing footer "Calendar check - <Full Month> <D>, <h:mm AM/PM>" matching the build's calendar pull (Oct 18+ issues)
    _m = re.search(r"(?:Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day, (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", html)
    if _m:
        import datetime as _d2, json as _j2
        _iso = _d2.datetime.strptime(" ".join(_m.groups()), "%B %d %Y").date().isoformat()
        if _iso >= "2026-10-18":
            _fl = re.findall(r'<p class="ph-cal-check"[^>]*>([^<]*)</p>', html)
            if len(_fl) != 1 or not re.fullmatch(r"Calendar check - (January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{1,2}:\d{2} (AM|PM)", _fl[0]):
                fails.append(f"R24 footer 'Calendar check - Month D, h:mm AM/PM' missing or malformed: {_fl}")
            else:
                _cp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "builder/calendar-pull", _iso + ".json")
                if os.path.exists(_cp) and _j2.load(open(_cp))["footer"] != _fl[0]:
                    fails.append(f"R24 footer '{_fl[0]}' does not match the build's calendar pull ({_j2.load(open(_cp))['footer']})")
    # R23: event/notice items link with "More →" only (report/message labels Read Full Report/Message/Update are allowed)
    for v in re.findall(r'>\s*((?:Read (?:Full )?(?:Details|More|more|Notice|Event)|Details|Full Details|Learn More)\s*→?)\s*</a>', html):
        fails.append(f"R23 event/notice link label '{v}' (use 'More →')")
    if re.search(r'class="[^"]*\bpha-banner', html): fails.append("R6 provenance/banner strip present (pha-banner) on an Oct 18+ issue")
    if re.search(r"<img\b[^>]*(qr|QR)[^>]*>", html): fails.append("R7 QR code image on the main newsletter page (QR belongs on the notice page)")
    for s in re.findall(r"Source:(?:(?!</).){0,120}", html):
        if re.search(r"Palm Hill (Calendar|Webmaster)", s): fails.append(f"R5 long source label: {re.sub('<[^>]+>','',s)[:80]}")
    # R14: Helpful Webpages links the Palm Hill Link Archives page; web copies never leave Link Monthly unlinked
    if "Palm Hill Link Monthly" in html:
        if "archive/palm-hill-link.html" not in html: fails.append("R14 Helpful Webpages missing 'Palm Hill Link Archives' link")
        if "<span>Palm Hill Link Monthly</span>" in html: fails.append("R14 'Palm Hill Link Monthly' has no link (web copy should point to the Link Archives page)")
    # R19: no dates in item titles when a date line sits beneath
    MD = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.? (\d{1,2}\b|\d{4})"
    for m in re.finditer(r'font-weight:bold[^>]*>([^<]{3,120})</td>(.{0,2500}?)</table>\s*<div style="font-size:14px;color:#666666;margin-top:2px;">((Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day, [^<]+)</div>', html, re.S):
        if re.search(MD, m.group(1)): fails.append(f"R19 title repeats a date above its date line: '{m.group(1)[:60]}' / '{m.group(3)}'")
    # R20: the issue links to its own week's Recurring pages, whose range starts on the publication date
    import datetime as _dt
    mm = re.search(r"(?:Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day, (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", html)
    if mm:
        iso = _dt.datetime.strptime(" ".join(mm.groups()), "%B %d %Y").date().isoformat()
        for d, k in re.findall(r'href="[^"]*?/pages/(\d{4}-\d{2}-\d{2})-recurring-activities-by-(date|name|location)\.html', html):
            if d != iso: fails.append(f"R20 Recurring link by-{k} points to the {d} pages, not this issue's {iso} pages"); continue
            pg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pages", f"{d}-recurring-activities-by-{k}.html")
            if not os.path.exists(pg): fails.append(f"R20 missing page pages/{d}-recurring-activities-by-{k}.html"); continue
            sub = re.search(r'ph-section-sub">([A-Z][a-z]+) (\d{1,2}) through', open(pg, encoding="utf-8").read())
            if not sub or _dt.datetime.strptime(f"{sub.group(1)[:3]} {sub.group(2)} {mm.group(3)}", "%b %d %Y").date().isoformat() != iso:
                fails.append(f"R20 {d}-recurring-activities-by-{k}.html range does not start on the issue date {iso}")
    # R13: meeting Agenda →/Zoom → (and any Zoom link on the newsletter page) must be palmhillnews Vercel pages
    for h, t in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>((?:(?!</a>).)*?)</a>', html, re.S):
        txt = re.sub(r"<[^>]+>", "", t).strip()
        if (re.match(r"(Agenda|Zoom)\b", txt) or "zoom.us" in h) and not h.startswith(("https://palmhillnews.vercel.app/", "/pages/")) and not re.match(r"^[\w./-]+\.html$", h):
            fails.append(f"R13 meeting link '{txt[:20]}' goes outside Vercel: {h.split('?')[0]}")
    return fails

def listen_checks(listens, view):
    fails = []
    for i, l in enumerate(listens):
        if l["ws"] != "nowrap": fails.append(f"R1 [{view}] Listen #{i+1} white-space={l['ws']} (must be nowrap)")
        if l["h"] > l["lh"] * 1.6: fails.append(f"R1 [{view}] Listen #{i+1} wraps (height {l['h']:.0f}px)")
        if not (8 <= l["inset"] <= 24): fails.append(f"R1 [{view}] Listen #{i+1} right inset {l['inset']}px (want ~14px)")
    return fails

def compare(a_path, b_path, diff_path):
    a, b = Image.open(a_path).convert("RGB"), Image.open(b_path).convert("RGB")
    if abs(a.height - b.height) > HEIGHT_TOL * 2 or a.width != b.width:
        return f"size {b.size} -> {a.size}"
    h = min(a.height, b.height); a, b = a.crop((0, 0, a.width, h)), b.crop((0, 0, b.width, h))
    d = np.asarray(ImageChops.difference(a, b)).max(axis=2) > 32
    ratio = d.mean()
    if ratio > PIXEL_TOL:
        m = Image.fromarray((d * 255).astype("uint8")); hl = a.copy(); hl.paste((255, 0, 0), mask=m); hl.save(diff_path)
        return f"{ratio:.2%} pixels changed"
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("page"); ap.add_argument("--golden", required=True)
    ap.add_argument("--capture", action="store_true"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    url = a.page if re.match(r"https?://", a.page) else pathlib.Path(a.page).resolve().as_uri()
    html = open(a.page, encoding="utf-8").read() if not url.startswith("http") else None
    gold = pathlib.Path(a.golden); out = pathlib.Path(a.out or (gold.parent / ("run-" + gold.name)))
    (gold if a.capture else out).mkdir(parents=True, exist_ok=True)
    fails, diffs, manifest = [], [], {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for view, kw in VIEWS.items():
            pg = br.new_page(**kw); pg.goto(url, wait_until="networkidle", timeout=60000)
            if html is None: html = pg.content()
            pg.evaluate(MASK_JS)
            fails += listen_checks(pg.evaluate(LISTEN_JS), view)
            if view == "mobile":  # R18: item summaries max 3 lines at 390px (and 660px below)
                fails += [f"R18 [390px] {x['sec'][:30]} / {x['title'][:40]}: summary is {x['lines']} lines (max 3)" for x in pg.evaluate(SUMMARY_JS) if x["lines"] > 3]
            for s in pg.evaluate(SECTIONS_JS):
                name = f"{s['i']:02d}-{slug(s['title'])}-{view}.png"; manifest[name] = s["title"]
                dst = (gold if a.capture else out) / name
                pg.screenshot(path=str(dst), full_page=True, clip={"x": s["x"], "y": s["y"], "width": s["w"], "height": max(1, s["h"])})
                if not a.capture:
                    g = gold / name
                    if not g.exists(): diffs.append(f"{name}: new section (no golden)"); continue
                    r = compare(dst, g, out / name.replace(".png", "-DIFF.png"))
                    if r: diffs.append(f"{name}: {r}")
            pg.close()
        p660 = br.new_page(viewport={"width": 660, "height": 900}); p660.goto(url, wait_until="networkidle", timeout=60000)
        fails += [f"R18 [660px] {x['sec'][:30]} / {x['title'][:40]}: summary is {x['lines']} lines (max 3)" for x in p660.evaluate(SUMMARY_JS) if x["lines"] > 3]
        br.close()
    fails = rule_checks(html, None) + fails
    if a.capture:
        (gold / "manifest.json").write_text(json.dumps(manifest, indent=1))
    else:
        for n in json.loads((gold / "manifest.json").read_text()) if (gold / "manifest.json").exists() else []:
            if n not in manifest: diffs.append(f"{n}: section missing")
    rep = ["PHNEWS format guard — " + a.page, f"rule failures: {len(fails)}", *("  FAIL " + f for f in fails),
           f"visual diffs vs {gold.name}: {'(golden captured)' if a.capture else len(diffs)}", *("  DIFF " + d for d in diffs)]
    print("\n".join(rep))
    if not a.capture: (out / "REPORT.txt").write_text("\n".join(rep) + "\n")
    sys.exit(1 if fails else (2 if diffs else 0))

if __name__ == "__main__": main()
