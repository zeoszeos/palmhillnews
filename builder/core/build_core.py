"""PHNEWS shared issue builder (coding batch 4, Steven Oct 24 2026 10:00 PM "We have time so let's do it correctly and just do it!";
STYLE-RULES R69 + R71). ONE builder for every issue from Oct 25 on: all logic and R-rule guards live here; each issue's own data
(date, Vol./No., story, dropped notices, per-issue flags, locked-check overrides) lives in builder/issues/<YYYY-MM-DD>.py.
Merged from builder/oct25/build_oct25.py and builder/nov1/build_nov1.py (which were clones of build_oct18.py). Box-side, draft only;
sends/publishes nothing. Run:  python3 builder/build_issue.py --issue <date>   (PHNEWS_DRYRUN=1 for a workspace dry run)
Input: ROOT/source/ (Oct 11 as-sent shell + Oct 18 seed), ROOT/data/cal-*.json (calendar = source of truth), the carried editorial
       content below (each item names its source), and the issue's content file.
Output: ROOT/PHNEWS-<issue>-preview.html, ROOT/local-<SHORT>/ review copy, archive rows/pages in REPO.
"""
import json, os, re, sys, glob, time
_R49_T0 = time.time() - 1  # STYLE-RULES R49: pages written by this run get the Listen-coverage check at the end
from datetime import date, datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo
HERE = Path(__file__).resolve().parent
# R69 (coding batch 3): builds start only from builder/build_issue.py --issue <date>, which picks this content file by date.
if os.environ.get("PHNEWS_ENTRY") != "build_issue" or not os.environ.get("PHNEWS_ISSUE"):
    raise SystemExit("R69: run  python3 builder/build_issue.py --issue <date>  (single builder entry point)")
sys.path.insert(0, str(HERE)); import issue_ctx as _ix   # R71: the issue's content file (builder/issues/<date>.py), data only
C = _ix.load(os.environ["PHNEWS_ISSUE"])
# Settings (coding batch 2, Steven Oct 24 2026 9:05 PM; STYLE-RULES R67): the two trees this builder uses, set in ONE place.
#   REPO = the PHNEWS git checkout (pages/, scripts/, archive/, builder/*/data); env PHNEWS_REPO, default = the content file's DEFAULT_REPO.
#   ROOT = the issue work tree (source/, data/cal-*.json, preview output, local-<SHORT>/); env PHNEWS_WORK, default = the content file's DEFAULT_WORK.
REPO = Path(os.environ.get("PHNEWS_REPO") or C.DEFAULT_REPO).resolve()
ROOT = Path(os.environ.get("PHNEWS_WORK") or C.DEFAULT_WORK).resolve()
PAGES = REPO / "pages"; SCRIPTS = str(REPO / "scripts")
sys.path.insert(0, SCRIPTS); import archive_items as _aj  # R68: the one archive-items.json editor
if not (REPO / "scripts/build_archive.js").exists(): raise SystemExit(f"R67: PHNEWS_REPO {REPO} is not a PHNEWS checkout")
SEED = ROOT / "source/PHNEWS-2026-10-18-seed-20261014.html"
ISSUE = C.ISSUE
# R21b (Steven, Oct 24 2026 9:05 PM, coding batch 1): calendar pull window comes from ISSUE (7 days before .. 60 days after), never hard-coded.
from datetime import date as _d0, timedelta as _td0
CAL_WINDOW = ((_d0.fromisoformat(ISSUE) - _td0(days=7)).isoformat(), (_d0.fromisoformat(ISSUE) + _td0(days=60)).isoformat())
# STYLE-RULES R21 (Steven, Oct 16 11:32 PM): re-pull the calendar right before every proof/publish build (prints the diff).
# PHNEWS_CAL_OFFLINE=1 only for re-renders that must reproduce an already-pulled snapshot.
if os.environ.get("PHNEWS_CAL_OFFLINE") != "1":
    sys.path.insert(0, SCRIPTS); import pull_calendar as _pc
    _pc.pull(str(ROOT / "data"), *CAL_WINDOW)
CALF = sorted(glob.glob(str(ROOT / "data/cal-*.json")))[-1]
OUTF = ROOT / f"PHNEWS-{ISSUE}-preview.html"
# R69 section windows, derived from ISSUE (builder/core/issue_ctx.windows): This Week 0-6, Upcoming 7-28 (~3 weeks, Oct 9 rule),
# Recurring 0-29, Meetings 0-30 days inclusive.
THIS_WEEK, UPCOMING, RECURRING, MEETINGS = (C.WINDOWS[k] for k in ("THIS_WEEK", "UPCOMING", "RECURRING", "MEETINGS"))
assert CAL_WINDOW == C.WINDOWS["CAL_WINDOW"], "R21b: calendar window must come from ISSUE"
BASE = "https://palmhillnews.vercel.app/pages/"; CAL = "https://www.palmhillcountryclub.net/calendar-1/"
ARCH = BASE + "archive/"
SPK = "https://palmhillnews.vercel.app/assets/images/phnews/2026-10-04/speaker-read-aloud-green-gold-512-v3.png"
G = "#3A6B1A"
MON3 = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
FULL = ("January","February","March","April","May","June","July","August","September","October","November","December")
assert all(globals()[k] == v for k, v in _ix.PRESEED.items()), "R71: core BASE/CAL/ARCH/G must equal issue_ctx.PRESEED"
# R71 (batch 5): this issue's content (builder/issues/<date>.py) -- events, meetings, notices, reports, DYK -- injected here, logic below.
_CONTENT = _ix.content_data(C); globals().update(_CONTENT)

cal = json.load(open(CALF)); events = cal["events"]
def pdate(iso): d = date.fromisoformat(iso); return f"{d:%A}, {MON3[d.month-1]} {d.day}, {d.year}"
def md(iso): d = date.fromisoformat(iso); return f"{MON3[d.month-1]} {d.day}"
def ptime(v):
    h, m = map(int, v.split(":")); return f"{(h-1)%12+1}:{m:02d} {'AM' if h<12 else 'PM'}"
def inw(e, w): return w[0] <= e["date"] <= w[1]
COMMITTEE_RE = re.compile(r"\bcommittee\b|\bboard of directors\b", re.I)
def is_cmte(e): return e.get("category") == "Meetings" and bool(COMMITTEE_RE.search(e["name"]))
def ok(e): return e.get("status") == "CONFIRMED" and e["name"] != "Private Event" and "test" not in e["name"].lower()
AS_RECURRING = {"Hand and Foot Cards", "Ukulele Group", "Ear Wax Removal", "I Got It", "Karaoke Obi-Time", "Writing Club"}
VENUE = {"Board Room South": "South Clubhouse Boardroom", "North Main Hall": "North Clubhouse", "South Main Hall": "South Clubhouse",
         "Off-Site": "Off-Site", "Small Meeting Room South": "Small Meeting Room South", "South Lawn and Patio": "South Lawn and Patio",
         "Golf Course": "Golf Course", "North Library": "North Library"}
CANON = {"Communications Committee": "Communications Committee Meeting", "Building & Grounds Committee": "Buildings and Grounds Committee Meeting",
         "Planning & Environmental Committee": "Planning and Environmental Committee Meeting"}

# ---------- meetings (committee/board only; one per committee; Calendar only) ----------
meetings, seen = [], set()
for e in sorted([e for e in events if ok(e) and is_cmte(e) and inw(e, MEETINGS)], key=lambda e: (e["date"], e["start"])):
    nm = CANON.get(e["name"], e["name"]); k = nm.lower().replace(" meeting", "")
    if k in seen and not globals().get("MEETINGS_ALL_IN_WINDOW", False): continue   # R87: Nov 1+ keeps every meeting in the window
    seen.add(k); meetings.append(dict(e, name=nm))
# L09: Tony "Meetings" category stays out of This Week/Upcoming, except MasterPlan Team (L25, Oct 10).
MEETINGS_CAT_ALLOWED = {"Palm Hill MasterPlan Team"}
def evsel(w):
    return sorted([e for e in events if ok(e) and inw(e, w) and not e.get("recurring") and not is_cmte(e)
                   and e["name"] not in AS_RECURRING and e.get("category") != "CLOSURE" and not e.get("allDay")
                   and (e.get("category") != "Meetings" or e["name"] in MEETINGS_CAT_ALLOWED)],
                  key=lambda e: (e["date"], e["start"]))
this_week, upcoming = evsel(THIS_WEEK), evsel(UPCOMING)

# Event text/links/More → pages (EVENT_DETAIL, EVENT_EXTRA_SRC, EVENT_LINK, PHONE_OK_PAGES, EVENT_PAGE, INFO_COVERED, TITLE) come
# from the issue content file (R71, batch 5); injected by _ix.content_data(C) above.
assert not any(re.search(r"\d{3}-\d{3}-\d{4}", v) for v in EVENT_DETAIL.values() if v), "phone rule: no phone numbers in issue summaries"
# R21: events whose summary already carries the whole calendar listing (checked by hand Oct 16) - no More → page needed
# STYLE-RULES R56 (Steven Oct 21 2026 10:44 AM, "middle path"): an event matched to a Webmaster/resident email notice shows calendar
# facts only; More → opens that notice page; no per-event page is generated or linked (already-published pages such as
# 2026-10-31-halloween-dance.html stay live, just unlinked). Source line stays Calendar + Webmaster (the notice).
MATCHED_NOTICE = dict(EVENT_EXTRA_SRC)
for _n, _u in MATCHED_NOTICE.items():
    EVENT_DETAIL.pop(_n, None); EVENT_PAGE.pop(_n, None); EVENT_LINK[_n] = ("More →", _u); INFO_COVERED.add(_n)

DRYRUN = os.environ.get("PHNEWS_DRYRUN") == "1"; DRYRUN_TODO = []
from explain import explain as _why  # R75
def _todo(msg):
    """Content guards stop a real build; with PHNEWS_DRYRUN=1 (and the issue's DRYRUN_OK) they are listed as TODOs instead (never publishes)."""
    if not (DRYRUN and C.DRYRUN_OK): raise SystemExit(msg)
    DRYRUN_TODO.append(msg); print("DRY-RUN TODO:", msg); print(_why(msg))  # R75 why/fix line
