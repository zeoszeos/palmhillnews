"""STYLE-RULES R86 (Steven, Oct 27 2026 1:25 PM, voice; agreed with Tony Ciaramitaro by email Oct 26-27): Tony's Palm Hill club
calendar (booking-system feed) is the single source of truth for meeting dates and times. This report compares every committee
and Board meeting on the calendar with (2) the committees' own agenda emails / report "next meeting" notes and (3) the recorded
RPM calendar values, and flags any difference. Corrective action: the committee must have Tony change the calendar to the
new date right away. Read-only: never writes the calendar, never sends mail.

Run:  python3 scripts/meeting_conflict_report.py --issue 2026-11-01 [--out DIR] [--work DIR]
Writes DIR/meeting-conflicts-<issue>-<stamp>.md, .html, -email.txt, -tony.txt and -tony.html (default DIR = <work>/reports).
-tony.txt (Steven, Oct 27 2026 2:26/2:27 PM): plain-text note for Tony in Steven's voice, real conflicts only; its first line is
always "Subject: " + TONY_SUBJECT (exact, no date, no issue number). -tony.html (Steven, Oct 27 2026 3:17 PM): the same note as
one professional HTML table (inline CSS only). Draft text only -- this script never sends anything.
RPM (Steven, Oct 27 2026 3:16 PM): the RPM values must be a timely live read (rpm_fetched in the sources file), never old notes."""
import argparse, glob, html, json, os, re, sys
from datetime import date, datetime, timedelta
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "builder/core"))
COLS = ["Committee/Meeting", "Calendar date", "Calendar time", "Agenda / committee-report suggested date (time, source)",
        "RPM calendar date (time)", "Agenda notice email date", "Calendar recurring", "RPM recurring", "What differs"]
TONY_SUBJECT = "Calendar Mismatches Report"   # R86 (Steven, Oct 27 2026 2:27 PM): every conflict email to Tony uses exactly this subject
# RPM (Steven Oct 27 2026 2:43 PM): reference only, to spot dates missing from the calendar; never overrides, never counted on calendar dates.
ACTION = "Corrective action: the committee must have Tony change the calendar to the new date right away (the calendar always rules)."
def fd(d): return datetime.strptime(d, "%Y-%m-%d").strftime("%a %b %-d, %Y") if d else "—"
def ft(t):
    if not t: return "—"
    h, m = map(int, t.split(":")); return f"{(h % 12) or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"
def ftr(s, e): return ft(s) + (" to " + ft(e) if e else "")
WINDOW_DAYS = 60
def load_cal(work):
    fs = sorted(glob.glob(str(Path(work) / "data/cal-*.json")))
    if not fs: raise SystemExit("R86: no calendar snapshot data/cal-*.json in " + str(work))
    cal = json.load(open(fs[-1], encoding="utf-8"))
    # extension snapshot (same feed, later range, e.g. January for the Annual Meeting): newest data/calx-*.json, events after cal's end only
    xs = sorted(glob.glob(str(Path(work) / "data/calx-*.json")))
    if xs:
        x = json.load(open(xs[-1], encoding="utf-8")); end = max(e["date"] for e in cal["events"])
        cal = dict(cal, events=cal["events"] + [e for e in x["events"] if e["date"] > end], ext=os.path.basename(xs[-1]))
    return fs[-1], cal
def committee_of(name, comm):
    for k, rx in comm.items():
        if re.search(rx, name, re.I): return k
