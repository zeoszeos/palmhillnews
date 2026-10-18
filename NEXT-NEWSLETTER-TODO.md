
## DONE Oct 17 10:45 PM ET (PR #121, tag format-locked-2026-10-18-approved-final-2)
- Held label batch (LABEL-AUDIT.md) shipped in the Oct 18 rebuild as R43; Committee Report Archives (R41 amended, Steven 10:33 PM).
- Info from Linda = one notice (R42). Follow-up to consider: archive pages now show "All Archives →" twice (top bar + crumb).

## DONE Oct 18 12:01 AM ET (PR #122, tag format-locked-2026-10-18-approved-final-3)
- R44 one All Archives link on all archive pages (duplicate top line resolved); Did You Know Archives; L27/L29 linked Webmaster credits + 3 source copies.
- Open: video committee pages no longer link back to the video archive list at the top (lower row only has Latest videos).

## Batch 6 (Steven Oct 18 12:07 AM) — PR #123 merged 7ebfb22, tag format-locked-2026-10-18-approved-final-4
- A: the "stale archive tops" report was a cached / pre-deploy view; production was already byte-identical to c11fd7e. New post-deploy guard: `python3 scripts/check_live_archive.py` (R44-live), run after every merge.
- B/R46: videos.html lower links removed (build_archive.js guard). Other lower cross-links reported to Steven, NOT changed: meeting-videos.html ("Latest Committee & Board Meeting Videos →", "How to watch (Did You Know) →"), the 9 video group pages ("Latest Committee & Board Meeting Videos →"), index.html (second "All Archives →" at the bottom), did-you-know.html (in-item "Latest Board and committee recordings →").
- C/R45: Community Stories is required every issue (the build stops without it). Oct 18 = Marge Taylor (Link Sep 2026). NEXT ISSUE: choose the next story (CANDIDATES.md in community-stories/) or record Steven's approval in COMMUNITY_STORIES_OMIT_APPROVED.
- SEND sha ae5d05af42c2ca45c5a704fcfead896a1919cf239bf431173da28a9f5b074790, 68,110 bytes; NAS PHNEWS-2026-10-18-SEND-20261018-0017.*

## Batch 7 (Steven Oct 18 12:23 AM) — PR #124 merged c298c0f, tag format-locked-2026-10-18-approved-final-5
- R47: Webmaster-sourced notices: More → / Listen open the same full-email page as the 'Webmaster' Source link (source_sections use_existing_page + summary_trim). Short 2026-10-18-notice-*.html pages stay live, unlinked.
- Listen added to Webmaster full-email pages: pool (10-16), property fraud (09-30), finance meeting notice (10-10), golf-cart parade (09-18).
- NEXT ISSUE: new Webmaster notices -> add to SOURCES with use_existing_page=True; summary_trim URL = the full-email page. Guard: style_rules.assert_webmaster_more.
- SEND sha 1acc8be865d70339b873595bec67c102699eab73a1f6f0dddcadca89a8f0344c, 68,078 bytes; NAS PHNEWS-2026-10-18-SEND-20261018-0029.*

## R48 (Steven Oct 18 12:31 AM) — event rows need an official date source
- Event rows (Meetings / This Week / Upcoming) must cite Calendar, RPM, or a committee agenda email (Agenda → = Source page). Webmaster/Linda may be added as a 2nd source and lend wording; a Webmaster/Linda-only event stays inside its notice (e.g. Largo Evening Market). Guard: style_rules.assert_event_sources (build, preview, publish).

## Oct 25 batch — TODO (Steven approved Oct 18 12:32 AM)
- [ ] Extend R47 to RPM-sourced notices (e.g. October Mowing Date): More →, Listen and the 'RPM' Source link all open the SAME full RPM email page (?listen=1 for Listen). If the full RPM email page is missing, create it verbatim from the RPM email (standard email-copy shell, with Listen). Extend style_rules.assert_webmaster_more (or a sibling check) to cover 'Source: RPM' items. Do not touch the Oct 18 SEND.
- [ ] Oct 25: roll out the A2 Listen player to all Listen pages via the shared scripts plus a rule and guard (Steven chose A, simplified).
  - A2 as approved for preview (Steven Oct 18 1:43 AM, redesigned 1:45 AM): no bottom bar, no Back/Forward buttons. One thin progress line (5px visible, 44px invisible touch zone) just under the header/date/Listen row, article-card width, sticky at the top while reading; tap or drag to jump to any paragraph. The Listen link is Play/Pause. Hidden until Listen is first pressed. Keeps paragraph highlight + auto-scroll, a compact resume prompt (Resume / Start over), and the R49 block list. Preview: pages/previews/listen-player/option-a2-simple.html. Port it into scripts/page_listen.py and build_archive.js (CHAIR_LISTEN_JS), add a STYLE-RULES row, and extend check_listen_coverage.py with the A2 control tests (tap, drag, pause/play, resume, full run with no duplicates).

## R49 (Steven Oct 18 12:39–12:44 AM) — Listen reads all visible content (required step)
- New pages with Listen: use scripts/page_listen.py SCRIPT (email/notice/event pages) or build_archive.js (stories/reports); never copy a script from another page. Guard: scripts/check_listen_coverage.py (runs automatically in build, preview, publish, build_archive, check_site_links, check_live_archive --live).
