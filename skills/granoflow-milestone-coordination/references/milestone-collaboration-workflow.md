# Milestone Collaboration Workflow

Owned by `granoflow-milestone-coordination`. For requirement-driven milestones,
read the shared
'granoflow-agent-workflow/requirement-intake-and-traceability' contract first.
The portfolio covers stable requirement ids and acceptance ids, not merely the
sections that happened to appear in a user's documents.

Milestone entity creation belongs to `granoflow-milestone-workflow`. Child task
title/description creation belongs to `granoflow-task-authoring`. Full
create-all pipelines belong to `granoflow-portfolio-orchestrator`.

This workflow coordinates one **active** confirmed milestone across an evolving
set of child tasks. It owns dependencies, handoffs, integration proof, and
milestone acceptance. It does not replace child Task Work and does not
batch-create milestones or author task prose.

**Milestone Work is optional and thin.** Product/acceptance current truth stays
in Project Work. Prefer milestone entity + Project coverage tables. Draft a
Milestone Work attachment only for parallel execution, authorization
aggregation, or integration closeout that needs a shared coordinator document.
Never treat Milestone Work as a second product requirement ledger.

## Phase Model

```text
Resolve active milestone and controller
  -> draft and confirm charter
  -> decompose and run decomposition check
  -> if required tasks missing as entities, hand off to task-authoring
  -> execute through child Task Work
  -> reconcile and replan from live evidence
  -> prove integration readiness
  -> accept and close the milestone
```

Only one phase transition may be claimed at a time. A later phase never repairs
an invalid earlier state silently.

## 1. Resolve And Establish Ownership

Resolve exactly one project and one **active** milestone. Read the milestone,
project context, completion summary, linked tasks, controller candidate, Task
Work and Delivery references, and relevant context pack.

Use an existing controller Task when its responsibility is milestone
orchestration and closeout. Otherwise preview a new controller Task bound to the
milestone. Its description must state that it owns the Milestone Work attachment,
portfolio decisions, integration evidence, and final closure, but not child
implementation.

If the Local HTTP API is unavailable, keep any local draft explicitly unbound or
bound only from prior trusted readback. Do not claim attachment, context update,
task creation, authorization, or active status until App/API readback succeeds.

## 2. Charter Confirmation

Draft only `charter_required` fields before decomposing (see
`milestone-work-document-template.md` Phased Required Fields):

- one milestone Outcome;
- user-visible or system-visible acceptance conditions with stable IDs;
- Scope and necessary non-goals;
- milestone-level current truth and constraints (not deep task Analysis);
- coarse workstreams or capability areas;
- material milestone-level risks;
- Integration Verification skeleton;
- at least one end-to-end example of combined false success;
- next orchestration action.

Leave `decompose_required` and `execute_preflight_required` as
`pending_decomposition` / `pending_task_analysis`. Do not invent a complete
Parallel Execution or External Capability matrix at charter time.

Ask only questions that can change charter fields. Show the current
understanding, recommendation, alternatives, impact, and requested decision
together. Explicit confirmation sets `charter_status: confirmed` and
`required_fields_phase: charter_required`.

Do not treat permission to discuss or decompose as execution authorization.

## 3. Decomposition Check

Complete `decompose_required` fields. Build the smallest sufficient portfolio.
Each child task must have one distinct responsibility and contribute evidence to
at least one milestone acceptance ID.

The decomposition passes only when all checks below pass:

1. **Coverage:** every mandatory acceptance ID has an accountable task or the
   controller.
2. **Necessity:** every proposed child task changes an acceptance result, removes
   a material blocker, or provides required integration evidence.
3. **Boundary:** child responsibilities do not duplicate each other or hide a
   second milestone.
4. **Dependencies:** every edge names an observable output and consuming input;
   cycles are removed or represented as explicit human/integration gates.
5. **Handoffs:** source of truth, compatibility contract, verification, and
   invalidation conditions are explicit.
6. **Acceptance:** cross-task checks have owners and cannot be satisfied only by
   local task completion.
7. **Readiness:** known accounts, inputs, environments, authorization, and manual
   decisions are available or recorded as blockers.

Set `decomposition_status: revisions_required` when the portfolio is plausible
but incomplete. Set `blocked` when a missing decision or unavailable prerequisite
prevents safe decomposition. Do not create speculative tasks merely to make the
table look complete. When required portfolio rows lack App task entities, hand
off to `granoflow-task-authoring` (or `granoflow-portfolio-orchestrator`) instead
of authoring full task prose inside this Skill. When the check passes, set
`decomposition_status: passed` and `required_fields_phase: decompose_required`.

## 4. Portfolio Execution

UI-changing child tasks must satisfy the Agent Workflow UI Change Prototype
Mandate before readiness or dispatch: `prototype_requirement: required`,
confirmed `ui_prototype`, and `derivedFrom` the project Design Baseline when
present. Missing prototypes return `ui_prototype_required` and stay out of the
executable batch.

### Execute preflight after child Analysis

Before non-dry-run dispatch, the milestone coordinator completes
`execute_preflight_required` in Milestone Work:

1. Let each ready child run Task Work Analysis (and Planning as needed) so
   write surfaces, dependencies, and authorization needs are explicit in Task
   Work—not in duplicated milestone prose.
2. Aggregate those Analysis outputs plus live repository/runtime facts into
   Parallel Execution, Delegation And Authorization Boundary, Persistent
   Execution Preflight, and External Capability Matrix.