def bg(i): return "#EAF4E4" if i % 2 else "#FFFFFF"
def src_cal(extra=None):
    s = f'Source: <a href="{CAL}" style="color:{G};">Calendar</a>'
    if extra: s += f', <a href="{extra}" style="color:{G};">Webmaster</a>'
    return s
# Meetings extras/notes/overrides (MTG_EXTRA, MTG_NOTE, MTG_OVERRIDE, MTG_OVERRIDE_SOURCE) come from the issue content file (R71).
# R62c below checks every override cites its agenda/report page and wording (this replaced the Oct 25 Finance item-12 assert).
_R62B_HITS = []
for _k in MTG_OVERRIDE:
    if _k not in MTG_OVERRIDE_SOURCE: raise SystemExit(f"R62c: meeting override {_k!r} has no cited agenda/report source")
    _sp, _sw = MTG_OVERRIDE_SOURCE[_k]
    if not (REPO / _sp).exists() or _sw not in open(REPO / _sp, encoding="utf-8").read():
        raise SystemExit(f"R62c: meeting override {_k!r} source {_sp} missing or lacks {_sw!r}")
for _e in meetings:
    _o = MTG_OVERRIDE.get(CANON.get(_e["name"], _e["name"]))
    if _o:
        _cal_start = _e.get("start", "")
        _e.update(_o); _e.pop("note", None); _R62B_HITS.append(_e["name"])
        # R62c time rule: an override without a source time keeps the calendar time (and place), or none if the calendar has none
        if "start" not in _o and _e.get("start", "") != _cal_start:
            raise SystemExit(f"R62c: override {_e['name']!r} has no source time but its time changed from the calendar's {_cal_start!r}")
meetings = sorted(meetings + MTG_EXTRA, key=lambda e: (e["date"], e["start"]))
# R54 (Steven Oct 20 4:33 PM): no meeting listed twice -- one row per committee/board, the NEXT instance only. MTG_EXTRA rows
# (agenda/TBC additions) were appended after the calendar's one-per-committee pass, so Board Oct 28 (calendar) + Board Nov 18 (TBC) both showed.
def _mkey(e): return CANON.get(e["name"], e["name"]).lower().replace(" meeting", "").strip()
# STYLE-RULES R87 (Steven Oct 27 2026 2:24 PM; Tony's option (c), Oct 26): from Nov 1 (content flag MEETINGS_ALL_IN_WINDOW) every
# meeting in the Meetings window is listed, repeats and all; only an exact duplicate (same committee, date and time, e.g. a TBC
# MTG_EXTRA that the calendar now carries) is dropped, keeping the calendar row. Oct 25 keeps R54 (one row per committee).
_ALLW = globals().get("MEETINGS_ALL_IN_WINDOW", False)
_rkey = (lambda e: (_mkey(e), e["date"], e["start"])) if _ALLW else _mkey
_seen = set(); _dropped = []
for _e in list(meetings):
    if _rkey(_e) in _seen: meetings.remove(_e); _dropped.append((_e["date"], _e["name"]))
    else: _seen.add(_rkey(_e))
print("R87 exact-duplicate meetings dropped:" if _ALLW else "R54 meetings dropped (already listed):", _dropped)
assert len({_rkey(e) for e in meetings}) == len(meetings), "R54/R87: a committee/board meeting is listed twice"
# RESTORED from build_oct11_final.py MEETING_DETAIL (Oct 9-11 rules L27): Webmaster agenda/Zoom notices drive the Oct 11 layout.
import urllib.parse as _up
def _nopwd(u):
    pr = _up.urlsplit(u); q = [(k, v) for k, v in _up.parse_qsl(pr.query) if k.lower() != "pwd"]
    return _up.urlunsplit((pr.scheme, pr.netloc, pr.path, _up.urlencode(q), ""))
MEETING_DETAIL = {(n["date"], n["name"]): n for n in json.load(open(ROOT / "data/webmaster-meeting-notices.json"))["notices"]}
def mtg_rows():
    out = []
    for i, e in enumerate(meetings):
        note = e.get("note") or MTG_NOTE.get((e["date"], e["name"]))
        nt = f' <span style="font-style:italic;white-space:nowrap;">{escape(note)}</span>' if note else ""
        srcx = e.get("src_html") or src_cal()  # Steven rule Oct 16: calendar entries -> Source: Calendar; agenda-only -> Webmaster notice page
        d = MEETING_DETAIL.get((e["date"], e["name"]))
        if d:  # Oct 11 meeting-entry style (Communications/Golf): date under title, (also on Zoom) right, Agenda/Zoom row
            nu = BASE + d["notice_page"]
            srcx = (f'Source: <a href="{CAL}" style="color:{G};">Calendar</a>,&nbsp;&nbsp; ' if e.get("from_calendar", True) else 'Source: ') + f'<a href="{nu}" style="color:{G};">Webmaster</a>'
            # STYLE-RULES.md R13 (Steven Oct 16 6:51 PM, Oct 11 precedent): Zoom → goes to the Vercel Zoom page, never zoom.us
            assert d.get("zoom_page"), f"{d['name']}: webmaster notice needs zoom_page (Vercel) - never link zoom.us directly"
            sys.path.insert(0, SCRIPTS); import meeting_zoom_page as _mzp
            (PAGES / d["zoom_page"]).write_text(_mzp.render(d), encoding="utf-8")
            e = dict(e, also=d["also"], agenda=nu, zoom=BASE + d["zoom_page"])
            L='style="font-size:14px;color:#666666;text-align:right;line-height:1.35;padding-top:1px;'
            out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:4px 8px;border-bottom:1px solid #ddd;"><table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">'
                f'<tr><td valign="top" align="left" style="font-size:15px;line-height:1.3;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">{escape(e["name"])}</td><td valign="top" align="right" style="font-size:14px;line-height:1.3;color:#666666;text-align:right;padding-top:1px;">{escape(e["venue"])}</td></tr>'
                f'<tr><td valign="top" align="left" style="font-size:14px;color:#666666;text-align:left;line-height:1.35;padding-top:1px;padding-right:10px;">{pdate(e["date"])}<span style="white-space:nowrap;"> • {ptime(e["start"])}</span></td><td valign="top" align="right" {L}"><div style="font-size:13px;line-height:1.35;color:#666666;white-space:nowrap;">{escape(e["also"])}</div></td></tr>'
                f'<tr><td valign="top" align="left" style="font-size:14px;line-height:1.35;text-align:left;white-space:nowrap;padding-top:1px;padding-right:10px;"><a href="{e["agenda"]}" style="color:{G};white-space:nowrap;">Agenda →</a>&nbsp;&nbsp;&nbsp;<a href="{e["zoom"]}" style="color:{G};white-space:nowrap;">Zoom →</a></td><td valign="top" align="right" {L}white-space:nowrap;"><span style="white-space:nowrap;">{srcx}</span></td></tr></table></td></tr>')
            continue
        out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:4px 8px;border-bottom:1px solid #ddd;"><table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation"><tr><td valign="top" align="left" style="font-size:15px;line-height:1.3;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">{escape(e["name"])}</td><td valign="top" align="right" style="font-size:14px;line-height:1.3;color:#666666;text-align:right;padding-top:1px;">{escape(VENUE.get(e["venue"], e["venue"]))}</td></tr><tr><td valign="top" align="left" style="font-size:14px;color:#666666;text-align:left;line-height:1.35;padding-top:1px;padding-right:10px;">{pdate(e["date"])}<span style="white-space:nowrap;"> • {ptime(e["start"])}</span>{nt}</td><td valign="top" align="right" style="font-size:14px;color:#666666;text-align:right;white-space:nowrap;line-height:1.35;padding-top:1px;"><span style="white-space:nowrap;">{srcx}</span></td></tr></table></td></tr>')
    return "".join(out)
sys.path.insert(0, SCRIPTS); import style_rules as _sr56
def ev_rows(evs):
    out = []
    assert all(v[0] == "More →" for v in EVENT_LINK.values()), "STYLE-RULES R23: event/notice links say More →"
    for e in evs:  # STYLE-RULES R21 guard
        if (e.get("info") or "").strip() and e["name"] not in EVENT_LINK and e["name"] not in INFO_COVERED:
            _todo(f"R21: {e['date']} {e['name']} has calendar listing text but no More → page (add EVENT_PAGE/EVENT_LINK or INFO_COVERED)")
        if e["name"] in EVENT_PAGE:
            import event_page as _ep; fn, paras = EVENT_PAGE[e["name"]]
            if e["name"] not in PHONE_OK_PAGES and any(re.search(r"\d{3}-\d{3}-\d{4}", x) for x in paras): raise SystemExit(f"phone rule: {e['name']} page has a phone number without Steven's OK (PHONE_OK_PAGES)")
            dl = f"{pdate(e['date'])} • {ptime(e['start'])}" + (f" to {ptime(e['end'])}" if e.get("end") else "") + f" • {VENUE.get(e['venue'], e['venue'])}"
            (PAGES / fn).write_text(_ep.render(e["name"], dl, paras), encoding="utf-8")
    for i, e in enumerate(evs):
        det = EVENT_DETAIL.get(e["name"]); lk = EVENT_LINK.get(e["name"])
        loc = "Mount Dora" if e["name"] == "Mount Dora Trip" else VENUE.get(e["venue"], e["venue"])
        out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;"><table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation"><tr><td valign="top" align="left" style="font-size:15px;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">{escape(TITLE.get(e["name"], e["name"]))}</td><td valign="top" align="right" style="font-size:14px;color:#666666;text-align:right;padding-top:1px;">{escape(loc)}</td></tr><tr><td valign="top" align="left" colspan="2" style="font-size:14px;color:#666666;text-align:left;padding-top:2px;padding-right:10px;">{pdate(e["date"])}<span style="white-space:nowrap;"> • {ptime(e["start"])}</span></td></tr></table>'
                   + (f'<div style="font-size:15px;color:#333333;margin-top:3px;">{escape(det)}</div>' if det else "")
                   + (f'<div style="font-size:14px;margin-top:4px;"><a href="{lk[1]}" style="color:{G};">{lk[0]}</a></div>' if lk else "")
                   + f'<div style="font-size:13px;color:#666666;margin-top:5px;">{src_cal(EVENT_EXTRA_SRC.get(e["name"]))}</div></td></tr>')
    import urllib.request as _ur
    for e, row in zip(evs, out):  # R56 guard
        if e["name"] in MATCHED_NOTICE:
            _u = MATCHED_NOTICE[e["name"]]; _lp = PAGES / _u.rsplit("/", 1)[1]
            assert _lp.exists(), f"R56: notice page missing {_lp}"
            _sr56.assert_matched_event_card(row, e["name"], _u, CAL, _lp.read_text(encoding="utf-8")); print("R56 matched:", e["date"], e["name"], "->", _lp.name)
    for _n, _u in MATCHED_NOTICE.items():  # R56b (Steven Oct 21 11:20 AM): a matched event's notice must be listed in Community Notices
        if any(e["name"] == _n for e in evs): assert any(n[3] == _u for n in NOTICES), f"R56b: {_n} links notice {_u} but it is not in Community Notices"
    return "".join(out)
