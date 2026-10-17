#!/usr/bin/env python3
"""Monthly Link save (STYLE-RULES.md R15 + R29, Steven Oct 16-17 2026): every Palm Hill Link PDF is kept permanently,
because issues drop off the Link website, but NEVER inside the Vercel deployment (Deployment Storage).

Run on each Friday build. Resolves the current download on monthly-media NID=121. If that month is new:
  1. downloads it (must start with %PDF);
  2. commits it to branch `link-pdf-store` (GitHub contents API; the branch is never merged or deployed);
  3. uploads it as an asset of GitHub release `link-pdfs` (permanent copy + fallback);
  4. adds {month, pdf, bytes, url} to data/link-issues.json (url = jsDelivr pinned to the store commit, application/pdf);
  5. rewrites the vercel.json redirects (/pages/archive/link/<pdf> -> url) and rebuilds pages/archive/palm-hill-link.html.
The PDF is never written under pages/. Leaves a copy in builder/link-new/ (git-ignored) for the Omen D:\\PHNEWS\\link\\ copy.
Needs `gh` logged in as zeoszeos. Prints what it did; the builder commits data + vercel.json + page in the week's batched PR."""
import base64, json, os, re, shutil, subprocess, sys, tempfile, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{R}/scripts")
import link_store as L
HUB = "https://monthly-media.com/mmnewsletter.php?NID=121"
FULL = ("January","February","March","April","May","June","July","August","September","October","November","December")
UA = {"User-Agent": "Mozilla/5.0 (PHNEWS builder)"}
GH = shutil.which("gh") or "/usr/local/bin/gh"

def gh(*args, input_file=None):
    cmd = [GH, "api", *args] + (["--input", input_file] if input_file else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

def store_commit(name, path):
    """Commit `name` to the store branch unless it is already there; return the commit sha that holds it."""
    rc, out, _ = gh(f"repos/{L.REPO}/commits?sha={L.STORE_BRANCH}&path={name}&per_page=1")
    if rc == 0 and json.loads(out): return json.loads(out)[0]["sha"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as t:
        json.dump({"message": f"Link PDF store: add {name}", "branch": L.STORE_BRANCH,
                   "content": base64.b64encode(open(path, "rb").read()).decode()}, t)
    rc, out, err = gh("-X", "PUT", f"repos/{L.REPO}/contents/{name}", input_file=t.name); os.unlink(t.name)
    if rc != 0: raise SystemExit(f"LINK SAVE: store commit failed for {name}: {err.strip()[:300]}")
    return json.loads(out)["commit"]["sha"]

def release_upload(path, name):
    r = subprocess.run([GH, "release", "view", L.RELEASE_TAG, "-R", L.REPO, "--json", "assets", "-q", ".assets[].name"],
                       capture_output=True, text=True)
    if name in r.stdout.split(): return "already on release"
    r = subprocess.run([GH, "release", "upload", L.RELEASE_TAG, path, "-R", L.REPO], capture_output=True, text=True)
    if r.returncode != 0: raise SystemExit(f"LINK SAVE: release upload failed for {name}: {r.stderr.strip()[:300]}")
    return "uploaded to release"

def main():
    html = urllib.request.urlopen(urllib.request.Request(HUB, headers=UA), timeout=30).read().decode("utf-8", "ignore")
    m = re.search(r'newsletter_download\.php\?t=([0-9a-f]+)&(?:amp;)?type=newsletter', html)
    if not m: print("LINK SAVE: no newsletter download on NID=121 - check by hand"); return 1
    url = f"https://monthly-media.com/newsletter_download.php?t={m.group(1)}&type=newsletter"
    r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120)
    fn = r.headers.get("Content-Disposition", "")
    mm = re.search(r"Link_-_(" + "|".join(FULL) + r")_(\d{4})", fn)
    if not mm: print(f"LINK SAVE: cannot read month from {fn!r} - check by hand"); return 1
    ym = f"{mm.group(2)}-{FULL.index(mm.group(1))+1:02d}"; name = f"Link-{ym}.pdf"
    D = L.load()
    if any(i["month"] == ym and i.get("url") for i in D["issues"]):
        print(f"LINK SAVE: {mm.group(1)} {mm.group(2)} already hosted ({name})"); return 0
    data = r.read()
    if not data.startswith(b"%PDF"): print("LINK SAVE: download is not a PDF - check by hand"); return 1
    os.makedirs(f"{R}/builder/link-new", exist_ok=True); local = f"{R}/builder/link-new/{name}"
    open(local, "wb").write(data)
    sha = store_commit(name, local); rel = release_upload(local, name)
    it = next((i for i in D["issues"] if i["month"] == ym), None)
    if it is None: it = {"month": ym, "pdf": name}; D["issues"].append(it)
    it.update({"pdf": name, "bytes": len(data), "url": L.cdn_url(sha, name)})
    L.save(D); n = L.write_redirects(D)
    subprocess.run([sys.executable, f"{R}/scripts/build_link_archive.py"], check=True)
    print(f"LINK SAVE: NEW issue {mm.group(1)} {mm.group(2)} ({len(data)/1e6:.1f} MB) -> store commit {sha[:7]}, {rel}; "
          f"data/link-issues.json + vercel.json ({n} redirects) + palm-hill-link.html updated - put them in this week's batched PR; "
          f"copy builder/link-new/{name} to Omen D:\\PHNEWS\\link\\")
    return 0
if __name__ == "__main__": sys.exit(main())
