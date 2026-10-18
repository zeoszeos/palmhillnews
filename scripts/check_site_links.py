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
# STYLE-RULES R41: no 'Previous Chair Reports' label on live non-archived pages (archived issue copies exempt)
r41=[]
for d in roots:
  for dp,_,fs in os.walk(os.path.join(R,d)):
    for f in fs:
      rel=os.path.relpath(os.path.join(dp,f),R)
      if f.endswith('.html') and not rel.startswith('pages/archive/issues/') and re.search(r'Previous (Chair Reports|Notices|Events|Meetings|Weekly Updates|Shareholders Reports|Tips|Videos)\b',open(os.path.join(dp,f),errors='ignore').read()): r41.append(rel)
print('R41 Previous-X label pages:',r41)
KNOWN = {('/pages/assets/ph-newsletter-shell.html', '/pages/assets/2026-10-04-recurring-activities-by-date.html')}  # design template, not served as a page link
sys.exit(1 if r41 or stamped or howto or (set(bad) - KNOWN) else 0)
