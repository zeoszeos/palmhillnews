#!/usr/bin/env python3
"""STYLE-RULES R38 guard (rendered, 1280px + 390px): on a banded archive page every .ph-row has a title band (.ph-band-a|b)
holding the title; a header band sits between the header block and the first item with margin-top >= 20px; titles keep the
baseline 15px / bold (700); band text contrast meets WCAG AA (>= 4.5:1).
Usage: /workspace/.venv-vr/bin/python scripts/check_title_band.py pages/archive/did-you-know.html"""
import sys, os, re
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def lum(c):
    r, g, b = [int(x) / 255 for x in re.findall(r"\d+", c)[:3]]
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
def ratio(a, b): la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
page = sys.argv[1]; fails = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    for w, tag in [(1280, "desktop"), (390, "mobile")]:
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.route("**/pages/assets/**", lambda r: r.fulfill(path=os.path.join(ROOT, r.request.url.split("/pages/", 1)[1].join(["pages/", ""]))))
        pg.goto("file://" + os.path.join(ROOT, page))
        d = pg.evaluate("""() => {
          const rows=[...document.querySelectorAll('.ph-row')], hb=document.querySelector('.ph-band-head');
          const first=rows[0];
          return {n:rows.length, banded:rows.filter(r=>r.querySelector(':scope > .ph-band .ph-row-title')).length,
            head: !!hb, headBefore: !!(hb && first && (hb.compareDocumentPosition(first) & Node.DOCUMENT_POSITION_FOLLOWING)),
            headMargin: hb ? parseFloat(getComputedStyle(hb).marginTop) : 0,
            titles: rows.map(r=>{const t=r.querySelector('.ph-row-title'), bd=r.querySelector('.ph-band'); const cs=getComputedStyle(t);
              return {fs:cs.fontSize, fw:cs.fontWeight, fg:cs.color, bg: bd?getComputedStyle(bd).backgroundColor:''};})};
        }""")
        if not d["head"] or not d["headBefore"]: fails.append(f"[{tag}] header band missing or not before the first item")
        if d["headMargin"] < 20: fails.append(f"[{tag}] header band margin-top {d['headMargin']}px < 20px")
        if d["banded"] != d["n"]: fails.append(f"[{tag}] bands on {d['banded']}/{d['n']} items")
        for i, t in enumerate(d["titles"]):
            if t["fs"] != "15px" or t["fw"] not in ("700", "bold"): fails.append(f"[{tag}] item {i+1} title {t['fs']}/{t['fw']} (want 15px/700)")
            if t["bg"] and ratio(t["fg"], t["bg"]) < 4.5: fails.append(f"[{tag}] item {i+1} contrast {ratio(t['fg'], t['bg']):.2f}:1 < 4.5")
        if tag == "desktop" and d["titles"]: t = d["titles"][0]; print(f"title {t['fg']} on {t['bg']}: {ratio(t['fg'], t['bg']):.2f}:1")
    b.close()
print(f"R38 title-band guard — {page}: {len(fails)} failure(s)"); [print("  FAIL", f) for f in fails]
sys.exit(1 if fails else 0)
