#!/usr/bin/env python3
"""STYLE-RULES R49 guard (Steven, Oct 18 12:39 AM): the Listen reader reads ALL visible article text.
For every page with a Listen script (speechSynthesis), load it in Chromium with a recording speech mock, tap Listen,
collect every spoken utterance, and compare with the page's visible text blocks (p, li, blockquote/pull quotes, h2-h6,
figcaption, table cells, dt/dd, pre, bare div/span text, the subtitle/byline and the closing source/credit line) inside
<main> (or <article>). A visible block whose text is not in the spoken text, or a long block read twice, is a FAIL.
Intentionally unread: the kicker, date line, navigation / archive links, Listen and Back controls, the email header row
(Subject/From/Sent) and the date line that repeats its Sent time, attachment lists, link-only rows ending in '→', buttons.
Usage: /workspace/.venv-vr/bin/python scripts/check_listen_coverage.py [PAGE.html ...] [--live [BASE]]
  (default: every Listen page in the repo; --live loads them from production; exit 1 on misses)
Required step (Steven, Oct 18 12:41 AM): every page generator, preview and publish call require(paths) on the pages
they write; check_site_links.py runs it on all Listen pages; check_live_archive.py runs it --live after deploy."""
import os, re, sys, json, threading, functools, http.server, socketserver
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK = """(() => {
  window.__spoken = [];
  const synth = {speaking: false, pending: false, paused: false, getVoices: () => [], cancel() {}, pause() {}, resume() {},
    speak(u) { window.__spoken.push(u.text); setTimeout(() => { u.onstart && u.onstart({}); u.onend && u.onend({}); }, 0); },
    addEventListener() {}, removeEventListener() {}};
  Object.defineProperty(window, 'speechSynthesis', {value: synth, configurable: true});
  window.SpeechSynthesisUtterance = function (t) { this.text = t; };
})();"""
VISIBLE = r"""() => {
  const root = document.querySelector('main') || document.querySelector('article') || document.body;
  const BLOCK = 'p,li,blockquote,h2,h3,h4,h5,h6,figcaption,td,th,dd,dt,pre,caption';
  const SKIP = 'h1,nav,header,footer,button,script,style,noscript,[role="navigation"],.ph-story-nav,.ph-story-links-long,.ph-archive-bar,.ph-dateline,.page-kicker,.ph-listen,.attachments,.ph-strip,.ph-links,[aria-hidden="true"]';
  const vis = (el) => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
  const out = [];
  for (const el of root.querySelectorAll(BLOCK)) {
    if (el.closest(SKIP) || !vis(el) || el.querySelector(BLOCK)) continue;
    const a = el.querySelectorAll('a');
    const linkOnly = a.length === 1 && a[0].innerText.trim() === el.innerText.trim() && /→\s*$/.test(el.innerText);  // a link row, not text
    const emailDate = el.classList.contains('ph-meta') && /Sent:/.test(root.innerText) && root.innerText.includes('Sent: ' + el.innerText.trim());  // duplicate of the skipped email header
    if (linkOnly || emailDate) continue;
    out.push({tag: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''), text: el.innerText});
  }
  // bare text in div/span etc. that is not inside any block element
  const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (tw.nextNode()) {
    const n = tw.currentNode; const p = n.parentElement;
    if (!n.textContent.trim() || !p || p.closest(BLOCK) || p.closest(SKIP) || p.closest('h1') || !vis(p)) continue;
    let host = p; while (host !== root && getComputedStyle(host).display.startsWith('inline')) host = host.parentElement;
    if (seen.has(host)) continue; seen.add(host);
    out.push({tag: host.tagName.toLowerCase() + (host.className ? '.' + String(host.className).split(' ')[0] : '') + '(text)', text: host.innerText});
  }
  return out;
}"""
MON = dict(Jan="January", Feb="February", Mar="March", Apr="April", Jun="June", Jul="July", Aug="August", Sep="September", Oct="October", Nov="November", Dec="December")
def norm(t):
    t = re.sub(r"\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b\.?", lambda m: MON[m.group(1)], t)
    return re.sub(r"\s+", "", t).lower()  # whitespace-insensitive: the reader re-joins sentences (URLs, ellipses) with spaces
