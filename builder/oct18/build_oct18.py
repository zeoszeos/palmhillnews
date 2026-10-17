"""PHNEWS Oct 18, 2026 (Vol. 1, No. 14) DRAFT builder. Box-side, draft only; sends/publishes nothing.
Input: ../source/PHNEWS-2026-10-11-FINAL-REVIEW-as-sent-omen.html (Oct 11 as sent, untouched) as the shell,
       ../data/cal-YYYYMMDD.json (Palm Hill calendar = source of truth for events/meetings; RPM never adds/overrides),
       editorial content below (each item names its source).
Saturday refresh: re-fetch calendar (fetch_calendar.sh), update NOTICES / MANAGER / Tony FB wording, rerun.
Output: ../PHNEWS-2026-10-18-preview.html
"""
import json, os, re, sys, glob
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
    _pc.pull(str(ROOT / "data"), "2026-10-18", "2026-12-17")
CALF = sorted(glob.glob(str(ROOT / "data/cal-*.json")))[-1]
OUTF = ROOT / "PHNEWS-2026-10-18-preview.html"
ISSUE = "2026-10-18"
THIS_WEEK = ("2026-10-18", "2026-10-24")
UPCOMING = ("2026-10-25", "2026-11-15")      # ~3 weeks (Oct 9 rule), starts after This Week
RECURRING = ("2026-10-18", "2026-11-16")
MEETINGS = ("2026-10-18", "2026-11-17")      # 30 days inclusive
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
    "Halloween Dance Party": "Doors open at 6:15 PM with no assigned seating. Bring a treat to share for table-to-table trick-or-treating.",
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
EVENT_LINK = {"Halloween Dance Party": ("Read Full Details →", BASE + "2026-10-31-halloween-dance.html"),
              "Mount Dora Trip": ("More →", BASE + "2026-10-24-mount-dora-trip.html"),
              "MESCO Spaghetti Dinner Fundraiser": ("More →", BASE + "2026-11-14-mesco-spaghetti-dinner-fundraiser.html"),
              "Bocce Party": ("More →", BASE + "2026-10-28-bocce-party.html")}
# R21: full calendar listing text for the More → page (personal phone numbers are not printed: see the club calendar)
EVENT_PAGE = {"Bocce Party": ("2026-10-28-bocce-party.html",
    ["Sign up at either clubhouse or by calling Pat Foor or Joe Cothran (their phone numbers are on the club calendar). Join us for the fellowship and fun!",
     "Rescheduled from 4:00 PM to 6:00 PM (6:00 to 7:00 PM)."])}
# R21: events whose summary already carries the whole calendar listing (checked by hand Oct 16) - no More → page needed
INFO_COVERED = {"Halloween Golf Cart Parade", "Senior Empowerment Luncheon", "North Clubhouse Craft Fair", "Pot Luck Supper", "Fall Festival",
                "Veterans Day Program", "Bookclub:Foster by Claire Keegan"}
TITLE = {"Bookclub:Foster by Claire Keegan": "Book Club: Foster by Claire Keegan"}

def bg(i): return "#EAF4E4" if i % 2 else "#FFFFFF"
def src_cal(extra=None):
    s = f'Source: <a href="{CAL}" style="color:{G};">Calendar</a>'
    if extra: s += f', <a href="{extra}" style="color:{G};">Webmaster</a>'
    return s
# Steven, Oct 16 (MEETING-SOURCES-COMPARE.md): Finance from agenda email (no Zoom link yet); Palm Hill dates for Nov conflicts, flagged TBC
MTG_EXTRA = [dict(date="2026-10-22", start="10:00", name="Finance Committee Meeting", venue="South Clubhouse Boardroom", from_calendar=False),
             dict(date="2026-11-18", start="13:00", name="Board of Directors Meeting", venue="Board Room South", note="(date to be confirmed)")]