# R1 (Steven Oct 24 12:18 PM): every Listen button sits ~14px in from its row's right edge (shared, not per-page)
LISTEN_INSET = "margin-right:14px;"
def listen(href, size=15):
    return (f'<a href="{href}" style="color:{G};white-space:nowrap;font-size:14px;display:inline-block;{LISTEN_INSET}"><img src="{SPK}" width="24" height="24" alt="" '
            f'style="display:inline-block;width:24px;height:24px;vertical-align:middle;border:0;outline:none;text-decoration:none;margin:-3px 4px -3px 0;">Listen</a>')
def title_row(title, right):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;"><tr><td valign="top" align="left" style="font-size:15px;line-height:18px;font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{title}</td>'
            f'<td valign="top" align="right" style="font-size:13px;line-height:18px;text-align:right;white-space:nowrap;width:1%;">{right}</td></tr></table>')

# ---------- Community Notices (palmhillblast + gotwicz Gmail as of Oct 15) ----------
# Notice data (TONY_FB*, FB*, WM_COPIES, NOTICE_PAGES, NOTICES, ...) come from the issue content file (R71).
# ---------- STYLE-RULES L27/L29 (Steven, Oct 17 11:51 PM): Webmaster source copies ----------
# Every Webmaster Source credit is the linked word "Webmaster" (no date, no sender) opening a copy of the source email.
# These three Webmaster emails (noreply@palmhillcountryclub.net, gotwicz Gmail) had no copy page; scripts/notice_page.py renders
# them in the info-from-linda shell, verbatim (only blank lines, &nbsp; runs, zero-width spaces and the unsubscribe footer dropped).
sys.path.insert(0, SCRIPTS); import notice_page as _np
# R60c-style source checks + generated notice pages (NOTICE_PAGES, content file) + Webmaster copy pages (WM_COPIES)
for _sv, _spg, _smsg in SOURCE_VERBATIM:
    assert _sv in (PAGES / _spg).read_text(encoding="utf-8"), _smsg
for _p in NOTICE_PAGES:
    (PAGES / _p["page"]).write_text(_np.render(_p["subject"], _p["sent"], _p["blocks"], **_p["kw"]), encoding="utf-8")
    _np.notice_listen.add(str(REPO), _p["page"])
for _n, _subj, _sent, _blocks in WM_COPIES:
    _np.write(str(REPO), _n, _subj, _sent, _blocks)
NOTICES = [n for n in NOTICES if n[0] not in NOTICES_DROPPED_OCT25]
# Per-issue carry policy (content file NOTICES_DROPPED): keep notices still valid on/after the issue date, drop the previous
# issue's one-offs that are expired or were news for that week only. Re-check every kept notice against the Friday inbox sweep.
NOTICES_DROPPED_ISSUE = set(C.NOTICES_DROPPED)
_unknown = NOTICES_DROPPED_ISSUE - {n[0] for n in NOTICES}
if _unknown: raise SystemExit(f"R71: {ISSUE} NOTICES_DROPPED names unknown notice title(s): {sorted(_unknown)}")
NOTICES = [n for n in NOTICES if n[0] not in NOTICES_DROPPED_ISSUE]
assert not {n[0] for n in NOTICES} & NOTICES_DROPPED_ISSUE
assert not {n[0] for n in NOTICES} & NOTICES_DROPPED_OCT25
def notice_rows():
    rows, items = [], [(TONY_FB[0], TONY_FB_TXT, TONY_FB_SOURCE, None)] + NOTICES
    for i, (t, txt, sl, sh) in enumerate(items):
        ph = t == TONY_FB[0] and TONY_FB_PLACEHOLDER
        lh = (NOTICE_LISTEN_OVERRIDE.get(t, sh) + "?listen=1") if sh else (FB_LISTEN if t == TONY_FB[0] else None)
        assert lh, f"R60: notice {t!r} has no Listen page"
        right = listen(lh)
        src = f'Source: <a href="{sh}" style="color:{G};">{escape(sl)}</a>' if sh else f"Source: {escape(sl)}"
        rowbg = "#FFF3B0" if ph else bg(i)
        rows.append(f'<tr style="background:{rowbg};page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;{"border:2px dashed #B8860B;" if ph else ""}">'
                    + title_row(escape(t), right)
                    + f'<div style="font-size:15px;color:#333333;margin-top:3px;">{txt if "<a " in txt else escape(txt)}</div>'
                    + f'<div style="font-size:13px;color:#666666;margin-top:5px;">{src}</div></td></tr>')
    return "".join(rows)

# ---------- Chair reports: stacked cards (to-do #12) ----------
# CHAIR (cards), CHAIR_REPORTS (generated report pages), RULES_ARCHIVE_ONLY and ARCHIVE_ROWS come from the issue content file (R71).
sys.path.insert(0, SCRIPTS); import chair_report_page as _crp
for _cr in CHAIR_REPORTS:
    if not (PAGES / _cr["page"]).exists(): (PAGES / _cr["page"]).write_text(  # a published page (Listen added by build_archive.js) is never overwritten
        _crp.render(_cr["title"], _cr["blocks"], _cr["source"], _cr["page"]), encoding="utf-8")
    # seed the listen-* page once; build_archive.js (dateline_listen) rebuilds it from the report page on every run
    _lp = PAGES / _cr["listen"]
    if not _lp.exists(): _lp.write_text((PAGES / _cr["page"]).read_text(encoding="utf-8"), encoding="utf-8")
    CHAIR.insert(0, _cr["card"])
def _arch_row(section, row):
    """R59: add an archive row (newest first) to archive/archive-items.json once; idempotent on the row's page."""
    _aj.add_rows(REPO, section, [row])
for _sec, _row in ARCHIVE_ROWS: _arch_row(_sec, _row)
for _pg, _ls, _blocks in RULES_ARCHIVE_ONLY:
    if not (PAGES / _pg).exists(): (PAGES / _pg).write_text(  # Oct 25: keep published page
        _crp.render(RULES_ARCHIVE_TITLE, _blocks, RULES_ARCHIVE_SOURCE, _pg), encoding="utf-8")
    _lp = PAGES / _ls
    if not _lp.exists(): _lp.write_text((PAGES / _pg).read_text(encoding="utf-8"), encoding="utf-8")
def chair_cards():
    out = []
    # RETENTION (Steven, Oct 16): latest report per committee, shown only if dated within 30 days of the issue; older -> archive only
    from datetime import date as _d, timedelta as _td
    cutoff = (_d.fromisoformat(ISSUE) - _td(days=30)).isoformat()
    latest = {}
    for c in sorted(CHAIR, key=lambda c: c[1], reverse=True): latest.setdefault(c[0], c)
    shown = [c for c in latest.values() if c[1] >= cutoff]
    print("chair reports dropped (30-day rule):", [(c[0], c[1]) for c in latest.values() if c[1] < cutoff])
    # President's Message + weekly/monthly Manager reports: stay until replaced by a newer one or Steven overrides (no age cutoff)
    for i, (t, d, s, full, lis) in enumerate(sorted(shown, key=lambda c: c[1], reverse=True)):
        out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:10px 10px;border-bottom:1px solid #ddd;border-left:4px solid #2D5016;">'
                   # R63 (Steven Oct 24 2026): Listen on the card's TITLE line, right-justified (like the other sections), not beside Read Full Report
                   f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;"><tr><td valign="top" align="left" style="font-size:16px;line-height:20px;font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{escape(t)}</td>'
                   f'<td valign="top" align="right" style="font-size:15px;line-height:20px;text-align:right;white-space:nowrap;width:1%;">{listen(lis)}</td></tr></table>'
                   f'<div style="font-size:14px;color:#666666;margin-top:2px;">{pdate(d)}</div>'
                   f'<div style="font-size:17px;line-height:1.45;color:#333333;margin-top:5px;">{escape(s)}</div>'
                   f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;margin-top:8px;"><tr><td align="left" style="font-size:15px;text-align:left;"><a href="{full}" style="color:{G};white-space:nowrap;">Read Full Report →</a></td></tr></table></td></tr>')
    # R63 guard: every chair card's Listen sits on its title line (before the date line); none beside Read Full Report
    for _r in out:
        if ">Listen</a>" in _r:
            assert _r.index(">Listen</a>") < _r.index('color:#666666;margin-top:2px;'), "R63: chair card Listen must be on the title line"
            assert ">Listen</a>" not in _r[_r.index("Read Full Report"):], "R63: Listen beside Read Full Report"
    out.append(f'<tr><td style="padding:6px 8px;font-size:14px;"><a href="{ARCH}committee-reports.html" style="color:{G};">Committee Report Archives →</a></td></tr>')
    return "".join(out)

# ---------- assemble ----------
s = SEED.read_text(encoding="utf-8")
s = s.replace("<title>", "<title>", 1)
s = re.sub(r"<title>.*?</title>", f"<title>PHNEWS {C.ISSUE_LONG} — DRAFT (not sent)</title>", s, count=1, flags=re.S)
s = s.replace('color:#e5f1d1;">October 18, 2026<', 'color:#e5f1d1;">Sunday, October 18, 2026<')  # batch item 1: weekday in masthead
s = s.replace("October 11, 2026", "October 18, 2026").replace("Vol. 1, No. 13", "Vol. 1, No. 14")
s = s.replace("October 18, 2026", C.ISSUE_LONG).replace("Vol. 1, No. 14", C.VOLNO)  # this issue (Oct 18 seed)
stamp = os.environ.get("PHNEWS_BUILD_STAMP") or datetime.now(ZoneInfo("America/New_York")).strftime("%-I:%M %p")  # override only for byte-identical re-renders
s = s.replace(">3:07 PM<", f">{stamp}<")

