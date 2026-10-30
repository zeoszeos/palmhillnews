#!/usr/bin/env python3
"""STYLE-RULES R49 (Steven, Oct 18 12:39 AM / 12:41 AM / 12:43 AM): the ONE shared page-listen script (between
<!-- ph-page-listen:start --> / <!-- ph-page-listen:end -->) used by every generated email copy, notice page and report page
with a 'ph-listen' button. It reads all visible content in page order, including the closing source / credit line.
Generators (notice_listen.py, notice_page.py, make_live_preview.py) take SCRIPT from here; `apply()` swaps an older block
for this one. Checked by scripts/check_listen_coverage.py.
R49b (Steven, Oct 18 2:05 AM): `add()` gives a page the script AND the standard button (scripts/listen_button.html); every
report / notice / story / message / email-copy page and every page an NL links with ?listen=1 must have both.
Usage: python3 scripts/page_listen.py [--add] PAGE.html [...]   (rewrites the block in place, --add also adds missing Listen)"""
import os, re, sys
START, END = "<!-- ph-page-listen:start -->", "<!-- ph-page-listen:end -->"
SCRIPT = "<!-- ph-page-listen:start -->\n<script>\n(() => {\n  const link = document.querySelector('a.ph-listen');\n  if (!link) return;\n  const label = Array.from(link.childNodes).find((n) => n.nodeType === 3 && n.textContent.trim());\n  if (!('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {\n    return;\n  }\n  const synth = window.speechSynthesis;\n  const MON = {Jan:'January',Feb:'February',Mar:'March',Apr:'April',Jun:'June',Jul:'July',Aug:'August',Sep:'September',Oct:'October',Nov:'November',Dec:'December'};\n  let run = 0, playing = false, started = false;\n  const setLabel = (t) => { if (label) label.textContent = t; link.setAttribute('aria-label', t === 'Stop' ? 'Stop reading' : 'Listen to this page'); };\n  function chunks(text) {\n    const clean = text.replace(/\\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\b\\.?/g, (m, k) => MON[k]).replace(/\\s+/g, ' ').trim();\n    if (!clean) return [];\n    const frags = typeof Intl.Segmenter === 'function'\n      ? Array.from(new Intl.Segmenter('en-US', {granularity: 'sentence'}).segment(clean), (s) => s.segment.trim()).filter(Boolean)\n      : [clean];\n    const out = []; let p = '';\n    for (const s of frags) { if (p && p.length + s.length + 1 > 260) { out.push(p); p = s; } else p += (p ? ' ' : '') + s; }\n    if (p) out.push(p);\n    return out;\n  }\n  function parts() {\n    // R49 (Steven, Oct 18 12:39/12:43 AM): read ALL visible content in page order -- the h1, every content card / email\n    // row (paragraphs, quotes, lists, tables inside), and the source / credit line at the end. Skipped: the email's\n    // Subject/From/Sent header row, attachment lists, navigation and the Listen button itself.\n    const h1 = document.querySelector('h1');\n    const sel = 'main .content-card, main .ph-row, main .ph-meta, main .source, main .ph-source, main .credit, main .byline';\n    const sent = (document.querySelector('main') || document.body).innerText;  // R49b: a .ph-meta line that only repeats the email's Sent time is the date line (skipped)\n    const all = Array.from(document.querySelectorAll(sel))\n      .filter((el) => !el.closest('nav, .ph-strip, .ph-links') && !el.classList.contains('attachments') && !/^\\s*Subject:/.test(el.innerText))\n      .filter((el) => !(el.classList.contains('ph-meta') && sent.includes('Sent: ' + el.innerText.trim())));\n    let blocks = all.filter((el) => !all.some((o) => o !== el && o.contains(el)))\n      .map((el) => el.innerText.trim())\n      .filter(Boolean);\n    if (!blocks.length) blocks = walkAll();  // R49b (Steven, Oct 18 2:05 AM): pages without content cards\n    return [h1 ? h1.textContent : '', ...blocks].flatMap((t) => t.split(/\\n+/)).flatMap(chunks);  // each visual line its own phrase\n  }\n  function walkAll() {\n    // R49b: early notice copies, simple / card pages and plain reports have no content cards -- read every visible block\n    // in <main> / <article> / <body> in page order (outermost block once; table rows, quotes, bare div text, the Source\n    // line). Skipped: header, kicker/badge, date line, navigation, archive links, the Listen button, Back links.\n    const BLOCK = 'h2,h3,h4,h5,h6,p,li,blockquote,figure,figcaption,pre,table,dl,aside';\n    const SKIP = 'h1,header,footer,script,style,noscript,nav,button,[role=\"navigation\"],.ph-listen,.ph-listen-row,.ph-story-nav,.ph-story-links-long,.ph-archive-bar,.ph-dateline,.page-kicker,.ph-strip,.ph-links,.badge,.meta,.date,.back,.attachments,[aria-hidden=\"true\"]';\n    const vis = (el) => el.getClientRects().length > 0;\n    const out = [];\n    const walk = (el) => {\n      let run = '';\n      const flush = () => { if (run.trim()) out.push(run.trim()); run = ''; };\n      for (const n of el.childNodes) {\n        if (n.nodeType === 3) { run += n.textContent; continue; }\n        if (n.nodeType !== 1 || n.matches(SKIP) || !vis(n)) continue;\n        if (n.matches(BLOCK)) {\n          flush();\n          if (n.matches('table,dl')) n.querySelectorAll('caption,tr,dt,dd').forEach((r) => { const x = r.innerText.trim(); if (x) out.push(x); });\n          else if (n.matches('figure,aside,blockquote') && n.querySelector('p,li,figcaption')) walk(n);\n          else { const x = n.innerText.trim(); if (x) out.push(x); }\n        } else if (getComputedStyle(n).display.startsWith('inline')) run += n.innerText;\n        else { flush(); walk(n); }\n      }\n      flush();\n    };\n    walk(document.querySelector('main') || document.querySelector('article') || document.body);\n    return out;\n  }\n\n  function stop() { run += 1; playing = false; synth.cancel(); setLabel('Listen'); }\n  function start(auto) {\n    const list = parts(); const me = ++run; let i = 0;\n    synth.cancel(); playing = true; started = false; setLabel('Stop');\n    const next = () => {\n      if (me !== run) return;\n      if (i >= list.length) { playing = false; setLabel('Listen'); return; }\n      const u = new SpeechSynthesisUtterance(list[i]);\n      u.lang = 'en-US'; u.rate = 1;\n      u.onstart = () => { if (me === run) started = true; };\n      u.onend = () => { if (me !== run) return; i += 1; next(); };\n      u.onerror = (e) => { if (me !== run || e.error === 'canceled' || e.error === 'interrupted') return; stop(); };\n      synth.speak(u);\n    };\n    next();\n    if (auto) window.setTimeout(() => { if (me === run && playing && !started) { stop(); arm(); } }, 4000);\n  }\n  link.addEventListener('click', (e) => { e.preventDefault(); if (playing) stop(); else start(false); });\n  function arm() {\n    const onTap = (e) => {\n      document.removeEventListener('click', onTap, true);\n      if (playing || (e.target.closest && e.target.closest('a'))) return;\n      start(false);\n    };\n    document.addEventListener('click', onTap, true);\n  }\n  window.addEventListener('pagehide', stop);\n  const q = new URLSearchParams(location.search);\n  if (q.get('listen') === '1' || q.get('autoplay') === '1') {\n    const go = () => start(true);\n    if (document.readyState === 'complete') window.setTimeout(go, 0); else window.addEventListener('load', go, {once: true});\n  }\n})();\n</script>\n<!-- ph-page-listen:end -->\n"
BUTTON = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "listen_button.html"), encoding="utf-8").read().strip()  # the ONE speaker + 'Listen' button (also read by build_archive.js)
ROW = '<div class="ph-listen-row" style="display:flex;justify-content:flex-end;margin:6px 0 10px">' + BUTTON + '</div>'
# top of a card page's <main>: same right edge as the content card (ph-read.css: 32em at 18px, content-box, card padding)
ROW_MAIN = '<div class="ph-listen-row" style="display:flex;justify-content:flex-end;font-size:18px;box-sizing:content-box;max-width:32em;margin:6px auto 10px;padding:0 calc(clamp(18px,4vw,28px) + 1px)">' + BUTTON + '</div>'
# STYLE-RULES R76 (Steven, Oct 25 2026 9:29 AM): v2 Listen = the v1 reader + a big "Tap to listen" bar when autoplay is
# blocked. Built from ONE reader (scripts/listen_reader.js, also used by the website in-place Listen). Issues before
# listen_settings.json v2_from keep SCRIPT (v1) byte for byte; a page that already has v2 keeps v2 (apply never downgrades).
_D = os.path.dirname(os.path.abspath(__file__))
import json as _json
V2_FROM = _json.load(open(os.path.join(_D, "listen_settings.json")))["v2_from"]
READER = open(os.path.join(_D, "listen_reader.js"), encoding="utf-8").read().rstrip("\n")
SCRIPT_V2 = open(os.path.join(_D, "page_listen_v2.html"), encoding="utf-8").read().replace("/*READER*/", READER)
INPLACE = open(os.path.join(_D, "listen_inplace.html"), encoding="utf-8").read().replace("/*READER*/", READER)
V2_MARK = 'data-ph-listen-v="2"'
def v2_for(issue): return bool(issue) and issue >= V2_FROM
def is_v2(t): return START in t and V2_MARK in t[t.index(START):t.index(END, t.index(START))]
def apply(t, v2=None):
    if START not in t: return t
    if v2 is None: v2 = is_v2(t)
    a = t.index(START); b = t.index(END, a) + len(END)
    return t[:a] + (SCRIPT_V2 if v2 else SCRIPT).strip() + t[b:]
