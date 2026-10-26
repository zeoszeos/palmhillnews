# Oct 25 clone of locked_checks_oct18.py (issue date / Vol-No expectations moved; rules unchanged)
"""PHNEWS Oct 11, 2026 — fail-closed LOCK checks (poka-yoke). Steven, Oct 9, 2026 (~8:30 PM ET).

Every rule here mirrors one line of ../LOCKED-RULES.md (same L-ids). build_oct11_final.py calls
check_email(page) BEFORE it writes anything; any FAIL -> exit 2, nothing in out/ is touched, and the
Omen preview must NOT be refreshed (no PREVIEW-OK.json is written).

To change a locked decision on purpose: edit LOCKED-RULES.md AND the matching check here in the same
change, with Steven's OK and the date. Never delete a check to make a build pass.

These are read-only string/structure checks. They never modify the page.
"""
import os as _os, sys as _sys; _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent)); import issue_ctx as _ix; C = _ix.load()  # R71 content file
import re
from pathlib import Path

WHITE = '-webkit-text-fill-color:#FFFFFF;">'
SECTION_ORDER = [  # L03 (Events - This Week omitted when empty per L07, Oct 11 ~1:00 PM ET)
    "Committee &amp; Board Meeting Schedules", "Committee Chair Reports", "Events - This Week",
    "Recurring Meetings &amp; Events", "Community Notices", "Events - Upcoming",
    "Community Stories", "From the Board President", "Did You Know?", "Residents Reference Guide"]
SECTION_ORDER_NO_THIS_WEEK = [h for h in SECTION_ORDER if h != "Events - This Week"]
MEETINGS_EXPECTED = []  # Oct 18: run_checks.py fills Meetings / This Week / Upcoming from build-audit-oct18.json (calendar pull)
THIS_WEEK_EXPECTED = []  # L07 (Oct 11 ~10:09 AM ET, Steven item 13: Karaoke Obi-Time moved to Recurring -> This Week empty for Oct 11)
UPCOMING_EXPECTED = []  # filled by run_checks.py from build-audit-oct18.json
TREAT_AS_RECURRING = ["Hand and Foot Cards", "Ukulele Group", "Ear Wax Removal", "I Got It", "Karaoke Obi-Time", "Writing Club"]  # A3 (Oct 24): + Writing Club; run_checks asserts this equals core build_core/recurring AS_RECURRING  # + Karaoke Obi-Time (Steven, Oct 11 ~10:09 AM ET, Tony item 13)
# L09/L19 (I Got It all dates, Steven Oct 9 ~8:35 PM; on Recurring pages ~8:45 PM)
NOTICES_EXPECTED = None  # R71 (batch 5): L11 list lives in the issue content file LOCKED (in order)
CHAIR_EXPECTED = None    # R71 (batch 5): L13 title -> intro lives in the issue content file LOCKED
FULL_MONTHS = ("January","February","March","April","May","June","July","August","September","October","November","December")
# L21 CODE POLICY M3 (Steven, Oct 9, 2026 ~8:57 PM ET): every user-visible month is 3 letters. "May" is already 3 letters.
FULL_MONTH_RE = re.compile(r'\b(January|February|March|April|June|July|August|September|October|November|December)\b')
BASE = "https://palmhillnews.vercel.app/pages/"
RIGHT_LOC_TD = '<td valign="top" align="right" style="font-size:14px;color:#666666;text-align:right;padding-top:1px;">'


class Locks:
    def __init__(self): self.results = []
    def ok(self, lid, cond, msg):
        self.results.append((lid, "PASS" if cond else "FAIL", msg)); return cond
    def warn(self, lid, msg): self.results.append((lid, "WARN", msg))
    @property
    def failed(self): return [r for r in self.results if r[1] == "FAIL"]
    def report(self):
        return "\n".join(f"  [{s}] {l}: {m}" for l, s, m in self.results)


def _headings(page):
    return [(m.start(), m.group(1)) for m in re.finditer(re.escape(WHITE) + r'([^<]+)</span>', page)]

def _section(page, title):
    hs = _headings(page)
    for i, (pos, t) in enumerate(hs):
        if t == title:
            end = hs[i + 1][0] if i + 1 < len(hs) else len(page)
            return page[pos:end]
    return ""

def _row_titles_mtg(sec):
    return re.findall(r'<td valign="top" align="left" style="font-size:15px;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">([^<]+)</td>', sec)

def _row_titles_plain(sec):
    return re.findall(r'<div style="font-size:15px;font-weight:bold;color:#333333;">([^<]+)</div>', sec)


