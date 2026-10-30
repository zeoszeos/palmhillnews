"""PHNEWS issue context (coding batch 4, Steven Oct 24 2026 10:00 PM "let's do it correctly"; STYLE-RULES R71).
Loads the ONE content file for the issue being built (builder/issues/<YYYY-MM-DD>.py) and derives everything that follows
from the issue date: long date, section windows (R69), calendar window (R21b), file names. Shared by every core script."""
import os, importlib.util
from datetime import date, timedelta
from pathlib import Path
CORE = Path(__file__).resolve().parent
ISSUES_DIR = CORE.parent / "issues"
FULL = ("January","February","March","April","May","June","July","August","September","October","November","December")
REQUIRED = ("ISSUE", "VOL_NO", "SHORT", "DEFAULT_REPO", "DEFAULT_WORK", "STORY", "NOTICES_DROPPED", "R60C_ICE_NOTICE",
            "DRYRUN_OK", "STORY_OMIT_DRYRUN_NOTE", "LOCKED")
# Batch 5 (Steven Oct 24 2026 10:26 PM "Don't wait"): every per-issue item (events text, meetings overrides, notices, chair reports,
# reports, Did You Know, archive rows) lives in the content file. Content files may use these shared names (pre-set before they load):
PRESEED = {"BASE": "https://palmhillnews.vercel.app/pages/", "CAL": "https://www.palmhillcountryclub.net/calendar-1/",
           "ARCH": "https://palmhillnews.vercel.app/pages/archive/", "G": "#3A6B1A"}
DERIVED = ("ISSUE_LONG", "VOLNO", "WINDOWS", "REPO", "WORK")
def content_data(c):
    """Per-issue data names of content file c (everything but the required/derived fields and the pre-set shared names), deep-copied
    so the core can extend them without touching the loaded file. build_core.py injects these into its namespace (R71)."""
    import copy, types
    skip = set(REQUIRED) | set(PRESEED) | set(DERIVED)
    return {k: copy.deepcopy(v) for k, v in vars(c).items()
            if not k.startswith("__") and k not in skip and not isinstance(v, types.ModuleType)}
def windows(issue):
    d = date.fromisoformat(issue); f = lambda n: (d + timedelta(days=n)).isoformat()
    return {"THIS_WEEK": (f(0), f(6)), "UPCOMING": (f(7), f(28)), "NEXT_WEEK": (f(7), f(13)), "RECURRING": (f(0), f(29)), "MEETINGS": (f(0), f(30)),
            "CAL_WINDOW": (f(-7), f(60))}
def content_path(issue): return ISSUES_DIR / f"{issue}.py"
def check(c, issue):
    """R71 guard: a content file carries every required field, names its own date, and holds data only (no functions/imports)."""
    miss = [k for k in REQUIRED if not hasattr(c, k)]
    if miss: raise SystemExit(f"R71: builder/issues/{issue}.py lacks required field(s): {', '.join(miss)}")
    if c.ISSUE != issue: raise SystemExit(f"R71: builder/issues/{issue}.py says ISSUE = {c.ISSUE!r}")
    if c.STORY is not None and not {"json", "listen", "teaser_sentences"} <= set(c.STORY):
        raise SystemExit(f"R71: {issue} STORY needs json, listen, teaser_sentences (or STORY = None)")
    return c
def load(issue=None):
    issue = issue or os.environ.get("PHNEWS_ISSUE")
    if not issue: raise SystemExit("R69: no issue date (run builder/build_issue.py --issue <date>)")
    p = content_path(issue)
    if not p.exists(): raise SystemExit(f"R71: no content file builder/issues/{issue}.py")
    spec = importlib.util.spec_from_file_location(f"phnews_issue_{issue.replace('-', '_')}", p); m = importlib.util.module_from_spec(spec)
    m.__dict__.update(PRESEED); spec.loader.exec_module(m); check(m, issue)
    d = date.fromisoformat(issue)
    m.ISSUE_LONG = f"{FULL[d.month-1]} {d.day}, {d.year}"            # "October 25, 2026"
    m.VOLNO = f"Vol. 1, No. {m.VOL_NO}"
    m.WINDOWS = windows(issue)
    m.REPO = Path(os.environ.get("PHNEWS_REPO") or m.DEFAULT_REPO); m.WORK = Path(os.environ.get("PHNEWS_WORK") or m.DEFAULT_WORK)
    return m
def md_full(iso): d = date.fromisoformat(iso); return f"{FULL[d.month-1]} {d.day}"
