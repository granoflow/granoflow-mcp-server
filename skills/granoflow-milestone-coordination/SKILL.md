---
name: granoflow-milestone-coordination
description: Charter, decompose coverage, coordinate execution, replan, integrate, and accept one active Granoflow milestone after milestone and child-task entities exist. Does not batch-create milestones or author task titles/descriptions.
---

# Granoflow Milestone Coordination

Use this Skill when milestones and (usually) child tasks already exist and the
user wants to charter, coordinate, replan, prove integration, or close **one
active** milestone. Child Task Work owns local Analysis, Planning, execution,
and Delivery.

Do **not** use this Skill to create the project milestone portfolio or to
author task titles/descriptions. Use `granoflow-milestone-workflow`,
`granoflow-task-authoring`, and `granoflow-portfolio-orchestrator` for that.

## Keyword

- `#milestone-coordination`
- `#milestone-charter`
- `#milestone-close`

## When To Use

- Milestone entities exist (from milestone-workflow or portfolio orchestrator).
- The user asks to coordinate, continue, integrate, or close an active
  milestone.
- Child tasks may still be split/merged/reordered inside a confirmed charter.

## Ownership Boundary

- The Granoflow App and Local HTTP API remain authoritative for the milestone,
  controller Task, child tasks, and completion summary.
- Until Granoflow exposes milestone attachments, one controller Task bound to
  the milestone owns the complete Milestone Work attachment. The active
  milestone description contains only the concise living summary and controller
  Task reference.
- Each child task owns its Task Work, Delivery, and local execution history.
- The MCP server stays a thin workflow and API adapter.

## Workflow

At entry, call `granoflow_agent_preferences_get(projectId)` once. Preferences
never weaken Task Work, test, Delivery, authorization, acceptance, or
external-action gates.

### 1. Resolve The Active Milestone And Its Controller

Read the project, active milestone, description, completion summary, controller
Task, child tasks, Task Work/Delivery references, and context pack. If more than
one active target remains plausible, stop before writing.

If no controller Task exists, preview one whose sole responsibility is
orchestration, integration evidence, and closeout—not child implementation.

Checkpoints:

- Stop before writing when more than one active target remains plausible.
- Controller Task owns orchestration and closeout—not child implementation.

### 2. Draft And Confirm The Charter

Read `references/milestone-work-document-template.md`. Complete only
`charter_required` sections. Do not invent a complete Parallel Execution or
External Capability matrix at charter time. Explicit user confirmation is
required before the charter becomes active.

Checkpoints:

- Do not invent Parallel Execution or External Capability matrices at charter time.
- Explicit user confirmation required before the charter becomes active.

### 3. Decompose Coverage Against Acceptance

Read `references/milestone-collaboration-workflow.md` and, for UI portfolios,
`references/milestone-task-plan-template.yaml` plus
`granoflow-agent-workflow/screen-task-portfolio-coverage`. Complete
`decompose_required` sections: structured `task_plan`, portfolio table,
handoffs, decomposition rules, and acceptance coverage. Reach
`task_plan.status: passed` before App create when user-visible pages apply. If
required child tasks are **missing as App entities**, stop and hand off to
`granoflow-task-authoring` (or `granoflow-portfolio-orchestrator`)—do not
silently invent incomplete tasks here. Prefer tasks that already exist from
authoring.

When requirement-driven, also read
`granoflow-agent-workflow/requirement-intake-and-traceability`.

Checkpoints:

- UI: `task_plan` passed (refined screens + split probes + task summaries) before create handoff.
- Missing required child App entities → hand off to task authoring; do not silently invent tasks.
- Prefer tasks that already exist from authoring.

### 4. Execute Through Child Task Work

For each ready child, first ensure Task Work **Analysis** exists and
**Analysis Deliverables** are complete. Any child that changes UI Must have a
confirmed `ui_prototype` (`prototype_requirement: required`, `derivedFrom`
Design Baseline when present) **before Analysis may be marked complete** and
before readiness or non-dry-run execution. Do not claim milestone-level
Analysis done while any in-scope UI child still lists the prototype as missing;
emit the remaining-deliverables list from
`task-work-document-workflow` § Analysis Deliverables. The coordinator then
fills `execute_preflight_required` in Milestone Work by aggregating Analysis
outputs. Then continue readiness, execution, Delivery, and local acceptance via
the single-task Agent Workflow and
`granoflow-agent-workflow/parallel-task-execution`.

