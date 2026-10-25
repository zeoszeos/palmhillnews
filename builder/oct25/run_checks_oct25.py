"""Oct 25, 2026 locked checks (A1/A2/A3, Steven-approved Oct 24 2026 2:26 PM, Claude review). STYLE-RULES R64.

Fail-closed: any FAIL -> exit 1. Expectations come from the build audit (calendar data) and the locked content lists in
locked_checks_oct25.py -- never scraped from the page being checked (old L11 scrape removed). The Oct 11-era layout locks
(L03/L05-L08/L12/L14-L17/L26/L27b-c) were superseded by later STYLE-RULES (R18/R45/R59-R63...) and the builder's own inline
guards; they are rewritten here against the current markup instead of being silently skipped.
Usage: python3 run_checks_oct25.py [issue.html]   (default ../PHNEWS-2026-10-25-preview.html). build_oct25.py runs it.
"""
import json, re, sys, importlib.util
from pathlib import Path
H = Path(__file__).resolve().parent
def _load(name, f):
    spec = importlib.util.spec_from_file_location(name, H / f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
lc = _load("lc25", "locked_checks_oct25.py")
ROOT = Path(__import__("os").environ.get("PHNEWS_WORK") or "/workspace/phnews-consolidation/oct18")  # R67 work tree (batch 3)
page_f = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "PHNEWS-2026-10-25-preview.html"
page = page_f.read_text(encoding="utf-8")
audit = json.load(open(ROOT / "build-audit-oct25.json"))
L = lc.Locks()
T = r'font-weight:bold;color:#333333;text-align:left;padding-right:\d+px;">([^<]+)<'
norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower().replace("&amp;", "&"))
titles = lambda sec: re.findall(T, sec)
text = lambda h: " ".join(re.sub(r"<[^>]+>", " ", h).split())

# L01/L02 masthead
L.ok("L01", re.search(r'header-volno"[^>]*>Vol\. 1, No\. 15</span>', page) is not None, "Vol. 1, No. 15 in the address bar")
L.ok("L02", page.count(">Sunday, October 25, 2026</span>") == 1 and page.count("masthead-palm-hd-320x334-v1.png") == 2, "issue date Sunday, October 25, 2026; HD palm x2")
# L03 section order (Oct 25 approved order)
ORDER = ["Committee &amp; Board Meeting Schedules", "Committee Chair Reports", "Events - This Week", "Recurring Meetings &amp; Events",
         "Community Notices", "Monthly Shareholders Report", "Weekly Manager Update", "Events - Upcoming", "Community Stories",
         "From the Board President", "Did You Know?", "Residents Reference Guide"]
got = [t for _, t in lc._headings(page)]
L.ok("L03", got == ORDER, f"section order {got}")
for bad in ("Block Captain", "Test Meeting", "Private Event", "Real Estate Committee Report", "Rules and Regulations Committee Report"):
    L.ok("L04", bad not in page, f'"{bad}" absent')