MTG_NOTE = {("2026-11-10", "Buildings and Grounds Committee Meeting"): "(date to be confirmed)",
            ("2026-11-10", "Planning and Environmental Committee Meeting"): "(date to be confirmed)"}
meetings = sorted(meetings + MTG_EXTRA, key=lambda e: (e["date"], e["start"]))
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
def ev_rows(evs):
    out = []
    for e in evs:  # STYLE-RULES R21 guard
        if (e.get("info") or "").strip() and e["name"] not in EVENT_LINK and e["name"] not in INFO_COVERED:
            raise SystemExit(f"R21: {e['date']} {e['name']} has calendar listing text but no More → page (add EVENT_PAGE/EVENT_LINK or INFO_COVERED)")
        if e["name"] in EVENT_PAGE:
            import event_page as _ep; fn, paras = EVENT_PAGE[e["name"]]
            dl = f"{pdate(e['date'])} • {ptime(e['start'])}" + (f" to {ptime(e['end'])}" if e.get("end") else "") + f" • {VENUE.get(e['venue'], e['venue'])}"
            (Path("/workspace/oct18-batch/pages") / fn).write_text(_ep.render(e["name"], dl, paras), encoding="utf-8")
    for i, e in enumerate(evs):
        det = EVENT_DETAIL.get(e["name"]); lk = EVENT_LINK.get(e["name"])
        loc = "Mount Dora" if e["name"] == "Mount Dora Trip" else VENUE.get(e["venue"], e["venue"])
        out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:6px 8px;border-bottom:1px solid #ddd;"><table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation"><tr><td valign="top" align="left" style="font-size:15px;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">{escape(TITLE.get(e["name"], e["name"]))}</td><td valign="top" align="right" style="font-size:14px;color:#666666;text-align:right;padding-top:1px;">{escape(loc)}</td></tr><tr><td valign="top" align="left" colspan="2" style="font-size:14px;color:#666666;text-align:left;padding-top:2px;padding-right:10px;">{pdate(e["date"])}<span style="white-space:nowrap;"> • {ptime(e["start"])}</span></td></tr></table>'
                   + (f'<div style="font-size:15px;color:#333333;margin-top:3px;">{escape(det)}</div>' if det else "")
                   + (f'<div style="font-size:14px;margin-top:4px;"><a href="{lk[1]}" style="color:{G};">{lk[0]}</a></div>' if lk else "")
                   + f'<div style="font-size:13px;color:#666666;margin-top:5px;">{src_cal(EVENT_EXTRA_SRC.get(e["name"]))}</div></td></tr>')
    return "".join(out)
def listen(href, size=15):
    return (f'<a href="{href}" style="color:{G};white-space:nowrap;font-size:14px;"><img src="{SPK}" width="24" height="24" alt="" '
            f'style="display:inline-block;width:24px;height:24px;vertical-align:middle;border:0;outline:none;text-decoration:none;margin:-3px 4px -3px 0;">Listen</a>')
def title_row(title, right):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;"><tr><td valign="top" align="left" style="font-size:15px;line-height:18px;font-weight:bold;color:#333333;text-align:left;padding-right:8px;">{title}</td>'
            f'<td valign="top" align="right" style="font-size:13px;line-height:18px;text-align:right;white-space:nowrap;width:1%;">{right}</td></tr></table>')

