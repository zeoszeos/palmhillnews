# PHNEWS — How the Newsletter Logic Works
## Plain-Language Guide for Tony C.

**Prepared for:** Tony C.  
**Updated:** September 25, 2026  
**Purpose:** Explain in plain language how PHNEWS gathers, checks, organizes, summarizes, and publishes Palm Hill information.

---

# One-Page Overview

**What this guide is for:** This is the plain-language explanation of PHNEWS for Tony C. and other non-programmer stakeholders.

**What it is not:** This guide is not the technical source of truth for code status, commits, tests, deployment state, or publication authorization. Those details belong in the System Handbook, current Handoff, and evidence records.

## PHNEWS in one page

Palm Hill residents receive information from several places: Palm Hill emails and calendar entries, RPM notices, reports, attachments, reminders, corrections, and other community communications.

PHNEWS helps turn that stream into one organized resident reference.

```text
approved sources
    ↓
check dates, identity, corrections, and duplicates
    ↓
preserve the complete useful source information
    ↓
write a short resident-friendly newsletter summary
    ↓
provide a fuller detail page when useful
    ↓
quality check
    ↓
human review
    ↓
publish only after approval
```

The main ideas are:

- PHNEWS does **not** replace urgent official communications.
- It helps residents find current information without searching many separate messages.
- A short newsletter item and a fuller detail page can come from the same verified information.
- Different sources may support different facts, so PHNEWS should not claim more than a source actually proves.
- Human review remains part of the system.
- Technical PASS does not mean permission to publish or send.

StevO retains final editorial and publication authority.

---


# The Basic Idea

PHNEWS is a **supervised editorial pipeline**, not an unrestricted AI writer.

It collects information from approved sources, preserves the evidence, compares and classifies the material, prepares resident-friendly content, and stops for human review before publication or sending.

The governing principle is:

> **Use the strongest appropriate source, preserve the evidence, explain uncertainty internally, and never publish or send without review and approval.**

The resident-facing newsletter should be simple and useful. The complicated source checks happen behind the scenes.

PHNEWS should never expose private email links, internal notes, local computer paths, unresolved conflict labels, or other technical information to residents.

---

# Why We Built It

Palm Hill residents receive a steady stream of:

- Webmaster emails
- RPM notices
- meeting announcements
- event reminders
- maintenance updates
- reports
- corrections
- calendar entries
- attachments
- repeated follow-ups

A 90-day sample from June 23 through September 23, 2026 contained 170 direct Palm Hill/RPM messages in one resident mailbox — about 56 per month.

Some messages repeat or update earlier information.

PHNEWS is intended to turn that fragmented stream into a more useful weekly reference:

```text
many separate messages and calendar entries
        ↓
identify what is current and unique
        ↓
combine related evidence
        ↓
remove/suppress stale or superseded versions
        ↓
organize into familiar newsletter headings
        ↓
give residents concise summaries
        ↓
provide fuller detail links where useful
```

PHNEWS does not replace urgent official communications. It makes the overall information stream easier to follow and easier to find again.

---

# What Stays Stable

PHNEWS now has a **canonical newsletter framework**.

The familiar presentation is treated as reusable structure:

- Palm Hill masthead
- colors and overall layout
- standard section heading treatment
- At-a-Glance area
- footer
- resident reference material
- the established section order

The issue date/time changes for each issue.

The framework should not be rebuilt or restyled differently every time.

---

# The 13 Canonical Newsletter Headings

PHNEWS now recognizes these headings as the official ordered structure:

1. Committee & Board Meeting Schedules
2. Committee Chair Reports
3. Events - This Week
4. Regularly Scheduled Meetings & Events
5. Community Notices
6. RPM - Resource Property Management
7. Palm Hill Updates
8. Weekly Shareholders Report
9. Monthly Manager’s Report
10. Past Maintenance Events
11. Events - Upcoming
12. Did You Know?
13. Residents Reference Guide

Internally, each heading has a stable identity.

Its sequence number is only where it appears in the newsletter. The title residents see is the label.

This prevents an old review filename or temporary number from accidentally becoming the section’s identity.

---

# One Section, One Canonical Renderer