def check_email(page):
    L = Locks()
    # L01 Vol/No left of the address, build time right of it
    L.ok("L01", page.count('<span class="header-time header-volno"') == 1 and
         re.search(r'header-volno"[^>]*>' + re.escape(C.VOLNO) + r'</span></td><td align="center"[^>]*><span class="address-text"[^>]*>1800 Seminole Blvd, Largo, FL 33778</span></td><td width="80" align="right"[^>]*><span class="header-time"[^>]*>\d{1,2}:\d{2} (AM|PM)</span>', page) is not None,
         f"address bar = [{C.VOLNO}] [1800 Seminole Blvd…] [build time h:mm AM/PM]")
    # L02 issue date + masthead palm
    L.ok("L02", page.count('>' + C.ISSUE_LONG + '</span>') == 1 and '>October 4, 2026</span>' not in page and '>Oct 4, 2026</span>' not in page
         and page.count('masthead-palm-hd-320x334-v1.png') == 2, "issue date Oct 11, 2026 (L21 3-letter month); HD palm x2")
    # L03 section order (This Week omitted when empty — L07, Steven Oct 11 ~1:00 PM ET)
    got = [t for _, t in _headings(page)]
    expect = SECTION_ORDER if THIS_WEEK_EXPECTED else SECTION_ORDER_NO_THIS_WEEK
    L.ok("L03", got == expect, f"section order {got}")
    # L03b replaced by R45 (Steven, Oct 18 12:07 AM): the Oct 11 omission was never approved; a story row is required
    import sys as _s; _s.path.insert(0, __import__("os").path.join(__import__("os").environ.get("PHNEWS_REPO") or str(C.DEFAULT_REPO), "scripts")); import style_rules as _sr45
    L.ok("L03b", not _sr45.community_stories_violations(page), f"R45 Community Stories section {_sr45.community_stories_violations(page) or 'present'}")
    # L04 hard exclusions
    for bad in ("Block Captain", "Test Meeting", "Private Event", "Message from Board President Henry Klain",
                "Real Estate Committee Report", "Rules and Regulations Committee Report"):
        L.ok("L04", bad not in page, f'"{bad}" absent')
    # L05/L06 Meetings
    sec = _section(page, "Committee &amp; Board Meeting Schedules")
    names = _row_titles_mtg(sec)
    L.ok("L05", names == MEETINGS_EXPECTED, f"Meetings rows {names}")
    L.ok("L05b", len(names) == len(set(names)), "one meeting per committee")
    L.ok("L05c", "PH Ladies Golf Assoc" not in sec, "PH Ladies Golf Assoc not in Meetings")
    # L26 (Steven, Oct 10 ~1:40 PM ET): Meetings window inside green header (italic), like This Week / Upcoming.
    # L26b (Steven, Oct 10 ~2:50 PM ET): Recurring email section also date-in-header (no "Recurring activities," lead).
    L.ok("L26", "Oct 11 through Nov 10" in sec and  # Oct 11-era lock; R78 (Nov 1 on) drops the Meetings range, see run_checks.py
         'font-style:italic;color:#FFFFFF;margin-top:3px;">Oct 11 through Nov 10</div>' in page,
         "Meetings: Oct 11 through Nov 10 inside green header (italic subtitle)")
    L.ok("L06", sec.count(RIGHT_LOC_TD) == len(MEETINGS_EXPECTED), "Meetings: location right-aligned on title line, every row")
    L.ok("L06b", sec.count('(also on Zoom and Community Channel)') == 1 and sec.count('(also on Zoom and Channel 732)') == 1,
         "Zoom suffix right-aligned under location (Comms, Golf)")
    L.ok("L06c", sec.count('>View Meeting Agenda →</a>') == 2 and sec.count('>Join on Zoom →</a>') == 2,
         "one agenda/Zoom link line per meeting with a notice (Comms, Golf)")
    # L07 This Week — omit entire section when empty (Steven, Oct 11 ~1:00 PM ET)
    sec = _section(page, "Events - This Week")
    names = _row_titles_plain(sec) + _row_titles_mtg(sec)
    if not THIS_WEEK_EXPECTED:
        L.ok("L07", "Events - This Week" not in page and not sec and "No one-time events this week" not in page,
             "This Week omitted when empty (no header, no empty message)")
        L.ok("L07b", True, "This Week layout N/A when section omitted")
    else:
        L.ok("L07", names == THIS_WEEK_EXPECTED and "Oct 11 through Oct 17" in sec, f"This Week rows {names}")
        L.ok("L07b", sec.count(RIGHT_LOC_TD) == len(THIS_WEEK_EXPECTED) and not _row_titles_plain(sec),
             "This Week: location right-aligned on title line, every row (Steven, Oct 10)")
    # L08/L09/L10 Upcoming
    sec = _section(page, "Events - Upcoming")
    names = _row_titles_mtg(sec)
    L.ok("L08", "Oct 18 through Nov 8" in sec, "Upcoming window Oct 18 – Nov 8")
    L.ok("L08b", names == UPCOMING_EXPECTED, f"Upcoming rows {names}")
    for n in TREAT_AS_RECURRING + ["PH Ladies Golf Assoc"]:
        L.ok("L09", n not in sec, f'Upcoming excludes "{n}"')
    L.ok("L09b", "I Got It" not in names and "I Got It" not in sec, "I Got It: never in Upcoming (treated as recurring, all dates)")
    tw = _section(page, "Events - This Week")
    L.ok("L09c", "I Got It" not in tw, "I Got It: never in This Week")
    for n in TREAT_AS_RECURRING:
        L.ok("L09d", n not in tw, f'This Week excludes "{n}"')
    L.ok("L10", sec.count(RIGHT_LOC_TD) == len(UPCOMING_EXPECTED) and not _row_titles_plain(sec),
         "Upcoming: location right-aligned on title line, every row")
    # L11 Community Notices
    sec = _section(page, "Community Notices")
    names = _row_titles_plain(sec)
    L.ok("L11", names == NOTICES_EXPECTED and "From the Board President" not in sec, f"Notices rows {names}")
    # L12 From the Board President = own section
    sec = _section(page, "From the Board President")
    L.ok("L12", page.count('>From the Board President</span>') == 1 and page.count('>From the Board President</div>') == 0
         and "Henry Klain&#x27;s Oct 4 Status Update is still available to read or hear." in sec
         and "Source: Henry Klain, Board President, Oct 4 issue" in sec, "Board President section text + source")
    for t, u in (("Read Full Message →", "2026-10-04-henry-klain-status-update.html"),
                 ("Listen to the Message →", "2026-10-04-listen-henry-klain-message.html"),
                 ("President's Message Archives →", "archive/presidents-message.html")):
        L.ok("L12b", page.count(BASE + u) == 1 and f'href="{BASE + u}"' in sec and f'>{t}</a>' in sec, f"Board President link {t}")
    # L13–L16 Chair reports
    sec = _section(page, "Committee Chair Reports")
    titles = re.findall(r'font-weight:bold;color:#333333;text-align:left;padding-right:8px;">([^<]+)</td>', sec)
    L.ok("L13", titles == list(CHAIR_EXPECTED), f"chair rows {titles} (August reports off email)")
    for t, intro in CHAIR_EXPECTED.items():
        L.ok("L13b", intro.replace("&", "&amp;") in sec or intro in sec, f"2-line intro: {t}")
    dates = re.findall(r'<div style="font-size:14px;color:#666666;margin-top:2px;">([^<]+)</div>', sec)
    L.ok("L14", len(dates) == 3 and not any(re.search(r'\b(' + "|".join(FULL_MONTHS) + r')\b', d) for d in dates),
         f"3-letter months in chair dates {dates}")
    L.ok("L15", sec.count('>Listen</a>') == 3 and "Listen to the Chair Report" not in sec
         and sec.count('width="24" height="24"') == 3 and 'width="32"' not in sec
         and sec.count('text-align:right;white-space:nowrap;width:1%;"><a href="' + BASE) == 3,
         'Listen = 24px speaker + "Listen" only, right of chair title (nowrap)')
    L.ok("L16", sec.count('>Read Full Report →</a>') == 3 and "Read Full Details" not in sec, "Read Full Report → under each intro")
    # L17 Recurring
    sec = _section(page, "Recurring Meetings &amp; Events")
    L.ok("L17", "Oct 11 through Nov 9, 2026" in sec and sec.count(BASE + "2026-10-11-recurring-activities-by-") == 3  # L17 amended Oct 11 ~10:09 AM ET: By Date · By Name · By Location
         and sec.count(BASE + "2026-10-11-recurring-activities-by-location.html") == 1
         and "Source: <a href=\"https://www.palmhillcountryclub.net/calendar-1/\" style=\"color:#3A6B1A;\">Calendar</a>" in sec
         and "2026-10-04-recurring-activities" not in page and "confirmed recurring" not in sec.lower(),
         "Recurring = links only, Oct 11 – Nov 9 pages; no \"confirmed\" wording (L20)")
    # L26b (Steven, Oct 10 ~2:50 PM ET): Recurring date window INSIDE green bar (italic), date-only — no
    # "Recurring activities," prefix and no <p class="subtitle"> lead under the bar.
    L.ok("L26b", 'font-style:italic;color:#FFFFFF;margin-top:3px;">Oct 11 through Nov 9, 2026</div>' in page
         and "Recurring Meetings &amp; Events</span><div style=\"font-size:14px;font-style:italic" in page
         and '<p class="subtitle">' not in page
         and "Recurring activities," not in page,
         "Recurring: Oct 11 through Nov 9, 2026 inside green header; no subtitle lead; no 'Recurring activities,'")
    return L