def section_span(s, heading):
    h = s.find(f">{heading}</span>"); assert h > 0, heading
    a = max(s.rfind('<div class="canonical-section">', 0, h), s.rfind('<div class="section04">', 0, h))
    nxt = [x for x in (s.find('<div class="canonical-section">', h), s.find('<div class="section04">', h),
                       s.find('<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 0 0;">', h)) if x > 0]
    return a, min(nxt)
def replace_table(heading, rows, subtitle=None):
    global s
    a, b = section_span(s, heading); sec = s[a:b]
    t0 = sec.find('<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 12px 0;">')
    sec = sec[:t0] + '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 12px 0;">' + rows + "</table></div>"
    if subtitle: sec = re.sub(r'(margin-top:3px;">)[^<]*(</div></div>)', lambda m: m.group(1) + subtitle + m.group(2), sec, count=1)
    s = s[:a] + sec + s[b:]

# R78 (Steven, Oct 26 2026 11:15 AM): from Nov 1 the Meetings header has no date range (one row per committee, R54, is not every
# meeting in a window). Content flag MEETINGS_SHOW_RANGE (default True = Oct 25 and earlier, byte for byte).
if globals().get("MEETINGS_SHOW_RANGE", True):
    replace_table("Committee &amp; Board Meeting Schedules", mtg_rows(), f"{md(MEETINGS[0])} through {md(max(MEETINGS[1], meetings[-1]["date"]))}")
else:
    replace_table("Committee &amp; Board Meeting Schedules", mtg_rows())
    _a, _b = section_span(s, "Committee &amp; Board Meeting Schedules")
    _sec = re.sub(r'<div style="font-size:14px;font-style:italic;color:#FFFFFF;margin-top:3px;">[^<]*</div>(</div>)', r"\1", s[_a:_b], count=1)
    assert " through " not in _sec[:_sec.find('<table')], "R78: Meetings header must carry no date range"
    s = s[:_a] + _sec + s[_b:]
replace_table("Committee Chair Reports", chair_cards())
replace_table("Community Notices", notice_rows())
# R79 (Steven, Oct 26 2026 11:25 AM): from Nov 1 both Events sections end with a link to the All Events page = every event in the
# issue's Recurring window that is not on the Recurring pages, chosen with the same rule as This Week/Upcoming (evsel).
# Link text + note come from the content file (ALL_EVENTS_LINK_TEXT / ALL_EVENTS_NOTE); off unless ALL_EVENTS_PAGE (Oct 25 unchanged).
_AE = bool(globals().get("ALL_EVENTS_PAGE", False))
all_events = evsel(RECURRING) if _AE else []
AE_FILE = f"{ISSUE}-all-events-by-date.html"  # default sort, like the Recurring link
def _ae_link():
    if not _AE: return ""
    return f'<tr><td style="padding:6px 8px;font-size:14px;"><a href="{BASE}{AE_FILE}" style="color:{G};">{escape(ALL_EVENTS_LINK_TEXT)}</a></td></tr>'
replace_table("Events - Upcoming", ev_rows(upcoming) + _ae_link(), f"{md(UPCOMING[0])} through {md(UPCOMING[1])}")
# Events - This Week (cloned from Upcoming shell) placed per L03 order
a, b = section_span(s, "Events - Upcoming"); up = s[a:b]
tw = up.replace("events-upcoming-detailed", "events-this-week-detailed").replace(">Events - Upcoming<", ">Events - This Week<").replace('data-heading-variant="upcoming_events"', 'data-heading-variant="this_week"')
r0, _ = section_span(s, "Recurring Meetings &amp; Events")
s = s[:r0] + tw + s[r0:]   # L03: This Week sits between Chair Reports and Recurring
replace_table("Events - This Week", ev_rows(this_week) + _ae_link(), f"{md(THIS_WEEK[0])} through {md(THIS_WEEK[1])}")
if _AE:  # R79 All Events pages are written by recurring.py + recurring_grouped.py (same shell and sorts as Recurring)
    assert not any(e.get("recurring") or e["name"] in AS_RECURRING for e in all_events), "R79: an All Events row is on the Recurring pages"
    for _o in ("date", "name", "location"):
        assert (PAGES / f"{ISSUE}-all-events-by-{_o}.html").exists(), f"R79: run recurring.py + recurring_grouped.py first ({ISSUE}-all-events-by-{_o}.html)"
# Recurring: window text; Oct 18 recurring pages don't exist yet -> keep live Oct 11 pages (flagged)
s = s.replace("Oct 11 through Nov 9, 2026", f"{md(RECURRING[0])} through {md(RECURRING[1])}, 2026")
# STYLE-RULES R20: the issue links to its own week's Recurring pages (recurring_oct18.py + recurring_grouped.py ... 2026-10-18)
s = s.replace("2026-10-11-recurring-activities-by-", f"{RECURRING[0]}-recurring-activities-by-")

# ---------- STYLE-RULES R45 (Steven, Oct 18 12:07 AM): Community Stories section ----------
# The section ran once (Oct 4, Mary Leslie). The Oct 11 builder dropped it ("no new story", drop_section) and the Oct 18 builder,
# cloned from Oct 11, never had it. Oct 18 carries Carolyn M. Story's Marge Taylor profile (Palm Hill Link Sep 2026, pp. 10-12;
# confirmed in Carolyn's Sep 28 email to palmhillblast; story + listen pages built Oct 9, PR #10; never in a newsletter before).
# Placed where Oct 4 had it: right before From the Board President. Teaser = verbatim sentence from the story page.
# Oct 25 (PR #130, Steven Oct 19): Joe Clay - Keeper of The Course; date line Oct 1, 2026; credit line TBD (no source credit printed;
# new rule Oct 20: no Palm Hill Link name inside articles). Preview pages until publish creates the live page (_JC live_page_planned).
# R18c (Steven Oct 24 12:18 PM): over-long phone teasers are CUT (never reworded) to their first source sentence(s);
# the full text stays word-for-word on the item's own page. Guard: the cut must be a prefix of the source text.
def _R18_CUT(text, n):
    import re as _re0
    sents = _re0.split(r"(?<=[.!?])\s+", text.strip()); cut = " ".join(sents[:n])
    assert text.startswith(cut) and cut, ("R18c cut is not a prefix of the source", text); return cut
STORY = None
if C.STORY:   # content file STORY = dict(json=<story data json>, listen=<listen page>, teaser_sentences=n)
    _JC = json.load(open(REPO / C.STORY["json"], encoding="utf-8"))
    STORY = dict(title=_JC["title"], date=_JC["date_iso"], teaser=_R18_CUT(_JC["teaser_candidate"], C.STORY["teaser_sentences"]),
                 page=_JC["live_page_planned"], listen=C.STORY["listen"],   # Steven Oct 20 4:33 PM: live page (written by stage script), never the undeployed preview URL
                 source=None, archive_title=_JC["title"])
# PHNEWS_DRYRUN=1 lets the build finish without a story for workspace testing only -- it is NOT Steven's R45 approval and never publishes.
COMMUNITY_STORIES_OMIT_APPROVED = (C.STORY_OMIT_DRYRUN_NOTE if os.environ.get("PHNEWS_DRYRUN") == "1" and C.DRYRUN_OK and not STORY else None)   # R45: set to "<Steven's approval, date/time>" only when Steven approves an issue without a story
if STORY: _story_page = (PAGES / STORY["page"]).read_text(encoding="utf-8")
if STORY: assert STORY["teaser"].replace("'", "\u2019") in _story_page or STORY["teaser"] in _story_page, "R45: story teaser must be verbatim from the story page"
if STORY: assert (PAGES / STORY["listen"]).exists(), "R45: story listen page missing"
if STORY:
    _d = date.fromisoformat(STORY["date"])
    _row = (f'<tr style="background:#FFFFFF;page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;">'
            + title_row(escape(STORY["title"]), listen(BASE + STORY["listen"] + "?listen=1"))
            + f'<div style="font-size:14px;color:#666666;margin-top:2px;">{_d.strftime("%A, %b %-d, %Y")}</div>'
            + f'<div style="font-size:15px;color:#333333;margin-top:3px;">{escape(STORY["teaser"])} <a href="{BASE + STORY["page"]}" style="color:{G};white-space:nowrap;">More →</a></div>'
            + f'<div style="margin-top:4px;font-size:14px;line-height:1.6;"><a href="{ARCH}community-stories.html" style="color:{G};white-space:nowrap;">Story Archives →</a></div>'
            + (f'<div style="font-size:13px;color:#666666;margin-top:5px;">Source: {escape(STORY["source"])}</div>' if STORY["source"] else "") + '</td></tr>')
    a, b = section_span(s, "From the Board President"); _pres = s[a:b]
    _cs = _pres[:_pres.find('<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 12px 0;">')]
    _cs = (_cs.replace(">From the Board President</span>", ">Community Stories</span>")
              .replace("2026-10-04/board-president-message-scroll-512-v1.png", "v3/residents-reference-guide-detailed-512-v1.png"))  # Oct 4 icon
    _cs += '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 12px 0;">' + _row + "</table></div>"
    s = s[:a] + _cs + s[a:]
    # the community-stories archive row records this issue ("In the newsletter: Oct 18")
    _sd = _aj.load(REPO)[1]["sections"]["community-stories"]["items"]
    _mi = [r for r in _sd if r.get("date") == STORY["date"] and r.get("title") == STORY["archive_title"]]
    _V2_STORY = ISSUE >= json.load(open(REPO / "scripts/listen_settings.json"))["v2_from"]
    if not _mi:  # Steven Oct 20 4:33 PM: preview builds add the archive row too (was deferred to publish)
        _aj.add_rows(REPO, "community-stories", [{"date": STORY["date"], "date_label": STORY_DATE_LABEL, "title": STORY["archive_title"], "summary": STORY["teaser"],
                           "page": STORY["page"], "listen": STORY["listen"], "issues": [ISSUE], **({"listen_v": 2} if _V2_STORY else {})}])
    elif _V2_STORY and _mi[0].get("listen_v") != 2:   # R83/R76: story carried in a v2 issue gets the v2 listen page
        _aj.set_field(REPO, "community-stories", {"date": STORY["date"], "title": STORY["archive_title"]}, "listen_v", 2)
    if _mi and ISSUE not in _mi[0].get("issues", []):
        _aj.set_field(REPO, "community-stories", {"date": STORY["date"], "title": STORY["archive_title"]}, "issues", _mi[0].get("issues", []) + [ISSUE])
