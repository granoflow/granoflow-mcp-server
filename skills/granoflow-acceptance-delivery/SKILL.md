---
name: granoflow-acceptance-delivery
description: >-
  Route milestone acceptance (Layer A/B) and final delivery. Milestone delivery
  stops at user-invisible milestone-scoped IT; final delivery may start after any
  Layer B green—1 feature milestone skips portfolio unit/IT and runs full-project
  E2E; ≥2 runs full unit + project IT + full-project E2E. Thin router over
  granoflow-agent-workflow references and IT/E2E campaign Skills. Not a
  substitute for task-orchestrator Analysis/Plan/run.
---

# Granoflow Acceptance And Final Delivery

Thin router for **验收分层** and **最终交付**. Contract detail is SoT in
`granoflow-agent-workflow` references. This Skill tells the agent **when** to
load which contract and **which path** to take—without fusing Layer A/B or
narrowing E2E.

## Keyword

- `#最终交付`
- `#milestone-it`
- `#full-delivery`
- `#acceptance-layers`

## When to use

- Closing child tasks vs closing a milestone (Layer A vs Layer B).
- Running 里程碑集成验收 (user-invisible IT).
- Offering or starting 最终交付 / 完整交付 / 交付测试.
- Checking whether to skip portfolio unit/IT before E2E.

## Not this Skill

| Concern                         | Owner                                                       |
| ------------------------------- | ----------------------------------------------------------- |
| Single-task Analysis/Plan/run   | `granoflow-task-orchestrator` + `granoflow-agent-workflow`  |
| Milestone charter / decompose   | `granoflow-milestone-coordination` (uses Layer B path here) |
| Portfolio IT execution loop     | `granoflow-integration-test-campaign`                       |
| Full-project E2E execution loop | `granoflow-e2e-test-campaign`                               |

## Mandatory loads

