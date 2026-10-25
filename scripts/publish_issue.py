"""Publish / live-preview any PHNEWS issue (A8, Steven-approved Oct 24 2026 2:26 PM; STYLE-RULES R64).
Generic version of builder/oct18/publish_oct18.py (+ make_live_preview's preview copy); the Oct 18 scripts stay as sent.

  python3 scripts/publish_issue.py --issue 2026-10-25 [--root /workspace/phnews-consolidation/oct18] [--dry-run]

Reads ROOT/PHNEWS-<issue>-preview.html (the builder output), removes the review stamp / DRAFT title / preview-only bits,
maps any pages/previews/<issue>/ page linked from the issue to its permanent pages/<issue>-... home, runs the same
STYLE-RULES asserts as publish_oct18 (R18 R22 R39-R49b), and writes the SEND file ROOT/PHNEWS-<issue>-SEND.html plus
ROOT/nas-layout/<yyyy-mm>/<issue>/sent-final/PHNEWS-<issue>-FINAL.html. Emails nothing.
--dry-run: writes ONLY the SEND/NAS-layout files; no repo page is written or touched (the R47 Listen add is checked, not done).
"""
import argparse, os, re, sys, time
from pathlib import Path
_T0 = time.time() - 1
HERE = Path(__file__).resolve().parent; REPO = HERE.parent
sys.path.insert(0, str(HERE))
import style_rules as _sr, summary_trim as _st, source_sections as _ss, notice_listen as _nl, readability as _rd, check_listen_coverage as _lc
ap = argparse.ArgumentParser(); ap.add_argument("--issue", required=True); ap.add_argument("--root", default=os.environ.get("PHNEWS_WORK") or "/workspace/phnews-consolidation/oct18")  # R67: env PHNEWS_WORK
ap.add_argument("--repo", default=str(REPO)); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
I = a.issue; ROOT = Path(a.root); REPO = Path(a.repo); assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", I), I
from datetime import date
_d = date.fromisoformat(I); LONG = f"{_d:%B} {_d.day}, {_d.year}"; SHORT = f"{_d:%b} {_d.day}"
L = "https://palmhillnews.vercel.app/pages/"; PV = REPO / f"pages/previews/{I}"
SRC = ROOT / f"PHNEWS-{I}-preview.html"; NAME = f"PHNEWS-{I}-FINAL.html"
s = SRC.read_text(encoding="utf-8")
# preview pages linked from the issue -> permanent homes (same rule as publish_oct18's MAP)
MAP = {}
for rel in sorted(set(re.findall(re.escape(L + f"previews/{I}/") + r'([^"?#]+\.html)', s))):
    if rel == f"PHNEWS-{I}-preview.html": continue
    MAP[rel] = f"{I}-notice-{rel.split('/', 1)[1]}" if rel.startswith("notices/") else (rel if rel.startswith(I) else f"{I}-{rel}")
def clean(t):
    t = t.replace('<meta name="robots" content="noindex,nofollow">\n', "").replace('<meta name="robots" content="noindex,nofollow">', "")
    t = t.replace(f" ({SHORT} preview)", "").replace(f" ({_d:%B} {_d.day} preview)", "")
    t = re.sub(r"<!-- ph-archive-nav:none \(PREVIEW-ONLY[^>]*-->", f"<!-- ph-archive-nav:none ({SHORT}, {_d.year} issue page) -->", t)
    t = t.replace(f"/pages/previews/{I}/PHNEWS-{I}-preview.html", f"/pages/archive/issues/{I}.html")
    for x, y in MAP.items(): t = t.replace(L + f"previews/{I}/" + x, L + y)
    return t
pages = {y: _sr.assert_no_stamp(_rd.apply(_sr.enforce_title_months(clean((PV / x).read_text(encoding="utf-8"))), y)[0], y) for x, y in MAP.items()}
s = clean(s)
s = re.sub(r"<!-- ph-review-stamp:start -->.*?<!-- ph-review-stamp:end -->", "", s, flags=re.S)  # R22
_sr.assert_no_stamp(s, NAME)  # R40
s = s.replace(f"PHNEWS {LONG} — DRAFT (not sent)", f"PHNEWS {LONG}")
assert f"previews/{I}" not in s and "DRAFT" not in s and "noindex" not in s, "preview-only text left in the SEND file"
s = _st.trim(_sr.enforce_title_months(s))  # R18 (no listen_fix: the builder already applied the R1/R18c Listen inset, Oct 24)
s = _sr.assert_archive_labels(_sr.archive_labels(s), NAME)  # R41/R43
s = _sr.assert_source_credits(s, NAME)
s = _sr.assert_community_stories(s, NAME, None)  # R45
_r42 = _ss.check_issue(s)
if _r42: raise SystemExit("R42: " + "; ".join(_r42))
_need = [p for p, src in _ss.SOURCES.items() if src.get("use_existing_page") and _ss.BASE + p in s]
_need += sorted(set(re.findall(r'<a href="' + re.escape(L) + r'([^"?#]+)"[^>]*>Webmaster</a>', s)))  # R47
if not a.dry_run:
    for y, t in pages.items(): (REPO / "pages" / y).write_text(t, encoding="utf-8")
    for p in _need: _nl.add(REPO, p)
else:
    missing = [p for p in _need if not (REPO / "pages" / p).exists()]
    if missing: raise SystemExit(f"R47 (dry run): linked source pages missing {missing}")
s = _sr.assert_webmaster_more(s, NAME, REPO)
s = _sr.assert_event_sources(s, NAME)  # R48
if "<script" in s.lower(): raise SystemExit("R76: the SEND copy must contain no <script> (email Listen = plain links)")
out = ROOT / f"PHNEWS-{I}-SEND.html"; out.write_text(s, encoding="utf-8")
nas = ROOT / f"nas-layout/{I[:7]}/{I}/sent-final"; nas.mkdir(parents=True, exist_ok=True); (nas / NAME).write_text(s, encoding="utf-8")
print(("DRY RUN: " if a.dry_run else "") + f"{I}: {len(MAP)} preview pages mapped {list(MAP.values())}; SEND -> {out}")
if not a.dry_run: _lc.require_since(_T0)  # R49
_lc.require_nl(out)  # R49b
