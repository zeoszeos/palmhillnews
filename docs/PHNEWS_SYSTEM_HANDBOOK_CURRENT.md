# PHNEWS System Handbook — Current Operating Rules and Architecture

**Project:** Palm Hill Country Club PHNEWS  
**Status:** Current working handbook  
**Updated:** September 25, 2026  
**Primary owner:** StevO  
**Audience:** StevO, Communications Committee, ChatGPT, Hermes, Codex, and future PHNEWS maintainers

> This document is the current working source of truth for the PHNEWS system. It combines the previously approved handbook-development rules with the architecture, editorial rules, source/provenance controls, review workflow, and corrective actions established through September 25, 2026.


---

# Documentation Authority, Claim Types, and Evidence Control

**Document role:** This Handbook is authoritative for durable PHNEWS architecture, editorial rules, provenance rules, QC rules, approval boundaries, and operating principles.

**This Handbook is not by itself proof that a current implementation is complete, tested, accepted, deployed, or publicly verified.** Current implementation claims must be supported by the newest reconciled Handoff, Git/test/artifact evidence, and the Evidence Ledger.

When information conflicts, use the authority-by-question model in `docs/PHNEWS_SHARED_DOCS_INDEX.md`.

Important claims in this Handbook should be understood as one of:

- **durable-rule**
- **current-state**
- **proposed**
- **historical**
- **unresolved**
- **pending-verification**

Implementation/acceptance state is distinct from provenance state.

### Implementation / acceptance stages

```text
IMPLEMENTED
FOCUSED_TEST_PASS
FULL_QC_PASS
HTML_INSPECTED
EDITORIALLY_ACCEPTED
APPROVED_FOR_PUBLICATION
PUBLISHED_VERIFIED
```

### Provenance states

```text
VERIFIED_CURRENT_SOURCE
VERIFIED_RETAINED_SOURCE
FALLBACK_ONLY
SOURCE_DATA_DEFECT
```

A feature can be implemented without being accepted. A source can be verified without the surrounding feature being publication-ready.

### Evidence pattern for important claims

Where practical, use:

```text
Claim type:
Status:
Status as of:
Evidence:
Verified by:
Owner:
Approval state:
Blocking conditions:
Next verification:
```

Detailed evidence belongs in the Handbook, Handoff, or Evidence Ledger rather than the Tony Guide.


# 1. Purpose

PHNEWS is a controlled resident-information publishing system for Palm Hill Country Club.

It exists to reduce resident information fragmentation and overload by turning many separate emails, calendar entries, reports, notices, attachments, corrections, and reminders into a consolidated, readable, current reference.

A previously reported 90-day Gmail sample covering June 23 through September 23, 2026 recorded **170 direct Palm Hill/RPM messages** in one resident mailbox:

- reported Palm Hill Webmaster count: 126
- reported Resource Property Management count: 44
- reported average: about 56 messages per month
- reported average: about 12.8 messages per week

**Claim type:** pending-verification  
**Current status:** REPORTED_PENDING_EVIDENCE_VERIFICATION  
**Meaning:** message volume, not unique information volume.  
**Evidence gap:** the original query/report and sender-definition set have not yet been preserved in the shared evidence layer.  
**Reproduction attempt, September 25, 2026:** using the exact sender addresses currently documented for the stated date window, GPT's live Gmail query returned 154 Palm Hill messages and 0 messages for the currently documented RPM sender address. This does not disprove the original 170 count; it shows that the current documentation is insufficient to reproduce the earlier calculation. See `docs/PHNEWS_EVIDENCE_LEDGER.md` and `docs/PHNEWS_CONTRADICTION_REGISTER.md`.

Repeated reminders, updates, corrections, and duplicate source routes remain part of the resident-information problem PHNEWS is designed to solve.

The high-level transformation is:

```text
Incoming source material
    ↓
identify unique information
    ↓
preserve full source evidence
    ↓
normalize and reconcile
    ↓
classify and route
    ↓
create concise newsletter summaries
    ↓
create complete detail pages when appropriate
    ↓
assemble in canonical PHNEWS shell
    ↓
run structural/content/provenance QC
    ↓
human review and approval
    ↓
publish supporting pages
    ↓
verify public destinations
    ↓
send exact approved artifact
```