# ---------- Community Notices (palmhillblast + gotwicz Gmail as of Oct 15) ----------
# (title, text, source label, source href or None, listen href or None)
TONY_FB_PLACEHOLDER = False  # set False Saturday once Tony's wording (due Fri Oct 16, palmhillblast) is pasted below
TONY_FB = ("Join the Palm Hill Residents Group on Facebook", None)  # Tony's wording arrived Fri Oct 16 (palmhillblast); verbatim
FBURL = "https://www.facebook.com/groups/720846344400510"
FBQR = "https://palmhillnews.vercel.app/pages/previews/2026-10-18/assets/fb-group-qr.png"
FBPAGE_NOTICE = "https://palmhillnews.vercel.app/pages/previews/2026-10-18/facebook-group-notice.html"
FBPAGE_DYK = "https://palmhillnews.vercel.app/pages/previews/2026-10-18/facebook-group-did-you-know.html"
TONY_FB_TXT = ('Palm Hill now has a private Facebook group just for residents, with park news, event reminders and photos posted by the admins (comments are turned off). '
    'Every request is checked against the member directory, so use the address and email the Office has for you, answer all 3 questions, or Facebook will turn the request down. '
    f'Search Facebook for &quot;Palm Hill Country Club - Residents Only Group&quot; or join here: <a href="{FBURL}" style="color:{G};">{FBURL}</a>'
    f'<br><a href="{FBPAGE_NOTICE}" style="color:{G};font-size:14px;">Full notice with QR code to scan →</a>')
