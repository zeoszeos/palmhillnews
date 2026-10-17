# PHNEWS Style Rules (locked format)

These are Steven Leonowicz's locked format decisions for the Palm Hill Newsletter (PHNEWS) and its pages on palmhillnews.vercel.app.
**Don't change them without Steven's OK.** The golden screenshots for this look are in `tests/golden/format-locked-2026-10-18/`, and git tag `format-locked-2026-10-18` marks the repo at that point.

Where each rule is enforced:
- Shared code: `scripts/style_rules.py`, imported by the issue builder, live preview, publish step and recurring generator.
- Archive hub generator: `scripts/build_archive.js`.
- Video hub generator: `scripts/build_meeting_video_archive.py`.
- Checks: `scripts/check_title_months.py` and `scripts/visual_regression.py`, which run on every builder pass.

| # | Rule | Enforced in |
|---|------|-------------|
| R1 | **Listen links:** speaker icon + "Listen" stay on one line (never wrapped or stacked), right-aligned, 14px in from the right edge. Same in every section, desktop and mobile. Needed because the archive CSS forces `white-space:normal` and `overflow-wrap:anywhere`, so every Listen link carries `white-space:nowrap !important`. | `style_rules.listen_fix`; checked by visual_regression R1 |
| R2 | **Masthead** shows the weekday and full date, e.g. "Sunday, October 18, 2026". | builder; visual_regression R2 |
| R3 | **Months are spelled out** in titles, headings, `<title>`, green section bars and their subtitle bands (e.g. "October 18 through November 18"), and archive month headings. Abbreviations ("Oct 22") appear only in body and entry lines: meeting and event rows, Source lines, list entries, video rows. | `style_rules.enforce_title_months` (title-safe `mon3_text`), build_archive `MONTHS_FULL`/`issueTitle`; check_title_months + visual_regression R3 |
| R4 | **Meeting entries:** title first, then the date/time line under it ("(also on Zoom)" when there is one). The link row reads `Agenda →` · `Zoom →`. Zoom passcodes may be shown and the full Zoom link is used. Webmaster notice details come from `data/webmaster-meeting-notices.json`, which restores the Oct 11 layout. | builder MEETING_DETAIL |
| R5 | **Source labels** use the short forms "Calendar", "Webmaster", or "Calendar, Webmaster", never "Palm Hill Calendar" or "Palm Hill Webmaster" on Source lines. A meeting that appears only in a webmaster notice says "Webmaster". | builder; visual_regression R5 |
| R6 | **No provenance/banner strip** (`pha-banner`) on issues dated Oct 18, 2026 or later. | build_archive `NO_BANNER_FROM`; visual_regression R6 |
| R7 | **No QR code on the main newsletter page.** QR codes go on the linked notice page (e.g. the Facebook group notice). | builder; visual_regression R7 |
| R8 | **Office/RPM business phone numbers** stay on notice pages. No personal phone numbers or secrets. The Craft Fair phone number is untouched until Steven decides. | manual review |
| R9 | **Notice Listen pages** are named `YYYY-MM-DD-notice-<slug>.html`. `build_archive` rejects new pages with "listen" in the name. Existing URLs stay valid: copy pages, never move them. | publish step |
| R10 | **Archived past issues stay exactly as sent.** Format fixes apply only to the current issue and current pages. After any `node scripts/build_archive.js` run, revert `pages/2026-09-30-shareholders-report.html` and `pages/2026-10-09-weekly-manager-update.html` with `git checkout`. | process |
| R11 | **Process for every change:** branch, then PR, then `gh pr merge --squash --delete-branch` (retry on "Base branch was modified"). No email, no Vantaca blast, and never email residents, unless Steven explicitly asks. | process |
| R12 | **Content decisions (Oct 16):** keep the short weekly summary, keep the fiduciary item; the birthday note is removed. | builder content |
| R13 | **Meeting links go to Vercel pages:** `Agenda →` and `Zoom →` in meeting entries link to palmhillnews.vercel.app pages, never straight to zoom.us or an outside agenda. This follows the Oct 11 precedent (`2026-10-12-communications-committee-zoom.html`, `2026-10-13-golf-committee-zoom.html`). The Zoom page has a big "Join Zoom Meeting" button that opens the full zoom.us link (with passcode), and it shows the join link, the full URL, the webinar ID, the passcode and the dial-ins. The Zoom page comes from `scripts/meeting_zoom_page.py`, using the `zoom_page` field in `webmaster-meeting-notices.json`. The builder stops if a notice has a Zoom link but no `zoom_page`. | builder + `meeting_zoom_page.py`; visual_regression R13 |
| R14 | **Palm Hill Link Archives:** the page is https://palmhillnews.vercel.app/pages/archive/palm-hill-link.html, built by `scripts/build_link_archive.py` from `data/link-issues.json`. The current issue comes first and links to our hosted PDF first, with the monthly-media page (NID=121) second. Below it, one row per month, newest first, each with its matching Community Story when there is one. In the email, Helpful Webpages shows "Palm Hill Link Monthly" (the latest monthly-media download) followed by "Palm Hill Link Archives". On Oct 18+ website copies, "Palm Hill Link Monthly" links to the Link Archives page instead of losing its link. The Main Archive hub has a "Palm Hill Link Archives" tile. | build_link_archive.py, link_archive_bullet.py, build_archive.js; visual_regression R14 |
| R15 | **Keep every Link PDF on Vercel permanently** (Steven, Oct 16): issues drop off the Link website over time. Each Friday build runs `scripts/fetch_link_pdf.py`. When monthly-media has a new month, it saves `pages/archive/link/Link-YYYY-MM.pdf`, adds the month to the data file and rebuilds the page. Then commit and PR it, and copy the PDF to Omen `D:\PHNEWS\link\`. Never delete a hosted Link PDF. | builder (build_oct18.py) + fetch_link_pdf.py |
| R16 | **"All Archives →" band on the Newsletter Archives page** (`pages/archive/index.html`): the bottom line "Looking for stories or reports? All Archives →" sits in its own light-green band (`#eef6e8`, 3px dark-green top border, 28px top margin), separate from the issue list. It is centered with a bold link that never wraps, and it reads well on mobile. | build_archive.js `.pa-quiet` CSS |
| R17 | **Note box on the Newsletter Archives page:** the "Volume 1 began…" note sits in a cream box (`#faf6ea`, thin tan border, 4px gold left edge `#b9913c`, rounded corners, padding). It has a 30px gap above it, separating it from the issue list, and a 26px gap below it before the green All Archives band (R16). The cream is meant to look clearly different from that green band. | build_archive.js `.pa-note` CSS |

## Visual regression (Friday/Saturday builds)

```
/workspace/.venv-vr/bin/python scripts/visual_regression.py <page.html|URL> --golden tests/golden/format-locked-2026-10-18/<issue|email> [--out DIR]
```

- The script screenshots every green-bar section plus the masthead at desktop 1280px and mobile 390px (2x).
- It compares them with the golden set and writes `REPORT.txt` plus `*-DIFF.png` highlights.
- Exit codes: `1` means a rule failed (fix it before sending), `2` means visual diffs only (review them; content changes every week, so diffs are expected in text-heavy sections), `0` means clean.
- `build_oct18.py` runs the script automatically against the `email` golden after it writes the preview.
- After Steven approves a new look, recapture the golden set with `--capture` and tag the repo `format-locked-YYYY-MM-DD`.
