"""PHNEWS Sunday, October 25, 2026 (Vol. 1, No. 15) -- issue content file (STYLE-RULES R71). Data only; all logic is in builder/core/.
Approved and locked: tag format-locked-2026-10-25-final-r4; tests/acceptance_oct25.py rebuilds it byte for byte."""
ISSUE = "2026-10-25"
VOL_NO = 15
SHORT = "oct25"                       # work-tree names: build-audit-oct25.json, local-oct25/, source/recurring-oct25-orig/
DEFAULT_REPO = "/workspace/oct18-batch"
DEFAULT_WORK = "/workspace/phnews-consolidation/oct18"
# Community Story (R45/R55): Joe Clay - Keeper of The Course (PR #130, Steven Oct 19); teaser = first source sentence (R18c).
STORY = dict(json="builder/oct25/data/community-story-joe-clay.json", listen="2026-10-listen-joe-clay-story.html", teaser_sentences=1)
STORY_OMIT_DRYRUN_NOTE = None         # Oct 25 has a story; never omitted
NOTICES_DROPPED = []                  # beyond the shared NOTICES_DROPPED_OCT25 (R53)
R60C_ICE_NOTICE = True                # R60c: ice machine notice 3rd, Source: Oct P&E Committee Report (Oct 25 only)
DRYRUN_OK = False                     # content guards always stop the Oct 25 build
LOCKED = {}                           # locked_checks overrides (none: core lists are the Oct 25 approved lists)
