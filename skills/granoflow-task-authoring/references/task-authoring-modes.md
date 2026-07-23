# Task Authoring Modes

## Skeleton Row Shape

```yaml
- local_key: T1 # must match Milestone task_plan.tasks[].local_key
  milestone_id: <id>
  title_draft: <action verb + object>
  responsibility: <one outcome sentence; frozen in task_plan>
  acceptance_ids: [A1]
  # Required when Milestone task_plan lists refined screens for this row.
  screen_ids: []
  depends_on: []
  create_status: pending | created | failed_quality
  task_id: null | <app id after create>
```

## Coverage Check

Before any `create_one` in a milestone portfolio:

### A. Acceptance coverage (unchanged)

1. Collect mandatory acceptance ids for that milestone (from Project Work /
   Milestone Work / user charter facts available at authoring time).
2. Every mandatory id must appear on at least one skeleton row (or an explicit
   controller-owned acceptance that does not need a child task).
3. Every skeleton row must map to at least one acceptance id or a documented
   integration-only responsibility owned by the controller.
4. On failure, return `task_portfolio_coverage_incomplete` with missing ids.

### B. Milestone `task_plan` coverage (hard, UI milestones)

Load `granoflow-agent-workflow/screen-task-portfolio-coverage` and
`granoflow-milestone-coordination/milestone-task-plan-template` via MCP first.

1. Require Milestone Work `task_plan.status: passed` (and
   `decomposition_status: passed`) when the milestone has user-visible pages.
2. Skeleton rows Must align with `task_plan.tasks` (`local_key`, `screen_ids`,
   `acceptance_ids`, `responsibility`).
3. Every `task_plan.refined_screens[].screen_id` must appear on ≥1 skeleton /
   task_plan task row; every refined screen must already have a completed
   `split_probe` on the Milestone `task_plan` (not Project Work).
4. On failure, return `milestone_task_plan_incomplete` /
   `task_portfolio_screen_coverage_incomplete` /
   `screen_split_probe_incomplete`—revise Milestone `task_plan` / skeleton; do
   not proceed to create.
5. After each successful create, write App `task_id` onto
   `task_plan.tasks[].task_id` (same batch as create readback).

Acceptance coverage alone never waives `task_plan` coverage. Do **not** write
task binding onto Project Work `screen_coverage`.

Prefer:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_task_screen_portfolio.py \
  <milestone-work.json> --skeleton <skeleton.json> --phase plan_passed
```

before starting the create loop (`ok: true` required).

## create_one Protocol

1. Load one skeleton row with `create_status: pending`.
2. Write final title and full description for **that row only** (plain-language
   task card—not Task Work Analysis, not hi-fi HTML).
3. Apply `task-authoring-quality-contract` (plain language, analogy, concrete
   example, title standard).
4. On failure: set `failed_quality`, keep other rows untouched, rewrite only
   this row.
5. On success: create via App/API, read back `task_id`, set `created`, and
   write `task_id` onto matching Milestone `task_plan.tasks[].task_id`.

## batch_create Protocol

```text
for row in skeleton where create_status != created:
  invoke create_one(row) in its own authoring step
```

Forbidden: one assistant message containing multiple complete task
descriptions intended for create.

## Resume

Record `tasks_created`, `tasks_total`, `current_local_key`, and
`milestone_id` in the host run state or Milestone Work next-action note so
interrupted runs continue at the next pending row.
