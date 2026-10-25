# How to start a new PHNEWS issue (STYLE-RULES R71)

A new week = **one new content file**. Never copy a builder (the R71 guard stops the build if a per-issue folder holds builder code).

1. Copy the idea of the latest content file: create `builder/issues/<YYYY-MM-DD>.py` (the Sunday issue date) with every required
   field: `ISSUE`, `VOL_NO`, `SHORT` (e.g. `nov8`), `DEFAULT_REPO`, `DEFAULT_WORK`, `STORY` (dict json/listen/teaser_sentences or None),
   `STORY_OMIT_DRYRUN_NOTE`, `NOTICES_DROPPED`, `R60C_ICE_NOTICE`, `DRYRUN_OK`, `LOCKED`. Data only: assignments and comments, no code.
   Then the issue's own content (R71b, batch 5): events detail/links, meetings overrides + `MEETING_ROW_CHECKS`, notices, chair
   reports, Weekly Manager Update, Did You Know, archive rows, PDF attachment, and `LOCKED = {"NOTICES_EXPECTED": [...],
   "CHAIR_EXPECTED": {...}}`. Start from the previous week's file; label anything not yet reviewed `CARRIED FROM <date>`.
   Never put issue text in `builder/core/` -- the R71b guard fails the build if a content string shows up there.
2. Everything else comes from the date: long date, Vol./No. text, This Week / Upcoming / Recurring / Meetings windows (R69),
   calendar window (R21b), file names (`PHNEWS-<date>-preview.html`, `build-audit-<SHORT>.json`, `local-<SHORT>/`).
3. Make the work tree (`DEFAULT_WORK`) with `source/` (seed + shell) and `data/` (calendar snapshots); put the week's source-verbatim
   item data in `builder/<SHORT>/data/` and, if needed, a `builder/<SHORT>/stage_<SHORT>_content.py` staging script.
4. Check: `python3 builder/build_issue.py --check`, then dry run `PHNEWS_DRYRUN=1 python3 builder/build_issue.py --issue <date>`.
5. A rule or logic change goes in `builder/core/` (one place for every issue) and must keep `python3 tests/acceptance_oct25.py` PASS.
6. Recurring pages: `PHNEWS_ISSUE=<date> python3 builder/core/recurring.py && python3 builder/core/recurring_grouped.py . <date>`.

Still draft only: nothing is sent, published or pushed without Steven's go. Oct 18 (`builder/oct18/`) is locked as sent and exempt.
