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

Also read `references/task-authoring-modes.md`. For UI milestones, also load
`granoflow-agent-workflow/screen-task-portfolio-coverage` and
`granoflow-milestone-coordination/milestone-task-plan-template` before treating
skeleton coverage as passed. Require Milestone `task_plan.status: passed`.
For every requirement-driven/software Milestone, load
`granoflow-agent-workflow/milestone-ai-review` and require schema v2 AI review
plus current digest before creating or continuing child tasks.

## Modes

### `create_one`

Author **exactly one** task's final title and description in this model turn,
run the quality contract, then create via App/API and read back. Never emit
multiple complete descriptions in one turn. Write back the App `task_id` onto
Milestone `task_plan.tasks[].task_id` for the matching `local_key`. Do not
bind tasks onto Project Work `screen_coverage`.

### `batch_skeleton`

Emit a table of skeleton rows for one milestone (or an explicit small set).
Each row includes title draft, one-line responsibility, acceptance ids,
`screen_ids` (aligned with Milestone `task_plan`), depends_on, and
milestone_id. No full description bodies. Then run coverage checks against
mandatory acceptance ids **and** Milestone `task_plan` (passed status, split
probes, ≥1 skeleton row per refined screen).

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

3. For `batch_skeleton`: ensure Milestone schema v2
   `task_plan.status: passed` with current AI review digest for
   requirement-driven/software work; when UI applies, write the table aligned
   to `task_plan.tasks`; verify every
   mandatory acceptance id **and** every refined `screen_id` has at least one
   accountable skeleton row. On failure, revise the skeleton / Milestone
   `task_plan`—do not proceed to create.

   Checkpoints:

   - Prove acceptance + task_plan coverage before any create loop; revise on
     failure—do not proceed.
   - Fail closed `milestone_task_plan_incomplete` /
     `task_portfolio_screen_coverage_incomplete` /
     `screen_split_probe_incomplete` when UI screens are orphaned or unprobed.

4. For each pending skeleton row: `create_one` → quality gate → App create →
   readback → write `task_id` on Milestone `task_plan`. Persist progress
   (`tasks_created N/M`) so a later turn can resume.

   Checkpoints:

   - Quality contract mandatory before create; failure returns `task_authoring_quality_failed` for that row only.
   - Persist `tasks_created N/M` so later turns can resume.

5. Done when all intended rows exist as App tasks with quality-passed
   descriptions and Milestone `task_plan.tasks[].task_id` filled.

   Checkpoints:

   - Every created task must pass quality contract and App readback before declaring done.

## Hard Rules

- Full description batch size is **1**.
- Skeleton batches may be larger but must stay short-field only.
- Quality contract is mandatory before create; no bypass from orchestrators.
- Do not start Analysis/Plan/execution in this Skill.
- Do not author hi-fi page HTML in this Skill.
- Never persist secrets in task descriptions.

## Success Criteria

- Every created task passes `task-authoring-quality-contract`.
- Skeleton coverage is proven before create loops begin (acceptance **and**
  Milestone `task_plan` when UI applies).
- Milestone `task_plan.tasks[].task_id` set after create.
- `batch_create` is visibly a loop of `create_one`, not one multi-description
  dump.
