#!/usr/bin/env python3
"""R119 (Steven, Nov 7 2026), no browser.

The shared v2 page-listen script (scripts/page_listen_v2.html):
  - on iPhone/iPad, shows Tap to listen immediately and does not start on load;
  - the first Listen tap starts speech unless speech has already begun;
  - if speech is talking, Listen stops it;
  - on desktop, a Listen-link open still calls start(true) on load.

The guard fails a fixture that restores the old swallow-first-tap handler
(`if (playing) stop(); else start(false)`) together with a load-time start on iPhone.
"""
import os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr

SRC = ROOT / "scripts" / "page_listen_v2.html"
GOOD_CLICK = "if (playing && started) stop(); else start(false);"
OLD_CLICK = "if (playing) stop(); else start(false);"
GOOD_BAR = "if (iphoneOrIpad()) showBar();"
OLD_LOAD = "if (iphoneOrIpad()) start(true);"

HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const m = html.match(/<script[^>]*>([\s\S]*?)<\/script>/);
if (!m) throw new Error('no script');
const code = m[1].replace('/*READER*/', 'function phParts(){ return ["Hello from Palm Hill."]; }\n');
const mode = process.argv[3];

function ClassList() { this._ = new Set(); }
ClassList.prototype.add = function () { for (const c of arguments) this._.add(c); };
ClassList.prototype.remove = function (c) { this._.delete(c); };
ClassList.prototype.contains = function (c) { return this._.has(c); };

function El(tag) {
  this.tag = tag; this.nodeType = 1; this.childNodes = []; this.classList = new ClassList();
  this.dataset = {}; this.style = {}; this.parentNode = null; this._on = {};
}
El.prototype.setAttribute = function (k, v) { this.attributes = this.attributes || {}; this.attributes[k] = String(v); };
El.prototype.getAttribute = function (k) { return (this.attributes || {})[k] || null; };
El.prototype.addEventListener = function (type, fn) { (this._on[type] = this._on[type] || []).push(fn); };
El.prototype.remove = function () {
  if (!this.parentNode) return;
  this.parentNode.childNodes = this.parentNode.childNodes.filter((n) => n !== this);
  this.parentNode = null;
};
El.prototype.insertBefore = function (node, ref) {
  const i = ref ? this.childNodes.indexOf(ref) : -1;
  this.childNodes.splice(i < 0 ? 0 : i, 0, node);
  node.parentNode = this;
  return node;
};
Object.defineProperty(El.prototype, 'firstChild', { get() { return this.childNodes[0] || null; } });
Object.defineProperty(El.prototype, 'textContent', {
  get() { return this.childNodes.map((n) => n.textContent || '').join(''); },
  set(v) { this.childNodes = [{ nodeType: 3, textContent: String(v) }]; },
});

function boot(opts) {
  const body = new El('body');
  body.dataset.phAutoplay = opts.autoplay ? '1' : '';
  const link = new El('a');
  link.classList.add('ph-listen');
  link.childNodes.push({ nodeType: 3, textContent: 'Listen' });
  body.childNodes.push(link); link.parentNode = body;
  const attempts = []; const spoken = [];
  let unlocked = !!opts.unlocked;
  const timers = [];
  const document = {
    body, readyState: 'complete',
    querySelector(sel) {
      if (sel !== 'a.ph-listen') return null;
      const walk = (el) => {
        if (!el || !el.childNodes) return null;
        if (el.classList && el.classList.contains('ph-listen')) return el;
        for (const c of el.childNodes) { const h = walk(c); if (h) return h; }
        return null;
      };
      return walk(body);
    },
    createElement(tag) { return new El(tag); },
    addEventListener() {}, removeEventListener() {},
  };
  const location = { search: opts.search || '', href: 'https://palmhillnews.vercel.app/pages/listen.html' };
  const window = {
    document, location, URL, URLSearchParams, Array, Object, Error, RegExp,
    navigator: { userAgent: opts.ua, platform: opts.platform || '', maxTouchPoints: opts.touch || 0 },
    scrollTo() {},
    addEventListener() {},
    setTimeout(fn, ms) { timers.push({ fn, ms: ms || 0 }); return timers.length; },
    clearTimeout() {},
  };
  window.window = window;
  function SpeechSynthesisUtterance(text) { this.text = text; this.lang = ''; this.rate = 1; }
  window.SpeechSynthesisUtterance = SpeechSynthesisUtterance;
  window.speechSynthesis = {
    speak(u) { attempts.push(u.text); if (unlocked && u.onstart) { spoken.push(u.text); u.onstart(); } },
    cancel() {},
  };
  vm.createContext(window);
  vm.runInContext(code, window);
  function label() { return link.childNodes.filter((n) => n.nodeType === 3).map((n) => n.textContent).join(''); }
  function bar() { return body.childNodes.find((n) => n.className === 'ph-tap-bar') || null; }
  function flush(max) {
    const due = timers.filter((t) => t.ms <= max);
    for (const t of due) timers.splice(timers.indexOf(t), 1);
    for (const t of due) t.fn();
  }
  function click() {
    unlocked = true;
    const e = { preventDefault() {}, stopPropagation() {}, target: link };
    for (const fn of link._on.click || []) fn(e);
  }
  return { attempts, spoken, label, bar, flush, click };
}

function assert(cond, msg) { if (!cond) throw new Error(mode + ': ' + msg); }
const IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1';
const DESK = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

