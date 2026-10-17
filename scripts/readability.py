#!/usr/bin/env python3
"""STYLE-RULES RD1-RD13 (Steven, Oct 17 2026, 3:44 AM): readability pass for palmhillnews.vercel.app reading pages,
written for an over-55 audience. It changes LAYOUT ONLY and never a word.

  apply(html, name) -> (html, template)   idempotent; template None = not a reading page (skipped)
  python3 scripts/readability.py [--check] [FILES...]   default: every pages/*.html + pages/information/*.html in scope

What it does:
  * links /pages/assets/ph-read.css (the shared style) right before </head> and tags <body> with "ph-rd ph-rd-<template>"
    (RD1-RD3, RD10, RD11; the CSS is scoped to those classes, so archive hubs and newsletter issues are untouched);
  * for email-derived templates, reflows <br>-walls into real paragraphs (RD4), rejoins hard breaks after abbreviations
    or before a lowercase word (RD5), starts a paragraph at short "Topic label:" lead-ins and bolds the label (RD6),
    turns "- " / "• " / "1." lines into lists that keep their marker (RD7);
  * RD12 WORDING LOCK: the visible text before == after (whitespace-normalised) or it raises, which stops the build.
Out of scope (RD13): pages/archive/** (hubs and archived newsletter issues), pages/previews/**, app/table tools in SKIP."""
import re, sys, html as H, pathlib
CSS_HREF = "/pages/assets/ph-read.css"
LINK = f'<link rel="stylesheet" href="{CSS_HREF}" id="ph-read-css">'
# app / tool pages: interactive grids, maps and calendars -- not running text (flagged, not changed)
SKIP = {"2026-10-04-complete-calendar.html": "interactive calendar app", "palm-hill-street-map.html": "map page",
        "2026-10-04-committee-video-guide.html": "video tile grid", "committee-board-meetings.html": "meeting schedule grid",
        "2026-10-04-regularly-scheduled-activities-by-activity.html": "activity schedule grid",
        "2026-10-04-regularly-scheduled-activities-by-date.html": "activity schedule grid",
        "regularly-scheduled-activities-by-activity.html": "activity schedule grid", "regularly-scheduled-activities.html": "activity schedule grid",
        "2026-07-15-monthly-management-and-maintenance-report-2026-07-.html": "PDF page-image viewer"}
REFLOW = {"early", "card", "simple", "message"}          # email-derived text (webmaster/manager emails)
def template(name, s):
    if name in SKIP: return None
    head = s[: s.find("</head>")] if "</head>" in s else s[:4000]
    if "recurring-activities-by-" in name: return "table"
    if re.search(r"\.summary\s*\{\s*font-size:\s*15px", head) and "max-width: 600px" in head: return "early"
    if re.search(r"font:(?:19|17)px/1\.7\d? Georgia", head): return "message"
    if "/pages/shared/ph-info.css" in head and "content-card" in s: return "card"
    if "/pages/assets/ph-newsletter.css" in head: return "shell"
    if "shared/ph-info.css" in head and 'class="card"' in s: return "info"
    if re.search(r"body\s*\{[^}]*font-family:\s*Arial", head) and "<table" not in s and "<script" not in s.split("</head>")[-1]: return "simple"
    if 'class="ph-rd ' in s: m = re.search(r'class="ph-rd ph-rd-(\w+)', s); return m.group(1)
    return None
def text_of(s):
    s = s[s.find("<body"):] if "<body" in s else s
    s = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
ABBR = re.compile(r"\b(?:Mon|Tue|Tues|Wed|Thu|Thurs|Fri|Sat|Sun|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|St|Dr|Mr|Mrs|Ms|No|approx|vs)\.$")
LABEL = re.compile(r"^([A-Z][A-Za-z0-9&'’/ -]{1,50}?):\s+(?=\S)")
LIST = re.compile(r"^(?:[-•*–]|\d{1,2}[.)])\s+")
BR = r"<br\s*/?>"
def plain(x): return H.unescape(re.sub(r"<[^>]+>", "", x)).strip()
def split_wall(inner):
    out = []
    for chunk in re.split(rf"(?:\s*{BR}\s*){{2,}}", inner):
        lines = []
        for seg in (x.strip() for x in re.split(BR, chunk)):
            if not seg: continue
            if lines and (ABBR.search(plain(lines[-1])) or re.match(r"[a-z]", plain(seg))): lines[-1] += " " + seg  # RD5
            else: lines.append(seg)
        para, lst = None, None
        def flush():
            nonlocal para, lst
            if para is not None: out.append(f"<p>{para}</p>"); para = None
            if lst is not None: out.append('<ul class="ph-rd-list">' + "".join(f"<li>{i}</li>" for i in lst) + "</ul>"); lst = None
        for ln in lines:
            t = plain(ln); m = LABEL.match(ln)
            if LIST.match(t):                                       # RD7: list item, marker kept
                if para is not None: out.append(f"<p>{para}</p>"); para = None
                lst = (lst or []) + [ln]; continue
            if lst is not None: flush()
            if m and len(m.group(1).split()) <= 6 and not re.match(r"^\d", m.group(1)):   # RD6: topic lead-in
                flush(); para = f"<strong>{m.group(1)}:</strong> " + ln[m.end():]; continue
            short = len(t.split()) <= 6 and not re.search(r"[.!?:]$", t)
            if para is None or short or len(plain(para).split()) >= 60:
                flush(); para = ln
                if short: flush()
            else: para += " " + ln
        flush()
    return "".join(out)