def check_recurring(L, recurring, this_week, upcoming, window):
    """L19 (Steven, Oct 9 ~8:45 PM): once our logic calls an event recurring, it is recurring in EVERY area.
    Recurring By Date / By Name pages = Tony-marked recurring PLUS every in-window date of the treat-as-recurring list."""
    names = {e["name"] for e in recurring}
    for n in TREAT_AS_RECURRING:
        L.ok("L19", n in names, f'Recurring pages include "{n}"')
    for e in recurring:
        if not e.get("recurring"):
            L.ok("L19b", e["name"] in TREAT_AS_RECURRING and e.get("category") != "Meetings",
                 f'non-Tony-recurring row on Recurring pages is on the treat-as-recurring list: {e["date"]} {e["name"]}')
    L.ok("L19c", all(window[0] <= e["date"] <= window[1] for e in recurring), "Recurring rows all inside the Recurring window")
    tw_up = {e["name"] for e in this_week + upcoming}
    for n in TREAT_AS_RECURRING:
        L.ok("L19d", n not in tw_up, f'"{n}" not in This Week/Upcoming data')
    return L


COMMITTEE_RE = re.compile(r"\bcommittee\b.*\bmeeting\b|\bboard of directors\b", re.I)

def check_meeting_rule(L, page, meetings, this_week, upcoming, recurring, events, eligible):
    """L25 (Steven, Oct 10, 2026 ~2:25 AM ET): "lets only put committee meetings in the top section of the nl and all
    other meetings go on upcoming or recurring, whatever the logic dictates". Top Meetings section = committee/board
    meetings only; committee/board meetings never appear in This Week / Upcoming / Recurring; every other meeting
    (incl. Tony category Meetings) is placed by the normal This Week / Upcoming / Recurring rules -- no blanket
    category exclusion."""
    L.ok("L25", meetings and all(COMMITTEE_RE.search(e["name"]) for e in meetings),
         f"Meetings section = committee/board only: {[e['name'] for e in meetings]}")
    leak = [e["name"] for e in this_week + upcoming + recurring if COMMITTEE_RE.search(e["name"])]
    L.ok("L25b", not leak, f"no committee/board meeting in This Week/Upcoming/Recurring {leak}")
    sec = _section(page, "Committee &amp; Board Meeting Schedules")
    other = [t for t in _row_titles_mtg(sec) if not COMMITTEE_RE.search(t)]
    L.ok("L25c", not other, f"email Meetings rows all committee/board {other}")
    placed = {id(e) for e in this_week + upcoming + recurring}
    for e in events:
        if not eligible(e) or e.get("category") != "Meetings" or COMMITTEE_RE.search(e["name"]): continue
        tw = e in this_week; up = e in upcoming; rc = e in recurring
        # wherever the normal windows put it -- never silently dropped just for being category Meetings
        expect_up = "2026-10-18" <= e["date"] <= "2026-11-08" and not e.get("recurring")
        expect_rc = e.get("recurring") and "2026-10-11" <= e["date"] <= "2026-11-09"
        L.ok("L25d", (up or not expect_up) and (rc or not expect_rc),
             f'non-committee Meetings-category "{e["name"]}" {e["date"]} placed by normal logic (TW={tw} UP={up} REC={rc})')
    return L


