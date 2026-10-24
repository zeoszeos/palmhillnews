"""PHNEWS Oct 25, 2026 (Vol. 1, No. 15) DRAFT builder (cloned from build_oct18.py Oct 20 2026; same shell/seed, windows shifted one week). Box-side, draft only; sends/publishes nothing.
Input: ../source/PHNEWS-2026-10-11-FINAL-REVIEW-as-sent-omen.html (Oct 11 as sent, untouched) as the shell,
       ../data/cal-YYYYMMDD.json (Palm Hill calendar = source of truth for events/meetings; RPM never adds/overrides),
       editorial content below (each item names its source).
Saturday refresh: re-fetch calendar (fetch_calendar.sh), update NOTICES / MANAGER / Tony FB wording, rerun.
Output: ../PHNEWS-2026-10-18-preview.html
"""
import json, os, re, sys, glob, time
_R49_T0 = time.time() - 1  # STYLE-RULES R49: pages written by this run get the Listen-coverage check at the end
from datetime import date, datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
SEED = ROOT / "source/PHNEWS-2026-10-18-seed-20261014.html"
# STYLE-RULES R21 (Steven, Oct 16 11:32 PM): re-pull the calendar right before every proof/publish build (prints the diff).
# PHNEWS_CAL_OFFLINE=1 only for re-renders that must reproduce an already-pulled snapshot.
if os.environ.get("PHNEWS_CAL_OFFLINE") != "1":
    sys.path.insert(0, "/workspace/oct18-batch/scripts"); import pull_calendar as _pc
    _pc.pull(str(ROOT / "data"), "2026-10-18", "2026-12-24")
CALF = sorted(glob.glob(str(ROOT / "data/cal-*.json")))[-1]
OUTF = ROOT / "PHNEWS-2026-10-25-preview.html"
ISSUE = "2026-10-25"
THIS_WEEK = ("2026-10-25", "2026-10-31")
UPCOMING = ("2026-11-01", "2026-11-22")      # ~3 weeks (Oct 9 rule), starts after This Week
RECURRING = ("2026-10-25", "2026-11-23")
MEETINGS = ("2026-10-25", "2026-11-24")      # 30 days inclusive
BASE = "https://palmhillnews.vercel.app/pages/"; CAL = "https://www.palmhillcountryclub.net/calendar-1/"
ARCH = BASE + "archive/"
SPK = "https://palmhillnews.vercel.app/assets/images/phnews/2026-10-04/speaker-read-aloud-green-gold-512-v3.png"
G = "#3A6B1A"
MON3 = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
FULL = ("January","February","March","April","May","June","July","August","September","October","November","December")

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
    if k in seen: continue
    seen.add(k); meetings.append(dict(e, name=nm))
# L09: Tony "Meetings" category stays out of This Week/Upcoming, except MasterPlan Team (L25, Oct 10).
MEETINGS_CAT_ALLOWED = {"Palm Hill MasterPlan Team"}
def evsel(w):
    return sorted([e for e in events if ok(e) and inw(e, w) and not e.get("recurring") and not is_cmte(e)
                   and e["name"] not in AS_RECURRING and e.get("category") != "CLOSURE" and not e.get("allDay")
                   and (e.get("category") != "Meetings" or e["name"] in MEETINGS_CAT_ALLOWED)],
                  key=lambda e: (e["date"], e["start"]))
this_week, upcoming = evsel(THIS_WEEK), evsel(UPCOMING)

# Event detail rewritten from the calendar "info" (no personal phone numbers or home addresses).
EVENT_DETAIL = {
    "Mount Dora Trip": "Bus loads at 8:00 AM for the arts and crafts festival, with an optional boat ride on the lake. $35 per seat, payable at coffee; the calendar shows about 12 seats left.",
    "Halloween Golf Cart Parade": "Line up at the North Clubhouse at 6:30 PM for the 7:00 PM parade to the South Clubhouse; it takes about 1½ hours. Charge golf-cart batteries fully.",
    "Halloween Dance Party": "Doors open at 6:15 PM with no assigned seating. The tickets are sold out as of now. Bring a treat to share for table-to-table trick-or-treating.",  # Steven Oct 17 10:29 PM: sold-out wording restored (Linda, Oct 8)
    "Senior Empowerment Luncheon": "The luncheon runs 10:00 AM to 1:00 PM; the room is booked from 9:15 AM for set-up. Pre-registration is required.",
    "North Clubhouse Craft Fair": "Crafters can rent a table for $20, 9:00 AM to 1:00 PM. See the club calendar for who to contact to book.",
    "Veterans Day Program": "Program at the South Clubhouse; check the club calendar for later details.",
    "Pot Luck Supper": "Doors open at 5:00 PM; dinner is at 5:30 PM. Bring your own table setup and drink.",
    "MESCO Spaghetti Dinner Fundraiser": "Doors open at 4:30 PM; dinner is served at 5:00 PM. The $12 donation covers bread and butter, salad, spaghetti and meatballs, dessert and coffee; BYOB for other drinks. Tickets are sold at both coffees until Monday morning, Nov 9; none at the door.",
    "Fall Festival": "Music and food trucks on the South Lawn and Patio.",
    "Bookclub:Foster by Claire Keegan": "Book club discussion of Foster by Claire Keegan.",
    "Bocce Party": "Sign up at either clubhouse or by calling Pat Foor or Joe Cothran. Join us for the fellowship and fun!",
}
EVENT_EXTRA_SRC = {"Halloween Golf Cart Parade": BASE + "2026-09-18-halloween-golf-cart-parade-notice.html",
                   "Halloween Dance Party": BASE + "2026-10-08-info-from-linda-notice.html"}
EVENT_LINK = {"Halloween Dance Party": ("More →", BASE + "2026-10-31-halloween-dance.html"),
              "Mount Dora Trip": ("More →", BASE + "2026-10-24-mount-dora-trip.html"),
              "MESCO Spaghetti Dinner Fundraiser": ("More →", BASE + "2026-11-14-mesco-spaghetti-dinner-fundraiser.html"),
              "Bocce Party": ("More →", BASE + "2026-10-28-bocce-party.html")}
# R21: full calendar listing text for the More → page. Personal phone numbers are not printed, EXCEPT on event pages Steven
# has explicitly OK'd (PHONE_OK_PAGES; Bocce Party approved Oct 16 11:37 PM). Issue summaries never carry them.
PHONE_OK_PAGES = {"Bocce Party"}
EVENT_PAGE = {"Bocce Party": ("2026-10-28-bocce-party.html",
    ["Sign up at either clubhouse or by calling Pat Foor (727-631-3372) or Joe Cothran (727-512-1185). Join us for the fellowship and fun!",  # PHONE_OK_PAGES
     "Rescheduled from 4:00 PM to 6:00 PM (6:00 to 7:00 PM)."]),
    # R21 calendar re-pull Sat Oct 17 1:47 PM: start moved 4:00 PM -> 5:00 PM; the More → page date line now comes from the calendar
    "MESCO Spaghetti Dinner Fundraiser": ("2026-11-14-mesco-spaghetti-dinner-fundraiser.html",
    ["Doors open at 4:30 PM; dinner is served at 5:00 PM. The $12 donation covers bread and butter, salad, spaghetti and meatballs, dessert and coffee; BYOB for other drinks. Tickets are sold at both coffees until Monday morning, Nov 9; none at the door."])}
assert not any(re.search(r"\d{3}-\d{3}-\d{4}", v) for v in EVENT_DETAIL.values() if v), "phone rule: no phone numbers in issue summaries"
# R21: events whose summary already carries the whole calendar listing (checked by hand Oct 16) - no More → page needed
INFO_COVERED = {"Halloween Golf Cart Parade", "Senior Empowerment Luncheon", "North Clubhouse Craft Fair", "Pot Luck Supper", "Fall Festival",
                "Veterans Day Program", "Bookclub:Foster by Claire Keegan"}
TITLE = {"Bookclub:Foster by Claire Keegan": "Book Club: Foster by Claire Keegan"}
# Oct 25: events new to the issue window (calendar re-pull Oct 20 2:40 PM). Detail = the calendar listing text (light edits only).
EVENT_DETAIL.update({
    "Taste of Golf": "Free. New golfers and residents welcome; golf teachers on each hole, treats and a hot dog on the Pro Shop patio. Sign up at the Pro Shop, North or South Clubhouse.",
    "Bookclub Lunch at Irish Pub": "Members and those joining book club only.",
    "December Cruise Information Meeting": "Information meeting for everyone going on the December cruise. Questions: Tony Ciaramitaro."})
EVENT_LINK["Taste of Golf"] = ("More →", BASE + "2026-10-14-taste-of-golf-notice.html")      # existing Webmaster copy page (gotwicz 1a13d9d5ef6e178f)
EVENT_EXTRA_SRC["Taste of Golf"] = BASE + "2026-10-14-taste-of-golf-notice.html"
INFO_COVERED |= {"Bookclub Lunch at Irish Pub", "December Cruise Information Meeting"}
TITLE["Bookclub Lunch at Irish Pub"] = "Book Club Lunch at Irish Pub"
# Calendar re-pull Oct 22 7:55 PM: new one-off Bridge Club (Oct 26, Pool Room South); detail = its calendar listing text verbatim
EVENT_DETAIL["Bridge Club"] = "Moved due to Haunted House"; INFO_COVERED.add("Bridge Club")
# STYLE-RULES R56 (Steven Oct 21 2026 10:44 AM, "middle path"): an event matched to a Webmaster/resident email notice shows calendar
# facts only; More → opens that notice page; no per-event page is generated or linked (already-published pages such as
# 2026-10-31-halloween-dance.html stay live, just unlinked). Source line stays Calendar + Webmaster (the notice).
MATCHED_NOTICE = dict(EVENT_EXTRA_SRC)
for _n, _u in MATCHED_NOTICE.items():
    EVENT_DETAIL.pop(_n, None); EVENT_PAGE.pop(_n, None); EVENT_LINK[_n] = ("More →", _u); INFO_COVERED.add(_n)

def bg(i): return "#EAF4E4" if i % 2 else "#FFFFFF"
def src_cal(extra=None):
    s = f'Source: <a href="{CAL}" style="color:{G};">Calendar</a>'
    if extra: s += f', <a href="{extra}" style="color:{G};">Webmaster</a>'
    return s
# Steven, Oct 16 (MEETING-SOURCES-COMPARE.md): Finance from agenda email (no Zoom link yet); Palm Hill dates for Nov conflicts, flagged TBC
MTG_EXTRA = [dict(  # Oct 25: Finance Oct 22 (agenda email) is past -> dropped; no newer Finance agenda in palmhillblast as of Oct 20 2:4x PM
             date="2026-11-18", start="13:00", name="Board of Directors Meeting", venue="Board Room South", note="(date to be confirmed)")]
MTG_NOTE = {("2026-11-10", "Buildings and Grounds Committee Meeting"): "(date to be confirmed)",
            }
# STYLE-RULES R62 (Steven Oct 23 6:38 PM): P&E next meeting = Elaine Cole's date (her Oct 14 report): Tuesday Nov 10, 12:30 PM;
# no "(date to be confirmed)". Data override only; her report page wording is untouched (her "a.m." stays as written).
MTG_OVERRIDE = {"Planning and Environmental Committee Meeting": dict(date="2026-11-10", start="12:30")}
for _e in meetings:
    _o = MTG_OVERRIDE.get(CANON.get(_e["name"], _e["name"]))
    if _o: _e.update(_o); _e.pop("note", None)