The design philosophy is:

> **Strict internally, forgiving externally.**

Residents should see clear, simple, useful information. Internally, PHNEWS must be strict about provenance, completeness, dates, source authority, link state, section identity, approval state, and regression prevention.

---

# 2. Handbook Development Rules

## 2.1 One chapter at a time

Develop Handbook material incrementally:

1. define chapter purpose
2. draft
3. add diagrams/tables/examples where useful
4. review for accuracy, completeness, usefulness, clarity, complexity, and reader experience
5. revise
6. approve/freeze
7. move to next chapter

Approved chapters become stable building blocks.

## 2.2 Separate chapter content from system-wide rules

A discovery made while working on one section may actually be a PHNEWS-wide rule.

Distinguish:

- **chapter/section-specific content**
- **system-wide rule**

System-wide rules belong in this handbook or another shared rule source, not only inside one renderer or one troubleshooting note.

## 2.3 Human product judgment governs PHNEWS

Automation and AI may:

- extract
- classify
- identify patterns
- summarize
- detect omissions
- propose rules
- generate code
- test consistency

StevO, as Product Owner and editorial authority, determines whether those recommendations serve residents and the real operating environment.

Technical completeness is not automatically preferable to simpler, clearer behavior.

## 2.4 Classify changes by type

During review, useful categories include:

- factual/logic correction
- missing source information
- business-rule refinement
- editorial judgment
- reader-experience preference
- scope simplification
- newly discovered operating condition
- regression prevention
- source/provenance defect
- publication-state defect

## 2.5 Prefer simplicity over unnecessary generalization

Build the smallest reusable rule that correctly handles the real need.

Generalize when:

- the requirement recurs in multiple places, or
- there is clear evidence the shared rule will be used.

## 2.6 Visual communication is a design principle

Use diagrams, workflows, hierarchies, comparison tables, and examples when they explain the system better than prose.

## 2.7 Two audiences

The full **PHNEWS System Handbook** may contain architecture, governance, operations, troubleshooting, and QC detail.

The **Tony Guide** should reuse the same truths but remain concise, approachable, and focused on how the system behaves rather than code internals.

## 2.8 Maintain traceability

For important rules preserve:

- what problem led to the rule
- what decision was made
- why
- where it applies
- where it does not apply
- what QC prevents recurrence

---

# 3. Roles and Decision Rights

## StevO

Acts as:

- Product Owner
- Domain Lead
- Editorial Lead
- final acceptance authority
- operational reviewer

StevO decides:

- what belongs in PHNEWS
- whether resident-facing wording is appropriate
- whether a section looks right
- whether a source claim is acceptable
- whether a section is approved
- whether publication may occur

## ChatGPT

Acts as:

- Business Analyst
- Solution Architect
- editorial/product partner
- QA/QC designer
- root-cause/corrective-action partner
- Codex instruction author

## Codex

Acts as:

- developer/implementation agent
- code troubleshooter
- test runner
- local artifact generator
- renderer/data-path modifier

## Hermes

Hermes can act as a project-aware agent using this handbook, the Tony Guide, and the current handoff as shared context.

Preferred operating loop:

```text
StevO
  ↓
ChatGPT
  ↓
Codex / Hermes
  ↓
ChatGPT + StevO review
  ↓
StevO approval
```

---

# 4. Canonical PHNEWS Architecture

PHNEWS is no longer to be treated as a loose collection of independent scripts.

The target architecture is:

```text
Verified Sources
      ↓
Canonical Full-Fidelity Records
      ↓
Section Rules / Renderers
      ↓
Detail Page Generation + Detail Manifest
      ↓
Canonical Section Registry
      ↓
Canonical PHNEWS Shell / Assembler
      ↓
Structural + Content + Provenance QC
      ↓
Approval / Reference Layer
      ↓
Publication
```

Core principles:

