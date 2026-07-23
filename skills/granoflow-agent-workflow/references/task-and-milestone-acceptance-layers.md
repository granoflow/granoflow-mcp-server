# Task And Milestone Acceptance Layers

Hard presentation rule: **task-local acceptance** and **milestone acceptance**
are two different logical stages. Hosts may finish one milestone (or several)
in a single Agent turn and show both surfaces in one message—but they **Must**
remain **two labeled sections**, never one fused “everything is done” blob.

## Layer A — Single-task completion (AI self-acceptance)

**When:** a child task’s Execution finishes.

**Owner:** single-task Agent Workflow / Task Delivery.

**Authority:** that task’s Task Work + confirmed Plan (and UI `ui_prototype` when
applicable)—not milestone closure.

**Typical gates (software):** project context; structural forecast reconciled;
UI Phase A when applicable; unit/static evidence; Implementation Design
Fidelity (`implementation-design-fidelity`); task-scoped Plan reconciliation;
Delivery + `acceptance_report` HTML; Card Checkpoint; task readback `done`.
Task-local IT may be **authored** here but **not executed** (Layer B runs them).

**Does not mean:** the milestone’s integration suite passed.

## Layer B — Milestone acceptance (integration tests only)

**When:** after Layer A for in-scope children (or with explicit residuals), the
coordinator runs the **milestone-scoped** integration suite.

**Owner:** milestone coordination + `milestone-integration-acceptance`
(orchestration mechanics may reuse `granoflow-integration-test-campaign`).

**What it is:** user-**invisible** acceptance via integration tests limited to
**this milestone’s** features. Orchestrate for minimal steps (e.g. add / browse /
list before delete). See `milestone-integration-acceptance.md`.

**What it is not:** E2E/screenshots; user click-confirm of acceptance IDs as the
acceptance decision; treating “all children done” as milestone accepted.

**Before milestone implement:** IT sufficiency + Suite Plan preflight for **all**
in-scope tasks (`milestone_it_preflight_missing` / `_coverage_insufficient`).

**After suite green:** record Experience assets from issues; write **任务回顾**
for covered tasks (`milestone_it_experience_unrecorded` /
`milestone_it_task_review_unrecorded` if skipped).

## Co-presentation (same turn / multi-milestone runs)

```markdown
## 单任务完成验收 (Layer A)

- <task> — Delivery / acceptance_report — passed|residual

## 里程碑集成验收 (Layer B · 不可见 IT)

- <milestone> — suite order — green|residual — Experience/回顾 refs
```

1. Layer A first, Layer B second.
2. Labels must stay distinct (`acceptance_layers_fused` if fused).
3. Multi-milestone runs: one Layer B block **per** milestone suite.

## 最终交付测试 (Full Delivery · stages 6–7)

**Milestone delivery** ends at Layer B (user-invisible IT). E2E is **not**
required to accept a milestone.

**最终交付** (optional after any Layer B green, including a single milestone
finished today) per `full-delivery-acceptance`:

- Project has **1** feature milestone → skip portfolio unit + stage 6 IT →
  **full-project** E2E
- Project has **≥2** → full unit → all project IT → **full-project** E2E

**Not a substitute** for Layer B.

## Lifecycle mapping

| Moment                                          | Layer                                                                |
| ----------------------------------------------- | -------------------------------------------------------------------- |
| Per-child Delivery during `milestone_implement` | **A**                                                                |
| Milestone IT preflight (before implement wave)  | **B prep**                                                           |
| Milestone IT suite run (acceptance)             | **B**                                                                |
| Milestone closeout                              | **A + B only** (no E2E)                                              |
| Final delivery when entered                     | **最终交付** (`full-delivery-acceptance`) — not a Layer B substitute |
| Plan acceptance pack                            | Plan-phase only                                                      |

## Must Not

- Ask the user to perform Layer B by clicking through the product.
- Skip Layer A because Layer B IT will run later.
- Skip Layer B because every child is `done`.
- Fuse Layer A, Layer B, and 最终交付 into one unlabeled “全部完成” list.
- Require user-visible E2E to close a milestone.
- Narrow final E2E to only the touched milestone.
