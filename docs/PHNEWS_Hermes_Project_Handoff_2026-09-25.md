# Handoff Authority and Snapshot Metadata

**Handoff date:** September 25, 2026  
**Document role:** Point-in-time implementation snapshot  
**Repository for shared documentation:** `zeoszeos/palmhillnews`  
**Documentation branch:** `phnews-shared-docs`  
**Handoff source commit:** documentation snapshot as maintained on `phnews-shared-docs`; verify current branch history before relying on a specific SHA  
**Handoff-declared primary worktree:** `/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter`  
**Worktree authority:** PENDING LIVE FILESYSTEM/GIT VERIFICATION  
**Last verified public Events - Upcoming deployment in this handoff:** merge commit `d058716faa58fa969393ceb2ad40c290130926a4` for the earlier six-page deployment  
**Latest local build/QC:** see current local artifacts and reports; live filesystem verification required before claiming current-state PASS  
**Last approved full-newsletter reference:** September 21, 2026 reference artifact as previously identified; approval-package formalization remains planned  
**Unresolved issues:** see the Immediate Next Steps, Evidence Ledger, and Contradiction Register

> This Handoff is a dated snapshot, not permanent law. It must not override later verified source evidence, later Git state, later approved artifacts, later System Handbook decisions, or explicit StevO decisions.

> Reading this Handoff does not authorize code changes, publication, deployment, sending email, or overwriting approved artifacts.

---

# PHNEWS / Palm Hill Newsletter — Hermes Project Handoff
## Detailed Progression, Architecture, Decisions, Current State, and Next Steps

**Prepared for:** Hermes  
**Project:** Palm Hill Country Club Newsletter / PHNEWS  
**As of:** September 25, 2026  
**Handoff-declared primary working project:** `/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter`  
**Path authority:** PENDING LIVE FILESYSTEM/GIT VERIFICATION  
**Primary reviewer / product owner:** StevO

> HERMES: Treat this file as the current PHNEWS handoff. Read it fully before making changes. Preserve the architecture, rules, paths, provenance logic, QC requirements, approval controls, and unresolved issues unless StevO explicitly changes them.

---

# 1. Executive Summary

PHNEWS has moved from a collection of partially independent scripts and section-specific behaviors toward a controlled publishing pipeline.

Current target flow:

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

Durable principles:

- one canonical shell
- one canonical ordered section registry
- one renderer/data path per section
- shared theme/components
- one assembly process
- stable section IDs separate from display order/title
- full-fidelity canonical source records
- concise newsletter summaries
- complete detail-page projections
- explicit provenance
- fact-level provenance where needed
- reusable QC
- approval/reference baselines
- no silent source-content loss
- no invented or guessed sources
- no internal/local paths exposed to residents
- no publication without explicit approval

Working philosophy:

> **Strict internally, forgiving externally.**

Residents should see clean, readable content. Internally PHNEWS should be strict about provenance, completeness, dates, event windows, source attribution, link readiness, approval state, and regression detection.

---

# 2. Roles

## StevO
Product Owner / Domain Lead / Editorial Lead / final acceptance authority.

StevO decides:
- resident-facing appropriateness
- newsletter inclusion
- wording
- visual acceptance
- source acceptance
- section approval
- publication approval

## ChatGPT
Business Analyst / Solution Architect / Editorial partner / QA-QC designer / root-cause partner / Codex prompt author.

## Codex
Developer / implementation agent / code troubleshooter / renderer-data-path modifier / local artifact generator / test runner.

Preferred loop:

```text
StevO → ChatGPT → Codex → ChatGPT + StevO review → StevO approval
```

---

# 3. Canonical Architecture

The assembler should be deliberately simple:

1. select canonical section IDs
2. invoke canonical section renderers
3. order via registry
4. insert returned fragments into the shell
5. output
6. run QC

Assembler must NOT:
- summarize
- rewrite
- rediscover
- reconstruct missing content
- restyle sections independently
- infer sources
- invent links

The same canonical section fragment must support:
- one-section review
- multi-section review
- full newsletter assembly

