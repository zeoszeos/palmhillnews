"""Oct 25, 2026 locked checks (A1/A2/A3, Steven-approved Oct 24 2026 2:26 PM, Claude review). STYLE-RULES R64.

Fail-closed: any FAIL -> exit 1. Expectations come from the build audit (calendar data) and the locked content lists in
locked_checks.py -- never scraped from the page being checked (old L11 scrape removed). The Oct 11-era layout locks
(L03/L05-L08/L12/L14-L17/L26/L27b-c) were superseded by later STYLE-RULES (R18/R45/R59-R63...) and the builder's own inline
guards; they are rewritten here against the current markup instead of being silently skipped.
Usage: python3 builder/core/run_checks.py [issue.html] with PHNEWS_ISSUE set (default WORK/PHNEWS-<issue>-preview.html). build_core.py runs it.
"""
import html
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
titles = lambda sec: [_html.unescape(t) for t in re.findall(T, sec)]   # R95: compare titles as text (an apostrophe is &#x27; in the HTML)
text = lambda h: " ".join(re.sub(r"<[^>]+>", " ", h).split())

# L01/L02 masthead
L.ok("L01", re.search(r'header-volno"[^>]*>' + re.escape(C.VOLNO) + r'</span>', page) is not None, f"{C.VOLNO} in the address bar")
L.ok("L02", page.count(f">Sunday, {C.ISSUE_LONG}</span>") == 1 and page.count("masthead-palm-hd-320x334-v1.png") == 2, f"issue date Sunday, {C.ISSUE_LONG}; HD palm x2")
# L03 section order (Oct 25 approved order)
ORDER = ["Committee &amp; Board Meeting Schedules", "Committee Chair Reports", "Events - This Week", "Recurring Meetings &amp; Events",
         "Community Notices", "Monthly Shareholders Report", "Weekly Manager Update", "Events - Upcoming", "Community Stories",
         "From the Board President", "Did You Know?", "Residents Reference Guide"]
got = [t for _, t in lc._headings(page)]
_NWS = getattr(C, "NEXT_WEEK_SECTION", False)   # R92 (Steven Oct 30 2026 11:40 AM)
UPH = "Events - Next Week" if _NWS else "Events - Upcoming"
if _NWS:
    ORDER.remove("Events - Upcoming"); ORDER.insert(ORDER.index("Events - This Week") + 1, "Events - Next Week")
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
tw = lc._section(page, "Events - This Week"); up = lc._section(page, UPH)
L.ok("L07", [norm(x) for x in titles(tw)] == [norm(n) for _, n in audit["this_week"]] and f">{_W('THIS_WEEK')}<" in tw, f"This Week rows {titles(tw)}")
L.ok("L08", [norm(x) for x in titles(up)] == [norm(n) for _, n in audit["upcoming"]] and f">{_W('NEXT_WEEK') if _NWS else C.UPCOMING_LABEL_EXPECTED}<" in up, f"{UPH} rows {titles(up)}")
if _NWS:   # R92 guard: Next Week directly under This Week, header range = issue day +7..+13, every row inside it, no Upcoming section
    _nw = C.WINDOWS["NEXT_WEEK"]
    L.ok("R92", got.index("Events - Next Week") == got.index("Events - This Week") + 1 and "Events - Upcoming" not in got
         and all(_nw[0] <= d <= _nw[1] for d, _ in audit["upcoming"]) and f">{_W('NEXT_WEEK')}<" in up,
         f"Next Week directly under This Week, {_W('NEXT_WEEK')}, {len(audit['upcoming'])} rows in window")
# A3: one shared treat-as-recurring list
b25 = (H / "build_core.py").read_text(encoding="utf-8")
_as = lambda src: set(eval(re.search(r"^AS_RECURRING = (\{[^}]*\})", src, re.M).group(1)))
L.ok("L09a", set(lc.TREAT_AS_RECURRING) == _as(b25) == _as((H / "recurring.py").read_text(encoding="utf-8")), "TREAT_AS_RECURRING == builder/recurring AS_RECURRING")
for n in lc.TREAT_AS_RECURRING:
    L.ok("L09", n not in tw and n not in up, f'This Week/Upcoming exclude "{n}"')
