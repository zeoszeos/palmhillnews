"""PHNEWS Sunday, November 1, 2026 (Vol. 1, No. 16) -- issue content file (STYLE-RULES R71). Data only; all logic is in builder/core/.
Workspace set up Oct 24 2026; Steven confirms content Friday. New week = copy the idea of this file, never a builder."""
ISSUE = "2026-11-01"
VOL_NO = 16
SHORT = "nov1"
DEFAULT_REPO = "/workspace/nov1-build"
DEFAULT_WORK = "/workspace/phnews-consolidation/nov1"
# Joe Clay (Oct 25) is NOT carried. Set STORY = dict(json="builder/nov1/data/<story>.json", listen="<listen page>", teaser_sentences=1)
STORY = None
# PHNEWS_DRYRUN=1 lets the build finish without a story for workspace testing only -- NOT Steven's R45 approval, never publishes.
STORY_OMIT_DRYRUN_NOTE = "DRY RUN ONLY - no Nov 1 story chosen yet (not an approval)"
# Carry policy (set up Oct 24 2026 8:3x PM; Steven confirms Friday): keep notices still valid on/after Nov 1, drop Oct 25 one-offs.
NOTICES_DROPPED = ["Library Closed starting the week of October 26th",   # closure ends Sun Nov 1
                   "Info from Linda",                                     # Halloween Dance Oct 31 / market Oct 24: past
                   "North Clubhouse Ice Machine Moved",                   # Oct 25 news item (R60c was Oct 25-only)
                   "Help with maintaining Sanitation Field", "Please observe important stop sign rules"]  # ran Oct 25 (Steven to confirm drop)
R60C_ICE_NOTICE = False               # the ice machine notice is dropped for Nov 1
DRYRUN_OK = True                      # PHNEWS_DRYRUN=1 lists content guards as TODOs (workspace only)
LOCKED = {}                           # TODO Friday: refresh NOTICES / CHAIR / Upcoming expectations once content is approved (L08/L11)