No separate fake preview renderer. Preview = real PHNEWS build with selected sections.

---

# 4. Stable Identity vs Presentation

Permanent distinction:

- stable internal ID = identity
- sequence number = presentation order
- resident-facing title = label

Example:
- key: `upcoming_events`
- title: **Events - Upcoming**
- sequence: 11

In user-facing discussion prefer heading titles, not section numbers.

---

# 5. Canonical Section Registry

Authoritative order:

1. `committee_board_meetings` — Committee & Board Meeting Schedules
2. `past_committee_board_summaries` — Committee Chair Reports
3. `whats_up_this_week` — Events - This Week
4. `regularly_scheduled_events` — Regularly Scheduled Meetings & Events
5. `community_announcements` — Community Notices
6. `rpm_updates` — RPM - Resource Property Management
7. `palm_hill_updates` — Palm Hill Updates
8. `shareholders_weekly` — Weekly Shareholders Report
9. `shareholders_monthly` — Monthly Manager’s Report
10. `past_maintenance_events` — Past Maintenance Events
11. `upcoming_events` — Events - Upcoming
12. `did_you_know` — Did You Know?
13. `permanent_utility_hub` — Residents Reference Guide

Registry owns:
- section identity
- order
- resident title
- controlled heading metadata such as `heading_variant`, `heading_icon`

Shell does not own order.

---

# 6. Canonical Shell / Visual Reference

Known-good reference:

```text
/mnt/d/TEMP/Palm Hill CC/Palm Hill Newsletter/
Palm_Hill_Newsletter_2026-09-21_20260921_091336.html
```

Preserve:
- ~660px email layout
- Palm Hill masthead
- palm trees
- Updated timestamp
- gold tagline band
- address band
- This Week At A Glance
- established fonts/colors
- tables/spacing
- rounded container
- footer

Header/footer/At-a-Glance are framework-level, not numbered sections.

---

# 7. Shared Theme / Components

Implemented:
- `phnews_canonical/theme.py`
- `phnews_canonical/components.py`

Shared helper:
```python
render_section_header(title, icon=None, variant="standard")
```

Theme centralizes:
- heading background
- title color
- title size/weight
- padding/margins
- border radius
- icon spacing
- reusable typography
- reusable link styling

Do not duplicate ordinary heading CSS inside renderers.

Residents Reference Guide remains a valid special-layout exception.

---

# 8. Review / Empty-State Behavior

Review/test builds should expose all 13 canonical sections to prevent silent omissions.

Valid-empty review text:
```text
No qualifying current items.
```

Production may omit valid-empty sections.

Current valid-empty examples:
- RPM - Resource Property Management
- Palm Hill Updates
- Monthly Manager’s Report

---

# 9. QC Model

## Structural QC
Examples:
- expected section exists
- canonical renderer used
- shared theme/header used
- no duplicate wrappers
- no stale unrelated content
- correct order
- correct windows
- no overlap/gap

## Content Completeness QC
Examples:
- summary captures important 5W+How
- detail page preserves substantive source facts
- cost/contact/organizer/instructions preserved
- detail not less complete than summary
- no silent substantive omission

## Provenance QC
Examples:
- source verified
- source label matches fact origin
- fallback provenance does not leak resident-facing
- source label does not overclaim
- supporting fact sources retained

Status vocabulary:
- PASS — populated
- PASS — valid empty / intentionally omitted
- FAIL — unresolved expected content
- FAIL — placeholder
- FAIL — stale/superseded

---

# 10. Resident-Facing Date Rule

Internal dates may remain ISO:
```text
YYYY-MM-DD
```

Resident-facing preferred:
```text
Wednesday, October 7, 2026
```

Shorter if needed:
```text
October 7, 2026
```

Never show ambiguous numeric dates.

If weekday shown:
- derive from canonical date
- if source weekday disagrees, flag QC
- use derived correct weekday

If incoming numeric date is ambiguous:
- do not guess
- resolve from authoritative context
- otherwise flag

Shared helper:
```python
format_resident_date(...)
```

---

# 11. Event Window Rules

## Events - This Week
Day 0 through Day 8 inclusive.

