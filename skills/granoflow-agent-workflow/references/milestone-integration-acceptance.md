# Milestone Integration Acceptance (Layer B)

**Layer B — milestone acceptance** is **only** the successful run of a
**milestone-scoped**, **user-invisible** integration-test suite. Milestone
delivery **ends here**. It is **not** a user-facing acceptance pack, not
E2E/screenshots, and not a click-through of acceptance IDs in chat. Project E2E
belongs to最终交付 (`full-delivery-acceptance`), not milestone closeout.

Reuse orchestration mechanics from
`granoflow-integration-test-campaign` (`integration-suite-orchestration.md`)
with the scoping and writeback rules in **this** file.

## Mandatory Load

Load when preparing to execute a software milestone, when closing Layer B, or
when co-presenting Layer A + Layer B:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "milestone-integration-acceptance"
)
```

Also load `task-and-milestone-acceptance-layers`.

## What Counts As Milestone Acceptance

| In                                                                                                        | Out                                                             |
| --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Integration tests (`service_path` / real I/O) that cover **this milestone’s** features and child Outcomes | UI click E2E, screenshot/vision campaigns                       |
| Orchestrated order (e.g. add → browse → list → delete)                                                    | Ad-hoc single-test runs that skip the Suite Plan                |
| Agent-driven run to green (or recorded external residual)                                                 | Asking the user to “确认里程碑验收” as the acceptance mechanism |
| Post-green writeback: Experience (from issues) + 任务回顾                                                 | Treating child `done` alone as milestone accepted               |

User-visible Closing Summary / Residual Report may **notify** results; they do
**not** replace the IT suite as the acceptance decision.

## Scope (hard)

1. Suite inventory **Must** be limited to tests that验收 **current milestone**
   features (in-scope child tasks’ Outcomes / Evidence / acceptance IDs mapped
   to IT cases).
2. Do **not** pull other milestones’ feature IT into this suite unless an
   explicit shared dependency requires a fixture (document the exception).
3. Project-wide **完整交付** IT (lifecycle stage `integration_campaign`, see
   `full-delivery-acceptance`) remains valid for **portfolio** hardening; it
   does **not** substitute for each functional milestone’s Layer B suite when
   this reference applies.

## Before Milestone Execution — IT Sufficiency And Orchestration Preflight

**Before** starting the milestone’s implementation wave (first in-scope
non-dry-run code execution), the coordinator **Must**:

1. List every in-scope child task and its Layer A verification intent (unit vs
   authored IT).
2. Judge whether the **planned / authored** integration cases (from Task Work
   Plans + Delivery drafts + repo paths) are **sufficient to验收 all** those
   tasks’ milestone-relevant Outcomes/Evidence for Layer B.
3. If insufficient: block milestone execution with
   `milestone_it_coverage_insufficient` and require Plan/Task Work updates
   (author missing IT or justify unit-only with basis that Layer B still has a
   covering case elsewhere in the milestone suite).
4. Build a **Milestone IT Suite Plan** (separate artifact under `temp/` or
   Milestone Work evidence): topological order using `requires` / `produces` /
   `mutates` / `destroys` — e.g. create/add before browse/list before delete;
   push destructive teardown last; merge into minimal shared-session journeys.
5. Prefer **fewer steps** (rewrite/merge redundant cases) over a long flat list,
   per `integration-suite-orchestration.md`.
6. Record preflight on Milestone Work:

```yaml
milestone_it_acceptance:
  schema: granoflow_milestone_it_acceptance_v1
  contract_loaded: true
  milestone_id: <id>
  preflight_status: pending | passed | blocked
  coverage: [{ task_id, outcome_refs, it_case_ids, gap: none|missing_case }]
  suite_plan_path: <path>
  suite_order: [<case_id>...]
  simplify_notes: <how steps were reduced>
```

Fail closed `milestone_it_preflight_missing` if execution starts without
`preflight_status: passed`.

Task-local policy still applies during implement: author ≤2 IT when unit tests
are insufficient; **do not execute** those IT inside the feature task—Layer B
runs them via the Milestone IT Suite Plan.

## Running Layer B (after Layer A for in-scope children)

1. Re-read Suite Plan; refresh inventory from Deliveries (authored IT paths).
2. Execute only this milestone’s orchestrated suite (agent_auto to green).
3. On failure: classify (`product_code` / `test_harness` / `suite_orchestration`
   / `environment_external`); fix per campaign rules; **capture each material
   issue as an Experience candidate** (user-experience asset)—see Writeback.
4. Suite green → set milestone `integration_readiness_status` evidence from IT
   results; Layer B acceptance for software = **IT suite passed** for this
   milestone scope (plus explicit residuals if any external blockers remain).
5. Do **not** require the user to confirm “里程碑验收通过” for the IT decision.
   User confirmation remains only for true external/manual blockers or for
   archiving/closure actions that the App still gates separately.

## Writeback After IT (hard)

### A. Experience assets (during / after issues)

Problems found while running or fixing the milestone IT suite **Must** be
treated as **user experience assets**:

1. Draft Experience via `experience_authoring_preview` (or project equivalent)
   with: symptom, cause class, fix, milestone/task anchors, IT case ids.
2. Apply only through the approved preview→confirm→write path (do not silent-
   write Experience).
3. Link usages to the affected tasks/milestone when apply succeeds.

Skipping capture for a material product or harness lesson fails closed as
`milestone_it_experience_unrecorded` when Delivery/closure claims Layer B done
with known fix history.

### B. 任务回顾 (after suite green)

After the milestone IT suite is green, for each in-scope child that contributed
IT or was covered by the suite:

1. Open or create **任务回顾** (Task Review) for that task.
2. Record: which IT cases covered it, order dependencies (e.g. depended on add
   before delete), failures/fixes relevant to the task, Experience ids linked.
3. Use the Task Review workflow (preview/confirm where required)—do not claim
   review written from chat alone.

Fail closed `milestone_it_task_review_unrecorded` if Layer B is marked passed
and in-scope tasks lack this review writeback when IT ran for them.

## Co-presentation With Layer A

When finishing tasks and Layer B in one turn:

```markdown
## 单任务完成验收 (Layer A)

- …

## 里程碑集成验收 (Layer B · 用户不可见 IT)

- Suite plan: …
- Order: add → browse → list → delete → …
- Result: green / residual
- Experience / 任务回顾: links or pending confirmations
```

Fusing into one “全部完成” list → `acceptance_layers_fused`.

## Fail-Closed Codes

| Code                                  | When                                                                   |
| ------------------------------------- | ---------------------------------------------------------------------- |
| `milestone_it_preflight_missing`      | Implement wave without passed IT preflight                             |
| `milestone_it_coverage_insufficient`  | Suite cannot验收 all in-scope tasks                                    |
| `milestone_it_suite_unorchestrated`   | Ran IT without Suite Plan / order                                      |
| `milestone_it_scope_expanded`         | Suite pulled unrelated milestone features without documented exception |
| `milestone_it_experience_unrecorded`  | Material IT issues not captured as Experience candidates/apply path    |
| `milestone_it_task_review_unrecorded` | Suite green but 任务回顾 not written for covered tasks                 |
| `acceptance_layers_fused`             | Layer A/B fused in user-facing closeout                                |

## Must Not

- Equate milestone acceptance with E2E or user click-through of screens.
- Start milestone implement without IT sufficiency + Suite Plan preflight.
- Run delete-before-add style suites that ignore declared dependencies.
- Leave IT lessons only in chat after a green suite.
- Use project-wide IT round milestones as a way to skip per-feature-milestone
  Layer B when this reference applies.
