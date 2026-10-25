# PHNEWS Nov 1, 2026 (Vol. 1, No. 16) — start-of-week checklist

Set up Sat Oct 24, 2026 ~8:45 PM ET (Steven: "Ready for next weeks nl", oct18/oct25 naming kept).
Branch `nov1-build` (off main 610be36). Oct 25 issue, SEND file, live pages and main untouched.

## Weekly rhythm
- **Friday:** main build (calendar re-pull, inbox sweep incl. Spam, all content in) -> preview + picture to Steven.
- **Saturday:** content deadline (6 PM sweep); Susan proofs Saturday.
- **Sunday Nov 1:** publish (`scripts/publish_issue.py --issue 2026-11-01 --dry-run` first), only on Steven's go.

## Workspace
- **Builder (R71, coding batch 4):** ONE shared builder in `builder/core/` (`build_core.py`, `locked_checks.py`, `run_checks.py`,
  `recurring.py`, `recurring_grouped.py`, `issue_ctx.py`) + this week's content file `builder/issues/2026-11-01.py` (data only).
  `builder/nov1/` now holds only `data/` and `stage_nov1_content.py`. Work root: `/workspace/phnews-consolidation/nov1`
  (own `data/` calendar snapshots, so Oct 25 rebuilds are not affected). Repo writes go to the `/workspace/nov1-build` worktree.
- **Build command (R69):** `python3 builder/build_issue.py --issue 2026-11-01` from `/workspace/nov1-build`. Guard only:
  `python3 builder/build_issue.py --check` (R71). Oct 25 regression check before any builder commit: `python3 tests/acceptance_oct25.py`
  (tag format-locked-2026-10-25-final-r5; must print ACCEPTANCE PASS). The old copy in `/workspace/phnews-consolidation/nov1/builder/` is obsolete.
- Recurring pages: `PHNEWS_ISSUE=2026-11-01 python3 builder/core/recurring.py && python3 builder/core/recurring_grouped.py . 2026-11-01`.
- **Locked-check expectations for Nov 1** (L08 Upcoming, L11 Notices, CHAIR): set them in `LOCKED = {...}` in `builder/issues/2026-11-01.py`
  once Steven approves content. New weeks: see `docs/NEW-ISSUE-HOWTO.md`.
- Dry run: `PHNEWS_DRYRUN=1 python3 builder/build_issue.py --issue 2026-11-01` — content guards are listed as TODOs instead of stopping; never use for publish.
- Previews: `D:\PHNEWS\nov1\PHNEWS-2026-11-01-preview.html` (fixed names), mirrored to NAS `PH Newsletter\2026-11-01-previews\`.
- Calendar-pull record: `builder/calendar-pull/2026-11-01.json`.

## Carry-over items
a. **Main-page links consolidation (Steven approved Oct 24):** Helpful Webpages goes 9 -> 7 links.
   "Committee Meeting Videos" -> `archive/videos.html` replaces Latest + Video Archives; add a "Committee Meeting Video Archives"
   link on `videos.html`. "Palm Hill Link" -> `archive/palm-hill-link.html` replaces Monthly + Link Archives; add the current
   monthly issue link at the top of `palm-hill-link.html`. No new pages. Picture to Steven before anything goes live.
   (Builder lines: "Helpful Webpages + archive footer links" block; R25 label assert must be updated with it.)
b. **R66 Rules teaser style** for any new Rules Did You Know item: "Information on X, Y, and Z" from the rule's lettered parts
   (`_R66_PHRASES`), main page + DYK archive row identical (R66b), <= 3 lines.
c. **R62c agenda-over-calendar:** a committee's own agenda/report next-meeting date beats the calendar; every `MTG_OVERRIDE`
   cites its page + exact wording; no source time = calendar time kept. Carried: P&E Tue Nov 10 12:30 PM, Finance Wed Nov 18 (still future).
   Drop each once its meeting passes or a newer agenda arrives.
d. **Meetings agenda/Zoom check:** agendas arrive only a few days before — search palmhillblast AND gotwicz, Spam included,
   Friday and Saturday (Board Oct 28 / Compliance Oct 29 now past; check every meeting in Nov 1 – Dec 1).
e. **Susan's Communications report** still outstanding (dropped for Oct 25 only).
f. **Three missing Listen pages** (Golf / Comms / RE) — NOT approved; ask Steven before building.
g. **Oct 25 leftovers waiting on Steven:** his final-check changes + Sunday go for Oct 25; Finance row Source "Agenda" link offer;
   OneDrive video links on Did You Know Archives (click once to confirm); Bill Bender's two Oct 17 emails still in Spam.

## Content decisions to confirm Friday (dry-run state)
- **Dropped from Oct 25:** Joe Clay story (no Nov 1 story yet -> R45 needs a story or Steven's omit OK), notices Library Closed
  (ended Nov 1), Info from Linda (Halloween/market past), North Clubhouse ice machine, Sanitation Field, Stop sign rules; R60c ice guard.
- **Carried (still valid / retention rules):** Tony FB notice, Holiday cards (Bill Bender), South Rec officers (Dec 2), Couples Golf
  (Nov 5), Pool food rules, Nov pancakes/coffee volunteers, Shuffleboard, Taste of Golf (Nov 18); chair reports P&E Oct 14 + Golf
  Oct 13 (30-day rule); Megan's Oct 23 Weekly Manager Update (until replaced — expect Oct 30); Did You Know Spectrum + Assessments
  (newest DYK stays until replaced); President's message; meeting overrides above.
- **Dry-run TODOs:** R21 Thanksgiving Dinner needs detail/More page; run_checks L03 (no Community Stories section),
  L08/L11 (expectations still Oct 25 — refresh `locked_checks_nov1.py` NOTICES/CHAIR/Upcoming once content is approved).
