# Milestone Portfolio Creation

Use with `granoflow-milestone-workflow` for single or batch milestone creation.
Task creation belongs to `granoflow-task-authoring`. Full pipeline belongs to
`granoflow-portfolio-orchestrator`.

## Planning Fields

When creating or amending the portfolio, align with Project Work:

- `milestone_strategy` sequencing and `project_completion_conditions`
- `acceptance_coverage` accountable milestones
- `requirement_coverage` primary owners at milestone layer
- `active_milestone_limit` (default `1`)

Each planned milestone record should include at least:

```yaml
- key: M1
  title: <short title>
  role: first_ship | refine | other
  order: 1
  acceptance_ids: []
  requirement_ids: []
  summary: <one sentence outcome>
```

## First Ship

When the project needs a user-visible first version, mark exactly one milestone
`role: first_ship` (or equivalent in `milestone_strategy`). Batch create still
creates **all** milestones; activation and later task authoring should prefer
the First Ship milestone first so users can see a vertical slice sooner.

## Empty Versus Existing

| State | Action |
| ----- | ------ |
| No App milestones | Plan entire set; write Project Work; create every milestone entity |
| Milestones exist | Amend only for coverage/sequencing gaps; do not recreate |

## Create Protocol

1. Preview titles, order, roles, and acceptance ownership.
2. Persist Project Work roadmap changes with readback.
3. Create milestone entities (batch or single) with App/API readback.
4. Activate at most `active_milestone_limit` milestones; leave others created
   but inactive.
5. Stop. Do not create tasks here.

## Handoff

After successful create/amend, hand off to:

- `granoflow-portfolio-orchestrator` if child tasks for those milestones are
  still missing; or
- `granoflow-task-authoring` for one milestone's tasks; or
- `granoflow-milestone-coordination` only when tasks already exist and the user
  wants charter/execution.