def build(issue, work, repo=REPO):
    src = json.load(open(repo / "builder/data/meeting-conflict-sources.json", encoding="utf-8"))
    import issue_ctx; C = issue_ctx.load(issue)
    calf, cal = load_cal(work); comm = src["committees"]
    since = min(issue, date.today().isoformat())   # still-upcoming meetings before the issue date are compared too
    until = (date.today() + timedelta(days=WINDOW_DAYS)).isoformat()   # Steven Nov 2 2026 8:19 AM: ANY committee/board meeting in the next 60 days
    cal = dict(cal, events=[e for e in cal["events"] if e["date"] <= until]); src = dict(src, rpm=[r for r in src["rpm"] if r["date"] <= until], agenda=[a for a in src["agenda"] if a["date"] <= until])
    mtgs = [e for e in cal["events"] if committee_of(e["name"], comm) and e["date"] >= since and e.get("status") != "RESCHEDULED"]
    moved = [e for e in cal["events"] if committee_of(e["name"], comm) and e["date"] >= since and e.get("status") == "RESCHEDULED"]
    notes = {}   # builder-side TBC notes on calendar-confirmed meetings (MTG_EXTRA / MTG_NOTE)
    for x in getattr(C, "MTG_EXTRA", []): notes[(src["extra_committee"].get(x["name"], x["name"]), x["date"])] = f"builder MTG_EXTRA adds {x['name']} {fd(x['date'])} {x.get('note', '')}".strip()
    for (d, n), v in getattr(C, "MTG_NOTE", {}).items(): notes[(committee_of(n, comm), d)] = f"builder MTG_NOTE {v}"
    ovr = {src["override_committee"].get(k, k): v for k, v in C.MTG_OVERRIDE.items()}
    month = lambda d: d[:7]
    rows, used_a, used_r = [], set(), set()
    for e in sorted(mtgs, key=lambda e: (e["date"], e["start"])):
        k = committee_of(e["name"], comm); ag = [(i, a) for i, a in enumerate(src["agenda"]) if a["committee"] == k and month(a["date"]) == month(e["date"])]
        rp = [(i, r) for i, r in enumerate(src["rpm"]) if r["committee"] == k and month(r["date"]) == month(e["date"])]
        used_a |= {i for i, _ in ag}; used_r |= {i for i, _ in rp}
        rows.append(dict(committee=k, name=e["name"], cal_date=e["date"], cal_time=e["start"], cal_end=e.get("end"), recurring=e.get("recurring"),
                         agenda=[a for _, a in ag], rpm=[r for _, r in rp], override=ovr.get(k), note=notes.get((k, e["date"]))))
    for i, r in enumerate(src["rpm"]):   # RPM entries with no calendar meeting that month
        if i not in used_r and r["date"] >= since:
            rows.append(dict(committee=r["committee"], name=r["committee"] + " (RPM only)", cal_date=None, cal_time=None, cal_end=None, recurring=None, agenda=[], rpm=[r], override=None, note=None))
    for i, a in enumerate(src["agenda"]):
        if i not in used_a and a["date"] >= since:
            rows.append(dict(committee=a["committee"], name=a["committee"] + " (agenda only)", cal_date=None, cal_time=None, cal_end=None, recurring=None, agenda=[a], rpm=[], override=ovr.get(a["committee"]), note=None))
    for r in rows:   # verbatim check + differences
        diffs, refs = [], []   # refs = reference-only notes (known typos, RPM day notes): shown, never counted (R86, Oct 27 2:43 PM)
        for a in r["agenda"]:
            t = (repo / a["page"]).read_text(encoding="utf-8") if (repo / a["page"]).exists() else ""
            if html.unescape(a["quote"]) not in re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))): raise SystemExit(f"R86: quote not found in {a['page']}: {a['quote']!r}")
            at = (a.get("typo") or {}).get("time", a["time"])
            if a.get("typo"): refs.append(("Agenda: known typo", f'The {a["kind"]} says "{a["quote"]}": {a["typo"]["note"]}.'))
            day = r["cal_date"] != a["date"]; tm = bool(at) and r["cal_time"] and at != r["cal_time"]
            if day or tm: diffs.append(("Agenda: " + ("both (day and time)" if day and tm else "day" if day else "time"),
                f"The calendar date is {fd(r['cal_date'])}, the calendar time is {ft(r['cal_time'])}, the agenda information is different "
                f"(agenda says {fd(a['date'])}{', ' + ft(a['time']) if a['time'] else ''}; {a['kind']}, {a['page'].split('/')[-1]})."))
        for p in r["rpm"]:
            if not r["cal_date"]: continue
            dd, td = r["cal_date"] != p["date"], r["cal_time"] != p.get("time")
            if dd or td: refs.append(("RPM note (reference only): " + ("day and time" if dd and td else "day" if dd else "time"),
                f"The calendar says {fd(r['cal_date'])}, {ftr(r['cal_time'], r.get('cal_end'))}; RPM says {fd(p['date'])}, {ftr(p.get('time'), p.get('end'))}. RPM is reference only (it never overrides the calendar)."))
        if r["cal_date"] and not r["rpm"]: refs.append(("RPM note (reference only): not on RPM", f"The calendar has {fd(r['cal_date'])}, {ftr(r['cal_time'], r.get('cal_end'))}; RPM has no entry for this meeting that month."))
        if not r["cal_date"]: diffs.insert(0, ("Not on the Palm Hill calendar", "No meeting for this committee on the Palm Hill calendar that month; " + ("RPM lists " + ", ".join(fd(p["date"]) + ", " + ftr(p.get("time"), p.get("end")) for p in r["rpm"]) if r["rpm"] else "only the agenda/report lists it") + ". If the meeting is real, the committee must ask Tony to add it to the calendar."))
        if r.get("note") and r["cal_date"]: diffs.append(("Builder note", f"The calendar has this meeting CONFIRMED, but the content file still adds a note: {r['note']}. Under R86 the calendar rules."))
        if r["override"]: diffs.insert(0, ("CONFLICT-OVERRIDDEN-BY-RULE", f"Nov 1 rows still use the locked R62/R62b override (" + ", ".join(f"{k} {fd(v) if k == 'date' else ft(v)}" for k, v in r['override'].items()) + ") until Steven releases R62/R62b/R62c."))
        r["diffs"], r["refs"] = diffs, refs
    if not src.get("rpm_fetched"): raise SystemExit("R86: RPM values need a live-read stamp (rpm_fetched); old notes are not acceptable (Steven Oct 27 3:16 PM)")
    return dict(issue=issue, calf=calf, cal=cal, comm=comm, rpm_fetched=src["rpm_fetched"], emails_searched=src.get("emails_searched"), rows=rows, moved=moved, overrides=ovr)
