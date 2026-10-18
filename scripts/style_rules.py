#!/usr/bin/env python3
"""Shared PHNEWS format rules (see STYLE-RULES.md). Import from any builder.

- enforce_title_months(html): spell months in full inside titles/headings/subtitle bands.
- mon3_text(html): abbreviate months in body text but SKIP title regions (fixes old mon3_text todo).
- listen_fix(html): Listen link one line, right cell 14px inset.
"""
import re, html as _h
MON3 = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
FULL = ("January","February","March","April","May","June","July","August","September","October","November","December")
_ABBR = {**{m: FULL[i] for i, m in enumerate(MON3)}, "Sept": "September"}
_ABBR_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\.?(?=\s+\d|\s*$|\s*[,–-])")
_FULL_RE = re.compile(r"\b(" + "|".join(FULL) + r")\b")
# Title regions: (open-tag regex, closing tag name)
TITLE_RES = [
    re.compile(r"(<title>)(.*?)(</title>)", re.S | re.I),
    re.compile(r"(<h[1-4]\b[^>]*>)(.*?)(</h[1-4]>)", re.S | re.I),
    re.compile(r"(<(div|p|span|td)\b[^>]*class=\"[^\"]*(?:section-title|subtitle|ph-section-sub|band-sub)[^\"]*\"[^>]*>)(.*?)(</\2>)", re.S | re.I),
    re.compile(r"(<div\b[^>]*font-style:\s*italic[^>]*color:\s*#fff[^>]*>)(.*?)(</div>)", re.S | re.I),
]
def _expand_text(t):  # only text between tags
    return re.sub(r">([^<]*)<", lambda m: ">" + _ABBR_RE.sub(lambda x: _ABBR[x.group(1)], m.group(1)) + "<", ">" + t + "<")[1:-1]
def _regions(s):
    for rx in TITLE_RES:
        for m in rx.finditer(s):
            inner_idx = 3 if rx.groups == 4 else 2
            yield m.start(inner_idx), m.end(inner_idx)
def enforce_title_months(s):
    spans = sorted(set(_regions(s)), reverse=True)
    done = []
    for a, b in spans:
        if any(a >= x and b <= y for x, y in done): continue
        s = s[:a] + _expand_text(s[a:b]) + s[b:]
        done.append((a, b))
    return s
def mon3_text(s):
    """Abbreviate full months in visible text, then restore full months in title regions."""
    s = re.sub(r">([^<]+)<", lambda m: ">" + _FULL_RE.sub(lambda x: MON3[FULL.index(x.group(1))], m.group(1)) + "<", s)
    return enforce_title_months(s)
def title_month_violations(s):
    out = []
    for a, b in _regions(s):
        t = re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", s[a:b]))).strip()
        if _ABBR_RE.search(t): out.append((s.count("\n", 0, a) + 1, t[:140]))
    return list(dict.fromkeys(out))
A_STYLE = "color:#3A6B1A;white-space:nowrap !important;word-break:keep-all !important;overflow-wrap:normal !important;display:inline-block;font-size:14px;"
TD_STYLE = "padding-right:14px;white-space:nowrap !important;min-width:76px;"
def listen_fix(s):
    def td(m):
        t = m.group(0)
        head = re.match(r'<td[^>]*>', t).group(0)
        if "padding-right:14px" not in head:
            head2 = head.replace('width:1%;"', 'width:1%;' + TD_STYLE + '"', 1)
            assert head2 != head, head
            t = head2 + t[len(head):]
        def a(mm):
            tag = mm.group(0)
            return re.sub(r'style="[^"]*"', f'style="{A_STYLE}"', tag, count=1)
        i = t.rfind('<a ')
        return t[:i] + re.sub(r'<a [^>]*>', a, t[i:], count=1)
    return re.sub(r'<td[^>]*>(?:(?!</td>).)*?>Listen</a>', td, s, flags=re.S)
if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        p = open(f, encoding="utf-8").read(); n = enforce_title_months(p)
        if n != p: open(f, "w", encoding="utf-8").write(n); print("fixed", f)


