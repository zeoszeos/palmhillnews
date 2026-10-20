# Oct 25 clone of recurring_oct18.py (issue/window/Vol-No moved)
"""Oct 18 Recurring pages (Steven Oct 16 11:16 PM, STYLE-RULES R20): window starts on the issue date and matches the
issue's Recurring band; Vol 1 No 14; data = newest calendar snapshot (data/cal-*.json, R21) with build_oct18's AS_RECURRING.
Writes ungrouped pages to source/recurring-oct25-orig/ (gen.py format); recurring_grouped.py then applies Option B."""
import json, re, sys
from datetime import date, datetime
from html import escape
from pathlib import Path
sys.path.insert(0, "/workspace/oct18-batch/scripts"); from style_rules import mon3_text
ROOT = Path(__file__).resolve().parent.parent
ISSUE = "2026-10-25"; RECURRING = ("2026-10-25", "2026-11-23"); VOLNO = "Vol. 1, No. 15"
AS_RECURRING = {"Hand and Foot Cards", "Ukulele Group", "Ear Wax Removal", "I Got It", "Karaoke Obi-Time", "Writing Club"}
CAL = "https://www.palmhillcountryclub.net/calendar-1/"
MON3 = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
def pdate(iso): d = date.fromisoformat(iso); return f"{d:%A}, {MON3[d.month-1]} {d.day}, {d.year}"
def ptime(v):
    if not v: return "Time not listed"
    t = datetime.strptime(v, "%H:%M"); return f"{(t.hour % 12) or 12}:{t:%M} {t:%p}"
def place(e):
    if e.get("offSite") and e.get("place"): return e["place"]
    v = e.get("venue", "")
    return {"North Main Hall": "North Clubhouse", "South Main Hall": "South Clubhouse", "Board Room South": "South Clubhouse Boardroom"}.get(v, v)
def md(iso): d = date.fromisoformat(iso); return f"{MON3[d.month-1]} {d.day}"
def longd(iso): d = date.fromisoformat(iso); return f"{MON3[d.month-1]} {d.day}, {d.year}"
CM = re.compile(r"\bcommittee\b.*\bmeeting\b|\bboard of directors\b", re.I)
# STYLE-RULES R21 (Oct 17 additions-2): use the newest calendar re-pull snapshot, not the Oct 15 one (Nov 4 Coffee 8:00-9:00)
CALSNAP = sorted((ROOT / "data").glob("cal-2*.json"))[-1]; print("recurring_oct18: calendar", CALSNAP.name)
events = json.load(open(CALSNAP))["events"]
k = lambda e: (e["date"], e.get("start") or "99:99", e["name"])
rec = sorted([e for e in events if e.get("status") == "CONFIRMED" and e.get("name") != "Private Event"
              and RECURRING[0] <= e["date"] <= RECURRING[1] and (e.get("recurring") or e["name"] in AS_RECURRING)
              and not CM.search(e.get("name", ""))], key=k)
assert rec[0]["date"] >= ISSUE, "R20: recurring window must start on the issue date"
orders = ("date", "name", "location"); LBL = {"date": "By Date", "name": "By Name", "location": "By Location"}
def rows(o):
    if o == "date": return rec
    if o == "name": return sorted(rec, key=lambda e: (e["name"], e["date"], e.get("start", "")))
    return sorted(rec, key=lambda e: (place(e) in ("TBD", "TBS"), place(e), e["date"], e.get("start") or "99:99", e["name"]))
out = ROOT / "source/recurring-oct25-orig"; out.mkdir(parents=True, exist_ok=True)
for o in orders:
    cur = lambda x: ' aria-current="page"' if x == o else ""
    nav = ('<nav class="ph-links" aria-label="Activity views">' + '<span class="ph-dot"> · </span>'.join(
        f'<a href="{ISSUE}-recurring-activities-by-{x}.html"{cur(x)}>{LBL[x]} →</a>' for x in orders) +
        '</nav>\n<p class="ph-source ph-lead-center" style="margin:0 0 6px;">Source: <a href="' + CAL + '" style="color:#3a6b1a;">Calendar</a></p>')
    acts = "".join(f'<div class="ph-row{" ph-alt" if i % 2 else ""}"><div class="ph-row-line"><div class="ph-row-title">{escape(e["name"])}</div>'
                   f'<div class="ph-row-loc">{escape(place(e))}</div></div><div class="ph-row-meta">{escape(pdate(e["date"]))} • {escape(ptime(e.get("start")))}</div></div>\n'
                   for i, e in enumerate(rows(o)))
    T = "Recurring Meetings &amp; Events"
    main = (f'<h1 class="ph-section">{T}<span class="ph-section-sub">{md(RECURRING[0])} through {longd(RECURRING[1])}</span></h1>\n'
            f'<div class="ph-section-date"><span class="ph-section-volno">{escape(VOLNO)}</span><span class="ph-section-issuedate">{longd(ISSUE)}</span></div>\n{nav}\n'
            '<p class="ph-lead ph-lead-center">Times and rooms are subject to change. The club calendar may require sign-in.</p>\n'
            f'<p class="ph-view ph-view-title">{LBL[o]}</p>\n<div class="ph-activities" data-activity-count="{len(rec)}">\n{acts}</div>')
    h = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{T} — {LBL[o]} — Palm Hill Country Club</title>
<link rel="stylesheet" href="/pages/assets/ph-newsletter.css">
</head>
<body>
<!-- Shell: /pages/assets/ph-newsletter-shell.html — one column, no min-width table, no pill links. -->
<div class="ph-page">
<main class="ph-body">
{main}
</main>
</div>
</body>
</html>
'''
    (out / f"{ISSUE}-recurring-activities-by-{o}.html").write_text(mon3_text(h), encoding="utf-8")
print("recurring Oct 25:", len(rec), "rows", rec[0]["date"], "->", rec[-1]["date"])