meetings = sorted(meetings + MTG_EXTRA, key=lambda e: (e["date"], e["start"]))
# R54 (Steven Oct 20 4:33 PM): no meeting listed twice -- one row per committee/board, the NEXT instance only. MTG_EXTRA rows
# (agenda/TBC additions) were appended after the calendar's one-per-committee pass, so Board Oct 28 (calendar) + Board Nov 18 (TBC) both showed.
def _mkey(e): return CANON.get(e["name"], e["name"]).lower().replace(" meeting", "").strip()
_seen = set(); _dropped = []
for _e in list(meetings):
    if _mkey(_e) in _seen: meetings.remove(_e); _dropped.append((_e["date"], _e["name"]))
    else: _seen.add(_mkey(_e))
print("R54 meetings dropped (already listed):", _dropped)
assert len({_mkey(e) for e in meetings}) == len(meetings), "R54: a committee/board meeting is listed twice"
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
            sys.path.insert(0, "/workspace/oct18-batch/scripts"); import meeting_zoom_page as _mzp
            (Path("/workspace/oct18-batch/pages") / d["zoom_page"]).write_text(_mzp.render(d), encoding="utf-8")
            e = dict(e, also=d["also"], agenda=nu, zoom=BASE + d["zoom_page"])
            L='style="font-size:14px;color:#666666;text-align:right;line-height:1.35;padding-top:1px;'
            out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:4px 8px;border-bottom:1px solid #ddd;"><table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">'
                f'<tr><td valign="top" align="left" style="font-size:15px;line-height:1.3;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">{escape(e["name"])}</td><td valign="top" align="right" style="font-size:14px;line-height:1.3;color:#666666;text-align:right;padding-top:1px;">{escape(e["venue"])}</td></tr>'
                f'<tr><td valign="top" align="left" style="font-size:14px;color:#666666;text-align:left;line-height:1.35;padding-top:1px;padding-right:10px;">{pdate(e["date"])}<span style="white-space:nowrap;"> • {ptime(e["start"])}</span></td><td valign="top" align="right" {L}"><div style="font-size:13px;line-height:1.35;color:#666666;white-space:nowrap;">{escape(e["also"])}</div></td></tr>'
                f'<tr><td valign="top" align="left" style="font-size:14px;line-height:1.35;text-align:left;white-space:nowrap;padding-top:1px;padding-right:10px;"><a href="{e["agenda"]}" style="color:{G};white-space:nowrap;">Agenda →</a>&nbsp;&nbsp;&nbsp;<a href="{e["zoom"]}" style="color:{G};white-space:nowrap;">Zoom →</a></td><td valign="top" align="right" {L}white-space:nowrap;"><span style="white-space:nowrap;">{srcx}</span></td></tr></table></td></tr>')
            continue
        out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:4px 8px;border-bottom:1px solid #ddd;"><table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation"><tr><td valign="top" align="left" style="font-size:15px;line-height:1.3;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">{escape(e["name"])}</td><td valign="top" align="right" style="font-size:14px;line-height:1.3;color:#666666;text-align:right;padding-top:1px;">{escape(VENUE.get(e["venue"], e["venue"]))}</td></tr><tr><td valign="top" align="left" style="font-size:14px;color:#666666;text-align:left;line-height:1.35;padding-top:1px;padding-right:10px;">{pdate(e["date"])}<span style="white-space:nowrap;"> • {ptime(e["start"])}</span>{nt}</td><td valign="top" align="right" style="font-size:14px;color:#666666;text-align:right;white-space:nowrap;line-height:1.35;padding-top:1px;"><span style="white-space:nowrap;">{srcx}</span></td></tr></table></td></tr>')
    return "".join(out)
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import style_rules as _sr56
def ev_rows(evs):
    out = []
    assert all(v[0] == "More →" for v in EVENT_LINK.values()), "STYLE-RULES R23: event/notice links say More →"
    for e in evs:  # STYLE-RULES R21 guard
        if (e.get("info") or "").strip() and e["name"] not in EVENT_LINK and e["name"] not in INFO_COVERED:
            raise SystemExit(f"R21: {e['date']} {e['name']} has calendar listing text but no More → page (add EVENT_PAGE/EVENT_LINK or INFO_COVERED)")
        if e["name"] in EVENT_PAGE:
            import event_page as _ep; fn, paras = EVENT_PAGE[e["name"]]
            if e["name"] not in PHONE_OK_PAGES and any(re.search(r"\d{3}-\d{3}-\d{4}", x) for x in paras): raise SystemExit(f"phone rule: {e['name']} page has a phone number without Steven's OK (PHONE_OK_PAGES)")
            dl = f"{pdate(e['date'])} • {ptime(e['start'])}" + (f" to {ptime(e['end'])}" if e.get("end") else "") + f" • {VENUE.get(e['venue'], e['venue'])}"
            (Path("/workspace/oct18-batch/pages") / fn).write_text(_ep.render(e["name"], dl, paras), encoding="utf-8")
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
            _u = MATCHED_NOTICE[e["name"]]; _lp = Path("/workspace/oct18-batch/pages") / _u.rsplit("/", 1)[1]
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
# (title, text, source label, source href or None, listen href or None)
TONY_FB_PLACEHOLDER = False  # set False Saturday once Tony's wording (due Fri Oct 16, palmhillblast) is pasted below
TONY_FB = ("Join the Palm Hill Residents Group on Facebook", None)  # Tony's wording arrived Fri Oct 16 (palmhillblast); verbatim
FBURL = "https://www.facebook.com/groups/720846344400510"
# R60 (Steven Oct 21 8:34 PM): live published Oct 18 URLs (publish_oct18 MAP), never pages/previews/ or #listen-pending
FBQR = "https://palmhillnews.vercel.app/pages/assets/phnews/2026-10-18/fb-group-qr.png"
FBPAGE_NOTICE = "https://palmhillnews.vercel.app/pages/2026-10-18-facebook-group-notice.html"
FBPAGE_DYK = "https://palmhillnews.vercel.app/pages/2026-10-18-did-you-know-facebook-group.html"
FB_LISTEN = "https://palmhillnews.vercel.app/pages/2026-10-18-notice-join-the-palm-hill-residents-group-on-facebook.html?listen=1"  # as in the approved Oct 18 issue
TONY_FB_TXT = ('Palm Hill now has a private Facebook group just for residents, with park news, event reminders and photos posted by the admins (comments are turned off). '
    'Every request is checked against the member directory, so use the address and email the Office has for you, answer all 3 questions, or Facebook will turn the request down. '
    f'Search Facebook for &quot;Palm Hill Country Club - Residents Only Group&quot; or join here: <a href="{FBURL}" style="color:{G};">{FBURL}</a>'
    f'<br><a href="{FBPAGE_NOTICE}" style="color:{G};font-size:14px;">Full notice with QR code to scan →</a>')
