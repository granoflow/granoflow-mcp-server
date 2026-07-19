---
name: granoflow-milestone-workflow
description: Define, decompose, coordinate, replan, integrate, and accept one Granoflow milestone through a stable Milestone Work contract while each child task keeps its own Task Work lifecycle.
---

# Granoflow Milestone Workflow

Use this bundled MCP skill when the user delegates an outcome that spans multiple
Granoflow tasks. It turns one milestone into a bounded collaboration contract,
keeps decomposition and dependencies explicit, lets child Task Work documents
own local execution, and requires milestone-level integration evidence before
closure.

## When To Use

- The requested outcome needs multiple tasks, workstreams, repositories, people,
  or delivery surfaces.
- The user asks an Agent to continue toward a milestone instead of completing one
  already-bounded task.
- Child tasks may be discovered, split, merged, reordered, deferred, or cancelled
  while the milestone Outcome and acceptance boundary remain stable.
- Completion requires cross-task integration or one user-visible journey that no
  individual Task Work can prove alone.

Do not use this skill for one bounded task, a project roadmap containing several
independent milestones, or a retrospective that does not authorize future work.
Use the bundled Granoflow Agent Workflow for each child task.

## Ownership Boundary

- The Granoflow App and Local HTTP API remain authoritative for the milestone,
  controller Task, child tasks, task states, nodes, descriptions, and completion
  summary.
- Until Granoflow exposes milestone attachments, one controller Task bound to the
  milestone owns the complete Milestone Work attachment. The active milestone
  description contains only the concise living summary and controller Task
  reference.
- Each child task owns its Task Work, Delivery, evidence, and local execution
  history. Never copy child implementation plans into Milestone Work.
- The MCP server stays a thin workflow and API adapter. Do not add a parallel
  milestone database, hidden task-state cache, or direct SQLite path.

## Workflow

At milestone entry, call `granoflow_agent_preferences_get(projectId)` once and
pass the compact resolved preferences to child task workflows. Project and local
defaults may control explanation detail, unattended defaults, and Git policy;
they never weaken Task Work, test, Delivery, authorization, acceptance, or
external-action gates.

### 1. Resolve One Milestone And Its Controller

Read the project, active milestone, milestone description, completion summary,
controller Task, child tasks, current Task Work and Delivery references, and
available context pack. If more than one target remains plausible, stop before
writing.

If no controller Task exists, preview one task bound to the milestone whose sole
responsibility is orchestration, integration evidence, and final closeout. Do not
pretend that creating the controller also authorizes child execution.

### 2. Draft And Confirm The Charter

Read `references/milestone-work-document-template.md`. Draft Outcome,
user-visible acceptance, Scope, non-goals, current truth, constraints, workstreams,
material risks, and the next allowed action. Do not begin with a frozen task list.

Discuss only decisions that can change the milestone Outcome, acceptance, Scope,
non-goals, ownership, or material risk. Explicit user confirmation is required
before the charter becomes active.

### 3. Decompose Against Acceptance

Read `references/milestone-collaboration-workflow.md`. Build workstreams, child
tasks, dependency and handoff edges, and an acceptance-coverage matrix. Every
mandatory acceptance condition must have one accountable task or the controller
Task. A task may contribute to several conditions, but no condition may be
considered covered merely because a related task title exists.

Run the bundled decomposition check. It passes only when the task portfolio is
minimal but sufficient, dependencies are acyclic or intentionally gated, handoff
outputs are observable, and every required integration check has an owner.

### 4. Execute Through Child Task Work

For each ready child task, delegate Analysis, Planning, readiness review,
execution, Delivery, and local acceptance to the bundled single-task workflow.
Run independent tasks in parallel only when their write surfaces, inputs, and
acceptance evidence do not conflict.

The milestone contract may authorize bounded continuation, but every action must
also pass the current delegated-authorization envelope. Missing authorization,
secrets, publishing rights, deletion rights, payment, external messaging, or a
subjective decision remains a real stop.

When execution may outlive one Agent turn, use the bundled
`granoflow_persistent_milestone_runner_skill`. It supervises finite workers with
leases and checkpoints; it does not make one conversation immortal. The public
workflow remains provider-neutral. A separate user Skill may select the worker
command or model without weakening authorization or acceptance.