- one canonical shell
- one canonical ordered section registry
- one canonical renderer/data path per section
- one shared theme/component system
- one assembly process
- one approval/reference model
- one current-build detail-page manifest
- no hidden reconstruction during assembly

---

# 5. The Assembler Must Be Deliberately Simple

The assembler should:

1. select canonical section IDs
2. invoke/use canonical renderers
3. order them from the registry
4. insert returned fragments into the shell
5. output
6. run QC

The assembler must **not**:

- write new section content
- summarize
- abbreviate
- reinterpret
- rediscover source facts
- reconstruct missing data
- independently restyle sections
- invent links
- invent provenance

A section should behave the same whether rendered by itself, in a multi-section review, or in the full newsletter.

---

# 6. Stable Identity vs Presentation

Permanent distinction:

- **stable internal ID** = identity
- **sequence number** = presentation order
- **resident-facing title** = label

Do not use filenames or temporary review numbers as permanent identity.

Example:

- canonical key: `upcoming_events`
- resident title: **Events - Upcoming**
- current order: 11

Use heading titles rather than section numbers in user-facing communication.

---

# 7. Canonical Section Registry

Authoritative order:

1. `committee_board_meetings` — **Committee & Board Meeting Schedules**
2. `past_committee_board_summaries` — **Committee Chair Reports**
3. `whats_up_this_week` — **Events - This Week**
4. `regularly_scheduled_events` — **Regularly Scheduled Meetings & Events**
5. `community_announcements` — **Community Notices**
6. `rpm_updates` — **RPM - Resource Property Management**
7. `palm_hill_updates` — **Palm Hill Updates**
8. `shareholders_weekly` — **Weekly Shareholders Report**
9. `shareholders_monthly` — **Monthly Manager’s Report**
10. `past_maintenance_events` — **Past Maintenance Events**
11. `upcoming_events` — **Events - Upcoming**
12. `did_you_know` — **Did You Know?**
13. `permanent_utility_hub` — **Residents Reference Guide**

The registry owns:

- section identity
- order
- resident-facing title
- controlled heading metadata such as `heading_variant` and `heading_icon`

The shell does not own order.

---

# 8. Canonical Shell and Shared Theme

Known-good whole-newsletter visual reference:

```text
/mnt/d/TEMP/Palm Hill CC/Palm Hill Newsletter/
Palm_Hill_Newsletter_2026-09-21_20260921_091336.html
```

Preserve established:

- approximately 660px email layout
- Palm Hill masthead
- palm-tree treatment
- Updated timestamp
- gold tagline band
- address band
- This Week At A Glance
- fonts/colors/spacing
- rounded container
- footer

Header, footer, and At-a-Glance are framework components, not numbered sections.

Shared theme files include:

```text
phnews_canonical/theme.py
phnews_canonical/components.py
```

Shared section header:

```python
render_section_header(title, icon=None, variant="standard")
```

Do not duplicate normal section-heading CSS inside each renderer.

The **Residents Reference Guide** remains a valid special-layout exception.

---

# 9. Preview and Review Architecture

There is no separate fake preview renderer.

A preview is the real PHNEWS system rendering selected canonical sections.

The same section fragment must support:

- one-section review
- multi-section review
- full newsletter build

Review/test builds should expose all 13 canonical headings, including valid-empty sections, to prevent silent omission.

Valid-empty review message:

```text
No qualifying current items.
```

Production may omit valid-empty sections.

Internal review/publication status belongs in manifests, run reports, QC, or logs — **not inside resident-facing newsletter content**.

Never put resident-facing banners such as:

- LOCAL REVIEW — NOT PUBLISHED — NOT EMAILED
- PHNEWS PROOF COPY
- draft
- proof
- not for publication
- not emailed

into the newsletter itself.

---

# 10. Source Model: Evidence, Authority, and Provenance

Provenance answers:

> Where did this fact come from?

Evidence is not automatically truth. A calendar can be stale, an email can contain old forwarded text, and a PDF can disagree with a subject line.

PHNEWS preserves source evidence and reconciles conflicts instead of silently choosing by convenience.