def cells(r):
    ag = "; ".join(f"{fd(a['date'])}{', ' + ft(a['time']) if a['time'] else ''} ({a['kind']}, {a['page'].split('/')[-1]})" for a in r["agenda"]) or "—"
    rp = "; ".join(f"{fd(p['date'])} ({ftr(p.get('time'), p.get('end'))})" for p in r["rpm"]) or "—"
    em = "; ".join(a["email_date"] for a in r["agenda"]) or "—"
    rec = "—" if r["recurring"] is None else ("☑" if r["recurring"] else "☐")
    rrec = " ".join("☑" if p.get("recurring") else "☐" for p in r["rpm"]) or "—"
    st = ("; ".join(k for k, _ in r["diffs"]) or "match") + "".join(f" [{k}]" for k, _ in r["refs"])
    return [r["name"], fd(r["cal_date"]), ft(r["cal_time"]), ag, rp, em, rec, rrec, st]
NOTES = ["The Palm Hill calendar (Tony Ciaramitaro's booking-system feed) is the single source of truth (R86).",
         "RPM values: {rpm_fetched} (signed-in box browser session, Agenda view). RPM shows start and end times.",
         "RPM is reference only: it helps spot meetings missing from the Palm Hill calendar and never overrides it. RPM day differences on calendar meetings are 'RPM note (reference only)' and are not counted; RPM-only meetings stay as items.",
         "Calendar recurring: ☑ = the calendar marks the entry as part of a recurring series, ☐ = not recurring (the feed's own 'recurring' marker).",
         "RPM recurring: ☑ = RPM month view shows its circular-arrow recurring icon on the entry, ☐ = no icon.",
         ACTION]
