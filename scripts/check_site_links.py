#!/usr/bin/env python3
"""Site internal-link guard + STYLE-RULES R37: every internal href/src resolves to a file (pages/events/reports/public) or a vercel.json redirect; no live (non-issue) page links the retired how-to-videos.html. Exit 1 on R37 hits or new broken links."""
import re,os,json,sys,urllib.parse
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V=json.load(open(R+'/vercel.json')); red={r['source'] for r in V.get('redirects',[])}
roots={'pages':'pages','events':'events','reports':'reports'}
bad=[];howto=[];n=0
for d in roots:
  for dp,_,fs in os.walk(os.path.join(R,d)):
    for f in fs:
      if not f.endswith('.html'): continue
      fp=os.path.join(dp,f); rel='/'+os.path.relpath(fp,R); t=open(fp,errors='ignore').read()
      if 'how-to-videos.html' in t and not rel.startswith('/pages/archive/issues/') and not rel.endswith('/how-to-videos.html'): howto.append(rel)
      for u in re.findall(r'(?:href|src)="([^"#?]+)',t):
        if u.startswith('https://palmhillnews.vercel.app'): u=u[len('https://palmhillnews.vercel.app'):]
        elif re.match(r'^[a-z]+:',u) or u.startswith('//'): continue
        if not u.startswith('/'): u=os.path.normpath(os.path.join(os.path.dirname(rel),u))
        u=urllib.parse.unquote(u); n+=1
        p=R+u; ok=os.path.isfile(R+'/public'+u) or u in red or os.path.isfile(p) or os.path.isfile(p.rstrip('/')+'/index.html') or u=='/'
        if not ok: bad.append((rel,u))
print('internal links',n,'broken',len(bad)); [print(' ',a,b) for a,b in sorted(set(bad))[:40]]
print('live pages linking how-to-videos:',howto)
# STYLE-RULES R40: no review/test stamp on any served page
stamped=[]
for d in roots:
  for dp,_,fs in os.walk(os.path.join(R,d)):
    for f in fs:
      if f.endswith('.html'):
        t=open(os.path.join(dp,f),errors='ignore').read()
        if 'ph-review-stamp' in t or 'Review copy' in t or 'Calendar checked:' in t or re.search(r'cal-\d{8}(?:-\d{4})?\.json',t): stamped.append(os.path.relpath(os.path.join(dp,f),R))
print('R40 stamped pages:',stamped)
# STYLE-RULES R41/R43: no retired archive label (Previous X, Chair Report Archives, Palm Hill Archives link, Did You Know? Archives,
# singular Video Archive, Past X) on live non-archived pages (archived issue copies exempt)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import style_rules as _SR
r41=[]
for d in roots:
  for dp,_,fs in os.walk(os.path.join(R,d)):
    for f in fs:
      rel=os.path.relpath(os.path.join(dp,f),R)
      if f.endswith('.html') and not rel.startswith('pages/archive/issues/') and re.search(_SR.RETIRED_ARCHIVE_LABEL_RE,open(os.path.join(dp,f),errors='ignore').read()): r41.append(rel)
print('R41/R43 retired archive label pages:',r41)
KNOWN = {('/pages/assets/ph-newsletter-shell.html', '/pages/assets/2026-10-04-recurring-activities-by-date.html')}  # design template, not served as a page link
# STYLE-RULES R44 (Steven, Oct 17 11:35 PM + 11:51 PM): every archive page's top area = exactly one 'All Archives →' link to
# main.html (main.html itself: none; redirect stubs and archived issue copies are skipped).
r44=[]
for dp,_,fs in os.walk(os.path.join(R,'pages','archive')):
  for f in fs:
    rel=os.path.relpath(os.path.join(dp,f),R)
    if not f.endswith('.html') or rel.startswith('pages/archive/issues/'): continue
    s=open(os.path.join(dp,f),errors='ignore').read()
    if re.search(r'http-equiv="?refresh',s,re.I): continue
    v=_SR.archive_top_violations(s,is_hub=(rel=='pages/archive/main.html'))
    if v: r44.append(f"{rel}: {'; '.join(v)}")
print('R44 archive top-area violations:',r44)
# STYLE-RULES L27/L29: Source credits on the current issue (review copy) and its generated notice pages carry no date and
# every 'Webmaster' is the linked short word. Archived issue copies keep their sent wording and are not checked.
l27=[]
_ISS=_SR.current_issue(R)  # A6 (Oct 24): current issue, not a hard-coded Oct 18
for rel in [f'pages/previews/{_ISS}/PHNEWS-{_ISS}-preview.html']+sorted('pages/'+f for f in os.listdir(os.path.join(R,'pages')) if f.startswith(f'{_ISS}-notice-')):
  fp=os.path.join(R,rel)
  if os.path.exists(fp):
    v=_SR.source_credit_violations(open(fp,errors='ignore').read())
    if v: l27.append(f"{rel}: {'; '.join(v)}")
print('L27/L29 Source credit violations:',l27)
# STYLE-RULES R49 (Steven, Oct 18 12:41 AM): every Listen page reads all visible content (scripts/check_listen_coverage.py)
import subprocess as _sp49
_lc_py = os.environ.get("PHNEWS_VR_PY", "/workspace/.venv-vr/bin/python")
if os.path.exists(_lc_py):
  _r49 = _sp49.run([_lc_py, os.path.join(R, "scripts", "check_listen_coverage.py")], capture_output=True, text=True)
  print((_r49.stdout or _r49.stderr).strip()[:3000]); r49 = _r49.returncode != 0
else:
  print("R49 Listen coverage: guard unavailable (" + _lc_py + " missing) -- FAIL, it is a required step"); r49 = True
sys.exit(1 if r41 or r44 or l27 or r49 or stamped or howto or (set(bad) - KNOWN) else 0)