# Weekly Manager Update page (WMU_* data from the issue content file): built from the previous page's card template, item by item.
_wp = PAGES / WMU_1023_PAGE
if not _wp.exists():  # published page (nav/Listen kept current by build_archive.js) is never overwritten
    _tpl = (PAGES / WMU_TEMPLATE).read_text(encoding="utf-8")
    def _li(x):
        if isinstance(x, tuple):
            return f"<li>{escape(x[0], quote=False)}<blockquote>" + "".join(f"<p>{q}</p>" for q in x[1]) + "</blockquote></li>"
        return f"<li>{escape(x, quote=False)}</li>"
    _a = _tpl.index('<main><section class="content-card">') + len('<main><section class="content-card">')
    _b = _tpl.index('<p class="signoff">', _a)
    _tpl = _tpl[:_a] + f"\n<p>{WMU_GREETING}</p>\n<ul>\n" + "\n".join(_li(x) for x in WMU_1023) + "\n</ul>\n" + _tpl[_b:]
    _a = _tpl.index('<section class="content-card attachments"'); _b = _tpl.index("</section>", _a) + len("</section>\n")
    _tpl = _tpl[:_a] + _tpl[_b:]   # Oct 16 photo attachment does not carry over; the RPM minutes PDF is not hosted (flagged)
    for o, n in WMU_REPLACE:
        _tpl = _tpl.replace(o, n)
    assert WMU_TEMPLATE_DATE not in _tpl.split("<!-- ph-page-listen:start -->")[0], "WMU template still has the template page's date refs"
    _wp.write_text(_tpl, encoding="utf-8")
# R65: the weekly update's attached PDF (WMU_1023_PDF*, content file) is copied (never moved) and linked in an Attachments card.
# R72 (batch 6, Steven Oct 24 2026 10:40 PM "do them all"): the PDF source is a content-file path relative to the work tree.
if Path(WMU_1023_PDF_SRC).is_absolute(): raise SystemExit("R72 FAIL: WMU_1023_PDF_SRC must be relative to PHNEWS_WORK, not a fixed folder. Why: builds must not depend on one machine's folders. Fix: copy the PDF into <work>/source/ and set the relative path in the content file.")
WMU_1023_PDF_SRC = ROOT / WMU_1023_PDF_SRC
if not WMU_1023_PDF_SRC.exists(): raise SystemExit(f"R72 FAIL: weekly update PDF {WMU_1023_PDF_SRC} is missing. Why: the Attachments card would link a missing file. Fix: copy the PDF there (copy, never move).")
_pdf = PAGES / WMU_1023_PDF
if not _pdf.exists():
    import shutil as _shp; _pdf.parent.mkdir(parents=True, exist_ok=True); _shp.copy2(WMU_1023_PDF_SRC, _pdf)
_wt = _wp.read_text(encoding="utf-8")
if WMU_1023_PDF not in _wt:
    _att = ('<section class="content-card attachments" aria-labelledby="att-h"><h2 id="att-h">Attachments</h2>\n<ul class="att-docs">\n'
            f'<li><a href="/pages/{WMU_1023_PDF}" target="_blank" rel="noopener"><span class="att-icon" aria-hidden="true">📄</span>'
            f'<span><b>{WMU_1023_PDF_TITLE}</b><small>{WMU_1023_PDF_DESC}</small></span></a></li>\n</ul>\n</section>\n')
    _k = _wt.index("</section>", _wt.index('<p class="signoff">')) + len("</section>\n")
    _wt = _wt[:_k] + _att + _wt[_k:]
    _wp.write_text(_wt, encoding="utf-8")
assert _wt.count(f'href="/pages/{WMU_1023_PDF}"') == 1 and _pdf.stat().st_size == WMU_1023_PDF_SRC.stat().st_size, "R65: weekly update PDF link/copy missing"
for _sec, _row in ARCHIVE_ROWS_LATE: _arch_row(_sec, _row)
# Weekly Manager Update card on the main page: the newest update replaces the seed card (retention rule); WMU_CARD_* in the content file
_W_OLD = s[s.find(WMU_CARD_OLD):]
_W_OLD = _W_OLD[:_W_OLD.find('</td></tr>')]
assert WMU_CARD_OLD_MARK in _W_OLD
_W_NEW = ('<div style="font-size:15px;font-weight:bold;color:#333333;">Weekly Manager Update</div>'  # R19: date only on the date line
    f'<div style="font-size:14px;color:#666666;margin-top:2px;">{WMU_CARD_DATE}</div>'
    f'<div style="font-size:15px;color:#333333;margin-top:3px;">{WMU_CARD_TEASER}</div>'
    f'<div style="margin-top:4px;font-size:14px;line-height:1.6;"><a href="{BASE}{WMU_1023_PAGE}" style="color:{G};white-space:nowrap;">Read Full Update →</a><span style="color:#999999;"> · </span><a href="{ARCH}weekly-manager-updates.html" style="color:{G};white-space:nowrap;">Weekly Manager Report Archives →</a></div>'
    f'<div style="font-size:13px;color:#666666;margin-top:5px;"><a href="{BASE}{WMU_1023_PAGE}" style="color:{G};">Source</a>: Weekly Manager Update</div>')
s = s.replace(_W_OLD, _W_NEW)
# Manager reports: Listen icon on the title line (pages have built-in Listen; ?listen=1 autostarts)
for t, href in MANAGER_LISTEN:
    old = f'<div style="font-size:15px;font-weight:bold;color:#333333;">{t}</div>'; assert old in s, t
    s = s.replace(old, title_row(t, listen(href + "?listen=1")))
# Henry October already the President's Message (to-do #7). Did You Know: archive link (to-do, Oct 11 evening)
old = f'<a href="{ARCH}videos.html" style="color:{G};">Latest Board and committee recordings →</a></div>'
assert old in s
s = s.replace(old, f'<a href="{ARCH}videos.html" style="color:{G};">Latest Board and Committee Meeting Videos →</a><span style="color:#999999;"> · </span><a href="{ARCH}did-you-know.html" style="color:{G};">Did You Know Archives →</a></div>')
# Did You Know: Tony's FB variation (verbatim, Oct 16) appended as 2nd row
a = s.find(">Did You Know?</span>"); e = s.find("</table></div>", a); assert a > 0 and e > 0
DYK_FB = (f'<tr style="background:#F5F5F5;page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;">'
    f'<div style="font-size:15px;color:#333333;margin-top:3px;">{DYK_FB_TEXT}</div>'
    f'<div style="font-size:14px;margin-top:4px;"><a href="{FBURL}" style="color:{G};">{FBURL}</a></div>'
    f'<div style="font-size:14px;margin-top:4px;"><a href="{FBPAGE_DYK}" style="color:{G};">Full item with QR code to scan →</a></div></td></tr>')
# Steven's rule (Oct 16): main issue shows ONLY the newest Did You Know; older items live on archive/did-you-know.html
# Steven, Oct 17 1:40 PM (post-proof addition): Rule of the week from David Bates (david.palmhill@gmail.com), palmhillblast
# "Park Rule for Newsletter", Sat Oct 17 1:17 PM ET (his corrected resend of "Rule for Newsletter", 12:53 PM). Summary = his
# wording; full narrative on the Did You Know page (make_live_preview.py dykpage -> publish 2026-10-18-did-you-know-traffic-rules.html).
# STYLE-RULES R39 (Steven, Oct 17 6:22 PM): DYK summary ~3 lines at desktop, built ONLY from Dave's own sentences (XI. TRAFFIC
# RULES text, 1:17 PM email); light trimming only ("Further - " dropped, ".." -> "."). Verbatim check in style_rules.dyk_summary_ok.
import html as _html
sys.path.insert(0, SCRIPTS); import style_rules as _sr_dyk
_DYK_SRC = json.load(open(ROOT / DYK_RULES_SOURCE_FILE))
assert _sr_dyk.dyk_summary_ok(DYK_RULES_SUMMARY, _DYK_SRC), "R39: DYK summary must be at most 3 of Dave's verbatim sentences"
# R39: the Did You Know archive row shows the same summary (archive/archive-items.json, id traffic-rules)
_AI = _aj.path(REPO)
_aj.set_field(REPO, "did-you-know", DYK_RULES_ARCHIVE_KEY, "text", DYK_RULES_SUMMARY)
if DYK_RULES_TEASER_MODE == "framing":
    assert _sr_dyk.dyk_framing_ok(DYK_RULES_TEASER, DYK_CONTRIBUTOR_NAMES, _DYK_SRC), "R39: framing teaser has a name, quotes a rule, or is over 3 lines"
    _DYK_MAIN = DYK_RULES_TEASER
else:
    _DYK_MAIN = DYK_RULES_SUMMARY
DYK_RULES = (f'<tr style="background:#F5F5F5;page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;">'
    f'<div style="font-size:15px;color:#333333;margin-top:3px;">{_html.escape(_DYK_MAIN)} '
    f'<a href="{DYK_RULES_PV}" style="color:{G};white-space:nowrap;">More →</a></div></td></tr>')
_DYK25 = json.load(open(REPO / DYK_ITEMS_JSON, encoding="utf-8"))
_DYK3 = json.load(open(REPO / DYK_RULES_ITEM_JSON, encoding="utf-8"))
# R57 (Steven Oct 21 11:22 AM): each Did You Know item is its own block -- bold title (the item's source heading), teaser, then
# More → on its own line; a white gap + green left bar separates items. Guard: style_rules.assert_dyk_blocks.
def _dyk_row(title, text, href):
    return (f'<tr class="ph-dyk-item" style="background:#F5F5F5;page-break-inside:avoid;break-inside:avoid;"><td style="padding:10px 10px;border-left:4px solid #2D5016;border-bottom:10px solid #FFFFFF;">'
            f'<div class="ph-dyk-title" style="font-size:16px;font-weight:bold;color:#333333;">{_html.escape(title)}</div>'
            f'<div style="font-size:15px;color:#333333;margin-top:4px;">{_html.escape(text)}</div>'
            f'<div class="ph-dyk-more" style="font-size:14px;margin-top:6px;"><a href="{href}" style="color:{G};white-space:nowrap;">More →</a></div></td></tr>')