def needs(inner):
    if len(re.findall(BR, inner)) >= 4: return True
    segs = [plain(x) for x in re.split(BR, inner)]
    for a, b in zip(segs, segs[1:]):
        if ABBR.search(a) or re.match(r"[a-z]", b) or LIST.match(b) or (LABEL.match(b) and len(LABEL.match(b).group(1).split()) <= 6): return True
    return False
def reflow(s):
    def fix_p(m):
        inner = m.group(2)
        return split_wall(inner) if BR[:3] in inner and needs(inner) else m.group(0)
    s = re.sub(r"<p( [^>]*)?>((?:(?!</?p[ >]).)*?)</p>", fix_p, s, flags=re.S)
    # .summary div holding bare text with <br> (no <p>)
    def fix_div(m):
        inner = m.group(2)
        return m.group(1) + (split_wall(inner) if "<p" not in inner and "<br" in inner and needs(inner) else inner) + "</div>"
    return re.sub(r'(<div class="summary"[^>]*>)((?:(?!</?div).)*?)</div>', fix_div, s, flags=re.S)
def apply(s, name):
    tpl = template(name, s)
    if tpl is None: return s, None
    before = text_of(s)
    if 'id="ph-read-css"' not in s: s = s.replace("</head>", LINK + "\n</head>", 1) if "</head>" in s else s
    cls = f"ph-rd ph-rd-{tpl}" + (" ph-rd-small" if tpl == "message" and "font:17px/1.7 Georgia" in s[: s.find("</head>")] else "")
    if 'class="ph-rd ' not in s:
        m = re.search(r"<body\b([^>]*)>", s)
        if m:
            attrs = m.group(1)
            if re.search(r'\bclass="', attrs): attrs = re.sub(r'\bclass="', f'class="{cls} ', attrs, 1)
            else: attrs += f' class="{cls}"'
            s = s[:m.start()] + f"<body{attrs}>" + s[m.end():]
    # RD10: the "Sent to Palm Hill residents by email on …" footnote is a meta line (16px #555), not body text
    s = re.sub(r'<p style="(font:15px/1\.5 Arial,sans-serif;color:#53604e;[^"]*)">(?=Sent to Palm Hill residents)', r'<p class="ph-rd-meta" style="\1">', s)
    if tpl in REFLOW:
        a = s.find("<body"); s = s[:a] + reflow(s[a:])
    if text_of(s) != before:  # RD12 wording lock
        raise SystemExit(f"RD12 wording lock: {name} visible text would change -- build stopped")
    return s, tpl
def scope(root):
    root = pathlib.Path(root)
    return sorted(list((root / "pages").glob("*.html")) + list((root / "pages/information").glob("*.html")))
if __name__ == "__main__":
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--only=")), None)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; check = "--check" in sys.argv
    files = [pathlib.Path(a) for a in args] or scope(pathlib.Path(__file__).resolve().parent.parent)
    from collections import Counter; c, changed = Counter(), Counter()
    for f in files:
        if "/archive/" in str(f) or "/previews/" in str(f): continue
        s = f.read_text(encoding="utf-8")
        if only and template(f.name, s) not in only: continue
        n, tpl = apply(s, f.name); c[tpl or "skipped"] += 1
        if n != s:
            changed[tpl] += 1
            if not check: f.write_text(n, encoding="utf-8")
    print("templates:", dict(c)); print(("would change:" if check else "changed:"), dict(changed))
    if check and sum(changed.values()): sys.exit(1)
