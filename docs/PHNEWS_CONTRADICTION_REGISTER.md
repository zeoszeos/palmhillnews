# PHNEWS Contradiction Register

**Repository:** `zeoszeos/palmhillnews`  
**Branch:** `phnews-shared-docs`  
**Updated:** September 25, 2026  
**Purpose:** Preserve and resolve material disagreements without silently editing away their history.

## C-001 — Canonical worktree path

**Claim A:** `/home/leono/hermes-bridge/Projects/PHNEWS-Palm-Hill-Newsletter` is the primary current project path.  
**Source:** September 25 Handoff / current shared documentation.

**Conflicting context:** Older PHNEWS project records identify other project and public-repository working paths.  
**Conflict type:** implementation/path authority.  
**Current working decision:** Treat the September 25 path as **handoff-declared**, not fully canonical.  
**Decision authority:** Live filesystem/Git verification, then StevO review if ambiguity remains.  
**Evidence needed:** `pwd`, Git top-level, remotes, branch, status, latest commit for each candidate.  
**Resolution status:** OPEN.  
**Documents to update when resolved:** Index, Handbook, current Handoff, Evidence Ledger.

---

## C-002 — 170-message mailbox statistic vs reproduction attempt

**Claim A:** A 90-day sample contained 170 direct Palm Hill/RPM messages: 126 Palm Hill and 44 RPM.  
**Source:** current Handbook based on earlier project analysis.

**Claim B:** September 25 reproduction using the exact sender addresses currently documented returned 154 Palm Hill messages and 0 for the documented RPM sender.  
**Source:** GPT live Gmail verification attempt, September 25, 2026.

**Conflict type:** evidence/reproducibility.  
**Current working decision:** Do not declare the 170 figure false. Mark it `REPORTED_PENDING_EVIDENCE_VERIFICATION`.  
**Likely causes to investigate:** alternate RPM sender(s), aliases, recipient scope, date boundaries, exported source set, or different inclusion logic.  
**Resolution status:** OPEN.  
**Documents to update when resolved:** Handbook, Evidence Ledger, Handoff if operationally relevant.

---

## C-003 — Events - Upcoming: earlier public deployment vs newer local implementation

**Claim A:** Six Events - Upcoming detail pages are publicly deployed.  
**Evidence:** earlier merge commit `d058716faa58fa969393ceb2ad40c290130926a4` and recorded public URLs.

**Claim B:** newer source-body, provenance, date/source-display, and fact-level source fixes exist locally and are not assumed deployed.  
**Source:** September 25 Handoff.

**Conflict type:** publication-state version mismatch.  
**Current working decision:** The public pages represent an earlier version; current local implementation must not be labeled `PUBLISHED_VERIFIED` until explicitly published and verified.  
**Resolution status:** OPEN until current milestone is accepted/published or deliberately left local.  
**Documents to update when resolved:** Handoff, Evidence Ledger, approval/reference package.

---

## C-004 — Karaoke Obi-Time time discrepancy

**Claim A:** canonical metadata has been recorded as 6:00–9:30 PM.  
**Claim B:** full retained Palm Hill Calendar source body states 6:30–9:00 PM.  
**Conflict type:** factual source conflict.  
**Current working decision:** unresolved; do not silently choose.  
**Decision authority:** verified authoritative source evidence under PHNEWS source rules.  
**Resolution status:** OPEN.  
**Documents to update when resolved:** canonical event data, Handoff, Evidence Ledger if material, regenerated detail/newsletter artifacts.

---

## C-005 — Section status shorthand vs acceptance stages

**Claim A:** historical project notes use labels such as `locked/ready`, `stable`, or `close to acceptance`.  
**Claim B:** those labels do not distinguish implementation, tests, full QC, HTML inspection, editorial acceptance, publication authorization, and public verification.  
**Conflict type:** status-model ambiguity.  
**Current working decision:** retain historical wording as history, but use staged acceptance language in current technical documentation.  
**Resolution status:** CONTROLLED / documentation model updated.  
**Documents affected:** Index, Handbook, Handoff, Evidence Ledger.

---

## Register maintenance rule

Use this register only when a contradiction could materially affect:

- factual content;
- source authority;
- canonical worktree/repository choice;
- section acceptance;
- publication/deployment;
- durable policy;
- maintenance behavior.

Minor wording differences do not belong here.
