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
from datetime import date, datetime
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "builder/core"))
COLS = ["Committee/Meeting", "Calendar date", "Calendar time", "Agenda / committee-report suggested date (time, source)",
        "RPM calendar date (time)", "Agenda notice email date", "Calendar recurring", "RPM recurring", "What differs"]
TONY_SUBJECT = "Calendar Conflicts Report"   # R86 (Steven, Oct 27 2026 2:27 PM): every conflict email to Tony uses exactly this subject
# RPM (Steven Oct 27 2026 2:43 PM): reference only, to spot dates missing from the calendar; never overrides, never counted on calendar dates.
ACTION = "Corrective action: the committee must have Tony change the calendar to the new date right away (the calendar always rules)."
def fd(d): return datetime.strptime(d, "%Y-%m-%d").strftime("%a %b %-d, %Y") if d else "—"
def ft(t):
    if not t: return "—"
    h, m = map(int, t.split(":")); return f"{(h % 12) or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"
def ftr(s, e): return ft(s) + (" to " + ft(e) if e else "")
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
            dd, td = r["cal_date"] != p["date"], (r["cal_time"], r.get("cal_end")) != (p.get("time"), p.get("end"))
            if dd or td: refs.append(("RPM note (reference only): " + ("day and time" if dd and td else "day" if dd else "time"),
                f"The calendar says {fd(r['cal_date'])}, {ftr(r['cal_time'], r.get('cal_end'))}; RPM says {fd(p['date'])}, {ftr(p.get('time'), p.get('end'))}. RPM is reference only (it never overrides the calendar)."))
        if r["cal_date"] and not r["rpm"]: refs.append(("RPM note (reference only): not on RPM", f"The calendar has {fd(r['cal_date'])}, {ftr(r['cal_time'], r.get('cal_end'))}; RPM has no entry for this meeting that month."))
        if not r["cal_date"]: diffs.insert(0, ("Not on the Palm Hill calendar", "No meeting for this committee on the Palm Hill calendar that month; " + ("RPM lists " + ", ".join(fd(p["date"]) + ", " + ftr(p.get("time"), p.get("end")) for p in r["rpm"]) if r["rpm"] else "only the agenda/report lists it") + ". If the meeting is real, the committee must ask Tony to add it to the calendar."))
        if r.get("note") and r["cal_date"]: diffs.append(("Builder note", f"The calendar has this meeting CONFIRMED, but the content file still adds a note: {r['note']}. Under R86 the calendar rules."))
        if r["override"]: diffs.insert(0, ("CONFLICT-OVERRIDDEN-BY-RULE", f"Nov 1 rows still use the locked R62/R62b override (" + ", ".join(f"{k} {fd(v) if k == 'date' else ft(v)}" for k, v in r['override'].items()) + ") until Steven releases R62/R62b/R62c."))
        r["diffs"], r["refs"] = diffs, refs
    if not src.get("rpm_fetched"): raise SystemExit("R86: RPM values need a live-read stamp (rpm_fetched); old notes are not acceptable (Steven Oct 27 3:16 PM)")
    return dict(issue=issue, calf=calf, cal=cal, comm=comm, rpm_fetched=src["rpm_fetched"], rows=rows, moved=moved, overrides=ovr)
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
    md += ["", "## Conflicts in plain words", ""] + [f"- **{r['name']}**: " + " ".join(t for _, t in r["diffs"]) for r in conf]
    md += ["", "## Reference notes (not counted)", ""] + [f"- **{r['name']}**: " + " ".join(t for _, t in r["refs"]) for r in R["rows"] if r["refs"]]
    md += ["", "## Calendar moves", ""] + [f"- {m}" for m in moved] + ["", "## Notes", ""] + [f"- {n}" for n in notes(R)]
    h = ["<!doctype html><meta charset='utf-8'><title>PHNEWS meeting conflicts " + R["issue"] + "</title>",
         "<style>body{font-family:Arial,sans-serif;max-width:1200px;margin:20px auto;color:#333}table{border-collapse:collapse;font-size:13px}"
         "th,td{border:1px solid #ccc;padding:5px;vertical-align:top;text-align:left}th{background:#2D5016;color:#fff}tr.c td{background:#FFF7E0}</style>",
         f"<h1>{html.escape(head.splitlines()[0])}</h1><p>{'<br>'.join(html.escape(x) for x in head.splitlines()[1:])}</p><p><b>{len(conf)} of {len(rows)} meetings need attention.</b></p>",
         "<table><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in COLS) + "</tr>"]
    h += [f"<tr{' class=c' if r['diffs'] else ''}>" + "".join(f"<td>{html.escape(c)}</td>" for c in x) + "</tr>" for r, x in zip(R["rows"], rows)]
    h += ["</table><h2>Conflicts in plain words</h2><ul>"] + [f"<li><b>{html.escape(r['name'])}</b>: {html.escape(' '.join(t for _, t in r['diffs']))}</li>" for r in conf]
    h += ["</ul><h2>Reference notes (not counted)</h2><ul>"] + [f"<li><b>{html.escape(r['name'])}</b>: {html.escape(' '.join(t for _, t in r['refs']))}</li>" for r in R["rows"] if r["refs"]]
    h += ["</ul><h2>Calendar moves</h2><ul>"] + [f"<li>{html.escape(m)}</li>" for m in moved] + ["</ul><h2>Notes</h2><ul>"] + [f"<li>{html.escape(n)}</li>" for n in notes(R)] + ["</ul>"]
    tx = [head, "", f"{len(conf)} of {len(rows)} meetings need attention.", ""]
    for r, x in zip(R["rows"], rows):
        tx += [f"{COLS[i]}: {v}" for i, v in enumerate(x)]
        tx += ["   " + t for _, t in r["diffs"]] + ["   (reference only) " + t for _, t in r["refs"]] + [""]
    tx += ["Calendar moves:"] + ["- " + m for m in moved] + ["", "Notes:"] + ["- " + n for n in notes(R)]
    return "\n".join(md) + "\n", "\n".join(h) + "\n", "\n".join(tx) + "\n"
TONY_COLS = ["Meeting", "Calendar (Tony)", "Agenda / committee says", "RPM says (live read Oct 27)", "What the newsletter prints", "Please confirm"]
def tony_rows(R):
    """Rows for Tony (Steven, Oct 27 2026 3:16/3:17 PM): differences only, calendar vs agenda/report vs the live RPM read.
    Agenda day/time differences, meetings RPM lists that are not on the calendar, RPM day or time differences, and calendar
    meetings RPM lacks. Known typos are left out. Source wording only; the calendar always rules."""
    import issue_ctx; w = issue_ctx.windows(R["issue"])["MEETINGS"]
    idate = datetime.strptime(R["issue"], "%Y-%m-%d").strftime("%B %-d")
    def prints(r):
        if not r["cal_date"]: return f"Not printed (not on the calendar)"
        if w[0] <= r["cal_date"] <= w[1]: return f"{fd(r['cal_date'])}, {ft(r['cal_time'])} (calendar)"
        if r["cal_date"] < R["issue"]: return f"Not in the {idate} issue (meets before it)"
        return f"Not in the {idate} issue yet (later issue prints the calendar date)"
    out = []
    for r in R["rows"]:
        ag = [a for a in r["agenda"] if r["cal_date"] != a["date"] or ((a.get("typo") or {}).get("time", a["time"]) and r["cal_time"] and (a.get("typo") or {}).get("time", a["time"]) != r["cal_time"])]
        rp = [p for p in r["rpm"] if r["cal_date"] and (r["cal_date"] != p["date"] or (r["cal_time"], r.get("cal_end")) != (p.get("time"), p.get("end")))]
        no_rpm = bool(r["cal_date"]) and not r["rpm"]
        if not (ag or rp or no_rpm or not r["cal_date"]): continue
        cal = "Not on the calendar" if not r["cal_date"] else f"{fd(r['cal_date'])}, {ftr(r['cal_time'], r.get('cal_end'))}"
        mv = [e for e in R["moved"] if committee_of(e["name"], R["comm"]) == r["committee"] and (e.get("movedTo") or "").startswith(r["cal_date"] or "x")]
        if mv: cal += f" (moved from {fd(mv[0]['date'])})"
        agt = "; ".join(f"{fd(a['date'])}{', ' + ft(a['time']) if a['time'] else ''} ({a['kind'].split(' (')[0]}, {a['email_date'].split(' (')[0]})" for a in ag) or "No difference"
        rpt = "; ".join(f"{fd(p['date'])}, {ftr(p.get('time'), p.get('end'))}" for p in (r["rpm"] if (rp or not r["cal_date"]) else [])) or ("Not listed" if no_rpm else "Same as calendar")
        ask = []
        if ag: ask += [f"Which date is right: the calendar's {fd(r['cal_date'])[:-6]} or the agenda's {fd(a['date'])[:-6]}?" if a["date"] != r["cal_date"] else "Which time is right?" for a in ag]
        if not r["cal_date"]: ask.append("Is this meeting planned? If so, please add it to the calendar.")
        for p in rp:
            ask.append("RPM shows a different " + ("day and time" if p["date"] != r["cal_date"] and (r["cal_time"], r.get("cal_end")) != (p.get("time"), p.get("end")) else "day" if p["date"] != r["cal_date"] else "time") + ". Is the calendar correct?")
        if no_rpm: ask.append("For your information: RPM does not list this meeting.")
        if mv and rp: ask[-1] = f"RPM still shows the old date ({fd(mv[0]['date'])[:-6]}). Is the calendar date correct?"
        out.append(dict(meeting=(r["rpm"][0].get("rpm_name") or r["committee"]) if not r["cal_date"] and r["rpm"] else r["name"].replace(" (agenda only)", ""), calendar=cal, agenda=agt, rpm=rpt, prints=prints(r), confirm=" ".join(ask)))
    return out
def _intro(R):
    idate = datetime.strptime(R["issue"], "%Y-%m-%d").strftime("%B %-d")
    return (f"Below are the meeting dates and times where the committee information or the RPM calendar (read live {R['rpm_fetched'].split(', live')[0].replace('about ', 'at about ')}) "
            f"differs from the Palm Hill calendar; the {idate} newsletter prints the calendar date and time for each.")
def render_tony(R):
    """Plain-text version of the Tony email (Steven's voice)."""
    rows = tony_rows(R)
    tx = [f"Subject: {TONY_SUBJECT}", "", "Hi Tony,", "", _intro(R), ""]
    for x in rows:
        tx += [x["meeting"]] + [f"  {c}: {x[k]}" for c, k in zip(TONY_COLS[1:], ("calendar", "agenda", "rpm", "prints", "confirm"))] + [""]
    if not rows: tx += ["No differences this time. Everything matches the calendar.", ""]
    tx += ["Thank you for your help keeping the calendar current.", "", "Thanks,", "Steven"]
    return "\n".join(tx) + "\n"
def render_tony_html(R):
    """HTML version: one clean table, inline CSS only (email-safe), header row shaded, 14px, mobile friendly."""
    rows = tony_rows(R); e = html.escape
    th = "background:#2D5016;color:#ffffff;font-weight:bold;text-align:left;padding:8px 10px;border:1px solid #2D5016;font-size:14px;"
    td = "padding:8px 10px;border:1px solid #d0d7cc;vertical-align:top;font-size:14px;line-height:1.4;"
    h = [f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{e(TONY_SUBJECT)}</title></head>",
         "<body style='margin:0;padding:16px;background:#ffffff;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222;'>",
         "<p style='margin:0 0 12px;font-size:14px;'>Hi Tony,</p>", f"<p style='margin:0 0 16px;font-size:14px;line-height:1.5;'>{e(_intro(R))}</p>",
         "<div style='overflow-x:auto;-webkit-overflow-scrolling:touch;'>",
         "<table role='table' cellpadding='0' cellspacing='0' style='border-collapse:collapse;width:100%;min-width:640px;'>",
         "<tr>" + "".join(f"<th style='{th}'>{e(c)}</th>" for c in TONY_COLS) + "</tr>"]
    for i, x in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f4f7f1"
        h.append(f"<tr style='background:{bg};'>" + f"<td style='{td}font-weight:bold;'>{e(x['meeting'])}</td>" +
                 "".join(f"<td style='{td}'>{e(x[k])}</td>" for k in ("calendar", "agenda", "rpm", "prints", "confirm")) + "</tr>")
    if not rows: h.append(f"<tr><td colspan='6' style='{td}'>No differences this time. Everything matches the calendar.</td></tr>")
    h += ["</table></div>", "<p style='margin:16px 0 4px;font-size:14px;'>Thank you for your help keeping the calendar current.</p>",
          "<p style='margin:12px 0 0;font-size:14px;'>Thanks,<br>Steven</p>", "</body></html>"]
    return "\n".join(h) + "\n"
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--issue", required=True); ap.add_argument("--work"); ap.add_argument("--out")
    a = ap.parse_args(argv); os.environ["PHNEWS_ISSUE"] = a.issue
    import issue_ctx; C = issue_ctx.load(a.issue)
    work = Path(a.work or os.environ.get("PHNEWS_WORK") or C.DEFAULT_WORK); out = Path(a.out or work / "reports"); out.mkdir(parents=True, exist_ok=True)
    R = build(a.issue, work); stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    md, h, tx = render(R, stamp); base = out / f"meeting-conflicts-{a.issue}-{datetime.now().strftime('%Y%m%d-%H%M')}"
    for ext, s in ((".md", md), (".html", h), ("-email.txt", tx), ("-tony.txt", render_tony(R)), ("-tony.html", render_tony_html(R))): Path(str(base) + ext).write_text(s, encoding="utf-8")
    print(f"R86 report: {base}.md / .html / -email.txt / -tony.txt / -tony.html ({sum(1 for r in R['rows'] if r['diffs'])} of {len(R['rows'])} need attention)")
    return R, base
if __name__ == "__main__": main()