def check_recurring_pages(L, pages, title):  # SUPERSEDED by L23 (check_recurring_page_layout), PR #19 merged Oct 10
    """L20 (Steven, Oct 9 ~8:50 PM): Recurring By Date / By Name pages -- title "Recurring Activities"
    (heading + browser title), no "confirmed" wording, no Palm Hill masthead (palm/date banner, gold tagline, address bar)."""
    for o, h in pages.items():
        L.ok("L20", f"<title>{title} — By {o.capitalize()} — " in h and f">{title}</span>" in h,
             f'by-{o}: title + heading "{title}"')
        L.ok("L20b", "confirmed" not in h.lower(), f"by-{o}: no \"confirmed\" wording")
        L.ok("L20c", "masthead-palm" not in h and "header-title" not in h and "1800 Seminole Blvd" not in h
             and "A look at upcoming events" not in h and "Vol. 1, No." not in h, f"by-{o}: no Palm Hill masthead")
        L.ok("L20d", "Recurring Meetings &amp; Events" not in h, f"by-{o}: old title gone")
    return L


def check_notice_pages(L, pr15_pages_dir, builder_pages_dir):
    """L18 Original Notice pages. Canonical copies live in the PR #15 working tree (read-only here).
    The builder's own out/pages/*-notice.html are LEGACY (old shell) and must never be deployed."""
    for slug in ("2026-10-12-communications-committee", "2026-10-13-golf-committee"):
        f = Path(pr15_pages_dir) / f"{slug}-notice.html"
        if not f.exists():
            L.warn("L18", f"PR #15 notice copy not found ({f}); cannot verify"); continue
        h = f.read_text(encoding="utf-8")
        L.ok("L18", "ph-masthead" not in h and "ph-banner" not in h, f"{slug}-notice: no masthead")
        L.ok("L18b", "Original Notice" not in h, f'{slug}-notice: no "Original Notice" in title or links (no self-link)')
        L.ok("L18c", "ph-footer" not in h and "ph-urgent" not in h and "ph-fineprint" not in h, f"{slug}-notice: no bottom block")
        L.ok("L18d", "full text of the Palm Hill webmaster notice" not in h, f"{slug}-notice: no intro line")
        L.ok("L18e", ">View Meeting Agenda →</a>" in h and ">Join on Zoom →</a>" in h, f"{slug}-notice: Agenda · Zoom kept")
        b = Path(builder_pages_dir) / f"{slug}-notice.html"
        if b.exists() and "ph-masthead" in b.read_text(encoding="utf-8"):
            L.warn("L18f", f"builder out/pages/{slug}-notice.html is LEGACY old-style — do NOT deploy it; PR #15 copy is canonical")
    return L


def check_meeting_pages(L, email, pr15_pages_dir):
    """L22 (Steven, Oct 9 ~11:30 PM): no "Original Notice →" link anywhere in the email; the meeting Source line's
    "Webmaster" (short per L29) links the notice page. PR #15 meeting/Zoom pages: no Vantaca box, no calendar
    disclaimer, no Previous Meetings / archive bar, no Original Notice link; Source links the notice page."""
    L.ok("L22", "Original Notice" not in email, 'email: no "Original Notice" link')
    for slug in ("2026-10-12-communications-committee", "2026-10-13-golf-committee"):
        L.ok("L22b", f'{slug}-notice.html" style="color:#3A6B1A;">Webmaster</a>' in email, f"email {slug}: Webmaster links notice page (L27/L29 short)")
        for kind in ("meeting", "zoom"):
            f = Path(pr15_pages_dir) / f"{slug}-{kind}.html"
            if not f.exists():
                L.warn("L22c", f"PR #15 copy not found ({f}); cannot verify"); continue
            h = f.read_text(encoding="utf-8")
            L.ok("L22c", not any(b in h for b in ("ph-footer", "ph-urgent", "ph-fineprint", "VANTACA", "always confirm event times")), f"{slug}-{kind}: no bottom block")
            L.ok("L22d", "Previous Meetings" not in h and "ph-archive-bar" not in h and "ph-archive-nav:none" in h, f"{slug}-{kind}: no archive bar (marked none)")
            L.ok("L22e", "Original Notice" not in h, f"{slug}-{kind}: no Original Notice link")
            L.ok("L22f", f'<a href="{slug}-notice.html">Palm Hill webmaster notice</a>' in h, f"{slug}-{kind}: Source links notice page")
    return L