DYK_ITEMS = []
# Steven Oct 21 11:25 AM: final page URLs (Oct 18 pattern pages/<issue>-did-you-know-<slug>.html, written by the stage script)
def _dyk_final(pp): return DYK_PAGE_PREFIX + pp
for _it in _DYK25["items"]:
    assert _sr_dyk.dyk_summary_ok(_TEASE[_it["id"]], _it["paragraphs"]), ("R39 distilled teaser not verbatim", _it["id"])
    DYK_ITEMS.append((_it["id"], _dyk_row(_DYK_TITLE.get(_it["id"], _it["title_display"]), _TEASE[_it["id"]], BASE + _dyk_final(_it["preview_page"]))))
_d3src = _DYK3["email_paragraphs"] + [x for _, x in _DYK3["rule_items"]]
# Steven Oct 21 11:22 AM: teaser = distilled summary in the official rule's own words (R39 distilled: verbatim sentences, <= 300 chars)
# Steven Oct 21 11:39 AM: teaser in the rule's own words (his wording). Guard: every content word is in the official rule text.
# R18c (Steven Oct 24 12:18 PM): cut at the semicolon (no rewording) so the phone teaser is <= 3 lines
_DYK3_TEASER = _DYK3_TEASER_FULL.split("; ")[0] + "."
assert _DYK3_TEASER_FULL.startswith(_DYK3_TEASER[:-1])
_rw = set(re.findall(r"[a-z0-9$.]+", " ".join(x for _, x in _DYK3["rule_items"]).lower().replace("home/unit", "home unit")))
_tw = [w.strip(".") for w in re.findall(r"[a-z0-9$.]+", _DYK3_TEASER.lower().replace("home/unit", "home unit"))]
_bad = [w for w in _tw if w and w not in _rw and w.rstrip(".") not in {x.rstrip(".") for x in _rw} and w not in {"if", "are", "total"}]
assert not _bad, f"R39: DYK #3 teaser words not in the official rule: {_bad}"
# R66 (Steven Oct 24 2026 3:02 PM): Rules DYK teaser generated from the rule's lettered parts; phrase override per item.
_DYK3_TEASER, _r66p = _sr_dyk.rules_dyk_teaser(_DYK3["rule_items"], _R66_PHRASES.get(_DYK3["id"]))
_sr_dyk.assert_rules_dyk(_DYK3_TEASER, _DYK3["rule_items"], _r66p, _DYK3["id"])
assert _DYK3_TEASER == DYK_RULES_ITEM_TEASER_APPROVED, _DYK3_TEASER  # Steven's chosen wording (content file)
# R66 covers every Rules DYK item (any item carrying rule_items); the Spectrum items are not rules.
assert not any("rule_items" in _it for _it in _DYK25["items"]), "R66: new Rules DYK item needs an _R66_PHRASES entry / review"
DYK_ITEMS.insert(0, (_DYK3["id"], _dyk_row(_DYK3["title_display"], _DYK3_TEASER, BASE + _dyk_final(_DYK3["preview_page"]))))  # Steven Oct 20 3:03 PM: Dave's rules item FIRST (R31)
DYK_MULTI_APPROVED = _DYK25["dyk_multi_approved"] + "; " + _DYK3["multi_approved"]
_sr_dyk.assert_dyk_items([{"id": i, "paragraphs": [r]} for i, r in DYK_ITEMS], DYK_MULTI_APPROVED)  # R50
t0 = s.find("<table", a)
s = s[:t0] + '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 12px 0;">' + "".join(r for _, r in DYK_ITEMS) + f'<tr><td style="padding:2px 8px;font-size:14px;"><a href="{ARCH}did-you-know.html" style="color:{G};">Did You Know Archives →</a></td></tr>' + s[e:]  # R50: one archive link after the last item
_sr_dyk.assert_dyk_blocks(s, len(DYK_ITEMS))  # R57
# R59 (Steven Oct 21 11:25 AM): preview builds add archive rows for every archive-backed issue item (DYK here; story above),
# newest first, existing row format; build_archive.js (run at the end) renders them. Guard at the end: each item is on its archive page.
_DYK_ROWS = [dict(date=DYK_ROW_DATE, id=_DYK3["id"].replace(DYK_PAGE_PREFIX, ""), title=_DYK3["title_display"], text=_DYK3_TEASER,
                  page=_dyk_final(_DYK3["preview_page"]), source_label=_DYK3["source"], issues=DYK_ROW_ISSUES)]
for _it in _DYK25["items"]:
    _r = dict(date=DYK_ROW_DATE, id=_it["id"].replace(DYK_PAGE_PREFIX, ""), title=_DYK_TITLE.get(_it["id"], _it["title_display"]), text=_TEASE[_it["id"]],
              page=_dyk_final(_it["preview_page"]), issues=DYK_ROW_ISSUES)
    if _it.get("byline"): _r["source_label"] = _it["byline"]
    _DYK_ROWS.append(_r)
_aj.add_rows(REPO, "did-you-know", _DYK_ROWS)
# R66b (Steven Oct 24 3:16 PM): current-issue Rules DYK archive row uses the same R66 teaser as the main page (past rows untouched)
_ai2 = _sr_dyk.sync_rules_dyk_archive_text(_AI.read_text(encoding="utf-8"), DYK_ROW_DATE, _DYK_ROWS[0]["id"], _DYK3_TEASER)
_aj.save_text(REPO, _ai2, json.loads(_ai2))
# R66c (Steven Oct 24 3:34 PM "Yes"): Oct 18 Traffic Rules archive row teaser re-generated in R66 style (archive row ONLY;
# Oct 18 issue, SEND html and the detail page stay as sent). Parts = the sentences of Dave's "Sections of the rule" (source json).
_TR_SRC = json.loads((REPO / R66C_SOURCE_JSON).read_text(encoding="utf-8"))[-1]
_TR_SENT = re.split(r"(?<=\.)\.?\s+", _TR_SRC.split("Sections of the rule:", 1)[1].strip())
_TR_ITEMS = [(chr(65 + i), t) for i, t in enumerate(_TR_SENT[:6])]  # A-F; last sentence ("Most of all, be safe...") is not a rule part
_TR_PHRASES = R66C_PHRASES
_TR_TEASER, _trp = _sr_dyk.rules_dyk_teaser(_TR_ITEMS, _TR_PHRASES)
_sr_dyk.assert_rules_dyk(_TR_TEASER, _TR_ITEMS, _trp, R66C_ROW_ID)
_ai3 = _sr_dyk.sync_rules_dyk_archive_text(_AI.read_text(encoding="utf-8"), R66C_ROW_DATE, R66C_ROW_ID, _TR_TEASER)
_aj.save_text(REPO, _ai3, json.loads(_ai3))
ARCHIVE_BACKED = [("did-you-know.html", r["page"]) for r in _DYK_ROWS]
# Steven Oct 23 5:09 AM: the two new Webmaster notices get Community Notices archive rows in this build (R59), teaser = issue teaser
_NOTICE_ROWS = NOTICE_ARCHIVE_ROWS
_aj.add_rows(REPO, "community-notices", _NOTICE_ROWS)
ARCHIVE_BACKED += [("community-notices.html", r["page"]) for r in _NOTICE_ROWS if r["title"] not in NOTICES_DROPPED_ISSUE]
# Helpful Webpages + archive footer links -> live /pages/ URLs
s = s.replace(f'<a href="{ARCH}meeting-videos.html" style="color:{G};">Palm Hill Committee Videos</a></div>',
              f'<a href="{ARCH}main.html" style="color:{G};">Palm Hill Newsletter Archives</a></div>\n          <div>• <a href="{ARCH}videos.html" style="color:{G};">Committee Meeting Videos - Latest</a></div>\n          <div>• <a href="{ARCH}meeting-videos.html" style="color:{G};">Committee Meeting Video Archives</a></div>')
# STYLE-RULES R25 (Steven, Oct 17 12:20 AM): footer archive-links row removed (links stay in Helpful Webpages);
# Helpful Webpages label is 'Committee Meeting Video Archives' (never 'Committee Meeting Videos - Archives')
assert 'Videos - Archives' not in s, 'R25 label'
sys.path.insert(0, SCRIPTS); import style_rules as _sr  # STYLE-RULES.md (shared)
s = _sr.enforce_title_months(s)  # full months in titles/bands
import link_archive_bullet as _lab; s = _lab.add(s)
# R81 (Steven approved Oct 24 2026; "go" Oct 26 11:49 AM): Helpful Webpages 9 -> 7 links from Nov 1 (content flag LINKS_SEVEN).
# "Committee Meeting Videos" (videos.html, which now links the Video Archives) replaces Latest + Video Archives; "Palm Hill Link"
# (palm-hill-link.html, which now starts with the current monthly issue) replaces Link Monthly + Link Archives. Old URLs stay live.
if globals().get("LINKS_SEVEN", False):
    _vo = (f'<div>• <a href="{ARCH}videos.html" style="color:{G};">Committee Meeting Videos - Latest</a></div>\n          '
           f'<div>• <a href="{ARCH}meeting-videos.html" style="color:{G};">Committee Meeting Video Archives</a></div>')
    assert s.count(_vo) == 1, "R81: video bullets not found"
    s = s.replace(_vo, f'<div>• <a href="{ARCH}videos.html" style="color:{G};">Committee Meeting Videos</a></div>')
    s, _n81 = re.subn(r'<div>• <a href="https://monthly-media\.com/newsletter_download\.php[^"]*" style="color:#3A6B1A;">Palm Hill Link Monthly</a></div>\s*'
                      r'<div>• <a href="' + re.escape(_lab.URL) + r'" style="color:#3A6B1A;">Palm Hill Link Archives</a></div>',
                      f'<div>• <a href="{_lab.URL}" style="color:{G};">Palm Hill Link</a></div>', s)
    assert _n81 == 1, "R81: Link Monthly + Link Archives bullets not found"
    _hw = s[s.index("Helpful Webpages</div>"):]; _hw = _hw[:_hw.index("</td>")]
    assert _hw.count("<div>• ") == 7 and "newsletter_download" not in _hw and "Videos - Latest" not in _hw, "R81/R25: Helpful Webpages must have the 7 approved links"