When execution may outlive one Agent turn, use
`granoflow_persistent_milestone_runner_skill`. Before the first non-dry run,
require complete `execute_preflight_required` and a confirmed authorization
manifest.

Checkpoints:

- UI-changing children: confirmed `ui_prototype` is an Analysis deliverable;
  refuse milestone Analysis-complete claims and Planning entry until present.
- Before first non-dry run require complete `execute_preflight_required` and confirmed authorization manifest.

### 5. Reconcile And Replan

Classify changes as `task_local`, `portfolio_change`, `charter_change`,
`follow_up`, or `stop`. Update the living milestone summary through
context-steward when needed. Never use Milestone Work as a second status DB.

For `portfolio_change`, `charter_change`, and `follow_up` (and for
`task_local` when Plan/Implement already started), apply the stage-rewind table
in `pipeline-attachment-and-reentry` after writeback + fan-out: re-open
Analysis/Plan as required, recompute the lifecycle board, and set
`entry_kind: midstream_change` when the digression was mid-pipeline. Do not keep
later stages falsely `done` (`pipeline_stage_not_rewound`).

Checkpoints:

- Never use Milestone Work as a second status DB.
- Confirmed early-scope changes mid-pipeline must rewind before more implement.

### 6. Milestone IT Acceptance (Layer B)

**Milestone delivery stops here** (user-invisible IT only—no E2E).

Actions:

- Before implement: IT sufficiency + Suite Plan for all in-scope tasks.
- After Layer A: run **milestone-scoped** IT; orchestrate
  (add/browse/list before delete).
- After green: Experience from issues → **任务回顾** (preview→confirm→write).
- Load `milestone-integration-acceptance` +
  `task-and-milestone-acceptance-layers`.

Success criteria:

- Preflight passed; suite scoped to this milestone; green or residual.
- Experience + 任务回顾 writeback done.

Checkpoints:

- Child `done` ≠ Layer B.
- Co-present Layer A then Layer B (`acceptance_layers_fused` if fused).

### 7. Accept And Close + optional最终交付

Actions:

- Present Outcome, Layer B evidence, residuals, follow-ups.
- Milestone accept: no E2E required.
- May offer最终交付 after any Layer B green via
  `granoflow_acceptance_delivery_skill` / `full-delivery-acceptance`:
  `project_feature_milestone_count` 1 → `e2e_direct` full-project E2E;
  ≥2 → unit + project IT + full-project E2E.
- Obtain milestone acceptance unless authorization envelope permits closure.
- Preview archive/closure, write, read back.

Success criteria:

- Milestone close evidenced by Layer B (not E2E).
- If最终交付 offered: `session_delivery` with correct `pre_e2e_path`.

Checkpoints:

- Preview→confirm→write for App mutations.
- Design lock: `temp/acceptance-delivery-design-lock-v1.json`.

## Periodic Review And Unattended Closure

Daily/weekly/monthly reviews may recommend accelerate, continue, or archive.
Unattended archive requires exact authorization, safe App capability, readable
evidence, follow-up destinations, and final readback.

## Hard Rules

- Fill Milestone Work by phase: `charter_required`, `decompose_required`,
  `execute_preflight_required`. Coordinator aggregates preflight after child
  Analysis; never fake matrices at charter time.
- Freeze confirmed Outcome/acceptance/Scope/non-goals; allow the task portfolio
  to evolve inside them.
- Child done ≠ milestone done; integration evidence is independent.
- Never persist secrets in Milestone Work, descriptions, logs, or chat.
- Completion is an evidence predicate, not a worker exit or task count.
- End every coordination turn with the Project Lifecycle Progress Board
  (`granoflow-agent-workflow/project-lifecycle-progress-board`): interactive
  keeps phase confirms; unattended is display-only.

## References

- Read [milestone-work-document-template.md](references/milestone-work-document-template.md)
  before drafting or revising the contract.
- Read [milestone-collaboration-workflow.md](references/milestone-collaboration-workflow.md)
  before decomposition, execution coordination, replanning, integration, or
  closure.
- Read `granoflow-agent-workflow/project-lifecycle-progress-board` before ending
  a project-bound turn; render next-step recommendation.

## Success Criteria

- Cold-start Agents recover why the active milestone exists and what overall
  success means.
- Every mandatory acceptance condition has accountable evidence.
- Child Task Work remains the only owner of child implementation detail.
- Final completion is proven on App/API readback.
