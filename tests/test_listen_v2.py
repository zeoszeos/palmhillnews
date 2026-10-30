#!/usr/bin/env python3
"""R76 (Steven, Oct 25 2026 9:29 AM) Playwright test, desktop + iPhone emulation, on the Nov 1 dry-run output:
  1. a ?listen=1 page opened with BLOCKED autoplay shows the big 'Tap to listen' bar; one tap starts reading (title first);
  2. an archive page's Listen reads IN PLACE (no page change), the button turns to Stop, a second tap stops;
  3. the Nov 1 issue web copy (preview + the in-place block, as build_archive writes pages/archive/issues/<date>.html)
     reads a card's Listen in place;
  4. the Nov 1 preview / SEND-like file has no <script>.
Usage: /workspace/pwvenv/bin/python tests/test_listen_v2.py [--shots DIR]"""
import os, sys, re, mimetypes
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(R, "scripts"))
import page_listen as PL
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
ISSUE = "2026-11-01"; PREV = f"pages/previews/{ISSUE}/PHNEWS-{ISSUE}-preview.html"
NOTICE = "pages/2026-10-23-holiday-greeting-distribution-plan.html"; ARCH = "pages/archive/presidents-message.html"
SLOW_BLOCK = """(() => { window.__spoken = []; window.__cancel = 0; let unlocked = false, cur = null;
  const synth = {speaking: false, pending: false, paused: false, getVoices: () => [], pause() {}, resume() {},
    cancel() { window.__cancel++; if (cur) { clearTimeout(cur.t); const u = cur.u; cur = null; u.onerror && u.onerror({error: 'canceled'}); } },
    speak(u) { if (!unlocked && !(navigator.userActivation && navigator.userActivation.isActive)) return; unlocked = true;
      if (u.text.trim()) window.__spoken.push(u.text);
      const t = setTimeout(() => { cur = null; u.onend && u.onend({}); }, u.text.trim() ? 1500 : 0); cur = {u, t}; setTimeout(() => u.onstart && u.onstart({}), 0); },
    addEventListener() {}, removeEventListener() {}};
  Object.defineProperty(window, 'speechSynthesis', {value: synth, configurable: true});
  window.SpeechSynthesisUtterance = function (t) { this.text = t; }; })();"""
ISSUE_WEB = PL.add_inplace(open(os.path.join(R, PREV), encoding="utf-8").read())
def serve(route):
    from urllib.parse import urlparse
    u = urlparse(route.request.url)
    if u.hostname != "palmhillnews.vercel.app": return route.continue_() if re.search(r"\.(png|jpe?g|gif|webp|svg|css|woff2?)$", u.path) else route.abort()
    p = u.path.lstrip("/")
    if p == f"pages/archive/issues/{ISSUE}.html": return route.fulfill(body=ISSUE_WEB, content_type="text/html")
    f = os.path.join(R, p)
    if not os.path.exists(f) and os.path.exists(os.path.join(R, "public", p)): f = os.path.join(R, "public", p)  # assets live in public/
    if os.path.isdir(f): f = os.path.join(f, "index.html")
    if not os.path.exists(f): return route.continue_() if not p.endswith(".html") else route.fulfill(status=404, body="nf")  # images: production
    route.fulfill(body=open(f, "rb").read(), content_type=mimetypes.guess_type(f)[0] or "application/octet-stream")
