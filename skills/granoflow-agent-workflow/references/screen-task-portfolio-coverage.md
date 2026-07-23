# Screen → Task Portfolio Coverage (Milestone `task_plan`)

Hard gate for **milestone decompose / task authoring**. Composition SoT is
**Milestone Work `task_plan`**, not Project Work and not Task Work.

Project Work keeps **key-page inventory** only (`key_pages_from_sources`,
`not_portfolio_complete`). Milestone `task_plan` holds refined screens, page
journeys, and frozen task summaries for this milestone.

## Mandatory Load

Before treating skeleton coverage as passed, and before App `create_one` when
user-visible pages apply, load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "screen-task-portfolio-coverage"
)
```

Also load shape authority:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-milestone-coordination",
  referenceId: "milestone-task-plan-template"
)
```

Skipping the load when the gate applies → `screen_task_portfolio_coverage_unread`.

## When It Applies

| Trigger                                                         | Gate                                                    |
| --------------------------------------------------------------- | ------------------------------------------------------- |
| Milestone `decompose_required` for UI / user-visible pages      | Required                                                |
| `granoflow-task-authoring` `batch_skeleton` / `create_one`      | Required                                                |
| `granoflow-portfolio-orchestrator` per-milestone task authoring | Required                                                |
| Declaring Portfolio Ready (UI milestones)                       | Required                                                |
| Task Analysis for a UI-changing task                            | Verify only (fail closed back to milestone `task_plan`) |

Non-UI milestones → `task_plan.status: not_applicable` (or omit refined
screens) and skip this gate.

## Hard Rules

### 1. Write `task_plan` on Milestone Work

Persist `task_plan` per `milestone-task-plan-template.yaml` on the Milestone
Work attachment (YAML). Include:

- `key_screen_refs` — Project Work key `screen_id`s this milestone traces
- `refined_screens[]` — delivery screens (may be finer than key pages)
- `page_journeys[]` — milestone page journeys
- `tasks[]` — task summaries (`local_key`, `responsibility`, `screen_ids`,
  `acceptance_ids`)

Refined screens Must set `traces_to_key_screen` **or**
`provenance: milestone_discovered`. They do not conflict with Project Work key
pages; key pages remain source anchors.

### 2. Split probe (page-as-task-scope)

For **every** `refined_screens[]` row, before `task_plan.status: passed`:

```yaml
split_probe:
  pass_completed: true
  conclusion: keep_cohesive | split | needs_user_decision
  rejected_split_summary: null # required when keep_cohesive
  accepted_split_summary: null # required when split (or resulting_screen_ids)
  resulting_screen_ids: []
  rationale: null
```

- Reuse Project journey-level `decomposition` when it already decided page
  count; still record screen-level `split_probe` (short cite + conclusion).
- `keep_cohesive` without `rejected_split_summary` →
  `screen_split_probe_incomplete`.
- `split` Must update `refined_screens` + `tasks` **before** create.
- `needs_user_decision` → interactive wait; unattended →
  `screen_split_probe_requires_user`.

### 3. At least one task summary per refined screen

Every refined `screen_id` Must appear on ≥1 `tasks[].screen_ids`. After App
create, write `tasks[].task_id`. Missing mapping →
`task_portfolio_screen_coverage_incomplete` /
`milestone_task_plan_incomplete`. Acceptance-only coverage is **not** enough.

### 3b. Project Work detail carry-forward (hard)

Users cannot reliably accept long detail lists at this phase. Agents Must still
**disposition every** Project Work `ui_details[]` on in-scope key pages into
`task_plan.detail_carryforward.rows`:

| disposition                 | Meaning                                            |
| --------------------------- | -------------------------------------------------- |
| `carried`                   | Bound to a refined screen + task local_key         |
| `deferred_out_of_milestone` | Explicitly not this milestone (rationale required) |
| `out_of_scope`              | Explicitly not product scope (rationale required)  |

Silent omission → `milestone_detail_carryforward_incomplete`.
`detail_carryforward.status` Must be `complete` (or `not_applicable` when no
in-scope PW details exist) before `task_plan.status: passed`.

Also: every in-scope Project Work key page (shares milestone acceptance ids, or
listed in `key_screen_refs`) Must appear in `key_screen_refs` and be covered by
at least one refined screen (`traces_to_key_screen`) or an explicit deferred /
out-of-scope carryforward row for that screen with no tasks (rare; prefer a
task).