Useful source families include:

- Palm Hill Calendar
- Palm Hill public pages
- RPM/VANTACA calendar
- Webmaster email
- RPM management email
- committee chair email
- committee chair report
- weekly manager report
- monthly manager report
- attached report
- attached committee summary
- event flyer
- resident/organizer submission
- meeting recording
- prior approved PHNEWS artifact as fallback/reference evidence

---

# 11. Source Recovery and Authority

For a missing source, preferred recovery order is:

1. live authoritative source
2. retained authoritative source
3. RPM/VANTACA
4. current authorized emails/attachments/notices
5. other verified source submissions
6. prior approved PHNEWS artifact as last-resort fallback

Important:

> Missing from retained cache does not prove the source does not exist.

Authority is field-specific. A source may control date/time but another source may enrich description or contact detail.

The calendar often provides the event skeleton; email/document sources often provide context.

---

# 12. Provenance States

Current conceptual states include:

```text
VERIFIED_CURRENT_SOURCE
VERIFIED_RETAINED_SOURCE
PROVENANCE_FALLBACK_ONLY
SOURCE_DATA_DEFECT
```

## VERIFIED_CURRENT_SOURCE

A current/live authoritative source has been verified.

## VERIFIED_RETAINED_SOURCE

An authoritative source is available in retained PHNEWS data.

## PROVENANCE_FALLBACK_ONLY

Only approved prior PHNEWS evidence remains for the occurrence/fact.

Do not convert this internal state into a resident-facing source label.

## SOURCE_DATA_DEFECT

A verified source exists, but canonical metadata is missing or incorrect.

Nickels provided a recent example: the Calendar source existed, but source metadata was not explicit in the canonical event record.

---

# 13. Resident-Facing Source Display

Resident source labels must represent verified factual origin.

Examples:

```text
Source: Palm Hill Calendar
```

or:

```text
Sources: Committee chair email + Attached committee summary document
```

Public source names may be clickable when the public destination is verified.

Never expose resident-facing:

- Gmail message IDs
- internal routing IDs
- WSL/local filesystem paths
- private attachment URLs
- internal source IDs
- `PROVENANCE_FALLBACK_ONLY`
- `Approved manual correction` unless there truly was a resident-relevant human correction and it is intentionally displayed
- `approved prior record`

If original factual source cannot be recovered, omit the resident-facing general source line rather than inventing one.

---

# 14. Fact-Level / Scoped Provenance

A major September 25 improvement is support for fact-level source attribution.

Old problem:

An item could only say:

- event has a source
- event has no source

That was too coarse.

Example: PHLGA

- November 13 occurrence/time/location = fallback-only
- Sue Waldecker contact = verified by Palm Hill LINK — September 2026

New concept:

```text
fact_sources
```

Example:

```json
{
  "fact_sources": {
    "contact": [
      {
        "label": "Palm Hill LINK — September 2026",
        "type": "attached_report",
        "verified": true,
        "public_url": null
      }
    ]
  }
}
```

Shared helper:

```python
render_fact_sources(...)
```

Resident output may therefore say:

```text
Contact source: Palm Hill LINK — September 2026
```

without falsely implying that the LINK verifies the entire event occurrence.

This pattern should be reusable for other mixed-provenance items.

---

# 15. Full-Fidelity Source Preservation

One of the most important recent corrections was recognizing that extracted facts alone are not enough.

A detail page can pass fact-based QC while still omitting meaningful sentences from the source.

For verified source records, especially Palm Hill Calendar events, retain the complete substantive description in:

```text
source_body
```

Desired projection model:

```text
authoritative source
      ↓
full-fidelity canonical record / source_body
      ↓                         ↓
newsletter summary             detail page
concise projection             complete projection
```

The Vercel detail page should derive from the full source body, not from the shortened newsletter summary.

---

# 16. Newsletter Summary vs Detail Page Contract

## Newsletter

A resident scan.

For substantive items, normally show:

- title
- resident-friendly date/time/location
- concise summary
- approximately 3–4 lines max when practical
- 5W+How when available
- detail link
- verified source line(s)

