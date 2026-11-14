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


# STYLE-RULES R118 (Steven Nov 7 2026): the Nov 8 Sunshine Directors main card keeps the printed sentence
# that ends at the semicolon, then the printed email line, as plain text. The 3-line teaser cut (R18/R18c/R39)
# had stopped at the semicolon. Steven looked at the live preview and said the email fits on the main card.
# Measured at 390px the email makes this one card 4 lines; "also, prayers can be offered." would make 5, so
# that clause stays on the item page with the rest of the printed body.
SUNSHINE_DYK_ID = "2026-11-08-email-for-sunshine-directors"
SUNSHINE_DYK_TITLE = "EMAIL for SUNSHINE DIRECTORS"
SUNSHINE_DYK_PAGE = "2026-11-08-did-you-know-email-for-sunshine-directors.html"
SUNSHINE_EMAIL_LINE = "Email address: Sunshineinpalmhill@gmail.com"
SUNSHINE_PRAYERS = "also, prayers can be offered."

def sunshine_main_teaser(paragraphs):
    """Printed main-card text: the first paragraph through its semicolon, then the email line."""
    if not paragraphs: return ""
    body = paragraphs[0]
    i = body.find(";")
    if i < 0 or SUNSHINE_EMAIL_LINE not in paragraphs: return ""
    return body[:i + 1] + " " + SUNSHINE_EMAIL_LINE

def sunshine_item_teaser_problem(item):
    """'' when this is not the Sunshine card, or its teaser is the R118 printed main-card text. Else a reason."""
    if item.get("id") != SUNSHINE_DYK_ID and item.get("title_display") != SUNSHINE_DYK_TITLE:
        return ""
    teaser = " ".join((item.get("teaser") or "").split())
    if "mailto:" in (item.get("teaser") or "").lower():
        return "Sunshine Directors main teaser must be plain text, no mailto:"
    want = sunshine_main_teaser(item.get("paragraphs") or [])
    if not want:
        return "Sunshine Directors source is missing the semicolon sentence or the printed email line"
    if teaser != want:
        return "Sunshine Directors main teaser must be the printed sentence through the semicolon, then " + SUNSHINE_EMAIL_LINE
    return ""

def dyk_new_item_teaser_ok(item):
    """R88/R39 verbatim sentences, or the R118 Sunshine card (email line kept on the main teaser)."""
    if item.get("id") == SUNSHINE_DYK_ID or item.get("title_display") == SUNSHINE_DYK_TITLE:
        return sunshine_item_teaser_problem(item) == ""
    return dyk_summary_ok(item["teaser"], item["paragraphs"])

def sunshine_main_card_problem(html):
    """R118 on a newsletter. None when this page is not Nov 8 and has no Sunshine card.
    '' when the card shows the printed email as plain text after the semicolon sentence. Else a reason."""
    nov8 = "Sunday, November 8, 2026" in html
    if SUNSHINE_DYK_TITLE not in html:
        return None if not nov8 else "main page is missing the EMAIL for SUNSHINE DIRECTORS card"
    m = re.search(r'EMAIL for SUNSHINE DIRECTORS</div><div[^>]*>([^<]*)</div>', html)
    if not m:
        return "Sunshine Directors card has no plain-text teaser"
    teaser = " ".join(_h.unescape(m.group(1)).split())
    if not teaser.endswith("through the Sunshine Directors; " + SUNSHINE_EMAIL_LINE):
        return "main card must keep the printed sentence through the semicolon, then the printed email line"
    if "pick-me-up" not in teaser:
        return "printed Sunshine Directors sentence is missing from the main card"
    if "mailto:" in m.group(0).lower():
        return "Sunshine Directors email is a mailto link on the main card"
    return ""

def sunshine_item_page_problem(html):
    """R118 on the item page: full printed body, including the prayers clause and the plain-text email."""
    if SUNSHINE_PRAYERS not in html:
        return "item page is missing the printed line " + SUNSHINE_PRAYERS
    if SUNSHINE_EMAIL_LINE not in html:
        return "item page is missing the printed email line"
    if "mailto:" in html.lower():
        return "item page must keep the email as plain text (no mailto:)"
    return ""


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
def assert_no_link_name(html, name, credit_line=None):
    import re as _re
    body = _re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<title>[\s\S]*?</title>", "", html)
    if credit_line:  # R83: the one Steven-approved credit line after </article> is the only allowed Link name
        assert_story_credit(html, credit_line, name)
        body = body.replace(f'<p class="source">{credit_line}</p>', "", 1)
    if _re.search(r"Palm\s+Hill\s+Link", body, _re.I): raise SystemExit(f"R52: {name} contains 'Palm Hill Link' (no Link name inside articles)")
    return html