### 4. Pass before create; freeze against Analysis reopen

- UI: `task_plan.status: passed` and `decomposition_status: passed` before
  `create_one` loops.
- Skeleton rows Must align with `task_plan.tasks` (`local_key`, `screen_ids`,
  `acceptance_ids`).
- Create writeback updates **Milestone `task_plan.tasks[].task_id` only**—never
  Project Work `screen_coverage` for task binding.
- Task Analysis Assumes the freeze. If Analysis finds orphan screens, missing
  probes, or wants to change ownership/split:

  1. fail closed `milestone_task_plan_incomplete` /
     `task_portfolio_screen_coverage_incomplete` /
     `screen_split_probe_incomplete`;
  2. do **not** silently enlarge the current task;
  3. reopen Milestone `task_plan` (`reopened` / `draft`), amend, re-pass, then
     resume Analysis.

Analysis still owns hi-fi `ui_prototype` and detail fill for screens listed on
that task's frozen `screen_ids`.

## Skeleton Row Shape

```yaml
- local_key: T1 # must match task_plan.tasks[].local_key
  milestone_id: <id>
  title_draft: <action verb + object>
  responsibility: <same freeze as task_plan>
  acceptance_ids: [A1]
  screen_ids: [S-reader]
  depends_on: []
  create_status: pending | created | failed_quality
  task_id: null | <app id after create>
```

## AI judgment assist (optional; not a substitute for lint)

This phase is **AI self-audit + deterministic lint**. Do not ask the user to
accept long detail tables. Preferred external reviewers when available
(`preferred_method`, `native_fallback` if missing):

| Skill                        | Source                                   | Fit for task_plan auto-audit                                        |
| ---------------------------- | ---------------------------------------- | ------------------------------------------------------------------- |
| `prd-review`                 | `yihannangua/prd-review-skill`           | Strong: omissions/contradictions/testability vs product docs        |
| `prd-implementation-ready`   | `wair56/prd-implementation-ready-skills` | Strong: page UX / fields / exceptions readiness                     |
| gstack `/plan-ceo-review`    | `garrytan/gstack`                        | Product/scope pressure-test (prefer report mode; avoid user Q loop) |
| gstack `/plan-design-review` | `garrytan/gstack`                        | Design-dimension review of the plan (same caveat)                   |
| `grill-finalizer`            | Product Builder pack                     | Missing-issue scan on the written plan                              |
| `grill-me`                   | Product Builder pack                     | **Poor fit here** — interviews the user; not silent auto-accept     |
| `impeccable`                 | Product Builder pack                     | Taste/slop only — not requirements carry-forward                    |

Record evidence on Milestone Work when a reviewer ran; never claim equivalence
if it did not. Lint remain the hard gate for carry-forward completeness.

## Lint

`skills/granoflow-agent-workflow/scripts/lint_task_screen_portfolio.py`

Input: Milestone Work JSON/YAML containing `task_plan` (or bare `task_plan`),
optionally `--skeleton`, and **`--project-work`** for detail/key-page
carry-forward checks. Phases: `plan_passed` | `portfolio_ready`.

## Fail Closed Codes

| Code                                        | Meaning                                          |
| ------------------------------------------- | ------------------------------------------------ |
| `screen_task_portfolio_coverage_unread`     | Gate reference not loaded                        |
| `milestone_task_plan_incomplete`            | Missing/invalid `task_plan` or status not passed |
| `milestone_detail_carryforward_incomplete`  | PW ui_detail or key page not dispositioned       |
| `task_portfolio_screen_coverage_incomplete` | Refined screen missing from tasks / skeleton     |
| `screen_split_probe_incomplete`             | Missing/invalid `split_probe` on refined screen  |
| `screen_split_probe_requires_user`          | Unattended hit `needs_user_decision`             |

## Admission Test (host self-check)

1. Did we load this reference + milestone-task-plan-template via MCP?
2. Is composition written on Milestone `task_plan` (not Project Work)?
3. Does every refined screen have split probe + ≥1 task row?
4. Would Analysis only execute frozen `screen_ids` without rediscovering orphans?

If any answer is no, revise Milestone Work before create / Analysis.
