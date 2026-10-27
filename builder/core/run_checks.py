"""Oct 25, 2026 locked checks (A1/A2/A3, Steven-approved Oct 24 2026 2:26 PM, Claude review). STYLE-RULES R64.

Fail-closed: any FAIL -> exit 1. Expectations come from the build audit (calendar data) and the locked content lists in
locked_checks.py -- never scraped from the page being checked (old L11 scrape removed). The Oct 11-era layout locks
(L03/L05-L08/L12/L14-L17/L26/L27b-c) were superseded by later STYLE-RULES (R18/R45/R59-R63...) and the builder's own inline
guards; they are rewritten here against the current markup instead of being silently skipped.
Usage: python3 builder/core/run_checks.py [issue.html] with PHNEWS_ISSUE set (default WORK/PHNEWS-<issue>-preview.html). build_core.py runs it.
"""
import os as _os, sys as _sys; _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent)); import issue_ctx as _ix; C = _ix.load()  # R71 content file
import json, re, sys, importlib.util
from pathlib import Path
import html as _html; _sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts")); import style_rules as _sr83  # R83
H = Path(__file__).resolve().parent
def _load(name, f):
    spec = importlib.util.spec_from_file_location(name, H / f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
lc = _load("lc_core", "locked_checks.py")
ROOT = Path(__import__("os").environ.get("PHNEWS_WORK") or str(C.DEFAULT_WORK))  # R67 work tree (batch 3)
page_f = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / f"PHNEWS-{C.ISSUE}-preview.html"
page = page_f.read_text(encoding="utf-8")
audit = json.load(open(ROOT / f"build-audit-{C.SHORT}.json"))
L = lc.Locks()
_W = lambda k: f"{_ix.md_full(C.WINDOWS[k][0])} through {_ix.md_full(C.WINDOWS[k][1])}"  # R69 window label
T = r'font-weight:bold;color:#333333;text-align:left;padding-right:\d+px;">([^<]+)<'
norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower().replace("&amp;", "&"))
titles = lambda sec: re.findall(T, sec)
text = lambda h: " ".join(re.sub(r"<[^>]+>", " ", h).split())

# L01/L02 masthead
L.ok("L01", re.search(r'header-volno"[^>]*>' + re.escape(C.VOLNO) + r'</span>', page) is not None, f"{C.VOLNO} in the address bar")
L.ok("L02", page.count(f">Sunday, {C.ISSUE_LONG}</span>") == 1 and page.count("masthead-palm-hd-320x334-v1.png") == 2, f"issue date Sunday, {C.ISSUE_LONG}; HD palm x2")
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
if getattr(C, "MEETINGS_ALL_IN_WINDOW", False):   # R87 (Nov 1+): repeats allowed, exact date+committee duplicates never
    L.ok("L05b", len(audit["meetings"]) == len({tuple(x) for x in audit["meetings"]}), "no meeting listed twice for the same date (R87)")
else:
    L.ok("L05b", len(titles(sec)) == len(set(titles(sec))), "one meeting per committee")
if getattr(C, "MEETINGS_SHOW_RANGE", True):   # R78: Oct 25 and earlier keep the range
    L.ok("L26", f">{_W('MEETINGS')}<" in sec, f"Meetings window {_W('MEETINGS')} in header")
else:
    _hd = sec[:sec.find("<table")]
    L.ok("R78", " through " not in _hd and not re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) \d", _hd),
         "Meetings header has no date range (R78, Nov 1 on)")
L.ok("L06", sec.count('text-align:right;padding-top:1px;">') >= len(audit["meetings"]), "Meetings: location right-aligned on title line")
for _mc in C.MEETING_ROW_CHECKS:  # R62/R62b expected wording = content file data
    _mt = text(sec[sec.find(_mc["start"]):]); _mt = _mt[:_mt.find("Source")]
    L.ok(_mc["rule"], all(x in _mt for x in _mc["need"]) and not any(x in _mt for x in _mc["never"]),
         f"{'Finance' if 'Finance' in _mc['start'] else 'P&E'} row {_mt[:90]}")
