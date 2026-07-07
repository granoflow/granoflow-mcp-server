# Import Planning

Read this reference before creating the first-run import preview document.

The preview is the control surface for this workflow. It prevents the agent from
turning a broad import request into repeated analysis or unreviewed writes.

## Preview Path

Use a private or temporary project path:

```text
docs-temp/first-run-import-preview-YYYY-MM-DD.md
```

If the current project documents a different local AI workspace, use that path.
Do not write private import previews into public docs unless the user explicitly
asks for a public artifact.

## Required Preview Sections

Use this structure:

```markdown
# First-Run Granoflow Import Preview

Date:
Source:
Granoflow API:
Dry-run only:

## Summary

- Sources inspected:
- Sources unavailable:
- Proposed projects:
- Proposed monthly milestones:
- Task candidates:
- Review-card candidates:
- Skipped records:
- Proposed write batches:

## Source Ledger

| Source | Type | Location | Date range | Project signal | Access status | Usable records | Excluded records | Citation form | Notes |
| ------ | ---- | -------- | ---------- | -------------- | ------------- | -------------- | ---------------- | ------------- | ----- |

## Project Proposals

| Project key | Title | Source signals | Create/reuse | Confidence | Dedupe key | Notes |
| ----------- | ----- | -------------- | ------------ | ---------- | ---------- | ----- |

## Monthly Milestone Proposals

| Project key | Month | Title | Create/reuse | Task count | Dedupe key | Notes |
| ----------- | ----- | ----- | ------------ | ---------- | ---------- | ----- |

## Task Candidates

| Candidate id | Title | Project | Milestone | Status | Source | Confidence | Dedupe key | Review candidate | Notes |
| ------------ | ----- | ------- | --------- | ------ | ------ | ---------- | ---------- | ---------------- | ----- |

## Review-Card Candidates

| Candidate id | Front | Back summary | Card type | Source | Worthiness reason | Dedupe key | Notes |
| ------------ | ----- | ------------ | --------- | ------ | ----------------- | ---------- | ----- |

## Skipped Records

| Source | Record | Reason | Revisit condition |
| ------ | ------ | ------ | ----------------- |

## Proposed Writes

| Batch | Objects | Count | Tool/path | Dry-run available | Requires confirmation |
| ----- | ------- | ----- | --------- | ----------------- | --------------------- |

## Risks And Assumptions

-

## Confirmation Request

<Name exactly what will be imported and what remains skipped.>
```

## Dedupe Keys

Every proposed project, milestone, task, and card needs a dedupe key.

Recommended shapes:

- project: `project:<normalized-repo-or-folder>`
- milestone: `milestone:<project-key>:YYYY-MM`
- task: `task:<project-key>:<month>:<source-id>:<normalized-title>`
- card: `card:<source-id>:<card-type>:<normalized-front>`

Use source ids when available. If no source id exists, combine source location,
date, and normalized title.

## Confirmation Gate

Before writing, ask the user to confirm:

- projects to create or reuse;
- monthly milestones to create or reuse;
- task batches;
- review-card batches;
- skipped records;
- whether project and milestone descriptions should be backfilled after
  readback.

If the user confirms only part of the preview, import only that part.

## Batch Rules

- Maximum 20 objects per write batch.
- Use dry-run first where tools support it.
- Stop the current batch on duplicate, unsupported capability, validation, or
  provenance errors.
- Do not retry by removing source summaries, dedupe keys, safety fields, or
  confirmation requirements.

## Stop Conditions

Stop and report instead of writing when:

- Granoflow Local HTTP API becomes unreachable;
- source data cannot be cited safely;
- the preview has not been confirmed;
- a batch would exceed the import budget;
- a needed app-owned capability is missing;
- the only way forward is to write directly to a database or hidden store.
