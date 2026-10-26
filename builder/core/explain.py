"""R75 (coding batch 6, Steven Oct 24 2026 10:40 PM "do them all"): plain-English failure messages.
explain(text) -> one extra line for a failed guard/check: WHY it matters and HOW to fix it, keyed by the rule id the
failure message starts with (R-number from STYLE-RULES.md, L-number from the locked checks). Unknown ids fall back to the
rule's own title in STYLE-RULES.md. Adds lines only: pass/fail decisions and counts never change."""
import re
from pathlib import Path
_SR = Path(__file__).resolve().parents[2] / "STYLE-RULES.md"
L_FAMILY = {  # locked checks (run_checks.py / locked_checks.py), by number
    "L01": ("the masthead Vol./No. must match this issue", "set VOL_NO in builder/issues/<date>.py"),
    "L02": ("the masthead date must be this Sunday's date", "check ISSUE in the content file"),
    "L03": ("sections must appear in the approved order", "fix the section order (or, for a new approved order, update run_checks ORDER)"),
    "L04": ("private/test items must never reach residents", "remove the listed item from the source data"),
    "L05": ("Meetings rows must match the calendar pull exactly", "re-pull the calendar or fix MTG_EXTRA / MTG_OVERRIDE in the content file"),
    "L06": ("meeting rows keep the approved layout", "rebuild; if it persists, the meetings markup in build_core changed"),
    "L07": ("This Week must list exactly the calendar's events for the week", "re-pull the calendar; check AS_RECURRING"),
    "L08": ("Upcoming must list exactly the calendar's events in its window", "re-pull the calendar; set UPCOMING_LABEL_EXPECTED in the content file"),
    "L09": ("recurring activities must not appear as one-off events", "keep TREAT_AS_RECURRING and AS_RECURRING the same"),
    "L10": ("event rows keep the approved layout", "rebuild; check the event markup"),
    "L11": ("Community Notices must be exactly the approved list, in order", "fix NOTICES in the content file, or (once Steven approves) LOCKED NOTICES_EXPECTED"),
    "L12": ("the Board President section must keep its links, Listen and Source", "check the seed's President block"),
    "L13": ("Chair Reports must be exactly the approved reports and intros", "fix CHAIR_REPORTS, or (once approved) LOCKED CHAIR_EXPECTED"),
    "L14": ("chair report dates must show (3-letter months)", "fix CHAIR_DATES_EXPECTED / the report dates in the content file"),
    "L15": ("each chair report needs exactly one Listen", "check CHAIR_REPORTS listen pages"),
    "L16": ("each chair report needs Read Full Report and the archives link", "check CHAIR_REPORTS pages"),
    "L17": ("Recurring must show this week's window and its 3 pages", "run builder/core/recurring.py + recurring_grouped.py for this issue"),
    "L30": ("titles must use full month names", "spell the month out in the item title"),
    "L31": ("no links to an older issue's preview/recurring pages", "rebuild from the current content file"),
}
FIX = {  # R-rules with a specific fix line (others: rule title from STYLE-RULES.md)
    "R18b": "cut the teaser to its first source sentence(s); never reword",
    "R21": "add an EVENT_PAGE / EVENT_LINK entry for the event in the content file (or Steven drops the detail)",
    "R42": "one source email = one notice: merge the split notice or add the missing section",
    "R56": "list the matched event's notice in Community Notices (NOTICES) or remove the match",
    "R60": "shorten the item so its summary is at most 3 lines at 390/660 px (cut, never reword)",
    "R60b": "set HOLIDAY_TITLE / HOLIDAY_SOURCE_LABEL / HOLIDAY_PAGE in the content file to the approved wording",
    "R60c": "set ICE_TITLE / ICE_SOURCE_LABEL / ICE_PAGE and keep the ice notice 3rd in NOTICES",
    "R77": "put the chair's wording in block by block, drop the meeting date from the title, and list one card per committee",
    "R78": "from Nov 1 the Meetings header carries no date range: set MEETINGS_SHOW_RANGE = False in the content file (Oct 25 keeps True)",
    "R79": "run recurring.py + recurring_grouped.py for the issue (writes the three All Events pages); keep ALL_EVENTS_LINK_TEXT / ALL_EVENTS_NOTE as Steven wrote them",
    "R62": "fix the date/time in MEETING_ROW_CHECKS or MTG_OVERRIDE (agenda/report date beats the calendar)",
    "R62b": "fix the Finance row in MTG_OVERRIDE / MEETING_ROW_CHECKS",
    "R62c": "each MTG_OVERRIDE must cite its agenda/report page and wording (MTG_OVERRIDE_SOURCE)",
    "R64": "read the failed checks listed above; fix the content file, or update LOCKED once Steven approves new content",
    "R71": "content files hold data only; logic goes in builder/core/",
    "R71b": "move the listed text from builder/core/ into builder/issues/<date>.py",
    "R72": "copy the PDF into the work tree and give its relative path in the content file",
    "R73": "get the missing source (copy, never move) or drop the item -- never invent it",
    "R74": "save a baseline only after Steven approves: scripts/save_visual_baseline.py",
}
_titles = None
def _rule_title(rid):
    global _titles
    if _titles is None:
        _titles = {}
        try:
            for m in re.finditer(r"^\| (R\d+[a-z]?) \| \*\*(.+?)\*\*", _SR.read_text(encoding="utf-8"), re.M): _titles.setdefault(m.group(1), m.group(2))
        except OSError: pass
    return _titles.get(rid) or _titles.get(re.sub(r"[a-z]+$", "", rid))
def explain(text):
    m = re.search(r"\b(R\d+[a-z]?|L\d+)(?=[a-z]?\b|:)", str(text))
    if not m: return "    why/fix: see the message above and STYLE-RULES.md"
    rid = m.group(1)
    if rid.startswith("L"):
        why, fix = L_FAMILY.get(rid[:3], ("a locked format check failed", "see builder/core/locked_checks.py " + rid))
        return f"    why: {why}. fix: {fix}. ({rid})"
    t = _rule_title(rid) or _rule_title(re.sub(r"[a-z]+$", "", rid)) or "see STYLE-RULES.md"
    fix = FIX.get(rid) or FIX.get(re.sub(r"[a-z]+$", "", rid)) or f"follow STYLE-RULES {rid}"
    return f"    why: {rid} -- {t.rstrip(':. ')}. fix: {fix}."
