#!/usr/bin/env python3
"""STYLE-RULES L27/L29 (Steven, Oct 17 2026 11:51 PM): every Webmaster Source credit links a copy of the source email.
render(subject, sent, blocks, source) -> the community-notice source-copy page in the same shell as
pages/2026-10-08-info-from-linda-notice.html (title only -- no date line under it, R133 --, Subject/From/Sent row with the sent date in smaller print, the email body copied as sent, Source line);
write(repo, name, ...) writes pages/<name> and adds the standard Listen block (scripts/notice_listen.py).
blocks: ("h", text) = a heading line of the email (underlined/centred), ("p", text) = a paragraph, ("ul", [items]) = a bullet list, ("img", (src, alt)) = an image as sent.
Text is the source wording; only whitespace (blank lines, &nbsp; runs, zero-width spaces) and the per-recipient unsubscribe
footer are left out. Plain text in, escaped here."""
import sys
from html import escape
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import notice_listen
import re as _re

# STYLE-RULES R133 (Steven, Nov 14 2026 10:40 PM ET, voice): a notice page's top line under the title must not show a
# date that could be read as the event date. The email's sent date appears only in the Subject/From/Sent box, in
# smaller print than the body (16px #555, the RD1/RD10 meta size; body text is 18px).
SENT_DATE_CLASS = "ph-sent-date"
SENT_DATE_STYLE = "font-size:16px;line-height:1.5;color:#555555"
SENT_LABEL = "<strong>Sent:</strong> "
_SENT_RE = _re.compile(r'<strong>Sent:</strong> (?!<span class="ph-sent-date")([^<]+)')


def sent_date_html(sent_escaped):
    return f'<span class="{SENT_DATE_CLASS}" style="{SENT_DATE_STYLE}">{sent_escaped}</span>'


def fix_sent_date(html):
    """R133: drop a <p class="ph-meta"> line that only repeats the email's Sent date, and put the Sent date in smaller print.
    A ph-meta line with other text (e.g. a meeting's own date, time and place) is kept."""
    if SENT_LABEL not in html:
        return html
    m = _SENT_RE.search(html)
    if m:
        html = html[:m.start()] + SENT_LABEL + sent_date_html(m.group(1)) + html[m.end():]
    sm = _re.search(r'<strong>Sent:</strong> <span class="ph-sent-date"[^>]*>([^<]+)</span>', html)
    if sm:
        sent = sm.group(1).strip()
        html = _re.sub(r'\n?<p class="ph-meta">\s*' + _re.escape(sent) + r'\s*</p>', "", html)
    return html


def sent_date_problems(html):
    """R133 guard: [] when the page has no Sent box, or when no date line under the title repeats the Sent date and
    the Sent date carries the smaller style."""
    if SENT_LABEL not in html:
        return []
    hits = []
    sm = _re.search(r'<strong>Sent:</strong> (<span class="ph-sent-date" style="([^"]*)">)?([^<]+)', html)
    if not sm:
        return ["Sent line not found"]
    sent = sm.group(3).strip()
    if not sm.group(1):
        hits.append("the Sent date is not in the smaller ph-sent-date style")
    elif sm.group(2) != SENT_DATE_STYLE:
        hits.append(f"the Sent date style is {sm.group(2)!r}, expected {SENT_DATE_STYLE!r}")
    if _re.search(r'<p class="ph-meta">\s*' + _re.escape(sent) + r'\s*</p>', html):
        hits.append(f"a date line under the title repeats the Sent date ({sent}) and can be read as the event date")
    return hits


def notice_pages_with_sent(repo):
    """Every live page with a Subject/From/Sent box (pages/*.html only: never pages/archive/**, previews or SEND files)."""
    return sorted(f for f in (Path(repo) / "pages").glob("*.html") if SENT_LABEL in f.read_text(encoding="utf-8"))


def fix_all(repo, skip=()):
    """R133: apply fix_sent_date to every notice page with a Sent box; returns the pages that changed."""
    changed = []
    for f in notice_pages_with_sent(repo):
        if f.relative_to(repo).as_posix() in skip:
            continue
        t = f.read_text(encoding="utf-8"); n = fix_sent_date(t)
        if n != t:
            f.write_text(n, encoding="utf-8"); changed.append(f.name)
    return changed

def _blk(kind, v):
    if kind == "h":
        return f'<div class="ph-row-title" style="line-height:1.6">{escape(v)}</div>'  # RD2: a wrapped heading line reads as body text (>= 1.55)
    if kind == "p":
        return f'<div class="ph-detail">{escape(v)}</div>'
    if kind == "ul":
        return ('<div class="ph-detail"><ul style="margin:0;padding-left:1.3em">'
                + "".join(f"<li>{escape(i)}</li>" for i in v) + "</ul></div>")
    if kind == "img":  # Steven Oct 23 6:38 PM: image-only Webmaster email (flyer) -> the flyer as sent, from the club site
        src, alt = v
        return f'<div class="ph-detail"><img src="{escape(src)}" alt="{escape(alt)}" style="max-width:100%;height:auto;display:block"></div>'
    raise ValueError(kind)

def render(subject, sent, blocks, source="Source: Palm Hill webmaster notice, copied as sent. Only the per-recipient unsubscribe link was left out.",
           title=None, sender="Palm Hill Webmaster", source_href=None):
    title = title or " ".join(subject.split())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — Palm Hill Country Club</title>
<link rel="stylesheet" href="/pages/assets/ph-newsletter.css">
<link rel="stylesheet" href="/pages/assets/ph-read.css" id="ph-read-css">
</head>
<body class="ph-rd ph-rd-shell">
<!-- Shell: /pages/assets/ph-newsletter-shell.html — one column, no min-width table, no pill links. -->
<!-- ph-archive-nav:none (community notice source copy: title only, no masthead/bar/footer; Steven Oct 10) -->
<!-- Generated by scripts/notice_page.py (L27/L29) from the builder's source blocks. Edit the builder, not this file. -->
<div class="ph-page">
<main class="ph-body">
<h1 class="ph-section">{escape(title)}</h1>
<div class="ph-row ph-alt"><div class="ph-detail"><strong>Subject:</strong> {escape(subject)}<br><strong>From:</strong> {escape(sender)}<br><strong>Sent:</strong> {sent_date_html(escape(sent))}</div></div>
<div class="ph-row">{"".join(_blk(k, v) for k, v in blocks)}</div>
<p class="ph-source">{(f'<a href="{escape(source_href)}">{escape(source)}</a>') if source_href else escape(source)}</p>
</main>
</div>
</body>
</html>
"""

def write(repo, name, subject, sent, blocks, **kw):
    f = Path(repo) / "pages" / name
    f.write_text(render(subject, sent, blocks, **kw), encoding="utf-8")
    notice_listen.add(repo, name)
    return f