# STYLE-RULES R27 (Steven, Oct 17 12:39 AM): the two footer service-request lines fit on one line at desktop/email width.
# 13px bold (was 14px from the box) fits the 620px box of the 660px newsletter column; <=640px viewports drop to 12px
# (never smaller); phones may wrap. Bold, colors and the VANTACA link are unchanged. Idempotent.
SVC_CSS = '<style id="ph-svc-r27">@media (max-width:640px){.ph-svc-line{font-size:12px !important;line-height:1.35 !important}}</style>'
def service_box_fit(s):
    import re as _re
    s = s.replace(SVC_CSS, "")
    n = 0
    for lab in ("NON-URGENT SERVICE REQUESTS", "URGENT SERVICE REQUESTS"):
        pat = _re.compile(r'<div (?:class="ph-svc-line" )?style="color:#2D5016;font-weight:bold;((?:margin-top:4px;)?)(?:font-size:\d+px;line-height:[\d.]+;)?">' + lab)
        s, k = pat.subn(lambda m: f'<div class="ph-svc-line" style="color:#2D5016;font-weight:bold;{m.group(1)}font-size:13px;line-height:1.35;">' + lab, s, count=1)
        n += k
    assert n == 2, f"R27: service-request lines not found ({n})"
    # phones: keep each phone number whole when the URGENT line wraps (no "(727)" / "581-8729" split)
    a = s.find('URGENT SERVICE REQUESTS – Business Hours:'); b = s.find("</div>", a)
    seg = _re.sub(r'(?<!nowrap;">)\((\d{3})\) (\d{3}-\d{4})', r'<span style="white-space:nowrap;">(\1) \2</span>', s[a:b])
    s = s[:a] + seg + s[b:]
    i = s.find('<div style="background:#FFF9E6;')
    assert i > 0, "R27: service-request box not found"
    return s[:i] + SVC_CSS + s[i:]


# STYLE-RULES R33 (Steven, Oct 17): Did You Know pieces end with the contributor's name as a plain byline -- the last paragraph
# of the content card is exactly the name (no title such as "Board VP", no "By", no comma suffix) unless the contributor asks.
def dyk_byline_ok(html, name):
    import re as _re
    card = _re.search(r'<div class="content-card">(.*?)</div>', html, _re.S)
    if not card: return False
    paras = _re.findall(r'<p[^>]*>(.*?)</p>', card.group(1), _re.S)
    return bool(paras) and _re.sub(r"<[^>]+>|\s+", " ", paras[-1]).strip() == name


# STYLE-RULES R34 (Steven, Oct 17): a Did You Know piece that cites a park rule links to the official club Rules & Regulations PDF
# on palmhillcountryclub.net (never a copy hosted on palmhillnews/Vercel/CDN), on its own line outside the piece card.
def dyk_rule_link_ok(html):
    import re as _re
    links = _re.findall(r'<p class="dyk-rules-link"[^>]*><a href="([^"]+)"', html)
    if len(links) != 1: return False
    u = links[0].replace("&#x27;", "'").replace("&amp;", "&")
    if not (u.startswith("https://www.palmhillcountryclub.net/") and u.lower().endswith(".pdf")): return False
    card = _re.search(r'<div class="content-card">(.*?)</div>', html, _re.S)
    if not (bool(card) and "dyk-rules-link" not in card.group(1) and html.find("dyk-rules-link") > card.end()): return False
    # R34 (Steven, Oct 17 2:40 PM): the cited rule's heading inside the piece links to the same official PDF
    heads = _re.findall(r'<a class="dyk-rule-heading" href="([^"]+)"', card.group(1))
    return len(heads) >= 1 and all(h == links[0] for h in heads)


# STYLE-RULES R39 (Steven, Oct 17; 6:28 PM: at most 3 source sentences): the issue's Did You Know summary is at most 3 sentences
# (and <= 300 characters) and every sentence is the contributor's own sentence, verbatim, from the source text (light trims
# only: a leading connector like "Further - " may be dropped and a doubled period collapsed).
def dyk_summary_ok(summary, source_paras):
    import re as _re
    src = " ".join(source_paras).replace("..", ".")
    src = _re.sub(r"\s+", " ", src)
    sents = [x.strip() for x in _re.split(r"(?<=[.!?])\s+", summary.strip()) if x.strip()]
    return len(summary) <= 300 and 1 <= len(sents) <= 3 and all(x in src for x in sents)  # Steven 6:28 PM: at most 3 source sentences


# STYLE-RULES R39 framing teaser (Steven, Oct 17 6:32 PM): a general description of the item's topic and source -- no contributor
# name, no quoted rule (no run of 5+ consecutive source words), <= 3 lines at desktop (<= 250 characters at 15px / 640px).
def dyk_framing_ok(teaser, names, source_paras):
    import re as _re
    if len(teaser) > 250 or any(_re.search(r"\b" + _re.escape(n) + r"\b", teaser, _re.I) for n in names): return False
    w = lambda t: _re.findall(r"[a-z0-9']+", t.lower())
    src = " " + " ".join(w(" ".join(source_paras))) + " "; tw = w(teaser)
    return not any(" " + " ".join(tw[i:i + 5]) + " " in src for i in range(len(tw) - 4))