# STYLE-RULES R83 (Steven, Oct 26 2026 12:19 PM, Katra Peck story: "go with first published"): a Community Story page may carry
# exactly ONE credit line <p class="source">First published in the Palm Hill Link, <Month YYYY></p>, right after </article>,
# only when the story data's credit_line is set. Anywhere else the R52 no-Link-name rule still applies.
def assert_story_credit(html, credit_line, name):
    import re as _re
    if not _re.fullmatch(r"First published in the Palm Hill Link, (January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d", credit_line):
        raise SystemExit(f"R83: {name} credit line {credit_line!r} is not 'First published in the Palm Hill Link, <Month YYYY>'")
    el = f'<p class="source">{credit_line}</p>'
    if html.count(el) != 1 or f"</article>\n{el}" not in html:
        raise SystemExit(f"R83: {name} needs exactly one credit line right after </article>")
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
    """Set the archive-items.json DYK row text (issue_date, row_id) to the R66 teaser; returns new json text (R68 helper)."""
    import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import archive_items as _aj
    try: return _aj.set_field_text(ai_text, "did-you-know", {"id": row_id, "date": issue_date}, "text", teaser)
    except SystemExit as e: raise SystemExit("R66b: " + str(e))

def assert_rules_dyk_archive(archive_html, row_id, main_teaser):
    """R66b guard: the rendered Did You Know Archives row equals the main-page teaser of the same build."""
    import re as _re, html as _h
    m = _re.search(r'<div class="ph-row(?: ph-alt)?" id="' + _re.escape(row_id) + r'">.*?<div class="ph-detail">(.*?)</div>', archive_html, _re.S)
    if not m: raise SystemExit(f"R66b: DYK archive row {row_id!r} not found")
    got = _h.unescape(m.group(1)).strip()
    if got != main_teaser: raise SystemExit(f"R66b: DYK archive teaser {row_id!r} differs from main page: {got!r} != {main_teaser!r}")

# STYLE-RULES R10 (Steven, Oct 24 2026 9:05 PM, coding batch 1): the two locked as-sent pages are pinned byte-for-byte.
# build_archive.js never rewrites them (R10_LOCKED); this guard fails the build if either page's bytes differ from the pin.
R10_LOCKED_SHA256 = {
    "pages/2026-09-30-shareholders-report.html": "9ab8daa1e31fba1e2d556979ec9e7480413ff21ce4910fb290556f9b01bd3b98",
    "pages/2026-10-09-weekly-manager-update.html": "b2976e40840afa02ce8e84fc08fee4336cb03e18cea38a6ca49f83dbd2c127db",
}
# R117 (Steven, Nov 6 2026): the R92b "See the All Events List" row uses the newsletter light green, the same tint as
# the alternating Committee Chair Reports highlight (build_core.bg / R98). Not a new green.
AE_ROW_GREEN = "#EAF4E4"
# STYLE-RULES R121 (Steven Nov 7 2026, voice): a calendar row whose visible title is only the word
# "reserved" is a room-booking placeholder, not an event. Surrounding whitespace and punctuation do not
# count. A longer title that merely contains the word stays.
# STYLE-RULES R120 (Steven Nov 7 2026): with no newer monthly report, the September 30 shareholders
# report card stays off the November 8 main page. The report page and the archive stay published.
_SEP30_REPORT = "2026-09-30-shareholders-report"
def sep30_shareholders_card_present(html):
    """True when the September 30 shareholders report card (or its report link) is in this HTML."""
    if not html: return False
    return (_SEP30_REPORT in html) or (">Monthly Shareholders Report</span>" in html)

def sep30_shareholders_main_problem(html):
    """'' or a reason. Only a November 8 main page is in scope. The report page itself is not."""
    if "November 8, 2026" not in (html or ""): return ""
    if sep30_shareholders_card_present(html):
        return "September 30 shareholders report is on the November 8 main page"
    return ""

def sep30_report_page_ok(repo):
    """The September 30 report page stays on disk. R10 also pins its bytes."""
    import os as _os
    p = _os.path.join(str(repo), "pages", _SEP30_REPORT + ".html")
    return _os.path.isfile(p) and _os.path.getsize(p) > 0

def reserved_only_name(name):
    """True when the visible title, after stripping surrounding whitespace and punctuation, is only 'reserved'."""
    if name is None: return False
    core = re.sub(r"^[\s\W_]+|[\s\W_]+$", "", str(name), flags=re.UNICODE)
    return core.casefold() == "reserved"

def _activity_event_name(title):
    """Event name from a calendar-list row. '11:00 AM · Reserved' is the name Reserved.
    A date/time line such as 'Nov 10 • 11:00 AM' is not a name."""
    title = _h.unescape(title).strip()
    if " · " in title: return title.split(" · ", 1)[1].strip()
    return title

def reserved_only_hits(html):
    """Reserved-only event titles in rendered newsletter or calendar-list HTML.
    Body copy that merely contains the word is not a hit. Returns the offending visible strings."""
    hits = []
    for t in re.findall(r'font-weight:bold;color:#333333;text-align:left;[^>]*>([^<]*)<', html or ""):
        name = _h.unescape(t).strip()
        if reserved_only_name(name): hits.append(name)
    for t in re.findall(r'class="ph-row-title">([^<]*)</div>', html or ""):
        if reserved_only_name(_activity_event_name(t)): hits.append(_h.unescape(t).strip())
    for t in re.findall(r'<h2 class="gx-h">([^<]*)<', html or ""):
        name = _h.unescape(t).strip()
        if reserved_only_name(name): hits.append(name)
    return hits

