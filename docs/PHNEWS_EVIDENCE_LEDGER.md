# PHNEWS Evidence Ledger

**Repository:** `zeoszeos/palmhillnews`  
**Branch:** `phnews-shared-docs`  
**Updated:** September 25, 2026  
**Purpose:** Bind a small set of operationally important PHNEWS claims to evidence and verification status. This is not a duplicate project history.

| ID | Claim | Claim type | Evidence | Verified by / date | Status | Notes |
|---|---|---|---|---|---|---|
| E-001 | PHNEWS has a 13-section canonical registry | durable-rule + current-state | `phnews_canonical/registry.json` per current Handoff; Handbook registry list | Handoff/Handbook, 2026-09-25 | PENDING LIVE WORKTREE VERIFICATION | Durable design is accepted; live file should still be verified before code work. |
| E-002 | Handoff-declared primary worktree is `/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter` | current-state | Current Handbook/Handoff | GPT/Hermes docs, 2026-09-25 | PENDING LIVE FILESYSTEM/GIT VERIFICATION | Older records name other PHNEWS locations. |
| E-003 | `source_body` full-fidelity detail-page behavior is implemented locally | current-state | Handoff sections describing `detail_pages.py`, generated detail review, and Calendar source preservation | Project handoff, 2026-09-25 | IMPLEMENTED_UNVERIFIED_LIVE | Needs live worktree/commit/test verification. |
| E-004 | Fact-level provenance / `fact_sources` is implemented locally | current-state | Handoff PHLGA implementation record; shared `render_fact_sources()` behavior | Project handoff, 2026-09-25 | IMPLEMENTED_UNVERIFIED_LIVE | Preventive provenance QC still pending. |
| E-005 | Earlier six Events - Upcoming detail pages were published | historical/current public reference | Merge commit `d058716faa58fa969393ceb2ad40c290130926a4`; public URLs recorded in Handoff | Prior deployment record, 2026-09-25 review | PUBLISHED_PREVIOUS_VERSION | Newer local fixes are not assumed published. |
| E-006 | Events - This Week uses Day 0–8 and Events - Upcoming uses Day 9–60 | durable-rule | Handbook/Handoff event-window rule | StevO-approved project rule recorded 2026-09-25 | ACCEPTED_RULE | Live tests should remain tied to this rule. |
| E-007 | September 21, 2026 full newsletter is the current whole-newsletter visual/reference fallback | reference/control | `/mnt/d/TEMP/Palm Hill CC/Palm Hill Newsletter/Palm_Hill_Newsletter_2026-09-21_20260921_091336.html` as recorded in Handoff | Handoff, 2026-09-25 | REFERENCE_RECORDED_PENDING_LIVE_PATH_VERIFY | Reference does not override newer per-section approvals or current rules. |
| E-008 | 90-day mailbox sample reportedly contained 170 Palm Hill/RPM messages | historical/pending-verification | Reported Handbook statistic: 126 Palm Hill + 44 RPM, 2026-06-23 through 2026-09-23 | Historical project record | REPORTED_PENDING_EVIDENCE_VERIFICATION | Message volume, not unique information volume. Original query/report not yet preserved in shared evidence. |
| E-009 | GPT reproduction using currently documented exact sender addresses did not reproduce 170 | current verification attempt | Gmail query on 2026-09-25: Palm Hill exact documented sender returned 154; documented RPM sender returned 0; combined exact sender query returned 154 | GPT, 2026-09-25 | VERIFIED_QUERY_RESULT_WITH_EVIDENCE_GAP | Durable exported query report not yet attached; result shows current documentation is insufficient for reproducibility, not that 170 is false. |
| E-010 | Latest local Events - Upcoming changes are newer than the earlier public deployment | current-state | Handoff records source-body, source-display, date/provenance/fact-source fixes as local only after commit `d058...` | Handoff, 2026-09-25 | CURRENT_LOCAL_NOT_PUBLISHED | Must not be described as published until explicit deploy + URL verification. |

## Ledger maintenance rule

Add entries only for claims that materially affect:

- source authority;
- implementation state;
- approval;
- publication;
- canonical path/repository identity;
- major architecture;
- reproducibility.

Do not use this ledger for every minor project fact.
