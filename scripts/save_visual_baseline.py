#!/usr/bin/env python3
"""R74 (coding batch 6, Steven Oct 24 2026 10:40 PM "do them all"): save the APPROVED visual baseline for one issue.
Run ONLY after Steven approves the look of that exact file:
    /workspace/.venv-vr/bin/python scripts/save_visual_baseline.py --issue 2026-11-01 --kind preview PAGE.html --approved "Steven, Oct 31 6:10 PM"
Writes tests/golden/issue-<date>/<kind>/ (section screenshots desktop 1280 + mobile 390, manifest.json) and APPROVED.json
(who/when, page sha256). Refuses to overwrite an existing baseline unless --replace. Later runs of
scripts/visual_regression.py PAGE --issue <date> --kind <kind> compare against it."""
import argparse, datetime, hashlib, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument("page"); ap.add_argument("--issue", required=True)
ap.add_argument("--kind", default="preview", choices=("preview", "send")); ap.add_argument("--approved", required=True)
ap.add_argument("--replace", action="store_true"); a = ap.parse_args()
gold = ROOT / "tests/golden" / f"issue-{a.issue}" / a.kind
if (gold / "manifest.json").exists() and not a.replace:
    sys.exit(f"R74: baseline already saved at {gold} (see APPROVED.json). Use --replace only for a newly approved look.")
r = subprocess.run([sys.executable, str(ROOT / "scripts/visual_regression.py"), a.page, "--golden", str(gold), "--capture"])
if not (gold / "manifest.json").exists(): sys.exit("R74 FAIL: capture did not write manifest.json")
page = pathlib.Path(a.page).read_bytes()
(gold / "APPROVED.json").write_text(json.dumps({"issue": a.issue, "kind": a.kind, "approved": a.approved, "page": str(a.page),
    "page_sha256": hashlib.sha256(page).hexdigest(), "saved": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "rule_check_exit": r.returncode}, indent=1))
print(f"R74: baseline saved -> {gold} ({len(json.loads((gold / 'manifest.json').read_text()))} sections)")
