# PHNEWS Shared Documentation Index

**Repository:** `zeoszeos/palmhillnews`  
**Branch:** `phnews-shared-docs`  
**Updated:** September 25, 2026

This branch is the shared documentation workspace for PHNEWS. It is intentionally separate from the live `main` deployment branch.

## Primary documents

### 1. PHNEWS System Handbook
`docs/PHNEWS_SYSTEM_HANDBOOK_CURRENT.md`

Detailed operating rules, architecture, provenance, QC, section registry, publication boundaries, approval/reference design, and current development principles.

### 2. Tony Guide
`docs/PHNEWS_TONY_GUIDE_CURRENT.md`

Plain-language explanation of how PHNEWS works, intended for Tony C. and other non-programmer stakeholders.

### 3. Hermes Project Handoff
`docs/PHNEWS_Hermes_Project_Handoff_2026-09-25.md`

Detailed project-state handoff covering recent implementation progress, current paths, Events - Upcoming work, and near-term next steps.

## Standard use

Tell Hermes or another project agent:

> Read the PHNEWS shared documentation from repository `zeoszeos/palmhillnews`, branch `phnews-shared-docs`, starting with `docs/PHNEWS_SHARED_DOCS_INDEX.md`.

Then read the System Handbook for durable rules and the current handoff for immediate implementation state.

## Documentation rule

- System Handbook = durable system rules and architecture
- Tony Guide = plain-English stakeholder explanation
- Handoff = current implementation state / recent progress / immediate next work

When a durable rule changes, update the Handbook.
When stakeholder-facing behavior changes materially, update the Tony Guide.
When implementation state changes, update the handoff.