def upgrade(t):
    """R76: swap a page's shared listen block for v2 (script block only; no visible content changes). No block -> unchanged."""
    return apply(t, True)
def add_inplace(t):
    """R76: website in-place Listen block before </body> (idempotent). Never for the SEND / email copies."""
    t = re.sub(r"\n?<!-- ph-inplace-listen:start -->.*?<!-- ph-inplace-listen:end -->", "", t, flags=re.S)
    i = t.lower().rfind("</body>")
    return t[:i] + INPLACE.strip() + "\n" + t[i:] if i >= 0 else t + INPLACE
def add(t):
    """R49b (Steven, Oct 18 2:05 AM): give a page working Listen -- the shared script AND the standard button -- without
    changing any other visible content. Button placement follows the page's layout:
      story date row (build_archive storyNav)   -> right end of the date row (same markup build_archive.js emits)
      committee-report dateline (listenDateline) -> right end of the dateline
      email-copy shell (h1.ph-section)           -> on the title line (as notice_listen.py always did)
      anything else (early / simple / card pages) -> a right-aligned Listen row under the date line (or under the h1)
    Idempotent; a page that already has script + button only gets the current shared script."""
    if START in t and 'class="ph-listen"' in t: return apply(t)
    if START in t: return _button(apply(t))
    return _button(t).replace("</body>", SCRIPT.strip() + "\n</body>", 1)