def ae_top_highlight_missing(section_html, link_text="See the All Events List"):
    """Return '' when this Events section's ph-ae-top cell carries #EAF4E4 and the exact All Events link; else a reason."""
    m = re.search(r'<td\b[^>]*\bclass="ph-ae-top"[^>]*>', section_html, re.I)
    if not m: return "no ph-ae-top cell"
    tag = m.group(0)
    if not re.search(r'background(?:-color)?\s*:\s*' + AE_ROW_GREEN + r'\b', tag, re.I):
        return "ph-ae-top cell has no background:" + AE_ROW_GREEN
    if not re.search(r'''bgcolor\s*=\s*['"]''' + AE_ROW_GREEN + r'''['"]''', tag, re.I):
        return "ph-ae-top cell has no bgcolor " + AE_ROW_GREEN
    end = section_html.find("</td>", m.end())
    cell = section_html[m.start(): end if end >= 0 else m.end()]
    if f">{link_text}</a>" not in cell: return f"ph-ae-top cell does not say {link_text}"
    return ""

def assert_r10_locked_pages(repo):
    import hashlib, os as _os
    for rel, want in R10_LOCKED_SHA256.items():
        f = _os.path.join(str(repo), rel)
        got = hashlib.sha256(open(f, "rb").read()).hexdigest() if _os.path.exists(f) else None
        if got != want: raise SystemExit(f"R10: locked page {rel} changed (sha256 {got}, pinned {want}); it must stay exactly as sent")

# R119 (Steven, Nov 7 2026): iPhone/iPad Listen on the page opened from the email.
# A blocked load-time start used to set playing while started stayed false, and
# `if (playing) stop()` swallowed the first Listen tap. The phone must show Tap to listen
# immediately, without waiting for speech to start.
_R119_SWALLOW = re.compile(r"if\s*\(\s*playing\s*\)\s*stop\(\)\s*;\s*else\s*start\(\s*false\s*\)")
_R119_START = re.compile(r"if\s*\(\s*playing\s*&&\s*started\s*\)\s*stop\(\)\s*;\s*else\s*start\(\s*false\s*\)")
_R119_BAR = re.compile(r"if\s*\(\s*iphoneOrIpad\(\)\s*\)\s*showBar\(\)\s*;")

def listen_page_iphone_problem(src):
    """R119. '' when this v2 page-listen script is safe. Else why the first iPhone tap would fail."""
    if _R119_SWALLOW.search(src):
        return "Listen click treats a blocked auto-start (playing, speech not started) as Stop"
    if not _R119_START.search(src):
        return "Listen click does not require speech to have started before Stop"
    if not _R119_BAR.search(src):
        return "iPhone/iPad path does not show Tap to listen before speech has started"
    if "Tap to listen" not in src:
        return "Tap to listen label is missing"
    if "start(true)" not in src:
        return "desktop auto-start on load is missing"
    return ""

def _page_listen_block(text):
    a = text.find("<!-- ph-page-listen:start -->")
    b = text.find("<!-- ph-page-listen:end -->", a if a >= 0 else 0)
    if a < 0 or b < 0: return ""
    return text[a:b]

def listen_iphone_tree_problems(repo):
    """R119 problems in the shared script and every inlined v2 / autoplay listen page. R10 pages are skipped."""
    import os as _os
    repo = str(repo)
    probs = []
    shared = _os.path.join(repo, "scripts", "page_listen_v2.html")
    why = listen_page_iphone_problem(open(shared, encoding="utf-8").read())
    if why: probs.append("scripts/page_listen_v2.html: " + why)
    pages = _os.path.join(repo, "pages")
    for dp, _, fs in _os.walk(pages):
        for name in fs:
            if not name.endswith(".html"): continue
            path = _os.path.join(dp, name)
            rel = _os.path.relpath(path, repo).replace("\\", "/")
            if rel in R10_LOCKED_SHA256: continue
            text = open(path, encoding="utf-8", errors="ignore").read()
            block = _page_listen_block(text)
            auto = 'data-ph-autoplay="1"' in text
            if not auto and 'data-ph-listen-v="2"' not in block: continue
            why = listen_page_iphone_problem(block or text)
            if why: probs.append(rel + ": " + why)
    return probs


# R104b (Steven, Nov 12 2026): an empty Chair Reports section keeps its heading and one placeholder line.
CHAIR_NO_REPORTS = "No reports this week."

