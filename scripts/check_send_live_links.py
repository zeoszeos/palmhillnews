#!/usr/bin/env python3
"""R123 (Steven, Nov 13 2026): no review copy or blast goes out with a link that is broken on the live site.

Every http(s) link in the SEND file is requested against production, following redirects.
A palmhillnews.vercel.app link that does not return 200 fails the check. Each failure is
labeled with its cause:

  NOT LIVE YET   the page exists in this checkout (draft branch) but not on the live site;
                 the draft must be merged to main (live pages only) before a review copy is sent
  MISSING        the page is in neither this checkout nor the live site (bad slug or page never built)

Outside links (club site, Drive, Zoom, PDFs) are retried once; a 404/410 fails, while a
timeout or other network error is printed as a warning only.

Usage:
  python3 scripts/check_send_live_links.py --issue 2026-11-15
  python3 scripts/check_send_live_links.py --file path/to/PHNEWS-...-SEND.html
Exit 0 = every link is good on production (safe to send the review copy). Exit 1 = do not send.
"""
import argparse, html, os, re, sys, urllib.parse, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://palmhillnews.vercel.app"
UA = "Mozilla/5.0 (PHNEWS R123 link check)"


def extract_urls(text):
    urls = re.findall(r'(?:href|src)\s*=\s*"(https?://[^"]+)"', text, re.I)
    urls += re.findall(r"(?:href|src)\s*=\s*'(https?://[^']+)'", text, re.I)
    return sorted({html.unescape(u).strip() for u in urls})


def fetch_status(url, timeout=25):
    """Return the final HTTP status after redirects, or 0 on a network error."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue  # some hosts refuse HEAD; try GET
            return e.code
        except Exception:
            if method == "HEAD":
                continue
            return 0
    return 0


def local_path(url):
    p = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
    if p in ("", "/"):
        return "index.html"
    return p.lstrip("/")


def in_checkout(url, root=ROOT):
    rel = local_path(url)
    cands = [rel, "public/" + rel, rel.rstrip("/") + "/index.html"]
    return any(os.path.isfile(os.path.join(root, c)) for c in cands)


def classify(url, status, root=ROOT):
    """Return None when OK, else (severity, cause). severity is 'FAIL' or 'WARN'."""
    if status == 200:
        return None
    if url.startswith(SITE):
        if in_checkout(url, root):
            return ("FAIL", "NOT LIVE YET (page is on the draft branch, not on main/live)")
        return ("FAIL", "MISSING (page is not in the repo or on the live site)")
    if status in (404, 410):
        return ("FAIL", f"OUTSIDE LINK BROKEN ({status})")
    if status == 0:
        return ("WARN", "outside link did not answer (network/timeout); check by hand")
    return ("WARN", f"outside link returned {status}; check by hand")


def check(urls, fetch=fetch_status, root=ROOT):
    with ThreadPoolExecutor(max_workers=8) as ex:
        codes = dict(zip(urls, ex.map(fetch, urls)))
    # retry anything not 200 once (transient errors)
    for u in [u for u, c in codes.items() if c != 200]:
        codes[u] = fetch(u)
    out = []
    for u in urls:
        r = classify(u, codes[u], root)
        if r:
            out.append((r[0], r[1], codes[u], u))
    return codes, out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue")
    ap.add_argument("--file")
    a = ap.parse_args(argv)
    if not (a.issue or a.file):
        ap.error("pass --issue YYYY-MM-DD or --file")
    fp = a.file or os.path.join(ROOT, "pages", "previews", a.issue, f"PHNEWS-{a.issue}-SEND.html")
    urls = extract_urls(open(fp, encoding="utf-8", errors="ignore").read())
    codes, problems = check(urls)
    fails = [p for p in problems if p[0] == "FAIL"]
    warns = [p for p in problems if p[0] == "WARN"]
    print(f"R123 live link check: {fp}")
    print(f"  {len(urls)} unique links, {sum(1 for c in codes.values() if c == 200)} OK, "
          f"{len(fails)} broken, {len(warns)} warnings")
    for sev, cause, code, u in sorted(problems, key=lambda p: (p[0], p[1], p[3])):
        print(f"  {sev} {code or 'ERR'} {cause}: {u}")
    if fails:
        print("R123 FAIL: do not send a review copy or the blast until every link above is live.")
        return 1
    print("R123 PASS: every link in the SEND opens on the live site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