INTENTIONAL = re.compile(r"^(subject:|from:|sent:|← back|listen$|stop$)", re.I)  # Source / credit lines ARE required (12:43 AM)
def listen_pages():
    out = []
    for dp, _, fs in os.walk(os.path.join(R, "pages")):
        for f in fs:
            if f.endswith(".html") and "/issues" not in dp:
                p = os.path.join(dp, f)
                t = open(p, errors="ignore").read()
                if "speechSynthesis" in t and 'class="ph-listen"' in t: out.append(os.path.relpath(p, R))
    return sorted(out)
VENV_PY = os.environ.get("PHNEWS_VR_PY", "/workspace/.venv-vr/bin/python")
def require(paths, name="R49"):
    """Run this guard on the given page files (generators call this after writing pages); stop the build on any miss."""
    import subprocess
    paths = [str(p) for p in paths if str(p).endswith(".html") and os.path.exists(str(p)) and "speechSynthesis" in open(str(p), errors="ignore").read()]
    if not paths: return
    if not os.path.exists(VENV_PY): raise SystemExit(f"{name}: Listen-coverage guard needs {VENV_PY} (playwright); it is a required step")
    r = subprocess.run([VENV_PY, os.path.abspath(__file__), *paths], capture_output=True, text=True)
    print((r.stdout or r.stderr).strip()[:3000])
    if r.returncode: raise SystemExit(f"{name}: Listen does not read all visible content (see above)")
def require_since(t0, name="R49"):
    """require() on every page under pages/ written since t0 (a generator's start time)."""
    out = []
    for dp, _, fs in os.walk(os.path.join(R, "pages")):
        if "/archive/issues" in dp: continue
        out += [os.path.join(dp, f) for f in fs if f.endswith(".html") and os.path.getmtime(os.path.join(dp, f)) >= t0]
    require(out, name)
def main(args, live=None):
    pages = [os.path.relpath(os.path.abspath(a), R) for a in args] or listen_pages()
    H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=R)
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), H); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright  # only the checker process needs playwright (require() shells out)
    fails = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(); ctx = b.new_context(); ctx.add_init_script(MOCK)
        if not live: ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())  # offline: fonts/images from production not needed
        for rel in pages:
            pg = ctx.new_page()
            try:
                url = f"{live.rstrip('/')}/{rel}?autoplay=0&cb={os.getpid()}" if live else f"http://127.0.0.1:{port}/{rel}?autoplay=0"
                pg.goto(url, wait_until="load", timeout=30000)
                pg.evaluate("() => { const a = document.querySelector('a.ph-listen'); if (a) a.click(); }")
                last = -1
                for _ in range(60):
                    n = pg.evaluate("() => window.__spoken.length")
                    if n == last and n > 0: break
                    last = n; pg.wait_for_timeout(100)
                spoken = norm(" ".join(pg.evaluate("() => window.__spoken")))
                miss = []
                blocks = pg.evaluate(VISIBLE)
                for blk in blocks:
                    t = blk["text"].strip()
                    if not t or INTENTIONAL.match(t) or not re.search(r"[A-Za-z0-9]", t): continue
                    if norm(t) not in spoken: miss.append(f"{blk['tag']}: {re.sub(r'\s+', ' ', t)[:90]}")
                    elif len(norm(t)) > 60 and spoken.count(norm(t)) > 1 and sum(norm(x["text"]) == norm(t) for x in blocks) == 1:
                        miss.append(f"double-read {blk['tag']}: {re.sub(r'\s+', ' ', t)[:90]}")
                if not spoken: miss.insert(0, "nothing spoken")
                if miss: fails[rel] = miss
            except Exception as e:
                fails[rel] = [f"page error: {str(e).splitlines()[0][:160]}"]
            finally:
                pg.close()
        b.close()
    srv.shutdown()
    print(f"R49 Listen coverage{' (LIVE ' + live + ')' if live else ''}: {len(pages)} pages checked, {len(fails)} with unread visible text")
    for rel, m in fails.items():
        print("  FAIL " + rel); [print("      " + x) for x in m[:8]]; len(m) > 8 and print(f"      ... +{len(m) - 8} more")
    return 1 if fails else 0
if __name__ == "__main__":
    a = sys.argv[1:]; live = None
    if "--live" in a:
        i = a.index("--live"); live = a[i + 1] if i + 1 < len(a) and not a[i + 1].endswith(".html") else "https://palmhillnews.vercel.app"
        a = [x for x in a if x not in ("--live", live)]
    sys.exit(main([x for x in a if not x.startswith("--")], live))
