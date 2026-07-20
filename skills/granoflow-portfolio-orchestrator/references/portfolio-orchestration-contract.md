# Portfolio Orchestration Contract

## Completion Predicate (Portfolio Ready)

All must hold with App/API readback evidence:

1. Entry prerequisites passed (Project Work; frontend Baseline + App Shell when
   applicable).
2. Every planned milestone entity exists (`milestones_created` matches plan
   after empty-create or amend-only rules).
3. For every milestone in the plan, a skeleton coverage check passed.
4. For every skeleton row, `create_status: created` and
   `task_authoring_quality` passed at create time.
5. No pending `failed_quality` rows without a successful rewrite.

Assistant prose, "we should create…", or a markdown table without App ids is
**not** completion.

## Resumable State

Persist and re-read:

```yaml
portfolio_orchestration:
  status: in_progress | portfolio_ready | blocked
  project_id: <id>
  milestones_planned: []
  milestones_created: []
  current_milestone_id: null | <id>
  current_milestone_tasks_total: 0
  current_milestone_tasks_created: 0
  current_local_key: null | T1
  blocker: null | project_milestone_prerequisites_incomplete | task_portfolio_coverage_incomplete | task_authoring_quality_failed | other
```

On resume: skip milestones already in `milestones_created` whose tasks are
complete; continue at `current_milestone_id` / `current_local_key`.

## Forbidden Collapses

- One model turn that outputs many complete task descriptions for create.
- Calling milestone-workflow to create tasks.
- Calling task-authoring `batch_create` as a single multi-description write.
- Marking Portfolio Ready while any mandatory acceptance id lacks an
  accountable created task (unless controller-owned explicitly).

## Sequencing

1. Create/amend all milestones first.
2. Author tasks milestone-by-milestone.
3. Prefer First Ship milestone's tasks before refine milestones when
   `role: first_ship` is set.
