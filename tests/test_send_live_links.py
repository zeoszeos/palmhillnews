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


def test_network_error_label():
    """A palmhillnews link that did not answer is NETWORK ERROR, not NOT LIVE YET or MISSING."""
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "pages"))
        open(os.path.join(root, "pages", "live.html"), "w").write("x")
        ev, cause = c.classify("https://palmhillnews.vercel.app/pages/live.html", 0, root=root)
        assert ev == "FAIL" and cause.startswith("NETWORK ERROR"), (ev, cause)
        ev2, cause2 = c.classify("https://palmhillnews.vercel.app/pages/live.html", 404, root=root)
        assert ev2 == "FAIL" and cause2.startswith("NOT LIVE YET"), (ev2, cause2)
        ev3, cause3 = c.classify("https://palmhillnews.vercel.app/pages/typo.html", 404, root=root)
        assert ev3 == "FAIL" and cause3.startswith("MISSING"), (ev3, cause3)


def test_all_outside_links_failed_is_failure():
    """If every outside link times out, the check fails (links were not verified)."""
    html = ('<a href="https://example.org/a">a</a>'
            '<a href="https://example.org/b">b</a>')
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d) / "SEND.html"
        fp.write_text(html)
        # Patch check() (its default fetch= is bound at import time). Individual
        # outside timeouts stay warnings; main() must still fail when ALL are unanswered.
        def fake_check(urls, fetch=None, root=None):
            codes = {u: 0 for u in urls}
            probs = [("WARN", "outside link did not answer (network/timeout); check by hand", 0, u) for u in urls]
            return codes, probs
        orig = c.check
        c.check = fake_check
        try:
            rc = c.main(["--file", str(fp)])
        finally:
            c.check = orig
        assert rc == 1

if __name__ == "__main__":
    test_classify(); test_network_error_label(); test_all_outside_links_failed_is_failure(); print("PASS test_send_live_links")
