---
name: granoflow-task-authoring
description: Create Granoflow tasks singly or via orchestrated batch—skeleton tables in batch, full title and description one task at a time with task-authoring-quality-contract. Does not run Analysis, Plan, or execution.
---

# Granoflow Task Authoring

Use this Skill to **create** Granoflow tasks with accurate titles and
descriptions. It supports skeleton batches and single full creates. It does
**not** run Task Work Analysis, Planning, execution, Delivery, or milestone
charter/integration.

Prefer `granoflow-portfolio-orchestrator` when the user wants all milestones
created and then every milestone's tasks authored. Prefer
`granoflow-task-orchestrator` when the user wants lifecycle routing (analyze /
plan / run), not portfolio creation.

## Keyword

- `#task-authoring`
- `#create-one`
- `#batch-skeleton`

## When To Use

- Create one task with a complete quality-checked description.
- Produce a skeleton portfolio table for one milestone, then create each task.
- Called by `granoflow-portfolio-orchestrator` inside its per-milestone loop.

## Required Reference

Before any create, read and apply
`granoflow-agent-workflow/task-authoring-quality-contract`. Failed quality
returns `task_authoring_quality_failed` for that task only; rewrite and retry
the same row—do not skip or widen the batch.

Also read `references/task-authoring-modes.md`.

## Modes

### `create_one`

Author **exactly one** task's final title and description in this model turn,
run the quality contract, then create via App/API and read back. Never emit
multiple complete descriptions in one turn.

### `batch_skeleton`

Emit a table of skeleton rows for one milestone (or an explicit small set).
Each row includes title draft, one-line responsibility, acceptance ids,
depends_on, and milestone_id. No full description bodies. Then run a coverage
check against the milestone's mandatory acceptance ids.

### `batch_create`

**Orchestration mode only:** loop `create_one` once per skeleton row that is
not yet created. Never implement `batch_create` as a single turn that writes
many full descriptions.

## Workflow

1. Resolve project and target milestone (or inbox only when capture is
   intentionally unbound—portfolio work must bind a milestone).

   Checkpoints:

   - Portfolio work must bind a milestone; inbox only when capture is intentionally unbound.

2. Choose mode. Portfolio pipelines use `batch_skeleton` then repeated
   `create_one`.

   Checkpoints:

   - `batch_create` is a loop of `create_one`, never one multi-description dump.

3. For `batch_skeleton`: write the table; verify every mandatory acceptance id
   has at least one accountable skeleton row (or controller note). On failure,
   revise the skeleton—do not proceed to create.

   Checkpoints:

   - Prove skeleton coverage before any create loop; revise skeleton on failure—do not proceed.

4. For each pending skeleton row: `create_one` → quality gate → App create →
   readback. Persist progress (`tasks_created N/M`) so a later turn can resume.

   Checkpoints:

   - Quality contract mandatory before create; failure returns `task_authoring_quality_failed` for that row only.
   - Persist `tasks_created N/M` so later turns can resume.

5. Done when all intended rows exist as App tasks with quality-passed
   descriptions.

   Checkpoints:

   - Every created task must pass quality contract and App readback before declaring done.

## Hard Rules

- Full description batch size is **1**.
- Skeleton batches may be larger but must stay short-field only.
- Quality contract is mandatory before create; no bypass from orchestrators.
- Do not start Analysis/Plan/execution in this Skill.
- Never persist secrets in task descriptions.

## Success Criteria

- Every created task passes `task-authoring-quality-contract`.
- Skeleton coverage is proven before create loops begin.
- `batch_create` is visibly a loop of `create_one`, not one multi-description
  dump.