import title_dates as _td; s = _td.fix(s)  # STYLE-RULES.md R19 no dates in titles above a date line  # STYLE-RULES.md R14 Helpful Webpages
# STYLE-RULES R40 (Steven, Oct 17 7:23 PM; replaces R22): NO review/test stamp on any copy (previews and test copies included).
_ct = datetime.fromtimestamp(os.path.getmtime(CALF), ZoneInfo("America/New_York"))
s = re.sub(r"<!-- ph-review-stamp:start -->.*?<!-- ph-review-stamp:end -->", "", s, flags=re.S)
# STYLE-RULES R24 (Steven, Oct 16 11:54 PM): resident-facing footer line "Calendar check - October 16, 11:38 PM" from the pull this build used
CALCHECK = f"Calendar check - {FULL[_ct.month-1]} {_ct.day}, {(_ct.hour-1)%12+1}:{_ct:%M} {'AM' if _ct.hour<12 else 'PM'}"
# STYLE-RULES R25 (Steven, Oct 17 12:20 AM): simplified footer -- no archive-links row, no "For the latest details, always confirm
# ... official Palm Hill calendar." sentence; the Calendar check line alone, right-aligned, where that sentence was.
CALCHECK_P = f'<p class="ph-cal-check" style="font-size:11px;color:#888888;text-align:right;margin:12px 0 0 0;">{CALCHECK}</p>'
s = re.sub(r'\n?\s*<p class="ph-cal-check"[^>]*>[^<]*</p>', "", s)
_conf = re.compile(r'<p style="font-size:12px;color:#666666;font-style:italic;text-align:center;margin-top:16px;">\s*For the latest details, always confirm event times and updates on the\s*<a [^>]*>official Palm Hill calendar</a>\.\s*</p>')
assert len(_conf.findall(s)) == 1, "R25: footer calendar-confirm sentence not found exactly once"
s = _conf.sub(lambda m: CALCHECK_P, s)
assert "All Newsletter Archives →" not in s and "always confirm event times" not in s and s.count('class="ph-cal-check"') == 1, "R25 footer"
s = _sr.service_box_fit(s)  # STYLE-RULES R27: footer service-request lines on one line at desktop width
(REPO / "builder/calendar-pull").mkdir(exist_ok=True)
(REPO / f"builder/calendar-pull/{ISSUE}.json").write_text(json.dumps({"calendar_file": os.path.basename(CALF), "pulled_at": _ct.isoformat(), "footer": CALCHECK}, indent=1) + "\n")
_sr_dyk.assert_no_stamp(s, OUTF.name)  # R40
# STYLE-RULES R41/R43 (Steven, Oct 17 10:29 / 10:33 PM): '<Singular noun> Archives →' on every newsletter archive link
# (seed 'Past President Messages →' / 'Past Shareholders Reports →' -> President's Message / Shareholders Report Archives →).
s = _sr.assert_archive_labels(_sr.archive_labels(s), OUTF.name)
s = _sr.assert_source_credits(s, OUTF.name)
s = _sr.assert_community_stories(s, OUTF.name, COMMUNITY_STORIES_OMIT_APPROVED)  # R45
s = _sr.assert_event_sources(s, OUTF.name)  # R48 (Steven, Oct 18 12:31 AM): event rows need Calendar/RPM/Agenda  # STYLE-RULES L27/L29: linked short 'Webmaster', no dates on Source credits
# STYLE-RULES R18/R60 (Steven Oct 21 8:34 PM): root-cause fix -- the Oct 25 builder never ran summary_trim (Oct 18 ran it in
# make_live_preview/publish), so notices showed their full text. Trim here, then guard (scripts/check_notices.py) after writing.
sys.path.insert(0, SCRIPTS); import summary_trim as _st
_um = _st.unmatched(s)  # R18b: report every saved trim that no longer matches; a current-issue one stops the build
print(f"R18b summary_trim: {len(_um)} saved trim(s) not in this issue" + "".join(f"\n  unmatched{' (CURRENT ISSUE)' if c else ''}: {pre[:60]!r}" for pre, u, c in _um))
for _pre, _u, _c in _um:
    if _c: _todo(f"R18b: saved trim {_pre[:60]!r} no longer matches its item ({_u}); update summary_trim.SHORT")
s = _st.trim(s)
import check_notices as _cn; _cnf = _cn.static(s)
if _cnf: raise SystemExit("R60: " + "; ".join(_cnf))
# STYLE-RULES R42: one source email = one Community Notice (source-to-sections map; split / missing section fails the build)
import source_sections as _ss
_r42 = _ss.check_issue(s)
if _r42: raise SystemExit("R42: " + "; ".join(_r42))
# STYLE-RULES R62/R62b (Steven Oct 23 6:38 PM / Oct 24 1:34 PM): meetings rows show the agenda/report date, no TBC note.
# The expected wording is issue data (content file MEETING_ROW_CHECKS); A4 (R64d): each check reads its own row only.
import re as _re62
for _mc in C.MEETING_ROW_CHECKS:
    _mi = s.find(_mc["start"]); _mt = _re62.sub(r"<[^>]+>", " ", s[_mi:][:_mc["span"]]) if _mi >= 0 else ""
    _mt = _mt[:_mt.find("Source")] if "Source" in _mt else _mt
    if not (all(x in _mt for x in _mc["need"]) and not any(x in _mt for x in _mc["never"])):
        raise SystemExit(f"{_mc['rule']}: meetings row must show {_mc['need']} and not {_mc['never']}: " + " ".join(_mt.split())[:200])
# STYLE-RULES R60b (Steven Oct 24 11:39 AM): Bill Bender notice title exact, Source "Bill Bender email" linked to its flyer page
_hs = _cn.section(s); _hi = _hs.find(">" + HOLIDAY_TITLE + "<")
if _hi < 0: raise SystemExit(f"R60b: Community Notice title {HOLIDAY_TITLE!r} not found")
_he = _hs.find('<tr style="background:', _hi); _hr = _hs[_hi:_he if _he > 0 else len(_hs)]
if f'Source: <a href="{BASE + HOLIDAY_PAGE}"' not in _hr or f">{C.HOLIDAY_SOURCE_LABEL}</a>" not in _hr: raise SystemExit(f"R60b: {HOLIDAY_TITLE!r} needs Source: {C.HOLIDAY_SOURCE_LABEL} linked to " + HOLIDAY_PAGE)
# STYLE-RULES R60c (Steven Oct 24 1:27 PM): ice machine notice -- exact title, 3rd notice (right after Bill Bender), Source
# "Oct P&E Committee Report" linked to the Oct 14 P&E page, More -> its own notice page
# R60c (ice machine notice 3rd, right after Bill Bender; Source: Oct P&E Committee Report) -- content file R60C_ICE_NOTICE (Oct 25 only).
if C.R60C_ICE_NOTICE:
    _ii = _hs.find(">" + ICE_TITLE + "<")
    if _ii < 0: raise SystemExit(f"R60c: Community Notice title {ICE_TITLE!r} not found")
    _ie = _hs.find('<tr style="background:', _ii); _ir = _hs[_ii:_ie if _ie > 0 else len(_hs)]
    if f'Source: <a href="{BASE + PE_1014_PAGE}"' not in _ir or f">{C.ICE_SOURCE_LABEL.replace('&', '&amp;')}</a>" not in _ir and f">{C.ICE_SOURCE_LABEL}</a>" not in _ir: raise SystemExit(f"R60c: ice machine notice needs Source: {C.ICE_SOURCE_LABEL} linked to " + PE_1014_PAGE)
    if not re.search(r'href="' + re.escape(BASE + ICE_PAGE) + r'"[^>]*>More →', _ir): raise SystemExit("R60c: ice machine notice needs More → " + ICE_PAGE)
    _tt = re.findall(r'font-weight:bold;color:#333333;text-align:left;padding-right:8px;">([^<]+)<', _hs)
    if len(_tt) < 3 or _tt[2] != ICE_TITLE or _hs.find(">" + HOLIDAY_TITLE + "<") > _ii: raise SystemExit(f"R60c: ice machine notice must be 3rd, right after Bill Bender: {_tt[:4]}")
# R1 (Steven Oct 24 12:18 PM): normalize EVERY Listen button in the issue (incl. sections carried from the seed) to the shared inset
def _r1_inset(m):
    a = m.group(0)
    if LISTEN_INSET in a: return a
    return re.sub(r'^<a ([^>]*?)style="([^"]*)"', lambda k: f'<a {k.group(1)}style="{k.group(2).rstrip(";")};white-space:nowrap;display:inline-block;{LISTEN_INSET}"', a, count=1)
s = re.sub(r'<a [^>]*>(?:<img[^>]*>)?\s*Listen\s*</a>', _r1_inset, s)
assert all(LISTEN_INSET in m.group(0) for m in re.finditer(r'<a [^>]*>(?:<img[^>]*>)?\s*Listen\s*</a>', s)), "R1 Listen inset missing"
# STYLE-RULES R85 (Steven Oct 27 2026 12:25 AM): from TEL_FROM on, every printed phone number is a tel: link (preview -> SEND).
sys.path.insert(0, SCRIPTS); import tel_links as _tel
if _tel.applies(ISSUE):
    s = _tel.linkify(s)
    if _tel.find_bare(s)[0] or _tel.tel_mismatches(s): raise SystemExit(f"R85: bare/mismatched phone in NL: {_tel.find_bare(s)} {_tel.tel_mismatches(s)}")
