#!/usr/bin/env python3
"""Committee Chair Report page generator (Steven, Oct 17 2026). Writes pages/<date>-<slug>-report.html in the
Chair Report card layout (same shell as 2026-09-08-golf-advisory-committee-report.html). The full text is the chair's
own wording, block by block (no rewriting). build_archive.js then adds the archive bar, the date line with the speaker
Listen (dateline_listen) and the clean listen-* page; readability.apply() sets RD1-RD13.
blocks: list of ("p", text) | ("h2", text) | ("ul", [items]); text is plain (escaped here)."""
import os, sys
from html import escape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import readability as _rd
CSS = """<style>
main { width:min(780px,100%); }
.page-kicker { color:#f7df82; font-size:.78rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
.header-meta { margin:8px 0 0; color:#eef5ec; }
.content-card { margin:0 0 18px; padding:clamp(18px,4vw,28px); background:#fff; border:1px solid #d7d1bd; border-radius:14px; box-shadow:0 3px 12px #0002; font-size:1rem; line-height:1.65; overflow-wrap:anywhere; }
.content-card p:last-child { margin-bottom:0; }
.content-card h2 { margin:18px 0 6px; font-size:1.1rem; color:#2d5016; }
.content-card h2:first-child { margin-top:0; }
.content-card ul { margin:0 0 14px; padding-left:22px; }
.content-card li { margin-bottom:6px; }
.content-card img { display:block; width:100%; height:auto; margin:0 0 14px; border:1px solid #ddd8c8; }
</style>"""
def render(title, blocks, source, name):
    body = []
    for kind, v in blocks:
        if kind == "ul": body.append("<ul>" + "".join(f"<li>{escape(x, quote=False)}</li>" for x in v) + "</ul>")
        else: body.append(f"<{kind}>{escape(v, quote=False)}</{kind}>")
    body.append(f"<p>{escape(source, quote=False)}</p>")
    html = (f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{escape(title)} — Palm Hill</title>\n<link rel="stylesheet" href="/pages/shared/ph-info.css">\n{CSS}\n</head><body>\n'
            f'<header><div class="page-kicker">Palm Hill Country Club</div><h1>{escape(title)}</h1></header>\n'
            f'<main><article class="content-card">{"".join(body)}</article></main>\n</body></html>\n')
    return _rd.apply(html, name)[0]   # STYLE-RULES RD1-RD13 (card template)