# ---------- STYLE-RULES L27/L29 (Steven, Oct 17 11:51 PM): Webmaster source copies ----------
# Every Webmaster Source credit is the linked word "Webmaster" (no date, no sender) opening a copy of the source email.
# These three Webmaster emails (noreply@palmhillcountryclub.net, gotwicz Gmail) had no copy page; scripts/notice_page.py renders
# them in the info-from-linda shell, verbatim (only blank lines, &nbsp; runs, zero-width spaces and the unsubscribe footer dropped).
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import notice_page as _np
WM_COPY_PANCAKES = "2026-10-15-november-pancakes-and-coffee-volunteers-notice.html"   # gotwicz 1a13ffdbd4141bdd
WM_COPY_SHUFFLE = "2026-10-12-shuffleboard-information-notice.html"                   # gotwicz 1a13200e1dcdde48
WM_COPY_GOLF = "2026-10-14-taste-of-golf-notice.html"                                  # gotwicz 1a13d9d5ef6e178f
WM_COPY_SANIT = "2026-10-22-sanitation-field-notice.html"                            # gotwicz 1a164e859613b210 (Steven Oct 23 5:09 AM, A)
WM_COPY_COUPLES = "2026-10-20-couples-golf-league-notice.html"                        # gotwicz 1a15c9dca2aac0fc (Steven Oct 23 5:09 AM, C)
WM_COPY_LIBRARY = "2026-10-22-library-closed-notice.html"                             # gotwicz 1a164ed6011d050d (Steven Oct 23 6:38 PM)
WM_COPY_STOP = "2026-10-21-stop-sign-rules-notice.html"                                # gotwicz 1a15eb6fba34f8ab (Steven Oct 23 6:38 PM; RPM duplicate ignored)
WM_COPY_SOUTHREC = "2026-10-21-south-rec-club-seeking-officers-notice.html"            # gotwicz 1a15eb2704b3f9a0 (Steven Oct 23 6:38 PM; image-only email)
SOUTHREC_IMG = "https://www.palmhillcountryclub.net/editor_upload/Image/South_Recreation_Club_Election_Smaller.jpeg"
WM_COPIES = [
    (WM_COPY_LIBRARY, "Library Closed starting the week of October 26th", "Thursday, Oct 22, 2026, 1:48 PM ET", [
        ("p", "We are very excited to offer our residents and their guests the experience of our Haunted Library again this year.  Our designer, Duane Smathers, along with Judy Flannigan, will be creating another Library that will definitely reflect the Halloween spirit."),
        ("p", "As additional animatronics will be featured, they will need the upcoming week to transform the room.   Therefore the Library will be closed beginning MONDAY, OCTOBER 26TH through SUNDAY, NOVEMBER 1ST."),
        ("p", "If you would like to pick up a book, please do so by Sunday the 25th.  To return books during that week,  Heidi Weeks has kindly placed a box in our main Recreation Hall near the curtain by the library for that purpose.   We so appreciate everyone's understanding and patience."),
        ("p", "Thank you,"),
        ("p", "Mollie Cardno"), ("p", "Inside Entertainment"), ("p", "North Recreation Hall")]),
    (WM_COPY_STOP, "Please observe important stop sign rules", "Wednesday, Oct 21, 2026, 9:42 AM ET", [
        ("p", "We hope this message finds you well. We are writing to remind all residents and their guests to please observe the posted speed limits and come to a complete stop at all stop signs throughout our community."),
        ("p", "As our northern friends join us for the season, there will be more vehicles on the road, making it even more important that we all follow these safety guidelines."),
        ("p", "The safety of our residents, their families, and guests is our top priority. Many of our neighbors enjoy walking, jogging, and cycling throughout Palm Hill, and we want to ensure everyone can do so safely."),
        ("p", "Please remember to:"),
        ("ul", ["Observe the posted speed limit at all times",
                "Come to a complete stop at all stop signs whether you are in a car, on a bike or in a golf cart",
                "Watch for pedestrians, cyclists, and golf carts",
                "Remind your guests and service providers of these safety rules"]),
        ("p", "Your cooperation in maintaining a safe environment for everyone is greatly appreciated. If you have any questions or concerns, please don't hesitate to contact the office at (727) 581-8729."),
        ("p", "Thank you for your attention to this important matter."),
        ("p", "Sincerely,"),
        ("p", "Resource Property Management, Inc. on behalf of Home Owners of Palm Hill, Inc")]),
    (WM_COPY_SOUTHREC, "2027 South Rec Club Seeking Officers", "Wednesday, Oct 21, 2026, 9:34 AM ET", [
        # the email body is one flyer image (no text); the flyer is shown as sent, alt text = its words (personal phone numbers left out)
        ("img", (SOUTHREC_IMG, "South Recreation Club. 2027 Election. Make a Difference! The South Recreation Club has the following positions available for the 2027 election: Inside Entertainment, Outside Entertainment, Bazaar Director. Deadline: December 2, 2026 at the close of the business meeting. If you're interested, please contact a search committee member: Joan Dougall, Martha Ladd, Tony Ciaramitaro. Get Involved... Help Keep Our Club Great! Thank you!")),
        ("p", "The South Recreation Club has the following positions available for the 2027 election: Inside Entertainment, Outside Entertainment, Bazaar Director."),
        ("p", "DEADLINE: December 2, 2026 at the close of the business meeting."),
        ("p", "If you're interested, please contact a search committee member: Joan Dougall, Martha Ladd, Tony Ciaramitaro.")]),
    (WM_COPY_SANIT, "Help with maintaining Sanitation Field", "Thursday, Oct 22, 2026, 1:42 PM ET", [
        ("p", "Dear Palm Hill Residents,"),
        ("p", "We need your help in maintaining our sanitation field and keeping disposal areas properly organized."),
        ("p", "Brush Dumpster - Brush Only: Please remember that the brush dumpster is designated for brush and yard waste ONLY. Do not place any trash, plastic bags, or other materials in this dumpster or on the brush pile near it. Only natural brush and plant material should be disposed of here."),
        ("p", "Broken Pavers: If you have broken pavers, please do not leave them in the sanitation field. All broken pavers and similar construction debris should be placed in the construction dumpster."),
        ("p", "Proper sorting helps us manage waste efficiently and keeps costs down for our community. Thank you for your cooperation in following these guidelines."),
        ("p", "If you have questions about where to dispose of specific items, please contact the office at (727) 581-8729."),
        ("p", "Thank you for helping keep Palm Hill clean and well-maintained."),
        ("p", "Sincerely,"),
        ("p", "Resource Property Management, Inc. on behalf of Home Owners of Palm Hill, Inc")]),
    (WM_COPY_COUPLES, "Couples Golf Leagur", "Tuesday, Oct 20, 2026, 11:59 PM ET", [   # subject as sent
        ("p", "Couples Golf League will be starting November 5th. A sign-up sheet for play and a Host Sign-up sheet, for the whole season, is posted at the Pro Shop. Couples League needs Hosting Volunteers."),
        ("p", "For Palm Hill Couples interested, please sign up and reach out to Mike McCarthy with any questions."),
        ("p", "Look forward to a fun Golf Season!"),
        ("p", "Julie Hughes")]),
    (WM_COPY_PANCAKES, "November Pancakes & Coffee Volunteers", "Thursday, Oct 15, 2026, 10:29 AM ET", [
        ("p", "An announcing chairperson is needed for the month of November for the North Club House coffees."),
        ("p", "8 volunteers are needed for November coffees in the North."),
        ("p", "14 volunteers are needed for pancakes on November 14th - arrival time is 7:30 AM"),
        ("p", "Please use the sign up sheets on the bulletin board at the north clubhouse."),
        ("p", "Thank you,"),
        ("p", "Mollie Cardon")]),
    (WM_COPY_SHUFFLE, "Shuffleboard Information", "Monday, Oct 12, 2026, 5:24 PM ET", [
        ("h", "With shuffleboard season approaching, just a few reminders:"),
        ("ul", ["For safety reasons, please do not walk on the courts.",
                "After use, return the disc to holders, and place under benches.",
                "After use, return cue sticks to wall hangers.",
                "When leaving the buildings, close the windows and turn off the lights and fans.",
                "All persons under 18 years old must be accompanied by an adult.",
                "No smoking.",
                "For safety, wear closed toe shoes"]),
        ("h", "Additional information for the north courts with embedded beads:"),
        ("ul", ["Do not drop the disc directly onto the beaded surface, as that can dislodge the beads. Place the disc outside of the playing area and push them forward into the kitchen to start play."]),
        ("p", "Thank you from the Shuffleboard Club.")]),
    (WM_COPY_GOLF, "Taste of Golf", "Wednesday, Oct 14, 2026, 11:31 PM ET", [
        ("h", "Palm Hill Country Club"),
        ("h", "\u201cTaste of Golf\u201d"),
        ("h", "November 18, 2026; 10 AM"),
        ("p", "Welcome New Golfers & Residents for a fun filled day to learn & play golf."),
        ("p", "Meet at Pro Shop.  Event is FREE."),
        ("p", "Golf teachers on each hole, teaching golf basics: Golf etiquette, Warm-up, Driving, Chipping, Putting, Reading the green."),
        ("p", "Not a golfer\u2026.Come walk & watch & enjoy the beauty of the course."),
        ("p", "Treats on each hole & enjoy a Hot Dog on the Pro Shop patio!"),
        ("p", "Join in on the fun and meet new friends!"),
        ("p", "Sign Up sheets:  Pro Shop, North Clubhouse, South Clubhouse"),
        ("p", "Questions contact:"),
        ("p", "Caroline Zimmerman")]),
]
# Steven Oct 24 11:38 AM: Bill Bender's flyer (gotwicz, bbenderfla@outlook.com, Fri Oct 23 11:38 PM ET, "Please add to your news
# letter....", attachment "Mari, Card.jpg"; the message is in Spam and stays there). Page = flyer image + its text as printed.
# Bill's email/phone are printed on the flyer as the program contact, so they are kept.
HOLIDAY_PAGE = "2026-10-23-holiday-greeting-distribution-plan.html"
HOLIDAY_IMG = "/pages/assets/notices/2026-10-23-holiday-greeting-distribution-plan.jpg"  # copy of /workspace/sweep/1024-0930/bill-bender-mari-card.jpg
HOLIDAY_BLOCKS = [
    ("img", (HOLIDAY_IMG, "Holiday Greeting Distribution Plan flyer")),
    ("h", "Holiday Greeting Distribution Plan"),
    ("p", "A simple way for Palm Hill residents to send holiday greetings to friends and neighbors within the community."),
    ("h", "Purpose"),
    ("p", "To offer shareholders a distribution plan for holiday greetings at Hanukkah and Christmas time. Limited to addresses within Palm Hill that do not require postage."),
    ("h", "How It Works"),
    ("ul", ["Send 1 or 1100 greetings — there is no minimum or limit.",
            "Save the cost of outside postage, currently about $.82 per item in the U.S.",
            "Any resident can participate, limited to greetings within Palm Hill.",
            "Address greetings as you would a normal letter: name and address.",
            "Greetings will be deposited in specially designated drop boxes in the clubhouses. Deposits can be made anytime the boxes are available.",
            "Boxes will be monitored and emptied as necessary. Contents will be stored until holiday week.",
            "If you are leaving, please drop off before you depart.  If you are not on site, please contact Bill for instructions."]),
    ("h", "Important Notes"),
    ("ul", ["Amazon and Wal-Mart have online offerings now!",
            "Sorting will take place as often as necessary by our committee.",
            "Please clearly mark on the envelope any cards for Hanukkah to ease sorting."]),
    ("h", "Distribution"),
    ("ul", ["Distribution will be made by residents approximately 1 week before Hanukkah or Christmas.",
            "In addition to our 1100 homes, cards will also be accepted for the administration offices and maintenance employees.",
            "Canadian and Northern friends: feel free to reach out for suggestions on getting your cards to us."]),
    ("h", "Volunteers Welcome"),
    ("p", "As the program develops, additional folks will be needed for various tasks. Please notify us if you would like to help."),
    ("h", "Contact"),
    ("p", "Comments or questions should be directed to:"),
    ("p", "Bill Bender"), ("p", "BBenderfla@outlook.com"), ("p", "315-520-0263"),
    ("h", "Friends Greeting Friends"),
    ("p", "This program is solely to encourage friends and neighbors to connect during the holiday season — friends greeting friends. Share your thoughts."),
    ("p", "Thank you... Let’s Succeed!!!!!"),
    ("p", "Bill Bender, Kate Wesoloowski, & Mike Okash")]
(Path("/workspace/oct18-batch/pages") / HOLIDAY_PAGE).write_text(_np.render("Please add to your news letter....", "Friday, Oct 23, 2026, 11:38 PM ET", HOLIDAY_BLOCKS,
    source="Source: flyer from Bill Bender (Mari, Card.jpg), shown as sent with its text transcribed as printed.",
    title="Holiday Greeting Distribution Plan", sender="Bill Bender"), encoding="utf-8")
_np.notice_listen.add("/workspace/oct18-batch", HOLIDAY_PAGE)
# Steven Oct 24 1:27 PM: North Clubhouse ice machine notice = Elaine Cole's sentence (Oct 14 P&E report, verbatim) + Steven's own
# confirmed details (he checked it in person), his words formed into sentences, no added facts. Title chosen (no source heading).
ICE_PAGE = "2026-10-24-north-clubhouse-ice-machine-moved-notice.html"
ICE_TITLE = "North Clubhouse Ice Machine Moved"   # chosen title (flagged: no source heading)
ICE_ELAINE = "The ice machine has been relocated so it no longer is a nuisance to the classes."   # Elaine Cole, P&E Oct 14, verbatim
ICE_STEVEN = ["The ice machine in the North Clubhouse was moved out of the North meeting room and into the pool table room.",
              "It's more convenient, and people getting ice won't disturb any meetings going on in the meeting room."]
_ICE_PE = "2026-10-14-planning-and-environmental-committee-report.html"
assert ICE_ELAINE in (Path("/workspace/oct18-batch/pages") / _ICE_PE).read_text(encoding="utf-8"), "R60c: Elaine's ice machine sentence must be verbatim from the P&E Oct 14 report"
ICE_TEASER = ICE_STEVEN[0]
(Path("/workspace/oct18-batch/pages") / ICE_PAGE).write_text(_np.render(ICE_TITLE, "Saturday, Oct 24, 2026", [
    ("h", "From the Planning and Environmental Committee Report (Oct 14, Elaine Cole)"), ("p", ICE_ELAINE),
    ("h", "Details confirmed by Steven Leonowicz"), ("p", " ".join(ICE_STEVEN))],
    source="Source: Oct P&E Committee Report", source_href=BASE + _ICE_PE, title=ICE_TITLE,
    sender="Oct P&E Committee Report (Elaine Cole); details confirmed by Steven Leonowicz"), encoding="utf-8")
_np.notice_listen.add("/workspace/oct18-batch", ICE_PAGE)
for _n, _subj, _sent, _blocks in WM_COPIES:
    _np.write("/workspace/oct18-batch", _n, _subj, _sent, _blocks)
