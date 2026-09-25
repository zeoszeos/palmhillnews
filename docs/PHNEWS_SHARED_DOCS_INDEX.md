# PHNEWS Shared Documentation Index

**Repository:** `zeoszeos/palmhillnews`  
**Branch:** `phnews-shared-docs`  
**Updated:** September 25, 2026  
**Document role:** Navigation, authority map, and documentation-maintenance standard  
**Authority:** This Index defines how the shared PHNEWS documentation set is used. It does not override verified source evidence, approved artifacts, StevO's explicit editorial/publication decisions, or the durable rules in the System Handbook.

This branch is the shared documentation workspace for PHNEWS. It is intentionally separate from the live `main` deployment branch.

---

## 1. Primary Documents

### PHNEWS System Handbook
`docs/PHNEWS_SYSTEM_HANDBOOK_CURRENT.md`

**Authoritative for:** durable architecture, editorial rules, provenance rules, QC rules, approval boundaries, and operating principles.

**Not authoritative for:** whether a particular current build is actually implemented, tested, accepted, deployed, or publicly verified. Use the current Handoff and evidence records for that.

### Tony Guide
`docs/PHNEWS_TONY_GUIDE_CURRENT.md`

**Authoritative for:** plain-language explanation of PHNEWS for Tony C. and other non-programmer stakeholders.

**Not authoritative for:** technical implementation state, source-of-truth code behavior, commit state, or publication authorization.

### Current Hermes Project Handoff
`docs/PHNEWS_Hermes_Project_Handoff_2026-09-25.md`

**Authoritative for:** point-in-time implementation context, known defects, current paths as reported, immediate next work, and unresolved technical state as of its handoff date.

**Not permanent law:** a Handoff is a dated snapshot and may be superseded by later verified Git state, source evidence, approved artifacts, later Handbooks, or explicit StevO decisions.

### Evidence Ledger
`docs/PHNEWS_EVIDENCE_LEDGER.md`

Binds important operational claims to evidence, verification status, dates, and notes.

### Contradiction Register
`docs/PHNEWS_CONTRADICTION_REGISTER.md`

Tracks material conflicts or stale claims that could affect behavior, source authority, acceptance, publication, or maintenance.

### Cross-model review record
`docs/PHNEWS_GPT_Response_to_Hermes_Documentation_Review_2026-09-25.md`

Records GPT's response to Hermes' independent documentation critique.

---

## 2. Authority by Question Type

PHNEWS does **not** use one universal precedence ladder for every question. Authority depends on the kind of decision.

### Editorial and publication decisions
1. Explicit StevO decision.

### Current factual content
1. Verified live authoritative source.
2. Verified retained authoritative source.
3. Verified supporting source for the fact it actually supports.
4. Approved prior PHNEWS artifact only as fallback/reference evidence.

### Accepted presentation/reference state
1. Latest approved PHNEWS artifact.

### Durable operating rules
1. Current System Handbook, subject to explicit StevO decisions.

### Current implementation status
1. Newest reconciled Handoff plus current Git/test/artifact evidence.

### Stakeholder explanation
1. Tony Guide.

Historical chats, old handoffs, old scripts, and unsupported model claims are background only unless independently verified.

---

## 3. Conflict-Resolution Procedure

When two sources or documents disagree:

1. Identify the claim and the question type: factual, editorial, implementation, presentation, or policy.
2. Do not silently merge or erase the contradiction.
3. Check the appropriate authority class above.
4. Record material unresolved conflicts in `PHNEWS_CONTRADICTION_REGISTER.md`.
5. Add evidence to `PHNEWS_EVIDENCE_LEDGER.md` when the claim is operationally important.
6. Mark the claim as unresolved or pending verification when evidence is insufficient.
7. Obtain StevO review before adopting consequential editorial, publication, or durable-policy changes.
8. Update all affected shared documents after resolution.
9. Preserve prior wording through Git history.

---

## 4. Standard Claim Types

Important technical-document claims should be identified as one of:

- **durable-rule**
- **current-state**
- **proposed**
- **historical**
- **unresolved**
- **pending-verification**

Implementation/acceptance state and source-provenance state are separate dimensions.

### Implementation / acceptance stages
- IMPLEMENTED
- FOCUSED_TEST_PASS
- FULL_QC_PASS
- HTML_INSPECTED
- EDITORIALLY_ACCEPTED
- APPROVED_FOR_PUBLICATION
- PUBLISHED_VERIFIED

### Source / provenance states
- VERIFIED_CURRENT_SOURCE
- VERIFIED_RETAINED_SOURCE
- FALLBACK_ONLY
- SOURCE_DATA_DEFECT

Do not use one state to imply the other.

---

## 5. AI Import / Handoff Instructions

A new AI or agent should start with:

```text
Repository: zeoszeos/palmhillnews
Branch: phnews-shared-docs

Read first:
docs/PHNEWS_SHARED_DOCS_INDEX.md

Then read:
1. docs/PHNEWS_SYSTEM_HANDBOOK_CURRENT.md
2. newest PHNEWS_Hermes_Project_Handoff file for current implementation state
3. docs/PHNEWS_TONY_GUIDE_CURRENT.md when stakeholder context is needed
4. docs/PHNEWS_EVIDENCE_LEDGER.md
5. docs/PHNEWS_CONTRADICTION_REGISTER.md
```

Reading documentation does **not** authorize:

- code modification
- publication
- deployment
- email sending
- overwriting approved artifacts
- changing durable rules without review

Before any side effect:

- verify the canonical worktree;
- verify current Git state;
- reconcile the newest Handoff with live evidence;
- confirm the requested side effect is explicit;
- preserve approval and publication boundaries.

---

## 6. Shared-Documentation Privacy Boundary

Shared documentation must never contain:

- passwords
- API keys
- authentication tokens
- session cookies
- private Gmail URLs
- authentication headers
- connection strings
- unnecessary resident private information
- unnecessary raw personal mailbox content

Use `[REDACTED]` when a sensitive event must be documented without exposing the secret.

---

## 7. Documentation Change Control

When a durable or operationally important rule changes:

1. identify the triggering defect, decision, or requirement;
2. classify the change as durable, temporary, current-state, historical, proposed, or unresolved;
3. update the System Handbook when the durable rule changes;
4. update the Tony Guide only when stakeholder-facing understanding changes;
5. update the Handoff when implementation state changes;
6. update this Index only when structure, authority, or document paths change;
7. update the Evidence Ledger for major operational claims;
8. update the Contradiction Register when a material conflict is opened or resolved;
9. add evidence/date/owner where practical;
10. request StevO review for consequential changes;
11. preserve prior versions through Git history.

---

## 8. Standard Maintenance Rule

- **System Handbook** = durable system rules and architecture
- **Tony Guide** = plain-English stakeholder explanation
- **Handoff** = time-bound implementation state and immediate work
- **Evidence Ledger** = evidence binding for important claims
- **Contradiction Register** = unresolved material disagreements
- **Index** = navigation, authority, and maintenance rules

The target is that GPT, Hermes, Codex, and a future maintainer can independently answer the same operational questions and identify the same unresolved risks without treating documentation reading as permission to make side effects.
