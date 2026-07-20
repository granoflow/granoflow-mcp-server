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

### 2. Draft And Confirm The Charter

Read `references/milestone-work-document-template.md`. Complete only
`charter_required` sections. Do not invent a complete Parallel Execution or
External Capability matrix at charter time. Explicit user confirmation is
required before the charter becomes active.

### 3. Decompose Coverage Against Acceptance

Read `references/milestone-collaboration-workflow.md`. Complete
`decompose_required` sections: portfolio table, handoffs, decomposition rules,
and acceptance coverage. If required child tasks are **missing as App
entities**, stop and hand off to `granoflow-task-authoring` (or
`granoflow-portfolio-orchestrator`)—do not silently invent incomplete tasks
here. Prefer tasks that already exist from authoring.

When requirement-driven, also read
`granoflow-agent-workflow/requirement-intake-and-traceability`.

### 4. Execute Through Child Task Work

For each ready child, first ensure Task Work **Analysis** exists. Any child that
changes UI must already satisfy the UI Change Prototype Mandate
(`prototype_requirement: required`, confirmed `ui_prototype`, `derivedFrom`
Design Baseline when present) before readiness or non-dry-run execution. The
coordinator then fills `execute_preflight_required` in Milestone Work by
aggregating Analysis outputs. Then continue readiness, execution, Delivery, and
local acceptance via the single-task Agent Workflow and
`granoflow-agent-workflow/parallel-task-execution`.

When execution may outlive one Agent turn, use
`granoflow_persistent_milestone_runner_skill`. Before the first non-dry run,
require complete `execute_preflight_required` and a confirmed authorization
manifest.

### 5. Reconcile And Replan

Classify changes as `task_local`, `portfolio_change`, `charter_change`,
`follow_up`, or `stop`. Update the living milestone summary through
context-steward when needed. Never use Milestone Work as a second status DB.

### 6. Prove Integration Readiness

Do not infer readiness from every child being `done`. Re-run acceptance coverage
against Delivery/readback, verify handoffs, run required integration checks.

### 7. Accept And Close

Present Outcome, acceptance results, integration evidence, residuals, and
follow-ups. Obtain explicit acceptance unless a precise authorization envelope
permits closure. Preview archive/closure, write, and read back.

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

## References

- Read [milestone-work-document-template.md](references/milestone-work-document-template.md)
  before drafting or revising the contract.
- Read [milestone-collaboration-workflow.md](references/milestone-collaboration-workflow.md)
  before decomposition, execution coordination, replanning, integration, or
  closure.

## Success Criteria

- Cold-start Agents recover why the active milestone exists and what overall
  success means.
- Every mandatory acceptance condition has accountable evidence.
- Child Task Work remains the only owner of child implementation detail.
- Final completion is proven on App/API readback.
