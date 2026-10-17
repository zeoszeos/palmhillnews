"""Vercel event page (Oct 18 event-page format: green title, Listen, date card, full calendar listing text, Source: Calendar).
STYLE-RULES R21: every issue event whose calendar listing has text beyond its summary gets one of these, linked with More →."""
import re
from html import escape
from pathlib import Path
TPL = Path(__file__).resolve().parent.parent / "pages/2026-10-24-mount-dora-trip.html"
def render(title, dateline, paragraphs):
    s = TPL.read_text(encoding="utf-8")
    s = s.replace("<title>Mount Dora Trip — ", f"<title>{escape(title)} — ", 1)
    s = s.replace('style="margin:0">Mount Dora Trip</h1>', f'style="margin:0">{escape(title)}</h1>', 1)
    body = f"<p><b>{escape(dateline)}</b></p>" + "".join(f"<p>{escape(p)}</p>" for p in paragraphs)
    s2 = re.sub(r'<div class="content-card">.*?</div>', lambda m: f'<div class="content-card">{body}</div>', s, count=1, flags=re.S)
    assert s2 != s and escape(title) in s2
    import sys as _s; _s.path.insert(0, str(Path(__file__).resolve().parent)); import readability as _rd  # STYLE-RULES RD1-RD13 (layout only; wording lock)
    return _rd.apply(s2, '')[0]