if (mode === 'iphone') {
  const b = boot({ ua: IPHONE, platform: 'iPhone', autoplay: true, search: '' });
  const bar = b.bar();
  assert(bar && /Tap to listen/.test(bar.textContent), 'Tap to listen is missing before any timer');
  assert(b.attempts.length === 0 && b.spoken.length === 0, 'iPhone spoke on load');
  assert(b.label() === 'Listen', 'iPhone label changed before a tap, got ' + b.label());
  b.click();
  assert(b.spoken[0] === 'Hello from Palm Hill.', 'first Listen tap did not start speech');
  assert(b.bar() === null, 'bar still showing after the tap');
  assert(b.label() === 'Stop', 'Listen did not become Stop once speech started');
  b.click();
  assert(b.label() === 'Listen', 'second Listen tap did not stop speech');
} else if (mode === 'ipad') {
  const b = boot({ ua: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.5 Safari/605.1.15', platform: 'MacIntel', touch: 5, autoplay: true });
  assert(b.bar() && /Tap to listen/.test(b.bar().textContent) && b.attempts.length === 0, 'iPad did not show Tap to listen immediately');
} else if (mode === 'desktop') {
  const b = boot({ ua: DESK, platform: 'Win32', autoplay: true, search: '?listen=1', unlocked: true });
  assert(b.bar() === null && b.spoken.length === 0, 'desktop spoke before the load timer');
  b.flush(0);
  assert(b.spoken[0] === 'Hello from Palm Hill.', 'desktop did not auto-start on load');
  assert(b.bar() === null, 'desktop showed Tap to listen after a successful auto-start');
  assert(b.label() === 'Stop', 'desktop auto-start did not show Stop');
  b.click();
  assert(b.label() === 'Listen', 'desktop Listen did not stop speech that had started');
} else if (mode === 'desktop-blocked') {
  const b = boot({ ua: DESK, platform: 'Win32', autoplay: true, search: '?listen=1', unlocked: false });
  b.flush(0);
  assert(b.attempts.length === 1 && b.spoken.length === 0, 'blocked desktop did not attempt one load-time start');
  assert(b.label() === 'Stop', 'blocked load-time start should still be waiting');
  b.click();
  assert(b.spoken[0] === 'Hello from Palm Hill.', 'first Listen tap during a blocked auto-start did not start speech');
} else if (mode === 'old-iphone') {
  const b = boot({ ua: IPHONE, platform: 'iPhone', autoplay: true, unlocked: false });
  assert(b.attempts.length === 1 && b.spoken.length === 0, 'old fixture did not block the load-time start');
  assert(!b.bar(), 'old fixture should not show Tap to listen');
  b.click();
  assert(b.spoken.length === 0, 'old fixture first Listen tap was expected to swallow speech');
  b.click();
  assert(b.spoken[0] === 'Hello from Palm Hill.', 'old fixture second tap should be the one that speaks');
} else throw new Error('unknown mode ' + mode);
console.log(mode + ' OK');
"""

def run_mode(src, mode):
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "player.html"
        page.write_text(src, encoding="utf-8")
        harness = Path(d) / "harness.js"
        harness.write_text(HARNESS, encoding="utf-8")
        r = subprocess.run(["node", str(harness), str(page), mode], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"R119 harness failed ({mode})")
    print(r.stdout.strip())

def main():
    src = SRC.read_text(encoding="utf-8")
    why = sr.listen_page_iphone_problem(src)
    assert why == "", why
    bad = src.replace(GOOD_CLICK, OLD_CLICK).replace(GOOD_BAR, OLD_LOAD)
    bad_why = sr.listen_page_iphone_problem(bad)
    assert bad_why, "guard did not fail the old swallow-first-tap fixture"
    assert "Stop" in bad_why, bad_why
    nobar = src.replace(GOOD_BAR, "if (iphoneOrIpad()) { /* bar removed */ }")
    nobar_why = sr.listen_page_iphone_problem(nobar)
    assert nobar_why and "Tap to listen" in nobar_why, nobar_why
    assert "start(true)" in src
    run_mode(src, "iphone")
    run_mode(src, "ipad")
    run_mode(src, "desktop")
    run_mode(src, "desktop-blocked")
    run_mode(bad, "old-iphone")
    send = (ROOT / "pages/previews/2026-11-08/PHNEWS-2026-11-08-SEND.html").read_text(encoding="utf-8")
    preview = (ROOT / "pages/previews/2026-11-08/PHNEWS-2026-11-08-preview.html").read_text(encoding="utf-8")
    assert "<script" not in send.lower()
    assert "<!-- ph-page-listen:start -->" not in preview
    assert preview.count("<!-- ph-inplace-listen:start -->") == 1
    for rel in ("pages/previews/2026-11-08/PHNEWS-2026-11-08-SEND.html", "pages/previews/2026-11-08/PHNEWS-2026-11-08-preview.html"):
        diff = subprocess.run(["git", "diff", "--", rel], cwd=ROOT, capture_output=True, text=True)
        assert diff.stdout == "", rel + " changed"
    sr.assert_r10_locked_pages(ROOT)
    stale = sr.listen_iphone_tree_problems(ROOT)
    assert not stale, "inlined listen player is stale:\n" + "\n".join(stale[:12])
    print("R119 tests OK")

if __name__ == "__main__":
    main()
