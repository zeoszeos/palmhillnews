"""STYLE-RULES R86 (Steven, Oct 27 2026 1:25 PM, voice; agreed with Tony Ciaramitaro by email Oct 26-27): Tony's Palm Hill club
calendar (booking-system feed) is the single source of truth for meeting dates and times. This report compares every committee
and Board meeting on the calendar with (2) the committees' own agenda emails / report "next meeting" notes and (3) the recorded
RPM calendar values, and flags any difference. Corrective action: the committee must have Tony change the calendar to the
new date right away. Read-only: never writes the calendar, never sends mail.

Run:  python3 scripts/meeting_conflict_report.py --issue 2026-11-01 [--out DIR] [--work DIR]
Writes DIR/meeting-conflicts-<issue>-<stamp>.md, .html, -email.txt and -tony.txt (default DIR = <work>/reports).
-tony.txt (Steven, Oct 27 2026 2:26/2:27 PM): plain-text note for Tony in Steven's voice, real conflicts only; its first line is
always "Subject: " + TONY_SUBJECT (exact, no date, no issue number). Draft text only -- this script never sends anything."""
import argparse, glob, html, json, os, re, sys
from datetime import date, datetime
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "builder/core"))
COLS = ["Committee/Meeting", "Calendar date", "Calendar time", "Agenda / committee-report suggested date (time, source)",
        "RPM calendar date (time)", "Agenda notice email date", "Calendar recurring", "What differs"]
TONY_SUBJECT = "Calendar Conflicts Report"   # R86 (Steven, Oct 27 2026 2:27 PM): every conflict email to Tony uses exactly this subject
# RPM (Steven Oct 27 2026 2:43 PM): reference only, to spot dates missing from the calendar; never overrides, never counted on calendar dates.
ACTION = "Corrective action: the committee must have Tony change the calendar to the new date right away (the calendar always rules)."
def fd(d): return datetime.strptime(d, "%Y-%m-%d").strftime("%a %b %-d, %Y") if d else "—"
def ft(t):
    if not t: return "—"
    h, m = map(int, t.split(":")); return f"{(h % 12) or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"
def load_cal(work):
    fs = sorted(glob.glob(str(Path(work) / "data/cal-*.json")))
    if not fs: raise SystemExit("R86: no calendar snapshot data/cal-*.json in " + str(work))
    return fs[-1], json.load(open(fs[-1], encoding="utf-8"))
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
        rows.append(dict(committee=k, name=e["name"], cal_date=e["date"], cal_time=e["start"], recurring=e.get("recurring"),
                         agenda=[a for _, a in ag], rpm=[r for _, r in rp], override=ovr.get(k), note=notes.get((k, e["date"]))))
    for i, r in enumerate(src["rpm"]):   # RPM entries with no calendar meeting that month
        if i not in used_r and r["date"] >= since:
            rows.append(dict(committee=r["committee"], name=r["committee"] + " (RPM only)", cal_date=None, cal_time=None, recurring=None, agenda=[], rpm=[r], override=None, note=None))
    for i, a in enumerate(src["agenda"]):
        if i not in used_a and a["date"] >= since:
            rows.append(dict(committee=a["committee"], name=a["committee"] + " (agenda only)", cal_date=None, cal_time=None, recurring=None, agenda=[a], rpm=[], override=ovr.get(a["committee"]), note=None))
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
            if r["cal_date"] and r["cal_date"] != p["date"]: refs.append(("RPM note (reference only)", f"The calendar date is {fd(r['cal_date'])}, the calendar time is {ft(r['cal_time'])}, RPM says {fd(p['date'])}. RPM is reference only (it never overrides the calendar)."))
        if not r["cal_date"]: diffs.insert(0, ("Not on the Palm Hill calendar", "No meeting for this committee on the Palm Hill calendar that month; " + ("RPM lists " + ", ".join(fd(p["date"]) for p in r["rpm"]) if r["rpm"] else "only the agenda/report lists it") + ". If the meeting is real, the committee must ask Tony to add it to the calendar."))
        if r.get("note") and r["cal_date"]: diffs.append(("Builder note", f"The calendar has this meeting CONFIRMED, but the content file still adds a note: {r['note']}. Under R86 the calendar rules."))
        if r["override"]: diffs.insert(0, ("CONFLICT-OVERRIDDEN-BY-RULE", f"Nov 1 rows still use the locked R62/R62b override (" + ", ".join(f"{k} {fd(v) if k == 'date' else ft(v)}" for k, v in r['override'].items()) + ") until Steven releases R62/R62b/R62c."))
        r["diffs"], r["refs"] = diffs, refs
    return dict(issue=issue, calf=calf, cal=cal, rows=rows, moved=moved, overrides=ovr)
