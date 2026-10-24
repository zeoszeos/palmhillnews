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


# STYLE-RULES R47 (Steven, Oct 18 12:23 AM): for a Webmaster-sourced item (Source line = the linked short word 'Webmaster' only,
# L27/L29 unchanged) the 'More →' link and the Source link open the SAME full-email page, and Listen opens that page with
# ?listen=1. The short 2026-10-18-notice-*.html summary pages stay live but are never linked from the issue. Mixed-source rows
# (e.g. 'Source: Calendar, Webmaster', where More → is the calendar listing page, R21) are not covered.
def webmaster_items(s):
    """[(title, webmaster_href, more_hrefs, listen_hrefs, all_hrefs)] for every issue row whose Source is only 'Webmaster'."""
    import re as _re, html as _h
    out = []
    for r in s.split('<tr style="background:')[1:]:
        m = _re.search(r'margin-top:5px;">(Source:.*?)</div>', r, _re.S)
        if not m: continue
        r = r[:m.end()]  # the Source line ends the row
        src = m.group(1)
        if _re.sub(r"\s+", " ", _h.unescape(_re.sub(r"<[^>]+>", "", src))).strip() != "Source: Webmaster": continue
        w = _re.search(r'<a href="([^"]+)"[^>]*>Webmaster</a>', src)
        if not w: continue
        t = _re.search(r'padding-right:8px;">(.*?)</td>', r, _re.S)
        links = _re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r, _re.S)
        more = [h for h, x in links if _re.sub(r"<[^>]+>", "", x).strip() == "More →"]
        lis = [h for h, x in links if _re.sub(r"<[^>]+>", "", x).strip().endswith("Listen")]
        out.append((_h.unescape(_re.sub(r"<[^>]+>", "", t.group(1))).strip() if t else "?", w.group(1), more, lis, [h for h, _ in links]))
    return out
def webmaster_more_violations(s, repo=None):
    bad = []
    for title, wm, more, lis, hrefs in webmaster_items(s):
        for h in more:
            if h.split("?")[0] != wm: bad.append(f"{title}: More → {h} differs from the Webmaster source {wm}")
        for h in lis:
            if h != wm + "?listen=1": bad.append(f"{title}: Listen {h} must be {wm}?listen=1")
        short = [h for h in hrefs if ISSUE_NOTICE_RE.search(h)]  # A6 (Oct 24): any issue date, not only Oct 18
        if short: bad.append(f"{title}: links a short notice page {short}")
        if repo is not None:
            import os as _os
            f = _os.path.join(str(repo), "pages", wm.split("/pages/", 1)[-1])
            if not _os.path.exists(f) or "<!-- ph-page-listen:start -->" not in open(f, encoding="utf-8").read():
                bad.append(f"{title}: full-email page {wm} has no Listen")
    return bad
def assert_webmaster_more(s, name, repo=None):
    bad = webmaster_more_violations(s, repo)
    if bad: raise SystemExit(f"R47: {name}: " + "; ".join(bad))
    return s


# STYLE-RULES R48 (Steven, Oct 18 12:31 AM): every event row (Committee & Board Meeting Schedules, Events - This Week,
# Events - Upcoming, any other Events/Meetings section) has an OFFICIAL date source: the Palm Hill club calendar ('Calendar'),
# an RPM calendar ('RPM'), or a committee agenda email (the row's 'Agenda →' opens the same email page its Source links).
# Date, time and place come from that source. A Webmaster email (incl. Linda's Info from Linda) may be added as a second
# 'Webmaster' source and lend description wording, but an event found ONLY in a Webmaster/Linda email is never an event row;
# it stays inside that email's Community Notice (e.g. the Largo Evening Market in Info from Linda).
R48_OFFICIAL = ("Calendar", "RPM", "RPM Calendar", "Agenda")
def _r48_sections(s):
    import re as _re
    heads = [(m.start(), m.group(1)) for m in _re.finditer(r'-webkit-text-fill-color:#FFFFFF;">([^<]+)</span>', s)]
    for i, (a, hd) in enumerate(heads):
        if not (hd.startswith("Events") or "Meeting Schedules" in hd or hd.startswith("Meetings")): continue
        yield hd, s[a:heads[i + 1][0] if i + 1 < len(heads) else len(s)]