# R39 issue check: the Did You Know "More →" links to the item's own page
def dyk_more_link_ok(issue_html, page_name):
    import re as _re
    sec = issue_html[issue_html.find("Did You Know?"):]
    m = _re.search(r'<a href="([^"]+)"[^>]*>More →</a>', sec)
    return bool(m) and m.group(1).endswith(page_name)


# STYLE-RULES R40 (Steven, Oct 17 7:23 PM): every copy -- live issue, SEND, previews, test copies -- is clean: no review/test
# stamp or banner. Fails the build on stamp markup, "Review copy", "Calendar checked:" or a cal-*.json snapshot filename.
# (The R24 resident footer line "Calendar check - October 17, 6:33 PM" is allowed.) Returns the html for chaining.
def assert_no_stamp(html, name):
    import re as _re
    bad = [m for m in ("ph-review-stamp", "Review copy", "Calendar checked:") if m in html]
    if _re.search(r"cal-\d{8}(?:-\d{4})?\.json", html): bad.append("cal-*.json filename")
    if bad: raise SystemExit(f"R40: {name} carries a review/test stamp: {bad}")
    return html


# STYLE-RULES R41 (amended Oct 17 10:33 PM) + R43 (Steven, Oct 17 10:29 PM): archive links read '<Singular noun> Archives →'.
# Committee reports come from the committee liaison: 'Committee Report Archives →', never 'Chair Report'. The newsletter's
# 'Past X →' section links, 'Did You Know? Archives →' (R44: no '?' since Oct 17 11:51 PM), singular 'Video Archive →', the 'Palm Hill Archives' link and the
# '← (All) Video Archives' back links are retired. Archived issue copies (pages/archive/issues/, issues/) stay exactly as sent.
EMAIL_ARCHIVE_LABELS = [
    ("Past President Messages →", "President's Message Archives →"),
    ("Past Shareholders Reports →", "Shareholders Report Archives →"),
    ("Past Weekly Manager Updates →", "Weekly Manager Report Archives →"),
    ("Chair Report Archives →", "Committee Report Archives →"),
    ("Did You Know? Archives →", "Did You Know Archives →"),  # R44 (Steven, Oct 17 11:51 PM): no '?' in archive labels
]
RETIRED_ARCHIVE_LABEL_RE = (r"Previous (?:Chair Reports|Notices|Events|Meetings|Weekly Updates|Shareholders Reports|Tips|Videos)\b"
    r"|Chair Report Archives|>Palm Hill Archives</a>|Did You Know\? Archives|Video Archive →|>← (?:All )?Video Archives<"
    r"|Past (?:President Messages|Shareholders Reports|Weekly Manager Updates|Stories|Messages|Meetings|Reports|Updates|Events|Notices|Tips|Videos) →")
def archive_labels(s):
    """Apply the R41/R43 label map to a newsletter/page string (link text only)."""
    for a, b in EMAIL_ARCHIVE_LABELS:
        s = s.replace(f">{a}<", f">{b}<")
    return s
def archive_label_violations(s):
    import re as _re
    return sorted(set(_re.findall(RETIRED_ARCHIVE_LABEL_RE, s)))
def assert_archive_labels(s, name):
    bad = archive_label_violations(s)
    if bad: raise SystemExit(f"R41/R43: {name} has retired archive label(s): {bad}")
    return s


# STYLE-RULES R44 (Steven, Oct 17 11:35 PM + 11:51 PM): an archive page's top area (masthead to the page title) carries exactly
# ONE link, 'All Archives →', to the All Archives page (main.html). No second crumb line, no jump/sibling links. The address
# strip is not a navigation link. Archived issue copies (pages/archive/issues/) keep their own frame and are not checked.
ARCHIVE_TOP_LABEL = "All Archives →"
def archive_top_links(s):
    """[(href, text)] of every link between <body> and the first <h1>, address strip excluded."""
    import re as _re, html as _h
    body = s.split("<body", 1)[-1]
    hero = _re.search(r'<header class="pa-hero">.*?</header>\s*(?:<nav class="pa-bar".*?</nav>)?', body, _re.S)  # archive hubs: the hero holds title + top link
    top = hero.group(0) if hero else _re.split(r"<h1\b", body, maxsplit=1)[0]
    top = _re.sub(r"<script.*?</script>|<style.*?</style>", "", top, flags=_re.S)
    out = []
    for href, txt in _re.findall(r'<a\b[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', top, _re.S):
        txt = _h.unescape(_re.sub(r"\s+", " ", _re.sub(r"<[^>]+>", "", txt))).strip()
        if "google.com/maps" in href or "Seminole Blvd" in txt: continue
        out.append((href, txt))
    return out