def chair_empty_section_problem(html, has_current_reports):
    """R104b. '' when the Chair Reports section matches the rule; else why it fails.
    has_current_reports True: reports are in the 30-day window, so the placeholder must be absent.
    has_current_reports False: the heading, the placeholder line, and the archives link must be present,
    and no Read Full Report card."""
    if not html:
        return "no html"
    has_heading = ">Committee Chair Reports</span>" in html
    has_placeholder = CHAIR_NO_REPORTS in html
    has_full = ">Read Full Report →</a>" in html
    has_arch = ">Committee Report Archives →</a>" in html
    if has_current_reports:
        if has_placeholder:
            return "placeholder shown while a current chair report is in the 30-day window"
        return ""
    if not has_heading:
        return "Committee Chair Reports heading is missing (the empty section was hidden)"
    if not has_placeholder:
        return "empty Chair Reports section has no 'No reports this week.' line"
    if has_full:
        return "empty Chair Reports section still has a Read Full Report card"
    if not has_arch:
        return "Committee Report Archives → link is missing from the empty Chair Reports section"
    return ""


# R122 (Steven, Nov 12 2026): club calendar always supersedes the RPM calendar.
_MON3 = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
_FULLM = ("January","February","March","April","May","June","July","August","September","October","November","December")

def _r122_key(name):
    n = re.sub(r"\s+", " ", _h.unescape(name or "")).strip().casefold()
    n = re.sub(r"\s+meeting$", "", n)
    n = n.replace("committee", " ").replace("of directors", " board ").replace("board of directors", "board")
    n = re.sub(r"\s+", " ", n).strip()
    if "board" in n and "direct" in (name or "").casefold():
        return "board"
    if n.startswith("board"):
        return "board"
    if "communication" in n:
        return "communications"
    return n

def _r122_date_phrases(iso):
    """Visible date forms a meetings row might use for YYYY-MM-DD."""
    if not iso or len(str(iso)) < 10:
        return []
    y, m, d = str(iso)[:10].split("-")
    m, d = int(m), int(d)
    return [
        f"{_FULLM[m-1]} {d}, {y}",
        f"{_FULLM[m-1]} {d}",
        f"{_MON3[m-1]} {d}, {y}",
        f"{_MON3[m-1]} {d}",
        f"{m}/{d}/{y}",
        f"{m}/{d}",
    ]

def _r122_time_phrases(start):
    """Visible time forms for '13:00' / '09:00' / '1:00 PM'."""
    if not start:
        return []
    s = str(start).strip()
    if re.search(r"(?i)[ap]m", s):
        return [s]
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        return [s]
    h, mi = int(m.group(1)), m.group(2)
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return [f"{h12}:{mi} {ampm}", f"{h12}:{mi}{ampm}", f"{h:02d}:{mi}"]

def _r122_meeting_row(html, name):
    """Slice of the Meetings section starting at this meeting's bold title, through the next title or end."""
    key = _r122_key(name)
    sec = html
    h = sec.find(">Committee &amp; Board Meeting Schedules</span>")
    if h < 0:
        h = sec.find(">Committee & Board Meeting Schedules</span>")
    if h >= 0:
        nxt = [x for x in (sec.find('<div class="canonical-section">', h + 10), sec.find('<div class="section04">', h + 10)) if x > 0]
        sec = sec[h:(min(nxt) if nxt else len(sec))]
    for m in re.finditer(r'font-weight:bold;color:#333333;text-align:left;[^>]*>([^<]+)<', sec):
        title = _h.unescape(m.group(1)).strip()
        if _r122_key(title) == key:
            rest = sec[m.start():]
            nxt = re.search(r'font-weight:bold;color:#333333;text-align:left;[^>]*>([^<]+)<', rest[m.end()-m.start():])
            return rest[: (m.end()-m.start() + nxt.start())] if nxt else rest
    return ""

