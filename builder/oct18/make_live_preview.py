"""Make the unlisted live preview of the Oct 18 draft for zeoszeos/palmhillnews (preview-only pages).
Writes into REPO/pages/previews/2026-10-18/: PHNEWS-2026-10-18-preview.html + notices/<slug>.html (each with Listen)."""
import re, sys, html as H
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import style_rules as _sr  # STYLE-RULES.md (shared)
import source_sections as _ss  # STYLE-RULES R42
from pathlib import Path
REPO = Path(sys.argv[1]); ROOT = Path(__file__).resolve().parent.parent
OUT = REPO / "pages/previews/2026-10-18"; (OUT / "notices").mkdir(parents=True, exist_ok=True)
LIVE = "https://palmhillnews.vercel.app/pages/previews/2026-10-18/"
s = (ROOT / "PHNEWS-2026-10-18-preview.html").read_text(encoding="utf-8")
w = (REPO / "pages/2026-10-09-weekly-manager-update.html").read_text(encoding="utf-8")
script = w[w.find("<!-- ph-page-listen:start -->"):w.find("<!-- ph-page-listen:end -->") + len("<!-- ph-page-listen:end -->")]
btn = re.findall(r'<a class="ph-listen".*?</a>', w, re.S)[0]
a, b = s.find(">Community Notices</span>"), s.find('<div class="canonical-section">', s.find(">Community Notices</span>"))
sec = s[a:b]
rows = [x for x in sec.split('<tr style="background:')[1:]]
new = sec
for r in rows:
    t = re.search(r'padding-right:8px;">([^<]+)</td>', r).group(1)
    body = re.search(r'<div style="font-size:15px;color:#333333;margin-top:3px;">(.*?)</div>', r, re.S).group(1)
    src = re.search(r'<div style="font-size:13px;color:#666666;margin-top:5px;">(.*?)</div>', r, re.S).group(1)
    slug = re.sub(r"[^a-z0-9]+", "-", H.unescape(t).lower()).strip("-")
    # STYLE-RULES R42: a notice that uses its existing source page (scripts/source_sections.py use_existing_page) gets NO generated
    # notice page; its Listen (and the R18 More →) open that page, e.g. Info from Linda -> 2026-10-08-info-from-linda-notice.html.
    _ex = _ss.existing_page(t)
    if _ex:
        url = _ex + "?listen=1"
        r2 = re.sub(r'(<td valign="top" align="right" style="font-size:13px;line-height:18px;text-align:right;white-space:nowrap;width:1%;"><a href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), r, count=1)
        new = new.replace(r, r2); continue
    page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{t} — Palm Hill Country Club (Oct 18 preview)</title>
<link rel="stylesheet" href="/pages/assets/ph-newsletter.css">
<style>main{{max-width:780px;margin:0 auto;padding:16px;font:18px/1.6 Arial,Helvetica,sans-serif}}.content-card{{background:#fff;border:1px solid #d7d1bd;border-radius:12px;padding:16px;margin:12px 0}}.hd{{display:flex;align-items:center;gap:12px;flex-wrap:wrap}}</style>
</head><body>
<!-- ph-archive-nav:none (PREVIEW-ONLY notice Listen page for the unsent Oct 18, 2026 draft; not linked from any archive) -->
<main><div class="hd"><h1 class="ph-section" style="margin:0">{t}</h1>{btn}</div>
<div class="content-card"><p>{body}</p></div>
<p class="source" style="font-size:14px;color:#666">{src}</p>
</main>
{script}
</body></html>
'''
    (OUT / "notices" / f"{slug}.html").write_text(_sr.enforce_title_months(page), encoding="utf-8")
    url = f"{LIVE}notices/{slug}.html?listen=1"
    r2 = re.sub(r'(<td valign="top" align="right" style="font-size:13px;line-height:18px;text-align:right;white-space:nowrap;width:1%;"><a href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), r, count=1)
    new = new.replace(r, r2)
s = s[:a] + new + s[b:]
assert "#listen-pending" not in s
sys.path.insert(0, str(Path(__file__).resolve().parent)); _listen_fix = _sr.listen_fix
import summary_trim as _st; s = _st.trim(s)  # STYLE-RULES.md R18: 3-line summaries (notice pages above keep full text)
s = _sr.enforce_title_months(_listen_fix(s))  # one-line Listen, 14px in from the right (Steven Oct 16)
s = s.replace("<head>", '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
(OUT / "PHNEWS-2026-10-18-preview.html").write_text(s, encoding="utf-8")

# ---- Batch item 3 (Oct 16): Tony's FB item gets its own pages (full article + QR); main issue links here instead of showing the QR
FBURL = "https://www.facebook.com/groups/720846344400510"
QR = "/pages/previews/2026-10-18/assets/fb-group-qr.png"
G = "#3A6B1A"
def fbpage(fn, title, body, src):
    qr = (f'<div class="content-card" style="text-align:center"><a href="{FBURL}" style="display:inline-block"><img src="{QR}" width="220" height="220" '
          f'alt="QR code: Palm Hill Country Club - Residents Only Group on Facebook" style="display:block;width:220px;height:220px;max-width:100%;border:0;background:#fff"></a>'
          f'<div style="font-size:15px;color:#666;margin-top:6px">Scan with your phone to join</div>'
          f'<div style="font-size:15px;margin-top:6px;word-break:break-all"><a href="{FBURL}" style="color:{G}">{FBURL}</a></div></div>')
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{title} — Palm Hill Country Club (Oct 18 preview)</title>
<link rel="stylesheet" href="/pages/assets/ph-newsletter.css">
<style>main{{max-width:780px;margin:0 auto;padding:16px;font:18px/1.6 Arial,Helvetica,sans-serif}}.content-card{{background:#fff;border:1px solid #d7d1bd;border-radius:12px;padding:16px;margin:12px 0}}.hd{{display:flex;align-items:center;gap:12px;flex-wrap:wrap}}</style>
</head><body>
<!-- ph-archive-nav:none (PREVIEW-ONLY page for the unsent Oct 18, 2026 draft) -->
<main><div class="hd"><h1 class="ph-section" style="margin:0">{title}</h1>{btn}</div>
<div class="content-card"><p>{body}</p></div>
{qr}
<p class="source" style="font-size:14px;color:#666">{src}</p>
<p style="font-size:15px"><a href="/pages/previews/2026-10-18/PHNEWS-2026-10-18-preview.html" style="color:{G}">← Back to the newsletter</a></p>
</main>
{script}
</body></html>
"""
    (OUT / fn).write_text(_sr.enforce_title_months(page), encoding="utf-8")
NOTICE_BODY = ('Palm Hill now has a private Facebook group just for residents, with park news, event reminders and photos posted by the admins (comments are turned off). '
    'Every request is checked against the member directory, so use the address and email the Office has for you, answer all 3 questions, or Facebook will turn the request down. '
    f'Search Facebook for &quot;Palm Hill Country Club - Residents Only Group&quot; or join here: <a href="{FBURL}" style="color:{G};">{FBURL}</a>')
fbpage("facebook-group-notice.html", "Join the Palm Hill Residents Group on Facebook", NOTICE_BODY, "Source: Tony Ciaramitaro, Communications Chair")
fbpage("facebook-group-did-you-know.html", "Did You Know? Palm Hill Residents Facebook Group",
       'Did you know Palm Hill has a private, residents-only Facebook group? Park news, events and photos. Search &quot;Palm Hill Country Club - Residents Only Group&quot; on Facebook and answer all 3 questions.',
       'Source: Tony Ciaramitaro, Communications Chair · <a href="/pages/archive/did-you-know.html" style="color:#3A6B1A">Did You Know? Archives →</a>')

# ---- Steven, Oct 17 1:40 PM: Did You Know rule of the week from David Bates (palmhillblast "Park Rule for Newsletter",
# Sat Oct 17 1:17 PM ET, his corrected resend). Full narrative in his wording (whitespace-only fixes); Listen like the FB page.
DYK_RULES_PARAS = [
    "A space has been provided in this newsletter for a discussion on the rules and regulations in Palm Hill. It is felt that having a review and discussion on specific rules we all will have a better understanding and appreciation for the rule.",
    "<strong>XI. TRAFFIC RULES</strong>",  # R34: heading linked to DYK_RULES_PDF below (his wording unchanged)
    "Let&#x27;s face it - we have all seen certain rules completely ignored and the rule violated.",
    "This week we would like to focus on traffic rules. The very first sentence in the rule states that the speed limit in the park is 15 MPH. We have all seen the rat race to get to the Seminole entrance or the 8th Ave entrance. Perhaps leaving home 5-10 minutes earlier or getting home a few minutes later would be okay.",
    "Sections of the rule: The speed limit in the park is 15 mph. It&#x27;s okay to go 15 mph and make a full stop at a stop sign. Further - Golf Carts and all motor vehicles shall not be operated after dark without tail lights and headlights. Golf carts and licensed mopeds shall not be operated by anyone under 16. Motorcycles are prohibited anywhere on Palm Hill property.. Please, all golf carts must be registered with the office. Most of all, be safe and be sure to follow the rules that are in place to protect us and follow a standard for the Park.",
]
# STYLE-RULES R33 (Steven, Oct 17 2:22 PM): a Did You Know piece ends with the contributor's name as a plain byline,
# exactly as given ("David Bates"), no title (he is Board VP; no title unless he asks). Guarded in style_rules.dyk_byline_ok.
# Dave asked for "Dave Bates, Board VP" (palmhillblast "Re: Park Rule for Newsletter", Sat Oct 17 5:12 PM ET) -> R33 "unless they ask"
DYK_RULES_BYLINE = "Dave Bates, Board VP"
# STYLE-RULES R34 (Steven, Oct 17 2:39 PM): a Did You Know piece that cites a park rule links to the official club PDF (never a
# hosted copy), on its own line after the piece card (byline stays the card's last paragraph, R33). URL checked 200 application/pdf,
# "Current as of September 30, 2026". Guarded in style_rules.dyk_rule_link_ok.
DYK_RULES_PDF = "https://www.palmhillcountryclub.net/editor_upload/File/Committee%20Meeting%20Minutes/Rules%20%26%20Regulations/Approved%20Rules%20%26%20Reg's/1-Rules%20and%20Regulations%20September%2030%202026.pdf"
DYK_RULES_PDF_LABEL = "Palm Hill Rules and Regulations (September 30, 2026) →"
DYK_RULES_PARAS = [x.replace("<strong>XI. TRAFFIC RULES</strong>", f'<strong><a class="dyk-rule-heading" href="{H.escape(DYK_RULES_PDF)}" style="color:#3A6B1A">XI. TRAFFIC RULES</a></strong>') for x in DYK_RULES_PARAS]
_dyk = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Did You Know? Traffic Rules — Palm Hill Country Club (Oct 18 preview)</title>
<link rel="stylesheet" href="/pages/assets/ph-newsletter.css">
<style>main{{max-width:780px;margin:0 auto;padding:16px;font:18px/1.6 Arial,Helvetica,sans-serif}}.content-card{{background:#fff;border:1px solid #d7d1bd;border-radius:12px;padding:16px;margin:12px 0}}.hd{{display:flex;align-items:center;gap:12px;flex-wrap:wrap}}</style>
</head><body>
<!-- ph-archive-nav:none (PREVIEW-ONLY page for the unsent Oct 18, 2026 draft) -->
<main><div class="hd"><h1 class="ph-section" style="margin:0">Did You Know? Traffic Rules</h1>{btn}</div>
<div class="content-card">{"".join(f"<p>{x}</p>" for x in DYK_RULES_PARAS)}<p class="dyk-byline">{DYK_RULES_BYLINE}</p></div>
<p class="dyk-rules-link" style="max-width:38em"><a href="{H.escape(DYK_RULES_PDF)}" style="color:#3A6B1A">{DYK_RULES_PDF_LABEL}</a></p>
<p class="source" style="font-size:14px;color:#666">Source: David Bates · <a href="/pages/archive/did-you-know.html" style="color:#3A6B1A">Did You Know? Archives →</a></p>
<p style="font-size:15px"><a href="/pages/previews/2026-10-18/PHNEWS-2026-10-18-preview.html" style="color:{G}">← Back to the newsletter</a></p>
</main>
{script}
</body></html>
"""
import json as _json
(ROOT / "data").mkdir(exist_ok=True); (ROOT / "data/dyk-traffic-rules-source.json").write_text(_json.dumps([H.unescape(re.sub(r"<[^>]+>", "", x)) for x in DYK_RULES_PARAS], indent=1), encoding="utf-8")  # R39 source
assert _sr.dyk_rule_link_ok(_dyk), "R34: park-rule Did You Know must link the official club PDF"
assert _sr.dyk_byline_ok(_dyk, DYK_RULES_BYLINE), "R33: Did You Know piece must end with the plain byline"
(OUT / "did-you-know-traffic-rules.html").write_text(_sr.enforce_title_months(_dyk), encoding="utf-8")

print("rows", len(rows), "->", OUT)

# STYLE-RULES.md format guard (Friday/Saturday builds report diffs; never blocks the write above)
import subprocess as _sp, os as _os
from datetime import datetime
from zoneinfo import ZoneInfo
_VR = "/workspace/.venv-vr/bin/python"; _G = "/workspace/oct18-batch/tests/golden/format-locked-2026-10-18/email"
if _os.path.exists(_VR) and _os.path.exists(_G) and not _os.environ.get("PHNEWS_SKIP_VR"):
    _r = _sp.run([_VR, "/workspace/oct18-batch/scripts/visual_regression.py", str(OUT / "PHNEWS-2026-10-18-preview.html"), "--golden", _G,
                  "--out", str(ROOT / f"vr-report-{datetime.now(ZoneInfo('America/New_York')):%Y%m%d-%H%M}")], capture_output=True, text=True)
    print(_r.stdout.strip() or _r.stderr.strip()[-800:])
    print({0: "FORMAT GUARD: clean", 1: "FORMAT GUARD: RULE FAILURES - fix before sending", 2: "FORMAT GUARD: visual diffs - review DIFF pngs"}.get(_r.returncode, f"FORMAT GUARD error {_r.returncode}"))
else:
    print("FORMAT GUARD skipped (venv or golden missing)")
# STYLE-RULES R40: no review/test stamp on any preview output
for _f in OUT.rglob("*.html"): _sr.assert_no_stamp(_f.read_text(encoding="utf-8"), str(_f.relative_to(REPO)))
