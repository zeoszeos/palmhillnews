#!/usr/bin/env python3
"""R149 (Steven, Nov 28 2026 11:01 AM ET): no review or test copy goes out until every
<img> in the SEND loads from the live site as an image.

Every <img src> is requested against the URL in the HTML (absolute production URLs).
A source must return HTTP 200 with an image Content-Type. A 404 or a non-image
response fails the check (SystemExit). Preview-deployment Vercel URLs also fail:
the SEND must use the live site (https://palmhillnews.vercel.app/...), never a
preview deployment, because a send would teach Gmail's image proxy a failed load
of a new filename.

This is a pre-send gate, like R123. It is not a mid-build run_checks network
fetch, because a new asset (for example a versioned crop) is not live until the
PR merges.

Usage:
  python3 scripts/check_send_live_images.py --issue 2026-11-29
  python3 scripts/check_send_live_images.py --file path/to/PHNEWS-...-SEND.html
Exit 0 = every image is live (safe to send). SystemExit / exit 1 = do not send.
"""
import argparse, html, os, re, sys, urllib.parse, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE_HOSTS = {"palmhillnews.vercel.app", "www.palmhillnews.vercel.app"}
UA = "Mozilla/5.0 (PHNEWS R149 live image check)"

# Import the detector so tests and run_checks share one implementation.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style_rules as sr


def extract_img_srcs(text):
    return sr.r149_img_srcs(text)


def is_preview_deployment(url):
    return sr.r149_is_preview_deployment(url)


def fetch_image(url, timeout=25):
    """Return (status, content_type). status is 0 on a network error."""
    # GET is required: we need the Content-Type, and some hosts refuse HEAD.
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return r.status, ctype
    except urllib.error.HTTPError as e:
        ctype = (e.headers.get("Content-Type") if e.headers else None) or ""
        ctype = ctype.split(";")[0].strip().lower()
        return e.code, ctype
    except Exception:
        return 0, ""


def check(srcs, fetch=None):
    """Return (results, problems). results maps src -> (status, content_type)."""
    fetch = fetch or fetch_image
    with ThreadPoolExecutor(max_workers=8) as ex:
        got = dict(zip(srcs, ex.map(fetch, srcs)))
    # retry anything that is not a live image once (transient errors)
    for u, (status, ctype) in list(got.items()):
        if status != 200 or not (ctype or "").startswith("image/"):
            if not sr.r149_is_preview_deployment(u):
                got[u] = fetch(u)
    problems = sr.send_live_image_problems_from_results(srcs, got)
    return got, problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue")
    ap.add_argument("--file")
    a = ap.parse_args(argv)
    if not (a.issue or a.file):
        ap.error("pass --issue YYYY-MM-DD or --file")
    fp = a.file or os.path.join(ROOT, "pages", "previews", a.issue, f"PHNEWS-{a.issue}-SEND.html")
    html_text = open(fp, encoding="utf-8", errors="ignore").read()
    srcs = extract_img_srcs(html_text)
    # Structural preview-URL failures do not need a fetch.
    preview_hits = [s for s in srcs if is_preview_deployment(s)]
    results, problems = check(srcs)
    print(f"R149 live image check: {fp}")
    ok = sum(1 for s in srcs if s not in {p.split(": ", 1)[-1] for p in problems} and s not in preview_hits)
    # Count OK from results
    ok = 0
    for s in srcs:
        status, ctype = results.get(s, (0, ""))
        if s not in preview_hits and status == 200 and (ctype or "").startswith("image/"):
            ok += 1
    print(f"  {len(srcs)} unique <img> sources, {ok} live images, {len(problems)} broken")
    for p in problems:
        print(f"  FAIL {p}")
    if problems:
        raise SystemExit(
            "R149 FAIL: do not send a review or test copy until every SEND image "
            "is live on the site with an image content-type.\n" + "\n".join(problems)
        )
    print("R149 PASS: every <img> in the SEND returns HTTP 200 with an image content-type from the live site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