def cells(r):
    ag = "; ".join(f"{fd(a['date'])}{', ' + ft(a['time']) if a['time'] else ''} ({a['kind']}, {a['page'].split('/')[-1]})" for a in r["agenda"]) or "—"
    rp = "; ".join(f"{fd(p['date'])} (time not recorded)" for p in r["rpm"]) or "—"
    em = "; ".join(a["email_date"] for a in r["agenda"]) or "—"
    rec = "—" if r["recurring"] is None else ("☑" if r["recurring"] else "☐")
    st = ("; ".join(k for k, _ in r["diffs"]) or "match") + "".join(f" [{k}]" for k, _ in r["refs"])
    return [r["name"], fd(r["cal_date"]), ft(r["cal_time"]), ag, rp, em, rec, st]
NOTES = ["The Palm Hill calendar (Tony Ciaramitaro's booking-system feed) is the single source of truth (R86).",
         "RPM values are the recorded RPM calendar values (Oct 16 2026 notes), not a fresh read: the RPM portal can't be read automatically. RPM gives no time.",
         "RPM is reference only: it helps spot meetings missing from the Palm Hill calendar and never overrides it. RPM day differences on calendar meetings are 'RPM note (reference only)' and are not counted; RPM-only meetings stay as items.",
         "Calendar recurring: ☑ = the calendar marks the entry as part of a recurring series, ☐ = not recurring (the feed's own 'recurring' marker).",
         "RPM recurring column left out: the RPM data has no recurring marker.",
         ACTION]