LINDA_TEASER = "Halloween Dance tickets are sold out. Be respectful at clubhouses. Largo Evening Market: Sat. Oct. 24th, 5-9pm, Ulmer Park."  # R42/R18: Linda's own words, all 3 sections, 3 lines max
SANIT_TEASER = "The brush dumpster is designated for brush and yard waste ONLY. Broken pavers should be placed in the construction dumpster."  # R18: source sentences, light trims
COUPLES_TEASER = "Couples Golf League will be starting November 5th. Couples League needs Hosting Volunteers."  # R18: source sentences verbatim
LIBRARY_TEASER = "The Library will be closed beginning MONDAY, OCTOBER 26TH through SUNDAY, NOVEMBER 1ST. Pick up books by Sunday the 25th."  # R18: source sentences verbatim
STOP_TEASER = "Please observe the posted speed limits and come to a complete stop at all stop signs throughout our community."  # R18: source sentence, lead-in trimmed
SOUTHREC_TEASER = "The South Recreation Club has positions available for the 2027 election. DEADLINE: December 2, 2026."  # R18: flyer wording
HOLIDAY_TITLE = "A convenient way to send holiday cards for Palm Hill residents"  # Steven correction Oct 24 11:39 AM: exact main-page title (R60b guard)
HOLIDAY_TEASER = "A simple way for Palm Hill residents to send holiday greetings to friends and neighbors within the community."  # flyer's own words, verbatim
NOTICES = [
    # Steven Oct 24 11:38 AM: Bill Bender's flyer (resident notice; Source = Bill Bender, linked to its page)
    (HOLIDAY_TITLE, HOLIDAY_TEASER, "Bill Bender email", BASE + HOLIDAY_PAGE),
    # Steven Oct 24 1:27 PM: position 3 (right after Bill Bender); Source links the Oct 14 P&E report page
    (ICE_TITLE, ICE_TEASER, "Oct P&E Committee Report", BASE + _ICE_PE),
    # Steven Oct 23 6:38 PM: three more Webmaster emails (gotwicz), newest first; RPM duplicate of the stop sign email ignored
    ("Library Closed starting the week of October 26th", LIBRARY_TEASER, "Webmaster", BASE + WM_COPY_LIBRARY),
    # Steven Oct 23 5:09 AM (A, C): two Webmaster emails (gotwicz); one email = one notice (R42); RPM duplicate of the sanitation email ignored
    ("Help with maintaining Sanitation Field", SANIT_TEASER, "Webmaster", BASE + WM_COPY_SANIT),
    ("Please observe important stop sign rules", STOP_TEASER, "Webmaster", BASE + WM_COPY_STOP),
    ("2027 South Rec Club Seeking Officers", SOUTHREC_TEASER, "Webmaster", BASE + WM_COPY_SOUTHREC),
    ("Couples Golf League", COUPLES_TEASER, "Webmaster", BASE + WM_COPY_COUPLES),
    ("Swimming Pool Food and Beverage Rules",  # Webmaster, Fri Oct 16 12:29 PM ET (gotwicz 1a1458d5b589bff6); newest notice after Tony's
     "All food and beverages must be kept at least 4 feet away from the edge of the pool (the \"wet deck\" area). No glass containers of any kind are permitted inside the fenced pool area; please use plastic or other non-breakable containers. Residents are responsible for ensuring that their guests comply with all pool rules and regulations.",
     "Webmaster", BASE + "2026-10-16-swimming-pool-food-and-beverage-rules-notice.html"),
    ("November Coffee and Pancake Volunteers",
     "An announcing chairperson is needed for November coffees at the North Clubhouse, along with 8 coffee volunteers. Pancakes on Saturday, Nov 14 need 14 volunteers, arriving at 7:30 AM. Sign-up sheets are on the North Clubhouse bulletin board.",
     "Webmaster", BASE + WM_COPY_PANCAKES),  # L27/L29: linked short Webmaster, no date/sender
    ("Shuffleboard Season Reminders",
     "Please don't walk on the courts; return discs to their holders under the benches and cue sticks to the wall hangers; close windows and turn off lights and fans when you leave. Anyone under 18 must be with an adult, no smoking, and wear closed-toe shoes. On the north courts with embedded beads, don't drop the disc onto the beaded surface — set it outside the playing area and push it forward into the kitchen.",
     "Webmaster", BASE + WM_COPY_SHUFFLE),  # L27/L29: "(Shuffleboard Club)" is a sender name -> dropped
    ("Taste of Golf — November 18",
     "New golfers and residents are welcome on Wednesday, Nov 18 at 10:00 AM. Meet at the Pro Shop; it's free. Golf teachers on each hole cover etiquette, warm-up, driving, chipping, putting and reading the green, with treats on each hole and a hot dog on the Pro Shop patio. Not a golfer? Walk, watch and enjoy the course. Sign-up sheets are at the Pro Shop and both clubhouses.",
     "Webmaster", BASE + WM_COPY_GOLF),  # L27/L29
    # STYLE-RULES R42 (Steven, Oct 17 10:29 PM): one source email = one notice. Linda Keehl's "Info from Linda" (Webmaster, Thu Oct 8
    # 5:25 PM ET) has three sections -- Halloween Dance, PLEASE-PLEASE-PLEASE (clubhouse courtesy), Largo Evening Market -- so it is ONE
    # notice titled with her subject, teaser in her words covering all three (scripts/source_sections.py SOURCES + guard). More → and
    # Listen open the existing copy of her email (use_existing_page: no generated notice page). The old 2026-10-18-notice-clubhouse-
    # courtesy-during-busy-season.html stays live (URL valid) but is no longer linked from the issue. Her email is not an event source of
    # truth: the Halloween Dance Party row's date/time/room come from the calendar.
    ("Info from Linda",
     LINDA_TEASER,
     "Webmaster", BASE + "2026-10-08-info-from-linda-notice.html"),
    ("Property Fraud Alert",
     f'The Palm Hill webmaster shared the sign-up link for <a href="https://www.propertyfraudalert.com/select" style="color:{G};">Property Fraud Alert</a>, a free service that notifies you when a document is recorded under your name.',
     "Webmaster", BASE + "2026-09-30-property-fraud-alert-notice.html"),
    ("October Mowing Date",
     "Reminder: BrightView's next tentative resident mowing date is Tuesday, Oct 27. The schedule may change.",
     "RPM", BASE + "2026-09-29-mowing-dates-notice.html"),
]
# Steven Oct 20 3:03 PM: drop stale carried-over notices (Linda's Oct 24 market email, Oct 27 mowing date, Taste of Golf notice --
# Taste of Golf stays as an event row). Guard: none of these titles may appear in Community Notices.
NOTICES_DROPPED_OCT25 = {"October Mowing Date", "Property Fraud Alert"}  # Steven Oct 21 8:43 PM: Property Fraud Alert dropped (its Vercel page stays live)  # Steven Oct 21 11:20 AM: Info from Linda + Taste of Golf notice restored (R56 event cards link them)
NOTICES = [n for n in NOTICES if n[0] not in NOTICES_DROPPED_OCT25]
assert not {n[0] for n in NOTICES} & NOTICES_DROPPED_OCT25
NOTICE_LISTEN_OVERRIDE = {ICE_TITLE: BASE + ICE_PAGE}  # R60c: Listen reads the notice's own page (Source is the P&E report)
def notice_rows():
    rows, items = [], [(TONY_FB[0], TONY_FB_TXT, "Tony Ciaramitaro, Communications Chair", None)] + NOTICES
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
CHAIR = [  # newest first; no Source line; no word "Report" in titles; 17px summary; action row at bottom
    ("Communications Committee", "2026-09-21", "Tony Ciaramitaro chaired his first meeting: booking system, Facebook trial, Zoom training.",
     BASE + "2026-09-21-communications-committee-report.html", BASE + "2026-10-04-listen-communications-committee-report.html"),
    ("Planning and Environmental Committee", "2026-09-09", "The committee found buying the land HOPH rents feasible; its report is with the Board.",
     BASE + "2026-09-16-planning-and-environmental-committee-report.html", BASE + "2026-10-04-listen-planning-environmental-committee-report.html"),
    ("Golf Advisory Committee", "2026-09-08", "Sprinkler work continues and hole #1 has a new sand trap. Golf clinic proposed for Nov 18.",
     BASE + "2026-09-08-golf-advisory-committee-report.html", BASE + "2026-10-04-listen-golf-advisory-committee-report.html"),
]
# Steven, Oct 17 1:40 PM (post-proof addition): Golf Advisory Committee summary from Carolyn Story (nystory11@gmail.com),
# palmhillblast "Golf Advisory Committee", Sat Oct 17 1:20 PM ET. Meeting date: not stated in the email; Tuesday Oct 13, 2026
# per the calendar-confirmed Golf Committee meeting (agenda: Board liaison Carolyn Story, Communications request, next meeting
# Nov 10) and "Finances (as of 10/13)". Full text = Carolyn's wording, block by block (scripts/chair_report_page.py).
GOLF_1013_PAGE = "2026-10-13-golf-advisory-committee-report.html"
GOLF_1013_LISTEN = "2026-10-18-listen-golf-advisory-committee-report.html"
GOLF_1013 = [
    ("p", "Please find the summary of our recent meeting notes below:"),
    ("h2", "Finances (as of 10/13) – Megan Leftwich"),
    ("ul", ["Budget: $2,534.31 over budget for the month; $5,519.89 over YTD.",
            "Activity: 76 paid memberships, 46 paid cart fees, and 8 ten-packs sold."]),
    ("h2", "Golf Course Update – Joe Clay, Superintendent"),
    ("ul", ["Course Conditions: Weather is currently affecting growth, but normal conditions are expected in about a week.",
            "Projects: Pro Shop plantings are complete, sod green work is ongoing, and new sand traps were added."]),
    ("h2", "Board Liaison Update – Carolyn Story"),
    ("ul", ["The amended Code of Conduct was unanimously approved by the Board of Directors on September 26, 2026.",
            "Commended the team on the upcoming Golf Clinic."]),
    ("h2", "Code of Conduct & Accountability – Caroline Zimmerman, Chair"),
    ("ul", ["Posting: The approved Code of Conduct will be posted in the Link, Pro Shop, and sign-up area, and included in membership packets.",
            "Accountability: Members must pay before play each season. The membership list is available to the Pro Shop."]),
    ("h2", "Fiscal Year"),
    ("ul", ["The Golf Committee is currently processing a request to move the fiscal year start from July to April."]),
    ("h2", "Associations & Leagues"),
    ("ul", ["Women's League (Sue Waldecker): Friday morning slot is reserved; league starts Nov 6, with the first meeting on Nov 13. Volunteer/chair sign-ups are in the Pro Shop. First year using an online handicap system managed by K. Kummer and D. Southward.",
            "Couples League (Mike McCarthy): Hosting sign-up is available at the Pro Shop. Thanksgiving, Christmas Eve, and New Year's Eve will be open play.",
            "Bandits (Chuck Silcox): Members are slowly returning."]),
    ("h2", "Pro Shop & Events"),
    ("ul", ["Deep cleaning is complete, and two large artificial ferns are on order for the patio.",
            "Golf Clinic: 15 people signed up so far. Sign-up sheets are in the Pro Shop and North/South Clubhouses."]),
    ("h2", "Communication Committee"),
    ("ul", ["Approved minutes will be sent after each meeting for posting on the PHCC website."]),
    ("h2", "Next Meeting"),
    ("ul", ["Date & Time: November 10, 2026, at 2:00 PM EST", "Location: SCH"]),
]
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import chair_report_page as _crp
if not (Path("/workspace/oct18-batch/pages") / GOLF_1013_PAGE).exists(): (Path("/workspace/oct18-batch/pages") / GOLF_1013_PAGE).write_text(  # Oct 25: published page (Listen added by build_archive.js) is never overwritten
    _crp.render("Golf Advisory Committee Report", GOLF_1013, "Source: Golf Advisory Committee Report (Carolyn Story)", GOLF_1013_PAGE), encoding="utf-8")
# seed the listen-* page once; build_archive.js (dateline_listen) rebuilds it from the report page on every run
_lp = Path("/workspace/oct18-batch/pages") / GOLF_1013_LISTEN
if not _lp.exists(): _lp.write_text((Path("/workspace/oct18-batch/pages") / GOLF_1013_PAGE).read_text(encoding="utf-8"), encoding="utf-8")
CHAIR.insert(0, ("Golf Advisory Committee", "2026-10-13",
    "The amended Code of Conduct was unanimously approved by the Board of Directors on September 26, 2026.",  # Carolyn's wording
    BASE + GOLF_1013_PAGE, BASE + GOLF_1013_LISTEN))
