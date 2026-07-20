# Task Authoring Modes

## Skeleton Row Shape

```yaml
- local_key: T1
  milestone_id: <id>
  title_draft: <action verb + object>
  responsibility: <one outcome sentence>
  acceptance_ids: [A1]
  depends_on: []
  create_status: pending | created | failed_quality
  task_id: null | <app id after create>
```

## Coverage Check

Before any `create_one` in a milestone portfolio:

1. Collect mandatory acceptance ids for that milestone (from Project Work /
   Milestone Work / user charter facts available at authoring time).
2. Every mandatory id must appear on at least one skeleton row (or an explicit
   controller-owned acceptance that does not need a child task).
3. Every skeleton row must map to at least one acceptance id or a documented
   integration-only responsibility owned by the controller.
4. On failure, return `task_portfolio_coverage_incomplete` with missing ids.

## create_one Protocol

1. Load one skeleton row with `create_status: pending`.
2. Write final title and full description for **that row only**.
3. Apply `task-authoring-quality-contract` (plain language, analogy, concrete
   example, title standard).
4. On failure: set `failed_quality`, keep other rows untouched, rewrite only
   this row.
5. On success: create via App/API, read back `task_id`, set `created`.

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