# L07/L08 This Week / Upcoming = audit rows; treat-as-recurring never there
tw = lc._section(page, "Events - This Week"); up = lc._section(page, "Events - Upcoming")
L.ok("L07", [norm(x) for x in titles(tw)] == [norm(n) for _, n in audit["this_week"]] and f">{_W('THIS_WEEK')}<" in tw, f"This Week rows {titles(tw)}")
L.ok("L08", [norm(x) for x in titles(up)] == [norm(n) for _, n in audit["upcoming"]] and f">{C.UPCOMING_LABEL_EXPECTED}<" in up, f"Upcoming rows {titles(up)}")
# A3: one shared treat-as-recurring list
b25 = (H / "build_core.py").read_text(encoding="utf-8")
_as = lambda src: set(eval(re.search(r"^AS_RECURRING = (\{[^}]*\})", src, re.M).group(1)))
L.ok("L09a", set(lc.TREAT_AS_RECURRING) == _as(b25) == _as((H / "recurring.py").read_text(encoding="utf-8")), "TREAT_AS_RECURRING == builder/recurring AS_RECURRING")
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
L.ok("L14", all(d in ch for d in C.CHAIR_DATES_EXPECTED), C.CHAIR_DATES_LABEL)
n = len(lc.CHAIR_EXPECTED)
L.ok("L15", len(re.findall(r">\s*Listen\s*</a>", ch)) == n and "Listen to the Chair Report" not in ch, "one Listen per chair report")
L.ok("L16", ch.count(">Read Full Report →</a>") == n and ">Committee Report Archives →</a>" in ch, "Read Full Report → each + archives link")
# L17 Recurring
rc = lc._section(page, "Recurring Meetings &amp; Events")
L.ok("L17", f">{_W('RECURRING')}, 2026<" in rc and rc.count(lc.BASE + f"{C.ISSUE}-recurring-activities-by-") == 3
     and "confirmed recurring" not in rc.lower(), C.RECURRING_CHECK_LABEL)
# no stale Oct 18 issue dates leaked into links
L.ok("L31", "previews/2026-10-18" not in page and "2026-10-18-recurring" not in page, "no Oct 18 preview/recurring links")
# R77 chair report from a chair's email: page = the chair's wording block by block (no edits), title without the meeting date,
# one card per committee (a newer report replaces the older card)
from html import escape as _esc
_RP = Path(lc.__file__).resolve().parents[2] / "pages"
for _cr in getattr(C, "CHAIR_REPORTS", []):
    _pg = (_RP / _cr["page"]).read_text(encoding="utf-8") if (_RP / _cr["page"]).exists() else ""
    _bits = [x for k, v in _cr["blocks"] for x in (v if k == "ul" else [v])]
    L.ok("R77", bool(_pg) and all(_esc(b, quote=False) in _pg for b in _bits), f"chair wording verbatim: {_cr['page']}")
    L.ok("R77", not re.search(r"(?i)meeting of|\b(19|20)\d\d\b|report\W+report", _cr["title"]), f"chair title has no date / duplicate Report: {_cr['title']}")