# Oct 23 Friday build: Planning and Environmental Committee report from Elaine Cole (elainezcole@gmail.com), palmhillblast
# "Blast report of P&E 10/14", Fri Oct 23 2:43 PM ET (Google Docs attachment "On-line report of P&E 10/14"). Meeting date
# confirmed (R30) by the Webmaster agenda "Notice is given of a Planning and Environmental Meeting" (gotwicz, Oct 9) and the
# "Reminder: Planning and Environmental Committee Meeting Today" notice (Oct 14): Wed Oct 14, 2026, 1:00 PM, South Board Room.
# Full text = Elaine's wording, block by block. Her "12:30 a.m." for Nov 10 is kept as written (flagged for Steven).
PE_1014_PAGE = "2026-10-14-planning-and-environmental-committee-report.html"
PE_1014_LISTEN = "2026-10-25-listen-planning-environmental-committee-report.html"
PE_1014 = [
    ("p", "There were 3 items on the P&E agenda: update on progress in the north clubhouse for wellness classes, decision on laundry service lease, and master plan update."),
    ("p", "The committee approved a motion to the Board to pay $857.33 to WindowFilm LLC, to provide privacy coverings for wellness classes. The ice machine has been relocated so it no longer is a nuisance to the classes. A hydration station has been installed. This station will accommodate filling water bottles."),
    ("p", "The committee also approved a motion to the Board that it contract with Laundry Leasing LLC to provide and maintain 2 washers and 2 dryers. Committee members who researched the issue of Largo's Business Receipt Tax determined that this operation will not subject Palm Hill to the tax."),
    ("p", "The Master Plan sub-committee will meet in late-October. It is working on evaluating HOPH's assets."),
    ("p", "The next meeting will be on Tuesday, Nov. 10, at 12:30 a.m."),
]
if not (Path("/workspace/oct18-batch/pages") / PE_1014_PAGE).exists(): (Path("/workspace/oct18-batch/pages") / PE_1014_PAGE).write_text(
    _crp.render("Planning and Environmental Committee Report", PE_1014, "Source: Planning and Environmental Committee Report (Elaine Cole)", PE_1014_PAGE), encoding="utf-8")
_lp = Path("/workspace/oct18-batch/pages") / PE_1014_LISTEN
if not _lp.exists(): _lp.write_text((Path("/workspace/oct18-batch/pages") / PE_1014_PAGE).read_text(encoding="utf-8"), encoding="utf-8")
CHAIR.insert(0, ("Planning and Environmental Committee", "2026-10-14",
    "Motion to the Board: pay $857.33 to WindowFilm LLC, to provide privacy coverings for wellness classes.",  # Elaine's wording, trimmed to 3 lines (R18)
    BASE + PE_1014_PAGE, BASE + PE_1014_LISTEN))
def _arch_row(section, row):
    """R59: add an archive row (newest first) to archive/archive-items.json once; idempotent on the row's page."""
    _f = Path("/workspace/oct18-batch/archive/archive-items.json"); _t = _f.read_text(encoding="utf-8")
    if f'"page": "{row["page"]}"' in _t: return
    _k = _t.find(f'"{section}": {{'); _i = _t.find('"items": [', _k); assert _k > 0 and _i > 0, section
    _i += len('"items": [')
    _t = _t[:_i] + "\n      " + json.dumps(row, ensure_ascii=False) + "," + _t[_i:]
    json.loads(_t); _f.write_text(_t, encoding="utf-8")
_arch_row("committee-reports", {"date": "2026-10-14", "title": "Planning and Environmental Committee Report", "page": PE_1014_PAGE,
                                "listen": PE_1014_LISTEN, "issues": ["2026-10-25"]})
# Rules and Regulations (Bob Newport, palmhillblast "Re: Committee Chair Reports Archive", Sat Oct 17 12:05 PM ET): the three
# attached reports are Mar 23, May 11 and Aug 10, 2026 -- all older than the 30-day retention cutoff (Sep 18), and Aug 10 is
# already published -- so none is added to the Oct 18 Chair Reports section without Steven's decision.
# Steven, Oct 17 (answer t839s3231): "Add March and May to the Chair Reports archive only". Full report + listen-* seed pages
# from Bob's own wording (Word files "Rules Mtg. March 23 26.docx", "Rules Meeting May 2026.docx"; R30), block by block, typos kept.
# ARCHIVE ONLY: not added to CHAIR (the Oct 18 issue / SEND are unchanged); archive rows live in archive/archive-items.json
# (committee-reports, issues: []) and build_archive.js adds the date line + R28 bottom-right speaker Listen. Aug 10 stays as published.
RULES_ARCHIVE_ONLY = [
    ("2026-03-23-rules-and-regulations-committee-report.html", "2026-03-23-listen-rules-regulations-committee-report.html", [
        ("p", "Rules and Regulation Committee"),
        ("p", "March 23, 2026 11 am"),
        ("p", "Boardroom, Zoom, and Ch.732"),
        ("p", "The Rules and Regulation Committee held a meeting on 23 March. 2026 at 11 am. Since this was the first meeting of the committee, the agenda was just topics for future actions, and discussions on Park issues. Also to allow the committee to meet each other."),
        ("p", "Topics for future actions and discussion are, Replacement of trees that are removed, ESA animals and the responsibility of them trespassing on others property, (especially where they toilet), Guns and Weapons Policy, Possible Speed Bump Locations, and Increasing the Application fee."),
        ("p", "There was Discussion of Rule Enforcement in the park, and this will be a subject for future discussion. The meeting was adjourned at 11:40 am.")]),
    ("2026-05-11-rules-and-regulations-committee-report.html", "2026-05-11-listen-rules-regulations-committee-report.html", [
        ("p", "Rules and Regulation Committee"),
        ("p", "May 11, 2026 1 pm"),
        ("p", "Boardroom, Zoom, and Ch.732"),
        ("p", "The Rules and Regulations Meeting was called to order at 1pm, and adjourned at 2:30pm. Although the length of the meeting was fairly long the number of Topics was limited. Discussion of a Firearms rule was briefly discussed but was tabled until further input could be accessed. There was also a brief discussion on Speed bumps but was tabled for future discussion. There was a lot of discussion on ESA dogs, but it is to be further reviewed in a Future meeting. The Committee reviewed the proposed Violations Policy, and made adjustments to it. It was then approved to be sent to the Board for adoption. The next meeting was set for August 10, 2026, at 1pm. Then the meeting was adjourned"),
        ("p", "Submitted by Bob Newport, Committee Laison")]),
]
for _pg, _ls, _blocks in RULES_ARCHIVE_ONLY:
    if not (Path("/workspace/oct18-batch/pages") / _pg).exists(): (Path("/workspace/oct18-batch/pages") / _pg).write_text(  # Oct 25: keep published page
        _crp.render("Rules and Regulations Committee Report", _blocks, "Source: Rules and Regulations Committee Report (Bob Newport)", _pg), encoding="utf-8")
    _lp = Path("/workspace/oct18-batch/pages") / _ls
    if not _lp.exists(): _lp.write_text((Path("/workspace/oct18-batch/pages") / _pg).read_text(encoding="utf-8"), encoding="utf-8")
def chair_cards():
    out = []
    # RETENTION (Steven, Oct 16): latest report per committee, shown only if dated within 30 days of the issue; older -> archive only
    from datetime import date as _d, timedelta as _td
    cutoff = (_d(2026, 10, 25) - _td(days=30)).isoformat()
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
s = re.sub(r"<title>.*?</title>", "<title>PHNEWS October 25, 2026 — DRAFT (not sent)</title>", s, count=1, flags=re.S)
s = s.replace('color:#e5f1d1;">October 18, 2026<', 'color:#e5f1d1;">Sunday, October 18, 2026<')  # batch item 1: weekday in masthead
s = s.replace("October 11, 2026", "October 18, 2026").replace("Vol. 1, No. 13", "Vol. 1, No. 14")
s = s.replace("October 18, 2026", "October 25, 2026").replace("Vol. 1, No. 14", "Vol. 1, No. 15")  # Oct 25 issue
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

replace_table("Committee &amp; Board Meeting Schedules", mtg_rows(), f"{md(MEETINGS[0])} through {md(max(MEETINGS[1], meetings[-1]["date"]))}")
replace_table("Committee Chair Reports", chair_cards())
replace_table("Community Notices", notice_rows())
replace_table("Events - Upcoming", ev_rows(upcoming), f"{md(UPCOMING[0])} through {md(UPCOMING[1])}")
# Events - This Week (cloned from Upcoming shell) placed per L03 order
a, b = section_span(s, "Events - Upcoming"); up = s[a:b]
tw = up.replace("events-upcoming-detailed", "events-this-week-detailed").replace(">Events - Upcoming<", ">Events - This Week<").replace('data-heading-variant="upcoming_events"', 'data-heading-variant="this_week"')
r0, _ = section_span(s, "Recurring Meetings &amp; Events")
s = s[:r0] + tw + s[r0:]   # L03: This Week sits between Chair Reports and Recurring
replace_table("Events - This Week", ev_rows(this_week), f"{md(THIS_WEEK[0])} through {md(THIS_WEEK[1])}")
# Recurring: window text; Oct 18 recurring pages don't exist yet -> keep live Oct 11 pages (flagged)
s = s.replace("Oct 11 through Nov 9, 2026", f"{md(RECURRING[0])} through {md(RECURRING[1])}, 2026")
# STYLE-RULES R20: the issue links to its own week's Recurring pages (recurring_oct18.py + recurring_grouped.py ... 2026-10-18)
s = s.replace("2026-10-11-recurring-activities-by-", f"{RECURRING[0]}-recurring-activities-by-")

# ---------- STYLE-RULES R45 (Steven, Oct 18 12:07 AM): Community Stories section ----------
# The section ran once (Oct 4, Mary Leslie). The Oct 11 builder dropped it ("no new story", drop_section) and the Oct 18 builder,
# cloned from Oct 11, never had it. Oct 18 carries Carolyn M. Story's Marge Taylor profile (Palm Hill Link Sep 2026, pp. 10-12;
# confirmed in Carolyn's Sep 28 email to palmhillblast; story + listen pages built Oct 9, PR #10; never in a newsletter before).
# Placed where Oct 4 had it: right before From the Board President. Teaser = verbatim sentence from the story page.
_JC = json.load(open("/workspace/oct18-batch/builder/oct25/data/community-story-joe-clay.json", encoding="utf-8"))
# Oct 25 (PR #130, Steven Oct 19): Joe Clay - Keeper of The Course; date line Oct 1, 2026; credit line TBD (no source credit printed;
# new rule Oct 20: no Palm Hill Link name inside articles). Preview pages until publish creates the live page (_JC live_page_planned).
# R18c (Steven Oct 24 12:18 PM): over-long phone teasers are CUT (never reworded) to their first source sentence(s);
# the full text stays word-for-word on the item's own page. Guard: the cut must be a prefix of the source text.
def _R18_CUT(text, n):
    import re as _re0
    sents = _re0.split(r"(?<=[.!?])\s+", text.strip()); cut = " ".join(sents[:n])
    assert text.startswith(cut) and cut, ("R18c cut is not a prefix of the source", text); return cut
STORY = dict(title=_JC["title"], date=_JC["date_iso"], teaser=_R18_CUT(_JC["teaser_candidate"], 1),
             page=_JC["live_page_planned"], listen="2026-10-listen-joe-clay-story.html",   # Steven Oct 20 4:33 PM: live page (written by stage script), never the undeployed preview URL
             source=None, archive_title=_JC["title"])
