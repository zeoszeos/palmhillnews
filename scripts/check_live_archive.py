#!/usr/bin/env python3
"""STYLE-RULES R44 live check (Steven, Oct 18 12:07 AM; batch 6 item A).
Run after every production deploy. For every non-issue pages/archive page it fetches production with a cache-busting
query, compares the bytes to the repo copy, and runs the R44 top-area check (one 'All Archives →') and R46 (no lower
cross-links on videos.html), then runs the R49 Listen-coverage guard on every Listen page live. A mismatch means the deploy has not landed (or a stale copy is served); exit 1.
Usage: python3 scripts/check_live_archive.py [--base https://palmhillnews.vercel.app]"""
import os, re, sys, time, hashlib, urllib.request
sys.path.insert(0, os.path.dirname(__file__)); import style_rules as SR
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "https://palmhillnews.vercel.app"
bust = str(int(time.time()))
bad, n = [], 0
for dp, _, fs in os.walk(os.path.join(R, "pages", "archive")):
    for f in sorted(fs):
        rel = os.path.relpath(os.path.join(dp, f), R).replace(os.sep, "/")
        if not f.endswith(".html") or rel.startswith("pages/archive/issues/"): continue
        local = open(os.path.join(dp, f), "rb").read()
        if re.search(rb'http-equiv="?refresh', local, re.I): continue
        try:
            req = urllib.request.Request(f"{base}/{rel}?cb={bust}", headers={"Cache-Control": "no-cache", "User-Agent": "phnews-live-check"})
            live = urllib.request.urlopen(req, timeout=30).read()
        except Exception as e:
            bad.append(f"{rel}: fetch failed {e}"); continue
        n += 1
        if hashlib.sha256(live).digest() != hashlib.sha256(local).digest(): bad.append(f"{rel}: live bytes differ from repo (deploy not landed?)")
        s = live.decode("utf-8", "ignore")
        v = SR.archive_top_violations(s, is_hub=(rel == "pages/archive/main.html"))
        if v: bad.append(f"{rel}: R44 {'; '.join(v)}")
        if rel == "pages/archive/videos.html" and ('class="ph-links"' in s or "Committee Meeting Video Archives →" in s):
            bad.append(f"{rel}: R46 lower cross-links present")
# STYLE-RULES R49: every Listen page, as served by production, reads all visible content
import subprocess as _sp49
_lc_py = os.environ.get("PHNEWS_VR_PY", "/workspace/.venv-vr/bin/python")
_r49 = _sp49.run([_lc_py, os.path.join(R, "scripts", "check_listen_coverage.py"), "--live", base], capture_output=True, text=True)
print((_r49.stdout or _r49.stderr).strip()[:3000])
if _r49.returncode: bad.append("R49 live Listen coverage failed (see above)")
print(f"live archive pages checked: {n}; problems: {len(bad)}")
for b in bad: print("  " + b)
sys.exit(1 if bad else 0)