## Detail page

A preservation-oriented page.

Preserve all substantive facts from verified source set, including as applicable:

- full description
- contact names
- phone numbers
- price/cost
- registration instructions
- organizer/sponsor
- duration
- warnings/reminders
- start/end locations
- eligibility
- deadlines
- other meaningful source statements

Formatting may improve readability. Substance may not silently disappear.

Source attribution is not a substitute for source content.

---

# 17. Resident-Facing Date Standard

Internal dates may remain:

```text
YYYY-MM-DD
```

Resident-facing preferred:

```text
Wednesday, October 7, 2026
```

Shorter when needed:

```text
October 7, 2026
```

Never show raw ISO or ambiguous numeric dates to residents.

If weekday is shown, derive it from canonical date.

If source weekday conflicts with canonical date:

- flag QC
- use the derived correct weekday

If incoming numeric date is ambiguous, do not guess.

Shared helper:

```python
format_resident_date(...)
```

---

# 18. Event Window Rules

Permanent event windows:

## Events - This Week

Day 0 through Day 8 inclusive.

## Events - Upcoming

Day 9 through Day 60 inclusive.

Anchor = canonical newsletter issue/build date.

Not:

- source date
- scrape date
- cache timestamp
- old newsletter date

Required checks include:

```text
canonical_build_date_used
this_week_window_0_8
upcoming_window_9_60
no_event_window_overlap
no_event_window_gap
```

---

# 19. Community Notices Classification

**Community Notices** are resident-facing announcements whose primary purpose is awareness, action, recognition, or general community information rather than attendance at a scheduled event.

Examples include:

- street closures
- parking restrictions
- office closings
- holiday/trash schedule changes
- maintenance/service disruptions
- volunteer requests
- deadlines
- registrations
- ticket sales
- lost and found
- resident reminders
- safety/service information
- community information that should remain visible until resolved or expired

A scheduled event belongs in an event-oriented section when attendance at a specific date/time is the primary purpose.

Generic words such as “help” do not automatically create a Community Notice. The request must have enough context to establish what residents are being asked to do.

Community Notices may use **Active-Until-Resolved** behavior where appropriate.

---

# 20. Regularly Scheduled Meetings & Events

This section is a navigation hub rather than a giant event dump.

Title:

```text
Regularly Scheduled Meetings & Events
```

Subtitle:

```text
Regular Palm Hill meetings and events scheduled over the next 30 days.
```

Navigation:

```text
By Date →
By Name →
Palm Hill Calendar →
```

Rolling window:

```text
window_start = generation date
window_end_exclusive = generation date + 30 days
include if start <= occurrence < end_exclusive
```

The same filtered dataset must drive both By Date and By Name.

---

# 21. Detail Page Generation Contract

Substantive resident items that need fuller information should have detail pages generated/refreshed as part of the current build.

Rules:

- stable URL retained for same canonical item
- current build regenerates/refreshed content
- newsletter links come from current-build detail manifest
- stale `previous_public_url` is not authoritative
- local generation alone is not public readiness

Current important files:

```text
phnews_canonical/detail_pages.py
phnews_canonical/generated_details/manifest.json
phnews_canonical/publish_to_vercel.py
```

---

# 22. Public Link Readiness

A link is not PASS merely because an `href` exists.

Do not expose:

- local paths
- private Gmail links
- internal attachment routes
- guessed URLs
- obsolete preview paths
- unverified placeholder destinations

Publication readiness stages are distinct:

```text
generated
≠ staged
≠ committed
≠ pushed
≠ deployed
≠ publicly verified
```

A public destination is ready only when:

1. generated
2. staged in deployment tree
3. committed
4. pushed/merged
5. deployed
6. publicly verified
7. newsletter href matches deployed destination

Network/DNS verification failure is not automatically proof that a previously valid URL is invalid. Diagnose the failure mode before deleting links.

---

# 23. QC Layers

## Structural QC

Examples:

- all canonical sections represented in review
- registry order correct
- canonical renderer used
- shared theme used
- no duplicate wrappers
- no placeholders
- no stale/superseded content