NOTICES = [
    ("Swimming Pool Food and Beverage Rules",  # Webmaster, Fri Oct 16 12:29 PM ET (gotwicz 1a1458d5b589bff6); newest notice after Tony's
     "All food and beverages must be kept at least 4 feet away from the edge of the pool (the \"wet deck\" area). No glass containers of any kind are permitted inside the fenced pool area; please use plastic or other non-breakable containers. Residents are responsible for ensuring that their guests comply with all pool rules and regulations.",
     "Webmaster", BASE + "2026-10-16-swimming-pool-food-and-beverage-rules-notice.html"),
    ("November Coffee and Pancake Volunteers",
     "An announcing chairperson is needed for November coffees at the North Clubhouse, along with 8 coffee volunteers. Pancakes on Saturday, Nov 14 need 14 volunteers, arriving at 7:30 AM. Sign-up sheets are on the North Clubhouse bulletin board.",
     "Webmaster, Oct 15", None),
    ("Shuffleboard Season Reminders",
     "Please don't walk on the courts; return discs to their holders under the benches and cue sticks to the wall hangers; close windows and turn off lights and fans when you leave. Anyone under 18 must be with an adult, no smoking, and wear closed-toe shoes. On the north courts with embedded beads, don't drop the disc onto the beaded surface — set it outside the playing area and push it forward into the kitchen.",
     "Webmaster (Shuffleboard Club), Oct 12", None),
    ("Taste of Golf — November 18",
     "New golfers and residents are welcome on Wednesday, Nov 18 at 10:00 AM. Meet at the Pro Shop; it's free. Golf teachers on each hole cover etiquette, warm-up, driving, chipping, putting and reading the green, with treats on each hole and a hot dog on the Pro Shop patio. Not a golfer? Walk, watch and enjoy the course. Sign-up sheets are at the Pro Shop and both clubhouses.",
     "Webmaster, Oct 14", None),
    ("Clubhouse Courtesy During Busy Season",
     "Classes and groups are starting up for the season. When you stop at a clubhouse for ice or other errands, please don't disrupt a group meeting in the room you are entering, and follow posted signs.",
     "Webmaster", BASE + "2026-10-08-info-from-linda-notice.html"),
    ("Property Fraud Alert",
     f'The Palm Hill webmaster shared the sign-up link for <a href="https://www.propertyfraudalert.com/select" style="color:{G};">Property Fraud Alert</a>, a free service that notifies you when a document is recorded under your name.',
     "Webmaster", BASE + "2026-09-30-property-fraud-alert-notice.html"),
    ("October Mowing Date",
     "Reminder: BrightView's next tentative resident mowing date is Tuesday, Oct 27. The schedule may change.",
     "RPM", BASE + "2026-09-29-mowing-dates-notice.html"),
]
def notice_rows():
    rows, items = [], [(TONY_FB[0], TONY_FB_TXT, "Tony Ciaramitaro, Communications Chair", None)] + NOTICES
    for i, (t, txt, sl, sh) in enumerate(items):
        ph = t == TONY_FB[0] and TONY_FB_PLACEHOLDER
        lh = (sh + "?listen=1") if sh else None
        right = listen(lh) if lh else listen(ARCH + "main.html", 15).replace(f'href="{ARCH}main.html"', 'href="#listen-pending"')
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
def chair_cards():
    out = []
    # RETENTION (Steven, Oct 16): latest report per committee, shown only if dated within 30 days of the issue; older -> archive only
    from datetime import date as _d, timedelta as _td
    cutoff = (_d(2026, 10, 18) - _td(days=30)).isoformat()
    latest = {}
    for c in sorted(CHAIR, key=lambda c: c[1], reverse=True): latest.setdefault(c[0], c)
    shown = [c for c in latest.values() if c[1] >= cutoff]
    print("chair reports dropped (30-day rule):", [(c[0], c[1]) for c in latest.values() if c[1] < cutoff])
    # President's Message + weekly/monthly Manager reports: stay until replaced by a newer one or Steven overrides (no age cutoff)
    for i, (t, d, s, full, lis) in enumerate(sorted(shown, key=lambda c: c[1], reverse=True)):
        out.append(f'<tr style="background:{bg(i)};page-break-inside:avoid;break-inside:avoid;"><td style="padding:10px 10px;border-bottom:1px solid #ddd;border-left:4px solid #2D5016;">'
                   f'<div style="font-size:16px;font-weight:bold;color:#333333;">{escape(t)}</div>'
                   f'<div style="font-size:14px;color:#666666;margin-top:2px;">{pdate(d)}</div>'
                   f'<div style="font-size:17px;line-height:1.45;color:#333333;margin-top:5px;">{escape(s)}</div>'
                   f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;margin-top:8px;"><tr><td align="left" style="font-size:15px;text-align:left;"><a href="{full}" style="color:{G};white-space:nowrap;">Read Full Report →</a></td><td align="right" style="font-size:15px;text-align:right;white-space:nowrap;width:1%;">{listen(lis)}</td></tr></table></td></tr>')
    out.append(f'<tr><td style="padding:6px 8px;font-size:14px;"><a href="{ARCH}committee-reports.html" style="color:{G};">Committee Report Archives →</a></td></tr>')
    return "".join(out)

# ---------- assemble ----------
s = SEED.read_text(encoding="utf-8")
s = s.replace("<title>", "<title>", 1)
s = re.sub(r"<title>.*?</title>", "<title>PHNEWS October 18, 2026 — DRAFT (not sent)</title>", s, count=1, flags=re.S)
s = s.replace('color:#e5f1d1;">October 18, 2026<', 'color:#e5f1d1;">Sunday, October 18, 2026<')  # batch item 1: weekday in masthead
s = s.replace("October 11, 2026", "October 18, 2026").replace("Vol. 1, No. 13", "Vol. 1, No. 14")
stamp = datetime.now(ZoneInfo("America/New_York")).strftime("%-I:%M %p")
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

# Weekly Manager Update Oct 16 (Megan, palmhillblast Oct 16 3:59 PM ET) replaces Oct 9 (retention rule)
_W_OLD = s[s.find('<div style="font-size:15px;font-weight:bold;color:#333333;">Weekly Manager Update — October 9</div>'):]
_W_OLD = _W_OLD[:_W_OLD.find('</td></tr>')]
assert "Duke Energy Waiver" in _W_OLD
_W_NEW = ('<div style="font-size:15px;font-weight:bold;color:#333333;">Weekly Manager Update — October 16</div>'
    '<div style="font-size:14px;color:#666666;margin-top:2px;">Friday, Oct 16, 2026</div>'
    '<div style="font-size:15px;color:#333333;margin-top:3px;">The invoice for the transformer was paid; installation will take approximately 6 weeks. The sewer liner along Fern was ordered, with installation expected the week of 10/26. New sign with office hours installed at the south clubhouse.</div>'
    f'<div style="margin-top:4px;font-size:14px;line-height:1.6;"><a href="{BASE}2026-10-16-weekly-manager-update.html" style="color:{G};white-space:nowrap;">Read Full Update →</a><span style="color:#999999;"> · </span><a href="{ARCH}weekly-manager-updates.html" style="color:{G};white-space:nowrap;">Past Weekly Manager Updates →</a></div>'
    f'<div style="font-size:13px;color:#666666;margin-top:5px;"><a href="{BASE}2026-10-16-weekly-manager-update.html" style="color:{G};">Source</a>: Weekly Manager Update</div>')
s = s.replace(_W_OLD, _W_NEW)
# Manager reports: Listen icon on the title line (pages have built-in Listen; ?listen=1 autostarts)
for t, href in [("Shareholders Report — September 30 Board Meeting", BASE + "2026-09-30-shareholders-report.html"),
                ("Weekly Manager Update — October 16", BASE + "2026-10-16-weekly-manager-update.html")]:
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
DYK_ITEMS = [("2026-10-16", DYK_FB)]   # newest first; add new items at the top
t0 = s.find("<table", a)
s = s[:t0] + '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 12px 0;">' + DYK_ITEMS[0][1].replace('</td></tr>', f'<div style="font-size:14px;margin-top:4px;"><a href="{ARCH}did-you-know.html" style="color:{G};">Did You Know Archives →</a></div></td></tr>', 1) + s[e:]
# Helpful Webpages + archive footer links -> live /pages/ URLs
s = s.replace(f'<a href="{ARCH}meeting-videos.html" style="color:{G};">Palm Hill Committee Videos</a></div>',
              f'<a href="{ARCH}main.html" style="color:{G};">Palm Hill Newsletter Archives</a></div>\n          <div>• <a href="{ARCH}videos.html" style="color:{G};">Committee Meeting Videos - Latest</a></div>\n          <div>• <a href="{ARCH}meeting-videos.html" style="color:{G};">Committee Meeting Videos - Archives</a></div>')
foot = (f'<p style="font-size:13px;text-align:center;margin:12px 0 0 0;"><a href="{ARCH}main.html" style="color:{G};">All Newsletter Archives →</a>'
        f'<span style="color:#999999;"> · </span><a href="{ARCH}videos.html" style="color:{G};">Latest Meeting Videos →</a>'
        f'<span style="color:#999999;"> · </span><a href="{ARCH}meeting-videos.html" style="color:{G};">Meeting Video Archives →</a></p>')
s = s.replace('    <p style="font-size:12px;color:#666666;font-style:italic;text-align:center;margin-top:16px;">', foot + '\n    <p style="font-size:12px;color:#666666;font-style:italic;text-align:center;margin-top:16px;">', 1)
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import style_rules as _sr  # STYLE-RULES.md (shared)
s = _sr.enforce_title_months(s)  # full months in titles/bands
import link_archive_bullet as _lab; s = _lab.add(s)
import title_dates as _td; s = _td.fix(s)  # STYLE-RULES.md R19 no dates in titles above a date line  # STYLE-RULES.md R14 Helpful Webpages
OUTF.write_text(s, encoding="utf-8")
# STYLE-RULES.md R15: monthly Link save (new Palm Hill Link PDF -> Vercel), non-fatal
import subprocess as _sp2; _lr = _sp2.run([sys.executable, "/workspace/oct18-batch/scripts/fetch_link_pdf.py"], capture_output=True, text=True); print((_lr.stdout or _lr.stderr).strip()[-400:])
json.dump({"calendar_file": CALF, "meetings": [(e["date"], e["name"]) for e in meetings], "this_week": [(e["date"], e["name"]) for e in this_week],
           "upcoming": [(e["date"], e["name"]) for e in upcoming], "stamp": stamp}, open(ROOT / "build-audit-oct18.json", "w"), indent=1)
print("wrote", OUTF, "| meetings", len(meetings), "| this week", len(this_week), "| upcoming", len(upcoming))

