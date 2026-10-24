import json,re
COMMITTEE_RE=re.compile(r"\bcommittee\b|\bboard of directors\b",re.I)
AS_REC={"Hand and Foot Cards","Ukulele Group","Ear Wax Removal","I Got It","Karaoke Obi-Time","Writing Club"}
CANON={"Communications Committee":"Communications Committee Meeting","Building & Grounds Committee":"Buildings and Grounds Committee Meeting","Planning & Environmental Committee":"Planning and Environmental Committee Meeting"}
D="/workspace/phnews-consolidation/oct18/data/"
def load(f): return json.load(open(D+f))["events"]
ok=lambda e:e.get("status")=="CONFIRMED" and e["name"]!="Private Event" and "test" not in e["name"].lower()
cm=lambda e:e.get("category")=="Meetings" and bool(COMMITTEE_RE.search(e["name"]))
inw=lambda e,w:w[0]<=e["date"]<=w[1]
def evsel(ev,w): return sorted([e for e in ev if ok(e) and inw(e,w) and not e.get("recurring") and not cm(e) and e["name"] not in AS_REC and e.get("category")!="CLOSURE" and not e.get("allDay") and (e.get("category")!="Meetings" or e["name"]=="Palm Hill MasterPlan Team")],key=lambda e:(e["date"],e["start"]))
def mtgs(ev,w):
  out,seen=[],set()
  for e in sorted([e for e in ev if ok(e) and cm(e) and inw(e,w)],key=lambda e:(e["date"],e["start"])):
    n=CANON.get(e["name"],e["name"]);k=n.lower().replace(" meeting","")
    if k in seen: continue
    seen.add(k);out.append(dict(e,name=n))
  return out
o=load("cal-20261018-0025.json");n=load("cal-20261020-1440.json")
O=evsel(o,("2026-10-18","2026-10-24"))+evsel(o,("2026-10-25","2026-11-15"))
N=evsel(n,("2026-10-25","2026-10-31"))+evsel(n,("2026-11-01","2026-11-22"))
k=lambda e:(e["name"],e["date"],e["start"])
OK={k(e) for e in O};NK={k(e) for e in N}
print("OCT18 issue events",len(O),"OCT25 issue events",len(N))
print("NEW:");[print("  ",e["date"],e["start"],e["name"],"@",e["venue"]) for e in N if k(e) not in OK]
print("PAST/DROPPED:");[print("  ",e["date"],e["start"],e["name"],"@",e["venue"], "(past)" if e["date"]<"2026-10-25" else "(dropped)") for e in O if k(e) not in NK]
print("OCT18 meetings:");[print("  ",e["date"],e["start"],e["name"],e["venue"]) for e in mtgs(o,("2026-10-18","2026-11-17"))]
print("OCT25 meetings:");[print("  ",e["date"],e["start"],e["name"],e["venue"]) for e in mtgs(n,("2026-10-25","2026-11-24"))]
print("ALL committee entries changed between snapshots (any status, Oct18-Dec17):")
f=lambda ev:{(e["name"],e["date"]):e for e in ev if cm(e) or COMMITTEE_RE.search(e["name"]) or "board" in e["name"].lower()}
A,B=f(o),f(n)
for x in sorted(set(A)|set(B),key=lambda x:x[1]):
  if x[1]>"2026-12-17" or x[1]<"2026-10-18": continue
  a,b=A.get(x),B.get(x)
  if a is None: print("  ADDED",x,b["start"],b["status"])
  elif b is None: print("  REMOVED",x,a["start"],a["status"])
  else:
    d={q:(a.get(q),b.get(q)) for q in ("start","end","venue","status","info","cancelReason") if a.get(q)!=b.get(q)}
    if d: print("  CHANGED",x,d)
