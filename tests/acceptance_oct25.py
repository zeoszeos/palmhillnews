#!/usr/bin/env python3
"""Acceptance test (coding batch 3, Steven voice OK Oct 24 2026; STYLE-RULES R69): rebuild the approved Oct 25 issue in a
throw-away temp copy and byte-compare it to the approved files. Never writes to /workspace/oct18-batch or the live work tree.
  repo tree  = git archive of tag format-locked-2026-10-25-final-r4, with this checkout's scripts/ + builder/ laid over it
  work tree  = copy (mtimes kept) of /workspace/phnews-consolidation/oct18
  build      = builder/build_issue.py --issue 2026-10-25 with PHNEWS_REPO / PHNEWS_WORK / PHNEWS_CAL_OFFLINE=1
Pass = new preview == approved preview AND (preview with the SEND title) == approved SEND, byte for byte."""
import hashlib, os, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
TAG = os.environ.get("PHNEWS_OCT25_TAG", "format-locked-2026-10-25-final-r4")  # r5 once the footer-alignment PR lands
WORK = Path(os.environ.get("PHNEWS_OCT25_WORK", "/workspace/phnews-consolidation/oct18"))
APPROVED_PREVIEW = WORK / "PHNEWS-2026-10-25-preview.html"
APPROVED_SEND = WORK / "PHNEWS-2026-10-25-SEND.html"
DRAFT_TITLE, SEND_TITLE = "<title>PHNEWS October 25, 2026 — DRAFT (not sent)</title>", "<title>PHNEWS October 25, 2026</title>"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]
def first_diff(a, b):
    n = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return f"first difference at byte {n}: approved {a[max(0,n-60):n+60]!r} vs rebuilt {b[max(0,n-60):n+60]!r}"
def main():
    want_p, want_s = APPROVED_PREVIEW.read_bytes(), APPROVED_SEND.read_bytes()
    import re; stamp = re.search(r"(\d{1,2}:\d\d [AP]M)</span", want_p.decode("utf-8")).group(1)  # the approved build-time stamp (masthead), reused so the re-render is comparable
    print("approved build stamp:", stamp)
    with tempfile.TemporaryDirectory(prefix="phnews-acc-oct25-") as t:
        t = Path(t); repo, work = t / "repo", t / "work"; repo.mkdir()
        tar = subprocess.run(["git", "archive", TAG], cwd=HERE, capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(repo)], input=tar, check=True)
        shutil.rmtree(repo / "builder")   # batch 4 (R71): the tag's old per-issue builders are replaced by this checkout's core + issues/
        for d in ("scripts", "builder"):
            shutil.copytree(HERE / d, repo / d, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(WORK, work, symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))  # copytree keeps mtimes (copy2)
        # Use the calendar snapshot the approved build used (recorded at the tag in builder/calendar-pull/2026-10-25.json): later
        # snapshots are hidden in the TEMP copy only (same calendar content, but the footer "Calendar check" time comes from the file).
        import json; rec = json.loads((repo / "builder/calendar-pull/2026-10-25.json").read_text()); used = rec["calendar_file"]
        later = [p for p in (work / "data").glob("cal-*.json") if p.name > used]
        for p in later: p.unlink()   # temp copy only
        print(f"calendar snapshot: {used} (approved footer {rec['footer']!r}); hidden in temp copy: {[p.name for p in later]}")
        env = dict(os.environ, PHNEWS_REPO=str(repo), PHNEWS_WORK=str(work), PHNEWS_CAL_OFFLINE="1", PHNEWS_BUILD_STAMP=stamp)
        r = subprocess.run([sys.executable, str(repo / "builder/build_issue.py"), "--issue", "2026-10-25"], env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-3000:]); print("ACCEPTANCE FAIL: Oct 25 rebuild did not finish"); return 1
        got = (work / "PHNEWS-2026-10-25-preview.html").read_bytes()
        got_send = got.decode("utf-8").replace(DRAFT_TITLE, SEND_TITLE, 1).encode("utf-8")
        ok = True
        for name, a, b in (("preview", want_p, got), ("SEND", want_s, got_send)):
            if a == b: print(f"PASS {name}: byte-for-byte equal ({len(a)} bytes, sha256 {hashlib.sha256(a).hexdigest()[:16]})")
            else: ok = False; print(f"FAIL {name}: {len(a)} vs {len(b)} bytes; " + first_diff(a.decode('utf-8','replace'), b.decode('utf-8','replace')))
        print("ACCEPTANCE", "PASS" if ok else "FAIL"); return 0 if ok else 1
if __name__ == "__main__": sys.exit(main())