Canonical contracts (prefer these over pointer stubs in this Skill):

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "task-and-milestone-acceptance-layers" | "milestone-integration-acceptance" | "full-delivery-acceptance"
)
```

Also emit `project-lifecycle-progress-board` on project-bound turns.

## Example requests

- 开始最终交付
- 里程碑集成验收怎么跑
- Layer A 和 Layer B 怎么分开写

## Workflow

For Delivery and review, route code review plus QA by default. Add
`design-review`, `benchmark`, CSO, or `canary` only when their conditions
apply. Treat third-party reviewers as preferred methods with evidenced native
fallback and no authorization effect; do not copy Milestone review protocol
into this skill.

### 1. Layer A — task closeout

Finish each child task with Delivery / `acceptance_report`. Author integration
tests when needed; **do not** run the suite inside the feature task.

Actions:

- Load `task-and-milestone-acceptance-layers`.
- Complete task-local Delivery gates (design fidelity / prototype Phase A when
  applicable).
- Author ≤2 `service_path` IT cases with `requires`/`produces` when useful.

Success criteria:

- Closeout has a labeled **单任务完成验收 (Layer A)** section.
- IT authored, not executed, in the feature task.
- Child `done` does **not** claim the milestone accepted.

Checkpoints:

- `acceptance_layers_fused` if merged with Layer B into one unlabeled blob.
- Preview→confirm→write for App mutations.

Artifacts:

- Delivery
- `acceptance_report`

Rules:

- No milestone claim from child `done` alone.

### 2. Layer B — milestone IT (milestone delivery ends here)

Accept the milestone with **user-invisible**, **milestone-scoped** integration
tests only. No user-visible E2E for milestone accept.

Actions:

- Before implement: IT sufficiency + Suite Plan for all in-scope tasks.
- Orchestrate a minimal order (e.g. add → browse → list → delete).
- Run under `campaign_drive: agent_auto` (reuse IT campaign mechanics) to green
  or residual.
- After green: Experience from issues → **任务回顾** (preview→confirm→write).
- Load `milestone-integration-acceptance`.

Success criteria:

- Suite green or residual recorded.
- Experience + 任务回顾 writeback done for covered tasks.
- Milestone closeout does **not** require E2E.

Checkpoints:

- `milestone_it_preflight_missing` / `milestone_it_coverage_insufficient` /
  `milestone_it_suite_unorchestrated` / `milestone_it_experience_unrecorded` /
  `milestone_it_task_review_unrecorded` when skipped.
- Co-present Layer A then Layer B as separate labeled sections.

Artifacts:

- Milestone IT Suite Plan
- Experience
- 任务回顾

Rules:

- User-invisible only; portfolio `integration_campaign` does **not** replace
  Layer B.

### 3. 最终交付 (optional after any Layer B green)

Before starting最终交付: if an open `midstream_change` or pending discussion
writeback still needs stage rewind, finish re-entry first
(`pipeline-attachment-and-reentry` / `pipeline_reentry_skipped`).

May offer/enter after **any** feature milestone’s Layer B is green—including
when only one milestone finished this run/day. Path uses **project**
feature-milestone count (via `milestone_list`), not session-touched count.

| `project_feature_milestone_count` | `pre_e2e_path`     | Steps                                                                                                                  |
| --------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| **1**                             | `e2e_direct`       | Skip portfolio unit + stage `integration_campaign`; `integration_gate: waived_single_milestone` → **full-project** E2E |
| **≥ 2**                           | `full_unit_and_it` | Full unit suite → `granoflow-integration-test-campaign` → **full-project** E2E                                         |

Actions:

- Load `full-delivery-acceptance`; emit `session_delivery` on the lifecycle board.
- Delegate IT/E2E loops to the campaign Skills; keep E2E **full-project**.

Success criteria:

- Correct `pre_e2e_path` for the project count.
- When E2E runs: suite green; Phase B AI loop complete; Evidence Pack; Closing
  Summary; `user_final_acceptance`; visible window; screenshots under `temp/`.

Checkpoints:

- `full_delivery_pre_e2e_skip_invalid` if `e2e_direct` with count ≠ 1.
- `full_delivery_e2e_not_full_project` if E2E is narrowed to “what we touched”.
- `full_delivery_milestone_e2e_required` if E2E is demanded to close a milestone.

Artifacts:

- `session_delivery`
- Evidence Pack (`granoflow_e2e_evidence_pack_v1`)
- Closing Summary (`granoflow_e2e_campaign_closing_summary_v1`)

Rules:

- Final delivery does not replace Layer B.
- Design lock: `temp/acceptance-delivery-design-lock-v1.json`.
- Device capability inventory is not the required E2E matrix. Run only
  `host_matrix.selection.selected_host_ids`. For every other supported
  platform, Delivery must preserve `tested: false` and provide an
  external-device test handoff. A reply equivalent to “知道了 / 了解 / 我会测试”
  changes only handoff acknowledgement to accepted; it must not claim that
  platform green.

## Hard Rules

1. Layer A and Layer B stay two labeled sections (`acceptance_layers_fused`).
2. Milestone delivery = user-invisible milestone IT only (no E2E).
3. Layer B: preflight + Suite Plan; Experience + 任务回顾 after green.
4. Final delivery may start after any Layer B green.
5. Path by project feature-milestone count (`e2e_direct` vs `full_unit_and_it`).
6. E2E is always full-project.
7. Preview→confirm→write for Experience / 任务回顾 / App-writing closeouts.
8. Before UI Task Delivery, load `responsive-prototype-finalization` and require
   rendered fidelity rows for every required layout family. Missing captures,
   threshold failures, failed AI visual review, or unapproved native
   differences block Delivery.

## References

Pointer stubs in this Skill list discoverable `referenceId`s. **Always load the
canonical body** from `granoflow-agent-workflow` with the same `referenceId`.

- [full-delivery-acceptance.md](references/full-delivery-acceptance.md)
- [milestone-integration-acceptance.md](references/milestone-integration-acceptance.md)
- [task-and-milestone-acceptance-layers.md](references/task-and-milestone-acceptance-layers.md)

## Success Criteria (skill quality)

- Preview→confirm→write remains a hard gate for App writes.
- Every major step leaves a machine-readable artifact or fail-closed code.
- Thread constraints in `temp/acceptance-delivery-design-lock-v1.json` still
  match the package references (preservation tests green).