# L11 Community Notices (locked list, not scraped)
cn = lc._section(page, "Community Notices")
L.ok("L11", titles(cn) == lc.NOTICES_EXPECTED, f"Notices rows {titles(cn)}")
# R93 (Steven Oct 30 2026 11:58 AM; approved 12:13 PM): notice titles carry no dates; each notice has a date line under its title
# (source wording, dates found in its source page) or an approved No date. Teaser line count = visual guard R18 (390/660px).
if getattr(C, "NOTICE_DATES", False):
    _MON = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?"
    _DT = re.compile(_MON + r"\s+\d{1,2}(st|nd|rd|th)?\b|\b\d{1,2}(st|nd|rd|th)\b|\b\d{1,2}/\d{1,2}\b|\b(Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day\b", re.I)
    _TOK = re.compile(_MON + r"\s+\d{1,2}(st|nd|rd|th)?(,\s*\d{4})?|\b\d{1,2}(:\d\d)?\s*(AM|PM)\b|month of \w+|\d+ week before [A-Za-z ]+?(?= ·|$)|before you depart", re.I)
    _items = [(t, h) for t, _x, _s, h in C.NOTICES if t in titles(cn)]
    for _t in titles(cn):
        L.ok("R93", not _DT.search(_t) and " — " not in _t, f"notice title has no date: {_t}")
        _dl = C.NOTICE_DATE_LINE.get(_t)
        L.ok("R93", bool(_dl) != (_t in C.NOTICE_NO_DATE), f"{_t}: date line or approved No date (not both)")
        if _dl:
            L.ok("R93", f'ph-notice-date" style="font-size:14px;color:#666666;text-align:left;padding-top:2px;">{_html.escape(_dl)}</div>' in cn,
                 f"{_t}: date line directly under the title")
            _h = dict(_items).get(_t); _sp = Path(_os.environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO)) / "pages" / _h.rsplit("/", 1)[1] if _h else None
            _st = " ".join(re.sub(r"<[^>]+>", " ", _html.unescape(_sp.read_text(encoding="utf-8"))).split()).lower() if _sp and _sp.exists() else ""
            _miss = [m.group(0) for m in _TOK.finditer(_dl) if " ".join(m.group(0).split()).lower() not in _st]
            L.ok("R93", bool(_st) and not _miss and all(": " in seg for seg in _dl.split(" · ") if _TOK.search(seg)) and ": " in _dl.split(" · ")[0], f"{_t}: date line words in source page {_miss}")
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
    for _sn in ("Events - This Week", UPH):
        _sx = lc._section(page, _sn)
        if _NWS:   # R92b: link is the FIRST row of the section, under the header/date range
            _t = _sx.find('style="margin:4px 0 12px 0;">'); _fr = _sx[_t:_sx.find("</tr>", _t)]
            L.ok("R92b", f'href="{lc.BASE}{_aef}"' in _fr and f">{C.ALL_EVENTS_LINK_TEXT}</a>" in _fr and _sx.count(_aef) == 1,
                 f"{_sn}: '{C.ALL_EVENTS_LINK_TEXT}' is the top row (once)")
        else:
            L.ok("R79", _ael in _sx, f"{_sn}: link '{C.ALL_EVENTS_LINK_TEXT}' -> {_aef}")
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
    _inbody = _rn in {n for _, n in audit["this_week"] + audit["upcoming"]}   # R92: events after Next Week live on All Events only
    L.ok("R82", (not _inbody or f'{lc.BASE}{_tf}" style="color:#3A6B1A;">More →</a>' in page) and _tp.exists() and _rw in _tp.read_text(encoding="utf-8"),
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
    _pg85 = sorted({u for u in re.findall(r'palmhillnews\.vercel\.app/pages/([^"?#]+\.html)', page) if _tel.dated_from(u) or u in {w[0] for w in getattr(C, "WM_COPIES", [])} | {q["page"] for q in getattr(C, "NOTICE_PAGES", [])}} | ({C.STORY["listen"]} if getattr(C, "STORY", None) else set()))
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
            _th86 = Path(str(_b86) + "-tony.html"); _html86 = _th86.read_text(encoding="utf-8") if _th86.exists() else ""; _ttx86 = _tn86.read_text(encoding="utf-8") if _tn86.exists() else ""
    except SystemExit as _e86: _R86, _ok86 = None, str(_e86)
    if _ok86 is True:   # Steven Oct 27 2026 2:27 PM: every conflict email to Tony has exactly this subject
        L.ok("R86", _m86.TONY_SUBJECT == "Calendar Conflicts Report" and _subj86 == "Subject: " + _m86.TONY_SUBJECT,
             f"Tony file subject line is exactly 'Subject: Calendar Conflicts Report' ({_subj86!r})")
    if _ok86 is True:   # Steven Oct 27 2026 3:16/3:17 PM: Tony email is one HTML table; RPM values are a timely live read
        import re as _re86
        L.ok("R86", len(_re86.findall(r"<table\b", _html86)) == 1 and "<th" in _html86 and f"<title>{_m86.TONY_SUBJECT}</title>" in _html86 and "<style" not in _html86,
             "Tony HTML email exists, has exactly one table with a header row, inline CSS only, title = exact subject")
        # Steven Oct 27 2026 11:40 PM: simplified Tony table wording; a plain "Mismatch" reason column; Palm Hill and RPM recurring flags shown On/Off
        L.ok("R86", all(f"<th" in _html86 and c in _html86 for c in ("Mismatch", "Palm Hill recurring", "RPM recurring")) and "Mismatch: Mismatch" not in _ttx86 and ("On" in _ttx86 and "Off" in _ttx86),
             "Tony table has a Mismatch column plus Palm Hill recurring and RPM recurring columns showing On/Off")
        L.ok("R86", bool(_R86.get("rpm_fetched")) and "Oct 16" not in _R86["rpm_fetched"] and _ttx86 and "Oct 16" not in _ttx86,
             f"RPM values carry a live-read stamp ({_R86.get('rpm_fetched')}); no Oct 16 notes in the Tony email")
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
        _re87 = re.compile(r"\bcommittee\b|\bboard of directors\b" + ("|" + C.MEETINGS_NAME_RE_EXTRA if getattr(C, "MEETINGS_NAME_RE_EXTRA", None) else ""), re.I)  # R87b
        _exp87 = sorted({(e["date"], e["start"], e["name"].lower().replace("&", "and").replace("building ", "buildings ").replace(" meeting", "").strip())
                         for e in _cal87["events"] if e.get("category") == "Meetings" and _re87.search(e["name"]) and e.get("status") == "CONFIRMED"
                         and e["name"] != "Private Event" and "test" not in e["name"].lower() and _w87[0] <= e["date"] <= _w87[1]})
        _got87 = [(d, n.lower().replace(" meeting", "").strip()) for d, n in audit["meetings"]]
        _miss87 = [x for x in _exp87 if (x[0], x[2]) not in _got87]
        L.ok("R87", not _miss87 and len(_got87) == len(set(_got87)) and len(_got87) == len(_exp87),
             f"Meetings rows = every calendar meeting {_w87[0]}..{_w87[1]} ({len(_got87)} rows, {len(_exp87)} on calendar) missing {_miss87}")
        # Finance row = calendar Mon Nov 16 10:00 AM: content-file MEETING_ROW_CHECKS (rule R87) above (R71b: no issue text in core)
        L.ok("R87", not getattr(C, "MTG_OVERRIDE", {}) and not getattr(C, "MTG_OVERRIDE_SOURCE", {}), "no MTG_OVERRIDE keys in the Nov 1 content")
# R88 (Steven Oct 29 2026 11:11 AM): new Did You Know items from the content file's DYK_NEW_JSON are the top R57 blocks, in order,
# title + verbatim teaser + More -> to the final page, which exists with one Listen and no retyped phone number; archive row present.
if getattr(C, "DYK_NEW_JSON", None):
    _R = Path(__file__).resolve().parents[2]; _dn = json.load(open(_R / C.DYK_NEW_JSON, encoding="utf-8"))
    _bl = re.findall(r'class="ph-dyk-title"[^>]*>([^<]*)</div><div[^>]*>([^<]*)</div><div class="ph-dyk-more"[^>]*><a href="([^"]+)"', page)
    for _n, _it in enumerate(_dn["items"]):
        _pg = _dn["page_prefix"] + _it["preview_page"]; _pf = _R / "pages" / _pg
        _ok = (len(_bl) > _n and _html.unescape(_bl[_n][0]) == _it["title_display"] and _html.unescape(_bl[_n][1]) == _it["teaser"]
               and _bl[_n][2].endswith("/pages/" + _pg) and _sr83.dyk_summary_ok(_it["teaser"], _it["paragraphs"]))
        _pt = _pf.read_text(encoding="utf-8") if _pf.exists() else ""
        _ok = _ok and _pt.count('class="ph-listen"') == 1 and not re.search(r"\d{3}-\d{3}-\d{4}", text(_pt.split("<main>")[1].split("</main>")[0]) if "<main>" in _pt else "x")
        _ai = (_R / "archive/archive-items.json").read_text(encoding="utf-8")
        L.ok("R88", _ok and f'"page": "{_pg}"' in _ai, f"new Did You Know {_it['id']} is block {_n + 1} (title, verbatim teaser, More -> {_pg}), page has Listen, archive row")
# R89 (Steven Oct 29 2026 11:33 AM): with DYK_CARRY_PREVIOUS=False the main page Did You Know is exactly this issue's new items,
# then one Did You Know Archives line; the previous issue's items are not on the page but keep their pages and archive rows.
if not getattr(C, "DYK_CARRY_PREVIOUS", True):
    _R = Path(__file__).resolve().parents[2]
    _dn = json.load(open(_R / C.DYK_NEW_JSON, encoding="utf-8")) if getattr(C, "DYK_NEW_JSON", None) else {"items": []}
    _dn = {"items": [{"title_display": r["title"]} for r in (getattr(C, "DYK_REPRISE", None) or [])] + _dn["items"]}
    _a89 = page.find(">Did You Know?</span>"); _seg89 = page[_a89:page.find("Did You Know Archives →", _a89)]
    _t89 = [_html.unescape(t) for t in re.findall(r'class="ph-dyk-title"[^>]*>([^<]*)</div>', _seg89)]
    L.ok("R89", _a89 > 0 and _t89 == [i["title_display"] for i in _dn["items"]] and page.count("Did You Know Archives →") == 1,
         f"main page Did You Know = only this issue's new items {_t89}, one Did You Know Archives line")
    _ai89 = json.loads((_R / "archive/archive-items.json").read_text(encoding="utf-8"))
    _prev = [r for r in _ai89["sections"]["did-you-know"]["items"] if r.get("date") == C.DYK_ROW_DATE]
    _arch = (_R / "pages/archive/did-you-know.html").read_text(encoding="utf-8")
    _gone = [r["page"] for r in _prev if not (_R / "pages" / r["page"]).exists() or r["page"] not in _arch or ("/pages/" + r["page"]) in page]
    L.ok("R89", bool(_prev) and not _gone, f"previous issue's {len(_prev)} Did You Know items keep page + archive row, off the main page {_gone}")
# R90 (Steven Oct 29 2026 12:50 PM): a Did You Know item built from an email/message (source_line in DYK_NEW_JSON) shows that
# source line, plain (no link), outside the content card right above the Did You Know Archives line; byline stays last in the card (R33).
if getattr(C, "DYK_NEW_JSON", None):
    _R = Path(__file__).resolve().parents[2]; _dn = json.load(open(_R / C.DYK_NEW_JSON, encoding="utf-8"))
    for _it in _dn["items"]:
        if not _it.get("source_line"): continue
        _pt = (_R / "pages" / (_dn["page_prefix"] + _it["preview_page"])).read_text(encoding="utf-8")
        _m = re.search(r'<div class="content-card">([\s\S]*?)</div>\n<p class="source dyk-email-source"[^>]*>([^<]*)</p>\n<p class="source"[^>]*><a [^>]*>Did You Know Archives →', _pt)
        _ok = bool(_m) and _html.unescape(_m.group(2)) == _it["source_line"] and _m.group(1).endswith(f'<p class="dyk-byline">{_html.escape(_it["byline"])}</p>') if _it.get("byline") else bool(_m)
        L.ok("R90", _ok and _pt.count("dyk-email-source") == 1, f"{_it['id']} page cites its source email: {_it['source_line']!r}")
# R91 (Steven Oct 29 2026 7:33 PM): DYK_REPRISE items are the top blocks (title, teaser = text printed then, More -> existing live
# page, no new archive row); parked pages (DYK_PARKED_PAGES) are not in the repo tree, the issue, or any archive row/page.
if getattr(C, "DYK_REPRISE", None) or getattr(C, "DYK_PARKED_PAGES", None):
    _R = Path(__file__).resolve().parents[2]
    _bl91 = re.findall(r'class="ph-dyk-title"[^>]*>([^<]*)</div><div[^>]*>([^<]*)</div><div class="ph-dyk-more"[^>]*><a href="([^"]+)"', page)
    for _n, _it in enumerate(getattr(C, "DYK_REPRISE", None) or []):
        _ok = len(_bl91) > _n and _html.unescape(_bl91[_n][0]) == _it["title"] and _html.unescape(getattr(C, _it["text_html"])).startswith(_html.unescape(_bl91[_n][1])) and _html.unescape(_bl91[_n][1])[-1:] in ".?!" and _bl91[_n][2] == _it["href"]
        L.ok("R91", _ok and (_R / "pages" / _it["href"].split("/pages/", 1)[1]).exists(), f"Did You Know block {_n + 1} = {_it['title']!r} re-run as printed, More -> {_it['href']}")
    _arch91 = [(_R / "archive/archive-items.json").read_text(encoding="utf-8"), (_R / "pages/archive/did-you-know.html").read_text(encoding="utf-8"), (_R / "pages/archive/archive-index.json").read_text(encoding="utf-8")]
    for _pp in getattr(C, "DYK_PARKED_PAGES", None) or []:
        L.ok("R91", not (_R / "pages" / _pp).exists() and _pp not in page and not any(_pp in t for t in _arch91), f"parked {_pp}: not in the tree, issue or archive")
# R94 (Steven Oct 30 2026 4:02 PM): the NL output (-> SEND / email) is script-free; only the review/live preview copy gets the
# in-place Listen block (checked after sync by scripts/check_preview_send_stamp.py).
import page_listen as _pl94
if _pl94.v2_for(C.ISSUE):
    L.ok("R94", "<script" not in page.lower(), "NL output (preview -> SEND/email) has no <script>")
    _sd94 = ROOT / f"PHNEWS-{C.ISSUE}-SEND.html"
    if _sd94.exists(): L.ok("R94", "<script" not in _sd94.read_text(encoding="utf-8").lower(), "SEND copy has no <script>")
# R97 (Steven Oct 30 2026 10:11 PM): SEND/email copy has no pure-white table/tr/td backgrounds (Gmail iOS dark mode -> black
# bands with dark text); they carry EMAIL_TINT on the row AND each cell (style + bgcolor), and the head says color-scheme light only.
import email_dark_mode as _dm97
if _dm97.applies(C.ISSUE):
    _sd97 = ROOT / f"PHNEWS-{C.ISSUE}-SEND.html"
    if _sd97.exists():
        _s97 = _sd97.read_text(encoding="utf-8")
        L.ok("R97", not _dm97.find_white(_s97), f"SEND: no pure-white row/cell/table backgrounds {_dm97.find_white(_s97)[:3]}")
        L.ok("R97", _dm97.head_ok(_s97), "SEND head: color-scheme / supported-color-schemes light only + :root{color-scheme:light only}")
# R98 (Steven Oct 30 2026 10:39 PM): no border-left accent on chair-report rows or Did You Know items (preview + SEND), from Nov 1.
if C.ISSUE >= "2026-11-01":
    _p98 = [page] + ([(ROOT / f"PHNEWS-{C.ISSUE}-SEND.html").read_text(encoding="utf-8")] if (ROOT / f"PHNEWS-{C.ISSUE}-SEND.html").exists() else [])
    L.ok("R98", not any(re.search(r"<td[^>]*border-left:\s*\d+px", x) for x in _p98), "no border-left accent bar on table cells (chair reports, Did You Know)")
# R99/R101: optional TOP_BANNERS (or TOP_BANNER) each exactly once, in order, all above the first section (preview + SEND);
# compact size (R101: heading 17px, padding 8px 12px); none otherwise.
_tbs99 = list(getattr(C, "TOP_BANNERS", None) or ([C.TOP_BANNER] if getattr(C, "TOP_BANNER", None) else []))
for _n99, _x99 in [("preview", page)] + ([("SEND", (ROOT / f"PHNEWS-{C.ISSUE}-SEND.html").read_text(encoding="utf-8"))] if (ROOT / f"PHNEWS-{C.ISSUE}-SEND.html").exists() else []):
    _c99 = _x99.count('class="ph-top-banner"')
    if not _tbs99: L.ok("R99", _c99 == 0, f"{_n99}: no top banner (issue defines none)"); continue
    _f99 = min([i for i in (_x99.find('<div class="canonical-section">'), _x99.find('<div class="section04">')) if i > 0] or [len(_x99)])
    _ps99 = [m.start() for m in re.finditer('class="ph-top-banner"', _x99)]
    L.ok("R99", _c99 == len(_tbs99) and all(0 < i < _f99 for i in _ps99), f"{_n99}: exactly {len(_tbs99)} top banner(s), above the first section")
    _last = -1
    for _tb in _tbs99:
        _bd = html.escape(_tb["body"]); _hd = html.escape(_tb["heading"].split(" ", 1)[1])
        _ih = _x99.find(_hd)
        L.ok("R99", _x99.count(_bd) == 1 and _x99.count(_hd) == 1 and _ih > _last, f"{_n99}: banner '{_hd}' verbatim once, in order")
        _last = _ih
    L.ok("R99", _x99.count("&#9200;") == 2, f"{_n99}: two clock icons")
    _seg = _x99[_ps99[0]:_f99] if _ps99 else ""
    L.ok("R101", "font:700 20px" not in _seg and "padding:12px 14px" not in _seg and _seg.count("font:700 17px/22px") == len(_tbs99), f"{_n99}: banners compact (17px heading, 8px 12px padding)")
# R102 (Steven Oct 31 2026 7:33 PM): each REQUIRED_TEL number appears as a tap-to-call link in preview, SEND and its copy page.
for _lb101, _num101, _pg101 in getattr(C, "REQUIRED_TEL", []):
    _h101 = 'href="tel:+1' + re.sub(r"\D", "", _num101) + '"'
    _srcs101 = [("preview", page)] + ([("SEND", (ROOT / f"PHNEWS-{C.ISSUE}-SEND.html").read_text(encoding="utf-8"))] if (ROOT / f"PHNEWS-{C.ISSUE}-SEND.html").exists() else [])
    _pp101 = Path(__import__("os").environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO)) / "pages" / _pg101
    _srcs101.append(("page " + _pg101, _pp101.read_text(encoding="utf-8") if _pp101.exists() else ""))
    for _n101, _x101 in _srcs101:
        L.ok("R102", _h101 in _x101 and _num101 in _x101, f"{_n101}: {_lb101} phone {_num101} is a tel: link")
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
