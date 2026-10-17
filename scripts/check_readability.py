#!/usr/bin/env python3
"""STYLE-RULES RD1-RD13 guard (Steven, Oct 17 2026). Runs on every reading page in scope (pages/*.html,
pages/information/*.html; never pages/archive/** or pages/previews/**) and FAILS (exit 1) on:
  RD12 wording lock  visible text differs from the same page at --base (default tag pre-readability-1) -- layout-only rule
  RD1  page not on the shared style (no ph-read.css link / body.ph-rd class) unless it is a listed SKIP tool page
  RD4  a <p> still holding >= 4 <br> (email wall)          RD5  <br> right after an abbreviation or between lowercase words
  RD6  "<br>Topic label:" left inside a paragraph           RD7  "<br>- " list lines left as text
  rendered (Chromium, repo served over http so /pages/assets/*.css resolve as on Vercel), desktop 1280 + phone 390:
  RD1  main reading text >= 18px (recurring tables >= 15px)  RD2  line-height >= 1.55 (tables >= 1.45)
  RD3  <= 75 characters per line at 1280px (tables exempt)   RD10 meta/source/date lines >= 16px, text contrast >= 4.5:1
  RD11 Back / Listen / archive-bar links >= 44px tall on the phone
Warnings (report only): RD8 blocks over 120 words with no email line break to split at; RD9 ALL-CAPS runs (kept as written).
Usage: /workspace/.venv-vr/bin/python scripts/check_readability.py [FILES...] [--base REF] [--no-render] [--golden DIR [--capture]]"""
import sys, re, json, argparse, pathlib, subprocess, threading, functools, http.server, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import readability as R
ROOT = pathlib.Path(__file__).resolve().parent.parent
JS = r"""(tpl) => {
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const skip = e => e.closest('.ph-archive-bar,.ph-story-nav,header,nav,footer,.badge,.ph-rd-meta,.source,p.sources,p.note,script,style');
  const blocks = [...document.querySelectorAll('p,li,.ph-detail,.summary,td,.ph-row-title')].filter(e => vis(e) && !skip(e) && (e.innerText||'').trim().length >= 40
     && ![...e.children].some(c => ['P','DIV','LI','UL','OL','TABLE'].includes(c.tagName) && (c.innerText||'').trim().length > 30));
  const res = {blocks: [], meta: [], taps: []};
  const ctx = document.createElement('canvas').getContext('2d');
  for (const b of blocks.sort((a, z) => z.innerText.length - a.innerText.length).slice(0, 6)) {
    const cs = getComputedStyle(b), fs = parseFloat(cs.fontSize), lh = cs.lineHeight === 'normal' ? fs * 1.15 : parseFloat(cs.lineHeight);
    ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`; const avg = ctx.measureText('the quick brown fox jumps over a lazy dog ').width / 42;
    const w = b.getBoundingClientRect().width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    res.blocks.push({t: b.innerText.trim().slice(0, 40), fs, lh: +(lh / fs).toFixed(2), cpl: Math.round(w / avg), words: b.innerText.trim().split(/\s+/).length});
  }
  const lum = c => { const m = c.match(/[\d.]+/g); if (!m) return 1; const [r, g, b] = m.slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * r + .7152 * g + .0722 * b; };
  const bg = e => { for (; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; const m = c.match(/[\d.]+/g); if (m && (m.length < 4 || +m[3] > .5)) return c; } return 'rgb(255,255,255)'; };
  for (const e of document.querySelectorAll('.meta,.ph-meta,.ph-row-meta,.ph-source,p.source,.back,.header-meta,.ph-rd-meta,.source,p.sources,p.note')) if (vis(e) && (e.innerText||'').trim()) {
    const cs = getComputedStyle(e), a = lum(cs.color), b = lum(bg(e)); res.meta.push({t: e.innerText.trim().slice(0, 30), fs: parseFloat(cs.fontSize), cr: +((Math.max(a, b) + .05) / (Math.min(a, b) + .05)).toFixed(1)});
  }
  for (const a of document.querySelectorAll('.back a,a.ph-listen,.ph-archive-bar a,.ph-story-back a')) if (vis(a)) res.taps.push({t: a.innerText.trim().slice(0, 24), h: Math.round(a.getBoundingClientRect().height)});
  return res; }"""
def html_fails(s):
    body = s[s.find("<body"):]
    body = re.sub(r"<!-- ph-archive-nav:start -->.*?<!-- ph-archive-nav:end -->", "", body, flags=re.S)
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", body, flags=re.S | re.I)
    f = []
    for inner in re.findall(r"<p(?: [^>]*)?>((?:(?!</?p[ >]).)*?)</p>", body, flags=re.S):
        n = len(re.findall(R.BR, inner))
        if n >= 4: f.append(f"RD4 paragraph with {n} <br> (email wall): {R.plain(inner)[:60]}")
        segs = [R.plain(x) for x in re.split(R.BR, inner)]
        for a, b in zip(segs, segs[1:]):
            if R.ABBR.search(a): f.append(f"RD5 hard break after abbreviation: '…{a[-20:]}⏎{b[:20]}…'")
            elif re.match(r"[a-z]", b) and re.search(r"[a-z,]$", a): f.append(f"RD5 hard break mid-sentence: '…{a[-20:]}⏎{b[:20]}…'")
            if R.LIST.match(b): f.append(f"RD7 list line left as text: '{b[:30]}'")
            m = R.LABEL.match(b)
            if m and len(m.group(1).split()) <= 6: f.append(f"RD6 topic lead-in buried after <br>: '{m.group(1)}:'")
    return f