COMMUNITY_STORIES_OMIT_APPROVED = None   # R45: set to "<Steven's approval, date/time>" only when Steven approves an issue without a story
_story_page = (Path("/workspace/oct18-batch/pages") / STORY["page"]).read_text(encoding="utf-8")
assert STORY["teaser"].replace("'", "\u2019") in _story_page or STORY["teaser"] in _story_page, "R45: story teaser must be verbatim from the story page"
assert (Path("/workspace/oct18-batch/pages") / STORY["listen"]).exists(), "R45: story listen page missing"
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
    _ai = _AI.read_text(encoding="utf-8") if "_AI" in globals() else Path("/workspace/oct18-batch/archive/archive-items.json").read_text(encoding="utf-8")
    _mi = re.search(r'(\{"date": "' + STORY["date"] + r'"[^\n]*?"title": "' + re.escape(STORY["archive_title"]) + r'"[^\n]*?"issues": \[)([^\]]*)(\])', _ai)
    if not _mi:  # Steven Oct 20 4:33 PM: preview builds add the archive row too (was deferred to publish)
        _row = json.dumps({"date": STORY["date"], "date_label": "Oct 2026", "title": STORY["archive_title"], "summary": STORY["teaser"],
                           "page": STORY["page"], "listen": STORY["listen"], "issues": ["2026-10-25"]}, ensure_ascii=False)
        _k = _ai.find('"community-stories": {'); _i = _ai.find('"items": [', _k); assert _k > 0 and _i > 0, "R45: community-stories items list"
        _i += len('"items": [')
        _ai = _ai[:_i] + "\n      " + _row + "," + _ai[_i:]
        Path("/workspace/oct18-batch/archive/archive-items.json").write_text(_ai, encoding="utf-8")
        json.loads(_ai)
    elif '"2026-10-25"' not in _mi.group(2):
        _iss = (_mi.group(2) + ', "2026-10-25"') if _mi.group(2).strip() else '"2026-10-25"'
        Path("/workspace/oct18-batch/archive/archive-items.json").write_text(_ai.replace(_mi.group(0), _mi.group(1) + _iss + _mi.group(3)), encoding="utf-8")
# Weekly Manager Update Oct 23 (Megan Leftwich, "Fw: Weekly Update 2026.10.23", palmhillblast Fri Oct 23 4:07 PM ET; her
# original went to the Board at 4:03 PM) replaces Oct 16 (retention rule). The page is built here from the Oct 16 page's
# card template with Megan's wording item by item (never hand-edited); decorative emoji in the insurance scenarios dropped.
WMU_1023_PAGE = "2026-10-23-weekly-manager-update.html"
WMU_1023 = [
    "We had a complaint regarding the temperature of the water in the north pool. Staff have checked over the heaters, and they are working properly and maintaining the correct temperatures. We will not be changing the temperature, as it has been established and is maintained year-round.",
    "At the Finance committee meeting, I confirmed the placement of the requested CDs. You now have 4 in your reserve account and 3 in your savings. All are $100,000 and have staggered due dates.",
    "The City of Largo picked up the trash compactor to empty on Friday, and their truck broke down with the unit on it. They dropped off an open-top container temporarily but were able to get the compactor back to us just now.",
    "The election equipment will be dropped off on Thursday morning next week, with the election on Tuesday the following week.",
    "Toni has begun preparing the First Notice for the annual meeting. It is scheduled to go out on or before November 20th.",
    "We received the second grease trap permit from the City of Largo this week. They are posted in the south clubhouse.",
    "We had a motorcycle in the community on Needle today. I spoke to them, and we sent them a letter regarding it.",
    ("David had asked if the insurance coverage was necessary and Lauren responded with the following:", [
        "The coverage is not mandatory, but a recommendation considering the prior policy included the coverage.",
        "Below are examples of claim scenarios that would preclude coverage without implementing such a policy:",
        "<strong>Scenario 1 – Neighbor Dispute Turns Physical</strong><br>Two residents get into a heated argument over a parking space in a common lot. The dispute escalates and one resident strikes the other. The injured party sues the park, alleging negligent security and failure to address prior complaints about the aggressive neighbor.",
        "<strong>Scenario 2 – Pool / Common Area Altercation</strong><br>A fight breaks out between teenagers at the community pool. A bystander resident is injured trying to break it up. The park is named in the lawsuit for failing to provide adequate supervision or security.",
        "<strong>Scenario 3 – On-Site Manager Involvement</strong><br>A park manager physically confronts a resident who is violating community rules. The resident alleges excessive force and files a claim against both the manager and the park ownership entity."]),
    "Lynntina with Duke confirmed receipt of the payment for the transformer. She has requested the signed waiver before they will schedule the work.",
    "Manhole inspections were conducted today. I have reached out to them to confirm they have completed them. We will submit the required paperwork by the November 6th deadline.",
    "Attached is a paper from RPM regarding minutes and some guidelines as to what to include. Please let me know if you have any questions, and I will share them with the committees.",
]
_wp = Path("/workspace/oct18-batch/pages") / WMU_1023_PAGE
if not _wp.exists():  # published page (nav/Listen kept current by build_archive.js) is never overwritten
    _tpl = (Path("/workspace/oct18-batch/pages") / "2026-10-16-weekly-manager-update.html").read_text(encoding="utf-8")
    def _li(x):
        if isinstance(x, tuple):
            return f"<li>{escape(x[0], quote=False)}<blockquote>" + "".join(f"<p>{q}</p>" for q in x[1]) + "</blockquote></li>"
        return f"<li>{escape(x, quote=False)}</li>"
    _a = _tpl.index('<main><section class="content-card">') + len('<main><section class="content-card">')
    _b = _tpl.index('<p class="signoff">', _a)
    _tpl = _tpl[:_a] + "\n<p>Good Afternoon Everyone,</p>\n<ul>\n" + "\n".join(_li(x) for x in WMU_1023) + "\n</ul>\n" + _tpl[_b:]
    _a = _tpl.index('<section class="content-card attachments"'); _b = _tpl.index("</section>", _a) + len("</section>\n")
    _tpl = _tpl[:_a] + _tpl[_b:]   # Oct 16 photo attachment does not carry over; the RPM minutes PDF is not hosted (flagged)
    for o, n in [("October 16, 2026", "October 23, 2026"), ("Oct 16, 2026", "Oct 23, 2026"),
                 ("2026-10-16-weekly-manager-update", "2026-10-23-weekly-manager-update"), ("2026.10.16", "2026.10.23")]:
        _tpl = _tpl.replace(o, n)
    assert "2026-10-16" not in _tpl.split("<!-- ph-page-listen:start -->")[0], "WMU Oct 23 template still has Oct 16 refs"
    _wp.write_text(_tpl, encoding="utf-8")
_arch_row("weekly-manager-updates", {"date": "2026-10-23", "title": "Weekly Manager Update", "byline": "Megan Leftwich",
                                     "page": WMU_1023_PAGE, "issues": ["2026-10-25"]})
# Weekly Manager Update Oct 16 (Megan, palmhillblast Oct 16 3:59 PM ET) replaces Oct 9 (retention rule)
_W_OLD = s[s.find('<div style="font-size:15px;font-weight:bold;color:#333333;">Weekly Manager Update — October 9</div>'):]
_W_OLD = _W_OLD[:_W_OLD.find('</td></tr>')]
assert "Duke Energy Waiver" in _W_OLD
_W_NEW = ('<div style="font-size:15px;font-weight:bold;color:#333333;">Weekly Manager Update</div>'  # R19: date only on the date line
    '<div style="font-size:14px;color:#666666;margin-top:2px;">Friday, Oct 23, 2026</div>'
    '<div style="font-size:15px;color:#333333;margin-top:3px;">The election equipment will be dropped off on Thursday morning next week, with the election on Tuesday the following week.</div>'
    f'<div style="margin-top:4px;font-size:14px;line-height:1.6;"><a href="{BASE}{WMU_1023_PAGE}" style="color:{G};white-space:nowrap;">Read Full Update →</a><span style="color:#999999;"> · </span><a href="{ARCH}weekly-manager-updates.html" style="color:{G};white-space:nowrap;">Weekly Manager Report Archives →</a></div>'
    f'<div style="font-size:13px;color:#666666;margin-top:5px;"><a href="{BASE}{WMU_1023_PAGE}" style="color:{G};">Source</a>: Weekly Manager Update</div>')
s = s.replace(_W_OLD, _W_NEW)
# Manager reports: Listen icon on the title line (pages have built-in Listen; ?listen=1 autostarts)
for t, href in [("Shareholders Report — September 30 Board Meeting", BASE + "2026-09-30-shareholders-report.html"),
                ("Weekly Manager Update", BASE + WMU_1023_PAGE)]:
    old = f'<div style="font-size:15px;font-weight:bold;color:#333333;">{t}</div>'; assert old in s, t
    s = s.replace(old, title_row(t, listen(href + "?listen=1")))
# Henry October already the President's Message (to-do #7). Did You Know: archive link (to-do, Oct 11 evening)
old = f'<a href="{ARCH}videos.html" style="color:{G};">Latest Board and committee recordings →</a></div>'
assert old in s
s = s.replace(old, f'<a href="{ARCH}videos.html" style="color:{G};">Latest Board and Committee Meeting Videos →</a><span style="color:#999999;"> · </span><a href="{ARCH}did-you-know.html" style="color:{G};">Did You Know Archives →</a></div>')
# Did You Know: Tony's FB variation (verbatim, Oct 16) appended as 2nd row
a = s.find(">Did You Know?</span>"); e = s.find("</table></div>", a); assert a > 0 and e > 0
DYK_FB = (f'<tr style="background:#F5F5F5;page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;">'
    '<div style="font-size:15px;color:#333333;margin-top:3px;">Did you know Palm Hill has a private, residents-only Facebook group? Park news, events and photos. Search &quot;Palm Hill Country Club - Residents Only Group&quot; on Facebook and answer all 3 questions.</div>'
    f'<div style="font-size:14px;margin-top:4px;"><a href="{FBURL}" style="color:{G};">{FBURL}</a></div>'
    f'<div style="font-size:14px;margin-top:4px;"><a href="{FBPAGE_DYK}" style="color:{G};">Full item with QR code to scan →</a></div></td></tr>')
# Steven's rule (Oct 16): main issue shows ONLY the newest Did You Know; older items live on archive/did-you-know.html
# Steven, Oct 17 1:40 PM (post-proof addition): Rule of the week from David Bates (david.palmhill@gmail.com), palmhillblast
# "Park Rule for Newsletter", Sat Oct 17 1:17 PM ET (his corrected resend of "Rule for Newsletter", 12:53 PM). Summary = his
# wording; full narrative on the Did You Know page (make_live_preview.py dykpage -> publish 2026-10-18-did-you-know-traffic-rules.html).
# STYLE-RULES R39 (Steven, Oct 17 6:22 PM): DYK summary ~3 lines at desktop, built ONLY from Dave's own sentences (XI. TRAFFIC
# RULES text, 1:17 PM email); light trimming only ("Further - " dropped, ".." -> "."). Verbatim check in style_rules.dyk_summary_ok.
import html as _html
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import style_rules as _sr_dyk
DYK_RULES_SUMMARY = ("The speed limit in the park is 15 mph. It's okay to go 15 mph and make a full stop at a stop sign. "
    "Golf Carts and all motor vehicles shall not be operated after dark without tail lights and headlights.")  # Steven 6:28 PM: 3 sentences max
