#!/usr/bin/env python3
"""STYLE-RULES R42 (Steven, Oct 17 2026 10:29 PM): a notice that uses its existing source page (source_sections.use_existing_page)
gets the standard Listen block on that page, same URL: the speaker + 'Listen' button on the title line and the shared page-listen
script (copied from pages/2026-10-09-weekly-manager-update.html, the block the generated notice pages use), reading the title and
each section of the email (the Subject/From/Sent header row and the Source line are skipped). ?listen=1 starts reading.
Idempotent. Usage: python3 scripts/notice_listen.py REPO PAGE.html [...]"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import page_listen as _pl
def add(repo, name):
    repo = Path(repo); f = repo / "pages" / name; t = f.read_text(encoding="utf-8")
    n = _pl.add(t)  # R49b (Oct 18 2:05 AM): one placement/markup source -- scripts/page_listen.py add() (title line on shell pages)
    if n != t: f.write_text(n, encoding="utf-8"); return True
    return False
if __name__ == "__main__":
    for n in sys.argv[2:]: print(("added Listen: " if add(sys.argv[1], n) else "unchanged: ") + n)
    import check_listen_coverage as _lc; _lc.require([Path(sys.argv[1]) / "pages" / n for n in sys.argv[2:]])  # R49 required step
