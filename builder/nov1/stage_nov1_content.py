"""Nov 1, 2026 content staging (stub, set up Oct 24 2026). Same pattern as builder/oct25/stage_oct25_content.py:
put each new item's source wording in builder/nov1/data/*.json (Did You Know, Community Story), verbatim-check it against
its source, and write unlisted preview pages under pages/previews/2026-11-01/. Nothing is staged yet; Oct 25's Spectrum,
Assessments and Joe Clay items are NOT carried. Does not touch the issue or the archives."""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "builder/nov1/data"; PV = ROOT / "pages/previews/2026-11-01"
items = sorted(D.glob("*.json"))
print("stage_nov1_content:", len(items), "data files;", "nothing to stage yet" if not items else [p.name for p in items])
