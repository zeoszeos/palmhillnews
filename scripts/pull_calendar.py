"""STYLE-RULES R21 (Steven, Oct 16 11:32 PM): re-pull Tony's calendar feed right before the proof build and the publish build.
Saves a new dated snapshot data/cal-YYYYMMDD-HHMM.json (never overwrites an older one), prints the diff against the
previous snapshot (time/date/room/status/cancel/info changes, adds, removals), and returns the new path."""
import glob, json, os, sys, urllib.parse, urllib.request
from datetime import datetime
FEED = "https://script.google.com/macros/s/AKfycbyvtkPTYvMnc5u_BmQdbRezCRNItiYdCDYe1jVZ3lN5qICGQwyeLPpA9Js40R9RTdI/exec"
FIELDS = ("date", "start", "end", "venue", "status", "movedTo", "place", "info", "cancelReason", "link", "recurring", "category")
def key(e): return (e["name"], e["date"], e["start"])
def diff(old, new):
    O = {key(e): e for e in old}; N = {key(e): e for e in new}; out = []
    for k in sorted(set(O) | set(N), key=lambda k: (k[1], k[2], k[0])):
        a, b = O.get(k), N.get(k)
        if a is None: out.append(f"ADDED   {k[1]} {k[2]} {k[0]} @ {b['venue']} [{b['status']}]")
        elif b is None: out.append(f"REMOVED {k[1]} {k[2]} {k[0]} @ {a['venue']} [{a['status']}]")
        else:
            d = {f: (a.get(f), b.get(f)) for f in FIELDS if a.get(f) != b.get(f)}
            if d: out.append(f"CHANGED {k[1]} {k[2]} {k[0]}: {d}")
    return out
def pull(data_dir, start, end):
    prev = sorted(glob.glob(os.path.join(data_dir, "cal-*.json")))
    raw = urllib.request.urlopen(urllib.request.Request(FEED + "?" + urllib.parse.urlencode({"action": "range_events", "start": start, "end": end}),
                                 headers={"User-Agent": "PHNEWS/1.0"}), timeout=90).read()
    d = json.loads(raw)
    if d.get("success") is not True or d.get("count") != len(d.get("events", [])) or not d["events"]: raise SystemExit("calendar pull failed/invalid - do not build")
    path = os.path.join(data_dir, f"cal-{datetime.now():%Y%m%d-%H%M}.json"); open(path, "wb").write(raw)
    if prev:
        ch = diff(json.load(open(prev[-1]))["events"], d["events"])
        print(f"calendar re-pulled: {d['count']} events -> {os.path.basename(path)}; {len(ch)} change(s) vs {os.path.basename(prev[-1])}")
        for c in ch: print("  " + c)
    return path
if __name__ == "__main__": print(pull(sys.argv[1], sys.argv[2], sys.argv[3]))
