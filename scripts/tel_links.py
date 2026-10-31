"""STYLE-RULES R85 (Steven, Oct 27 2026 12:25 AM: "We need to be sure all phone numbers are live links for smartphones").
One shared helper: wrap every printed phone number in a tel: link, link styled like the issue's other links.
Visible text is never changed; the href carries +1 and the digits. Gated from TEL_FROM so Oct 25 stays byte-identical.
7-digit numbers are NOT auto-linked (area code would be a guess) -- they are reported by find_bare() as 'needs Steven OK'."""
import re
TEL_FROM = "2026-11-01"
LINK_STYLE = "color:#3A6B1A;white-space:nowrap;"   # = the NL's standard nowrap link style (G)
# R85b: tolerate one stray space/nbsp around the last separator ("608-312 -6958"); visible text kept.
# 10-digit (with optional +1 / ext.) or toll-free; separators - . space; (727) form
PHONE = re.compile(r"(?<![\w/=.+-])(?:\+?1[ .-]?)?(?:\(\d{3}\)[ \u00a0]?|\d{3}[ .\u00a0-])\d{3}[ \u00a0]?[.-][ \u00a0]?\d{4}(?:\s*(?:ext\.?|x)\s*\d{1,5})?(?![\w-])")
SEVEN = re.compile(r"(?<![\w/=.()+-])(?<!\) )\d{3}-\d{4}(?![\w-])")
_SKIP = re.compile(r"(<script\b[\s\S]*?</script>|<style\b[\s\S]*?</style>|<!--[\s\S]*?-->|<a\b[\s\S]*?</a>|<title\b[\s\S]*?</title>|<head\b[\s\S]*?</head>|<[^>]+>)", re.I)
def applies(issue): return issue >= TEL_FROM
def dated_from(name):
    """a page whose file name starts with a date >= TEL_FROM (archive/ and undated pages never)."""
    return bool(re.match(r"\d{4}-\d{2}-\d{2}-", name)) and name[:10] >= TEL_FROM
def href(num):
    m = re.match(r"(.*?)(?:\s*(?:ext\.?|x)\s*(\d+))?$", num); d = re.sub(r"\D", "", m.group(1))
    if len(d) == 11 and d[0] == "1": d = d[1:]
    assert len(d) == 10, num
    return "tel:+1" + d + ("," + m.group(2) if m.group(2) else "")
def _wrap_text(t):
    return PHONE.sub(lambda m: f'<a href="{href(m.group(0))}" style="{LINK_STYLE}">{m.group(0)}</a>', t)
def linkify(html):
    """Wrap bare phone numbers in text nodes only (never inside tags, existing <a>, head, script, style)."""
    parts = _SKIP.split(html)
    return "".join(p if i % 2 else _wrap_text(p) for i, p in enumerate(parts))
def _text_nodes(html):
    parts = _SKIP.split(html); return [p for i, p in enumerate(parts) if not i % 2]
def find_bare(html):
    """(bare 10-digit numbers, bare 7-digit numbers) left in text nodes."""
    tn = _text_nodes(html); ten = [m.group(0) for t in tn for m in PHONE.finditer(t)]
    seven = [m.group(0) for t in tn for m in SEVEN.finditer(PHONE.sub("", t))]
    return ten, seven
def tel_mismatches(html):
    """every <a href="tel:..."> whose visible digits do not match the href digits (+1, ext as ',')."""
    bad = []
    for m in re.finditer(r'<a\b[^>]*href="tel:([^"]+)"[^>]*>([\s\S]*?)</a>', html, re.I):
        h = re.sub(r"[^\d,]", "", m.group(1)).replace(",", ""); vis = re.sub(r"<[^>]+>", "", m.group(2))
        v = re.sub(r"\D", "", vis)
        if not v: continue  # icon-only / "Call" link: nothing visible to compare
        if len(v) == 10 or (len(v) > 10 and not v.startswith("1")): v = "1" + v
        if h != v and not (h.startswith("1") and h[1:] == v): bad.append((m.group(1), vis.strip()))
    return bad
if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        t = open(f, encoding="utf-8").read(); print(f, find_bare(t), tel_mismatches(t))