def _button(t):
    if 'class="ph-listen"' in t: return t
    # anchors are searched with every <script>/<style> blanked out (same length), so text inside code never matches
    mask = re.sub(r"<(script|style)\b.*?</\1>", lambda m: " " * len(m.group(0)), t, flags=re.S)
    nav = re.search(r"<!-- ph-archive-nav:start -->.*?<!-- ph-archive-nav:end -->", mask, re.S)
    navs = t[nav.start():nav.end()] if nav else ""   # real text (the mask only locates the block)
    put = lambda new: t[:nav.start()] + new + t[nav.end():]
    m = re.search(r'(<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:)baseline(;gap:4px 16px;margin:0"><span style="[^"]*">[^<]*</span>)(</div>)', navs)
    if 'class="ph-story-nav"' in navs and m:
        new = navs.replace(m.group(0), m.group(1) + "center" + m.group(2) + BUTTON + m.group(3), 1)
        return put(new)
    m = re.search(r'(<div class="ph-dateline" style="display:flex;[^"]*"><span style="[^"]*">[^<]*</span>)(</div>)', navs)
    if m:
        return put(navs.replace(m.group(0), m.group(1) + BUTTON + m.group(2), 1))
    h = re.search(r'<h1 class="ph-section">(.*?)</h1>', mask, re.S)
    if h:
        hd = (f'<div class="hd" style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
              f'<h1 class="ph-section" style="margin:0">{h.group(1)}</h1>{BUTTON}</div>')
        return t.replace(h.group(0), hd, 1)
    body = mask[nav.end():] if nav else mask
    off = nav.end() if nav else 0
    d = re.search(r'<(div|p) class="(?:meta|date|ph-dateline)"[^>]*>.*?</\1>', body, re.S)
    if not d:  # card pages: header + archive nav, then <main> -- right-aligned at the top of the content column
        mm = re.search(r'<main\b[^>]*>', body)
        if mm: k = off + mm.end(); return t[:k] + ROW_MAIN + t[k:]
        d = re.search(r'<h1\b[^>]*>.*?</h1>', body, re.S)
    assert d, "no date line, <main> or h1 to anchor the Listen button"
    k = off + d.end()
    return t[:k] + "\n" + ROW + t[k:]
def add_file(path):
    t = open(path, encoding="utf-8").read(); n = add(t)
    if n != t: open(path, "w", encoding="utf-8").write(n); return True
    return False
def apply_file(path):
    t = open(path, encoding="utf-8").read(); n = apply(t)
    if n != t: open(path, "w", encoding="utf-8").write(n); return True
    return False
if __name__ == "__main__":
    a = sys.argv[1:]; adding = "--add" in a; a = [x for x in a if x != "--add"]
    for f in a: print(("updated " if (add_file(f) if adding else apply_file(f)) else "unchanged ") + f)
    sys.path.insert(0, __import__("os").path.dirname(__file__)); import check_listen_coverage as _lc; _lc.require(a)  # R49 required step