## Events - Upcoming
Day 9 through Day 60 inclusive.

Anchor = canonical newsletter issue/build date.

Do not use:
- scrape date
- source date
- stale newsletter date
- cache timestamp

Required checks:
- `canonical_build_date_used`
- `this_week_window_0_8`
- `upcoming_window_9_60`
- `no_event_window_overlap`
- `no_event_window_gap`

---

# 12. Newsletter Summary vs Detail Page Contract

## Newsletter
Concise resident scan:
- title
- resident-friendly date/time/location
- 3–4 line max summary generally
- important 5W+How
- detail link
- source line(s) when verified

Newsletter should not dump the full source.

## Vercel detail page
Preservation-oriented:
- complete substantive verified source content
- descriptions
- names
- phones
- prices
- registration instructions
- organizer/sponsor
- duration
- start/end locations
- eligibility
- warnings/reminders
- special notes
- source attribution

Formatting may improve readability. Substantive information may not disappear.

---

# 13. Full-Fidelity Source Body

Major defect discovered:
detail generation previously preferred reconstructed fields such as `public_detail` / `full_detail` / summary. This allowed source sentences to disappear before rendering.

Correction:
introduce `source_body`.

For Palm Hill Calendar items, `source_body` should preserve the complete substantive Calendar Description.

Target pattern:

```text
verified authoritative source
        ↓
source_body / complete source description
        ↓
canonical full-fidelity item
        ↓                         ↓
newsletter summary               Vercel detail page
short projection                 complete projection
```

Detail generator should prefer `source_body`.

---

# 14. Events - Upcoming — Pilot Section

Current event set:
1. Karaoke Obi-Time
2. Halloween Golf Cart Parade
3. Nickels
4. North Clubhouse Craft Fair
5. PHLGA
6. Pancakes Breakfast

Presentation direction:
- centered dark-green rounded section header
- event/calendar icon
- white title
- subtitle: `A look ahead — Next 60 Days`
- alternating event rows
- named-month dates
- concise summaries
- Vercel detail links
- resident-facing source labels where verified

Windows review:
```text
C:\Users\leono\Desktop\PHNEWS-Previews\PHNEWS-Events-Upcoming-Preview.html
```

Detail review:
```text
C:\Users\leono\Desktop\PHNEWS-Previews\Vercel-Publish\
```

Generated WSL detail source:
```text
/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter/
phnews_canonical/generated_details/
```

---

# 15. Earlier Public Vercel Deployment

Repository:
```text
zeoszeos/palmhillnews
```

Real local checkout:
```text
/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter/repos/palmhillnews
```

Earlier branch:
```text
phnews-events-upcoming-publish
```

Earlier PR:
```text
PR #1 — Publish Events - Upcoming detail pages
```

Earlier merge commit:
```text
d058716faa58fa969393ceb2ad40c290130926a4
```

Important:
newer local fixes after that publication are NOT yet published, including latest source-body, provenance, date-format, source-display, and fact-level source work.

---

# 16. Publication Readiness Rule

Distinguish:

```text
generated locally
≠ copied to deploy tree
≠ committed
≠ pushed
≠ deployed
≠ publicly verified
```

Public readiness requires:
1. generated
2. staged in deploy tree
3. committed
4. pushed
5. deployed
6. publicly verified
7. newsletter href matches deployed destination

---

# 17. Source Classes

Controlled source vocabulary includes:
- Palm Hill Calendar
- RPM Calendar / VANTACA
- Webmaster email
- RPM management email
- Committee chair email
- Committee chair report
- Board/committee meeting notice
- Weekly Manager Report
- Monthly Manager Report
- Attached report
- Attached committee summary document
- Event flyer
- Resident/organizer submission
- Meeting recording

Prior approved PHNEWS output is reference/control provenance, not automatically the original source.

---

# 18. Provenance States

```text
VERIFIED_CURRENT_SOURCE
VERIFIED_RETAINED_SOURCE
PROVENANCE_FALLBACK_ONLY
SOURCE_DATA_DEFECT
```