B = "https://palmhillnews.vercel.app/"
def main():
    from playwright.sync_api import sync_playwright
    fails = []; ok = lambda c, m: (print(("PASS " if c else "FAIL ") + m), c or fails.append(m))
    ok("<script" not in open(os.path.join(R, PREV), encoding="utf-8").read().lower(), "Nov 1 preview (= SEND body) has no <script>")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name, opts in (("desktop", {"viewport": {"width": 1280, "height": 900}}), ("iphone", pw.devices["iPhone 13"])):
            ctx = b.new_context(**opts); ctx.add_init_script(SLOW_BLOCK); ctx.route("**/*", serve)
            pg = ctx.new_page(); pg.goto(B + NOTICE + "?listen=1", wait_until="load")
            pg.wait_for_selector(".ph-tap-bar", state="visible", timeout=2500)
            ok(pg.evaluate("() => window.__spoken.length") == 0, f"{name}: blocked autoplay -> Tap to listen bar shown, nothing spoken")
            if SHOTS and name == "iphone": pg.screenshot(path=f"{SHOTS}/1-tap-to-listen-bar-iphone.png")
            if SHOTS and name == "desktop": pg.screenshot(path=f"{SHOTS}/1b-tap-to-listen-bar-desktop.png")
            (pg.tap if name == "iphone" else pg.click)(".ph-tap-bar"); pg.wait_for_timeout(300)
            h1 = pg.evaluate("() => document.querySelector('h1').textContent")
            first = pg.evaluate("() => window.__spoken[0] || ''")
            ok(bool(first) and first.replace(" ", "")[:15] in h1.replace(" ", "").replace("\n", ""), f"{name}: tap on bar starts reading from the title ({first[:40]!r})")
            ok(pg.query_selector(".ph-tap-bar") is None, f"{name}: bar gone after tap")
            for label, url, sel in (("archive", B + ARCH, "a.ph-listen"), ("issue page", B + f"pages/archive/issues/{ISSUE}.html", 'a[href*="listen=1"]')):
                pg = ctx.new_page(); pg.goto(url, wait_until="load"); a = pg.locator(sel).first; a.scroll_into_view_if_needed()
                if SHOTS and name == "iphone" and label == "issue page":
                    pg.evaluate("(s) => { const a = document.querySelector(s); const r = a.closest('table') || a.parentElement; r.style.outline = '3px dashed #c00'; }", sel)
                    pg.screenshot(path=f"{SHOTS}/2-issue-card-listen-before-iphone.png"); pg.evaluate("(s) => { const a = document.querySelector(s); (a.closest('table') || a.parentElement).style.outline = ''; }", sel)
                (a.tap if name == "iphone" else a.click)(); pg.wait_for_timeout(700)
                ok(pg.url == url, f"{name} {label}: Listen reads in place (no page change)")
                ok(len(pg.evaluate("() => window.__spoken")) > 0, f"{name} {label}: speech started ({(pg.evaluate('() => window.__spoken[0]') or '')[:40]!r})")
                ok("Stop" in a.inner_text() and a.get_attribute("aria-pressed") == "true", f"{name} {label}: button shows Stop")
                if SHOTS and name == "iphone": pg.screenshot(path=f"{SHOTS}/3-{label.replace(' ', '-')}-stop-state-iphone.png")
                n = len(pg.evaluate("() => window.__spoken")); (a.tap if name == "iphone" else a.click)(); pg.wait_for_timeout(2000)
                ok("Listen" in a.inner_text() and len(pg.evaluate("() => window.__spoken")) == n and pg.url == url, f"{name} {label}: second tap stops (back to Listen)")
            ctx.close()
        # no speech support -> the link still opens the listen page
        ctx = b.new_context(); ctx.add_init_script("delete window.speechSynthesis; delete window.SpeechSynthesisUtterance;"); ctx.route("**/*", serve)
        pg = ctx.new_page(); pg.goto(B + ARCH, wait_until="load"); href = pg.locator("a.ph-listen").first.get_attribute("href")
        pg.locator("a.ph-listen").first.click(); pg.wait_for_load_state("load")
        ok(pg.url.split("?")[0] == href.split("?")[0], "no speech support: Listen link opens the listen page (fallback)")
        b.close()
    print("test_listen_v2:", "PASS" if not fails else f"FAIL ({len(fails)})"); return 1 if fails else 0
if __name__ == "__main__": sys.exit(main())
