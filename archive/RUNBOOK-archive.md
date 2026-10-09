# RUNBOOK: PHNEWS Newsletter Archive

Plain Node CLI, with no Grok Bot or cloud steps. Hermes (the `phnews` profile on the Omen) can run it from a clone of `zeoszeos/palmhillnews`.

## What it does
- Builds the resident archive at `/pages/archive/`:
  - an archive home
  - 7 section pages: Community Stories, President's Message, Committee Chair Reports, Manager Reports, Community Notices, Did You Know, and Meeting Videos
  - `archive-index.json`
  - one frozen page per sent issue
- Adds a "Previous … → · Newsletter Archive →" strip to each listed detail page. Nothing else in those pages changes, and no URLs change (Handbook §8).
- Issue pages are written **once** and never overwritten (Handbook §17).

## When to run it
After each issue is **sent**: as part of that week's pages PR, or as its own PR. Never before the send, because the archive only lists sent issues. Merging to `main` publishes, so that step needs Steven's OK.

## Steps
1. **Save the exact sent build (copy only).** Use the HTML build whose PDF was actually linked (or, from Oct 4 on, the resident blast body); confirm by hashing the linked PDF against the build's PDF. Copy it, preserving its timestamp, to
   `\\freenas2\zeosdata2\E_Drive\OpenClaw\PH Newsletter\02-Issues\<YYYY-MM>\<send date>\sent-final\PHNEWS-<send date>-sent-<original name>`
   and add a row to `02-Issues\PHNEWS-sent-finals-INDEX.csv` (send time, file date, size, sha256, source). The issue key is the **send date** (ET).
   Remove any personal unsubscribe token from that copy; the script also strips it.
2. **Edit `archive/archive-items.json`:**
   - Add the issue: `date` (send date), `label` (e.g. "Week of October 11, 2026"), `sent` (ISO send time with offset), `file_dated` (ISO time of the HTML build, from its file time / "Updated:" line), `format`, `source`, `nas` (`02-Issues/<YYYY-MM>/<send date>/sent-final/<file>`), and an optional `caveat` or `remove_sections`.
   - Give it `volume` and `number` ("Vol. 1, No. 13"). Numbering: Jul 21, 2026 is Vol. 1, No. 1; every SENT issue (not a correction or "correction coming" notice) is the next No.; the volume goes up on each Jul 21 anniversary and No. restarts at 1 (rule in `numbering`). Get the value from the phnews helper: `python3 pipeline/scripts/issue_number.py <send date>`. The builder fills in a missing value and stops with an error if a stored value breaks the rule. Vol./No. appears in the archive home list, the issue page banner and title, and `archive-index.json`.
   - The issue banner reads "Archive copy · Sent <weekday, Month d, yyyy> at <time> ET · file dated <Mon d, yyyy h:mm AM/PM>", then the caveat.
   - Add each new item to its section, giving `page` (existing `pages/…` file) or `id` + `text` for notices that have no page of their own, plus `issues: [date]`.
   - Append the new date to `issues` on items carried over from earlier issues.
   - Videos: add `{group, date, url}` rows from the signed-in "Committees of Palm Hill" save (the `scan_committee_videos.py` output).
3. **Build:**
   ```
   node scripts/build_archive.js --issues-from "/mnt/z/E_Drive/OpenClaw/PH Newsletter/02-Issues"   # or a local copy of 02-Issues
   ```
   Without `--issues-from`, only the section pages, home, index and strips are rebuilt.
4. **Verify:**
   - `node scripts/build_archive.js --check` exits 0 (everything is up to date).
   - `git diff --stat`: changes to existing `pages/*.html` must be strip-only (3–4 added lines each).
   - Open `pages/archive/index.html` and the new issue page at 375, 390 and 660 px. There must be no sideways scrolling.
   - Every `palmhillnews.vercel.app/pages/…` link resolves. External OneDrive links may return 403 to scripts but open in a browser.
   - Search the new issue page for `unsubscribe`, `passcode`, `zoom.us`, `pwd=`, `newsletter_download.php` and `LOCAL REVIEW`. All must be absent. The builder already removes Zoom links/passcodes, unlinks monthly-media download-token links (text kept) and the unsubscribe link, and stops with an error if any of these survive.
5. **Commit** on a branch and open a **draft** PR. Never merge without Steven's OK.

## Inputs and outputs
| | Path |
|---|---|
| In | `archive/archive-items.json` (curated, not published) |
| In | `pages/*.html` (existing detail pages) |
| In | `<02-Issues>/<YYYY-MM>/<send date>/sent-final/<file>` (exact sent HTML; resolved from `issues[].nas`; old `<date>/<basename>` layout still accepted) |
| Out | `pages/archive/index.html`, `pages/archive/{community-stories,presidents-message,committee-reports,manager-reports,community-notices,did-you-know,videos}.html` |
| Out | `pages/archive/issues/<date>.html` (immutable) |
| Out | `pages/archive/archive-index.json` |
| Out | the marked strip in listed detail pages |

**Errors and exit codes:**
- A missing detail page, listen page or issue source makes the script stop with an error and a non-zero exit.
- `--check` exits 1 if anything is out of date.
- `--force-issues` regenerates frozen issue pages. Use it only before they are published.
