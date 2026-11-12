"""STYLE-RULES R70 (Steven, Oct 24 2026 9:56 PM): the live preview page and the SEND (emailed proof) copy carry the SAME
"Calendar check" footer line and the same masthead time. Root cause it guards: the repo preview
(pages/previews/<issue>/PHNEWS-<issue>-preview.html) was a hand-synced copy, left at an earlier build's stamp after the
SEND was rebuilt. The builder now syncs it (sync()), and check() fails on any mismatch.
R115 (Steven Nov 7 2026): that sync used to copy the R96 local review file unchanged. The review file's page links are
sibling filenames so they open from disk. The live preview sits at pages/previews/<issue>/, so those hrefs 404.
From 2026-11-01, sync() writes absolute https://palmhillnews.vercel.app/pages/... links (same as SEND) and check()
fails if any same-folder or archive/ relative .html href remains. Oct 25 and earlier stay a byte copy.
R115b (Steven Nov 12 2026): the November 1 live preview still had those relative hrefs after R115 landed, because
check() only looked at the issue passed to it (November 8). check() now scans every dated live preview from
2026-11-01 on, and fails if a relative page/archive href remains or an absolute /pages/ target is missing on disk.
Usage: python scripts/check_preview_send_stamp.py --issue 2026-10-25 [--root DIR] [--repo DIR]"""
import argparse, re, shutil, sys
from pathlib import Path
CAL = re.compile(r'<p class="ph-cal-check"[^>]*>([^<]*)</p>')
MAST = re.compile(r'white-space:nowrap;">(\d{1,2}:\d{2} [AP]M)</span>')
# R115: issues that publish the nested pages/previews/<issue>/ copy. Oct 25 and earlier stay a byte copy (acceptance_oct25).
ABSOLUTE_FROM = "2026-11-01"
PAGE = "https://palmhillnews.vercel.app/pages/"
_REL_PAGE = re.compile(r'href="(?!https?:|//|mailto:|tel:|#)([^"]*?\.(?:html|pdf)[^"]*)"')
_SCRIPT = re.compile(r"(<script\b[^>]*>.*?</script>)", re.I | re.S)

def _outside_script(html):
    return [p for p in _SCRIPT.split(html) if p[:7].lower() != "<script"]

def relative_page_hrefs(html):
    """R115: .html and .pdf hrefs with no scheme (sibling names, archive/..., other relative paths). They 404 from
    pages/previews/<issue>/. tel:, mailto:, #, and absolute http(s) are not included. Script text is ignored."""
    return [h for part in _outside_script(html) for h in _REL_PAGE.findall(part)]

def absolutize_live_preview(html):
    """R115: restore R96 sibling and archive/ page hrefs to PAGE + path. Idempotent. Does not add or remove script.
    Leaves tel:, mailto:, fragments, external https, and already-absolute links unchanged. Local review files are
    not passed here; sync() applies this only to the repo preview, and only when issue >= ABSOLUTE_FROM."""
    def repl_region(region):
        def repl(m):
            url = m.group(1)
            if url.startswith("/pages/"): url = url[len("/pages/"):]
            elif url.startswith("/"): return m.group(0)
            return 'href="' + PAGE + url + '"'
        return _REL_PAGE.sub(repl, region)
    return "".join(p if p[:7].lower() == "<script" else repl_region(p) for p in _SCRIPT.split(html))

def live_preview_files(repo):
    """Dated pages/previews/<YYYY-MM-DD>/PHNEWS-<YYYY-MM-DD>-preview.html files. Skips folders like listen-player."""
    root = Path(repo) / "pages/previews"
    if not root.is_dir():
        return []
    found = []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d.name):
            continue
        prev = d / f"PHNEWS-{d.name}-preview.html"
        if prev.is_file():
            found.append((d.name, prev))
    return found

def _rel_to_repo(path, repo):
    try:
        return Path(path).resolve().relative_to(Path(repo).resolve()).as_posix()
    except ValueError:
        return str(path)

def missing_page_targets(html, repo):
    """Absolute PAGE hrefs whose path (query/fragment stripped) is not a file under repo/pages/."""
    missing, seen = [], set()
    for part in _outside_script(html):
        for url in re.findall(r'href="' + re.escape(PAGE) + r'([^"]+)"', part):
            path = url.split("?", 1)[0].split("#", 1)[0]
            if path in seen:
                continue
            seen.add(path)
            if not (Path(repo) / "pages" / path).is_file():
                missing.append(url)
    return missing

