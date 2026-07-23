# Full Delivery Acceptance (最终交付测试 / 完整交付)

User-facing **最终交付** for lifecycle stages **`integration_campaign` +
`e2e_campaign`**, with a path that may skip the pre-E2E suite when the project
has only one feature milestone. This is **not** a substitute for per-milestone
Layer B (`milestone-integration-acceptance`).

**Milestone delivery** ends when Layer B (user-invisible milestone IT) is green.
Milestone closeout **Must not** require user-visible E2E.

Thread design lock (do not drop on polish):
`temp/acceptance-delivery-design-lock-v1.json`.

## Mandatory Load

Load when offering or entering最终交付测试 / 完整交付 / 交付测试, or when
closing a software session after milestone Layer B:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "full-delivery-acceptance"
)
```

Also load `project-lifecycle-progress-board` and
`task-and-milestone-acceptance-layers`.

## When Final Delivery May Start

Final delivery **May** be offered or entered after **any** feature milestone’s
Layer B is green—including when only one milestone was finished in this run /
day. Do **not** treat a single finished milestone as “session already delivered,
never mention最终交付”.

Interactive: advise or ask whether to run最终交付 now (list other milestones when
the project has more than one). Unattended: emit recommendation on the board /
Residual Report; start only when the durable grant covers campaign stages or the
user later requests it.

## Project Milestone Count (hard)

Count **feature milestones in the Granoflow project** (via `milestone_list` /
resolve)—not “milestones touched this session”.

| `project_feature_milestone_count` | Pre-E2E path (`pre_e2e_path`)                                                                                                              | E2E                         |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------- |
| **1**                             | `e2e_direct` — **skip** portfolio full unit suite and stage `integration_campaign` (milestone Layer B already covered that milestone’s IT) | **Always full-project** E2E |
| **≥ 2**                           | `full_unit_and_it` — full unit suite → orchestrate **all** user-invisible project IT → then E2E                                            | **Always full-project** E2E |

Fail closed:

- `full_delivery_pre_e2e_skip_invalid` — used `e2e_direct` when count ≠ 1, or
  skipped unit/IT when count ≥ 2 without residual
- `full_delivery_e2e_not_full_project` — E2E suite scoped to a subset of
  journeys to “save time” after a local change

## Execution Order

### Path A — `e2e_direct` (exactly one feature milestone)

1. Confirm Layer B green for that milestone (or recorded residual).
2. Mark stage `integration_campaign` **waived** for this path:
   - Board evidence: `waived_single_milestone_project` (status `done` with that
     evidence, or `not_started` with `session_delivery.pre_e2e_path: e2e_direct`
     and next_action → `e2e_campaign`).
   - E2E durable state: `integration_gate: waived_single_milestone`.
3. Run **full-project** `e2e_campaign` (coverage matrix from Project Work; no
   narrowed “only what we touched” suite).

Do **not** re-run portfolio unit + IT as a gate before E2E on this path.

### Path B — `full_unit_and_it` (two or more feature milestones)

1. **Full unit tests** — entire unit/static suite. Fail closed
   `full_delivery_unit_suite_incomplete` if skipped or not green without
   residual.
2. **All user-invisible integration tests** — project-wide suite via
   `granoflow-integration-test-campaign` / stage `integration_campaign`
   (`campaign_drive: agent_auto`). Does **not** replace per-milestone Layer B.
3. **Full-project E2E** — `integration_gate: complete`, then
   `granoflow-e2e-test-campaign` / stage `e2e_campaign`.

Do not claim `project_complete` while skipping required path steps without an
explicit residual.

## Why E2E Is Always Full-Project

E2E exists to catch regressions when a change in one place breaks another.
Narrowing E2E to the touched milestone or touched screens fails closed as
`full_delivery_e2e_not_full_project`.

## Board Fields

```yaml
session_delivery:
  schema: granoflow_session_delivery_v1
  milestones_touched_count: <int> # this run; informational
  milestones_touched: [<key-or-id>]
  project_feature_milestone_count: <int> # hard input for path selection
  pre_e2e_path: e2e_direct | full_unit_and_it | not_selected
  status: offer_or_ask | in_progress | complete | not_applicable
  prompt_full_delivery: true | false # may be true after any Layer B green
  other_milestones: [] # when count ≥ 2 or advising
  recommendation: "<plain language>"
```

User-facing labels: **完整交付 / 最终交付测试**. Stage ids stay
`integration_campaign` + `e2e_campaign`.

## Co-presentation

```markdown
## 单任务完成验收 (Layer A)

…

## 里程碑集成验收 (Layer B · 用户不可见 IT · 里程碑交付止于此)

…

## 最终交付测试 (可选 / 进行中)

- 项目功能里程碑数: 1 → 跳过全量单测与项目级 IT，直接全面 E2E
- 或: 项目功能里程碑数: N → 全量单测 → 全部不可见 IT → 全面 E2E
```

## Relationship

| Concern              | Owner                                    |
| -------------------- | ---------------------------------------- |
| Milestone acceptance | Layer B only (no E2E)                    |
| Final delivery       | This reference + IT/E2E Skills           |
| True project close   | After final delivery green (or residual) |

## Fail-Closed Codes

| Code                                   | When                                                           |
| -------------------------------------- | -------------------------------------------------------------- |
| `full_delivery_pre_e2e_skip_invalid`   | `e2e_direct` when count ≠ 1, or skipped unit/IT when count ≥ 2 |
| `full_delivery_e2e_not_full_project`   | E2E not full-project                                           |
| `full_delivery_unit_suite_incomplete`  | Path B without green full unit suite                           |
| `full_delivery_order_violation`        | Path B steps out of order                                      |
| `full_delivery_session_fields_missing` | Invalid / incomplete `session_delivery` when present           |
| `full_delivery_milestone_e2e_required` | Agent required user-visible E2E to close a milestone           |

## Must Not

- Require E2E to accept a milestone (Layer B is enough).
- Skip offering最终交付 solely because only one milestone finished today.
- Use `e2e_direct` on multi-milestone projects.
- Narrow E2E to “what we changed”.
- Fuse Layer A / Layer B / 最终交付 into one unlabeled “全部完成” list.