## Content completeness QC

Examples:

```text
summary_present_when_source_has_substance
summary_5w_how_coverage
summary_length_within_policy
source_description_preserved
contact_details_preserved
cost_preserved
organizer_preserved
instructions_preserved
source_to_detail_content_completeness
detail_page_more_complete_than_summary
detail_page_contains_all_summary_facts
detail_page_contains_all_verified_source_facts
detail_page_not_less_complete_than_section_summary
```

## Full-source Calendar QC

```text
calendar_description_captured
calendar_description_not_truncated
source_body_to_detail_completeness
all_substantive_source_lines_represented
detail_derived_from_full_source_not_summary
newsletter_summary_is_separate_projection
```

## Provenance QC

```text
verified_source_provenance
no_internal_provenance_leak
source_attribution_matches_fact_origin
no_source_claim_for_unverified_fact_origin
```

## Fact-level provenance preventive QC

Next shared controls:

```text
fact_source_scope_valid
source_label_does_not_overclaim_scope
verified_supporting_fact_source_preserved
fallback_occurrence_not_mislabeled
resident_source_scope_matches_fact_origin
```

---

# 24. Root Cause and Corrective Action Standard

When a defect appears, PHNEWS should not merely patch the visible item.

Preferred sequence:

```text
observe defect
    ↓
identify root cause
    ↓
identify data-model / renderer / QC failure
    ↓
make shared corrective action
    ↓
add preventive QC
    ↓
regenerate
    ↓
inspect actual HTML
    ↓
human acceptance
```

Avoid:

```text
observe defect → patch one HTML file → move on
```

Each defect should make the system harder to break in the same way again.

---

# 25. Current Events - Upcoming Pilot Lessons

Events - Upcoming has been the main proving ground for the new architecture.

Current working set:

- Karaoke Obi-Time
- Halloween Golf Cart Parade
- Nickels
- North Clubhouse Craft Fair
- PHLGA
- Pancakes Breakfast

Expected source display:

- Karaoke Obi-Time — Source: Palm Hill Calendar
- Halloween Golf Cart Parade — Source: Palm Hill Calendar
- Nickels — Source: Palm Hill Calendar
- North Clubhouse Craft Fair — Source: Palm Hill Calendar
- PHLGA — Contact source: Palm Hill LINK — September 2026; no general occurrence source
- Pancakes Breakfast — no source line until original source is recovered

Important unresolved/cleanup items:

- verify/resolve Karaoke source-time discrepancy before final approval
- clean stale Craft Fair fallback typo `727-315-436-4369`; authoritative source body contains `727-315-4369`
- remove dangerous implicit default source behavior where missing metadata can be silently labeled Palm Hill Calendar
- implement fact-level provenance QC

---

# 26. Approval / Reference Architecture

Critical principle:

> **Latest Approved Artifact wins — not latest file, not latest build.**

Planned structure:

```text
phnews_canonical/reference/
  current_reference.json
  approved/
    YYYY-MM-DD/
      approved-newsletter.html
      approval_manifest.json
      detail_manifest.json
      build_manifest.json
      section_hashes.json
```

The latest approved full newsletter becomes the next whole-newsletter reference.

Older approved packages are archived, never overwritten.

Per-section approved artifacts may be newer than the whole-newsletter reference.

Fallback reference may provide a **visual/presentation baseline only**.

It must never roll back:

- current source data
- current business rules
- current QC
- current date rules
- current link rules
- current components

Fallback is not rollback.

---

# 27. Section Status as of September 25, 2026

## Committee & Board Meeting Schedules

Needs current dynamic source selection; avoid hardcoded stale occurrences.

## Committee Chair Reports

Locked/ready in current direction.

Expected four recent reports:

- Golf Advisory Committee
- Planning and Environmental
- Real Estate
- Rules and Regulations

Full report content should be preserved.

## Events - This Week

Shared theme/header; Day 0–8 window.

## Regularly Scheduled Meetings & Events

Locked/ready navigation-hub concept.

## Community Notices