def render(R, stamp):
    R["rows"].sort(key=lambda r: (r["cal_date"] or min(x["date"] for x in r["rpm"] + r["agenda"]), r["cal_time"] or "")); rows = [cells(r) for r in R["rows"]]; conf = [r for r in R["rows"] if r["diffs"]]
    head = f"PHNEWS meeting conflict report, issue {R['issue']} (run {stamp} ET)\nCalendar snapshot: {os.path.basename(R['calf'])} (pulled {R['cal'].get('start')}..{R['cal'].get('end')} window)"
    moved = [f"{e['name']} {fd(e['date'])}: calendar marks RESCHEDULED, moved to {e.get('movedTo')}" for e in R["moved"]]
    md = [f"# {head.splitlines()[0]}", "", head.splitlines()[1], "", f"**{len(conf)} of {len(rows)} meetings need attention.**", "",
          "| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)] + ["| " + " | ".join(c.replace("|", "/") for c in x) + " |" for x in rows]
    md += ["", "## Conflicts in plain words", ""] + [f"- **{r['name']}**: " + " ".join(t for _, t in r["diffs"]) for r in conf]
    md += ["", "## Reference notes (not counted)", ""] + [f"- **{r['name']}**: " + " ".join(t for _, t in r["refs"]) for r in R["rows"] if r["refs"]]
    md += ["", "## Calendar moves", ""] + [f"- {m}" for m in moved] + ["", "## Notes", ""] + [f"- {n}" for n in NOTES]
    h = ["<!doctype html><meta charset='utf-8'><title>PHNEWS meeting conflicts " + R["issue"] + "</title>",
         "<style>body{font-family:Arial,sans-serif;max-width:1200px;margin:20px auto;color:#333}table{border-collapse:collapse;font-size:13px}"
         "th,td{border:1px solid #ccc;padding:5px;vertical-align:top;text-align:left}th{background:#2D5016;color:#fff}tr.c td{background:#FFF7E0}</style>",
         f"<h1>{html.escape(head.splitlines()[0])}</h1><p>{html.escape(head.splitlines()[1])}</p><p><b>{len(conf)} of {len(rows)} meetings need attention.</b></p>",
         "<table><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in COLS) + "</tr>"]
    h += [f"<tr{' class=c' if r['diffs'] else ''}>" + "".join(f"<td>{html.escape(c)}</td>" for c in x) + "</tr>" for r, x in zip(R["rows"], rows)]
    h += ["</table><h2>Conflicts in plain words</h2><ul>"] + [f"<li><b>{html.escape(r['name'])}</b>: {html.escape(' '.join(t for _, t in r['diffs']))}</li>" for r in conf]
    h += ["</ul><h2>Reference notes (not counted)</h2><ul>"] + [f"<li><b>{html.escape(r['name'])}</b>: {html.escape(' '.join(t for _, t in r['refs']))}</li>" for r in R["rows"] if r["refs"]]
    h += ["</ul><h2>Calendar moves</h2><ul>"] + [f"<li>{html.escape(m)}</li>" for m in moved] + ["</ul><h2>Notes</h2><ul>"] + [f"<li>{html.escape(n)}</li>" for n in NOTES] + ["</ul>"]
    tx = [head, "", f"{len(conf)} of {len(rows)} meetings need attention.", ""]
    for r, x in zip(R["rows"], rows):
        tx += [f"{COLS[i]}: {v}" for i, v in enumerate(x)]
        tx += ["   " + t for _, t in r["diffs"]] + ["   (reference only) " + t for _, t in r["refs"]] + [""]
    tx += ["Calendar moves:"] + ["- " + m for m in moved] + ["", "Notes:"] + ["- " + n for n in NOTES]
    return "\n".join(md) + "\n", "\n".join(h) + "\n", "\n".join(tx) + "\n"
def render_tony(R):
    """Plain text for Tony (Steven's voice): only real differences; RPM-only meetings as 'not on the calendar, please confirm'."""
    import issue_ctx; w = issue_ctx.windows(R["issue"])["MEETINGS"]
    C = issue_ctx.load(R["issue"]); idate = datetime.strptime(R["issue"], "%Y-%m-%d").strftime("%B %-d")
    def prints(r):
        if not r["cal_date"]: return f"Not printed in the {idate} issue (it is not on the calendar)."
        if w[0] <= r["cal_date"] <= w[1]: return f"{fd(r['cal_date'])}, {ft(r['cal_time'])} (the calendar date and time)."
        return f"Not in the {idate} issue (outside its meeting window); a later issue will print the calendar date."
    blocks, fyi = [], []
    for r in R["rows"]:
        ag = [a for a in r["agenda"] if r["cal_date"] != a["date"] or ((a.get("typo") or {}).get("time", a["time"]) and r["cal_time"] and (a.get("typo") or {}).get("time", a["time"]) != r["cal_time"])]
        rp = [p for p in r["rpm"] if r["cal_date"] != p["date"]]
        if r["cal_date"] and not ag:   # RPM-only difference on a calendar meeting: short FYI line, not a conflict
            fyi += [f"- {r['name']}: calendar {fd(r['cal_date'])}; RPM shows {fd(p['date'])}." for p in rp]; continue
        if not (ag or rp): continue
        b = [r["name"] + (" -- not on the calendar, please confirm" if not r["cal_date"] else ""),
             f"  Calendar date: {fd(r['cal_date']) if r['cal_date'] else 'not on the calendar'}",
             f"  Calendar time: {ft(r['cal_time']) if r['cal_date'] else '--'}"]
        for a in ag:
            v = fd(a["date"]) + (", " + ft(a["time"]) if a["time"] else "")
            b.append(f"  Agenda/report says: {v} -- from the {a['kind']}, {a['email_date']}")
        for p in rp: b.append(f"  RPM calendar says: {fd(p['date'])} (no time given)")
        b.append(f"  The newsletter prints: {prints(r)}")
        blocks.append("\n".join(b))
    tx = [f"Subject: {TONY_SUBJECT}", "", "Hi Tony,", "",
          "Here are the dates the newsletter found that differ from the calendar. The "
          f"{idate} issue prints the calendar date for each one. When you have a minute, please check whether the calendar or "
          "the committee's information needs to be corrected.", ""]
    tx += ["\n\n".join(blocks) if blocks else "No differences this time -- everything matches the calendar.", ""]
    if fyi: tx += ["FYI only (no action needed, the calendar rules): RPM shows a different day for these:"] + fyi + [""]
    tx += [
           "One caveat: the RPM dates come from my Oct 16 notes, not a live read of RPM, so some may already be fixed.", "",
           "Thanks,", "Steven"]
    return "\n".join(tx) + "\n"
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--issue", required=True); ap.add_argument("--work"); ap.add_argument("--out")
    a = ap.parse_args(argv); os.environ["PHNEWS_ISSUE"] = a.issue
    import issue_ctx; C = issue_ctx.load(a.issue)
    work = Path(a.work or os.environ.get("PHNEWS_WORK") or C.DEFAULT_WORK); out = Path(a.out or work / "reports"); out.mkdir(parents=True, exist_ok=True)
    R = build(a.issue, work); stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    md, h, tx = render(R, stamp); base = out / f"meeting-conflicts-{a.issue}-{datetime.now().strftime('%Y%m%d-%H%M')}"
    for ext, s in ((".md", md), (".html", h), ("-email.txt", tx), ("-tony.txt", render_tony(R))): Path(str(base) + ext).write_text(s, encoding="utf-8")
    print(f"R86 report: {base}.md / .html / -email.txt / -tony.txt ({sum(1 for r in R['rows'] if r['diffs'])} of {len(R['rows'])} need attention)")
    return R, base
if __name__ == "__main__": main()
