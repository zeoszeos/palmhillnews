#!/usr/bin/env python3
"""R116 / R117 (Steven, Nov 6 2026), no browser.

R116: Stop on a dedicated listen-*.html chair link (no ?listen=1, no ph-listen class) stays on the
newsletter. The first tap still reads in place. Speech missing, file://, or a failed load still
opens the listen page. The harness runs scripts/listen_inplace.html.

R117: both Events sections' "See the All Events List" row on the November 8 live preview and the
SEND copy carries the newsletter light green #EAF4E4. SEND stays script-free.
"""
import os, re, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import page_listen as pl
import style_rules as sr

WHITE = '-webkit-text-fill-color:#FFFFFF;">'
LINK = "See the All Events List"
ISSUE = ROOT / "pages/previews/2026-11-08"
CHAIR = (
    "https://palmhillnews.vercel.app/pages/2026-10-25-listen-planning-environmental-committee-report.html",
    "https://palmhillnews.vercel.app/pages/2026-10-18-listen-golf-advisory-committee-report.html",
)

def section(page, title):
    hs = [(m.start(), m.group(1)) for m in re.finditer(re.escape(WHITE) + r"([^<]+)</span>", page)]
    for i, (pos, t) in enumerate(hs):
        if t == title:
            end = hs[i + 1][0] if i + 1 < len(hs) else len(page)
            return page[pos:end]
    return ""

def test_highlight():
    bare = '<td align="center" class="ph-ae-top" style="padding:6px 8px 8px 8px;text-align:center;"><a href="x">' + LINK + "</a></td>"
    assert sr.ae_top_highlight_missing(bare)  # the row Steven saw, before the highlight
    good = bare.replace('class="ph-ae-top" style="', 'bgcolor="#EAF4E4" class="ph-ae-top" style="background:#EAF4E4;')
    assert sr.ae_top_highlight_missing(good) == ""
    assert sr.ae_top_highlight_missing(good.replace(LINK, "See the All Events List →"))
    for name in ("PHNEWS-2026-11-08-preview.html", "PHNEWS-2026-11-08-SEND.html"):
        html = (ISSUE / name).read_text(encoding="utf-8")
        for title in ("Events - This Week", "Events - Next Week"):
            miss = sr.ae_top_highlight_missing(section(html, title), LINK)
            assert miss == "", f"{name} {title}: {miss}"
        assert html.count('class="ph-ae-top"') == 2
        assert html.count(">See the All Events List</a>") == 2
        assert "See the All Events List →" not in html
        assert "https://www.palmhillcountryclub.net/calendar-1/" in html
    send = (ISSUE / "PHNEWS-2026-11-08-SEND.html").read_text(encoding="utf-8")
    preview = (ISSUE / "PHNEWS-2026-11-08-preview.html").read_text(encoding="utf-8")
    assert "<script" not in send.lower()
    assert preview.count("<!-- ph-inplace-listen:start -->") == 1
    assert "<script" not in pl.strip_inplace(preview).lower()
    assert pl.INPLACE.strip() in preview  # the live preview carries the shared script, not a hand patch
    oct25 = (ROOT / "pages/previews/2026-10-25/PHNEWS-2026-10-25-preview.html").read_text(encoding="utf-8")
    assert "ph-ae-top" not in oct25 and "See the All Events List" not in oct25

HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const root = process.argv[2];
const html = fs.readFileSync(path.join(root, 'scripts/listen_inplace.html'), 'utf8');
const m = html.match(/<script[^>]*>([\s\S]*?)<\/script>/);
if (!m) throw new Error('no script in listen_inplace.html');
const stub = `
  function phParts(doc) {
    if (doc && doc.__fail === 'empty') return [];
    return ['Planning and Environmental Committee. Motion to the Board.'];
  }
`;
const code = m[1].replace('/*READER*/', stub);
const CHAIR = [
  'https://palmhillnews.vercel.app/pages/2026-10-25-listen-planning-environmental-committee-report.html',
  'https://palmhillnews.vercel.app/pages/2026-10-18-listen-golf-advisory-committee-report.html',
];
const NEWS = 'https://palmhillnews.vercel.app/pages/previews/2026-11-08/PHNEWS-2026-11-08-preview.html';

function ClassList() { this._ = new Set(); }
ClassList.prototype.add = function () { for (const c of arguments) this._.add(c); };
ClassList.prototype.remove = function (c) { this._.delete(c); };
ClassList.prototype.contains = function (c) { return this._.has(c); };

