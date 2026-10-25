#!/usr/bin/env python3
"""PHNEWS single builder entry point (R69, coding batch 3) over ONE shared builder (R71, coding batch 4, Steven Oct 24 2026 10:00 PM).
    python3 builder/build_issue.py --issue 2026-11-01          (add PHNEWS_DRYRUN=1 for a workspace dry run)
    python3 builder/build_issue.py --check                     (R71 guard only: content files + no per-issue builders)
The issue date picks the issue's content file builder/issues/<date>.py (data only). All logic and every R-rule guard live in
builder/core/ (build_core.py, locked_checks.py, run_checks.py, recurring.py, recurring_grouped.py, issue_ctx.py). Section and
calendar windows are derived from the date (issue_ctx.windows). Draft builds only: never sends, publishes or pushes."""
import argparse, ast, os, runpy, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
CORE = HERE / "core"; ISSUES = HERE / "issues"
sys.path.insert(0, str(CORE)); import issue_ctx as _ix
# Oct 18 (builder/oct18/) is locked as sent (R10) and predates the shared builder; it is exempt and never built here.
EXEMPT_DIRS = {"core", "issues", "calendar-pull", "oct18", "tools", "__pycache__"}
LOGIC_PREFIXES = ("build_", "locked_checks", "run_checks", "recurring", "make_live_preview", "publish_")
def r71_violations():
    """R71 guard: (a) every content file is data only (assignments + docstring, no def/class/import/loops) and has the required
    fields; (b) no per-issue builder folder holds builder logic -- only data/, stage_<short>_content.py and README.md."""
    bad = []
    for p in sorted(ISSUES.glob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for n in tree.body:
            if not (isinstance(n, (ast.Assign, ast.AnnAssign)) or (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))):
                bad.append(f"{p.relative_to(HERE)} line {n.lineno}: content files are data only ({type(n).__name__})")
        try: _ix.load(p.stem)
        except SystemExit as e: bad.append(str(e))
    for d in sorted(x for x in HERE.iterdir() if x.is_dir() and x.name not in EXEMPT_DIRS):
        for f in sorted(d.iterdir()):
            if f.name in ("data", "README.md", "__pycache__") or (f.name.startswith("stage_") and f.suffix == ".py"): continue
            if f.suffix == ".py" and f.name.startswith(LOGIC_PREFIXES): bad.append(f"{f.relative_to(HERE)}: per-issue builder logic (R71: use builder/core + builder/issues/<date>.py)")
            elif f.suffix == ".py": bad.append(f"{f.relative_to(HERE)}: code in a per-issue folder (R71)")
    return bad
# R71b (batch 5, Steven Oct 24 2026 10:26 PM "Don't wait"): builder/core/ holds logic only. Any string literal (>= 16 chars) that
# a content file uses must NOT also be a string literal in core code -- that means issue content leaked back into the core.
# Standing club vocabulary (committee names, venues, section headings, archive folders) is shared on purpose and allowed here.
R71B_MINLEN = 16
R71B_CLUB_VOCAB = {
    "Planning and Environmental Committee", "Planning and Environmental Committee Meeting", "Buildings and Grounds Committee Meeting",
    "Communications Committee", "Finance Committee", "Finance Committee Meeting", "Rules and Regulations Committee Report",
    "South Clubhouse Boardroom", "Board Room South", "Palm Hill Country Club", "Weekly Manager Update",
    "weekly-manager-updates", "committee-reports", "NOTICES_EXPECTED", "CHAIR_EXPECTED"}
# Oct 18-era L24/L27 lists kept in locked_checks.py for the locked-as-sent Oct 18 issue (R10); not used by the shared checks.
R71B_LEGACY_NAMES = {"COMMUNITY_SOURCES", "WEBMASTER_SOURCE_LINKS"}
def _strs(tree, skip=()):
    out = set()
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id in skip for x in n.targets): continue
        for k in ast.walk(n):
            if isinstance(k, ast.Constant) and isinstance(k.value, str): out.add(k.value)
    return out
def r71b_violations():
    content = set()
    for p in sorted(ISSUES.glob("*.py")):
        content |= {x for x in _strs(ast.parse(p.read_text(encoding="utf-8"))) if len(x) >= R71B_MINLEN and not x.startswith("/")}
    content -= R71B_CLUB_VOCAB
    bad = []
    for c in sorted(CORE.glob("*.py")):
        for x in sorted(content & _strs(ast.parse(c.read_text(encoding="utf-8")), R71B_LEGACY_NAMES)):
            bad.append(f"core/{c.name}: issue content {x[:70]!r} is hard-coded in the core (R71b: move it to builder/issues/<date>.py)")
    return bad
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--issue", choices=sorted(p.stem for p in ISSUES.glob("20*.py"))); g.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    bad = r71_violations() + r71b_violations()
    if bad: raise SystemExit("R71 guard FAIL:\n  " + "\n  ".join(bad))
    if a.check: print("R71/R71b guard OK:", ", ".join(sorted(p.stem for p in ISSUES.glob("20*.py")))); return
    c = _ix.load(a.issue)
    os.environ.setdefault("PHNEWS_REPO", c.DEFAULT_REPO); os.environ.setdefault("PHNEWS_WORK", c.DEFAULT_WORK)
    os.environ["PHNEWS_ENTRY"] = "build_issue"; os.environ["PHNEWS_ISSUE"] = a.issue
    print(f"build_issue: {a.issue} -> core/build_core.py + issues/{a.issue}.py | REPO {os.environ['PHNEWS_REPO']} | WORK {os.environ['PHNEWS_WORK']}"
          + (" | DRY RUN" if os.environ.get("PHNEWS_DRYRUN") == "1" else ""))
    sys.argv = [str(CORE / "build_core.py")]
    runpy.run_path(str(CORE / "build_core.py"), run_name="__main__")
if __name__ == "__main__": main()