L.ok("R77", len(titles(ch)) == len(set(titles(ch))), "one chair card per committee (newer replaces older)")
# R79 (Steven Oct 26 2026 11:25 AM): from Nov 1 both Events sections link "See the All Events List" to the All Events page; the
# page carries Steven's note verbatim, has no Recurring-page event, and lists every window event not on the Recurring pages.
if getattr(C, "ALL_EVENTS_PAGE", False):
    _aef = f"{C.ISSUE}-all-events-by-date.html"; _ael = f'href="{lc.BASE}{_aef}" style="color:#3A6B1A;">{C.ALL_EVENTS_LINK_TEXT}</a>'
    for _sn in ("Events - This Week", "Events - Upcoming"):
        L.ok("R79", _ael in lc._section(page, _sn), f"{_sn}: link '{C.ALL_EVENTS_LINK_TEXT}' -> {_aef}")
    _RPg = Path(_os.environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO)) / "pages"; _aeh = ""
    for _o in ("date", "name", "location"):   # Steven Oct 26 11:28 AM: same three sorts as Recurring, note on all three
        _p = _RPg / f"{C.ISSUE}-all-events-by-{_o}.html"; _h = _p.read_text(encoding="utf-8") if _p.exists() else ""
        L.ok("R79", bool(_h) and f'ph-all-events-note">{C.ALL_EVENTS_NOTE}</p>' in _h and all(f"{C.ISSUE}-all-events-by-{x}.html" in _h for x in ("date", "name", "location")),
             f"All Events {_o} page exists, note verbatim, sort tabs to all three: {_p.name}")
        if _o == "date": _aeh = _h
    _cal = json.load(open(ROOT / "data" / audit["calendar_file"]))["events"] if (ROOT / "data" / audit["calendar_file"]).exists() else json.load(open(audit["calendar_file"]))["events"]
    _w = C.WINDOWS["RECURRING"]; _asr = {"Hand and Foot Cards", "Ukulele Group", "Ear Wax Removal", "I Got It", "Karaoke Obi-Time", "Writing Club"}
    _cre = re.compile(r"\bcommittee\b|\bboard of directors\b", re.I)
    _base = [e for e in _cal if e.get("status") == "CONFIRMED" and e["name"] != "Private Event" and "test" not in e["name"].lower() and _w[0] <= e["date"] <= _w[1]]
    _rec = {(e["date"], e["name"]) for e in _base if e.get("recurring") or e["name"] in _asr}
    _exp = {(e["date"], e["name"]) for e in _base if (e["date"], e["name"]) not in _rec and not _cre.search(e["name"]) and e.get("category") not in ("CLOSURE",)
            and not e.get("allDay") and (e.get("category") != "Meetings" or e["name"] == "Palm Hill MasterPlan Team")}
    _got = {tuple(x) for x in audit.get("all_events", [])}
    L.ok("R79", not (_got & _rec), f"All Events has no Recurring-page event {sorted(_got & _rec)}")
    L.ok("R79", _got == _exp and f'data-activity-count="{len(_exp)}"' in _aeh, f"All Events = every window event not on Recurring ({len(_exp)}); missing {sorted(_exp - _got)} extra {sorted(_got - _exp)}")
# R80 (Steven Oct 26 2026 11:41 AM): every All Events row (all three sorts) has its own Source line with the linked Calendar,
# plus the linked Webmaster notice for every event the content maps to one (EVENT_EXTRA_SRC, the R48/R56 map); none invented.
if getattr(C, "ALL_EVENTS_PAGE", False):
    from html import escape as _esc
    _CALU = "https://www.palmhillcountryclub.net/calendar-1/"; _xs = dict(getattr(C, "EVENT_EXTRA_SRC", {}))
    _wanted = {n: u for n, u in _xs.items() if any(n == x[1] for x in _got)}
    for _o in ("date", "name", "location"):
        _h = (_RPg / f"{C.ISSUE}-all-events-by-{_o}.html").read_text(encoding="utf-8")
        _rows = []   # each row is prefixed with its group heading (the By Name page carries the name in the heading only)
        for _g in re.split(r'(?=<h2 class="gx-h">)', _h.split('class="ph-activities"', 1)[1]):
            _hd = (re.match(r'<h2 class="gx-h">(.*?)<span', _g) or [None, ""])[1]
            _rows += [f"[{_hd}] " + r for r in re.split(r'<div class="ph-row(?: ph-alt)?">', _g)[1:]]
        _nosrc = [r[:80] for r in _rows if f'ph-row-src' not in r or f'Source: <a href="{_CALU}"' not in r]
        L.ok("R80", len(_rows) == len(_got) and not _nosrc, f"All Events {_o}: {len(_rows)} rows, each with Source: Calendar (missing {_nosrc})")
        _bad = [n for n, u in _wanted.items() if not any(_esc(n) in r and f'<a href="{u}" style="color:#3a6b1a;">Webmaster</a>' in r for r in _rows)]
        _extra = [r[:60] for r in _rows if "Webmaster</a>" in r and not any(_esc(n) in r and u in r for n, u in _wanted.items())]
        L.ok("R80", not _bad and not _extra, f"All Events {_o}: Webmaster source on {sorted(_wanted)} only (missing {_bad}, unmapped {_extra})")