def event_source_violations(s):
    import re as _re, html as _h
    bad = []
    for hd, sec in _r48_sections(s):
        for r in sec.split('<tr style="background:')[1:]:
            t = _re.search(r'padding-right:8px;">(.*?)</td>', r, _re.S) or _re.search(r'font-weight:bold[^>]*>(.*?)</', r, _re.S)
            title = _h.unescape(_re.sub(r"<[^>]+>", "", t.group(1))).strip() if t else "?"
            i = r.find("Source:")
            if i < 0: bad.append(f"{_h.unescape(hd)} / {title}: no Source line"); continue
            src = r[i:]
            labels = [_re.sub(r"<[^>]+>", "", x).strip() for _, x in _re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', src, _re.S)]
            labels += [x.strip() for x in _re.split(r"[,;]", _h.unescape(_re.sub(r"<a .*?</a>|<[^>]+>", "", src[len("Source:"):]).replace("\xa0", " "))) if x.strip()]
            srch = [h.split("?")[0] for h, _ in _re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', src, _re.S)]
            agenda = [h.split("?")[0] for h, x in _re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r[:i], _re.S) if _re.sub(r"<[^>]+>", "", x).strip().startswith("Agenda")]
            official = any(l in R48_OFFICIAL for l in labels) or any(h in srch for h in agenda)
            if not official:
                why = "only source is Webmaster" if labels and all(l == "Webmaster" for l in labels) else f"Source {labels} has no Calendar/RPM/Agenda"
                bad.append(f"{_h.unescape(hd)} / {title}: {why} (R48: event rows need an official date source)")
    return bad
def assert_event_sources(s, name):
    bad = event_source_violations(s)
    if bad: raise SystemExit(f"R48: {name}: " + "; ".join(bad))
    return s


# R50 (Steven, Oct 19 2026 9:25 PM): amends R31 newest-only Did You Know.
def dyk_items_ok(items, multi_approved=None):
    """Issue shows DYK_ITEMS[0] only unless Steven approved several for this issue.
    multi_approved: '<who/when>' string recorded in the builder/data. Each item needs id + paragraphs."""
    if not items: return False
    if len(items) > 1 and not (isinstance(multi_approved, str) and multi_approved.strip()):
        return False
    return all(i.get("id") and i.get("paragraphs") for i in items)

def assert_dyk_items(items, multi_approved=None):
    assert dyk_items_ok(items, multi_approved), "R50: more than one Did You Know in the issue needs Steven's recorded approval (DYK_MULTI_APPROVED)"


# STYLE-RULES R52 (Steven, Oct 20 2026 3:03 PM): no "Palm Hill Link" name inside any article / story / Did You Know page
# (body, source line or credit). Site navigation in the newsletter (Palm Hill Link Archives etc.) is not an article page.
def assert_no_link_name(html, name):
    import re as _re
    body = _re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<title>[\s\S]*?</title>", "", html)
    if _re.search(r"Palm\s+Hill\s+Link", body, _re.I): raise SystemExit(f"R52: {name} contains 'Palm Hill Link' (no Link name inside articles)")
    return html


# STYLE-RULES R56 (Steven, Oct 21 2026 10:44 AM, "middle path"): an event that matches a Webmaster/resident email notice shows ONLY
# calendar facts (name, place, date, time); More → goes straight to the notice page; no text copied from the email; the only
# links allowed are the notice page and the club Calendar (Source line). Fails the build otherwise.
def assert_matched_event_card(row, name, notice_url, cal_url, notice_html):
    import re as _re, html as _h
    hrefs = set(_re.findall(r'href="([^"]+)"', row))
    bad = hrefs - {notice_url, cal_url}
    if bad: raise SystemExit(f"R56: {name} event card links {sorted(bad)} (only the notice page + Calendar allowed)")
    if not _re.search(r'<a href="' + _re.escape(notice_url) + r'"[^>]*>More →</a>', row): raise SystemExit(f"R56: {name} More → must open the notice page")
    if 'font-size:15px;color:#333333;margin-top:3px;' in row: raise SystemExit(f"R56: {name} event card has a description line (calendar facts only)")
    w = lambda t: _re.findall(r"[a-z0-9']+", _h.unescape(_re.sub(r"<[^>]+>", " ", t)).lower())
    nw = w(_re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", notice_html)); grams = {tuple(nw[i:i+6]) for i in range(len(nw) - 5)}
    cw = w(_re.sub(r'<div style="font-size:13px[^>]*>.*?</div>', "", row))
    hit = [" ".join(cw[i:i+6]) for i in range(len(cw) - 5) if tuple(cw[i:i+6]) in grams]
    if hit: raise SystemExit(f"R56: {name} event card copies email text: {hit[0]!r}")
    return row


# STYLE-RULES R57 (Steven, Oct 21 2026 11:22 AM): each Did You Know item on the newsletter is its own block (tr.ph-dyk-item) with a
# non-empty bold title, a teaser, and More → on its own line; blocks are visibly separated.
def assert_dyk_blocks(html, n):
    import re as _re
    a = html.find(">Did You Know?</span>"); seg = html[a:html.find("Did You Know Archives →", a)]
    blocks = _re.findall(r'<tr class="ph-dyk-item"[\s\S]*?</td></tr>', seg)
    if len(blocks) != n: raise SystemExit(f"R57: {len(blocks)} Did You Know blocks, expected {n}")
    for b in blocks:
        t = _re.search(r'<div class="ph-dyk-title"[^>]*>([^<]+)</div>', b)
        if not t or not t.group(1).strip() or "font-weight:bold" not in b: raise SystemExit("R57: Did You Know block without a bold title")
        if not _re.search(r'<div class="ph-dyk-more"[^>]*><a href="[^"]+"[^>]*>More →</a></div>', b): raise SystemExit(f"R57: {t.group(1)}: More → not on its own line")
        if "border-bottom:10px solid #FFFFFF" not in b: raise SystemExit(f"R57: {t.group(1)}: no separation between items")
    return html


# A6 (Steven-approved Oct 24 2026, Claude review): issue-date-agnostic helpers shared by the scripts below.
# The current issue = PHNEWS_ISSUE env var, else the newest pages/previews/YYYY-MM-DD folder.
ISSUE_NOTICE_RE = re.compile(r"\d{4}-\d{2}-\d{2}-notice-|/previews/\d{4}-\d{2}-\d{2}/notices/")
def current_issue(repo=None):
    import os as _o
    if _o.environ.get("PHNEWS_ISSUE"): return _o.environ["PHNEWS_ISSUE"]
    repo = repo or _o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
    ds = sorted(d for d in _o.listdir(_o.path.join(repo, "pages", "previews")) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d))
    return ds[-1]


# STYLE-RULES R66 (Steven, Oct 24 2026 3:02 PM): Rules & Regulations Did You Know teasers are generated from the rule's
# lettered parts (A, B, C...): one short topic phrase per part, joined as "Information on X, Y, and Z." Phrases may only
# use topics present in the rule text (per-item override of the phrase list allowed). <= 3 lines at 390px mobile.
R66_GENERIC = {"information", "on", "and", "the", "of", "for", "dates", "date", "due", "rules", "when", "how"}
R66_MAX_CHARS_390 = 135  # 15px Arial in the DYK block at 390px (~45 chars/line x 3), conservative

def _r66_words(t):
    return re.findall(r"[a-z]+", t.lower())

def rules_dyk_phrase_auto(part_text):
    """Default topic phrase for a lettered part: its first sentence's subject words up to the verb (source words only)."""
    first = re.split(r"(?<=[.])\s", part_text.strip())[0]
    m = re.split(r"\b(?:is|are|shall|must|may|will)\b", first, maxsplit=1)[0]
    return re.sub(r"^(?:a|an|the)\s+", "", m.strip().rstrip(",").lower())

def rules_dyk_teaser(rule_items, phrases=None):
    # one entry per lettered part; an entry may be a list of topics when a part covers several (e.g. due dates + late fees)
    phrases = list(phrases) if phrases else [rules_dyk_phrase_auto(t) for _, t in rule_items]
    flat = [x for p in phrases for x in ([p] if isinstance(p, str) else p)]
    if len(flat) == 1: body = flat[0]
    elif len(flat) == 2: body = f"{flat[0]} and {flat[1]}"
    else: body = ", ".join(flat[:-1]) + ", and " + flat[-1]
    return f"Information on {body}.", phrases

def rules_dyk_violations(teaser, rule_items, phrases):
    v = []
    if not re.fullmatch(r"Information on .+\.", teaser): v.append("not in 'Information on ...' form")
    if len(phrases) != len(rule_items): v.append(f"{len(phrases)} topic phrases for {len(rule_items)} lettered parts")
    rule_w = set(_r66_words(" ".join(t for _, t in rule_items)))
    for p in [x for q in phrases for x in ([q] if isinstance(q, str) else q)]:
        if p.lower() not in teaser.lower(): v.append(f"phrase not in teaser: {p!r}")
        for w in _r66_words(p):
            if w in R66_GENERIC: continue
            st = w[:5] if len(w) > 5 else w.rstrip("s")
            if not any(r.startswith(st) for r in rule_w): v.append(f"topic word not in rule text: {w!r}")
    if len(teaser) > R66_MAX_CHARS_390: v.append(f"over 3 lines at 390px ({len(teaser)} > {R66_MAX_CHARS_390} chars)")
    return v

def assert_rules_dyk(teaser, rule_items, phrases, name=""):
    v = rules_dyk_violations(teaser, rule_items, phrases)
    if v: raise SystemExit(f"R66: Rules DYK teaser {name!r}: " + "; ".join(v))

# R66b (Steven, Oct 24 2026 3:16 PM): the Did You Know Archives teaser for a current-issue Rules DYK item is the SAME
# R66 teaser as the main page (one source: rules_dyk_teaser). Past issues' rows stay exactly as sent.
def sync_rules_dyk_archive_text(ai_text, issue_date, row_id, teaser):
    """Set the archive-items.json DYK row text (issue_date, row_id) to the R66 teaser; returns new json text."""
    import json as _j
    d = _j.loads(ai_text); rows = d["sections"]["did-you-know"]["items"]
    hit = [r for r in rows if r.get("id") == row_id and r.get("date") == issue_date]
    if len(hit) != 1: raise SystemExit(f"R66b: expected one DYK archive row {issue_date}/{row_id}, found {len(hit)}")
    old = hit[0]["text"]
    if old == teaser: return ai_text
    pat = '"id": "' + row_id + '", '
    i = ai_text.find(pat); j = ai_text.find('"text": ', i) + len('"text": ')
    k = j + len(_j.dumps(old, ensure_ascii=False))
    assert ai_text[j:k] == _j.dumps(old, ensure_ascii=False), "R66b: archive row text not found verbatim"
    out = ai_text[:j] + _j.dumps(teaser, ensure_ascii=False) + ai_text[k:]
    _j.loads(out); return out

def assert_rules_dyk_archive(archive_html, row_id, main_teaser):
    """R66b guard: the rendered Did You Know Archives row equals the main-page teaser of the same build."""
    import re as _re, html as _h
    m = _re.search(r'<div class="ph-row(?: ph-alt)?" id="' + _re.escape(row_id) + r'">.*?<div class="ph-detail">(.*?)</div>', archive_html, _re.S)
    if not m: raise SystemExit(f"R66b: DYK archive row {row_id!r} not found")
    got = _h.unescape(m.group(1)).strip()
    if got != main_teaser: raise SystemExit(f"R66b: DYK archive teaser {row_id!r} differs from main page: {got!r} != {main_teaser!r}")