def club_calendar_supersedes_rpm_problems(html, club_meetings, rpm_meetings, overrides=None, notes=None):
    """R122. Return a list of problems when a draft uses an RPM date that conflicts with the club calendar,
    or when MTG_OVERRIDE / MTG_NOTE would apply such a date. club_meetings / rpm_meetings are dicts with
    name, date (YYYY-MM-DD), optional time, optional status. Only CONFIRMED (or unstated) club rows rule;
    RESCHEDULED club rows are not the source of truth."""
    problems = []
    club_by = {}
    for e in club_meetings or []:
        st = (e.get("status") or "CONFIRMED").upper()
        if st and st != "CONFIRMED":
            continue
        k = _r122_key(e.get("name") or e.get("title") or "")
        if not k or not e.get("date"):
            continue
        club_by.setdefault(k, []).append(e)
    rpm_by = {}
    for e in rpm_meetings or []:
        k = _r122_key(e.get("name") or e.get("title") or e.get("committee") or "")
        if not k or not e.get("date"):
            continue
        rpm_by.setdefault(k, []).append(e)

    def _iso(v):
        return str(v)[:10] if v else ""

    def _conflicts(club_list, rpm_list):
        out = []
        for r in rpm_list:
            rd = _iso(r.get("date"))
            if rd and all(_iso(c.get("date")) != rd for c in club_list):
                out.append(r)
        return out

    for k, clubs in club_by.items():
        rpms = rpm_by.get(k) or []
        bad = _conflicts(clubs, rpms)
        if not bad:
            continue
        # Overrides / notes must not adopt a conflicting RPM date.
        for label, blob in (("MTG_OVERRIDE", overrides), ("MTG_NOTE", notes)):
            if not blob:
                continue
            text = blob if isinstance(blob, str) else str(blob)
            text_l = text.casefold()
            if k not in text_l and not any(_r122_key(str(x)) == k for x in (blob.keys() if isinstance(blob, dict) else [])):
                # still scan values
                pass
            for r in bad:
                for phr in _r122_date_phrases(r.get("date")):
                    if phr in text or phr.replace(",", "") in text:
                        # only flag if the club date is not the one being applied exclusively...
                        problems.append(f"{label} uses RPM date {phr} for {k}, which conflicts with the club calendar")
                        break
        # Rendered meetings row must show a club date, not the conflicting RPM date.
        if html:
            # Use the first club meeting's name for row lookup; also try common titles.
            names = [clubs[0].get("name") or k] + [c.get("name") for c in clubs if c.get("name")]
            row = ""
            for n in names:
                row = _r122_meeting_row(html, n)
                if row:
                    break
            if not row:
                continue  # not printed in this issue's Meetings window
            # club date present
            if not any(any(p in row for p in _r122_date_phrases(c.get("date"))) for c in clubs):
                problems.append(f"{names[0]} row does not show the club calendar date")
            for r in bad:
                phrases = _r122_date_phrases(r.get("date"))
                if any(p in row for p in phrases):
                    problems.append(f"{names[0]} row shows RPM date {r.get('date')}, which conflicts with the club calendar")
    # Overrides that name a committee and an RPM-only date even when the meeting is not on the page
    if overrides:
        items = overrides.items() if isinstance(overrides, dict) else []
        for name, val in items:
            k = _r122_key(name)
            clubs = club_by.get(k) or []
            rpms = rpm_by.get(k) or []
            if not clubs or not rpms:
                continue
            text = str(val)
            for r in _conflicts(clubs, rpms):
                if any(p in text for p in _r122_date_phrases(r.get("date"))):
                    if not any(p in text for p in _r122_date_phrases(clubs[0].get("date"))):
                        msg = f"MTG_OVERRIDE for {name} uses RPM date {r.get('date')}, which conflicts with the club calendar"
                        if msg not in problems:
                            problems.append(msg)
    # unique
    out = []
    for p in problems:
        if p not in out:
            out.append(p)
    return out


# R124 (Steven, Nov 13 2026: "Let's combine the individual dates for the 9 day cruise to a range"). A multi-day event is a
# title whose every CONFIRMED calendar occurrence at the same place falls on back-to-back days (one unbroken run of 2+ days,
# one row per day). Calendar-list pages show it as ONE row with a date range instead of a row per day. Weekly or weekday
# series (Tennis, Billiards) have gaps, so they are never collapsed.
def _mday_key(e):
    return (e.get("name", ""), e.get("venue", ""), e.get("place", ""))

def multiday_runs(events):
    """{(name, venue, place): {name, start, end, days, first_start}} for every multi-day run in the calendar feed."""
    from datetime import date as _d, timedelta as _td
    g = {}
    for e in events:
        if e.get("status") != "CONFIRMED" or reserved_only_name(e.get("name")): continue
        g.setdefault(_mday_key(e), []).append(e)
    out = {}
    for k, v in g.items():
        ds = sorted({e["date"] for e in v})
        if len(ds) < 2 or len(ds) != len(v): continue
        dd = [_d.fromisoformat(x) for x in ds]
        if all(b - a == _td(days=1) for a, b in zip(dd, dd[1:])):
            first = min(v, key=lambda e: e["date"])
            out[k] = {"name": k[0], "start": ds[0], "end": ds[-1], "days": len(ds), "first_start": first.get("start")}
    return out

def range_label(start_iso, end_iso):
    """'Monday, Dec 7 – Wednesday, Dec 16, 2026' (start year shown only when the range crosses a year)."""
    from datetime import date as _d
    a, b = _d.fromisoformat(start_iso), _d.fromisoformat(end_iso)
    left = f"{a:%A}, {MON3[a.month-1]} {a.day}" + (f", {a.year}" if a.year != b.year else "")
    return f"{left} \u2013 {b:%A}, {MON3[b.month-1]} {b.day}, {b.year}"

def collapse_multiday(rows, events):
    """Keep the first (earliest) row of each multi-day run, tagged with range_start/range_end/range_first_start; drop the rest.
    The range is the full run in the calendar feed, not clipped to the page window."""
    runs = multiday_runs(events); seen = set(); out = []
    for e in sorted(rows, key=lambda x: (x["date"], x.get("start") or "99:99")):
        k = _mday_key(e)
        if k in runs:
            if k in seen: continue
            seen.add(k); r = runs[k]
            e = dict(e, range_start=r["start"], range_end=r["end"], range_first_start=r["first_start"])
        out.append(e)
    return out  # caller re-sorts for each view

def _mon3_norm(s):
    return re.sub(r"\b(" + "|".join(FULL) + r")\b", lambda m: MON3[FULL.index(m.group(1))], s)