Uses Active-Until-Resolved where appropriate and current-build detail-page contract.

## RPM - Resource Property Management

Currently valid empty.

## Palm Hill Updates

Currently valid empty.

## Weekly Shareholders Report

Locked/ready current direction; shared theme.

## Monthly Manager’s Report

Currently valid empty.

Editorial exception: may display the full report/document in newsletter and link to original PDF.

## Past Maintenance Events

Known qualifying examples:

- North Spa is open
- North Clubhouse Updates

Canonical renderer still needs stabilization.

## Events - Upcoming

Active pilot; architecture is close to acceptance but preventive provenance QC and a few cleanup items remain.

## Did You Know?

Persistent approved guidance includes:

- submitting a VANTACA service request
- viewing a meeting on Zoom

## Residents Reference Guide

Locked/ready; intentional distinctive layout.

---

# 28. Accessibility — Parked Until Current Milestone

Future accessibility layer may include:

- larger fonts
- font scaling
- high contrast
- keyboard navigation
- screen-reader-friendly structure
- descriptive links
- larger touch targets
- optional Listen/TTS control

Distinguish:

- **PHNEWS Theme** = appearance/design system
- **PHNEWS Accessibility Layer** = usability/inclusion constraints

Do not disrupt current stabilization milestone unless explicitly requested.

---

# 29. Current Important Paths

Primary canonical project:

```text
/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter
```

Important files:

```text
phnews_canonical/registry.json
phnews_canonical/framework.py
phnews_canonical/assembler.py
phnews_canonical/renderers.py
phnews_canonical/theme.py
phnews_canonical/components.py
phnews_canonical/detail_pages.py
phnews_canonical/content_qc.py
phnews_canonical/run_content_qc.py
phnews_canonical/publish_to_vercel.py
phnews_canonical/generated_details/manifest.json
PHNEWS-STABILIZATION-REPORT.md
```

Real Git checkout:

```text
/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter/repos/palmhillnews
```

Windows review:

```text
C:\Users\leono\Desktop\PHNEWS-Previews
```

Events - Upcoming preview:

```text
C:\Users\leono\Desktop\PHNEWS-Previews\PHNEWS-Events-Upcoming-Preview.html
```

Detail review copies:

```text
C:\Users\leono\Desktop\PHNEWS-Previews\Vercel-Publish\
```

---

# 30. Standard Work for Shared Documentation

Shared PHNEWS documentation is now stored on a dedicated GitHub documentation branch:

```text
Repository: zeoszeos/palmhillnews
Branch: phnews-shared-docs
```

This creates a common reference point for StevO, ChatGPT, Hermes, and Codex.

Shared docs should be updated when architecture or durable operating rules materially change.

Recommended shared set:

- `PHNEWS_SYSTEM_HANDBOOK_CURRENT.md`
- `PHNEWS_TONY_GUIDE_CURRENT.md`
- `PHNEWS_Hermes_Project_Handoff_2026-09-25.md`
- `PHNEWS_SHARED_DOCS_INDEX.md`

---

# 31. Major Lessons Worth Preserving

1. Visual PASS is not enough; test the canonical path.
2. Source attribution is not content completeness.
3. Missing retained source data is not proof the source does not exist.
4. Detail pages must derive from full source, not newsletter summary.
5. Extracted fact lists can still lose meaningful source content.
6. Fact-level provenance is necessary for mixed-source items.
7. Prior approved PHNEWS is not automatically the original factual source.
8. Verification failure is not proof a link is invalid.
9. Generated locally is not the same as publicly deployed.
10. Approval state outranks timestamp.
11. Shared rules should replace repeated one-off fixes.
12. Actual generated HTML must be inspected; QC JSON alone is not acceptance.

---

# 32. Current Immediate Next Steps

1. implement fact-level provenance QC
2. clean stale Craft Fair fallback phone typo
3. remove/tighten implicit default-source behavior
4. resolve Karaoke time discrepancy before final approval
5. regenerate Events - Upcoming newsletter + all detail pages
6. inspect actual HTML
7. obtain StevO acceptance
8. only then publish latest detail pages
9. verify public URLs
10. create approved reference baseline
11. move to next canonical heading