def check_live_preview_hrefs(repo):
    """R115/R115b: every live preview from ABSOLUTE_FROM on has only absolute page/archive hrefs,
    and each of those hrefs exists under pages/. Previews dated earlier are left as byte copies."""
    fails = []
    repo = Path(repo)
    for issue, path in live_preview_files(repo):
        if issue < ABSOLUTE_FROM:
            continue
        html = path.read_text(encoding="utf-8")
        shown = _rel_to_repo(path, repo)
        bad = relative_page_hrefs(html)
        if bad:
            fails.append(
                f"R115: live preview {shown} has {len(bad)} relative page href(s) that 404 under /pages/previews/{issue}/ (e.g. {bad[0]})"
            )
        missing = missing_page_targets(html, repo)
        if missing:
            fails.append(
                f"R115: live preview {shown} has {len(missing)} page href(s) with no file under pages/ (e.g. {missing[0]})"
            )
    return fails

def stamps(html):
    c, m = CAL.findall(html), MAST.findall(html)
    assert len(c) == 1, f"R70: expected 1 Calendar check line, found {len(c)}"
    return c[0], (m[0] if m else None)

def sync(local_preview, repo, issue):
    dst = Path(repo) / f"pages/previews/{issue}/PHNEWS-{issue}-preview.html"
    if str(issue) < ABSOLUTE_FROM:  # Oct 25 rebuild path: byte copy, including R96 relative hrefs
        shutil.copyfile(local_preview, dst); return dst
    # R115: the local review copy stays relative (R96). The nested live preview gets SEND's absolute page URLs.
    dst.write_text(absolutize_live_preview(Path(local_preview).read_text(encoding="utf-8")), encoding="utf-8")
    return dst

STALE_HINT = "SEND is from an earlier build, re-run publish_issue (python3 scripts/publish_issue.py --issue {i} --root {r} [--dry-run])"

def stale_copy(issue, root, preview_html):
    """R70b (Steven Nov 4 2026 9:06 PM): a rebuild that changes the calendar stamp makes an existing SEND stale. COPY it (never
    delete/move) to PHNEWS-<issue>-SEND.stale-<old stamp>.html so the mismatch is visible; the strict check still fails until
    publish_issue regenerates SEND. Returns the copy path or None."""
    sd = Path(root) / f"PHNEWS-{issue}-SEND.html"
    if not sd.exists(): return None
    s = stamps(sd.read_text(encoding="utf-8")); p = stamps(preview_html)
    if s == p: return None
    tag = re.sub(r"[^A-Za-z0-9]+", "-", s[0].replace("Calendar check", "")).strip("-").lower() or "unknown"
    dst = Path(root) / f"PHNEWS-{issue}-SEND.stale-{tag}.html"
    if not dst.exists(): shutil.copy2(sd, dst)
    return dst

def check(issue, root, repo):
    pv = Path(repo) / f"pages/previews/{issue}/PHNEWS-{issue}-preview.html"; sd = Path(root) / f"PHNEWS-{issue}-SEND.html"
    pt = pv.read_text(encoding="utf-8"); p = stamps(pt); fails = []
    # R115 (Steven Nov 7 2026) / R115b (Steven Nov 12 2026): every dated live preview from Nov 1 on
    # (not only this --issue) must use absolute page URLs, and those URLs must exist under pages/.
    fails.extend(check_live_preview_hrefs(repo))
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
    if fails and any(f.startswith("R70:") for f in fails): fails.append("R70b: " + STALE_HINT.format(i=issue, r=root))
    return fails, p

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--issue", required=True)
    a.add_argument("--root", default="/workspace/phnews-consolidation/oct18"); a.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    a = a.parse_args(); f, p = check(a.issue, a.root, a.repo)
    ok = f"R70 PASS: preview = SEND ({p[0]}; masthead {p[1]})"
    if not any(x.startswith("R115") for x in f): ok += "; R115 PASS: every live preview from 2026-11-01 on has absolute page links that exist under pages/"
    print("\n".join(f) if f else ok); sys.exit(1 if f else 0)