function El(tag) {
  this.tag = tag;
  this.nodeType = 1;
  this.attributes = {};
  this.childNodes = [];
  this.classList = new ClassList();
  this.dataset = {};
  this.style = {};
  this.parentNode = null;
  this.id = '';
}
El.prototype.setAttribute = function (k, v) { this.attributes[k] = String(v); };
El.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null; };
El.prototype.removeAttribute = function (k) { delete this.attributes[k]; };
Object.defineProperty(El.prototype, 'href', { get() { return this.getAttribute('href'); } });
El.prototype.matches = function (sel) { return sel === 'a[href]' && this.tag === 'a' && !!this.getAttribute('href'); };
El.prototype.closest = function (sel) { for (let n = this; n; n = n.parentNode) if (n.matches && n.matches(sel)) return n; return null; };
El.prototype.appendChild = function (ch) { this.childNodes.push(ch); ch.parentNode = this; return ch; };
El.prototype.remove = function () {
  if (!this.parentNode) return;
  this.parentNode.childNodes = this.parentNode.childNodes.filter((n) => n !== this);
  this.parentNode = null;
};
Object.defineProperty(El.prototype, 'textContent', {
  get() { return this.childNodes.map((n) => n.textContent || '').join(''); },
});

function link(href, text, cls) {
  const a = new El('a');
  a.setAttribute('href', href);
  if (cls) a.classList.add(cls);
  const img = new El('img');
  const tn = { nodeType: 3, textContent: text || 'Listen' };
  a.appendChild(img);
  a.childNodes.push(tn);
  return { a, img };
}
function labelOf(a) { return a.childNodes.filter((n) => n.nodeType === 3).map((n) => n.textContent).join(''); }

function boot(opts) {
  opts = opts || {};
  const spoken = [];
  let cancels = 0;
  const location = { origin: opts.origin || 'https://palmhillnews.vercel.app', protocol: opts.protocol || 'https:', href: opts.href || NEWS };
  const document = { body: new El('body') };
  document.getElementById = function (id) {
    const walk = (el) => {
      if (!el || !el.childNodes) return null;
      for (const c of el.childNodes) {
        if (c.id === id) return c;
        const hit = walk(c);
        if (hit) return hit;
      }
      return null;
    };
    return walk(document.body);
  };
  document.createElement = function (tag) {
    const el = new El(tag);
    if (tag === 'iframe') {
      Object.defineProperty(el, 'src', {
        configurable: true,
        set(v) {
          el._src = v;
          const mode = window.__iframeMode || 'ok';
          if (mode === 'delay') return;
          if (typeof el.onload === 'function') el.onload();
        },
        get() { return el._src || ''; },
      });
      Object.defineProperty(el, 'contentDocument', {
        get() {
          const mode = window.__iframeMode || 'ok';
          if (mode === 'throw') throw new Error('cross-origin');
          return { __fail: mode === 'empty' ? 'empty' : '' };
        },
      });
    }
    return el;
  };
  const listeners = [];
  document.addEventListener = function (type, fn) { if (type === 'click') listeners.push(fn); };
  const timers = [];
  let nid = 1;
  const window = {
    document, location, URL, Array, Error, Object,
    __iframeMode: opts.iframe || 'ok',
    addEventListener() {},
    setTimeout(fn) { const id = nid++; timers.push({ id, fn }); return id; },
    clearTimeout(id) { const i = timers.findIndex((t) => t.id === id); if (i >= 0) timers.splice(i, 1); },
  };
  window.window = window;
  if (opts.speech !== false) {
    function SpeechSynthesisUtterance(text) { this.text = text; this.volume = 1; this.lang = ''; this.rate = 1; }
    window.SpeechSynthesisUtterance = SpeechSynthesisUtterance;
    window.speechSynthesis = {
      speak(u) { spoken.push(u); },
      cancel() { cancels += 1; },
    };
  }
  vm.createContext(window);
  vm.runInContext(code, window);
  function click(el) {
    const e = { target: el, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } };
    for (const fn of listeners) fn(e);
    return e;
  }
  function flush() { const t = timers.splice(0); for (const x of t) x.fn(); }
  return { click, location, spoken, document, flush, cancels: () => cancels, listening: listeners.length > 0 };
}

function assert(cond, msg) { if (!cond) throw new Error(msg); }