def check_month_policy(L, docs):
    """L21 CODE POLICY M3 (Steven, Oct 9, 2026 ~8:57 PM ET): all months are displayed as three letters
    (Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec) everywhere -- email and Vercel pages. FAIL on ANY full English
    month name anywhere in the HTML (text, titles, attributes). docs = {label: html}."""
    for label, h in docs.items():
        h = _strip_titles(h)  # L30 (Oct 11, 2026): titles/headings use FULL month names -- exempt from L21
        hits = [h[max(0, m.start() - 30):m.end() + 10].replace("\n", " ") for m in FULL_MONTH_RE.finditer(h)]
        L.ok("L21", not hits, f"{label}: 3-letter months only" + (f" -- {len(hits)} full month name(s), e.g. {hits[:3]}" if hits else ""))
    return L


# L30 FULL MONTH NAMES IN TITLES (Steven, Oct 11, 2026 ~2:20 AM ET): all titles and headings (every section) use full
# month names, never 3-letter abbreviations. Date rows, section date windows, masthead date, Source lines, body prose
# still use 3-letter months (L21/L26/L02).
MON3_ABBR_RE = re.compile(r'\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b\.?')
_TITLE_PATTERNS = [
    re.compile(r'(<span[^>]*-webkit-text-fill-color:#FFFFFF;">)([^<]+)(</span>)'),          # green section-bar headings
    re.compile(r'(<div style="font-size:15px;font-weight:bold;color:#333333;">)([^<]+)(</div>)'),  # bold item titles (plain rows)
    re.compile(r'(<td valign="top" align="left" style="font-size:15px;font-weight:bold;color:#333333;text-align:left;padding-right:10px;">)([^<]+)(</td>)'),  # bold item titles (loc-right rows)
]

def _titles(h):
    return [m.group(2) for rx in _TITLE_PATTERNS for m in rx.finditer(h)]

def _strip_titles(h):
    for rx in _TITLE_PATTERNS:
        h = rx.sub(lambda m: m.group(1) + m.group(3), h)
    return h

def check_title_months(L, docs):
    """L30: FAIL (fail-closed) if any heading or bold item title contains a 3-letter month abbreviation."""
    for label, h in docs.items():
        ts = _titles(h)
        bad = [t for t in ts if MON3_ABBR_RE.search(t)]
        L.ok("L30", bool(ts) and not bad, f"{label}: {len(ts)} titles, full month names only" + (f" -- abbreviated: {bad}" if bad else ""))
    return L


COMMUNITY_SOURCES = [  # L24 refreshed for Oct 18 (Steven, Oct 17 10:29 PM; R42 one source email = one notice)
    ("Swimming Pool Food and Beverage Rules", "2026-10-16-swimming-pool-food-and-beverage-rules-notice", "Webmaster", ""),
    ("Info from Linda", "2026-10-08-info-from-linda-notice", "Webmaster", ""),  # whole email (3 sections), no "Linda Keehl,"
    ("Property Fraud Alert", "2026-09-30-property-fraud-alert-notice", "Webmaster", ""),
    ("October Mowing Date", "2026-09-29-mowing-dates-notice", "RPM", ""),
]

def check_community_sources(L, email, pages):
    """L24: every Community Notices Source line links its notice page (green underlined, same <a> style as the
    meeting Source lines); notice pages are title-only (no masthead/archive bar/footer, ph-archive-nav:none),
    carry no unsubscribe link, no 'Original Notice' wording, and 3-letter months only."""
    sec = _section(email, "Community Notices")
    for title, slug, words, tail in COMMUNITY_SOURCES:
        a = f'<a href="{BASE}{slug}.html" style="color:#3A6B1A;">{words}</a>{tail}</div>'
        L.ok("L24", a in sec, f'{title}: Source links {slug}.html')
        h = pages.get(slug, "")
        L.ok("L24b", bool(h) and "ph-archive-nav:none" in h and "ph-masthead" not in h and "ph-footer" not in h
             and "ph-archive-bar" not in h, f"{slug}: title-only page")
        L.ok("L24c", "unsubscribe.php" not in h and "adminfiles" not in h and "Original Notice" not in h and not FULL_MONTH_RE.search(h),
             f"{slug}: no unsubscribe link / no 'Original Notice' / 3-letter months")
    L.ok("L24d", sec.count('href="https://www.propertyfraudalert.com/select"') == 1, "Property Fraud Alert body link kept")
    L.ok("L24e", sec.count("Source: ") == len(COMMUNITY_SOURCES) and sec.count(f'href="{BASE}') == len(COMMUNITY_SOURCES),
         "one linked Source per notice")
    return L