A major improvement is that PHNEWS should not have one version of a section for preview and another for the final newsletter.

The same canonical section output should be usable for:

- one-section review
- several-section review
- full newsletter assembly

That means when StevO approves a section, the final build should be using that same logic and formatting rather than reconstructing it later.

---

# The Assembler Is Kept Intentionally Simple

The final assembler should:

1. select the section IDs
2. use each section’s approved renderer
3. put the sections in registry order
4. insert them into the standard PHNEWS shell
5. run quality checks

The assembler should **not** start rewriting, summarizing, rediscovering, or restyling the content.

This is a major safeguard against regressions.

---

# Where the Information Comes From

PHNEWS uses several source families.

## Palm Hill Calendar and Public Pages

Used especially for:

- Palm Hill meetings
- events
- official dates
- official times
- official locations
- public event descriptions

The occurrence-level Calendar record is preferred over merely assuming a recurring series still applies.

## RPM / VANTACA

Used for:

- property-management information
- maintenance activity
- RPM notices
- RPM-controlled calendar information

## Approved Gmail Messages

Email can supply:

- committee reports
- management notices
- explanations
- cancellations
- updates
- supporting details
- contact information

Email is an internal source. Private Gmail URLs must never become resident links.

## Attachments

PDF, DOC, and DOCX attachments can contain the real substantive report or notice.

For a committee report, the attachment heading/content may be stronger evidence of the formal committee name than an informal email subject.

---

# Calendar = Skeleton; Email/Documents = Context

A useful way to understand PHNEWS is:

> **The Calendar often supplies the skeleton; email and documents supply the context.**

For example:

- Calendar may verify the occurrence, date, time, and place.
- Email may explain why it matters.
- A flyer may add cost and registration.
- A report may add the full narrative.

PHNEWS can merge those sources without pretending they all have equal authority for every fact.

---

# A Source Is Evidence, Not Automatically Truth

Sources can disagree.

Examples:

- an old forwarded email contains an outdated time
- a calendar occurrence changed
- a subject line uses an informal committee name
- a correction supersedes an earlier notice

PHNEWS retains the source evidence and applies source authority to the facts each source is qualified to control.

Important conflicts should be flagged for review instead of guessed.

---

# Source Recovery Order

When a source seems to be missing, PHNEWS should look in this general order:

1. current/live authoritative source
2. retained authoritative source
3. RPM/VANTACA when appropriate
4. current approved emails and attachments
5. other verified source material
6. prior approved PHNEWS output as a last-resort fallback

A source missing from a local cache does **not** prove the original source never existed.

---

# Resident-Facing Source Labels

When PHNEWS has a verified source, it can show a simple line such as:

```text
Source: Palm Hill Calendar
```

or:

```text
Sources: Committee chair email + Attached committee summary document
```

Residents should never see internal terms such as:

- Gmail message IDs
- local file paths
- internal provenance codes
- fallback database terminology
- private authenticated links

If the original source cannot be recovered, PHNEWS should generally omit the source line rather than invent one.

---

# A New Improvement: Source Attribution Can Be Fact-Specific

We recently found an important edge case.

An item can contain several facts, and different sources may support different facts.

Example: **PHLGA**

The currently retained event occurrence says:

- Friday, November 13, 2026
- 1:00 PM to 3:30 PM
- North Clubhouse

We have not recovered the original source that proves that occurrence.

However, the September Palm Hill LINK does verify:

- Sue Waldecker
- 248-842-1552

It would be misleading to write:

```text
Source: Palm Hill LINK
```

because that could imply the LINK proves the November 13 occurrence.

PHNEWS now supports a more precise line:

```text
Contact source: Palm Hill LINK — September 2026
```

This preserves useful verified information without overstating what the source proves.

That is an example of **fact-level source attribution**.

---

# Full Source Content Is Preserved

Another major improvement concerns detail pages.

Originally, PHNEWS could extract the main facts and create a clean detail page, but that could still omit meaningful sentences from the original Calendar description.

The better rule is:

> Preserve the complete substantive source description in the canonical record first.

PHNEWS now keeps the complete useful Calendar description before creating any shorter resident version.

The system then creates two different views from that same complete record:

