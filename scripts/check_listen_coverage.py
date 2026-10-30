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
they write; check_site_links.py runs it on all Listen pages; check_live_archive.py runs it --live after deploy.
R49b (Steven, Oct 18 2:05 AM -- 2026-10-16-weekly-manager-update.html had the script but no button, so it never played and
the old page list, which needed BOTH script and button, skipped it): the page set is now
  (1) every page with ANY Listen part (script or button) -- a page with one but not the other FAILS;
  (2) every page that SHOULD have Listen (required_pages(): story / message / report / notice archive pages, any page whose
      name says notice / report / message / weekly update, and every email copy with a Subject/From/Sent header), minus
      the short EXEMPT list -- a required page without Listen FAILS;
  (3) every page an NL links with ?listen=1 (archived issues, previews, the SEND; add more with --nl FILE) -- the target
      must exist, have Listen, and START READING on its own when opened with ?listen=1 (no tap), title first."""
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
# R76 (Oct 25 2026): a fake voice that BLOCKS like iPhone Safari opened from an email -- speak() is silent (no 'start')
# until the first call made during a real tap; after that, speech works (the browser is unlocked).
MOCK_BLOCK = """(() => {
  window.__spoken = []; let unlocked = false;
  const synth = {speaking: false, pending: false, paused: false, getVoices: () => [], cancel() {}, pause() {}, resume() {},
    speak(u) { if (!unlocked && !(navigator.userActivation && navigator.userActivation.isActive)) return; unlocked = true;
      if (u.text.trim()) window.__spoken.push(u.text); setTimeout(() => { u.onstart && u.onstart({}); u.onend && u.onend({}); }, 0); },
    addEventListener() {}, removeEventListener() {}};
  Object.defineProperty(window, 'speechSynthesis', {value: synth, configurable: true});
  window.SpeechSynthesisUtterance = function (t) { this.text = t; };
})();"""
V2_MARK = 'data-ph-listen-v="2"'
def blocked_case(ctxb, base, rel):
    """R76: ?listen=1 with blocked autoplay must show the Tap to listen bar within 2.5 s (nothing spoken), and one tap on
    the bar must start reading from the title. Returns a list of problems (empty = pass)."""
    pg = ctxb.new_page(); out = []
    try:
        pg.goto(f"{base}/{rel}?listen=1&cb={os.getpid()}", wait_until="load", timeout=30000)
        try: pg.wait_for_selector(".ph-tap-bar", state="visible", timeout=2500)
        except Exception: return ["blocked autoplay: no 'Tap to listen' bar within 2.5 s (silent wait)"]
        bar = pg.query_selector(".ph-tap-bar"); txt = bar.inner_text(); box = bar.bounding_box()
        if "Tap to listen" not in txt: out.append(f"bar text is {txt!r}")
        if not box or box["y"] > 5 or box["height"] < 56: out.append(f"bar not big at the top: {box}")
        if pg.evaluate("() => window.__spoken.length"): out.append("spoke before the tap")
        bar.click(); pg.wait_for_timeout(600)
        first = pg.evaluate("() => window.__spoken[0] || ''"); h1 = pg.evaluate("() => (document.querySelector('h1') || {}).textContent || ''")
        if not first: out.append("tap on the bar did not start reading")
        elif norm(h1) and not norm(first).startswith(norm(h1)[:20]): out.append(f"after tap starts with '{first[:40]}', not the title")
        if pg.query_selector(".ph-tap-bar"): out.append("bar still shown after the tap")
    finally:
        pg.close()
    return out
VISIBLE = r"""() => {
  const root = document.querySelector('main') || document.querySelector('article') || document.body;
  const BLOCK = 'p,li,blockquote,h2,h3,h4,h5,h6,figcaption,td,th,dd,dt,pre,caption';
  const SKIP = 'h1,nav,header,footer,button,script,style,noscript,[role="navigation"],.ph-story-nav,.ph-story-links-long,.ph-archive-bar,.ph-dateline,.page-kicker,.ph-listen,.ph-listen-row,.badge,.meta,.date,.back,.attachments,.ph-strip,.ph-links,[aria-hidden="true"]';
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
    out.push({tag: host.tagName.toLowerCase() + (host.className ? '.' + String(host.className).split(' ')[0] : '') + '(text)', text: host === root ? (p === root ? n.textContent : p.innerText) : host.innerText});  // bare inline text straight in <body>: just that run
  }
  return out;
}"""
MON = dict(Jan="January", Feb="February", Mar="March", Apr="April", Jun="June", Jul="July", Aug="August", Sep="September", Oct="October", Nov="November", Dec="December")
def norm(t):
    t = re.sub(r"\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b\.?", lambda m: MON[m.group(1)], t)
    return re.sub(r"\s+", "", t).lower()  # whitespace-insensitive: the reader re-joins sentences (URLs, ellipses) with spaces
INTENTIONAL = re.compile(r"^(subject:|from:|sent:|← back|listen$|stop$)", re.I)  # Source / credit lines ARE required (12:43 AM)
def _pages():
    for dp, _, fs in os.walk(os.path.join(R, "pages")):
        if "/archive" in dp or "/previews" in dp or "/shared" in dp or "/assets" in dp: continue
        for f in fs:
            if f.endswith(".html"): yield os.path.relpath(os.path.join(dp, f), R)
def has_script(t): return "speechSynthesis" in re.sub(r"<!-- ph-inplace-listen:start -->.*?<!-- ph-inplace-listen:end -->", "", t, flags=re.S)  # R76: the website in-place block is not a page reader
def has_button(t): return 'class="ph-listen"' in t
def listen_pages():
    """(1) every page with any Listen part (script or button)."""
    out = []
    for rel in _pages():
        t = open(os.path.join(R, rel), errors="ignore").read()
        if has_script(t) or has_button(t): out.append(rel)
    return sorted(out)
REQ_SECTIONS = {"community-stories", "presidents-message", "committee-reports", "manager-reports", "weekly-manager-updates", "community-notices"}
REQ_NAME = re.compile(r"notice|report|message|weekly-manager|weekly-update|presidents-corner|-story", re.I)
EMAIL_COPY = re.compile(r">\s*Subject:.*?>\s*Sent:", re.S)
# Pages of a required type that cannot have Listen (keep this list short; Steven reviews it):
EXEMPT = {
    "pages/2026-07-15-monthly-management-and-maintenance-report-2026-07-.html": "image-only PDF page scans (no text to read); the PDF download is the source",
}
def required_pages():
    """(2) pages that SHOULD have Listen -> reason."""
    try: secs = json.load(open(os.path.join(R, "archive", "archive-items.json")))
    except Exception: secs = {}
    secs = secs.get("sections", secs) if isinstance(secs, dict) else {}
    mem = {}
    for k, s in secs.items():
        if isinstance(s, dict) and k in REQ_SECTIONS:
            for it in s.get("items", []):
                for key in ("page", "listen"):
                    if it.get(key): mem.setdefault("pages/" + it[key], k)
    out = {}
    for rel in _pages():
        if rel in EXEMPT: continue
        t = open(os.path.join(R, rel), errors="ignore").read()
        why = ("archive section " + mem[rel]) if rel in mem else ("page name" if REQ_NAME.search(os.path.basename(rel)) else ("email copy" if EMAIL_COPY.search(t) else None))
        if why: out[rel] = why
    return out
def _default_send():  # A6 (Oct 24): the current issue's SEND file (PHNEWS_ISSUE or newest preview folder)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import style_rules as _s
    iss = _s.current_issue(R)
    _w = os.environ.get("PHNEWS_WORK")  # R67 (batch 2): the issue work tree, when set, is checked first
    for c in ((f"{_w}/PHNEWS-{iss}-SEND.html",) if _w else ()) + (f"/workspace/phnews-consolidation/oct18/PHNEWS-{iss}-SEND.html", f"/workspace/oct18-additions/PHNEWS-{iss}-SEND.html"):
        if os.path.exists(c): return c
    return f"/workspace/oct18-additions/PHNEWS-{iss}-SEND.html"
DEFAULT_SEND = os.environ.get("PHNEWS_SEND_HTML") or _default_send()
def nl_files():
    out = []
    for dp, _, fs in os.walk(os.path.join(R, "pages")):
        if "/archive/issues" in dp or "/previews" in dp:
            out += [os.path.join(dp, f) for f in fs if f.endswith(".html") and "listen=1" in open(os.path.join(dp, f), errors="ignore").read()]
    if os.path.exists(DEFAULT_SEND): out.append(DEFAULT_SEND)
    return sorted(out)
LISTEN1 = re.compile(r'href="(?:https://palmhillnews\.vercel\.app)?/?(pages/[^"?#]+\.html)\?(?:[^"]*&)?listen=1[^"]*"')
def nl_targets(files):
    """(3) page -> NL files that link it with ?listen=1."""
    out = {}
    for f in files:
        for rel in LISTEN1.findall(open(f, errors="ignore").read()): out.setdefault(rel, []).append(os.path.basename(f))
    return out
VENV_PY = os.environ.get("PHNEWS_VR_PY", "/workspace/.venv-vr/bin/python")
def require(paths, name="R49"):
    """Run this guard on the given page files (generators call this after writing pages); stop the build on any miss."""
    import subprocess
    req = required_pages()
    def wanted(p):
        if not (p.endswith(".html") and os.path.exists(p)): return False
        t = open(p, errors="ignore").read()
        return has_script(t) or has_button(t) or os.path.relpath(os.path.abspath(p), R) in req
    paths = [str(p) for p in paths if wanted(str(p))]
    if not paths: return
    if not os.path.exists(VENV_PY): raise SystemExit(f"{name}: Listen-coverage guard needs {VENV_PY} (playwright); it is a required step")
    r = subprocess.run([VENV_PY, os.path.abspath(__file__), *paths], capture_output=True, text=True)
    print((r.stdout or r.stderr).strip()[:3000])
    if r.returncode: raise SystemExit(f"{name}: Listen does not read all visible content (see above)")
def require_nl(nl_html, name="R49b"):
    """Every page this NL links with ?listen=1 must exist, have Listen, and start reading on its own (build/preview/publish)."""
    import subprocess
    if not os.path.exists(VENV_PY): raise SystemExit(f"{name}: Listen-coverage guard needs {VENV_PY} (playwright); it is a required step")
    r = subprocess.run([VENV_PY, os.path.abspath(__file__), "--nl-only", "--nl", str(nl_html)], capture_output=True, text=True)
    print((r.stdout or r.stderr).strip()[:3000])
    if r.returncode: raise SystemExit(f"{name}: a ?listen=1 link in {os.path.basename(str(nl_html))} opens a page without working Listen (see above)")
def require_since(t0, name="R49"):
    """require() on every page under pages/ written since t0 (a generator's start time)."""
    out = []
    for dp, _, fs in os.walk(os.path.join(R, "pages")):
        if "/archive/issues" in dp: continue
        out += [os.path.join(dp, f) for f in fs if f.endswith(".html") and os.path.getmtime(os.path.join(dp, f)) >= t0]
    require(out, name)
def main(args, live=None, nl=None, nl_only=False):
    nlf = (nl or []) if nl_only else nl_files() + (nl or [])
    targets = nl_targets(nlf)
    req = {} if (args or nl_only) else required_pages()
    if args: pages = [os.path.relpath(os.path.abspath(a), R) for a in args]
    elif nl_only: pages = sorted(targets)
    else: pages = sorted(set(listen_pages()) | set(req) | set(targets))
    req_all = required_pages()
    H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=R)
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), H); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright  # only the checker process needs playwright (require() shells out)
    fails = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(); ctx = b.new_context(); ctx.add_init_script(MOCK)
        ctxb = b.new_context(); ctxb.add_init_script(MOCK_BLOCK); v2n = [0, 0]
        if not live:
            ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())
            ctxb.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())  # offline: fonts/images from production not needed
        base = live.rstrip("/") if live else f"http://127.0.0.1:{port}"
        for rel in pages:
            src_p = os.path.join(R, rel)
            if not os.path.exists(src_p):
                fails[rel] = [f"missing page (linked with ?listen=1 from {', '.join(targets.get(rel, []))})"]; continue
            src = open(src_p, errors="ignore").read()
            pre = []
            if not has_button(src) and not has_script(src) and rel not in req_all and rel not in targets: continue  # not a Listen page, not required
            if not has_button(src): pre.append("no Listen button (a.ph-listen)")
            if not has_script(src): pre.append("no Listen script (speechSynthesis)")
            if pre:
                why = []
                if rel in targets: why.append("linked with ?listen=1 from " + ", ".join(targets[rel]))
                if rel in req_all: why.append("required type: " + req_all[rel])
                fails[rel] = [p + (" -- " + "; ".join(why) if why else "") for p in pre]; continue
            pg = ctx.new_page()
            try:
                url = f"{base}/{rel}?autoplay=0&cb={os.getpid()}"
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
                    elif len(norm(t)) > 60 and spoken.count(norm(t)) > 1 and sum(norm(x["text"]) == norm(t) for x in blocks) == 1 \
                            and spoken.count(norm(t)) > sum(norm(t) in norm(x["text"]) for x in blocks):  # Oct 20: text quoted again inside another visible block (DYK email line + full rule) is read once per block, not a double read
                        miss.append(f"double-read {blk['tag']}: {re.sub(r'\s+', ' ', t)[:90]}")
                if not spoken: miss.insert(0, "nothing spoken")
                if rel in targets:  # R49b: ?listen=1 must start reading by itself, title first
                    pg2 = ctx.new_page()
                    try:
                        pg2.goto(f"{base}/{rel}?listen=1&cb={os.getpid()}", wait_until="load", timeout=30000)
                        for _ in range(30):
                            if pg2.evaluate("() => window.__spoken.length"): break
                            pg2.wait_for_timeout(100)
                        first = pg2.evaluate("() => window.__spoken[0] || ''"); h1 = pg2.evaluate("() => (document.querySelector('h1') || {}).textContent || ''")
                        if not first: miss.insert(0, "?listen=1 does not start reading (linked from " + ", ".join(targets[rel]) + ")")
                        elif norm(h1) and not norm(first).startswith(norm(h1)[:20]): miss.insert(0, f"?listen=1 starts with '{first[:40]}', not the title")
                    finally:
                        pg2.close()
                    if V2_MARK in src:  # R76 blocked-autoplay case (v2 pages)
                        v2n[0] += 1; miss[:0] = blocked_case(ctxb, base, rel)
                    else: v2n[1] += 1
                if miss: fails[rel] = miss
            except Exception as e:
                fails[rel] = [f"page error: {str(e).splitlines()[0][:160]}"]
            finally:
                pg.close()
        b.close()
    srv.shutdown()
    print(f"R49 Listen coverage{' (LIVE ' + live + ')' if live else ''}: {len(pages)} pages checked "
          f"({len([p for p in pages if p in req_all])} required-type, {len([p for p in pages if p in targets])} ?listen=1 targets from {len(nlf)} NL file(s)), "
          f"{len(fails)} failing; R76 blocked-autoplay bar: {v2n[0]} v2 target(s) tested, {v2n[1]} v1 target(s) without bar")
    for rel, m in fails.items():
        print("  FAIL " + rel); [print("      " + x) for x in m[:8]]; len(m) > 8 and print(f"      ... +{len(m) - 8} more")
    return 1 if fails else 0
if __name__ == "__main__":
    a = sys.argv[1:]; live = None; nl = []; since = None
    while "--nl" in a:
        i = a.index("--nl"); nl.append(a[i + 1]); del a[i:i + 2]
    if "--since" in a:
        i = a.index("--since"); since = float(a[i + 1]); del a[i:i + 2]
    nl_only = "--nl-only" in a
    if "--live" in a:
        i = a.index("--live"); live = a[i + 1] if i + 1 < len(a) and not a[i + 1].endswith(".html") else "https://palmhillnews.vercel.app"
        a = [x for x in a if x not in ("--live", live)]
    a = [x for x in a if not x.startswith("--")]
    if since is not None:  # pages under pages/ written since EPOCH that have, or must have, Listen
        req = required_pages()
        a = [os.path.join(R, rel) for rel in _pages() if os.path.getmtime(os.path.join(R, rel)) >= since]
        a = [p for p in a if has_script(open(p, errors="ignore").read()) or has_button(open(p, errors="ignore").read()) or os.path.relpath(p, R) in req]
        if not a: print("R49 Listen coverage: no Listen / required pages written"); sys.exit(0)
    sys.exit(main(a, live, nl, nl_only))