# L23 (Steven, Oct 10, 2026 ~12:40 AM ET, PR #19): Recurring By Date / By Name Vercel pages —
#   (a) no Palm Hill masthead (palm banner + issue date, gold tagline, address bar);
#   (b) issue date kept, directly under the green "Recurring Meetings & Events" title (above the view links);
#   (c) every activity row: title LEFT + location RIGHT on line 1, "Day, Mon D, YYYY • time" on line 2 (no place in meta);
#   (d) 3-letter months throughout (Jan..Dec): issue date, intro window, By Date dividers, row dates (Steven, Oct 10 ~12:45 AM);
#   (e) window line inside the green title bar (italic subtitle); By Date / By Name = white-on-green band (Steven, Oct 10 ~12:55 AM).
#   (f) one title per event: no By Date day dividers / By Name group headers; date+time under the name (Steven, Oct 10 ~1:05 AM).
# Raises AssertionError (fail-closed: builder stops before writing the page).
#   (g) under the green bar: "Vol. 1, No. N" LEFT + issue date RIGHT, plain small print; no centred bold date (~1:20 AM).
#   (i) 'Times and rooms are subject to change...' line centred (~1:27 AM).
#   (j) no footer: VANTACA service-request box and 'For the latest details...' line removed (~1:35 AM).
#   (h) shading = simple per-row zebra: row 1 white, row 2 pale green, ... regardless of day/activity (~1:25 AM).
def check_recurring_page_layout(html_s, label, issue_long, n_rows, rows_in_order=None, volno=None):
    # L23k (Steven, Oct 10 ~1:40 AM ET, PR #19): NO committee / board meetings on the Recurring pages. Since L25 (Oct 10 ~2:25 AM)
    # only committee/board titles are excluded; other Meetings-category items follow Tony's recurring flag.
    _titles = re.findall(r'class="ph-row-title">([^<]+)<', html_s)
    _mtg = [t for t in _titles if re.search(r"\bcommittee\b.*\bmeeting\b", t, re.I) or re.search(r"\bboard of directors\b", t, re.I)]
    assert not _mtg, f"L23k recurring page {label}: committee/board meeting rows must not appear: {_mtg}"
    # L23j (Steven, Oct 10 ~1:35 AM ET, PR #19): no footer on these pages -- no beige VANTACA NON-URGENT / URGENT
    # service-request box and no italic "For the latest details, always confirm ..." line.
    for marker in ('class="ph-footer"', 'class="ph-urgent', 'VANTACA', 'SERVICE REQUESTS', 'class="ph-fineprint"', 'For the latest details'):
        assert marker not in html_s, f"L23j recurring page {label}: footer marker {marker!r} must be gone"
    for marker in ('class="ph-banner"', 'class="ph-masthead"', 'class="ph-palm"', 'class="ph-tagline"', 'class="ph-address"', 'ph-issuedate'):
        assert marker not in html_s, f"L23a recurring page {label}: masthead marker {marker} present"
    assert len(re.findall(r'<h1 class="ph-section">Recurring Meetings &amp; Events<span class="ph-section-sub">[^<]+</span></h1>\n'
                          + r'<div class="ph-section-date"><span class="ph-section-volno">Vol\. \d+, No\. \d+</span>'
                          + re.escape(f'<span class="ph-section-issuedate">{issue_long}</span></div>\n<nav class="ph-links"'), html_s)) == 1, \
        f"L23b/L23g recurring page {label}: Vol/No (left) + issue date (right) line must sit directly under the green section title"
    # L23g: exactly one Vol/No + one issue date on the page; old centred bold <p class="ph-section-date"> gone.
    assert '<p class="ph-section-date">' not in html_s, f"L23g recurring page {label}: old centred bold issue date still present"
    assert html_s.count('class="ph-section-volno"') == 1 and html_s.count('class="ph-section-issuedate"') == 1, f"L23g recurring page {label}: Vol/No/date line count"
    if volno is not None:
        assert f'<span class="ph-section-volno">{volno}</span>' in html_s, f"L23g recurring page {label}: Vol/No must be {volno}"
    # L23e (Steven, Oct 10 ~12:55 AM ET; date-only Oct 10 ~2:50 PM ET): window INSIDE green title bar as italic
    # subtitle — date only ("Oct 11 through Nov 9, 2026"), no "Recurring activities," prefix; By Date / By Name = green band.
    subs = re.findall(r'<span class="ph-section-sub">([^<]+)</span>', html_s)
    assert len(subs) == 1 and re.fullmatch(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2} through '
                                           r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}', subs[0]), \
        f"L23e recurring page {label}: window subtitle missing/wrong inside green bar: {subs}"
    assert "Recurring activities," not in html_s, f"L23e recurring page {label}: 'Recurring activities,' prefix must be gone"
    assert html_s.count(subs[0]) == 1, f"L23e recurring page {label}: window line must appear only in the green bar"
    assert "Recurring Palm Hill activities" not in html_s and not re.search(r'<p class="ph-lead">Recurring activities', html_s), \
        f"L23e recurring page {label}: old window lead line below the bar must be gone"
    assert html_s.count(f'<p class="ph-view ph-view-title">{label}</p>\n<div class="ph-activities"') == 1, \
        f"L23e recurring page {label}: green-band {label} title must sit directly above the list"
    assert "ph-view-date" not in html_s, f"L23b recurring page {label}: date must not sit under By Date / By Name"
    rows = re.findall(r'<div class="ph-row(?: ph-alt)?">(.*?)</div></div>\n', html_s)
    assert len(rows) == n_rows, f"L23c recurring page {label}: {len(rows)} rows != {n_rows}"
    pat = re.compile(r'<div class="ph-row-line"><div class="ph-row-title">[^<]+</div><div class="ph-row-loc">[^<]+</div></div>'
                     r'<div class="ph-row-meta">[A-Z][a-z]+day, (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4} • [^<•]+$')
    bad = [r for r in rows if not pat.match(r)]
    assert not bad, f"L23c recurring page {label}: {len(bad)} rows not title-left/location-right, e.g. {bad[0][:160]}"
    # L23f (Steven, Oct 10 ~1:05 AM ET, PR #19): ONE title per event. No By Date day-divider headings and no By Name
    # group headings (no ph-subhead / h2 anywhere in the list); each row shows the activity name once, with
    # "Day, Mon D, YYYY • time" directly under it. Rows must appear in the expected order with the right name + date.
    lst = html_s.split('<div class="ph-activities"', 1)[1].split('</main>', 1)[0]
    assert 'ph-subhead' not in html_s and '<h2' not in lst and '<h3' not in lst, \
        f"L23f recurring page {label}: date/name divider headings must be gone (one title per event)"
    # L23i (Steven, Oct 10 ~1:27 AM ET): caution line centred (ph-lead-center), exactly once.
    assert html_s.count('<p class="ph-lead ph-lead-center">Times and rooms are subject to change. The club calendar may require sign-in.</p>') == 1, \
        f"L23i recurring page {label}: 'Times and rooms...' line must be centred (ph-lead-center)"
    # L23h: simple per-row zebra -- even index white (no ph-alt), odd index pale green (ph-alt); no clumping.
    flags = [m == ' ph-alt' for m in re.findall(r'<div class="ph-row( ph-alt)?">', lst)]
    assert flags == [i % 2 == 1 for i in range(len(flags))], f"L23h recurring page {label}: rows must alternate white / pale green per row"
    for r in rows:
        assert r.count('class="ph-row-title"') == 1, f"L23f recurring page {label}: row has != 1 title: {r[:120]}"
    if rows_in_order is not None:
        import html as _h
        got = [(_h.unescape(re.search(r'class="ph-row-title">([^<]+)<', r).group(1)),
                _h.unescape(re.search(r'class="ph-row-meta">([^<•]+?) •', r).group(1))) for r in rows]
        assert got == list(rows_in_order), f"L23f recurring page {label}: row order/name/date mismatch"
    # L23d (Steven, Oct 10 ~12:45 AM ET, PR #19): 3-letter months THROUGHOUT these pages (issue date, intro window,
    # By Date dividers, row dates). No full month name may appear anywhere in the page.
    full = [m for m in FULL_MONTHS if re.search(r'\b' + m + r'\b', html_s)]
    assert not full, f"L23d recurring page {label}: full month name(s) {full} present; use Jan..Dec"
    assert re.fullmatch(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}', issue_long), f"L23d issue date {issue_long!r} not 3-letter"


