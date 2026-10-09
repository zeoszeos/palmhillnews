# Newsletter Archive (v1, draft)

- **Data:** `archive/archive-items.json` is hand-curated. It lists issue membership, the text of notices that never had a page, the video list, and the hidden duplicates. This folder is not published, because `vercel.json` copies only `pages/`, `events/` and `reports/`.
- **Build:** `node scripts/build_archive.js` writes `pages/archive/*.html`, `pages/archive/archive-index.json`, and the "Previous … → · Newsletter Archive →" strip on each listed detail page.
- **Issue pages:** `node scripts/build_archive.js --issues-from <dir>` writes `pages/archive/issues/<date>.html` from the sent HTML. `<dir>` uses the NAS `02-Issues/<YYYY-MM>/<send date>/sent-final/` layout (path taken from `issues[].nas`). Issues run from Jul 21, 2026 (first resident issue) and every page is built from the exact sent build. Each issue page is written once and never overwritten (Handbook 17).
- **Check:** `node scripts/build_archive.js --check` exits 1 if anything is out of date.
- **Rules:**
  - Detail pages keep their URLs and content (Handbook 8). Only the marked strip is added before `</body>`.
  - Hidden pages stay live and are simply not listed.
  - Raw sources are not committed. The Oct 4 blast carried a personal unsubscribe link, and the Aug–Sep builds carry Zoom meeting links/passcodes and a monthly-media download token; the builder strips these.
- **Adding Oct 11 after PR #9 merges:**
  1. Add the issue (sent time, source file) and its new items to `archive-items.json`.
  2. Save the exact sent HTML to the NAS (`02-Issues/2026-10/<send date>/sent-final/`).
  3. Run the builder with `--issues-from`.
- **Runbook** (for Hermes or anyone): `archive/RUNBOOK-archive.md`. Run `node scripts/build_archive.js --help` to see the inputs and outputs.