## VERIFIED_CURRENT_SOURCE
Current/live authoritative source verified now.

## VERIFIED_RETAINED_SOURCE
Authoritative source preserved in retained data.

## PROVENANCE_FALLBACK_ONLY
Only prior approved PHNEWS artifact remains for occurrence/fact.
General resident-facing source line normally omitted.

## SOURCE_DATA_DEFECT
Verified source exists but canonical record lacks/incorrectly configures source metadata.

---

# 19. Source Recovery Order

For missing source:
1. live authoritative source
2. retained authoritative source
3. RPM/VANTACA
4. webmaster/RPM/management email
5. attached flyer/PDF/notice
6. resident/organizer submission
7. approved prior PHNEWS artifact as last resort

Critical:
> Missing retained data does not prove a source does not exist.

---

# 20. Source Display Rules

One verified source:
```text
Source: Palm Hill Calendar
```

Multiple verified sources:
```text
Sources: Source A + Source B
```

Verified public source names may be links.

Never expose:
- Gmail IDs
- WSL/local paths
- internal source IDs
- temporary review URLs
- `Approved manual correction`
- `approved prior record`
- `PROVENANCE_FALLBACK_ONLY`

---

# 21. Fact-Level Source Attribution

Major improvement: item-level provenance was too coarse.

An item can have:
- occurrence facts with one provenance state
- contact facts from another source
- flyer/email details from another source

New model:
```text
fact_sources
```

Concept:
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

This enables:
```text
Contact source: Palm Hill LINK — September 2026
```

without claiming that the LINK verifies the whole event occurrence.

---

# 22. PHLGA Current State

Occurrence facts retained:
- Friday, November 13, 2026
- 1:00 PM to 3:30 PM
- North Clubhouse

Original occurrence source not recovered.

Occurrence provenance:
```text
PROVENANCE_FALLBACK_ONLY
```

Separately verified contact:
- Sue Waldecker
- 248-842-1552

Supporting source:
```text
Palm Hill LINK — September 2026
```

That source supports the contact, but NOT:
- November 13 occurrence
- 1:00–3:30 PM
- North Clubhouse

Resident-facing intended behavior:
```text
Sue Waldecker — 248-842-1552
Contact source: Palm Hill LINK — September 2026
```

No general Source line for the occurrence.

---

# 23. Pancakes Breakfast Current State

Fallback facts:
- Saturday, November 14, 2026
- 8:30 AM to 10:00 AM

Original source unrecovered.

Do not invent:
- location
- organizer
- cost
- source
- description

Provenance:
```text
PROVENANCE_FALLBACK_ONLY
```

Resident-facing source line:
OMIT.

---

# 24. Karaoke Obi-Time Current State

Verified Palm Hill Calendar content includes:
- Chuck and Sandy Obi
- phone number
- singing/dancing
- thousands of songs
- North Clubhouse
- full source time wording

Complete retained calendar description now stored in `source_body`.

Resident source:
```text
Source: Palm Hill Calendar
```

---

# 25. Halloween Golf Cart Parade Current State

Verified Palm Hill Calendar details:
- Saturday, October 24, 2026
- North Clubhouse
- lineup 6:30 PM
- start 7:00 PM
- ends South Clubhouse
- batteries fully charged
- approx. 1½ hours start to finish

Full supplied calendar description preserved in `source_body`.

An earlier Recreation Club sponsorship detail came from fallback content, not the calendar, and was removed resident-facing because attribution could not be verified.

Resident source:
```text
Source: Palm Hill Calendar
```

---

# 26. Nickels Current State

Occurrence:
- Wednesday, October 28, 2026
- 6:30 PM
- North Clubhouse

Retained calendar description is empty.

Defect found:
Nickels relied on implicit generator default instead of explicit source metadata.

Correction:
explicit verified Palm Hill Calendar source record added.

Resident source:
```text
Source: Palm Hill Calendar
```

This was a SOURCE_DATA_DEFECT, not a valid missing-source case.

---

# 27. North Clubhouse Craft Fair Current State