# L27 + L29 (Steven, Oct 10, 2026 ~2:10 PM ET linked webmaster Source only; amended Oct 11, 2026 ~8:37 AM ET
# L29: short form EVERYWHERE — linked word is "Webmaster", never "Palm Hill Webmaster". Same for Calendar on
# Source lines. No "email", "notice(s)", sender names or dates on the Source credit.
WEBMASTER_SOURCE_LINKS = {  # Source owner -> Vercel page the "Webmaster" link must open
    # refreshed for Oct 18 (Steven, Oct 17 10:29 PM). The Halloween Dance Party row is the R42 calendar-row exception: its
    # date/time/room come from the calendar; Linda's email is only its extra Webmaster source.
    "Finance Committee Meeting": "2026-10-10-finance-committee-meeting-notice.html",
    "Halloween Golf Cart Parade": "2026-09-18-halloween-golf-cart-parade-notice.html",
    "Swimming Pool Food and Beverage Rules": "2026-10-16-swimming-pool-food-and-beverage-rules-notice.html",
    # L27/L29 (Steven, Oct 17 11:51 PM): the three dated, unlinked credits now link copies made by scripts/notice_page.py
    "November Coffee and Pancake Volunteers": "2026-10-15-november-pancakes-and-coffee-volunteers-notice.html",
    "Shuffleboard Season Reminders": "2026-10-12-shuffleboard-information-notice.html",
    "Taste of Golf — November 18": "2026-10-14-taste-of-golf-notice.html",
    "Info from Linda": "2026-10-08-info-from-linda-notice.html",
    "Property Fraud Alert": "2026-09-30-property-fraud-alert-notice.html",
    "Halloween Dance Party": "2026-10-08-info-from-linda-notice.html",
    # Did You Know videos Source is now "Committees of Palm Hill Webpage" (not Webmaster) — Oct 11 FINAL-REVIEW
}
def check_webmaster_sources(L, email):
    """L27/L29: every webmaster Source is linked short 'Webmaster' only; L29: no Palm Hill * on Source lines."""
    srcs = re.findall(r'Source: (.*?)(?:</div>|</td>|</span></td>)', email)
    # Fallback if regex yields nothing useful — also gather simple Source: …</div>
    if not srcs:
        srcs = re.findall(r'Source: (.*?)</div>', email)
    wm = [x for x in srcs if "ebmaster" in x]
    good = re.compile(r'<a href="https://palmhillnews\.vercel\.app/pages/[^"]+" style="color:#3A6B1A;">Webmaster</a>')
    for x in wm:
        L.ok("L27", bool(good.search(x)) and x.count("ebmaster") == 1 and "Palm Hill Webmaster" not in x,
             f"Webmaster Source is linked 'Webmaster' only (L29 short), last on the line: {re.sub(r'<[^>]+>', '', x)[:80]}")
    L.ok("L27b", len(wm) == len(WEBMASTER_SOURCE_LINKS), f"{len(wm)} webmaster Sources (expected {len(WEBMASTER_SOURCE_LINKS)})")
    for title, page in WEBMASTER_SOURCE_LINKS.items():
        i = email.find(f">{title}<")
        j = email.find("Source: ", i)
        # end at </div> or </td>
        if i >= 0 and j >= 0:
            end_j = email.find("</div>", j)
            end_td = email.find("</td>", j)
            ends = [e for e in (end_j, end_td) if e >= 0]
            line = email[j:min(ends)] if ends else ""
        else:
            line = ""
        L.ok("L27c", f'{BASE}{page}" style="color:#3A6B1A;">Webmaster</a>' in line, f"{title}: Webmaster -> {page}")
    L.ok("L27d", not re.search(r"Webmaster (?:email|notices?)\b|Linda Keehl, |Palm Hill Webmaster", " ".join(srcs)),
         "no 'Webmaster email/notice', 'Linda Keehl,', or 'Palm Hill Webmaster' in any Source line")
    # L29: Source lines never use long Palm Hill Calendar / Palm Hill Webmaster
    bad_src = [re.sub(r'<[^>]+>', '', x)[:100] for x in srcs if "Palm Hill Calendar" in x or "Palm Hill Webmaster" in x]
    L.ok("L29", not bad_src, "L29 short Source labels everywhere (no Palm Hill Calendar/Webmaster on Source lines)"
         + (f" -- e.g. {bad_src[:3]}" if bad_src else ""))
    return L


