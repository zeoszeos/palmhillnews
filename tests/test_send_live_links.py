#!/usr/bin/env python3
"""R123 (Steven, Nov 13 2026): every SEND link must open on the live site before a review copy goes out."""
import os, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_send_live_links as c

SEND = ('<a href="https://palmhillnews.vercel.app/pages/live.html">a</a>'
        '<a href="https://palmhillnews.vercel.app/pages/draft-only.html?listen=1">b</a>'
        '<a href="https://palmhillnews.vercel.app/pages/typo.html">c</a>'
        '<a href="https://example.org/gone.pdf">d</a>'
        '<a href="https://example.org/slow">e</a>'
        '<a href="https://palmhillnews.vercel.app/pages/live.html">dup</a>')
CODES = {"https://palmhillnews.vercel.app/pages/live.html": 200,
         "https://palmhillnews.vercel.app/pages/draft-only.html?listen=1": 404,
         "https://palmhillnews.vercel.app/pages/typo.html": 404,
         "https://example.org/gone.pdf": 404,
         "https://example.org/slow": 0}

def test_classify():
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "pages"))
        for f in ("live.html", "draft-only.html"):
            open(os.path.join(root, "pages", f), "w").write("x")
        urls = c.extract_urls(SEND)
        assert len(urls) == 5, urls
        _, probs = c.check(urls, fetch=lambda u: CODES[u], root=root)
        got = {u: (sev, cause.split(" (")[0]) for sev, cause, _, u in probs}
        assert got["https://palmhillnews.vercel.app/pages/draft-only.html?listen=1"] == ("FAIL", "NOT LIVE YET")
        assert got["https://palmhillnews.vercel.app/pages/typo.html"] == ("FAIL", "MISSING")
        assert got["https://example.org/gone.pdf"][0] == "FAIL"
        assert got["https://example.org/slow"][0] == "WARN"
        assert "https://palmhillnews.vercel.app/pages/live.html" not in got

if __name__ == "__main__":
    test_classify(); print("PASS test_send_live_links")
