"""Make the unlisted live preview of the Oct 18 draft for zeoszeos/palmhillnews (preview-only pages).
Writes into REPO/pages/previews/2026-10-18/: PHNEWS-2026-10-18-preview.html + notices/<slug>.html (each with Listen)."""
import re, sys, html as H
sys.path.insert(0, "/workspace/oct18-batch/scripts"); import style_rules as _sr  # STYLE-RULES.md (shared)
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
       'Source: Tony Ciaramitaro, Communications Chair · <a href="/pages/archive/did-you-know.html" style="color:#3A6B1A">Did You Know Archives →</a>')

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