# R81 (Steven approved Oct 24 2026; go Oct 26 11:49 AM): Helpful Webpages has the 7 approved links; the two hub pages carry the moved links.
if getattr(C, "LINKS_SEVEN", False):
    _hw = page[page.index("Helpful Webpages</div>"):]; _hw = _hw[:_hw.index("</td>")]
    _lb = re.findall(r'<div>• <a href="([^"]+)"[^>]*>([^<]+)</a></div>', _hw)
    L.ok("R81", len(_lb) == 7 and (lc.BASE + "archive/videos.html", "Committee Meeting Videos") in _lb and (lc.BASE + "archive/palm-hill-link.html", "Palm Hill Link") in _lb
         and not any(t in ("Committee Meeting Videos - Latest", "Committee Meeting Video Archives", "Palm Hill Link Monthly", "Palm Hill Link Archives") for _, t in _lb),
         f"Helpful Webpages = 7 links {[t for _, t in _lb]}")
    _RA = Path(_os.environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO)) / "pages" / "archive"
    _vh = (_RA / "videos.html").read_text(encoding="utf-8"); _lh = (_RA / "palm-hill-link.html").read_text(encoding="utf-8")
    L.ok("R81", _vh.count("Committee Meeting Video Archives →</a>") == 1 and "meeting-videos.html" in _vh, "videos.html links Committee Meeting Video Archives")
    L.ok("R81", _lh.split('<h1 class="ph-section">', 1)[1].split("<a ", 1)[1].startswith('href="https://monthly-media.com/newsletter_download.php'), "palm-hill-link.html starts with the current monthly issue link")
# R82 (Steven Oct 26 2026 11:49 AM): calendar-only More → pages (R82_CAL_PAGES) carry the calendar wording, names exactly as the calendar.
for _rn, _rw in getattr(C, "R82_CAL_PAGES", {}).items():   # content file: event -> calendar wording its More → page must carry
    _tf = C.EVENT_PAGE[_rn][0]; _tp = Path(_os.environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO)) / "pages" / _tf
    L.ok("R82", f'{lc.BASE}{_tf}" style="color:#3A6B1A;">More →</a>' in page and _tp.exists() and _rw in _tp.read_text(encoding="utf-8"),
         f"{_rn}: More → {_tf} with the calendar wording")
# R83 (Steven Oct 26 2026 12:19 PM): the issue's Community Story -- section teaser + More → the story page, the story page carries
# exactly one approved credit line after </article> (R52 exception), and no test/review/dry-run wording anywhere in the preview.
if getattr(C, "STORY", None):
    _rp = Path(_os.environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO)); _sj = json.load(open(_rp / C.STORY["json"], encoding="utf-8"))
    _cs = lc._section(page, "Community Stories"); _spf = _rp / "pages" / _sj["live_page_planned"]
    L.ok("R83", _sj["title"].replace("’", "&#x27;") in _cs or _html.escape(_sj["title"]) in _cs or _sj["title"] in _cs, "Community Stories shows the story title")
    L.ok("R83", f'{lc.BASE}{_sj["live_page_planned"]}"' in _cs and (_rp / "pages" / C.STORY["listen"]).exists(), "story More → live page; listen page exists")
    _sp = _spf.read_text(encoding="utf-8") if _spf.exists() else ""
    try: _sr83.assert_no_link_name(_sp, _spf.name, credit_line=_sj.get("credit_line")); _okc = bool(_sp)
    except SystemExit: _okc = False
    L.ok("R83", _okc, f"story page credit line: {_sj.get('credit_line')}")
    # R84 (Steven Oct 26 2026 12:52 PM): the Link cover photo sits at the top of the story page (and its Listen page) like Joe Clay's;
    # absolute palmhillnews URL, alt text, file in public/ (resolves live only after a deploy). Main page: text teaser only, as Oct 25.
    _ph = _sj.get("photo")
    if _ph:
        _pf = _rp / "public" / _ph["src"].split("vercel.app/", 1)[-1]
        _fig = f'<figure><img src="{_ph["src"]}" width="{_ph["w"]}" height="{_ph["h"]}" alt="{_html.escape(_ph["alt"])}">'
        _lp = (_rp / "pages" / C.STORY["listen"]).read_text(encoding="utf-8") if (_rp / "pages" / C.STORY["listen"]).exists() else ""
        L.ok("R84", _ph["src"].startswith("https://palmhillnews.vercel.app/assets/") and _pf.exists() and _ph["alt"].strip() != "", f"cover photo {_pf.name} in public/, absolute URL, alt text")
        L.ok("R84", _fig in _sp.split("<article>")[0], "cover photo at the top of the story page")
        L.ok("R84", _fig in _lp.split("<article>")[0], "cover photo at the top of the Listen page")