Verified calendar content includes:
- Saturday, November 7, 2026
- 9 AM–1 PM
- North Clubhouse
- invitation to crafters
- opportunity to sell crafts
- $20 table rental
- Tom Sagitas
- 727-315-4369
- Home # notation
- instruction to book/reserve table
- Brenda Sagitas appears in retained source content

Full calendar description now in `source_body`.

Newsletter stays concise.
Detail page preserves full substantive content.

Resident source:
```text
Source: Palm Hill Calendar
```

Important cleanup:
an intermediate stale `full_detail` contained apparent typo:
```text
727-315-436-4369
```
Authoritative `source_body` has:
```text
727-315-4369
```
Current detail rendering should be correct because source_body outranks full_detail, but stale fallback value should still be cleaned.

---

# 28. Source Display RCA

## Root cause
Technical:
both render paths relied primarily on item-level source rendering. When fallback-only items suppressed unverified general sources, legitimate supporting source evidence could be hidden.

Data model:
no fact-level/scoped provenance.

QC gap:
item-level source visibility was checked, but verified supporting fact attribution was not.

## Corrective action
Implemented:
- `fact_sources`
- `render_fact_sources()`

PHLGA now supports:
```text
Occurrence: fallback-only
Contact source: Palm Hill LINK — September 2026
```

---

# 29. Preventive Provenance QC — Next

Implement shared checks:
```text
fact_source_scope_valid
source_label_does_not_overclaim_scope
verified_supporting_fact_source_preserved
fallback_occurrence_not_mislabeled
resident_source_scope_matches_fact_origin
```

These are intended to prevent the same class of provenance error in other sections.

---

# 30. Full Calendar Description QC

Shared concepts:
```text
calendar_description_captured
calendar_description_not_truncated
source_body_to_detail_completeness
all_substantive_source_lines_represented
detail_derived_from_full_source_not_summary
newsletter_summary_is_separate_projection
```

PASS means every substantive statement from the verified Calendar Description is represented in the detail page.

---