def multiday_range_problems(page_html, events, window):
    """R124 guard on one calendar-list page: each multi-day run that overlaps the page window and is listed on the page must be
    one row (title once; By Name group count (1)) and must show its date range."""
    txt = _mon3_norm(_h.unescape(page_html)); out = []
    for k, r in multiday_runs(events).items():
        if r["end"] < window[0] or r["start"] > window[1]: continue
        t = r["name"]
        if t not in txt: continue
        n = txt.count(t)
        grp = re.search(re.escape(t) + r'<span class="n">\((\d+)\)', txt)
        if grp and grp.group(1) != "1": out.append(f"{t}: By Name group shows ({grp.group(1)}) rows, expected one range row")
        elif not grp and n != 1: out.append(f"{t}: listed {n} times, expected one range row")
        lab = range_label(r["start"], r["end"]); short = re.sub(r", \d{4}$", "", lab)
        if lab not in txt and short not in txt: out.append(f"{t}: date range '{short}' missing")
    return out


# STYLE-RULES R126 (Steven, Nov 13 2026 9:16 PM ET, voice): a Rules Did You Know has a plain-language
# summary intro with key highlights, then the official regulation text exactly once. A contributor
# closing note stays verbatim once after the regulation, next to the Rules PDF link, and is not
# merged into the summary. The same substantial paragraph must not be printed twice in a DYK or
# notice body (the Nov 15 Rule VI.G page had Dave's email quote of G. and the official blockquote).
_R126_MIN = 80  # characters, after normalize; short repeated labels are not a repeat

def _r126_plain(t):
    t = _h.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    t = re.sub(r"\s+", " ", t).strip().lower()
    return re.sub(r"^[a-z]\.\s+", "", t)

def _r126_blocks(html):
    """Visible block texts from a DYK/notice body (content card or main), skipping bylines, sources, nav, scripts."""
    s = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", html or "", flags=re.I)
    m = re.search(r'<div class="content-card">([\s\S]*?)</div>', s)
    if not m:
        m = re.search(r"<main\b[^>]*>([\s\S]*?)</main>", s, re.I)
    body = m.group(1) if m else s
    body = re.sub(r'<p class="(?:dyk-byline|source|ph-source|credit|byline)"[^>]*>[\s\S]*?</p>', " ", body, flags=re.I)
    body = re.sub(r"<nav\b[\s\S]*?</nav>", " ", body, flags=re.I)
    chunks = re.findall(r"<(?:p|li|h[1-6]|div class=\"ph-detail\")\b[^>]*>([\s\S]*?)</(?:p|li|h[1-6]|div)>", body, re.I)
    out = []
    for c in chunks:
        n = _r126_plain(c)
        if n:
            out.append(n)
    return out

def repeated_regulation_problems(html):
    """Non-empty list if a DYK/notice body prints the same substantial paragraph (or lettered rule) twice."""
    blocks = _r126_blocks(html)
    seen = {}
    problems = []
    for b in blocks:
        if len(b) < _R126_MIN:
            continue
        if b in seen:
            problems.append(f"repeated paragraph ({len(b)} chars): {b[:80]}…")
        else:
            seen[b] = 1
    return problems

def rules_dyk_intro_facts_ok(intro, highlights, rule_text):
    """Numbers, money, and Paragraph references in the intro/highlights must appear in the official rule (no invented facts)."""
    src = rule_text or ""
    blob = " ".join([intro or ""] + [
        (h[0] + " " + h[1]) if isinstance(h, (list, tuple)) and len(h) >= 2 else str(h)
        for h in (highlights or [])
    ])
    facts = re.findall(r"\$\d+(?:\.\d+)?|\bParagraph\s+\d+\b|\b\d+\s+hour\b|\b\d+\s+hours\b", blob, re.I)
    missing = [f for f in facts if f.lower() not in src.lower() and re.sub(r"\s+", " ", f.lower()) not in re.sub(r"\s+", " ", src.lower())]
    # "$50" should match "$50 per hour" in the rule
    missing = [f for f in missing if f.lstrip("$") not in re.sub(r"[^\d.]", " ", src)]
    return not missing, missing

