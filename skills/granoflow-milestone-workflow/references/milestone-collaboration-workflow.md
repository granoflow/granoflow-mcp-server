# Milestone Collaboration Workflow

This workflow coordinates one confirmed milestone across an evolving set of
child tasks. It owns the portfolio, dependencies, handoffs, integration proof,
and milestone acceptance. It does not replace child Task Work.

## Phase Model

```text
Resolve milestone and controller
  -> draft and confirm charter
  -> decompose and run decomposition check
  -> execute through child Task Work
  -> reconcile and replan from live evidence
  -> prove integration readiness
  -> accept and close the milestone
```

Only one phase transition may be claimed at a time. A later phase never repairs
an invalid earlier state silently.

## 1. Resolve And Establish Ownership

Resolve exactly one project and one active milestone. Read the milestone, project
context, completion summary, linked tasks, controller candidate, Task Work and
Delivery references, and relevant context pack.

Use an existing controller Task when its responsibility is milestone
orchestration and closeout. Otherwise preview a new controller Task bound to the
milestone. Its description must state that it owns the Milestone Work attachment,
portfolio decisions, integration evidence, and final closure, but not child
implementation.

If the Local HTTP API is unavailable, keep any local draft explicitly unbound or
bound only from prior trusted readback. Do not claim attachment, context update,
task creation, authorization, or active status until App/API readback succeeds.

## 2. Charter Confirmation

Draft these stable fields before decomposing:

- one milestone Outcome;
- user-visible or system-visible acceptance conditions with stable IDs;
- Scope and necessary non-goals;
- authoritative current truth and constraints;
- required workstreams or capability areas;
- material milestone-level risks;
- default delegation and stop boundary.

Ask only questions that can change those fields. Show the current understanding,
recommendation, alternatives, impact, and requested decision together. Explicit
confirmation sets `charter_status: confirmed`.

Do not treat permission to discuss or decompose as execution authorization.

## 3. Decomposition Check

Build the smallest sufficient portfolio. Each child task must have one distinct
responsibility and contribute evidence to at least one milestone acceptance ID.

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
table look complete.

## 4. Portfolio Execution

### Persistent execution preflight

For work expected to continue beyond one Agent turn, establish all of these
before starting workers:

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
