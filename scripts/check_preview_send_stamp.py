"""STYLE-RULES R70 (Steven, Oct 24 2026 9:56 PM): the live preview page and the SEND (emailed proof) copy carry the SAME
"Calendar check" footer line and the same masthead time. Root cause it guards: the repo preview
(pages/previews/<issue>/PHNEWS-<issue>-preview.html) was a hand-synced copy, left at an earlier build's stamp after the
SEND was rebuilt. The builder now syncs it (sync()), and check() fails on any mismatch.
Usage: python scripts/check_preview_send_stamp.py --issue 2026-10-25 [--root DIR] [--repo DIR]"""
import argparse, re, shutil, sys
from pathlib import Path
CAL = re.compile(r'<p class="ph-cal-check"[^>]*>([^<]*)</p>')
MAST = re.compile(r'white-space:nowrap;">(\d{1,2}:\d{2} [AP]M)</span>')

def stamps(html):
    c, m = CAL.findall(html), MAST.findall(html)
    assert len(c) == 1, f"R70: expected 1 Calendar check line, found {len(c)}"
    return c[0], (m[0] if m else None)

def sync(local_preview, repo, issue):
    dst = Path(repo) / f"pages/previews/{issue}/PHNEWS-{issue}-preview.html"
    shutil.copyfile(local_preview, dst); return dst

def check(issue, root, repo):
    pv = Path(repo) / f"pages/previews/{issue}/PHNEWS-{issue}-preview.html"; sd = Path(root) / f"PHNEWS-{issue}-SEND.html"
    pt = pv.read_text(encoding="utf-8"); p = stamps(pt); fails = []
    # R94 (Steven Oct 30 2026 4:02 PM): from v2_from the live preview carries exactly one in-place Listen block and no other
    # script; the SEND/email copy carries none. Comparisons with SEND ignore only that block (page_listen.strip_inplace).
    sys.path.insert(0, str(Path(__file__).resolve().parent)); import page_listen as pl
    if pl.v2_for(issue):
        if pt.count("<!-- ph-inplace-listen:start -->") != 1: fails.append("R94: live preview lacks the in-place Listen block")
        if "<script" in pl.strip_inplace(pt).lower(): fails.append("R94: live preview has a script other than the in-place Listen block")
    if not sd.exists(): return fails, p
    st = sd.read_text(encoding="utf-8"); s = stamps(st)
    if "<script" in st.lower(): fails.append("R94/R76c: SEND copy contains <script>")
    if p[0] != s[0]: fails.append(f"R70: preview footer '{p[0]}' != SEND footer '{s[0]}'")
    if p[1] != s[1]: fails.append(f"R70: preview masthead time '{p[1]}' != SEND masthead time '{s[1]}'")
    return fails, p

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--issue", required=True)
    a.add_argument("--root", default="/workspace/phnews-consolidation/oct18"); a.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    a = a.parse_args(); f, p = check(a.issue, a.root, a.repo)
    print("\n".join(f) if f else f"R70 PASS: preview = SEND ({p[0]}; masthead {p[1]})"); sys.exit(1 if f else 0)