// Chair links: first press reads in place and says Stop; second press stops and does not navigate.
for (const href of CHAIR) {
  const b = boot();
  const { a, img } = link(href);
  const first = b.click(img);  // Steven taps the speaker image
  assert(first.defaultPrevented, 'chair first press must stay on the page: ' + href);
  assert(labelOf(a) === 'Stop', 'chair first press relabels to Stop, got ' + JSON.stringify(labelOf(a)));
  assert(a.classList.contains('ph-playing'), 'chair first press marks the control playing');
  assert(a.getAttribute('aria-pressed') === 'true', 'chair first press sets aria-pressed');
  assert(b.location.href === NEWS, 'chair first press must not navigate');
  assert(!a.classList.contains('ph-listen') && !/[?&]listen=1\b/.test(href), 'fixture must be a bare listen-*.html link');
  assert(b.spoken.some((u) => /Planning and Environmental/.test(u.text)), 'chair first press starts speaking the report');
  const frame = b.document.body.childNodes.find((n) => n.tag === 'iframe');
  assert(frame && frame._src && frame._src.indexOf(href.split('/').pop()) >= 0 && /[?&]autoplay=0/.test(frame._src), 'chair first press loads that listen page in place');
  const second = b.click(a);
  assert(second.defaultPrevented, 'chair Stop must not follow the href: ' + href);
  assert(b.location.href === NEWS, 'chair Stop navigated to ' + b.location.href);
  assert(labelOf(a) === 'Listen', 'chair Stop restores Listen, got ' + JSON.stringify(labelOf(a)));
  assert(!a.classList.contains('ph-playing'), 'chair Stop clears the playing state');
  assert(b.cancels() >= 1, 'chair Stop cancels speech');
  b.flush();  // the load timer must not navigate after Stop
  assert(b.location.href === NEWS, 'late load failure after Stop must not navigate');
}

// Stop before the listen page has loaded (the label is already Stop).
{
  const b = boot({ iframe: 'delay' });
  const { a } = link(CHAIR[0]);
  const first = b.click(a);
  assert(first.defaultPrevented && labelOf(a) === 'Stop' && b.location.href === NEWS, 'delayed first press stays and says Stop');
  const second = b.click(a);
  assert(second.defaultPrevented && labelOf(a) === 'Listen' && b.location.href === NEWS, 'Stop before load stays on the newsletter');
}

// Notice / manager links that already use ?listen=1, and archive links with ph-listen, still read in place.
for (const spec of [
  { href: 'https://palmhillnews.vercel.app/pages/2026-11-08-notice-example.html?listen=1', cls: '' },
  { href: 'https://palmhillnews.vercel.app/pages/2026-10-25-listen-planning-environmental-committee-report.html', cls: 'ph-listen' },
]) {
  const b = boot();
  const { a } = link(spec.href, 'Listen', spec.cls);
  const first = b.click(a);
  assert(first.defaultPrevented && labelOf(a) === 'Stop' && b.location.href === NEWS, 'first press in place: ' + spec.href);
  const second = b.click(a);
  assert(second.defaultPrevented && b.location.href === NEWS && labelOf(a) === 'Listen', 'second press stops: ' + spec.href);
}

// A report title link is not a Listen control.
{
  const b = boot();
  const { a } = link('https://palmhillnews.vercel.app/pages/2026-10-25-planning-environmental-committee-report.html', 'Read Full Report →');
  const ev = b.click(a);
  assert(!ev.defaultPrevented && b.location.href === NEWS && b.spoken.length === 0, 'Read Full Report must not be intercepted');
}

// Fallback: no speech support. The script installs no listener, so the browser follows the href.
{
  const b = boot({ speech: false });
  const { a } = link(CHAIR[0]);
  const ev = b.click(a);
  assert(!b.listening && !ev.defaultPrevented && labelOf(a) === 'Listen', 'no speech: Listen stays a normal link');
}

// Fallback: opened from disk (file://) with a sibling listen page. target() declines, so the link navigates.
{
  const b = boot({ href: 'file:///D:/PHNEWS/local-nov8/PHNEWS-2026-11-08-preview.html', protocol: 'file:', origin: 'null' });
  const { a } = link('2026-10-25-listen-planning-environmental-committee-report.html');
  const ev = b.click(a);
  assert(!ev.defaultPrevented && labelOf(a) === 'Listen' && b.location.href.startsWith('file:'), 'file:// Listen stays a normal link');
}

// Fallback: the listen page fails to load (empty read, or the frame cannot be read). Open the listen page.
for (const mode of ['empty', 'throw']) {
  const b = boot({ iframe: mode });
  const { a } = link(CHAIR[1]);
  const ev = b.click(a);
  assert(ev.defaultPrevented, mode + ': the tap was handled');
  assert(b.location.href === CHAIR[1], mode + ': load failure must open the listen page, got ' + b.location.href);
}

console.log('listen inplace Stop tests OK');
"""

def test_stop():
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(HARNESS)
        name = f.name
    try:
        r = subprocess.run(["node", name, str(ROOT)], capture_output=True, text=True)
    finally:
        os.unlink(name)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("R116 listen Stop harness failed")
    print(r.stdout.strip())

if __name__ == "__main__":
    test_stop()
    test_highlight()
    print("R116/R117 tests OK")
