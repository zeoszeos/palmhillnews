#!/usr/bin/env python3
"""STYLE-RULES R28 guard (Steven, Oct 17 2026): on archive section pages whose rows carry Listen on the bottom
"In the newsletter" line (pages/archive/committee-reports.html), every Listen is the speaker icon + "Listen", one line
(nowrap), right-justified ~14px in from the row edge, on the same visual line as "In the newsletter", and the date line has
no "Listen →". Checked at desktop 1280px and mobile 390px. Optional --golden DIR [--capture] compares/saves full-page PNGs.
Usage: /workspace/.venv-vr/bin/python scripts/check_archive_listen.py pages/archive/committee-reports.html [--golden DIR] [--capture]"""
import sys, pathlib, argparse
from playwright.sync_api import sync_playwright
JS = r"""() => [...document.querySelectorAll('.ph-row')].filter(r => r.querySelector('a[href*="listen"]')).map(r => {
  const a = r.querySelector('a.ph-listen'); const foot = r.querySelector('.ph-row-foot');
  const meta = foot && foot.querySelector('.ph-row-meta'); const rr = r.getBoundingClientRect();
  const dateLine = [...r.querySelectorAll(':scope > .ph-row-meta')].map(m => m.textContent).join(' | ');
  if (!a) return {title: r.querySelector('.ph-row-title')?.textContent, err: 'no speaker Listen'};
  const ar = a.getBoundingClientRect(), mr = meta ? meta.getBoundingClientRect() : null, cs = getComputedStyle(a);
  return {title: r.querySelector('.ph-row-title')?.textContent.slice(0, 40), icon: !!a.querySelector('img[src*="speaker-read-aloud"]'),
    ws: cs.whiteSpace, h: Math.round(ar.height), inset: Math.round(rr.right - ar.right), inFoot: !!(foot && foot.contains(a)),
    nl: !!(meta && /^In the newsletter:/.test(meta.textContent.trim())), sameLine: !!(mr && ar.top < mr.bottom && ar.bottom > mr.top),
    dateListen: /Listen/.test(dateLine)}; })"""
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("page"); ap.add_argument("--golden"); ap.add_argument("--capture", action="store_true"); a = ap.parse_args()
    # serve the repo over http so /pages/assets/ph-newsletter.css resolves exactly as on Vercel
    import http.server, threading, functools, os
    root = pathlib.Path(__file__).resolve().parent.parent
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *x): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_port}/" + os.path.relpath(pathlib.Path(a.page).resolve(), root); fails = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for view, kw in {"desktop": dict(viewport={"width": 1280, "height": 900}), "mobile": dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True)}.items():
            pg = b.new_page(**kw); pg.goto(url, wait_until="networkidle")
            rows = pg.evaluate(JS)
            if not rows: fails.append(f"[{view}] no Listen rows found")
            for r in rows:
                if r.get("err"): fails.append(f"R28 [{view}] {r['title']}: {r['err']}"); continue
                bad = [k for k, ok in (("icon", r["icon"]), ("nowrap", r["ws"] == "nowrap"), ("one line", r["h"] <= 32), ("inset~14px", 10 <= r["inset"] <= 18),
                       ("on In the newsletter line", r["inFoot"] and r["nl"] and r["sameLine"]), ("date line has no Listen", not r["dateListen"])) if not ok]
                if bad: fails.append(f"R28 [{view}] {r['title']}: {', '.join(bad)} ({r})")
            if a.golden:
                g = pathlib.Path(a.golden); g.mkdir(parents=True, exist_ok=True)
                pg.screenshot(path=str(g / f"page-{view}.png") if a.capture else f"/tmp/r28-{view}.png", full_page=True)
            pg.close()
    print(f"R28 archive Listen guard — {a.page}: {len(fails)} failure(s)"); [print("  FAIL", f) for f in fails]
    sys.exit(1 if fails else 0)
if __name__ == "__main__": main()
