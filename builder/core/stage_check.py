#!/usr/bin/env python3
"""R73 (coding batch 6, Steven Oct 24 2026 10:40 PM "do them all"): check-driven, repeatable pull-in check for one issue.
    python3 builder/core/stage_check.py --issue 2026-11-01 [--max-age-hours 48] [--strict]
Reads ONLY: the issue content file, the repo (PHNEWS_REPO or DEFAULT_REPO) and the work tree (PHNEWS_WORK or DEFAULT_WORK).
Lists every expected source -- calendar pull (stamp + record), notice / chair report / copy pages, notice images, story and
Did You Know data files, the weekly update PDF -- as FOUND / MISSING / STALE. Writes nothing, invents nothing.
Exit 1 if anything is MISSING (or STALE with --strict); exit 0 otherwise. Safe to run any number of times."""
import argparse, datetime as dt, os, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); import issue_ctx as _ix

def items(c, repo, work):
    """(group, label, path, why) for every source the content file says this issue needs."""
    P = repo / "pages"
    for p in getattr(c, "NOTICE_PAGES", []): yield "notice page", p["page"], P / p["page"], "Community Notices More → page"
    for p in getattr(c, "NOTICE_PAGES", []):
        for kind, v in p["blocks"]:
            if kind == "img": yield "notice image", v[0], repo / v[0].lstrip("/"), "flyer shown on the notice page"
    for w in getattr(c, "WM_COPIES", []): yield "webmaster copy", w[0], P / w[0], "L27/L29 Webmaster source copy page"
    for r in getattr(c, "CHAIR_REPORTS", []): yield "chair report", r["page"], P / r["page"], "Committee Chair Reports card"
    if c.STORY: yield "story data", c.STORY["json"], repo / c.STORY["json"], "Community Story source wording"
    for n in ("DYK_ITEMS_JSON", "DYK_RULES_ITEM_JSON", "DYK_RULES_SOURCE_FILE"):
        v = getattr(c, n, None)
        if isinstance(v, str): yield "did you know data", v, ((work if n == "DYK_RULES_SOURCE_FILE" else repo) / v), f"{n} (Did You Know source)"
    v = getattr(c, "WMU_1023_PDF_SRC", None)
    if v: yield "weekly update PDF", v, (work / v), "R65 Attachments card (R72: relative to the work tree)"
    yield "calendar record", f"builder/calendar-pull/{c.ISSUE}.json", repo / f"builder/calendar-pull/{c.ISSUE}.json", "R21b calendar pull record"

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--issue", required=True); ap.add_argument("--max-age-hours", type=float, default=48); ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    c = _ix.load(a.issue)
    repo = Path(os.environ.get("PHNEWS_REPO") or c.DEFAULT_REPO); work = Path(os.environ.get("PHNEWS_WORK") or c.DEFAULT_WORK)
    rows = []
    seen = set()
    for g, label, path, why in items(c, repo, work):
        if (g, label) in seen: continue
        seen.add((g, label)); rows.append((("FOUND" if path.exists() else "MISSING"), g, label, why))
    # calendar pull stamp: newest data/cal-YYYYMMDD-HHMM.json in the work tree, must be recent and before the issue
    cals = sorted((work / "data").glob("cal-*.json"))
    if not cals: rows.append(("MISSING", "calendar pull", "data/cal-*.json", "R21b: run the calendar pull"))
    else:
        m = re.match(r"cal-(\d{8})-(\d{4})\.json", cals[-1].name)
        st = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M") if m else None
        age = (dt.datetime.now() - st).total_seconds() / 3600 if st else 1e9
        ok = st and age <= a.max_age_hours and st.date() <= dt.date.fromisoformat(c.ISSUE)
        rows.append(("FOUND" if ok else "STALE", "calendar pull", f"{cals[-1].name} ({age:.0f} h old)",
                     f"R21b: newest pull must be under {a.max_age_hours:.0f} h old -- re-pull if STALE"))
    print(f"stage_check {c.ISSUE} | repo {repo} | work {work}")
    for s, g, label, why in rows: print(f"  {s:7} {g:18} {label}  -- {why}")
    n = {k: sum(r[0] == k for r in rows) for k in ("FOUND", "MISSING", "STALE")}
    print(f"stage_check {c.ISSUE}: {n['FOUND']} found, {n['MISSING']} missing, {n['STALE']} stale")
    if n["MISSING"]: print("R73 FAIL: sources missing. Why: the build would link or quote something we do not have. "
                           "Fix: get the source (copy, never move) or drop the item from the content file -- never invent it.")
    return 1 if n["MISSING"] or (a.strict and n["STALE"]) else 0
if __name__ == "__main__": sys.exit(main())