def rules_dyk_r126_parts(item):
    """Card inner HTML (intro, highlight list, official rule once, byline) and the after-card closing note (if any)."""
    import html as _html
    intro = (item.get("intro") or "").strip()
    highlights = item.get("highlights") or []
    if not intro or not highlights or not item.get("rule_items"):
        raise ValueError("R126: item needs intro, highlights, and rule_items")
    rule_src = " ".join(t for _, t in item["rule_items"])
    ok, missing = rules_dyk_intro_facts_ok(intro, highlights, rule_src)
    if not ok:
        raise ValueError(f"R126: intro/highlights have facts not in the official rule: {missing}")
    rp = _html.escape(item["rule_pdf"])
    lis = []
    for h in highlights:
        lead, rest = (h[0], h[1]) if isinstance(h, (list, tuple)) and len(h) >= 2 else ("", str(h))
        lis.append(f'<li style="margin:0 0 8px 0"><strong>{_html.escape(lead)}:</strong> {_html.escape(rest)}</li>')
    card = (
        f'<p class="dyk-rule-intro">{_html.escape(intro)}</p>'
        + '<ul class="dyk-rule-highlights" style="margin:12px 0 16px 1.2em;padding:0">' + "".join(lis) + "</ul>"
        + '<blockquote class="dyk-full-rule" style="border-left:4px solid #2d5016;background:#f3f8ee;padding:12px 16px;margin:16px 0">'
        + f'<p style="margin:0 0 8px 0;"><strong><a class="dyk-rule-heading" href="{rp}" style="color:#3A6B1A">{_html.escape(item["rule_heading"])}</a></strong></p>'
        + "".join(f'<p style="margin:0;"><strong>{_html.escape(l)}</strong> {_html.escape(txt)}</p>' for l, txt in item["rule_items"])
        + "</blockquote>"
        + f'<p class="dyk-byline">{_html.escape(item["byline"])}</p>'
    )
    note = (item.get("closing_note") or "").strip()
    after = ""
    if note:
        # Keep the note verbatim; only turn "the full document" into the official PDF link (same as the prior page).
        linked = _html.escape(note).replace("the full document", f'<a href="{rp}" style="color:#3A6B1A">the full document</a>', 1)
        after = f'<p class="source dyk-dave-note">{linked}</p>\n'
    return card, after

def rules_dyk_r126_problems(html, item):
    """'' when the page matches R126 (intro, highlights, official rule once, optional note once). Else a reason."""
    if not item.get("intro") or not item.get("rule_items"):
        return ""
    reps = repeated_regulation_problems(html)
    if reps:
        return "; ".join(reps)
    rule = _r126_plain(" ".join(t for _, t in item["rule_items"]))
    body = _r126_plain(html)
    if rule and body.count(rule) != 1:
        return f"official rule text appears {body.count(rule)} time(s), want 1"
    if _r126_plain(item["intro"]) not in body:
        return "summary intro is missing"
    for h in item.get("highlights") or []:
        rest = h[1] if isinstance(h, (list, tuple)) and len(h) >= 2 else str(h)
        if _r126_plain(rest) not in body:
            return f"highlight missing: {rest[:60]}"
    note = (item.get("closing_note") or "").strip()
    if note:
        n = _r126_plain(note)
        if body.count(n) != 1:
            return f"closing note appears {body.count(n)} time(s), want 1"
        # The note must sit after the official rule and next to the PDF link, not in the intro.
        intro_html = re.search(r'class="dyk-rule-intro"[^>]*>([\s\S]*?)</p>', html or "")
        if intro_html and _r126_plain(note) in _r126_plain(intro_html.group(1)):
            return "closing note must not be merged into the summary intro"
        if "dyk-dave-note" not in (html or "") or "dyk-rules-link" not in (html or ""):
            return "closing note and Rules PDF link must both be present after the regulation"
    return ""


# ---------------------------------------------------------------------------
# R127 / R128 (Steven, Nov 14 2026): the archive lists only shipped issues;
# the current week's issue is added the following week, after it has been sent.
# Source of truth: archive/sent-issues.json (status=shipped).
# R129 (Steven, Nov 14 2026): no faint white seam lines in the green masthead
# on either side of the "Palm Hill Country Club" title.
# ---------------------------------------------------------------------------
import json as _json
from pathlib import Path as _Path

SENT_ISSUES_REL = "archive/sent-issues.json"
ARCHIVE_ITEMS_REL = "archive/archive-items.json"
ARCHIVE_INDEX_REL = "pages/archive/archive-index.json"
ARCHIVE_HOME_REL = "pages/archive/index.html"
MASTHEAD_GREEN = "#2D5016"
MASTHEAD_PALM_PX = 100
MASTHEAD_PALM_MOBILE_PX = 60
# The 50%+50%+1% column widths cannot add up, and many email clients then
# show a 1px gap (the pale card background) on each side of the title.
MASTHEAD_BAD_PALM_CSS = re.compile(r"\.header-palm-cell\s*\{\s*width:\s*50%\s*!important\s*;\s*\}")
MASTHEAD_BAD_PALM_TD = re.compile(
    r'<td class="header-palm-cell" width="50%" align="center" valign="middle" bgcolor="#2D5016" style="width:50%;height:105px;background:#2D5016;">'
)
MASTHEAD_BAD_TITLE_TD = re.compile(
    r'<td width="1%" align="center" valign="middle" bgcolor="#2D5016" style="width:1%;white-space:nowrap;height:105px;background:#2D5016;color:#ffffff;text-align:center;">'
)


def _repo_root(repo=None):
    if repo: return _Path(repo)
    return _Path(__file__).resolve().parents[1]


def load_sent_issues(repo=None):
    """Return the shipped-issue records from archive/sent-issues.json."""
    p = _repo_root(repo) / SENT_ISSUES_REL
    data = _json.loads(p.read_text(encoding="utf-8"))
    return [i for i in data.get("issues", []) if i.get("status", "shipped") == "shipped"]