# 31. Other Shared QC Concepts

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
verified_source_provenance
no_internal_provenance_leak
detail_page_more_complete_than_summary
detail_page_contains_all_summary_facts
detail_page_contains_all_verified_source_facts
detail_page_not_less_complete_than_section_summary
source_attribution_matches_fact_origin
no_source_claim_for_unverified_fact_origin
```

Consolidate into shared QC rather than renderer-specific checks.

---

# 32. Current Events - Upcoming Source Display

Expected:

Karaoke Obi-Time:
```text
Source: Palm Hill Calendar
```

Halloween Golf Cart Parade:
```text
Source: Palm Hill Calendar
```

Nickels:
```text
Source: Palm Hill Calendar
```

North Clubhouse Craft Fair:
```text
Source: Palm Hill Calendar
```

PHLGA:
```text
Contact source: Palm Hill LINK — September 2026
```
No general Source line.

Pancakes Breakfast:
no source line.

---

# 33. Community Notices Lessons

A detail-page contract was introduced here too.

Relevant:
- `phnews_canonical/detail_pages.py`
- `phnews_canonical/generated_details/manifest.json`
- `phnews_canonical/publish_to_vercel.py`

Important rule:
do not use stale `previous_public_url` as authoritative current-build link state.

For substantive detail pages:
- regenerate/refresh every build
- retain stable URL for same canonical item
- current-build manifest is authoritative
- deploy
- verify publicly
- then mark link ready

---

# 34. Regularly Scheduled Meetings & Events

Navigation hub, not event index.

Title:
```text
Regularly Scheduled Meetings & Events
```

Subtitle:
```text
Regular Palm Hill meetings and events scheduled over the next 30 days.
```

Links:
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

Same filtered dataset drives By Date and By Name.

---

# 35. Other Section Status

## Committee Chair Reports
Locked/ready.
Known current set:
- Golf Advisory Committee
- Planning and Environmental
- Real Estate
- Rules and Regulations

## Events - This Week
Uses `render_whats_up_this_week()`, shared theme/header, Day 0–8 window.

## Community Notices
Qualifying items have included:
- Block captain is needed
- Bingo Volunteers Needed
- Bocce Play Is Weather-Dependent
- Bring Your Clubhouse Fob

Uses Active-Until-Resolved.

## RPM - Resource Property Management
Valid empty.

## Palm Hill Updates
Valid empty.

## Weekly Shareholders Report
Locked/ready, shared theme.

## Monthly Manager’s Report
Valid empty.
Editorial exception: full report/document may be shown in newsletter and linked to original PDF.

## Past Maintenance Events
Known qualifying examples:
- North Spa is open
- North Clubhouse Updates
Still needs canonical renderer work.

## Did You Know?
Persistent topics:
- submit VANTACA service request
- view a meeting on Zoom

## Residents Reference Guide
Locked/ready, intentional special layout.

---

# 36. Accessibility Parking Lot

After newsletter milestone:
- larger fonts
- theme variants
- high contrast
- screen-reader structure
- keyboard navigation
- larger touch targets
- descriptive links
- optional listen/TTS button

Distinction:
- PHNEWS Theme = appearance/design system
- Accessibility Layer = usability/inclusion constraints

---

# 37. Desired Future Commands

```text
phsection 4
phsection regularly_scheduled_events
phsection "Regularly Scheduled Meetings & Events"
phsection 4-7
phsection 2,4,8
phsection list
phbuild
```

Defer until canonical milestone is stable.

---

# 38. Important Paths

Primary working project:
```text
/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter
```

Canonical files:
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

Old/snapshot code:
```text
/mnt/d/TEMP/phnews-unified-dev-snapshot/phnews
```

Snapshot deploy tree:
```text
/mnt/d/TEMP/phnews-unified-dev-snapshot/palmhillnews
```

Historic output:
```text
/mnt/d/TEMP/Palm Hill CC/Palm Hill Newsletter
```

Backups:
```text
/mnt/d/Backups/PHNEWS
/home/leono/phnews-backups
```

Windows preview:
```text
C:\Users\leono\Desktop\PHNEWS-Previews
```

---

# 39. Approval / Reference Layer

Planned:

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

Principle:

> Latest Approved Artifact wins — not latest file and not automatically latest build.

New approved full newsletter becomes current whole-newsletter reference.
Older approved packages are archived, never overwritten.

Fallback reference may provide visual/presentation baseline only.
Never roll back current business rules, source data, QC, dates, components, or link logic.

---

# 40. Major Lessons Learned

1. Visual PASS is not enough.
2. Source attribution and content completeness are separate dimensions.
3. Missing local cache data is not proof a source does not exist.
4. Detail pages must not be generated from newsletter summaries.
5. Extracted fact lists are not enough when the authoritative source body is richer.
6. Fact-level provenance matters.
7. Prior approved PHNEWS output is not automatically the original factual source.
8. Verification failure is not proof a link is invalid.
9. Local generation is not publication.
10. Latest file is not authority; approval state is.

---

# 41. Root-Cause / Corrective-Action Pattern

Preferred:

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
user acceptance
```

Avoid:
```text
observe defect → patch one HTML file → move on
```

---

# 42. Immediate Next Steps

1. Implement preventive fact-level provenance QC:
   - `fact_source_scope_valid`
   - `source_label_does_not_overclaim_scope`
   - `verified_supporting_fact_source_preserved`
   - `fallback_occurrence_not_mislabeled`
   - `resident_source_scope_matches_fact_origin`

2. Clean stale Craft Fair fallback typo:
   - wrong intermediate value: `727-315-436-4369`
   - authoritative value: `727-315-4369`

3. Regenerate Events - Upcoming:
   - newsletter section
   - all six detail pages
   - content QC
   - provenance QC

4. Inspect actual HTML, not only JSON/tests.

5. StevO final visual acceptance.

6. If approved:
   - stage current detail pages into real deploy repo
   - commit
   - push/merge
   - allow Vercel deployment
   - verify every public URL
   - verify newsletter hrefs match live destinations

7. Create approved Events - Upcoming baseline only after acceptance.

8. Then move to next canonical heading.

---

# 43. Do Not Do Yet