```text
complete source record
      ↓                    ↓
newsletter summary        detail page
short                     complete
```

The newsletter is intentionally concise.

The detail page is intentionally complete.

---

# Newsletter Summary vs Full Detail Page

## In the Newsletter

Residents should see:

- title
- friendly date/time/location
- short summary
- the important 5W+How when available
- link to more information
- verified source label where appropriate

The summary should usually fit in about 3–4 lines.

## On the Detail Page

The fuller page should preserve substantive source details such as:

- full event description
- contact person
- phone
- price
- how to register
- warnings
- start/end location
- duration
- eligibility
- organizer
- special instructions

This keeps the newsletter easy to scan without throwing away source information.

---

# Dates Are Standardized

Internally PHNEWS can store:

```text
2026-10-24
```

Residents should see:

```text
Saturday, October 24, 2026
```

This avoids ambiguous dates such as:

```text
10/11/26
```

If the weekday is shown, PHNEWS derives it from the canonical date.

If an incoming date is genuinely ambiguous, PHNEWS should stop and resolve it rather than guess.

---

# Events - This Week and Events - Upcoming

The current event-window rule is simple and non-overlapping.

## Events - This Week

Day 0 through Day 8 inclusive.

## Events - Upcoming

Day 9 through Day 60 inclusive.

The anchor is the newsletter’s canonical issue/build date.

This prevents an event from appearing in both sections or falling through a gap.

---

# Community Notices

Community Notices are announcements whose main purpose is **awareness, action, recognition, or general community information**, rather than attendance at a scheduled event.

Examples:

- road/street closures
- parking restrictions
- office closings
- trash/holiday changes
- maintenance disruptions
- volunteer requests
- deadlines
- registrations
- ticket sales
- lost and found
- resident reminders
- service/safety information

A scheduled event belongs in an event section when attendance at a specific date/time is the main point.

Some Community Notices stay active until resolved or expired instead of disappearing after a single issue.

---

# Regularly Scheduled Meetings & Events

This section has intentionally become a navigation hub instead of one enormous list.

Residents can use:

```text
By Date →
By Name →
Palm Hill Calendar →
```

The system uses a rolling 30-day set of recurring activities.

The same filtered data drives the By Date and By Name views so those pages do not drift apart.

---

# Public Detail Pages and Links

When fuller information is useful, PHNEWS can generate a resident-safe public detail page.

But a generated local file is not automatically a live public page.

The stages are:

```text
generated locally
→ placed in deployment tree
→ committed
→ pushed to GitHub
→ deployed by Vercel
→ publicly verified
```

Only after the public page is actually verified should the newsletter treat its link as publication-ready.

This distinction has prevented several false-PASS situations.

---

# Review Does Not Mean Resident-Facing “Draft” Banners

PHNEWS still has a local review stage.

However, internal status belongs in:

- run reports
- manifests
- QC reports
- logs

The resident-facing newsletter itself should not contain technical banners such as:

- LOCAL REVIEW
- PROOF COPY
- NOT EMAILED
- NOT FOR PUBLICATION
- DRAFT

That keeps the actual newsletter presentation clean and prevents internal workflow labels from leaking into resident content.

---

# Quality Checks Are Now More Than “Does It Look Good?”

PHNEWS separates several kinds of quality checks.

## Structural

- correct headings
- correct order
- correct renderer
- no duplicates
- no missing canonical sections in review
- no placeholders

## Content Completeness

- important source facts preserved
- contact details preserved
- cost preserved
- instructions preserved
- detail page more complete than summary
- no meaningful source statements silently dropped

## Provenance

- source is verified
- source label matches the facts it actually supports
- fallback/internal labels stay internal
- a source does not get credit for facts it did not prove

Actual generated HTML is still inspected by a human. Automated PASS does not replace visual acceptance.

---

# Why Root Cause Matters

When something is wrong, the goal is not to patch only that one newsletter row.

The preferred method is:

```text
find visible problem
    ↓
find root cause
    ↓
fix shared logic/data model
    ↓
add a QC check
    ↓
regenerate
    ↓
inspect actual HTML
```

That way, the defect teaches PHNEWS how to become more reliable.

