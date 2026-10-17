#!/usr/bin/env python3
"""Palm Hill Link PDF hosting (STYLE-RULES.md R15 + R29, Steven Oct 17 2026).

Link PDFs (~10 MB each) are NOT part of the Vercel deployment (Hobby Deployment Storage is 10 GB and every
deployment stored a full copy). Each PDF lives:
  1. on branch `link-pdf-store` (storage only, never merged, never deployed), served with Content-Type
     application/pdf by https://cdn.jsdelivr.net/gh/zeoszeos/palmhillnews@<commit>/<file> (pinned, immutable);
  2. as an asset of GitHub release `link-pdfs` (permanent copy + catch-all fallback);
  3. on the Omen at D:\\PHNEWS\\link\\.
https://palmhillnews.vercel.app/pages/archive/link/<file> keeps working through vercel.json redirects.

`python3 scripts/link_store.py` (re)writes the vercel.json redirects from data/link-issues.json. Idempotent."""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "zeoszeos/palmhillnews"
STORE_BRANCH = "link-pdf-store"
RELEASE_TAG = "link-pdfs"
DATA = f"{R}/data/link-issues.json"
VJ = f"{R}/vercel.json"
LINK_PATH = "/pages/archive/link"

def cdn_url(sha, name): return f"https://cdn.jsdelivr.net/gh/{REPO}@{sha}/{name}"
def release_url(name): return f"https://github.com/{REPO}/releases/download/{RELEASE_TAG}/{name}"

def load(): return json.load(open(DATA, encoding="utf-8"))

def save(D):
    """Same layout as before: header keys, then one issue per line, newest first."""
    D["issues"].sort(key=lambda i: i["month"], reverse=True)
    head = [f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in D.items() if k != "issues"]
    rows = [f"  {json.dumps(i, ensure_ascii=False)}" for i in D["issues"]]
    txt = "{" + ",\n".join(head).lstrip() + ",\n \"issues\": [\n" + ",\n".join(rows) + "\n ]}\n"
    json.loads(txt); open(DATA, "w", encoding="utf-8").write(txt)

def write_redirects(D=None):
    D = D or load()
    v = json.load(open(VJ, encoding="utf-8"))
    keep = [r for r in v.get("redirects", []) if not r["source"].startswith(LINK_PATH + "/")]
    link = [{"source": f"{LINK_PATH}/{i['pdf']}", "destination": i["url"], "permanent": False} for i in D["issues"]]
    link.append({"source": f"{LINK_PATH}/:file", "destination": release_url(":file"), "permanent": False})
    v["redirects"] = keep + link
    open(VJ, "w", encoding="utf-8").write(json.dumps(v, indent=2, ensure_ascii=False) + "\n")
    return len(link)

if __name__ == "__main__":
    print(f"vercel.json: {write_redirects()} Link redirects written"); sys.exit(0)
