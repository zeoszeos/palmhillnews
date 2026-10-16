#!/usr/bin/env python3
"""Monthly Link save (STYLE-RULES.md R15, Steven Oct 16 2026): every Palm Hill Link PDF is kept on Vercel permanently,
because issues drop off the Link website. Run on each Friday build: resolves the current download on monthly-media
NID=121; if that month is not yet in pages/archive/link/, downloads it, adds it to data/link-issues.json (newest first)
and rebuilds pages/archive/palm-hill-link.html. Prints what it did; the builder commits it in the next PR."""
import json, os, re, sys, subprocess, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = "https://monthly-media.com/mmnewsletter.php?NID=121"
FULL = ("January","February","March","April","May","June","July","August","September","October","November","December")
UA = {"User-Agent": "Mozilla/5.0 (PHNEWS builder)"}
def main():
    html = urllib.request.urlopen(urllib.request.Request(HUB, headers=UA), timeout=30).read().decode("utf-8", "ignore")
    m = re.search(r'newsletter_download\.php\?t=([0-9a-f]+)&(?:amp;)?type=newsletter', html)
    if not m: print("LINK SAVE: no newsletter download on NID=121 - check by hand"); return 1
    url = f"https://monthly-media.com/newsletter_download.php?t={m.group(1)}&type=newsletter"
    r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120)
    fn = r.headers.get("Content-Disposition", "")
    mm = re.search(r"Link_-_(" + "|".join(FULL) + r")_(\d{4})", fn)
    if not mm: print(f"LINK SAVE: cannot read month from {fn!r} - check by hand"); return 1
    ym = f"{mm.group(2)}-{FULL.index(mm.group(1))+1:02d}"; name = f"Link-{ym}.pdf"; dst = f"{R}/pages/archive/link/{name}"
    D = json.load(open(f"{R}/data/link-issues.json"))
    if os.path.exists(dst) and any(i["month"] == ym for i in D["issues"]):
        print(f"LINK SAVE: {mm.group(1)} {mm.group(2)} already hosted ({name})"); return 0
    data = r.read()
    if not data.startswith(b"%PDF"): print("LINK SAVE: download is not a PDF - check by hand"); return 1
    open(dst, "wb").write(data)
    if not any(i["month"] == ym for i in D["issues"]):
        D["issues"].insert(0, {"month": ym, "pdf": name}); D["issues"].sort(key=lambda i: i["month"], reverse=True)
        json.dump(D, open(f"{R}/data/link-issues.json", "w"), indent=1, ensure_ascii=False)
    subprocess.run([sys.executable, f"{R}/scripts/build_link_archive.py"], check=True)
    print(f"LINK SAVE: NEW issue {mm.group(1)} {mm.group(2)} saved to pages/archive/link/{name} ({len(data)/1e6:.1f} MB) - commit + PR, copy to Omen D:\\PHNEWS\\link\\")
    return 0
if __name__ == "__main__": sys.exit(main())
