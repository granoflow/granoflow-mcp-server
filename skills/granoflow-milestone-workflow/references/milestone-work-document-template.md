# Milestone Work Document Template

Use this template for one milestone-level collaboration contract. It freezes the
confirmed Outcome, acceptance boundary, Scope, and non-goals while allowing the
child-task portfolio to evolve. It is not a large Task Work document and must not
duplicate child implementation plans.

Until Granoflow exposes milestone attachments, store the complete document on one
controller Task bound to the milestone. Keep only a concise living summary and the
controller Task reference in the active milestone description.

```markdown
# Milestone Work: <milestone title>

document_type: milestone_work
schema_version: 1
project_id: <project id>
milestone_id: <milestone id>
controller_task_id: <controller task id>
work_version: <positive integer>
supersedes: null | <prior milestone_work attachment>
charter_status: draft | awaiting_confirmation | confirmed | reopened
decomposition_status: not_started | draft | passed | revisions_required | blocked
execution_state: not_started | active | waiting | integration_review | stopped | completed
integration_readiness_status: not_run | passed | revisions_required | blocked
acceptance_status: not_run | partial | passed | failed | blocked
execution_authorization: not_requested | awaiting_confirmation | direct_confirmed | delegated_confirmed | denied
created_at: <local timestamp>
updated_at: <local timestamp>

> Scope notice: This is the milestone collaboration contract. Child Task Work documents own task-local Analysis, Planning, execution, verification, and Delivery.

## Reader Summary

<Why this milestone exists, who or what benefits, and the overall change that should become true.>

## Milestone Outcome

<One coherent result, not a list of implementation tasks.>

## User-visible Acceptance

<Observable conditions that prove the combined result works and rule out false success.>

## Scope And Non-goals

<Fixed boundary, explicitly excluded outcomes, and what belongs in a later milestone.>

## Current Truth And Constraints

<Inspected facts, authoritative surfaces, material unknowns, compatibility constraints, and available inputs.>

## Workstreams And Required Capabilities

<The minimal streams of responsibility needed to satisfy acceptance. Do not freeze child implementation detail here.>

## Decomposition Rules

<When to create, split, merge, reorder, defer, cancel, or move a task to follow-up.>

## Task Portfolio

| Task ID | Responsibility | Depends On | Acceptance Contribution | Current Evidence Reference |
| ------- | -------------- | ---------- | ----------------------- | -------------------------- |
| <id>    | <one outcome>  | <ids/none> | <acceptance ids>        | <live Task Work/Delivery>  |

## Dependency And Handoff Map

<For every material edge: upstream output, downstream input, authoritative surface, verification, and invalidation rule.>

## Delegation And Authorization Boundary

<Allowed repositories, actions, time/budget boundary, parallelism, user-only decisions, forbidden actions, and expiry. Record secret availability only, never values.>

### Persistent Execution Preflight

- Runtime access: required=<full | other>; observed=<full | other>; evidence=<host evidence>
- Internal phase gates: <preauthorized in-scope gates or explicit exceptions>
- Authorization manifest: <private reference, schema/version, confirmation and expiry; never secret values>
- Worker routing: <host/user Skill reference or manual; public contract remains provider-neutral>

### External Capability Matrix

| Capability | Affected Task IDs | Disposition                                 | Credential Reference | Interaction Node |
| ---------- | ----------------- | ------------------------------------------- | -------------------- | ---------------- |
| <name>     | <ids>             | granted \| excluded \| interaction_required | <reference/none>     | <id/none>        |

## Milestone Risks

<Cross-task, integration, scope, compatibility, operational, or user-visible risks. Keep task-local risks in Task Work.>

## Integration Verification

| Acceptance ID | Accountable Task  | Required Evidence | Integration Check | Result  |
| ------------- | ----------------- | ----------------- | ----------------- | ------- |
| A1            | <task/controller> | <evidence>        | <combined check>  | pending |

## Replanning And Stop Conditions

<What remains task-local, what changes the portfolio, what reopens the charter, what becomes follow-up, and what stops the milestone. Include the no-progress threshold, required strategy change, interaction-wait transition, attempt-history bound, recovery fingerprint, and proof that other independent tasks continue.>

## Next Orchestration Action

<The next state transition currently allowed, its owner, and its evidence or stop condition.>
```

The initial draft ends there. Add `Completion Summary` only during final
acceptance:

```markdown
## Completion Summary

- Outcome achieved:
- Acceptance evidence:
- Scope differences:
- Residuals and follow-ups:
- Final App/API readback:
```

## Field Semantics

- `charter_status` covers Outcome, acceptance, Scope, non-goals, ownership, and
  material milestone risk. A material change to any of them sets `reopened` and
  requires confirmation again.
- `decomposition_status` says whether the current task portfolio minimally and
  sufficiently covers the confirmed charter. It may return to `draft` after a
  portfolio change without reopening the charter.
- `execution_state` is the contract's collaboration phase, not a replacement for
  the live Granoflow milestone or child-task status.
- `integration_readiness_status` covers combined behavior, handoffs, regression,
  and user-visible journeys. It cannot be derived only from child states.
- `acceptance_status` records the final milestone-level judgment. Use `partial`
  when evidence is incomplete; do not relabel partial completion as passed.
- The external capability matrix is exhaustive for the confirmed milestone.
  Missing rows block persistent execution; `interaction_required` is an explicit
  resumable state, not inferred consent or completion.

## Writing Rules

- Include at least one concrete end-to-end example showing the user-visible or
  system-visible result and why separately completed child tasks could still fail
  to deliver it.
- Keep stable metadata keys in English and write prose in the user's language.
- Distinguish inspected fact, user-confirmed decision, inference, and unknown.
- Reference child tasks by stable ID and evidence contribution. Read live task
  state instead of maintaining status prose by hand.
- Use a dependency diagram only when it clarifies three or more material edges.
- Do not include file-by-file implementation instructions, shell commands,
  task-local reproduction steps, or copied child Execution Plans unless they are
  themselves the milestone-level integration surface.