# L28 (Steven, Oct 10 ~2:48 PM ET): Helpful Webpages Palm Hill Link Monthly must be the
# latest monthly-media newsletter download — never a prior-month token. Fail-closed: if
# monthly-media cannot be reached or the token/PDF month cannot be confirmed, the build stops.
LINK_HUB = "https://monthly-media.com/mmnewsletter.php?NID=121"
LINK_DL_RE = re.compile(
    r"https://monthly-media\.com/newsletter_download\.php\?t=([0-9a-f]+)&(?:amp;)?type=newsletter"
)
_MON_EN = ("January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December")


def resolve_latest_link_download():
    """Return the absolute latest Palm Hill Link newsletter_download URL (with & not &amp;).
    Raises on any failure (caller treats that as L28 FAIL)."""
    import urllib.request
    from datetime import datetime
    from zoneinfo import ZoneInfo
    with urllib.request.urlopen(LINK_HUB, timeout=30) as r:
        hub = r.read().decode("utf-8", "replace")
    m = re.search(
        r"newsletter_download\.php\?t=([0-9a-f]+)&(?:amp;)?type=newsletter", hub
    )
    if not m:
        raise RuntimeError(f"no newsletter_download token on {LINK_HUB}")
    token = m.group(1)
    dl = f"https://monthly-media.com/newsletter_download.php?t={token}&type=newsletter"
    req = urllib.request.Request(dl, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as r:
        cd = r.headers.get("Content-Disposition", "") or ""
    now = datetime.now(ZoneInfo("America/New_York"))
    mon = _MON_EN[now.month - 1]
    needle = f"{mon}_{now.year}"
    if needle not in cd.replace(" ", "_") and needle not in cd:
        raise RuntimeError(
            f"latest download is not {mon} {now.year} (Content-Disposition={cd!r})"
        )
    return dl


def check_link_monthly_latest(L, email):
    """L28: Palm Hill Link Monthly href in Helpful Webpages == live latest download."""
    try:
        latest = resolve_latest_link_download()
    except Exception as e:
        L.ok("L28", False, f"could not resolve latest Link download (fail-closed): {e}")
        return L
    latest_amp = latest.replace("&", "&amp;")
    hrefs = re.findall(
        r'<a href="(https://monthly-media\.com/newsletter_download\.php\?t=[0-9a-f]+&amp;type=newsletter)"[^>]*>Palm Hill Link Monthly</a>',
        email,
    )
    L.ok(
        "L28",
        len(hrefs) == 1 and hrefs[0] == latest_amp,
        f"Helpful Webpages Palm Hill Link Monthly = latest ({latest})",
    )
    toks = re.findall(
        r"newsletter_download\.php\?t=([0-9a-f]+)&amp;type=newsletter", email
    )
    latest_tok = latest.split("t=")[1].split("&")[0]
    L.ok(
        "L28b",
        bool(toks) and all(t == latest_tok for t in toks),
        f"no stale Link download tokens in email (want {latest_tok}; got {toks})",
    )
    return L


# R71: per-issue expectation overrides from the content file (LOCKED = {"NAME": value}); unknown names stop the checks.
for _k, _v in C.LOCKED.items():
    if _k not in globals(): raise SystemExit(f"R71: {C.ISSUE} LOCKED override {_k!r} is not a locked_checks name")
    globals()[_k] = _v
for _k in ("NOTICES_EXPECTED", "CHAIR_EXPECTED"):
    if globals()[_k] is None: raise SystemExit(f"R71: {C.ISSUE} content file LOCKED must set {_k}")
