# Milestone Work Document Template

Owned by `granoflow-milestone-coordination`. Use this template for one
milestone-level **coordination** contract and—when UI/software child tasks are
authored—the structured **`task_plan`** composition SoT.

**Not product SoT.** Product journeys, key-page inventory, acceptance, and
verification mandates live in **Project Work** (current). Task history and
hi-fi prototypes live in **Task Work**. This document **must not** rewrite
`R-*` statements or copy the full Project requirement ledger.

**Composition SoT (hard for UI portfolio):** before App task create for a
milestone that touches user-visible pages, persist machine-readable
`task_plan` per `milestone-task-plan-template.yaml` (refined screens, page
journeys, task summaries, split probes). `task_plan.status: passed` aligns
with `decomposition_status: passed`. Non-UI milestones may keep Milestone Work
thin (entity + Project coverage only) when no refined screens apply.

When used, it freezes the milestone Outcome boundary, Scope, and—after
`task_plan` pass—child-task responsibilities. It is not a large Task Work
document and must not duplicate child implementation plans. Milestone **entity**
creation remains `granoflow-milestone-workflow`; App task create remains
`granoflow-task-authoring` against a passed `task_plan`.

Until Granoflow exposes milestone attachments, store the complete document on one
controller Task bound to the milestone. Keep only a concise living summary and the
controller Task reference in the active milestone description.

## Phased Required Fields

Do not pretend every section is complete at charter confirmation. Fill by phase:

| Phase key                    | When it must be complete                                 | Typical sections                                                                                                                                                                                                                                                           |
| ---------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `charter_required`           | Before `charter_status: confirmed`                       | Reader Summary, Outcome, Acceptance, Requirement Coverage (owned ids), Scope/Non-goals, Current Truth (milestone-level only), Workstreams (coarse), Milestone Risks (cross-task), Integration Verification **skeleton**, one end-to-end example, Next Orchestration Action |
| `decompose_required`         | Before `decomposition_status: passed` / `task_plan.status: passed` | Decomposition Rules, structured **`task_plan`** (see `milestone-task-plan-template.yaml`), Task Portfolio table synced to `task_plan.tasks`, Dependency And Handoff Map; Integration Verification rows named to accountable tasks |
| `execute_preflight_required` | Before non-dry-run child execution or persistent workers | Parallel Execution, Delegation And Authorization Boundary, Persistent Execution Preflight, External Capability Matrix                                                                                                                                                      |

**Fill ownership for `execute_preflight_required`:**

- Child Task Work Analysis owns task-local write surfaces, dependencies, risks, and
  authorization _needs_.
- The milestone **coordinator** (controller Task / this Skill) aggregates those
  Analysis outputs into Milestone Work after Analysis material is available and
  before execution dispatch. Do not require every child Analysis to be confirmed
  before writing a first preflight; refresh on reconcile when write surfaces
  change.
- Do **not** invent a complete Parallel / External Capability matrix at charter
  time. Placeholders such as `pending_task_analysis` are allowed until preflight.
- Do **not** copy Parallel / External Capability tables into each child Task Work.

Frontend / UI milestones: keep Current Truth pointing at the confirmed project
Design Baseline (exact ids/SHA) and contract fidelity; do not upload a second
milestone design authority.

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

# Tracks which template phases are satisfied for the current work_version.

required_fields_phase: charter_required | decompose_required | execute_preflight_required
created_at: <local timestamp>
updated_at: <local timestamp>

> Scope notice: This is the milestone collaboration contract. Child Task Work documents own task-local Analysis, Planning, execution, verification, and Delivery.

<!-- charter_required -->

## Reader Summary

<Why this milestone exists, who or what benefits, and the overall change that should become true.>

## Milestone Outcome

<One coherent result, not a list of implementation tasks.>

## User-visible Acceptance

<Observable conditions that prove the combined result works and rule out false success. Include at least one concrete end-to-end example of why separately completed child tasks could still fail to deliver the milestone.>

## Requirement Coverage

Read the shared
'granoflow-agent-workflow/requirement-intake-and-traceability' contract. List
only the Project Work requirement ids this milestone owns or verifies; never
copy the complete product ledger.

| Requirement ID | Project Work source | Milestone contribution | Accountable Task | Acceptance IDs | Result  |
| -------------- | ------------------- | ---------------------- | ---------------- | -------------- | ------- |
| R-001          | <stable reference>  | <bounded outcome>      | <task id or TBD> | <ids>          | pending |

## Scope And Non-goals

<Fixed boundary, explicitly excluded outcomes, and what belongs in a later milestone.>

## Current Truth And Constraints

<Milestone-level inspected facts, authoritative surfaces (including confirmed Design Baseline ids/SHA when UI is in scope), material unknowns, and compatibility constraints. Deep module/code truth belongs in child Task Work Analysis.>

## Workstreams And Required Capabilities

<The minimal streams of responsibility needed to satisfy acceptance. Do not freeze child implementation detail here.>

## Milestone Risks

<Cross-task, integration, scope, compatibility, operational, or user-visible risks. Keep task-local risks in Task Work.>

## Integration Verification

| Acceptance ID | Accountable Task                    | Required Evidence | Integration Check | Result  |
| ------------- | ----------------------------------- | ----------------- | ----------------- | ------- |
| A1            | <task/controller or TBD at charter> | <evidence>        | <combined check>  | pending |

## Next Orchestration Action

<The next state transition currently allowed, its owner, and its evidence or stop condition.>