def warn(s):
    t = R.text_of(s); w = []
    if re.search(r"\b(?:[A-Z]{2,}[\s,–-]+){4,}", t): w.append("RD9 ALL-CAPS run kept as written")
    return w
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="*"); ap.add_argument("--base", default="pre-readability-1")
    ap.add_argument("--no-render", action="store_true"); ap.add_argument("--golden"); ap.add_argument("--capture", action="store_true"); ap.add_argument("--json")
    a = ap.parse_args()
    files = [pathlib.Path(x).resolve() for x in a.files] or R.scope(ROOT)
    files = [f for f in files if "/archive/" not in str(f) and "/previews/" not in str(f)]
    fails, warns, skipped, tpls = {}, {}, {}, {}
    for f in files:
        s = f.read_text(encoding="utf-8"); rel = str(f.relative_to(ROOT)); ff = []
        if f.name in R.SKIP: skipped[rel] = R.SKIP[f.name]; continue
        m = re.search(r'class="ph-rd ph-rd-(\w+)', s); tpl = m.group(1) if m else None; tpls[rel] = tpl
        if not tpl or 'id="ph-read-css"' not in s: ff.append("RD1 not on the shared readability style (run scripts/readability.py)")
        try: base = subprocess.run(["git", "show", f"{a.base}:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        except subprocess.CalledProcessError: base = None
        if base is not None and R.text_of(base) != R.text_of(s): ff.append(f"RD12 wording changed vs {a.base} (layout-only rule)")
        ff += html_fails(s); w = warn(s)
        if ff: fails[rel] = ff
        if w: warns[rel] = w
    if not a.no_render:
        from playwright.sync_api import sync_playwright
        class Q(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *x): pass
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT)))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        with sync_playwright() as p:
            b = p.chromium.launch()
            views = {"desktop": dict(viewport={"width": 1280, "height": 900}), "mobile": dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True)}
            pages = {v: b.new_page(**kw) for v, kw in views.items()}
            for pg in pages.values(): pg.route(re.compile(r"^https?://(?!127\.0\.0\.1)"), lambda r: r.abort())
            for rel, tpl in tpls.items():
                if not tpl: continue
                ff = fails.setdefault(rel, []); table = tpl == "table"
                for v, pg in pages.items():
                    try: pg.goto(f"http://127.0.0.1:{srv.server_port}/{rel}", wait_until="load", timeout=20000); r = pg.evaluate(JS, tpl)
                    except Exception as e: ff.append(f"[{v}] render error {e}"[:120]); continue
                    for x in r["blocks"]:
                        if x["fs"] < (15 if table else 18): ff.append(f"RD1 [{v}] text {x['fs']}px: '{x['t']}'")
                        if x["lh"] < (1.45 if table else 1.55): ff.append(f"RD2 [{v}] line-height {x['lh']}: '{x['t']}'")
                        if v == "desktop" and not table and x["cpl"] > 75: ff.append(f"RD3 [desktop] {x['cpl']} characters per line: '{x['t']}'")
                        if v == "desktop" and x["words"] > 120: warns.setdefault(rel, []).append(f"RD8 {x['words']}-word block (no email break to split at): '{x['t']}'")
                    for x in r["meta"]:
                        if x["fs"] < 16 and not table: ff.append(f"RD10 [{v}] meta text {x['fs']}px: '{x['t']}'")
                        if x["cr"] < 4.5: ff.append(f"RD10 [{v}] contrast {x['cr']}:1: '{x['t']}'")
                    if v == "mobile":
                        for x in r["taps"]:
                            if x["h"] < 44: ff.append(f"RD11 [phone] tap target {x['h']}px: '{x['t']}'")
                    if a.golden:
                        g = pathlib.Path(a.golden); g.mkdir(parents=True, exist_ok=True)
                        if a.capture: pg.screenshot(path=str(g / f"{pathlib.Path(rel).stem}-{v}.png"), full_page=True)
                if not ff: fails.pop(rel)
            b.close()
    fails = {k: sorted(set(v)) for k, v in fails.items() if v}
    print(f"PHNEWS readability guard (RD1-RD13): {len(tpls)} pages checked, {len(skipped)} skipped tool pages, {len(fails)} failing, {len(warns)} with warnings")
    for k, v in sorted(fails.items()): print("  FAIL", k); [print("     ", x) for x in v[:6]]
    if a.json: json.dump({"fails": fails, "warns": {k: sorted(set(v)) for k, v in warns.items()}, "skipped": skipped, "templates": tpls}, open(a.json, "w"), indent=1)
    sys.exit(1 if fails else 0)
if __name__ == "__main__": main()