---

# Example: What We Learned from Events - Upcoming

Events - Upcoming recently exposed several important issues.

We corrected or clarified:

- full Calendar descriptions must be preserved
- source labels must appear in both newsletter and detail pages
- a source label must not overclaim what the source proves
- missing metadata can be a data defect rather than a legitimate no-source condition
- local generation is not the same as public deployment
- a detail page must contain more complete information than the newsletter summary

Current source behavior:

- Karaoke Obi-Time — Palm Hill Calendar
- Halloween Golf Cart Parade — Palm Hill Calendar
- Nickels — Palm Hill Calendar
- North Clubhouse Craft Fair — Palm Hill Calendar
- PHLGA — Contact source: Palm Hill LINK — September 2026; event occurrence source still unresolved
- Pancakes Breakfast — source line omitted until original source is recovered

---

# Approval Matters More Than “Newest File”

Another important safeguard is:

> **The latest approved artifact wins — not simply the newest generated file.**

A newer build can contain a regression.

Once a section or complete newsletter is approved, that approved artifact should be kept as a reference.

The next build is compared against it.

A deliberate re-approval is required before replacing the baseline.

---

# Human Review and Publication Boundaries

The conceptual workflow is now:

```text
collect current sources
    ↓
normalize/reconcile
    ↓
build canonical section data
    ↓
generate detail pages locally
    ↓
assemble standard PHNEWS shell
    ↓
run structural/content/provenance QC
    ↓
human review
    ↓
explicit approval to publish
    ↓
deploy/verify public pages
    ↓
re-render with verified public links
    ↓
final approval
    ↓
send exact approved artifact
```

PHNEWS should not use live publication or email sending as a debugging step.

---

# Current General Section Status

As of September 25:

- **Committee Chair Reports** — stable current direction
- **Events - This Week** — shared theme, Day 0–8 rule
- **Regularly Scheduled Meetings & Events** — navigation-hub concept stable
- **Community Notices** — current classification and Active-Until-Resolved logic established
- **RPM - Resource Property Management** — currently valid empty
- **Palm Hill Updates** — currently valid empty
- **Weekly Shareholders Report** — stable current direction
- **Monthly Manager’s Report** — currently valid empty; may show full report/document as an exception
- **Past Maintenance Events** — still needs canonical renderer stabilization
- **Events - Upcoming** — close to acceptance; still finishing preventive provenance QC/cleanup
- **Did You Know?** — stable guidance topics
- **Residents Reference Guide** — stable special-layout section

---

# What the Current Work Is Trying to Achieve

PHNEWS is becoming less dependent on one person remembering every exception.

The system is increasingly built around:

- one canonical shell
- one section registry
- shared design components
- reusable renderers
- full source preservation
- concise resident summaries
- complete detail pages
- explicit source provenance
- fact-level source attribution
- quality gates
- approved baselines
- safe publication boundaries

In plain language:

> We are turning the newsletter from a collection of scripts and remembered rules into a maintainable publishing system.

That should make it easier for StevO, Tony, Hermes, Codex, or a future maintainer to understand why the newsletter behaves the way it does.

---

# Shared Documentation

The current shared PHNEWS documents are maintained in:

```text
GitHub repository: zeoszeos/palmhillnews
Branch: phnews-shared-docs
```

The shared documentation is intended to keep StevO, ChatGPT, Hermes, Codex, and future maintainers working from the same rules rather than passing large blocks of text back and forth.



---

# Document Authority and Maintenance Note

This Tony Guide is authoritative for **plain-language explanation**, not technical implementation state.

When a technical detail changes, the System Handbook and current Handoff should be updated first. This Guide should be updated only when the change affects how a stakeholder should understand PHNEWS.

If this Guide conflicts with verified source evidence, an approved artifact, StevO's explicit decision, the durable System Handbook, or a newer reconciled Handoff, report the contradiction rather than silently deciding that this Guide wins.

Technical evidence identifiers, commit SHAs, test names, and detailed provenance codes should generally remain outside this Guide so it stays readable.

A good acceptance test is:

> Could Tony accurately explain PHNEWS to another committee member after reading this guide once?
