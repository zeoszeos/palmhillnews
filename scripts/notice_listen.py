#!/usr/bin/env python3
"""STYLE-RULES R42 (Steven, Oct 17 2026 10:29 PM): a notice that uses its existing source page (source_sections.use_existing_page)
gets the standard Listen block on that page, same URL: the speaker + 'Listen' button on the title line and the shared page-listen
script (copied from pages/2026-10-09-weekly-manager-update.html, the block the generated notice pages use), reading the title and
each section of the email (the Subject/From/Sent header row and the Source line are skipped). ?listen=1 starts reading.
Idempotent. Usage: python3 scripts/notice_listen.py REPO PAGE.html [...]"""
import re, sys
from pathlib import Path
MARK = "<!-- ph-page-listen:start -->"
def add(repo, name):
    repo = Path(repo); f = repo / "pages" / name; t = f.read_text(encoding="utf-8")
    if MARK in t: return False
    w = (repo / "pages/2026-10-09-weekly-manager-update.html").read_text(encoding="utf-8")
    script = w[w.find(MARK):w.find("<!-- ph-page-listen:end -->") + len("<!-- ph-page-listen:end -->")]
    btn = re.findall(r'<a class="ph-listen".*?</a>', w, re.S)[0]
    # read the email copy's rows (shell template) instead of .content-card; skip the Subject/From/Sent header row
    old = "Array.from(document.querySelectorAll('main .content-card'))"
    assert old in script, "page-listen script changed; update notice_listen.py"
    script = script.replace(old, "Array.from(document.querySelectorAll('main .content-card, main .ph-row')).filter((el) => !/^\\s*Subject:/.test(el.innerText))")
    h = re.search(r'<h1 class="ph-section">(.*?)</h1>', t, re.S); assert h, f"{name}: no h1"
    hd = (f'<div class="hd" style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
          f'<h1 class="ph-section" style="margin:0">{h.group(1)}</h1>{btn}</div>')
    t = t.replace(h.group(0), hd, 1).replace("</body>", script + "\n</body>", 1)
    f.write_text(t, encoding="utf-8"); return True
if __name__ == "__main__":
    for n in sys.argv[2:]: print(("added Listen: " if add(sys.argv[1], n) else "unchanged: ") + n)