<!-- decompose_required -->

## Decomposition Rules

<When to create, split, merge, reorder, defer, cancel, or move a task to follow-up.>

## Task Plan (structured YAML — composition SoT)

Persist the machine-readable `task_plan` object from
`milestone-task-plan-template.yaml` on this Milestone Work (YAML attachment /
embedded block). Required before App `create_one` when the milestone has
user-visible pages.

- Start from Project Work **key pages** (`key_screen_refs`); refine into
  `refined_screens` + `page_journeys` (may add `milestone_discovered` screens).
- Every refined screen: completed `split_probe`; ≥1 `tasks[]` row listing it.
- Freeze responsibilities in `tasks[].responsibility` + `screen_ids`.
- `task_plan.status: passed` ⇔ `decomposition_status: passed` for UI
  portfolios. Changing ownership/split → `reopened` / `draft`; Task Analysis
  Must not silently reopen (`forbidden_without_milestone_task_plan_reopen`).
- Lint: `granoflow-agent-workflow/scripts/lint_task_screen_portfolio.py`.

## Task Portfolio

Human-readable mirror of `task_plan.tasks` (keep in sync after create):

| Task ID | local_key | Responsibility | screen_ids | Depends On | Acceptance Contribution | Current Evidence Reference |
| ------- | --------- | -------------- | ---------- | ---------- | ----------------------- | -------------------------- |
| <id>    | T1        | <one outcome>  | <S-*>      | <ids/none> | <acceptance ids>        | <live Task Work/Delivery>  |

## Dependency And Handoff Map

<For every material edge: upstream output, downstream input, authoritative surface, verification, and invalidation rule.>

<!-- execute_preflight_required: coordinator fills after child Analysis outputs; before non-dry-run execution -->

## Parallel Execution

<Read `granoflow-agent-workflow/parallel-task-execution`. Aggregate pairwise
conflict decisions from current child Task Work Analysis and live
repository/runtime facts. Record assessed revisions, parallel-safe batches,
serialized edges, exact reasons, and host capacity limits. Unknown material write
surfaces must serialize. Do not use `doing` as an AI lease. Until Analysis
outputs exist, status may be `pending_task_analysis`—never a fake complete matrix.>

## Delegation And Authorization Boundary

<Allowed repositories, actions, time/budget boundary, parallelism, user-only decisions, forbidden actions, and expiry. Record secret availability only, never values. Refine from child Analysis authorization needs at execute preflight.>

### Persistent Execution Preflight

- Runtime access: required=<full | other>; observed=<full | other>; evidence=<host evidence>
- Internal phase gates: <preauthorized in-scope gates or explicit exceptions>
- Authorization manifest: <private reference, schema/version, confirmation and expiry; never secret values>
- Worker routing: <host/user Skill reference or manual; public contract remains provider-neutral>

### External Capability Matrix

| Capability | Affected Task IDs | Disposition                                 | Credential Reference | Interaction Node |
| ---------- | ----------------- | ------------------------------------------- | -------------------- | ---------------- |
| <name>     | <ids>             | granted \| excluded \| interaction_required | <reference/none>     | <id/none>        |

## Replanning And Stop Conditions

<What remains task-local, what changes the portfolio, what reopens the charter, what becomes follow-up, and what stops the milestone. Include the no-progress threshold, required strategy change, interaction-wait transition, attempt-history bound, recovery fingerprint, and proof that other independent tasks continue.>
```

The initial charter draft may omit `decompose_required` and
`execute_preflight_required` bodies or mark them
`pending_decomposition` / `pending_task_analysis`. Add `Completion Summary` only
during final acceptance:

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
  requires confirmation again. Confirming charter does **not** require
  `execute_preflight_required` sections to be complete.
- `decomposition_status` says whether the current task portfolio / `task_plan`
  minimally and sufficiently covers the confirmed charter. For UI portfolios it
  tracks `task_plan.status`. It may return to `draft` / `reopened` after a
  portfolio or ownership/split change without necessarily reopening the
  charter.
- `required_fields_phase` is the highest phase whose required sections are
  currently satisfied for this `work_version`.
- `execution_state` is the contract's collaboration phase, not a replacement for
  the live Granoflow milestone or child-task status.
- `integration_readiness_status` covers combined behavior, handoffs, regression,
  and user-visible journeys. It cannot be derived only from child states.
- `acceptance_status` records the final milestone-level judgment. Use `partial`
  when evidence is incomplete; do not relabel partial completion as passed.
- The external capability matrix is exhaustive for the confirmed milestone at
  execute preflight. Missing rows block persistent execution;
  `interaction_required` is an explicit resumable state, not inferred consent or
  completion.

## Writing Rules

- Include at least one concrete end-to-end example showing the user-visible or
  system-visible result and why separately completed child tasks could still fail
  to deliver it (`charter_required`).
- Keep stable metadata keys in English and write prose in the user's language.
- Distinguish inspected fact, user-confirmed decision, inference, and unknown.
- Reference child tasks by stable ID and evidence contribution. Read live task
  state instead of maintaining status prose by hand.
- Use a dependency diagram only when it clarifies three or more material edges.
- Do not include file-by-file implementation instructions, shell commands,
  task-local reproduction steps, or copied child Execution Plans unless they are
  themselves the milestone-level integration surface.
- Do not maintain Parallel Execution or External Capability Matrix inside child
  Task Work; those remain milestone coordinator fields filled at
  `execute_preflight_required`.