---

# 33. Final Operating Principle

PHNEWS should become easier to maintain after every defect.

The goal is not merely to make the next newsletter work.

The goal is to turn each discovered problem into:

- a clearer rule
- a better data model
- a shared component
- a stronger QC check
- a safer approval boundary
- a reusable piece of standard work

That is the direction of the PHNEWS system.


---

# Evidence, Conflict, and Change-Control Addendum — September 25, 2026

## A. Current path authority

**Claim type:** current-state / pending-verification

Handoff-declared primary project path:

```text
/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter
```

**Authority status:** PENDING LIVE FILESYSTEM/GIT VERIFICATION.

Older PHNEWS records identify other project and repository paths. Do not silently merge those histories or assume the newest remembered path is canonical.

Before code changes, verify candidate worktrees with:

```text
pwd
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git status
git log -1 --oneline
```

Record the resulting decision in the Evidence Ledger and resolve the corresponding Contradiction Register entry.

## B. Evidence-based section status

Do not use `locked`, `ready`, `stable`, or `close to acceptance` as a complete technical status.

For major sections, prefer:

```text
Section:
Canonical ID:
Implementation state:
Current renderer:
Source families:
Latest test/QC:
Latest artifact:
HTML inspected:
Editorial acceptance:
Publication state:
Known gaps:
Next action:
```

A section may simultaneously be IMPLEMENTED and still be awaiting FULL_QC_PASS, EDITORIALLY_ACCEPTED, or PUBLISHED_VERIFIED.

## C. Current Events - Upcoming status

**Claim type:** current-state  
**Status as of:** September 25, 2026

- Architecture and renderer work: IMPLEMENTED based on the September 25 Handoff.
- Full-fidelity `source_body` handling: reported IMPLEMENTED; live worktree/commit verification still required.
- Fact-level provenance / `fact_sources`: reported IMPLEMENTED; live worktree/commit verification still required.
- Preventive fact-level provenance QC: IN_PROGRESS / not yet established as FULL_QC_PASS.
- Latest local HTML: previously inspected during section review, but current regenerated post-QC artifact still requires final confirmation.
- Editorial acceptance: pending final StevO acceptance after remaining issues.
- Publication authorization: not granted for the latest local fixes.
- Public state: earlier six detail pages were deployed from merge commit `d058716faa58fa969393ceb2ad40c290130926a4`; newer local source-body/provenance/source-display changes are not assumed published.

Known remaining items:

1. implement preventive fact-level provenance QC;
2. clean stale Craft Fair fallback phone typo;
3. tighten/remove implicit default-source behavior;
4. resolve Karaoke time discrepancy;
5. regenerate section and six detail pages;
6. run structural/content/full-source/provenance QC;
7. inspect actual HTML;
8. obtain StevO acceptance;
9. publish only after explicit approval;
10. verify every public URL;
11. create approved Events - Upcoming baseline.

## D. Material conflict procedure

When sources, approved artifacts, implementation status, and editorial decisions disagree:

1. classify the question;
2. preserve both claims;
3. identify the relevant authority type;
4. verify evidence;
5. record material unresolved conflicts;
6. avoid silently promoting fallback evidence into factual authority;
7. seek StevO decision for consequential editorial/publication choices;
8. update all affected documents after resolution.

## E. Shared-document privacy

Never store in shared PHNEWS documentation:

- passwords
- API keys
- session cookies
- authentication tokens
- connection strings
- private Gmail URLs
- raw authentication headers
- unnecessary resident-private information
- unnecessary raw personal mailbox content

Use `[REDACTED]` where a security-related event must be documented.

## F. Change control

A durable rule change should identify its trigger, evidence, affected documents, and approval state.

Update:

- Handbook for durable rules;
- Tony Guide for stakeholder-facing explanation;
- Handoff for implementation state;
- Index for document structure/authority;
- Evidence Ledger for major claims;
- Contradiction Register for material conflicts.

Preserve prior versions through Git history.
