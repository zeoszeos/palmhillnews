#!/usr/bin/env python3
"""STYLE-RULES R61 guard: video data must match the LIVE club Committees page.
Fails if (1) archive/club-committees-live.json is missing or older than MAX_AGE_DAYS, or older than the data;
(2) a dated video on the live page is missing from archive/committee-videos.json (unless recorded as a dead 404 in
archive/club-videos-sync.json); (3) Latest videos (archive-items.json) is not the newest working recording per group.
--live re-pulls the page now (needs PALMHILL_CLUB_USER/PASS) instead of reading the saved pull."""
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_AGE_DAYS=7
def main(a):
  fails=[]
  if '--live' in a:
    import pull_club_videos as P; live=P.main()
  else:
    p=os.path.join(ROOT,'archive/club-committees-live.json')
    if not os.path.exists(p): print('R61 FAIL: no live pull (run build_meeting_video_archive.py)'); return 1
    live=json.load(open(p))
  age=(datetime.datetime.now().astimezone()-datetime.datetime.fromisoformat(live['fetched_at'])).days
  if age>MAX_AGE_DAYS: fails.append(f'live pull is {age} days old (max {MAX_AGE_DAYS}); data is stale vs the club page')
  data=json.load(open(os.path.join(ROOT,'archive/committee-videos.json')))
  sync=json.load(open(os.path.join(ROOT,'archive/club-videos-sync.json')))
  dead={(d['url'],d['date']) for d in sync.get('dead',[])}
  have={(r['url'],r['date']) for r in data}
  for i in live['items']:
    k=(i['url'],i['date'])
    if k not in have and k not in dead: fails.append(f"missing listed video: {i['group']} {i['date']} {i['url']}")
  newest=max(r['date'] for r in data)
  if newest>live['fetched_at'][:10]: fails.append('data has a video dated after the live pull')
  lat=json.load(open(os.path.join(ROOT,'archive/archive-items.json')))['sections']['videos']['items']
  slug={'Board Meeting':'board','Buildings & Grounds Committee':'buildings-and-grounds','Communications Committee':'communications',
    'Finance Committee':'finance','Golf Committee':'golf','Planning & Environmental Committee':'planning-and-environmental',
    'Rules & Regulations Committee':'rules-and-regulations','Real Estate Committee':'real-estate'}
  for it in lat:
    rs=[r for r in data if r['group']==slug.get(it['group']) and r.get('link_status')=='ok' and 'drive.google' in r['host']]
    if rs and max(r['date'] for r in rs)>it['date']: fails.append(f"Latest videos: {it['group']} shows {it['date']}, newer {max(r['date'] for r in rs)} exists")
  for f in fails: print('R61 FAIL:',f)
  if not fails: print(f"R61 OK: {len(live['items'])} live-page videos all in data ({len(dead)} dead left out); pull {live['fetched_at']}; Latest = newest per group")
  return 1 if fails else 0
if __name__=='__main__': sys.exit(main(sys.argv))