def archive_top_violations(s, is_hub=False):
    links = archive_top_links(s)
    if is_hub: return [] if not links else [f"hub page carries top links {links}"]
    if len(links) != 1: return [f"{len(links)} top links {[t for _, t in links]} (want exactly 1 '{ARCHIVE_TOP_LABEL}')"]
    href, txt = links[0]
    bad = []
    if txt != ARCHIVE_TOP_LABEL: bad.append(f"top link reads {txt!r}, want {ARCHIVE_TOP_LABEL!r}")
    if not href.split("#")[0].endswith("main.html"): bad.append(f"top link goes to {href!r}, want main.html")
    return bad
def assert_archive_top(s, name, is_hub=False):
    bad = archive_top_violations(s, is_hub)
    if bad: raise SystemExit(f"R44: {name}: " + "; ".join(bad))
    return s


# STYLE-RULES L27/L29 (Steven, Oct 10 ~2:10 PM, amended Oct 11 ~8:37 AM; restated as a rule + guard Oct 17 11:51 PM):
# a Webmaster Source credit is the linked short word 'Webmaster' (the link opens the copy of the source email) and nothing
# else -- no date, no sender name in brackets, no 'email'/'notice', never 'Palm Hill Webmaster'. No Source credit carries a date.
_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d"
def source_credits(s):
    """Raw HTML of every 'Source: ...' credit (up to the end of its line/cell)."""
    import re as _re
    return [_re.split(r"</div>|</p>|</td>|<br", s[m.start():m.start() + 900], maxsplit=1)[0]
            for m in _re.finditer(r"Source:\s", s)]
def source_credit_violations(s):
    import re as _re, html as _h
    bad = []
    for raw in source_credits(s):
        txt = _h.unescape(_re.sub(r"<[^>]+>", "", raw)).replace("\xa0", " ").strip()
        if _re.search(_MONTH, txt): bad.append(f"date in Source credit: {txt!r}")
        if "Webmaster" in txt:
            linked = _re.findall(r"<a\b[^>]*>\s*Webmaster\s*</a>", raw)
            if txt.count("Webmaster") != len(linked): bad.append(f"unlinked Webmaster: {txt!r}")
            if _re.search(r"Webmaster\s*[(,]|Palm Hill Webmaster|Webmaster (?:email|notice)", txt): bad.append(f"Webmaster credit not short: {txt!r}")
    return bad
def assert_source_credits(s, name):
    bad = source_credit_violations(s)
    if bad: raise SystemExit(f"L27/L29: {name}: " + "; ".join(bad))
    return s


# STYLE-RULES R45 (Steven, Oct 18 12:07 AM): every issue carries a Community Stories section with at least one story row
# (title, date line, teaser, More → to the story page, Listen to its listen page). Leaving it out needs Steven's approval,
# recorded in the builder (COMMUNITY_STORIES_OMIT_APPROVED = "<who/when>"); without it the build stops.
def community_stories_violations(s):
    import re as _re
    h = s.find(">Community Stories</span>")
    if h < 0: return ["no Community Stories section"]
    end = min([x for x in (s.find('<div class="canonical-section">', h), s.find('<div class="section04">', h)) if x > 0] or [len(s)])
    sec = s[h:end]
    bad = []
    if "More →</a>" not in sec: bad.append("Community Stories row has no 'More →' link")
    if not _re.search(r'href="[^"]*listen[^"]*"', sec): bad.append("Community Stories row has no Listen link")
    if not _re.search(r'>(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day, [A-Z][a-z]{2} \d{1,2}, \d{4}<', sec): bad.append("Community Stories row has no date line")
    return bad
def assert_community_stories(s, name, omit_approved=None):
    if omit_approved:
        if ">Community Stories</span>" in s: raise SystemExit(f"R45: {name}: omission approved ({omit_approved}) but the section is present")
        return s
    bad = community_stories_violations(s)
    if bad: raise SystemExit(f"R45: {name}: " + "; ".join(bad) + " (an issue without a story needs Steven's approval: COMMUNITY_STORIES_OMIT_APPROVED)")
    return s