def notes(R): return [n.replace("{rpm_fetched}", R["rpm_fetched"]) for n in NOTES]
def render(R, stamp):
    R["rows"].sort(key=lambda r: (r["cal_date"] or min(x["date"] for x in r["rpm"] + r["agenda"]), r["cal_time"] or "")); rows = [cells(r) for r in R["rows"]]; conf = [r for r in R["rows"] if r["diffs"]]
    head = f"PHNEWS meeting conflict report, issue {R['issue']} (run {stamp} ET)\nCalendar snapshot: {os.path.basename(R['calf'])} (pulled {R['cal'].get('start')}..{R['cal'].get('end')} window{', plus ' + R['cal']['ext'] + ' for later dates' if R['cal'].get('ext') else ''})\nRPM: {R['rpm_fetched']}"
    moved = [f"{e['name']} {fd(e['date'])}: calendar marks RESCHEDULED, moved to {e.get('movedTo')}" for e in R["moved"]]
    md = [f"# {head.splitlines()[0]}", "", *head.splitlines()[1:], "", f"**{len(conf)} of {len(rows)} meetings need attention.**", "",
          "| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)] + ["| " + " | ".join(c.replace("|", "/") for c in x) + " |" for x in rows]
    md += ["", "## Mismatches in plain words", ""] + [f"- **{r['name']}**: " + " ".join(t for _, t in r["diffs"]) for r in conf]
    md += ["", "## Reference notes (not counted)", ""] + [f"- **{r['name']}**: " + " ".join(t for _, t in r["refs"]) for r in R["rows"] if r["refs"]]
    md += ["", "## Calendar moves", ""] + [f"- {m}" for m in moved] + ["", "## Notes", ""] + [f"- {n}" for n in notes(R)]
    h = ["<!doctype html><meta charset='utf-8'><title>PHNEWS meeting conflicts " + R["issue"] + "</title>",
         "<style>body{font-family:Arial,sans-serif;max-width:1200px;margin:20px auto;color:#333}table{border-collapse:collapse;font-size:13px}"
         "th,td{border:1px solid #ccc;padding:5px;vertical-align:top;text-align:left}th{background:#2D5016;color:#fff}tr.c td{background:#FFF7E0}</style>",
         f"<h1>{html.escape(head.splitlines()[0])}</h1><p>{'<br>'.join(html.escape(x) for x in head.splitlines()[1:])}</p><p><b>{len(conf)} of {len(rows)} meetings need attention.</b></p>",
         "<table><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in COLS) + "</tr>"]
    h += [f"<tr{' class=c' if r['diffs'] else ''}>" + "".join(f"<td>{html.escape(c)}</td>" for c in x) + "</tr>" for r, x in zip(R["rows"], rows)]
    h += ["</table><h2>Mismatches in plain words</h2><ul>"] + [f"<li><b>{html.escape(r['name'])}</b>: {html.escape(' '.join(t for _, t in r['diffs']))}</li>" for r in conf]
    h += ["</ul><h2>Reference notes (not counted)</h2><ul>"] + [f"<li><b>{html.escape(r['name'])}</b>: {html.escape(' '.join(t for _, t in r['refs']))}</li>" for r in R["rows"] if r["refs"]]
    h += ["</ul><h2>Calendar moves</h2><ul>"] + [f"<li>{html.escape(m)}</li>" for m in moved] + ["</ul><h2>Notes</h2><ul>"] + [f"<li>{html.escape(n)}</li>" for n in notes(R)] + ["</ul>"]
    tx = [head, "", f"{len(conf)} of {len(rows)} meetings need attention.", ""]
    for r, x in zip(R["rows"], rows):
        tx += [f"{COLS[i]}: {v}" for i, v in enumerate(x)]
        tx += ["   " + t for _, t in r["diffs"]] + ["   (reference only) " + t for _, t in r["refs"]] + [""]
    tx += ["Calendar moves:"] + ["- " + m for m in moved] + ["", "Notes:"] + ["- " + n for n in notes(R)]
    return "\n".join(md) + "\n", "\n".join(h) + "\n", "\n".join(tx) + "\n"
TONY_COLS = ["Meeting", "Palm Hill calendar", "RPM calendar", "Palm Hill recurring", "RPM recurring", "Mismatch"]
def _ct(t):   # compact time: 10 AM, 12:30 PM
    h, m = map(int, t.split(":")); return f"{(h % 12) or 12}{'' if m == 0 else ':%02d' % m} {'AM' if h < 12 else 'PM'}"
def _ctr(s, e): return _ct(s)   # Steven Nov 1 2026 10:30 PM: Tony table shows the start time only (end times still compared in the data)
def _onoff(v): return "n/a" if v is None else ("On" if v else "Off")   # Steven Nov 1 2026 10:29 PM: n/a, not a dash
def tony_rows(R):
    """Rows for Tony (Steven, Oct 27 2026 3:16/3:17 PM; simplified 11:40 PM): one row per meeting with a difference. Columns: the Palm Hill
    calendar, RPM, what the agenda says, the recurring flag on each calendar (On/Off), and a plain 'Mismatch' reason. Known typos are left
    out. Source wording only; the calendar always rules (the intro says so)."""
    def sd(d): return datetime.strptime(d, "%Y-%m-%d").strftime("%a %b %-d" + (", %Y" if d[:4] != R["issue"][:4] else ""))
    out = []
    for r in R["rows"]:
        ag = [a for a in r["agenda"] if r["cal_date"] != a["date"] or ((a.get("typo") or {}).get("time", a["time"]) and r["cal_time"] and (a.get("typo") or {}).get("time", a["time"]) != r["cal_time"])]
        rp = [p for p in r["rpm"] if r["cal_date"] and (r["cal_date"] != p["date"] or r["cal_time"] != p.get("time"))]
        no_rpm = bool(r["cal_date"]) and not r["rpm"]
        # R105 (Steven Nov 1 2026 10:13 PM): every meeting is listed and colour-coded (green match / amber reference-only / red conflict)
        cal = "Not on the calendar" if not r["cal_date"] else f"{sd(r['cal_date'])}, {_ctr(r['cal_time'], r.get('cal_end'))}"
        mv = [e for e in R["moved"] if committee_of(e["name"], R["comm"]) == r["committee"] and (e.get("movedTo") or "").startswith(r["cal_date"] or "x")]
        if mv: cal += f" (moved from {sd(mv[0]['date'])})"
        agt = "; ".join(f"{sd(a['date'])}{', ' + _ct(a['time']) if a['time'] else ''} (notice email {a['email_date'].split(', 2026')[0]})" for a in ag) or "\u2014"
        rpt = "; ".join(f"{sd(p['date'])}, {_ctr(p.get('time'), p.get('end'))}" for p in (r["rpm"] if (rp or not r["cal_date"]) else [])) or ("Not on calendar" if no_rpm else "Same as calendar")   # Steven Nov 1 2026 10:36 PM
        why = []
        # Steven Nov 2 2026 12:07 AM: "Don't mention agenda date" -- agenda differences still make the row red, but are not named
        # R105f (Steven Nov 4 2026 4:26 PM): Palm Hill is the source of truth; each phrase names the calendar that is off and the Palm Hill value
        phv = f"{sd(r['cal_date'])}, {_ct(r['cal_time'])}" if r["cal_date"] else ""
        if not r["cal_date"]: why.append("Palm Hill is missing this meeting - RPM has " + "; ".join(f"{sd(p['date'])}, {_ct(p.get('time'))}" for p in r["rpm"]) if r["rpm"] else "Palm Hill is missing this meeting")
        for p in rp:
            why.append(f"RPM is off - RPM still has the old date, {sd(p['date'])} (Palm Hill moved it to {sd(r['cal_date'])})" if mv else f"RPM is off - RPM has {sd(p['date'])}, {_ct(p.get('time'))}; Palm Hill has {phv}")
        if no_rpm: why.append(f"RPM is missing this meeting (Palm Hill has {phv})")
        # Steven Nov 1 2026 10:32 PM: recurring flags are display-only; they never make a mismatch (inferred from his Golf = Match expectation)
        level = "red" if (ag or (not r["cal_date"] and r["agenda"])) else "amber" if why else "green"
        cat = 0 if ag else 1 if not r["cal_date"] else 3 if (no_rpm or r["committee"] == "Annual Meeting") else 2
        out.append(dict(cat=cat, sortdate=r["cal_date"] or r["rpm"][0]["date"], meeting=(r["rpm"][0].get("rpm_name") or r["committee"]) if not r["cal_date"] and r["rpm"] else r["name"].replace(" (agenda only)", ""),
                        calendar=cal, rpm=rpt, agenda=agt, phrec=_onoff(r["recurring"]), rpmrec=" / ".join(_onoff(p.get("recurring")) for p in r["rpm"]) or "n/a",
                        level=level, mismatch=LEVEL_LABEL[level] + ((("; " if level == "red" else ": ") + "; ".join(why)) if why else "")))
    return sorted(out, key=lambda x: (("red", "amber", "green").index(x["level"]), x["sortdate"]))   # Steven Oct 27 3:27 PM: agenda conflict, not on calendar, RPM differences, FYI
# R105 (Steven Nov 1 2026 10:13 PM): colour code; the text label keeps the meaning without colour.
LEVEL_LABEL = {"red": "Conflict", "amber": "Check", "green": "Match"}
LEVEL_ROW = {"red": "#fde2e1", "amber": "#fff3cd", "green": "#e6f4ea"}
TEXT_DARK, MUTED_DARK = "#1f1f1f", "#4a4a4a"   # R108: explicit dark text (>= 4.5:1 on every row colour)
LEVEL_BADGE = {"red": "#b3261e", "amber": "#8a5a00", "green": "#1e6b34"}
COLOR_KEY = ("Color key (only the date and start time are compared): green = Match (all sources agree); amber = Check (reference-only difference in date or start time, or not on RPM); "
             "red = Conflict (a committee source gives a different date or time than the Palm Hill calendar); pink = not on the Palm Hill calendar.")
NOT_ON_CAL_BG, NOT_ON_CAL_FG = "#F8BBD9", "#880E4F"   # Steven Nov 1 2026 10:31 PM (final): pink "Not on the calendar" cells, distinct from red Conflict
# Steven Nov 1 2026 10:33/10:34 PM: "Notes for Tony" block under the colour key (exact wording). Note 1's wording was never
# received by this build, so only Note 2 is listed until Steven gives Note 1.
# Steven Nov 1 2026 10:35 PM: each Meeting cell links to the club calendar page (the same URL the newsletter's Calendar links use)
CLUB_CALENDAR_URL = "https://www.palmhillcountryclub.net/calendar-1/"
NOTES_FOR_TONY_LABEL = "Notes for Tony"
NOTES_FOR_TONY = ["Note 1: Different end times between sources used to cause mismatches. A row now counts as a Match when the Palm Hill calendar and RPM have the same date and the same start time; end times are ignored.",
                  "Note 2: n/a in the RPM recurring column means there is no calendar date in RPM for this event. n/a in the Palm Hill recurring column means there is no Palm Hill calendar event, though that is also stated in the Palm Hill column itself. n/a replaces the dashes used before, to show whether the event is on each calendar."]   # Steven Nov 1 2026 10:40 PM: Note 1 first; Note 2 + n/a clause
def th_text(c):
    """Steven Nov 1 2026 10:38 PM: two-line headers ("Palm Hill<br>calendar", "RPM<br>recurring") so the table is narrower."""
    return "<br>".join(html.escape(x) for x in c.rsplit(" ", 1)) if " " in c else html.escape(c)
def run_lines(R):
    """R105b (Steven Nov 1 2026 10:18 PM): report run time, calendar pull time and RPM read time at the top."""
    m = re.search(r"cal-(\d{8})-(\d{4})", os.path.basename(R["calf"]))
    pull = datetime.strptime("".join(m.groups()), "%Y%m%d%H%M").strftime("%a %b %-d, %Y, %-I:%M %p") + " ET" if m else os.path.basename(R["calf"])
    rpm = R["rpm_fetched"].split(", live")[0]; rpm = re.sub(r", \d{4},", ",", rpm)
    return [f"Report run: {R['run']} ET", f"Palm Hill calendar pulled {pull}", f"RPM read {rpm}"]
# R109 (Steven Nov 4 2026 5:02 PM): "Refresh date" line + what the refresh covers. Built only from the real stamps; a source whose
# stamp is older than FRESH_MINUTES before the run (or has no stamp) is never called refreshed -- its real time is shown instead.
FRESH_MINUTES = 30
def _stamp_dt(txt):
    m = re.search(r"([A-Z][a-z]{2} [A-Z][a-z]{2} \d{1,2}, \d{4}),? (?:about |at about )?(\d{1,2}:\d{2} [AP]M)", txt or "")
    return datetime.strptime(m.group(1) + " " + m.group(2), "%a %b %d, %Y %I:%M %p") if m else None
def refresh_block(R):
    run = datetime.strptime(R["run"], "%a %b %d, %Y, %I:%M %p")
    m = re.search(r"cal-(\d{8})-(\d{4})", os.path.basename(R["calf"]))
    srcs = [("Palm Hill calendar", "reviewed", datetime.strptime("".join(m.groups()), "%Y%m%d%H%M") if m else None, ""),
            ("RPM calendar", "reviewed", _stamp_dt(R["rpm_fetched"]), "about " if "about" in R["rpm_fetched"] else ""),
            ("Committee and board emails that may mention a meeting date", "checked", _stamp_dt(R.get("emails_searched")), "about " if "about" in (R.get("emails_searched") or "") else "")]
    subs, fresh = [], []
    for name, verb, t, ab in srcs:
        ok = t is not None and timedelta(0) <= run - t <= timedelta(minutes=FRESH_MINUTES); fresh.append(ok)
        if ok: subs.append(f"{name}: {verb} for this run at {ab}{t.strftime('%-I:%M %p')} ET.")
        elif t is None: subs.append(f"{name}: not refreshed at this run (no time was recorded for the last time they were {verb}).")
        else: subs.append(f"{name}: not refreshed at this run; last {verb} {t.strftime('%a %b %-d, %Y, %-I:%M %p')} ET.")
    return f"Refresh date: {run.strftime('%a %b %-d, %Y')}, for the report run at {run.strftime('%-I:%M %p')} ET", subs, fresh
TONY_KEYS = ("calendar", "rpm", "phrec", "rpmrec", "mismatch")
def _intro(R):
    idate = datetime.strptime(R["issue"], "%Y-%m-%d").strftime("%B %-d")
    return (f"Here is how each upcoming meeting compares between the Palm Hill calendar and RPM (read live {R['rpm_fetched'].split(', live')[0].replace('about ', 'at about ')}); the colors show what needs attention. "
            f"The {idate} newsletter prints the Palm Hill calendar date and time for each.")
def render_tony(R):
    """Plain-text version of the Tony email (Steven's voice)."""
    rows = tony_rows(R)
    rl, rs, _ = refresh_block(R)
    tx = [f"Subject: {TONY_SUBJECT}", ""] + run_lines(R) + ["", rl] + [f"  - {x}" for x in rs] + ["", "Hi Tony,", "", _intro(R), ""]
    for x in rows:
        tx += [x["meeting"]] + [f"  {c}: {x[k]}" for c, k in zip(TONY_COLS[1:], TONY_KEYS)] + [""]
    if not rows: tx += ["No differences this time. Everything matches the calendar.", ""]
    tx += [COLOR_KEY, "", NOTES_FOR_TONY_LABEL] + NOTES_FOR_TONY + [""]
    tx += ["Thanks,", "Steven"]
    return "\n".join(tx) + "\n"
def render_tony_html(R):
    """HTML version: one clean table, inline CSS only (email-safe), header row shaded, 14px, mobile friendly."""
    rows = tony_rows(R); e = html.escape
    # R108 (Steven Nov 4 2026 4:53 PM, iPhone Gmail dark mode screenshot): every cell, link and paragraph carries an explicit dark text
    # colour and its row background (style + bgcolor), and the head says "light only" (R97/R98 email_dark_mode approach).
    import email_dark_mode as _edm
    bgp = _edm.EMAIL_TINT
    th = "background:#2D5016;color:#ffffff;font-weight:bold;text-align:left;padding:7px 8px;border:1px solid #2D5016;font-size:14px;"
    td = f"color:{TEXT_DARK};padding:7px 8px;border:1px solid #d0d7cc;vertical-align:top;font-size:14px;line-height:1.4;"
    h = [f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{e(TONY_SUBJECT)}</title>{_edm.HEAD_ADD}</head>",
         f"<body bgcolor='{bgp}' style='margin:0;padding:16px;background:{bgp};font-family:Arial,Helvetica,sans-serif;font-size:14px;color:{TEXT_DARK};'>",
         f"<p style='margin:0 0 14px;font-size:12px;color:{MUTED_DARK};line-height:1.5;'>" + "<br>".join(e(x) for x in run_lines(R)) + "</p>",
         f"<p style='margin:0 0 4px;font-size:13px;font-weight:bold;color:{TEXT_DARK};'>{e(refresh_block(R)[0])}</p>",
         f"<ul style='margin:0 0 14px;padding-left:20px;font-size:12px;line-height:1.5;color:{MUTED_DARK};'>" + "".join(f"<li style='color:{MUTED_DARK};'>{e(x)}</li>" for x in refresh_block(R)[1]) + "</ul>",
         f"<p style='margin:0 0 12px;font-size:14px;color:{TEXT_DARK};'>Hi Tony,</p>", f"<p style='margin:0 0 16px;font-size:14px;line-height:1.5;color:{TEXT_DARK};'>{e(_intro(R))}</p>",
         "<div style='overflow-x:auto;-webkit-overflow-scrolling:touch;'>",
         "<table role='table' cellpadding='0' cellspacing='0' style='border-collapse:collapse;width:100%;min-width:680px;max-width:900px;'>",
         "<tr>" + "".join(f"<th bgcolor='#2D5016' style='{th}width:{wd}%;'>{th_text(c)}</th>" for c, wd in zip(TONY_COLS, (18, 20, 20, 10, 10, 22))) + "</tr>"]
    for i, x in enumerate(rows):
        bg = LEVEL_ROW[x["level"]]; bd = LEVEL_BADGE[x["level"]]
        cells = "".join(f"<td bgcolor='{NOT_ON_CAL_BG}' style='{td}background:{NOT_ON_CAL_BG};color:{NOT_ON_CAL_FG};font-weight:bold;' data-notoncal='1'>{e(x[k])}</td>" if k == "calendar" and x[k] == "Not on the calendar"
                        else f"<td bgcolor='{bg}' style='{td}background:{bg};'>{e(x[k])}</td>" for k in TONY_KEYS[:-1])
        cells += f"<td bgcolor='{bg}' style='{td}background:{bg};border-left:5px solid {bd};color:{bd};font-weight:bold;' data-level='{x['level']}'>{e(x['mismatch'])}</td>"
        h.append(f"<tr bgcolor='{bg}' style='background:{bg};'>" + f"<td bgcolor='{bg}' style='{td}background:{bg};font-weight:bold;'><a href='{CLUB_CALENDAR_URL}' style='color:#1a4d0f;text-decoration:underline;'>{e(x['meeting'])}</a></td>" + cells + "</tr>")
    if not rows: h.append(f"<tr><td colspan='6' bgcolor='{bgp}' style='{td}background:{bgp};'>No differences this time. Everything matches the calendar.</td></tr>")
    h += ["</table></div>", f"<p style='margin:8px 0 0;font-size:12px;color:{MUTED_DARK};'>{e(COLOR_KEY)}</p>", f"<p style='margin:12px 0 4px;font-size:13px;font-weight:bold;color:{TEXT_DARK};'>{e(NOTES_FOR_TONY_LABEL)}</p>", *[f"<p style='margin:0 0 6px;font-size:13px;line-height:1.4;color:{TEXT_DARK};'>{e(n)}</p>" for n in NOTES_FOR_TONY],
          f"<p style='margin:12px 0 0;font-size:14px;color:{TEXT_DARK};'>Thanks,<br>Steven</p>", "</body></html>"]
    return "\n".join(h) + "\n"
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--issue", required=True); ap.add_argument("--work"); ap.add_argument("--out"); ap.add_argument("--run-stamp", help="YYYYMMDD-HHMM: reuse an earlier run time when re-rendering the same data")
    a = ap.parse_args(argv); os.environ["PHNEWS_ISSUE"] = a.issue
    import issue_ctx; C = issue_ctx.load(a.issue)
    work = Path(a.work or os.environ.get("PHNEWS_WORK") or C.DEFAULT_WORK); out = Path(a.out or work / "reports"); out.mkdir(parents=True, exist_ok=True)
    now = datetime.strptime(a.run_stamp, "%Y%m%d-%H%M") if a.run_stamp else datetime.now()
    R = build(a.issue, work); R["run"] = now.strftime("%a %b %-d, %Y, %-I:%M %p"); stamp = now.strftime("%Y-%m-%d %H:%M")
    md, h, tx = render(R, stamp); base = out / f"meeting-conflicts-{a.issue}-{now.strftime('%Y%m%d-%H%M')}"
    for ext, s in ((".md", md), (".html", h), ("-email.txt", tx), ("-tony.txt", render_tony(R)), ("-tony.html", render_tony_html(R))): Path(str(base) + ext).write_text(s, encoding="utf-8")
    print(f"R86 report: {base}.md / .html / -email.txt / -tony.txt / -tony.html ({sum(1 for r in R['rows'] if r['diffs'])} of {len(R['rows'])} need attention)")
    return R, base
if __name__ == "__main__": main()