OUTF.write_text(s, encoding="utf-8")
_cn.check(str(OUTF))  # R60 rendered 3-line guard at 390/660px
# STYLE-RULES R76 (Steven, Oct 25 2026 9:29 AM): from listen_settings v2_from on, every page this NL links with ?listen=1
# gets the v2 listen block (big "Tap to listen" bar when autoplay is blocked). Script block only; R10 locked pages untouched.
# The NL itself (preview -> SEND) never carries a script.
sys.path.insert(0, SCRIPTS); import page_listen as _plv
if "<script" in s.lower(): raise SystemExit("R76: the newsletter (preview/SEND) must not contain any <script>; email copies are plain links")
if _plv.v2_for(ISSUE):
    _r10 = set(_sr_dyk.R10_LOCKED_SHA256)
    for _rel in sorted(set(re.findall(r'href="(?:https://palmhillnews\.vercel\.app)?/?pages/([^"?#]+\.html)\?(?:[^"]*&)?listen=1', s))):
        _f = PAGES / _rel
        if "pages/" + _rel in _r10 or not _f.exists(): continue
        _t = _f.read_text(encoding="utf-8"); _n = _plv.upgrade(_t)
        if _n != _t: _f.write_text(_n, encoding="utf-8"); print("R76 v2 listen:", _rel)
sys.path.insert(0, SCRIPTS); import check_listen_coverage as _lc; _lc.require_since(_R49_T0)  # R49 (Steven, Oct 18 12:41 AM): required step
_lc.require_nl(OUTF)  # R49b (Steven, Oct 18 2:05 AM): every ?listen=1 link in this NL opens a page whose Listen starts reading
# STYLE-RULES.md R15: monthly Link save (new Palm Hill Link PDF -> Vercel), non-fatal
import subprocess as _sp2; _lr = _sp2.run([sys.executable, str(REPO / "scripts/fetch_link_pdf.py")], capture_output=True, text=True); print((_lr.stdout or _lr.stderr).strip()[-400:])
json.dump({"calendar_file": CALF, "meetings": [(e["date"], e["name"]) for e in meetings], "this_week": [(e["date"], e["name"]) for e in this_week],
           "upcoming": [(e["date"], e["name"]) for e in upcoming], "stamp": stamp,
           **({"all_events": [(e["date"], e["name"]) for e in all_events]} if _AE else {})}, open(ROOT / f"build-audit-{C.SHORT}.json", "w"), indent=1)
print("wrote", OUTF, "| meetings", len(meetings), "| this week", len(this_week), "| upcoming", len(upcoming))
# STYLE-RULES R64 (A2, Steven-approved Oct 24 2:26 PM): the Oct 25 locked checks run on every build and stop it on any FAIL
_rc = _sp2.run([sys.executable, str(HERE / "run_checks.py"), str(OUTF)], capture_output=True, text=True)
print((_rc.stdout or "").strip().splitlines()[-1:] or _rc.stderr[-400:])
if _rc.returncode != 0: _todo(f"R64: run_checks ({ISSUE}) FAIL\n" + "\n".join(l for l in _rc.stdout.splitlines() if "FAIL" in l or l.startswith("    why")) + _rc.stderr[-600:])

# Steven Oct 20 4:33 PM: preview builds refresh the archive pages too (the story row shows on Community Stories before publish)
import subprocess as _sp3
_ba = _sp3.run(["node", "scripts/build_archive.js"], cwd=str(REPO), capture_output=True, text=True)
print("build_archive:", (_ba.stdout or "").strip()[-300:], (_ba.stderr or "").strip()[-300:]); assert _ba.returncode == 0, "build_archive.js failed"
_sr_dyk.assert_r10_locked_pages(REPO)  # R10: locked as-sent pages unchanged (byte pin)
_sr_dyk.assert_rules_dyk_archive((REPO / "pages/archive/did-you-know.html").read_text(encoding="utf-8"), _DYK_ROWS[0]["id"], _DYK3_TEASER)  # R66b
_sr_dyk.assert_rules_dyk_archive((REPO / "pages/archive/did-you-know.html").read_text(encoding="utf-8"), "traffic-rules", _TR_TEASER)  # R66c
_ca = (REPO / "pages/archive/community-stories.html").read_text(encoding="utf-8")
if STORY: ARCHIVE_BACKED.append(("community-stories.html", STORY["page"]))
for _ap, _pg in ARCHIVE_BACKED:  # R59 guard: every archive-backed issue item is on its archive page and the page exists
    assert (PAGES / _pg).exists(), f"R59: {_pg} missing"
    assert _pg in (PAGES / "archive" / _ap).read_text(encoding="utf-8"), f"R59: {_pg} not on archive/{_ap}"
    assert (BASE + _pg) in s, f"R59: issue does not link the final URL {_pg}"
print("R59 archive-backed items OK:", ARCHIVE_BACKED)
assert not STORY or STORY["page"] in _ca, "R45: the issue's story is not on the Community Stories archive page"
# Local review copy (D:\PHNEWS\<week>\, fixed names): the story More → / Listen and Story Archives → point to sibling files in the
# same folder so they open from disk; the repo/Vercel copy keeps absolute URLs that resolve after publish.
# R58 (Steven Oct 21 11:24 AM): Story Archives → = the canonical live archive page (the one Oct 18 + Main Archive use).
STORY_ARCHIVE_URL = ARCH + "community-stories.html"   # https://palmhillnews.vercel.app/pages/archive/community-stories.html
_sa = re.findall(r'href="([^"]+)"[^>]*>Story Archives →', s)
assert (not STORY or _sa) and all(u == STORY_ARCHIVE_URL for u in _sa), f"R58: Story Archives → must link {STORY_ARCHIVE_URL}, got {_sa}"
assert 'href="community-stories.html"' in (REPO / "pages/archive/main.html").read_text(encoding="utf-8"), "R58: Main Archive no longer links community-stories.html"
# Local review copy (D:\PHNEWS\<week>\, fixed names). The issue's story + Story Archives links open local copies that mirror the
# live paths: <story>.html and archive/community-stories.html (the canonical page, incl. this issue's story); every other
# root-relative link/asset in the local archive copy is made absolute to palmhillnews.vercel.app so it renders like the live page.
LOCAL = ROOT / f"local-{C.SHORT}"; LOCAL.mkdir(exist_ok=True); (LOCAL / "archive").mkdir(exist_ok=True)
_loc = (s.replace(BASE + STORY["page"], STORY["page"]) if STORY else s).replace(STORY_ARCHIVE_URL, "archive/community-stories.html")
(LOCAL / f"PHNEWS-{ISSUE}-preview.html").write_text(_loc, encoding="utf-8")
import shutil as _sh
if STORY: _sh.copy(PAGES / STORY["page"], LOCAL / STORY["page"])
_lca = re.sub(r'(href|src)="/(?!/)', r'\1="https://palmhillnews.vercel.app/', _ca)
_lca = re.sub(r'href="(?!https?:|#|mailto:)([^"/][^"]*\.html)"', r'href="https://palmhillnews.vercel.app/pages/archive/\1"', _lca)
for _u in (("https://palmhillnews.vercel.app/pages/" + STORY["page"], "https://palmhillnews.vercel.app/pages/archive/../" + STORY["page"]) if STORY else ()):
    _lca = _lca.replace('href="' + _u, 'href="../' + STORY["page"])
(LOCAL / "archive/community-stories.html").write_text(_lca, encoding="utf-8")
_old = LOCAL / "community-stories.html"
if _old.exists(): _old.unlink()   # local review scratch copy only (box), replaced by archive/community-stories.html
assert not STORY or ('href="../' + STORY["page"]) in _lca, "R58: local archive copy must list and link this issue's story"
_ld = (REPO / "pages/archive/did-you-know.html").read_text(encoding="utf-8")
_ld = re.sub(r'(href|src)="/(?!/)', r'\1="https://palmhillnews.vercel.app/', _ld)
_ld = re.sub(r'href="(?!https?:|#|mailto:)([^"/][^"]*\.html)"', r'href="https://palmhillnews.vercel.app/pages/archive/\1"', _ld)
_loc = (LOCAL / f"PHNEWS-{ISSUE}-preview.html").read_text(encoding="utf-8").replace(ARCH + "did-you-know.html", "archive/did-you-know.html")
for _ap, _pg in ARCHIVE_BACKED:
    if _ap != "did-you-know.html": continue
    _sh.copy(PAGES / _pg, LOCAL / _pg)
    _loc = _loc.replace(BASE + _pg, _pg)
    for _u in ("https://palmhillnews.vercel.app/pages/" + _pg, "https://palmhillnews.vercel.app/pages/archive/../" + _pg): _ld = _ld.replace('href="' + _u, 'href="../' + _pg)
    assert 'href="../' + _pg in _ld, f"R59: local DYK archive copy missing {_pg}"
(LOCAL / "archive/did-you-know.html").write_text(_ld, encoding="utf-8"); (LOCAL / f"PHNEWS-{ISSUE}-preview.html").write_text(_loc, encoding="utf-8")
print("local review copy:", sorted(str(p.relative_to(LOCAL)) for p in LOCAL.rglob("*") if p.is_file()))
print("DRY-RUN TODOs:", len(DRYRUN_TODO)) if DRYRUN else None
# STYLE-RULES R70 (Steven, Oct 24 2026 9:56 PM; PR #139, carried into the shared builder in batch 4): the live preview page is synced
# from this build's local copy (never hand-copied), and its Calendar check + masthead time must equal the SEND copy's
# (build with PHNEWS_CAL_OFFLINE=1 + PHNEWS_BUILD_STAMP to match a SEND). No SEND file yet (e.g. a Nov 1 dry run) = nothing to compare.
import check_preview_send_stamp as _r70
(REPO / f"pages/previews/{ISSUE}").mkdir(parents=True, exist_ok=True)
print("R70 synced:", _r70.sync(LOCAL / f"PHNEWS-{ISSUE}-preview.html", REPO, ISSUE))
_r70f, _ = _r70.check(ISSUE, ROOT, REPO)
if _r70f: raise SystemExit("; ".join(_r70f))
# R85: Nov 1+ generated pages this issue links (date prefix >= TEL_FROM) get the same tel: links; older published pages untouched.
if _tel.applies(ISSUE):
    for _u in sorted(set(re.findall(r'palmhillnews\.vercel\.app/pages/([^"?#]+\.html)', s))):
        _f = PAGES / _u
        if _f.exists() and _tel.dated_from(_u):
            _t = _f.read_text(encoding="utf-8"); _n = _tel.linkify(_t)
            if _n != _t: _f.write_text(_n, encoding="utf-8"); print("R85 tel links:", _u)