_DYK_SRC = json.load(open(ROOT / "data/dyk-traffic-rules-source.json"))
assert _sr_dyk.dyk_summary_ok(DYK_RULES_SUMMARY, _DYK_SRC), "R39: DYK summary must be at most 3 of Dave's verbatim sentences"
# R39: the Did You Know archive row shows the same summary (archive/archive-items.json, id traffic-rules)
_AI = Path("/workspace/oct18-batch/archive/archive-items.json"); _ai = _AI.read_text(encoding="utf-8")
_m = re.search(r'("id": "traffic-rules", "title": "Traffic Rules", "text": )"((?:[^"\\]|\\.)*)"', _ai); assert _m, "R39: traffic-rules archive row not found"
_new = _m.group(1) + json.dumps(DYK_RULES_SUMMARY, ensure_ascii=False)
if _m.group(0) != _new: _AI.write_text(_ai.replace(_m.group(0), _new), encoding="utf-8")
DYK_RULES_PV = "https://palmhillnews.vercel.app/pages/previews/2026-10-18/did-you-know-traffic-rules.html"
# R39 (Steven, Oct 17 6:32 PM): teaser mode per item -- "framing" (topic/source description, no author name, no rule quotes) or
# "distilled" (<= 3 verbatim source sentences). Traffic Rules = framing on the main page; the archive row keeps the distilled summary.
DYK_RULES_TEASER_MODE = "framing"
DYK_RULES_TEASER = "A look at traffic rules from the park's official Rules and Regulations."   # Steven's wording, 6:32 PM
DYK_CONTRIBUTOR_NAMES = ["Dave", "David", "Bates", "Board VP"]
if DYK_RULES_TEASER_MODE == "framing":
    assert _sr_dyk.dyk_framing_ok(DYK_RULES_TEASER, DYK_CONTRIBUTOR_NAMES, _DYK_SRC), "R39: framing teaser has a name, quotes a rule, or is over 3 lines"
    _DYK_MAIN = DYK_RULES_TEASER
else:
    _DYK_MAIN = DYK_RULES_SUMMARY
DYK_RULES = (f'<tr style="background:#F5F5F5;page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;">'
    f'<div style="font-size:15px;color:#333333;margin-top:3px;">{_html.escape(_DYK_MAIN)} '
    f'<a href="{DYK_RULES_PV}" style="color:{G};white-space:nowrap;">More →</a></div></td></tr>')
_DYK25 = json.load(open("/workspace/oct18-batch/builder/oct25/data/dyk-link-oct2026-spectrum.json", encoding="utf-8"))
_DYK3 = json.load(open("/workspace/oct18-batch/builder/oct25/data/dyk-dave-assessments.json", encoding="utf-8"))
_PV25 = "https://palmhillnews.vercel.app/pages/previews/2026-10-25/"
# R39 distilled teasers: at most 3 verbatim sentences from each item (ALL CAPS kept, RD9)
_TEASE = {"2026-10-25-spectrum-information": "SPECTRUM SUPPORT PHONE NUMBER: 877-647-7732 is the Community Solutions Line for Bulk Owners Customer Support.",  # R18c cut (Steven Oct 24 12:18 PM)
          "2026-10-25-spectrum-music-channels": "Did you know with our new Spectrum set up we have access to several music channels? Simply turn on your TV then select the Spectrum app."}
# R57 (Steven Oct 21 11:22 AM): each Did You Know item is its own block -- bold title (the item's source heading), teaser, then
# More → on its own line; a white gap + green left bar separates items. Guard: style_rules.assert_dyk_blocks.
def _dyk_row(title, text, href):
    return (f'<tr class="ph-dyk-item" style="background:#F5F5F5;page-break-inside:avoid;break-inside:avoid;"><td style="padding:10px 10px;border-left:4px solid #2D5016;border-bottom:10px solid #FFFFFF;">'
            f'<div class="ph-dyk-title" style="font-size:16px;font-weight:bold;color:#333333;">{_html.escape(title)}</div>'
            f'<div style="font-size:15px;color:#333333;margin-top:4px;">{_html.escape(text)}</div>'
            f'<div class="ph-dyk-more" style="font-size:14px;margin-top:6px;"><a href="{href}" style="color:{G};white-space:nowrap;">More →</a></div></td></tr>')
DYK_ITEMS = []
# Steven Oct 21 11:25 AM: final page URLs (Oct 18 pattern pages/<issue>-did-you-know-<slug>.html, written by the stage script)
def _dyk_final(pp): return "2026-10-25-" + pp
_DYK_TITLE = {"2026-10-25-spectrum-information": "Spectrum Support Phone Number"}   # Steven Oct 21: short block title (source wording)
for _it in _DYK25["items"]:
    assert _sr_dyk.dyk_summary_ok(_TEASE[_it["id"]], _it["paragraphs"]), ("R39 distilled teaser not verbatim", _it["id"])
    DYK_ITEMS.append((_it["id"], _dyk_row(_DYK_TITLE.get(_it["id"], _it["title_display"]), _TEASE[_it["id"]], BASE + _dyk_final(_it["preview_page"]))))
_d3src = _DYK3["email_paragraphs"] + [x for _, x in _DYK3["rule_items"]]
# Steven Oct 21 11:22 AM: teaser = distilled summary in the official rule's own words (R39 distilled: verbatim sentences, <= 300 chars)
# Steven Oct 21 11:39 AM: teaser in the rule's own words (his wording). Guard: every content word is in the official rule text.
_DYK3_TEASER_FULL = ("$100.00 total ($50.00 transfer + $50.00 administrative) is required when a home/unit is transferred; "
                "maintenance fees are due on the first day of the month, delinquent if not received by the tenth.")
# R18c (Steven Oct 24 12:18 PM): cut at the semicolon (no rewording) so the phone teaser is <= 3 lines
_DYK3_TEASER = _DYK3_TEASER_FULL.split("; ")[0] + "."
assert _DYK3_TEASER_FULL.startswith(_DYK3_TEASER[:-1])
_rw = set(re.findall(r"[a-z0-9$.]+", " ".join(x for _, x in _DYK3["rule_items"]).lower().replace("home/unit", "home unit")))
_tw = [w.strip(".") for w in re.findall(r"[a-z0-9$.]+", _DYK3_TEASER.lower().replace("home/unit", "home unit"))]
_bad = [w for w in _tw if w and w not in _rw and w.rstrip(".") not in {x.rstrip(".") for x in _rw} and w not in {"if", "are", "total"}]
assert not _bad, f"R39: DYK #3 teaser words not in the official rule: {_bad}"
DYK_ITEMS.insert(0, (_DYK3["id"], _dyk_row(_DYK3["title_display"], _DYK3_TEASER, BASE + _dyk_final(_DYK3["preview_page"]))))  # Steven Oct 20 3:03 PM: Dave's rules item FIRST (R31)
DYK_MULTI_APPROVED = _DYK25["dyk_multi_approved"] + "; " + _DYK3["multi_approved"]
_sr_dyk.assert_dyk_items([{"id": i, "paragraphs": [r]} for i, r in DYK_ITEMS], DYK_MULTI_APPROVED)  # R50
t0 = s.find("<table", a)
s = s[:t0] + '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 12px 0;">' + "".join(r for _, r in DYK_ITEMS) + f'<tr><td style="padding:2px 8px;font-size:14px;"><a href="{ARCH}did-you-know.html" style="color:{G};">Did You Know Archives →</a></td></tr>' + s[e:]  # R50: one archive link after the last item
_sr_dyk.assert_dyk_blocks(s, len(DYK_ITEMS))  # R57
# R59 (Steven Oct 21 11:25 AM): preview builds add archive rows for every archive-backed issue item (DYK here; story above),
# newest first, existing row format; build_archive.js (run at the end) renders them. Guard at the end: each item is on its archive page.
_ai = _AI.read_text(encoding="utf-8")
_DYK_ROWS = [dict(date="2026-10-25", id=_DYK3["id"].replace("2026-10-25-", ""), title=_DYK3["title_display"], text=_DYK3_TEASER,
                  page=_dyk_final(_DYK3["preview_page"]), source_label=_DYK3["source"], issues=["2026-10-25"])]
for _it in _DYK25["items"]:
    _r = dict(date="2026-10-25", id=_it["id"].replace("2026-10-25-", ""), title=_DYK_TITLE.get(_it["id"], _it["title_display"]), text=_TEASE[_it["id"]],
              page=_dyk_final(_it["preview_page"]), issues=["2026-10-25"])
    if _it.get("byline"): _r["source_label"] = _it["byline"]
    _DYK_ROWS.append(_r)
_k = _ai.find('"did-you-know": {'); _i = _ai.find('"items": [', _k) + len('"items": ['); assert _k > 0
_new = "".join("\n      " + json.dumps(r, ensure_ascii=False) + "," for r in _DYK_ROWS if f'"page": "{r["page"]}"' not in _ai)
if _new: _ai = _ai[:_i] + _new + _ai[_i:]; json.loads(_ai); _AI.write_text(_ai, encoding="utf-8")
ARCHIVE_BACKED = [("did-you-know.html", r["page"]) for r in _DYK_ROWS]
# Steven Oct 23 5:09 AM: the two new Webmaster notices get Community Notices archive rows in this build (R59), teaser = issue teaser
_NOTICE_ROWS = [dict(date="2026-10-25", id="2026-10-25-sanitation-field", title="Help with maintaining Sanitation Field", text=SANIT_TEASER,
                     page=WM_COPY_SANIT, source="Palm Hill Webmaster notice, Oct 22", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-couples-golf-league", title="Couples Golf League", text=COUPLES_TEASER,
                     page=WM_COPY_COUPLES, source="Palm Hill Webmaster notice, Oct 20", issues=["2026-10-25"]),
                # Steven Oct 23 6:38 PM
                dict(date="2026-10-25", id="2026-10-25-library-closed", title="Library Closed starting the week of October 26th", text=LIBRARY_TEASER,
                     page=WM_COPY_LIBRARY, source="Palm Hill Webmaster notice, Oct 22", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-stop-sign-rules", title="Please observe important stop sign rules", text=STOP_TEASER,
                     page=WM_COPY_STOP, source="Palm Hill Webmaster notice, Oct 21", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-south-rec-club-seeking-officers", title="2027 South Rec Club Seeking Officers", text=SOUTHREC_TEASER,
                     page=WM_COPY_SOUTHREC, source="Palm Hill Webmaster notice, Oct 21", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-holiday-greeting-distribution-plan", title=HOLIDAY_TITLE, text=HOLIDAY_TEASER,
                     page=HOLIDAY_PAGE, source="Flyer from Bill Bender, Oct 23", issues=["2026-10-25"]),
                dict(date="2026-10-25", id="2026-10-25-north-clubhouse-ice-machine-moved", title=ICE_TITLE, text=ICE_TEASER,
                     page=ICE_PAGE, source="Oct P&E Committee Report (Elaine Cole); details confirmed by Steven Leonowicz", issues=["2026-10-25"])]
_ai = _AI.read_text(encoding="utf-8"); _k = _ai.find('"community-notices": {'); _i = _ai.find('"items": [', _k) + len('"items": ['); assert _k > 0
_new = "".join("\n      " + json.dumps(r, ensure_ascii=False) + "," for r in _NOTICE_ROWS if f'"page": "{r["page"]}"' not in _ai)
if _new: _ai = _ai[:_i] + _new + _ai[_i:]; json.loads(_ai); _AI.write_text(_ai, encoding="utf-8")
ARCHIVE_BACKED += [("community-notices.html", r["page"]) for r in _NOTICE_ROWS]
# Helpful Webpages + archive footer links -> live /pages/ URLs
s = s.replace(f'<a href="{ARCH}meeting-videos.html" style="color:{G};">Palm Hill Committee Videos</a></div>',
              f'<a href="{ARCH}main.html" style="color:{G};">Palm Hill Newsletter Archives</a></div>\n          <div>• <a href="{ARCH}videos.html" style="color:{G};">Committee Meeting Videos - Latest</a></div>\n          <div>• <a href="{ARCH}meeting-videos.html" style="color:{G};">Committee Meeting Video Archives</a></div>')
