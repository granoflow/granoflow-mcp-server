# Task And Milestone Acceptance Layers

Hard presentation rule: **task-local acceptance** and **milestone acceptance**
are two different logical stages. Hosts may finish one milestone (or several)
in a single Agent turn and show both surfaces in one message—but they **Must**
remain **two labeled sections**, never one fused “everything is done” blob.

## Feature Completeness Matrix (hard)

Software milestones that own Project Work requirement / acceptance / detail
ids **Must** keep a machine-readable
`feature_completeness_matrix` (`granoflow_feature_completeness_matrix_v1`) on
Milestone Work. It is an **owned-slice ledger** over Project Work
`product_spec_coverage` — never a second editable product SoT.

```yaml
feature_completeness_matrix:
  schema: granoflow_feature_completeness_matrix_v1
  status: draft | ready | green | blocked
  fail_closed_code: feature_completeness_matrix_incomplete
  rows:
    - id: FCM-...
      sot_ref: <Project Work R-* / detail / acceptance id>
      task_local_key: T1
      task_id: <uuid|null until create>
      impl_status: pending | implemented | blocked_external
      test_ref: <path or case id|null until implement>
      result: pending | green | blocked_external
```

Rules:

- `task_plan.status: passed` requires matrix `status: ready` (every row has
  `sot_ref` + `task_local_key`).
- Layer A task finish requires every row owned by that task to have
  `impl_status: implemented` and non-empty `test_ref`, then `result: green`
  (or `blocked_external` only for true host/environment blockers).
- Layer B / `acceptance_status: passed` requires matrix `status: green`.
- Child tasks all `done` is **not** enough without matrix green.
- Lint: `scripts/lint_feature_completeness_matrix.py`.

### Residual classification (hard)

| Allowed residual                          | Forbidden (functional residual)                                  |
| ----------------------------------------- | ---------------------------------------------------------------- |
| `blocked_external` host/OS capability     | `stub` / `deferred_feature` as shippable UI                      |
| Pixel / Baseline manual visual            | User-visible “后续版本提供” / “将在后续版本” deferral copy       |
| External-device handoff (`tested: false`) | Delivery `Residuals` that close a SoT behavior without impl+test |

Functional residuals fail closed as `functional_residual_forbidden`. Claiming
Layer A/B / milestone / final delivery green while matrix rows remain
`pending` or stubbed fails as `feature_completeness_overclaim_green`.

## Layer A — Single-task completion (AI self-acceptance)

**When:** a child task’s Execution finishes.

**Owner:** single-task Agent Workflow / Task Delivery.

**Authority:** that task’s Task Work + confirmed Plan (and UI `ui_prototype` when
applicable)—not milestone closure.

**Typical gates (software):** project context; structural forecast reconciled;
UI Phase A when applicable; unit/static evidence; Implementation Design
Fidelity (`implementation-design-fidelity`); task-scoped Plan reconciliation;
owned `feature_completeness_matrix` rows updated (`implemented` + `test_ref`);
Delivery + `acceptance_report` HTML; Card Checkpoint; task readback `done`.
Task-local IT may be **authored** here but **not executed** (Layer B runs them).

**Does not mean:** the milestone’s integration suite passed, or that other
matrix rows for sibling tasks are green.

## Layer B — Milestone acceptance (integration tests only)

**When:** after Layer A for in-scope children (or with **allowed** residuals
only), the coordinator runs the **milestone-scoped** integration suite.

**Owner:** milestone coordination + `milestone-integration-acceptance`
(orchestration mechanics may reuse `granoflow-integration-test-campaign`).

**What it is:** user-**invisible** acceptance via integration tests limited to
**this milestone’s** features **plus** matrix `status: green`. Orchestrate for
minimal steps (e.g. add / browse / list before delete). See
`milestone-integration-acceptance.md`.

**What it is not:** E2E/screenshots; user click-confirm of acceptance IDs as the
acceptance decision; treating “all children done” as milestone accepted;
treating suite green while matrix rows stay stubbed/pending.

**Before milestone implement:** IT sufficiency + Suite Plan preflight for **all**
in-scope tasks (`milestone_it_preflight_missing` / `_coverage_insufficient`);
matrix at least `ready`.

**After suite green:** matrix must reach `green`; record Experience assets from
issues; write **任务回顾** for covered tasks (`milestone_it_experience_unrecorded`
/ `milestone_it_task_review_unrecorded` if skipped).

## Co-presentation (same turn / multi-milestone runs)

```markdown
## 单任务完成验收 (Layer A)

- <task> — Delivery / acceptance_report — passed|residual
- matrix rows: <ids> → green|blocked_external

## 里程碑集成验收 (Layer B · 不可见 IT)

- <milestone> — suite order — green|residual — matrix status — Experience/回顾 refs
```

1. Layer A first, Layer B second.
2. Labels must stay distinct (`acceptance_layers_fused` if fused).
3. Multi-milestone runs: one Layer B block **per** milestone suite.

## 最终交付测试 (Full Delivery · stages 6–7)

**Milestone delivery** ends at Layer B (user-invisible IT + matrix green). E2E
is **not** required to accept a milestone.

**最终交付** (optional after any Layer B green, including a single milestone
finished today) per `full-delivery-acceptance`:

- Project has **1** feature milestone → skip portfolio unit + stage 6 IT →
  **full-project** E2E
- Project has **≥2** → full unit → all project IT → **full-project** E2E

Before claiming final delivery complete: every feature milestone matrix is
`green` (row-level `blocked_external` only for allowed residual classes) and a
deferral-copy gap scan is clean (`functional_residual_forbidden` otherwise).

**Not a substitute** for Layer B.

## Lifecycle mapping

| Moment                                          | Layer                                                                |
| ----------------------------------------------- | -------------------------------------------------------------------- |
| Per-child Delivery during `milestone_implement` | **A**                                                                |
| Milestone IT preflight (before implement wave)  | **B prep**                                                           |
| Milestone IT suite run (acceptance)             | **B**                                                                |
| Milestone closeout                              | **A + B only** (no E2E); matrix `green`                              |
| Final delivery when entered                     | **最终交付** (`full-delivery-acceptance`) — not a Layer B substitute |
| Plan acceptance pack                            | Plan-phase only                                                      |

## Fail-Closed Codes

| Code                                     | When                                                                 |
| ---------------------------------------- | -------------------------------------------------------------------- |
| `feature_completeness_matrix_missing`    | Software milestone lacks matrix when decompose/close requires it     |
| `feature_completeness_matrix_incomplete` | Matrix not `ready`/`green` for the gate being claimed                |
| `functional_residual_forbidden`          | Feature stub / deferral copy / functional gap labeled as residual    |
| `feature_completeness_overclaim_green`   | Claimed Layer A/B/milestone/final green while matrix rows incomplete |
| `acceptance_layers_fused`                | Layer A/B fused in user-facing closeout                              |

## Must Not

- Ask the user to perform Layer B by clicking through the product.
- Skip Layer A because Layer B IT will run later.
- Skip Layer B because every child is `done`.
- Skip matrix green because the IT suite is green.
- Fuse Layer A, Layer B, and 最终交付 into one unlabeled “全部完成” list.
- Require user-visible E2E to close a milestone.
- Narrow final E2E to only the touched milestone.
- Close tasks or milestones with user-visible “后续版本” / stub delivery
  surfaces for SoT behaviors.
- Park unfinished SoT features in Unattended Residual Report as if the
  declared scope were complete.