3. Refresh the same Milestone Work sections on reconcile when a child Analysis
   revises material write surfaces. Do not wait for every child Analysis in the
   whole portfolio to finish before filling preflight for the first ready batch.
4. Never treat a charter-time placeholder matrix as a real conflict assessment.

Then read `granoflow-agent-workflow/parallel-task-execution` and dispatch every
member of a fully `parallel_safe` batch at once when the host supports multiple
workers. Serialize ordered dependencies, overlapping writes, shared side
effects, and unknown material surfaces. Recheck revisions before writes and
replan only the affected batch when new overlap is discovered; other independent
work continues. Set `required_fields_phase: execute_preflight_required` only when
preflight sections are complete for the work about to run.

### Persistent execution preflight

For work expected to continue beyond one Agent turn, establish all of these
before starting workers (still coordinator-owned in Milestone Work / manifest):

- the host reports full runtime access and the milestone requires it;
- one confirmed authorization manifest preauthorizes in-scope internal phase
  gates without pretending to grant external account access;
- every required external capability is explicitly `granted`, `excluded`, or
  `interaction_required` and is mapped to affected task ids;
- granted capabilities carry only a credential reference; secret values never
  enter Granoflow, runner state, prompts, logs, or chat;
- unresolved interaction tasks are ordered after all independent safe work.

Use the Persistent Milestone Runner when restart recovery is required. Each
worker remains finite. The supervisor persists leases, heartbeats, bounded
attempt metadata, and checkpoints so later workers can resume. Worker selection
is supplied by the host or a user Skill; this public contract does not define a
provider or model ladder.

Before creating a controller or child task, read and apply
`granoflow-agent-workflow/task-authoring-quality-contract`. Milestone
decomposition changes placement and coordination, not task writing quality.

For each unblocked task:

1. create or resolve the child task under the same milestone;
2. invoke the single-task Agent Workflow;
3. keep its Analysis, Plan, readiness, execution, Delivery, and acceptance local;
4. consume only current direct or delegated authorization;
5. read back Task Work, Delivery, nodes, and final task state;
6. update the milestone acceptance coverage with evidence references, not copied
   execution prose.

Parallel execution is allowed only when tasks do not write the same authoritative
surface, do not depend on unconfirmed outputs, and do not compete for a subjective
user decision. Otherwise preserve dependency order.

The coordinator should continue all independent safe work before waiting. It may
batch decision-changing questions, but it must not turn a missing answer into
consent.

### Progress and completion are different states

A final answer, summary, successful process exit, worker report, elapsed runtime,
or child-task count may update progress only. A child is accepted only after
authoritative task readback, a readable accepted Task Delivery whose content hash
matches, and finished task nodes when present. The milestone still requires its
separate integration-readiness and closure checks.

If three consecutive attempts produce no new verifiable evidence, require a
materially different plan. If the next attempt also stagnates, preserve a
resumable interaction node and stop retrying that task until its task fingerprint
or authorization changes. Scan past it and continue other eligible tasks.

## 5. Replanning Rules

Reconcile after every meaningful Delivery, blocker, shared-contract change, or
new discovery.

| Classification     | Required action                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| `task_local`       | Revise or reopen only the affected Task Work.                                                   |
| `portfolio_change` | Update tasks, dependency edges, coverage, and decomposition status; keep the charter confirmed. |
| `charter_change`   | Set `charter_status: reopened`, stop affected execution, and request confirmation.              |
| `follow_up`        | Create or propose work outside the current acceptance boundary.                                 |
| `stop`             | Record evidence, stop unsafe work, and present recovery or abandonment choices.                 |

A new child task is not automatically scope expansion. It belongs inside the
milestone only when it is necessary to satisfy an already-confirmed acceptance
condition. A desirable improvement that changes the Outcome or adds a new
acceptance condition is follow-up or a charter change.

## 6. Integration Readiness Check

Read actual Deliveries and authoritative runtime/App/API state. For every
acceptance ID verify:

- accountable evidence exists and is readable;
- upstream outputs match downstream inputs;
- shared schemas, APIs, files, UI states, or operating procedures agree;
- required regression and failure-path checks pass;
- the real user-visible or system-visible journey works;
- residual work is either outside Scope or blocks readiness explicitly.

Set `integration_readiness_status: passed` only when all mandatory conditions
pass. Child task `done` states, local edits, isolated unit tests, or filenames are
inputs to this judgment, never substitutes for it.

## 7. Acceptance And Closure

Present a compact acceptance review:

- confirmed Outcome and whether it became true;
- each acceptance ID, result, and evidence;
- cross-task integration and regression result;
- planned versus actual Scope;
- residuals, deferred work, and recommended destination;
- proposed milestone completion summary.

Manual or subjective conditions require user acceptance. Milestone closure also
requires explicit user confirmation by default. A delegated grant may authorize
closure only when it names the exact milestone, exact action, current charter
version, acceptance boundary, and expiry, and no manual condition remains.

Use the App-owned milestone context archive/closure preview before writing. On
approval, persist the completion summary, move follow-ups, apply supported
closure, and read back milestone state. Set `acceptance_status: passed` and
`execution_state: completed` only after this readback.

## Collaboration Reporting

During long-running work, report only meaningful changes:

- a phase passed or reopened;
- a child task delivered evidence;
- a dependency became ready or blocked;
- the portfolio changed;
- user input or authorization is required;
- integration evidence passed or failed.

Do not narrate unchanged polling, repeat every deterministic command, or claim
the milestone is nearly done from task counts alone.