# L05/L26 Meetings = audit (calendar) rows, window in header
sec = lc._section(page, "Committee &amp; Board Meeting Schedules")
L.ok("L05", [norm(x) for x in titles(sec)] == [norm(n) for _, n in audit["meetings"]], f"Meetings rows {titles(sec)}")
L.ok("L05b", len(titles(sec)) == len(set(titles(sec))), "one meeting per committee")
L.ok("L26", ">October 25 through November 24<" in sec, "Meetings window October 25 through November 24 in header")
L.ok("L06", sec.count('text-align:right;padding-top:1px;">') >= len(audit["meetings"]), "Meetings: location right-aligned on title line")
fi = text(sec[sec.find(">Finance Committee<"):])
fi = fi[:fi.find("Source")]
L.ok("R62b", "Wednesday, Nov 18, 2026" in fi and "10:00 AM" in fi and "to be confirmed" not in fi and "Nov 16" not in fi, f"Finance row {fi[:90]}")
pe = text(sec[sec.find(">Planning and Environmental Committee Meeting<"):]); pe = pe[:pe.find("Source")]
L.ok("R62", "Tuesday, Nov 10, 2026" in pe and "12:30 PM" in pe and "to be confirmed" not in pe, f"P&E row {pe[:90]}")
# L07/L08 This Week / Upcoming = audit rows; treat-as-recurring never there
tw = lc._section(page, "Events - This Week"); up = lc._section(page, "Events - Upcoming")
L.ok("L07", [norm(x) for x in titles(tw)] == [norm(n) for _, n in audit["this_week"]] and ">October 25 through October 31<" in tw, f"This Week rows {titles(tw)}")
L.ok("L08", [norm(x) for x in titles(up)] == [norm(n) for _, n in audit["upcoming"]] and ">November 1 through November 22<" in up, f"Upcoming rows {titles(up)}")
# A3: one shared treat-as-recurring list
b25 = (H / "build_oct25.py").read_text(encoding="utf-8")
_as = lambda src: set(eval(re.search(r"^AS_RECURRING = (\{[^}]*\})", src, re.M).group(1)))
L.ok("L09a", set(lc.TREAT_AS_RECURRING) == _as(b25) == _as((H / "recurring_oct25.py").read_text(encoding="utf-8")), "TREAT_AS_RECURRING == builder/recurring AS_RECURRING")
for n in lc.TREAT_AS_RECURRING:
    L.ok("L09", n not in tw and n not in up, f'This Week/Upcoming exclude "{n}"')
# L11 Community Notices (locked list, not scraped)
cn = lc._section(page, "Community Notices")
L.ok("L11", titles(cn) == lc.NOTICES_EXPECTED, f"Notices rows {titles(cn)}")
L.ok("L11b", "From the Board President" not in cn, "President not inside Notices")
# L12 Board President section
bp = lc._section(page, "From the Board President")
L.ok("L12", page.count(">From the Board President</span>") == 1 and ">Read Full Message →</a>" in bp and ">President's Message Archives →</a>" in bp
     and "Source: Henry Klain, Board President" in bp and ">Listen</a>" in bp, "Board President: Read Full Message, Archives, Listen, Source")
# L13-L16 Chair reports
ch = lc._section(page, "Committee Chair Reports")
L.ok("L13", titles(ch) == list(lc.CHAIR_EXPECTED), f"chair rows {titles(ch)}")
for t, intro in lc.CHAIR_EXPECTED.items():
    L.ok("L13b", intro.replace("&", "&amp;") in ch or intro in ch, f"intro: {t}")
L.ok("L14", "Wednesday, Oct 14, 2026" in ch and "Tuesday, Oct 13, 2026" in ch, "chair dates P&E Oct 14, Golf Oct 13 (3-letter months)")
n = len(lc.CHAIR_EXPECTED)
L.ok("L15", len(re.findall(r">\s*Listen\s*</a>", ch)) == n and "Listen to the Chair Report" not in ch, "one Listen per chair report")
L.ok("L16", ch.count(">Read Full Report →</a>") == n and ">Committee Report Archives →</a>" in ch, "Read Full Report → each + archives link")
# L17 Recurring
rc = lc._section(page, "Recurring Meetings &amp; Events")
L.ok("L17", ">October 25 through November 23, 2026<" in rc and rc.count(lc.BASE + "2026-10-25-recurring-activities-by-") == 3
     and "confirmed recurring" not in rc.lower(), "Recurring: Oct 25 window, By Date/Name/Location pages")
# no stale Oct 18 issue dates leaked into links
L.ok("L31", "previews/2026-10-18" not in page and "2026-10-18-recurring" not in page, "no Oct 18 preview/recurring links")
L2 = lc.Locks(); lc.check_title_months(L2, {"newsletter": page})
# L27b/c webmaster-source counts: superseded by R47 (style_rules.assert_webmaster_more), enforced inside the builder
res = L.results + L2.results
for r in res: print(r)
fails = [r for r in res if r[1] == "FAIL"]
print(f"run_checks_oct25: {len(res) - len(fails)} PASS, {len(fails)} FAIL")
sys.exit(1 if fails else 0)
