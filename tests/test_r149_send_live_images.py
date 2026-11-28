"""R149: every SEND <img> must be a live-site image before a review or test copy goes out."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_rules as sr
import check_send_live_images as c

LIVE = "https://palmhillnews.vercel.app/assets/images/phnews/2026-11/smiling-ladies-luncheon-main-november-2026-v2.jpg"
OLD = "https://palmhillnews.vercel.app/assets/images/phnews/2026-11/smiling-ladies-luncheon-main-november-2026.jpg"
PREVIEW = "https://palmhillnews-git-nov29-late-coffee-zeoszeos.vercel.app/assets/images/phnews/2026-11/smiling-ladies-luncheon-main-november-2026-v2.jpg"
ICON = "https://palmhillnews.vercel.app/assets/images/phnews/v4/speaker-read-aloud-green-gold-48-v1.png"

HTML = f'''<img src="{LIVE}" alt="crop"><img src="{ICON}" alt="">'''


def test_live_images_pass():
    def fetch(url):
        return (200, "image/jpeg") if url.endswith(".jpg") else (200, "image/png")
    assert sr.send_live_image_problems(HTML, fetch) == []


def test_404_fails():
    def fetch(url):
        if "v2.jpg" in url:
            return (404, "text/html")
        return (200, "image/png")
    hits = sr.send_live_image_problems(HTML, fetch)
    assert hits and "v2.jpg" in hits[0] and "404" in hits[0]


def test_non_image_content_type_fails():
    def fetch(url):
        return (200, "text/html")
    hits = sr.send_live_image_problems(f'<img src="{LIVE}">', fetch)
    assert hits and "content-type" in hits[0] and "text/html" in hits[0]


def test_preview_deployment_url_fails():
    html = f'<img src="{PREVIEW}" alt="crop">'
    assert sr.r149_is_preview_deployment(PREVIEW)
    assert not sr.r149_is_preview_deployment(LIVE)
    hits = sr.r149_preview_image_url_problems(html, label="SEND")
    assert hits and "preview-deployment" in hits[0]
    # even a 200 image fetch cannot clear a preview URL
    hits2 = sr.send_live_image_problems(html, fetch=lambda u: (200, "image/jpeg"))
    assert hits2 and "preview-deployment" in hits2[0]


def test_script_systemexit_on_failure(tmp_path):
    send = tmp_path / "PHNEWS-2026-11-29-SEND.html"
    send.write_text(f'<img src="{LIVE}">', encoding="utf-8")
    # Patch fetch used by check()
    orig = c.fetch_image
    c.fetch_image = lambda url, timeout=25: (404, "text/html")
    try:
        raised = None
        try:
            c.main(["--file", str(send)])
        except SystemExit as e:
            raised = e
        assert raised is not None
        msg = str(raised)
        assert "R149 FAIL" in msg and "do not send" in msg and "v2.jpg" in msg
    finally:
        c.fetch_image = orig


def test_old_and_v2_are_distinct_urls():
    assert LIVE != OLD
    assert LIVE.endswith("-v2.jpg")


if __name__ == "__main__":
    import tempfile, os
    class Tmp:
        def __init__(self, p):
            self._p = Path(p)
        def __truediv__(self, n):
            return self._p / n
    for n, f in list(globals().items()):
        if n.startswith("test_") and callable(f):
            if n == "test_script_systemexit_on_failure":
                with tempfile.TemporaryDirectory() as d:
                    f(Tmp(d))
            else:
                f()
            print("PASS", n)