# R85 (Steven Oct 27 2026 12:25 AM): from TEL_FROM, no bare phone number in the NL (preview = SEND body) or the Nov 1+ pages it links;
# every tel: href digits = the visible digits (+1 added). 7-digit numbers would need Steven's OK for the area code.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts")); import tel_links as _tel
if _tel.applies(C.ISSUE):
    _rp85 = Path(_os.environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO))
    _b10, _b7 = _tel.find_bare(page)
    L.ok("R85", not _b10 and not _b7 and not _tel.tel_mismatches(page), f"NL (preview/SEND): every phone a tel: link with matching digits {_b10 + _b7 + _tel.tel_mismatches(page)}")
    _pg85 = sorted({u for u in re.findall(r'palmhillnews\.vercel\.app/pages/([^"?#]+\.html)', page) if _tel.dated_from(u)} | ({C.STORY["listen"]} if getattr(C, "STORY", None) else set()))
    _bad85 = []
    for _u in _pg85:
        _f = _rp85 / "pages" / _u
        if _f.exists():
            _t = _f.read_text(encoding="utf-8"); _x = _tel.find_bare(_t)
            if _x[0] or _x[1] or _tel.tel_mismatches(_t): _bad85.append((_u, _x, _tel.tel_mismatches(_t)))
    L.ok("R85", not _bad85, f"{len(_pg85)} Nov 1+ linked pages: no bare phone, tel: digits match {_bad85}")
# R86 (Steven Oct 27 2026 1:25 PM): Tony's Palm Hill calendar is the single source of truth for meeting dates/times; the
# conflict report (scripts/meeting_conflict_report.py) is the guard. It must exist, run, and list every MTG_OVERRIDE as a
# CONFLICT-OVERRIDDEN-BY-RULE item (the R62/R62b/R62c overrides stay until Steven releases them). Report only; output unchanged.
_mcr = Path(__file__).resolve().parents[2] / "scripts/meeting_conflict_report.py"
if C.ISSUE < "2026-11-01": pass   # R86 starts with the Nov 1 issue; Oct 25 stays as approved
elif _mcr.exists():
    import tempfile as _tf86, importlib.util as _iu86
    _sp86 = _iu86.spec_from_file_location("mcr86", _mcr); _m86 = _iu86.module_from_spec(_sp86); _sp86.loader.exec_module(_m86)
    try:
        with _tf86.TemporaryDirectory() as _d86:
            _R86, _b86 = _m86.main(["--issue", C.ISSUE, "--out", _d86]); _ok86 = True
            _tn86 = Path(str(_b86) + "-tony.txt"); _subj86 = _tn86.read_text(encoding="utf-8").split("\n", 1)[0] if _tn86.exists() else None
    except SystemExit as _e86: _R86, _ok86 = None, str(_e86)
    if _ok86 is True:   # Steven Oct 27 2026 2:27 PM: every conflict email to Tony has exactly this subject
        L.ok("R86", _m86.TONY_SUBJECT == "Calendar Conflicts Report" and _subj86 == "Subject: " + _m86.TONY_SUBJECT,
             f"Tony file subject line is exactly 'Subject: Calendar Conflicts Report' ({_subj86!r})")
    L.ok("R86", _ok86 is True, f"meeting conflict report runs for {C.ISSUE} {'' if _ok86 is True else _ok86}")
    if _R86:
        # Oct 27 2026 2:24 PM: Steven released R62/R62b/R62c for Nov 1 (calendar only; Tony agreed Oct 26). No row may say
        # CONFLICT-OVERRIDDEN-BY-RULE; Finance and P&E stay listed, as agenda-differs only.
        _ovr86 = [r["name"] for r in _R86["rows"] if any(d[0] == "CONFLICT-OVERRIDDEN-BY-RULE" for d in r["diffs"])]
        L.ok("R86", not _ovr86 and not _R86["overrides"], f"no CONFLICT-OVERRIDDEN-BY-RULE rows (calendar only) {_ovr86 or ''}")
        # Oct 27 2026 2:43 PM: P&E "a.m." is a known typo (reference only); RPM day differences on calendar dates are reference only.
        _cal86 = [r for r in _R86["rows"] if r["cal_date"]]
        _fin86 = [d[0] for r in _cal86 if "Finance" in r["name"] for d in r["diffs"]]
        _pe86 = [r for r in _cal86 if "Planning" in r["name"]]
        L.ok("R86", _fin86 and all(k.startswith("Agenda:") for k in _fin86), f"Finance listed as agenda-differs only {_fin86}")
        L.ok("R86", _pe86 and all(not r["diffs"] and any(k == "Agenda: known typo" for k, _ in r["refs"]) for r in _pe86),
             "P&E a.m. wording is a known typo, not counted")
        _rpm86 = [r["name"] for r in _cal86 if any(k.startswith("RPM") for k, _ in r["diffs"])]
        L.ok("R86", not _rpm86 and any(not r["cal_date"] for r in _R86["rows"]), f"RPM differences on calendar dates are reference only {_rpm86}; RPM-only meetings stay items")
