# Calendar Mismatches Report button - PARKED (Nov 4, 2026, 8 PM ET)

Parked at Steven's request (voice, Nov 4 2026 8:03 PM ET). Nothing has been sent to Tony. Nothing is merged or tagged.

## What the button does (once it is live)
- Tony gets one private link, with no login. One tap does all of this:
  1. It pulls the Palm Hill calendar live.
  2. It tries to read the RPM calendar.
  3. It tries the Gmail search for committee and board emails that may mention meeting dates.
  4. It rebuilds the Calendar Mismatches Report from whatever it got.
- Every report shows a Refresh date, plus a note for each source saying when that source was last checked (R109).
- Kill switch: the `REPORT_BUTTON_ENABLED` environment variable. The button only works when it is set on Vercel.
- The link goes to Tony only. Steven can shut the link off and issue a new one, or turn the setting off and redeploy. Either way the old link stops working.

## Done
- Draft PRs, all open and unmerged:
  - #151 `nov8-start` at fb04b2d (Nov 8 issue start)
  - #152 `calendar-report-colors` at 3d3813a (report colours and times, R105-R112)
  - #153 `report-button-anytime` at b8f6951 (the button, R106; stacked on #152)
  - #154 `nov8-yellow-contrast` at e508434 (R107 contrast guard)
  - These shas were current before this doc was committed.
- `REPORT_BUTTON_ENABLED` exists in the code but is **not** set on Vercel.
- Rules R105-R112 are in STYLE-RULES.md, each with a guard in `builder/core/run_checks.py`:
  - R105/R105f: deviation wording
  - R106: the anytime button
  - R107: yellow-background contrast
  - R108: dark mode / table cell contrast
  - R109: Refresh date, with a note per source
  - R110: live sources plus a secret scan
  - R111: report-link notes
  - R112: an explicit colour on every text element; body text solid #1f1f1f
- Scripts:
  - `scripts/refresh_live_sources.py`: Palm Hill pull, RPM login, and a read-only Gmail IMAP search. Writes `<work>/data/live-sources.json`.
  - `scripts/try_it_email.py`: the 'try it' email, built from a template with light-only, R112-checked HTML.
- Secrets are named `RPM_USERNAME`, `RPM_PASSWORD` and `GMAIL_APP_PASSWORD`. They are stored securely as environment variables. Their values are never in the repo, logs, PRs or chat.
- Gmail drafts kept in palmhillblast (none sent):
  - r2500255153710338124: the report to Tony (Nov 4 data, R112 fix)
  - r5613485118976703622: 'try it' to Tony
  - r6105113832009756897: test button, to Steven only
  - s:119334061055160716: the 5:17 PM report draft, left by Steven's choice
- Copies of the deleted drafts are in `/workspace/draft-archive-2026-11-04/` on the Grok Bot box.

## Status today (Nov 4 2026, about 8 PM ET)
- The live site has no button yet: https://palmhillnews.vercel.app/api/calendar-mismatches returns 404 because #153 is not merged or deployed.
- The RPM live read is **not working**. The portal needs an email-address login, and the saved RPM_USERNAME is not an email address.
- The Gmail live search is **not working**. IMAP (imap.gmail.com ports 993/143) is blocked from the build box, so the app password was never tested.
- A report run today would use the saved Nov 4 data:
  - Palm Hill pulled 4:08 PM ET (an identical re-pull at 5:16 PM ET showed no changes)
  - RPM read about 4:11 PM ET
  - Committee/board email time not recorded
- The 'try it' draft describes a button that is not live yet. It has a bracketed "[STEVEN - REMOVE BEFORE SENDING ...]" line. The report draft's "About the report link" block also refers to a link that does not exist yet.

## Blocked: needs Steven
1. Re-enter the RPM username as the email address used for the RPM portal. The saved one is not an email; a secret card is waiting.
2. Grant Vercel team access (`steves-projects-b5bb4bd0` currently returns 403). Then set `RPM_USERNAME`, `RPM_PASSWORD`, `GMAIL_APP_PASSWORD` and `REPORT_BUTTON_ENABLED` on Vercel.
3. Gmail server connection, one of:
   - test the app password from a host that can reach IMAP,
   - switch to OAuth, or
   - use Grok Bot's own Gmail connection.
4. Steven's explicit OK to merge #151-#154.
5. Write the RPM calendar parser. This can only be done once the RPM login works.

## Rule for background work
Agents may keep working on anything that does not need Steven, such as guards, docs and tests on the draft branches. They must stop at anything that needs him: secrets, Vercel access, merges, sends, or Tony-facing changes.

## Copies
- Repo: this file on `calendar-report-colors` and `report-button-anytime`.
- Omen: `D:\PHNEWS\docs\` is **not** updated. The Grok Bot box cannot reach the LAN and Steven's computer was offline. A copy is at `/workspace/REPORT-BUTTON-PARKED-2026-11-04.md` on the box and needs copying to Omen `D:\PHNEWS\docs\` when Omen is reachable.
