"""Publish Oct 18 (Vol.1 No.14) to the Vercel archive (no email). Copies preview pages to permanent homes (preview URLs stay valid),
writes ../PHNEWS-2026-10-18-FINAL.html and the NAS-layout copy for build_archive --issues-from."""
import re, sys, shutil
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import style_rules as _sr  # STYLE-RULES.md
from pathlib import Path
REPO = Path(sys.argv[1]); ROOT = Path(__file__).resolve().parent.parent
PV = REPO / "pages/previews/2026-10-18"; L = "https://palmhillnews.vercel.app/pages/"
ISSUE = L + "archive/issues/2026-10-18.html"
(REPO / "pages/assets/phnews/2026-10-18").mkdir(parents=True, exist_ok=True)
shutil.copy(PV / "assets/fb-group-qr.png", REPO / "pages/assets/phnews/2026-10-18/fb-group-qr.png")
MAP = {"facebook-group-notice.html": "2026-10-18-facebook-group-notice.html",
       "facebook-group-did-you-know.html": "2026-10-18-did-you-know-facebook-group.html",
       "did-you-know-traffic-rules.html": "2026-10-18-did-you-know-traffic-rules.html"}  # Steven Oct 17: David Bates rule
for f in sorted((PV / "notices").glob("*.html")): MAP["notices/" + f.name] = f"2026-10-18-notice-{f.name}"
def clean(t):
    t = t.replace('<meta name="robots" content="noindex,nofollow">\n', "").replace('<meta name="robots" content="noindex,nofollow">', "")
    t = t.replace(" (Oct 18 preview)", "").replace(" (October 18 preview)", "")
    t = re.sub(r"<!-- ph-archive-nav:none \(PREVIEW-ONLY[^>]*-->", "<!-- ph-archive-nav:none (Oct 18, 2026 issue page) -->", t)
    t = t.replace("/pages/previews/2026-10-18/assets/fb-group-qr.png", "/pages/assets/phnews/2026-10-18/fb-group-qr.png")
    t = t.replace(L + "previews/2026-10-18/assets/fb-group-qr.png", L + "assets/phnews/2026-10-18/fb-group-qr.png")
    t = t.replace("/pages/previews/2026-10-18/PHNEWS-2026-10-18-preview.html", "/pages/archive/issues/2026-10-18.html")
    for a, b in MAP.items(): t = t.replace(L + "previews/2026-10-18/" + a, L + b)
    return t
import readability as _rd  # STYLE-RULES RD1-RD13 on the published notice pages (never on the issue / SEND file)
for a, b in MAP.items(): (REPO / "pages" / b).write_text(_sr.assert_no_stamp(_rd.apply(_sr.enforce_title_months(clean((PV / a).read_text(encoding="utf-8"))), b)[0], b), encoding="utf-8")
s = clean((PV / "PHNEWS-2026-10-18-preview.html").read_text(encoding="utf-8"))
s = re.sub(r"<!-- ph-review-stamp:start -->.*?<!-- ph-review-stamp:end -->", "", s, flags=re.S)  # R22: review-only stamp never published
_sr.assert_no_stamp(s, "PHNEWS-2026-10-18-FINAL.html")  # R40
s = s.replace("PHNEWS October 18, 2026 — DRAFT (not sent)", "PHNEWS October 18, 2026")
assert "previews/2026-10-18" not in s and "DRAFT" not in s and "noindex" not in s
import summary_trim as _st
s = _st.trim(_sr.listen_fix(_sr.enforce_title_months(s)))  # R18
assert _sr.dyk_more_link_ok(s, "2026-10-18-did-you-know-traffic-rules.html"), "R39: DYK More -> must link the item page"
s = _sr.assert_archive_labels(_sr.archive_labels(s), "PHNEWS-2026-10-18-FINAL.html")  # R41/R43
s = _sr.assert_source_credits(s, "PHNEWS-2026-10-18-FINAL.html")
s = _sr.assert_community_stories(s, "PHNEWS-2026-10-18-FINAL.html", None)  # R45 (omission needs Steven's approval in the builder)  # STYLE-RULES L27/L29: linked short 'Webmaster', no dates on Source credits
import source_sections as _ss, notice_listen as _nl  # STYLE-RULES R42
_r42 = _ss.check_issue(s)
if _r42: raise SystemExit("R42: " + "; ".join(_r42))
for _p, _src in _ss.SOURCES.items():  # existing source page used by a notice: standard Listen block, same URL
    if _src.get("use_existing_page") and _ss.BASE + _p in s: _nl.add(REPO, _p)
# R47 (Steven, Oct 18 12:23 AM): every Webmaster full-email page linked from the issue carries the standard Listen block, and a
# Webmaster-sourced item's More → / Listen open that same page (the short 2026-10-18-notice-*.html pages stay live, unlinked).
for _wm in sorted(set(re.findall(r'<a href="' + re.escape(L) + r'([^"?#]+)"[^>]*>Webmaster</a>', s))): _nl.add(REPO, _wm)
s = _sr.assert_webmaster_more(s, "PHNEWS-2026-10-18-FINAL.html", REPO)
(ROOT / "PHNEWS-2026-10-18-FINAL.html").write_text(s, encoding="utf-8")
nas = ROOT / "nas-layout/2026-10/2026-10-18/sent-final"; nas.mkdir(parents=True, exist_ok=True)
(nas / "PHNEWS-2026-10-18-FINAL.html").write_text(s, encoding="utf-8")
print(len(MAP), "pages"); [print(" ", b) for b in MAP.values()]
