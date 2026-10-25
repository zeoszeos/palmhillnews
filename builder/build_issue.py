#!/usr/bin/env python3
"""PHNEWS single builder entry point (coding batch 3, Steven voice OK Oct 24 2026; STYLE-RULES R69).
    python3 builder/build_issue.py --issue 2026-11-01          (add PHNEWS_DRYRUN=1 for a workspace dry run)
The issue date picks the issue's content/build file from ISSUES below; nothing else chooses it. This file owns the shared
settings every issue uses (R67 PHNEWS_REPO / PHNEWS_WORK defaults per issue, R21b calendar window, the section windows) and
checks the content file agrees with them before anything runs. Draft builds only: never sends, publishes or pushes."""
import argparse, os, re, runpy, sys
from datetime import date, timedelta
from pathlib import Path
HERE = Path(__file__).resolve().parent
# issue date -> (content/build file under builder/, default PHNEWS_REPO, default PHNEWS_WORK)
ISSUES = {
    "2026-10-25": ("oct25/build_oct25.py", "/workspace/oct18-batch", "/workspace/phnews-consolidation/oct18"),
    "2026-11-01": ("nov1/build_nov1.py",   "/workspace/nov1-build",  "/workspace/phnews-consolidation/nov1"),
}
# Oct 18 is not listed: its builder (builder/oct18/build_oct18.py) predates the shared settings and the issue is locked as sent (R10).
def windows(issue):
    d = date.fromisoformat(issue); f = lambda n: (d + timedelta(days=n)).isoformat()
    return {"ISSUE": issue, "THIS_WEEK": (f(0), f(6)), "UPCOMING": (f(7), f(28)), "RECURRING": (f(0), f(29)), "MEETINGS": (f(0), f(30)),
            "CAL_WINDOW": (f(-7), f(60))}
def check_content(path, issue):
    """R69 guard: the content file's ISSUE and section windows must equal the ones derived from --issue."""
    t = path.read_text(encoding="utf-8"); bad = []
    for k, v in windows(issue).items():
        if k == "CAL_WINDOW":
            if "CAL_WINDOW = ((_d0.fromisoformat(ISSUE) - _td0(days=7))" not in t: bad.append("CAL_WINDOW not derived from ISSUE (R21b)")
            continue
        m = re.search(rf"^{k} = (.+?)\s*(#.*)?$", t, re.M)
        if not m or eval(m.group(1), {}) != v: bad.append(f"{k} = {m.group(1) if m else 'missing'} (expected {v!r})")
    if "PHNEWS_ENTRY" not in t: bad.append("content file lacks the R69 entry-point check")
    if bad: raise SystemExit(f"R69: {path.name} disagrees with build_issue for {issue}: " + "; ".join(bad))
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0]); ap.add_argument("--issue", required=True, choices=sorted(ISSUES))
    a = ap.parse_args(argv)
    rel, repo, work = ISSUES[a.issue]; path = HERE / rel
    check_content(path, a.issue)
    os.environ.setdefault("PHNEWS_REPO", repo); os.environ.setdefault("PHNEWS_WORK", work)
    os.environ["PHNEWS_ENTRY"] = "build_issue"; os.environ["PHNEWS_ISSUE"] = a.issue
    print(f"build_issue: {a.issue} -> {rel} | REPO {os.environ['PHNEWS_REPO']} | WORK {os.environ['PHNEWS_WORK']}"
          + (" | DRY RUN" if os.environ.get("PHNEWS_DRYRUN") == "1" else ""))
    sys.path.insert(0, str(path.parent)); sys.argv = [str(path)]
    runpy.run_path(str(path), run_name="__main__")
if __name__ == "__main__": main()