else:
    L.ok("R86", False, "scripts/meeting_conflict_report.py missing")
# R87 (Steven Oct 27 2026 2:24 PM, Tony's option c): from Nov 1 (MEETINGS_ALL_IN_WINDOW) the Meetings rows are every calendar
# committee/board meeting in the window, none missing, none twice; Finance prints the calendar's Mon Nov 16 10:00 AM; no overrides.
if C.ISSUE >= "2026-11-01" and getattr(C, "MEETINGS_ALL_IN_WINDOW", False):
    _cal87 = json.load(open(audit["calendar_file"])) if Path(str(audit.get("calendar_file", ""))).exists() else None
    if _cal87 is None: L.ok("R87", False, f"calendar snapshot {audit.get('calendar_file')} missing")
    else:

        import issue_ctx as _ix87; _w87 = _ix87.windows(C.ISSUE)["MEETINGS"]
        _re87 = re.compile(r"\bcommittee\b|\bboard of directors\b", re.I)
        _exp87 = sorted({(e["date"], e["start"], e["name"].lower().replace("&", "and").replace("building ", "buildings ").replace(" meeting", "").strip())
                         for e in _cal87["events"] if e.get("category") == "Meetings" and _re87.search(e["name"]) and e.get("status") == "CONFIRMED"
                         and e["name"] != "Private Event" and "test" not in e["name"].lower() and _w87[0] <= e["date"] <= _w87[1]})
        _got87 = [(d, n.lower().replace(" meeting", "").strip()) for d, n in audit["meetings"]]
        _miss87 = [x for x in _exp87 if (x[0], x[2]) not in _got87]
        L.ok("R87", not _miss87 and len(_got87) == len(set(_got87)) and len(_got87) == len(_exp87),
             f"Meetings rows = every calendar meeting {_w87[0]}..{_w87[1]} ({len(_got87)} rows, {len(_exp87)} on calendar) missing {_miss87}")
        # Finance row = calendar Mon Nov 16 10:00 AM: content-file MEETING_ROW_CHECKS (rule R87) above (R71b: no issue text in core)
        L.ok("R87", not getattr(C, "MTG_OVERRIDE", {}) and not getattr(C, "MTG_OVERRIDE_SOURCE", {}), "no MTG_OVERRIDE keys in the Nov 1 content")
_vis = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->|<[^>]+>", " ", page)
L.ok("R83", not re.search(r"\b(test|review|dry[ -]?run)\b", _vis, re.I), "no test / review / dry run text in the preview")
L2 = lc.Locks(); lc.check_title_months(L2, {"newsletter": page})
# L27b/c webmaster-source counts: superseded by R47 (style_rules.assert_webmaster_more), enforced inside the builder
res = L.results + L2.results
from explain import explain as _why  # R75: plain-English why/fix line under each FAIL (counts unchanged)
for r in res:
    print(r)
    if r[1] == "FAIL": print(_why(r[0]))
fails = [r for r in res if r[1] == "FAIL"]
print(f"run_checks {C.ISSUE}: {len(res) - len(fails)} PASS, {len(fails)} FAIL")
sys.exit(1 if fails else 0)
