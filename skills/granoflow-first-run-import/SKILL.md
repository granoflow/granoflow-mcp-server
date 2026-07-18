---
name: granoflow-first-run-import
description: Use when a user asks to initialize Granoflow, optionally import data from Cursor, Codex, Hermes, or another agent, install recommended external capabilities during first-run onboarding, or perform agent history import, project and monthly milestone setup, task extraction, review-card candidate extraction, and post-import context backfill.
---

# Granoflow First-Run Import

Use this skill when the user asks:

```text
Initialize Granoflow
Initialize Granoflow and import data
```

Also accept equivalent requests in the user's language, including:

```text
初始化 Granoflow
初始化 Granoflow 并导入数据
```

Public README and directory-listing copy should use the English prompt. Runtime
behavior is multilingual: parse equivalent user commands in the user's language,
and continue prompts, confirmations, preview summaries, blockers, task
descriptions, and final reports in the user's language by default unless the
user asks otherwise.

This workflow initializes the Granoflow connection, offers the fixed
`granoflow_product_builder_v1` capability pack as one decision, and optionally imports data from Cursor,
Codex, Hermes, or other agents. It is an onboarding orchestration skill. A
plain initialization request may stop after connection and capability setup;
data import runs only when requested.

This skill does not read hidden chat histories, scrape browser history, access
cloud accounts by itself, or write directly to Granoflow storage. It uses only
user-provided or host-exposed sources and Granoflow Local HTTP API tools.

## Required Base Skill

Before applying this workflow, read the bundled
`granoflow-agent-workflow` skill. Reuse its rules for:

- task completion and task reviews;
- review-card authoring;
- long-term work memory;
- waiting for user input;
- weekly/monthly review drafting;
- project and milestone context stewardship.

Do not duplicate those detailed rules here. This skill sequences the import.
An import is not a daily review. If the user separately asks to review a day,
call `granoflow_daily_review_skill`; do not draft or write it during import.

## Fixed Sequence

Follow this order. Do not redesign the workflow from scratch.

1. Connect and inspect Granoflow capabilities.
2. Offer the complete unavailable portion of the fixed capability pack as one decision.
3. Stop after setup when the user requested initialization only.
4. Discover import sources and record authorization when import was requested.
5. Build a source ledger.
6. Create a local import preview document.
7. Propose projects and monthly milestones.
8. Propose task candidates.
9. Propose review-card candidates.
10. Ask for confirmation before any data write.
11. Import in bounded batches.
12. Read back created or reused objects.
13. Backfill project and milestone descriptions.
14. Report imported, skipped, failed, and deferred items.

## Phase 0: Connect And Capability Check

Before source analysis:

1. Call `granoflow_agent_workflow_skill`.
2. Check that the Granoflow Local HTTP API is reachable.
3. Call `granoflow_ai_agent_tools` and inspect available project, milestone,
   task, review-card, context-pack, memory-batch, and context-steward tools.
4. Call `granoflow_source_tags_ensure` so the `AI` and `人工` completion source
   tags exist before any import write. Reuse existing tags; do not create
   near-duplicate labels.
5. If Granoflow is unreachable, stop and tell the user to open Granoflow and
   enable the Local HTTP API. Do not create a fake preview from chat memory.

Fail closed when there is no safe task or project write surface.

## Phase 0.5: Recommended External Capabilities

After the connection check and before import source discovery, read
`references/recommended-external-skills.md`.

The host discovers which recommended collections are already available. If any
are unavailable, show the reference's localized `User Prompt`: names and
plain-language functions only. Recommend installing all offered collections;
do not require item-by-item selection.

Use the reference states `ready`, `awaiting_confirmation`, `approved_all`,
`declined`, and `partial_failure`. Ask exactly once. A refusal or partial
failure leaves connection and manual use available but records
`capability_pack_not_ready`; automatic project design initialization must stop
instead of offering item-by-item choices. Approval may lead to a host-native
confirmation. After installation, rediscover availability and account for
required host reload; do not infer success from a command result.

This phase does not run `setup-matt-pocock-skills`; that setup needs a real
software repository. Installation approval does not authorize data import.

If the user requested only `Initialize Granoflow` or `初始化 Granoflow`, report
connection and recommended-capability readiness, then stop. Continue to Phase 1
only when the user also requested import or later asks to import data.

## Phase 1: Source Discovery

Read `references/source-discovery.md`.

The source ledger must state:

- which agent, workspace, folder, repository, thread export, or user-provided
  file is in scope;
- which date range is in scope;
- which sources are unavailable;
- how each source can be cited without copying raw private history;
- import budgets for projects, milestones, tasks, cards, and batch writes.

If the current host does not expose historical threads, say so and offer a
file-based or current-workspace import path.

## Phase 2: Import Preview

Read `references/import-planning.md`.

Create a local preview document before any write. Use a private or temporary
path such as:

```text
docs-temp/first-run-import-preview-YYYY-MM-DD.md
```

The preview must include project, monthly milestone, task, card, skipped-record,
dedupe, risk, and proposed-write ledgers.

No Granoflow write may happen before the preview is shown and confirmed.

## Phase 3: Project And Milestone Mapping

Read `references/project-milestone-mapping.md`.

Map sources to projects using explicit repository, folder, workspace, or project
signals before themes. Create monthly milestones only for months with retained
task candidates. Reuse existing projects or milestones when tools can resolve
them safely.

## Phase 4: Task And Card Import

Read `references/task-and-card-import.md`.

Delegate all card candidates to `granoflow-review-card-draft`; do not copy or replace its authoring rules.

Create task candidates only for clear work units, outcomes, blockers, or next
actions. Create card candidates only for durable decisions, failure modes,
project rules, engineering conventions, security principles, useful preferences,
or professional concepts worth spaced practice.

Keep task and card writes in bounded batches. Use dry-run or preview tools when
available. Stop on duplicate, unsupported capability, or provenance errors.

## Phase 5: Context Backfill

Read `references/context-backfill.md`.

Backfill project and active milestone descriptions only after import readback.
Use imported tasks, task reviews, cards, source ledger, decisions, risks,
blockers, and next actions as evidence. Do not write raw thread dumps, secrets,
tokens, private auth URLs, or long copied conversation text into descriptions.

## Confirmation Gate

Ask for explicit confirmation before writes. The confirmation must name:

- projects to create or reuse;
- monthly milestones to create or reuse;
- task batches;
- card batches;
- records skipped;
- residual risks;
- context descriptions to backfill after readback.

If the user confirms only part of the preview, import only that part and keep
the rest deferred.

## Final Report

Report:

- preview document path;
- source count and unavailable sources;
- created or reused projects;
- created or reused milestones;
- imported tasks;
- imported cards;
- skipped records and reasons;
- context descriptions updated;
- failed batches and recovery options;
- sync/readback status;
- remaining user decisions.

## Boundaries

- Do not publish npm, registry, or directory updates as part of this workflow.
- Do not open manual directory admin pages unless the user explicitly asks after
  the local implementation or import is complete.
- Do not treat manual directory publication as a blocker.
- Do not bypass Granoflow Local HTTP API tools or app-owned import semantics.
- Do not drop provenance or safety fields to make a write succeed.
