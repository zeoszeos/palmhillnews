#!/usr/bin/env python3
"""STYLE-RULES R61: pull the LIVE club Committees page (sign-in) and list every dated meeting video.
Credentials come only from env PALMHILL_CLUB_USER / PALMHILL_CLUB_PASS (never printed, never stored).
Writes archive/club-committees-live.json: {fetched_at, url, items:[{group,meeting,date,label,url}]}."""
import os, re, sys, json, html, datetime, http.cookiejar, urllib.request, urllib.parse
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'archive/club-committees-live.json')
PAGE='https://www.palmhillcountryclub.net/committees/'
# section heading on the club page -> (group slug, meeting name used in committee-videos.json)
SECTIONS=[
 ('Sewer Lining Project Meeting Video',('special-meetings','Sewer Lining Project')),
 ('Board Meeting Videos',('board','')),
 ('Committee Meeting Videos',None),
 ('Buildings & Grounds Committee',('buildings-and-grounds','')),
 ('Communications Committee',('communications','')),
 ('Finance Committee',('finance','')),
 ('Golf Committee',('golf','')),
 ('Planning & Environmental Committee',('planning-and-environmental','')),
 ('Rules & Regulations Committee',('rules-and-regulations','')),
 ('Real Estate Committee',('real-estate','')),
 ('Palm Hill Management Resource Team Town Hall Meeting Video',('special-meetings','PHMRT Town Hall')),
 ('Cable Broker Videos',('special-meetings','Cable Broker')),
 ('Strategic Planning Presentation Videos',('special-meetings','Strategic Planning')),
 ('Town Hall “Land Purchase Initiative” Meeting Video',('special-meetings','Land Purchase Initiative Town Hall')),
 ('Training Videos','STOP'),
]
def txt(s): return ' '.join(html.unescape(re.sub(r'<[^>]+>',' ',s)).replace('\xa0',' ').split())
def fetch():
  u,p=os.environ.get('PALMHILL_CLUB_USER'),os.environ.get('PALMHILL_CLUB_PASS')
  if not (u and p): sys.exit('R61: PALMHILL_CLUB_USER / PALMHILL_CLUB_PASS not set; cannot re-pull the live Committees page (build stops).')
  op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
  op.addheaders=[('User-Agent','Mozilla/5.0')]
  op.open(PAGE,timeout=30).read()
  data=urllib.parse.urlencode({'uname':u,'pass':p,'submit2':'Login'}).encode()
  r=op.open('https://www.palmhillcountryclub.net/login/?redirect=%2Fcommittees%2F',data,timeout=30)
  s=r.read().decode('utf-8','replace')
  if '/committees/' not in r.geturl() or 'Board Meeting Videos' not in s:
    sys.exit('R61: club sign-in failed or Committees page changed (build stops).')
  return s
def parse(s):
  marks=[]
  for m in re.finditer(r'<(h3|strong)[^>]*>(.*?)</\1>',s,re.S):
    t=txt(m.group(2))
    for name,val in SECTIONS:
      if t==name: marks.append((m.start(),val))
  if not marks: sys.exit('R61: no video sections found on the live page (build stops).')
  items=[]
  for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',s,re.S):
    cur=None
    for pos,val in marks:
      if pos<m.start(): cur=val
    if cur in (None,'STOP'): continue
    label=txt(m.group(2)); d=re.match(r'(\d\d)/(\d\d)/(\d{4})\s*(.*)',label)
    if not d: continue
    url=html.unescape(m.group(1)); g,meeting=cur
    items.append(dict(group=g,meeting=meeting,date=f'{d[3]}-{d[1]}-{d[2]}',label=label,note=d[4].strip(' .-'),url=url))
  return items
def main():
  s=fetch(); items=parse(s)
  out=dict(fetched_at=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),url=PAGE,count=len(items),items=items)
  json.dump(out,open(OUT,'w'),indent=1,ensure_ascii=False); print(f'R61: live Committees page pulled: {len(items)} dated video links')
  return out
if __name__=='__main__': main()