Before the first non-dry run, require a confirmed milestone authorization
manifest that records observed full runtime access, preauthorization of in-scope
internal phase gates, and every required external capability as `granted`,
`excluded`, or `interaction_required`. Unresolved external work is scheduled
after independent safe work and remains a visible resumable interaction node.

### 5. Reconcile And Replan

After a child completes, blocks, changes a shared contract, or discovers new
work, re-read live milestone and task state. Classify the change as:

- `task_local`: revise only that Task Work;
- `portfolio_change`: add, split, merge, reorder, defer, or cancel child tasks
  without changing the confirmed charter;
- `charter_change`: reopen confirmation because Outcome, acceptance, Scope,
  non-goals, ownership, or material risk changed;
- `follow_up`: move desirable but non-required work outside this milestone;
- `stop`: evidence invalidates the milestone or makes safe continuation impossible.

Update the active milestone description through the App-owned context-steward
surface when the concise living summary materially changes. Never use document
prose as a second task-status database.

### 6. Prove Integration Readiness

Do not infer milestone readiness from every child being `done`. Re-run the
acceptance-coverage matrix against actual Delivery and readback evidence, verify
cross-task handoffs, run required regression or end-to-end checks, and identify
residual or follow-up work.

Set integration readiness to passed only when the combined system or user journey
exists on the real required surface. A green local test, an uploaded filename, or
several independently completed tasks is insufficient by itself.

### 7. Accept And Close The Milestone

Show the user the milestone Outcome, acceptance results, integration evidence,
scope differences, unresolved residuals, and proposed follow-up placement. Obtain
explicit user acceptance for subjective or manual conditions and for milestone
closure unless a current authorization envelope names this exact milestone and
explicitly permits that closure.

Preview archive/closure through the App-owned milestone context workflow. After
approval, persist the completion summary, move follow-ups, archive or complete the
milestone through supported App/API behavior, and read the final state back.

## Periodic Review And Unattended Closure

Daily, weekly, and monthly reviews inspect milestone deadline,
title/description signals, status, and linked internal tasks. Classify whether
to accelerate, continue, or consider archival; wording signals remain inference
until backed by evidence or user confirmation. An overdue milestone is not
automatically obsolete.

In unattended mode, announce the recommendation and evidence as a notice before
any action. Archive only when authorization covers this exact milestone, the App
exposes a safe archive operation, completion and integration evidence are
readable, follow-ups have a destination, and final state is read back. Otherwise
stop at a visible blocker; never emulate archive with a generic status or
description update.

## Hard Rules

- Freeze the confirmed Outcome, acceptance boundary, Scope, and non-goals; allow
  the task portfolio to evolve inside them.
- Keep live task state in Granoflow entities. Milestone Work records responsibility,
  dependency, evidence contribution, and decisions, not a manually maintained
  duplicate status ledger.
- A child task being done proves only its local contract. Milestone completion
  requires independent integration evidence.
- Reopen charter confirmation for material scope or acceptance changes; do not
  hide expansion inside a new child task.
- Preserve preview, confirmation, controlled write, and App/API readback for the
  controller Task, Milestone Work attachment, milestone context, and closure.
- Never persist secrets, OTPs, recovery codes, tokens, or private authorization
  material in Milestone Work, task descriptions, logs, or chat.
- Never treat a worker exit, final answer, progress summary, elapsed time, or
  task count as completion. Completion remains an evidence predicate.
- Repeated no-evidence attempts must become replan, then a visible interaction
  wait; continue other independent tasks instead of repeating the same strategy.

## References

- Read [milestone-work-document-template.md](references/milestone-work-document-template.md)
  before drafting or revising the contract.
- Read [milestone-collaboration-workflow.md](references/milestone-collaboration-workflow.md)
  before decomposition, execution coordination, replanning, integration review,
  or closure.

## Success Criteria

- A cold-start Agent can recover why the milestone exists, what counts as overall
  success, which boundaries are fixed, how child tasks contribute, and when to
  stop or ask the user.
- Every mandatory acceptance condition has accountable evidence, including
  cross-task and user-visible integration where applicable.
- Child Task Work remains the only owner of child implementation detail.
- Final completion is proven on the App/API-owned surface and read back instead
  of inferred from prose or local work.