def load_known_sent_unconfirmed(repo=None):
    p = _repo_root(repo) / SENT_ISSUES_REL
    data = _json.loads(p.read_text(encoding="utf-8"))
    return [i for i in data.get("issues", []) if i.get("status") == "sent-copy-unconfirmed"]


def archive_listed_dates(repo=None):
    """Issue dates listed on the published archive index (JSON + home page + curated items)."""
    root = _repo_root(repo)
    dates = set()
    items = root / ARCHIVE_ITEMS_REL
    if items.exists():
        data = _json.loads(items.read_text(encoding="utf-8"))
        for i in data.get("issues", []):
            if i.get("date"): dates.add(i["date"])
    idx = root / ARCHIVE_INDEX_REL
    if idx.exists():
        data = _json.loads(idx.read_text(encoding="utf-8"))
        for i in data.get("issues", []):
            if i.get("date"): dates.add(i["date"])
    home = root / ARCHIVE_HOME_REL
    if home.exists():
        t = home.read_text(encoding="utf-8")
        dates.update(re.findall(r"archive/issues/(\d{4}-\d{2}-\d{2})\.html", t))
        dates.update(re.findall(r'href="issues/(\d{4}-\d{2}-\d{2})\.html"', t))
    return dates


def archive_unsent_or_current_week_problems(repo=None, current=None):
    """R127: fail if the archive index lists an unsent issue, or one dated the current week or later."""
    root = _repo_root(repo)
    current = current or current_issue(root)
    shipped = {i["date"] for i in load_sent_issues(root)}
    hits = []
    for d in sorted(archive_listed_dates(root), reverse=True):
        if d not in shipped:
            hits.append(f"{d} is in the archive index but is not marked shipped in {SENT_ISSUES_REL}")
        if d >= current:
            hits.append(f"{d} is in the archive index but is the current week's issue or later ({current}); add it the following week, after it has been sent")
    return hits


def archive_missing_sent_problems(repo=None, current=None):
    """R128: fail if a shipped issue older than the current week is missing from the archive index or has no frozen page."""
    root = _repo_root(repo)
    current = current or current_issue(root)
    listed = archive_listed_dates(root)
    hits = []
    for i in load_sent_issues(root):
        d = i["date"]
        if d >= current:
            continue  # R127: do not require (or allow) the current week in the archive yet
        if d not in listed:
            hits.append(f"{d} (Vol. {i.get('volume')}, No. {i.get('number')}) is shipped but missing from the archive index")
        page = root / "pages" / "archive" / "issues" / f"{d}.html"
        if not page.exists():
            hits.append(f"{d}: frozen archive issue page pages/archive/issues/{d}.html is missing")
    return hits


def fix_masthead_seams(html):
    """R129: rewrite the 3-cell green masthead so palm columns use a fixed pixel width (not 50%+50%+1%)."""
    if not html or "header-palm-cell" not in html:
        return html
    html = MASTHEAD_BAD_PALM_CSS.sub(
        f".header-palm-cell {{ width:{MASTHEAD_PALM_MOBILE_PX}px !important; }}",
        html,
        count=1,
    )
    html = re.sub(
        r'(<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;)(background:#2D5016;">)',
        r"\1border-spacing:0;\2",
        html,
        count=1,
    )
    palm_open = (
        f'<td class="header-palm-cell" width="{MASTHEAD_PALM_PX}" align="center" valign="middle" bgcolor="#2D5016" '
        f'style="width:{MASTHEAD_PALM_PX}px;height:105px;background:#2D5016;padding:0;border:0;font-size:0;line-height:0;">'
    )
    html = MASTHEAD_BAD_PALM_TD.sub(palm_open, html)
    html = MASTHEAD_BAD_TITLE_TD.sub(
        '<td align="center" valign="middle" bgcolor="#2D5016" style="white-space:nowrap;height:105px;background:#2D5016;color:#ffffff;text-align:center;padding:0 8px;">',
        html,
        count=1,
    )
    return html


def masthead_seam_problems(html):
    """R129: the preview/SEND masthead must not use the 50%+50%+1% column widths that leave white seams."""
    if not html or "header-palm-cell" not in html:
        return []
    hits = []
    if MASTHEAD_BAD_PALM_CSS.search(html) or re.search(r"\.header-palm-cell\s*\{[^}]*width:\s*50%\s*!important", html):
        hits.append("mobile CSS sets .header-palm-cell { width:50% !important }")
    for td in re.findall(r"<td class=\"header-palm-cell\"[^>]*>", html):
        if re.search(r'width="50%"|width:\s*50%', td) or re.search(r'width="\d+%"|width:\s*\d+%', td):
            hits.append("a palm cell uses a percentage width (must be a fixed pixel width)")
            break
    if MASTHEAD_BAD_TITLE_TD.search(html) or re.search(r'<td width="1%"[^>]*>[^<]*<span class="header-title"', html):
        hits.append("the title cell uses width 1% next to two 50% palm cells")
    return hits
