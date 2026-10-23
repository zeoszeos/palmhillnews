#!/usr/bin/env python3
"""STYLE-RULES R60 (Steven Oct 21 8:34 PM): Community Notices guard. Fails the build when any main-page notice
(a) renders more than 3 lines at 390px or 660px (R18), (b) is trimmed (its source text is in summary_trim.SHORT with a
full-text page) but lacks More → to that page (R23/R47), or (c) has a #listen-pending Listen or a pages/previews/ link."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import summary_trim as _st

def section(s):
    h = s.find(">Community Notices</span>"); assert h > 0, "R60: Community Notices section not found"
    e = min([x for x in (s.find('<div class="canonical-section">', h + 1), s.find('<div class="section04">', h + 1)) if x > 0] or [len(s)])
    return s[h:e]

def static(s):
    sec, fails = section(s), []
    if "#listen-pending" in sec: fails.append("R60: #listen-pending Listen in Community Notices")
    for u in re.findall(r'(?:href|src)="([^"]*previews/[^"]*)"', sec): fails.append(f"R60: preview link {u}")
    for pre, short, url in _st.SHORT:
        if url and short in sec:
            i = sec.find(short); blk = sec[i:sec.find("</div>", i)]
            if f'href="{url}"' not in blk or "More →" not in blk: fails.append(f"R60: trimmed notice {short[:40]!r} lacks More → {url}")
    # R47/R60 (Oct 23): every Webmaster notice carries More → to the same page as its Source link
    for row in sec.split('<tr style="background:')[1:]:
        m = re.search(r'Source: <a href="([^"]+)"[^>]*>Webmaster</a>', row)
        if m and not re.search(r'href="' + re.escape(m.group(1)) + r'"[^>]*>More →', row): fails.append(f"R60/R47: Webmaster notice without More → {m.group(1)}")
    for row in re.findall(r'margin-top:3px;">(.*?)</div>', sec, re.S):
        txt = re.sub(r"<[^>]+>", "", row)
        if len(txt) > 260 and "More →" not in txt: fails.append(f"R60: long notice without More → {txt[:50]!r}")
    return fails

VR = "/workspace/.venv-vr/bin/python"
def rendered(path):
    try: from playwright.sync_api import sync_playwright
    except ImportError:  # builder python has no playwright: measure in the visual-regression venv (fails closed)
        import subprocess, json
        r = subprocess.run([VR, __file__, "--rendered-json", path], capture_output=True, text=True)
        if r.returncode: raise SystemExit("R60: rendered check could not run: " + r.stderr[-400:])
        return json.loads(r.stdout.strip().splitlines()[-1])
    js = open(os.path.join(os.path.dirname(__file__), "summary_lines.js")).read()
    fails = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in (390, 660):
            pg = b.new_page(viewport={"width": w, "height": 900}); pg.goto("file://" + os.path.abspath(path))
            for x in pg.evaluate(js):
                if x["sec"].startswith("Community Notices") and x["lines"] > 3: fails.append(f"R60/R18 [{w}px] {x['title'][:40]}: {x['lines']} lines")
        b.close()
    return fails

def check(path):
    s = open(path, encoding="utf-8").read()
    f = static(s) + rendered(path)
    if f: raise SystemExit("Community Notices guard FAILED:\n  " + "\n  ".join(f))
    print("R60 Community Notices guard OK:", path)

if __name__ == "__main__":
    if sys.argv[1:2] == ["--rendered-json"]:
        import json; print(json.dumps(rendered(sys.argv[2]))); sys.exit(0)
    for a in sys.argv[1:]: check(a)
