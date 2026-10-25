"""Nov 1, 2026 content staging (R73, coding batch 6). Check-driven and repeatable: runs builder/core/stage_check.py for
2026-11-01, which lists every expected source (calendar pull stamp, notices, Megan's PDF, chair reports, story / Did You
Know data) as FOUND / MISSING / STALE. It writes nothing and never invents content; new item wording still goes into
builder/nov1/data/*.json verbatim from its source. Usage: python3 builder/nov1/stage_nov1_content.py"""
import pathlib, runpy, sys
CORE = pathlib.Path(__file__).resolve().parents[1] / "core"
sys.argv = [str(CORE / "stage_check.py"), "--issue", "2026-11-01"] + sys.argv[1:]
runpy.run_path(str(CORE / "stage_check.py"), run_name="__main__")