Until current Events - Upcoming acceptance is complete:
- do not reorganize Vercel repo
- do not migrate old URLs
- do not build complex menus
- do not start broad accessibility work
- do not replace canonical architecture with old scripts
- do not patch obsolete v2 builds
- do not overwrite approved baseline prematurely
- do not publish merely because automated QC says PASS

---

# 44. Parked Vercel Repository Reorganization

Future goal:
stop using one giant flat `pages/` directory.

Potential organization:
- content type
- year
- month

Requirements:
- inventory existing pages
- preserve stable URLs
- use redirects when needed
- migration manifest
- zero broken links
- no silent URL changes

Do this only after current architecture is stable.

---

# 45. Hermes Operating Guidance

When continuing PHNEWS:

1. Prefer the canonical project under:
   `/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter`

2. Treat old snapshot scripts as reference, not authority.

3. Do not recreate content in assembler.

4. Do not use short newsletter summary text as detail-page source.

5. Preserve complete authoritative source bodies.

6. Keep resident-facing output simple.

7. Keep provenance strict internally.

8. Do not invent source labels.

9. Do not expose internal provenance terms resident-facing.

10. Use fact-scoped sources when an item mixes provenances.

11. Run shared QC.

12. Inspect actual generated HTML.

13. Do not publish unless StevO explicitly approves.

14. After approval, preserve the accepted artifact as the next baseline rather than overwriting history.

---

# 46. Current Milestone

PHNEWS is being converted from a loose collection of scripts into a controlled publishing pipeline with:

- canonical identity
- canonical order
- shared design system
- reusable components
- full-fidelity source preservation
- concise resident summaries
- complete detail pages
- explicit provenance
- fact-level attribution
- reusable QC
- approval baselines
- staged publication
- regression prevention

The guiding principle is:

> Turn lessons from individual defects into shared program behavior.


---

# 47. Claim / Evidence Status Addendum

This section distinguishes implementation claims from acceptance claims.

## Canonical worktree

**Claim type:** current-state / unresolved  
**Status:** PENDING LIVE FILESYSTEM/GIT VERIFICATION  
**Declared path:** `/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter`  
**Evidence needed:** `pwd`, Git top-level, remotes, branch, status, and latest commit for each plausible worktree.

## `source_body`

**Claim type:** current-state  
**Reported state:** IMPLEMENTED  
**Evidence currently available:** this Handoff's recorded local implementation behavior and generated-detail review history.  
**Evidence still needed:** live worktree/commit/test verification before upgrading the claim to fully verified current implementation.

## Fact-level provenance / `fact_sources`

**Claim type:** current-state  
**Reported state:** IMPLEMENTED  
**Known behavior:** PHLGA contact source is scoped to the contact fact; fallback occurrence is not given a general source label.  
**Evidence still needed:** live worktree/commit verification and preventive fact-level provenance QC.

## Events - Upcoming

**Claim type:** current-state  
**Implementation:** reported IMPLEMENTED  
**Focused behavior:** locally reviewed  
**Preventive provenance QC:** still pending/in progress  
**Editorial acceptance:** pending final review after remaining defects  
**Publication authorization for latest local fixes:** not granted  
**Published state:** earlier six-page public deployment exists; newer local fixes are not assumed published.

## 170-message statistic

**Claim type:** pending-verification  
**Reported historical result:** 170 messages, reported as 126 Palm Hill + 44 RPM, June 23 through September 23, 2026.  
**Reproduction attempt:** September 25, 2026 live query using the currently documented exact sender addresses produced 154 Palm Hill results and 0 results for the currently documented RPM sender address.  
**Interpretation:** the original statistic is not disproven; its original query/report and sender definitions are not yet preserved well enough for reproducibility.  
**Action:** recover or reconstruct durable evidence before treating the statistic as VERIFIED_CURRENT.

## Conflict handling

If this Handoff conflicts with:

- live authoritative source evidence;
- current verified Git state;
- a later approved artifact;
- a later durable Handbook decision;
- explicit StevO direction;

record the conflict and reconcile it rather than treating this dated Handoff as controlling.
