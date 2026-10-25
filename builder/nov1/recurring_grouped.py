"""Batch item 10 (Steven, Oct 16): grouped Recurring pages. Input: untouched Oct 11 pages in ../source/recurring-oct11-orig/.
Output: REPO/pages/2026-10-11-recurring-activities-by-{date,name,location}.html (same URLs).
Option B sticky 'Sort by' pills; Source + note tightened into the header strip; sort-name band above the data;
bold group headings with (n) counts; item lines regular weight."""
import re, sys
from pathlib import Path
REPO = Path(sys.argv[1]); ISSUE = sys.argv[2] if len(sys.argv) > 2 else "2026-10-11"  # STYLE-RULES R20: one set per issue
SRC = Path(__import__("os").environ.get("PHNEWS_WORK") or "/workspace/phnews-consolidation/nov1") / f"source/recurring-{ISSUE[5:7]}{ISSUE[8:]}-orig".replace("recurring-1011-", "recurring-oct11-").replace("recurring-1018-", "recurring-oct18-").replace("recurring-1025-", "recurring-oct25-").replace("recurring-1101-", "recurring-nov1-")
F = ISSUE + "-recurring-activities-by-%s.html"
LAB = {"date": "By Date", "name": "By Name", "location": "By Location"}
CSS = """.sx-sticky{position:sticky;top:0;z-index:5;background:#e8f2e0;border-bottom:1px solid #c9dcbc;margin:12px -14px 0;padding:9px 14px;display:flex;align-items:center;gap:6px;flex-wrap:nowrap;font-family:Arial,sans-serif}
.sx-sticky b{font-size:14px;color:#2d5016;white-space:nowrap}
.sx-sticky a{padding:6px 10px;white-space:nowrap;border-radius:999px;border:2px solid #2d5016;color:#2d5016;background:#fff;font-size:14px;font-weight:bold;text-decoration:none}
.sx-sticky a[aria-current]{background:#2d5016;color:#fff}
.sx-note{margin:0 -14px 10px;padding:4px 14px 7px;background:#e8f2e0;border-bottom:2px solid #2d5016;font:13px/1.4 Arial,sans-serif;color:#555}
.sx-note a{color:#3a6b1a}
.sx-band{margin:0 0 4px;padding:7px 10px;background:#2d5016;color:#fff;font:bold 17px/1.3 Arial,sans-serif;text-align:center;letter-spacing:.3px;border-radius:4px}
.gx-h{margin:12px 0 0;padding:6px 8px;background:#e8f2e0;border-left:4px solid #2d5016;font:bold 16px/1.3 Arial,sans-serif;color:#2d5016}
.gx-h .n{font-weight:normal;font-size:13px;color:#555;margin-left:6px}
.ph-activities .ph-row .ph-row-title{font-weight:normal}"""
for k in LAB:
    s = (SRC / (F % k)).read_text(encoding="utf-8")
    rows = re.findall(r'ph-row-title">(.*?)</div><div class="ph-row-loc">(.*?)</div></div><div class="ph-row-meta">(.*?)</div>', s)
    groups = {}
    for t, l, m in rows:
        d, tm = m.split(" • ")
        groups.setdefault({"date": d, "location": l, "name": t}[k], []).append((t, l, d, tm))
    out = []
    for g, items in groups.items():
        out.append(f'<h2 class="gx-h">{g}<span class="n">({len(items)})</span></h2>')
        for i, (t, l, d, tm) in enumerate(items):
            dd = d.replace(", 2026", "")
            L, R = {"date": (f"{tm} · {t}", l), "location": (t, f"{dd} • {tm}"), "name": (f"{dd} • {tm}", l)}[k]
            out.append(f'<div class="ph-row{" ph-alt" if i % 2 else ""}"><div class="ph-row-line"><div class="ph-row-title">{L}</div><div class="ph-row-loc">{R}</div></div></div>')
    nav = ('<nav class="sx-sticky" aria-label="Sort by"><b>Sort by:</b>'
           + "".join(f'<a href="{F % x}"{" aria-current=\"page\"" if x == k else ""}>{LAB[x][3:]}</a>' for x in LAB) + "</nav>\n"
           '<p class="sx-note">Source: <a href="https://www.palmhillcountryclub.net/calendar-1/">Calendar</a> · Times and rooms are subject to change. The club calendar may require sign-in.</p>\n'
           f'<p class="sx-band" role="heading" aria-level="2">{LAB[k]}</p>\n')
    a = s.index('<nav class="ph-links"'); b = s.index('<div class="ph-activities"')
    s = s[:a] + nav + s[b:]
    s = re.sub(r'(<div class="ph-activities"[^>]*>).*?(</div>\s*</main>)', lambda m: m.group(1) + "\n" + "\n".join(out) + "\n" + m.group(2), s, flags=re.S)
    s = s.replace("</head>", f"<style>{CSS}</style>\n</head>", 1)
    sys.path.insert(0, __import__("os").path.join(__import__("os").environ.get("PHNEWS_REPO") or "/workspace/nov1-build", "scripts")); import style_rules as _sr
    s = _sr.enforce_title_months(s)
    s = re.sub(r'(ph-section-issuedate">)([A-Z][a-z]{2}) ', lambda m: m.group(1) + {k3[:3]: k3 for k3 in ("January","February","March","April","May","June","July","August","September","October","November","December")}[m.group(2)] + " ", s)
    sys.path.insert(0, str(REPO / "scripts")); import readability as _rd  # STYLE-RULES RD1-RD13 (recurring tables: 15px/1.5)
    (REPO / "pages" / (F % k)).write_text(_rd.apply(s, F % k)[0], encoding="utf-8")
    print(k, len(rows), "rows", len(groups), "groups")