# STYLE-RULES R25 (Steven, Oct 17 12:20 AM): footer archive-links row removed (links stay in Helpful Webpages);
# Helpful Webpages label is 'Committee Meeting Video Archives' (never 'Committee Meeting Videos - Archives')
assert 'Videos - Archives' not in s, 'R25 label'
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import style_rules as _sr  # STYLE-RULES.md (shared)
s = _sr.enforce_title_months(s)  # full months in titles/bands
import link_archive_bullet as _lab; s = _lab.add(s)
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
Path("/workspace/oct18-batch/builder/calendar-pull").mkdir(exist_ok=True)
Path("/workspace/oct18-batch/builder/calendar-pull/2026-10-25.json").write_text(json.dumps({"calendar_file": os.path.basename(CALF), "pulled_at": _ct.isoformat(), "footer": CALCHECK}, indent=1) + "\n")
_sr_dyk.assert_no_stamp(s, OUTF.name)  # R40
# STYLE-RULES R41/R43 (Steven, Oct 17 10:29 / 10:33 PM): '<Singular noun> Archives →' on every newsletter archive link
# (seed 'Past President Messages →' / 'Past Shareholders Reports →' -> President's Message / Shareholders Report Archives →).
s = _sr.assert_archive_labels(_sr.archive_labels(s), OUTF.name)
s = _sr.assert_source_credits(s, OUTF.name)
s = _sr.assert_community_stories(s, OUTF.name, COMMUNITY_STORIES_OMIT_APPROVED)  # R45
s = _sr.assert_event_sources(s, OUTF.name)  # R48 (Steven, Oct 18 12:31 AM): event rows need Calendar/RPM/Agenda  # STYLE-RULES L27/L29: linked short 'Webmaster', no dates on Source credits
# STYLE-RULES R18/R60 (Steven Oct 21 8:34 PM): root-cause fix -- the Oct 25 builder never ran summary_trim (Oct 18 ran it in
# make_live_preview/publish), so notices showed their full text. Trim here, then guard (scripts/check_notices.py) after writing.
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import summary_trim as _st; s = _st.trim(s)
import check_notices as _cn; _cnf = _cn.static(s)
if _cnf: raise SystemExit("R60: " + "; ".join(_cnf))
# STYLE-RULES R42: one source email = one Community Notice (source-to-sections map; split / missing section fails the build)
import source_sections as _ss
_r42 = _ss.check_issue(s)
if _r42: raise SystemExit("R42: " + "; ".join(_r42))
# STYLE-RULES R62 (Steven Oct 23 6:38 PM): P&E next meeting shows Elaine's date, no TBC note
import re as _re62; _pe = _re62.sub(r"<[^>]+>", " ", s[s.find("Planning and Environmental Committee Meeting"):][:1500])
_pe = _pe[:_pe.find("Source")] if "Source" in _pe else _pe
if not ("Tuesday, Nov 10, 2026" in _pe and "12:30 PM" in _pe and "to be confirmed" not in _pe):
    raise SystemExit("R62: P&E next meeting row must be Tuesday, Nov 10, 2026 12:30 PM with no '(date to be confirmed)': " + " ".join(_pe.split())[:200])
# STYLE-RULES R60b (Steven Oct 24 11:39 AM): Bill Bender notice title exact, Source "Bill Bender email" linked to its flyer page
_hs = _cn.section(s); _hi = _hs.find(">" + HOLIDAY_TITLE + "<")
if _hi < 0: raise SystemExit(f"R60b: Community Notice title {HOLIDAY_TITLE!r} not found")
_he = _hs.find('<tr style="background:', _hi); _hr = _hs[_hi:_he if _he > 0 else len(_hs)]
if f'Source: <a href="{BASE + HOLIDAY_PAGE}"' not in _hr or ">Bill Bender email</a>" not in _hr: raise SystemExit("R60b: Bill Bender notice needs Source: Bill Bender email linked to " + HOLIDAY_PAGE)
# STYLE-RULES R60c (Steven Oct 24 1:27 PM): ice machine notice -- exact title, 3rd notice (right after Bill Bender), Source
# "Oct P&E Committee Report" linked to the Oct 14 P&E page, More -> its own notice page
_ii = _hs.find(">" + ICE_TITLE + "<")
if _ii < 0: raise SystemExit(f"R60c: Community Notice title {ICE_TITLE!r} not found")
_ie = _hs.find('<tr style="background:', _ii); _ir = _hs[_ii:_ie if _ie > 0 else len(_hs)]
if f'Source: <a href="{BASE + PE_1014_PAGE}"' not in _ir or ">Oct P&amp;E Committee Report</a>" not in _ir and ">Oct P&E Committee Report</a>" not in _ir: raise SystemExit("R60c: ice machine notice needs Source: Oct P&E Committee Report linked to " + PE_1014_PAGE)
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
OUTF.write_text(s, encoding="utf-8")
_cn.check(str(OUTF))  # R60 rendered 3-line guard at 390/660px
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import check_listen_coverage as _lc; _lc.require_since(_R49_T0)  # R49 (Steven, Oct 18 12:41 AM): required step
_lc.require_nl(OUTF)  # R49b (Steven, Oct 18 2:05 AM): every ?listen=1 link in this NL opens a page whose Listen starts reading
# STYLE-RULES.md R15: monthly Link save (new Palm Hill Link PDF -> Vercel), non-fatal
import subprocess as _sp2; _lr = _sp2.run([sys.executable, "/workspace/oct18-batch/scripts/fetch_link_pdf.py"], capture_output=True, text=True); print((_lr.stdout or _lr.stderr).strip()[-400:])
json.dump({"calendar_file": CALF, "meetings": [(e["date"], e["name"]) for e in meetings], "this_week": [(e["date"], e["name"]) for e in this_week],
           "upcoming": [(e["date"], e["name"]) for e in upcoming], "stamp": stamp}, open(ROOT / "build-audit-oct25.json", "w"), indent=1)
print("wrote", OUTF, "| meetings", len(meetings), "| this week", len(this_week), "| upcoming", len(upcoming))

# Steven Oct 20 4:33 PM: preview builds refresh the archive pages too (the story row shows on Community Stories before publish)
import subprocess as _sp3
_ba = _sp3.run(["node", "scripts/build_archive.js"], cwd="/workspace/oct18-batch", capture_output=True, text=True)
print("build_archive:", (_ba.stdout or "").strip()[-300:], (_ba.stderr or "").strip()[-300:]); assert _ba.returncode == 0, "build_archive.js failed"
_ca = Path("/workspace/oct18-batch/pages/archive/community-stories.html").read_text(encoding="utf-8")
ARCHIVE_BACKED.append(("community-stories.html", STORY["page"]))
for _ap, _pg in ARCHIVE_BACKED:  # R59 guard: every archive-backed issue item is on its archive page and the page exists
    assert (Path("/workspace/oct18-batch/pages") / _pg).exists(), f"R59: {_pg} missing"
    assert _pg in Path("/workspace/oct18-batch/pages/archive/" + _ap).read_text(encoding="utf-8"), f"R59: {_pg} not on archive/{_ap}"
    assert (BASE + _pg) in s, f"R59: issue does not link the final URL {_pg}"
print("R59 archive-backed items OK:", ARCHIVE_BACKED)
assert STORY["page"] in _ca, "R45: the issue's story is not on the Community Stories archive page"
# Local review copy (D:\PHNEWS\<week>\, fixed names): the story More → / Listen and Story Archives → point to sibling files in the
# same folder so they open from disk; the repo/Vercel copy keeps absolute URLs that resolve after publish.
# R58 (Steven Oct 21 11:24 AM): Story Archives → = the canonical live archive page (the one Oct 18 + Main Archive use).
STORY_ARCHIVE_URL = ARCH + "community-stories.html"   # https://palmhillnews.vercel.app/pages/archive/community-stories.html
_sa = re.findall(r'href="([^"]+)"[^>]*>Story Archives →', s)
assert _sa and all(u == STORY_ARCHIVE_URL for u in _sa), f"R58: Story Archives → must link {STORY_ARCHIVE_URL}, got {_sa}"
assert 'href="community-stories.html"' in Path("/workspace/oct18-batch/pages/archive/main.html").read_text(encoding="utf-8"), "R58: Main Archive no longer links community-stories.html"
# Local review copy (D:\PHNEWS\<week>\, fixed names). The issue's story + Story Archives links open local copies that mirror the
# live paths: <story>.html and archive/community-stories.html (the canonical page, incl. this issue's story); every other
# root-relative link/asset in the local archive copy is made absolute to palmhillnews.vercel.app so it renders like the live page.
LOCAL = ROOT / "local-oct25"; LOCAL.mkdir(exist_ok=True); (LOCAL / "archive").mkdir(exist_ok=True)
_loc = s.replace(BASE + STORY["page"], STORY["page"]).replace(STORY_ARCHIVE_URL, "archive/community-stories.html")
(LOCAL / "PHNEWS-2026-10-25-preview.html").write_text(_loc, encoding="utf-8")
import shutil as _sh
_sh.copy("/workspace/oct18-batch/pages/" + STORY["page"], LOCAL / STORY["page"])
_lca = re.sub(r'(href|src)="/(?!/)', r'\1="https://palmhillnews.vercel.app/', _ca)
_lca = re.sub(r'href="(?!https?:|#|mailto:)([^"/][^"]*\.html)"', r'href="https://palmhillnews.vercel.app/pages/archive/\1"', _lca)
for _u in ("https://palmhillnews.vercel.app/pages/" + STORY["page"], "https://palmhillnews.vercel.app/pages/archive/../" + STORY["page"]):
    _lca = _lca.replace('href="' + _u, 'href="../' + STORY["page"])
(LOCAL / "archive/community-stories.html").write_text(_lca, encoding="utf-8")
_old = LOCAL / "community-stories.html"
if _old.exists(): _old.unlink()   # local review scratch copy only (box), replaced by archive/community-stories.html
assert ('href="../' + STORY["page"]) in _lca, "R58: local archive copy must list and link this issue's story"
_ld = Path("/workspace/oct18-batch/pages/archive/did-you-know.html").read_text(encoding="utf-8")
_ld = re.sub(r'(href|src)="/(?!/)', r'\1="https://palmhillnews.vercel.app/', _ld)
_ld = re.sub(r'href="(?!https?:|#|mailto:)([^"/][^"]*\.html)"', r'href="https://palmhillnews.vercel.app/pages/archive/\1"', _ld)
_loc = (LOCAL / "PHNEWS-2026-10-25-preview.html").read_text(encoding="utf-8").replace(ARCH + "did-you-know.html", "archive/did-you-know.html")
for _ap, _pg in ARCHIVE_BACKED:
    if _ap != "did-you-know.html": continue
    _sh.copy("/workspace/oct18-batch/pages/" + _pg, LOCAL / _pg)
    _loc = _loc.replace(BASE + _pg, _pg)
    for _u in ("https://palmhillnews.vercel.app/pages/" + _pg, "https://palmhillnews.vercel.app/pages/archive/../" + _pg): _ld = _ld.replace('href="' + _u, 'href="../' + _pg)
    assert 'href="../' + _pg in _ld, f"R59: local DYK archive copy missing {_pg}"
(LOCAL / "archive/did-you-know.html").write_text(_ld, encoding="utf-8"); (LOCAL / "PHNEWS-2026-10-25-preview.html").write_text(_loc, encoding="utf-8")
print("local review copy:", sorted(str(p.relative_to(LOCAL)) for p in LOCAL.rglob("*") if p.is_file()))
