# Task Work Document Template

Use this as the only Task Work template for new Granoflow task work. It combines
confirmed Analysis and applicable Planning in one document family. Do not create
separate new Task Analysis or Task Plan files. A task may have at most two active
`document_type: task_work` attachments: one actual execution document and, only
when needed, one post-completion revision.

## Role: task history + task-local contract

Task Work is the **history and execution contract for one task**—Analysis,
Planning, gates, and writeback evidence for that unit of work. It is **not** the
project-wide latest product truth.

- Cross-task product, journey, acceptance, or verification-mandate changes must
  update **Project Work** (current) in the same discussion batch; keep
  `discussion_writeback` / traceability / Verification Plan here as history.
- Do not maintain a parallel “current product rules” section that disagrees with
  Project Work.

```markdown
# Task Work: <task title>

document_type: task_work
schema_version: 1
task_id: <task id>
work_version: <positive integer>
document_slot: execution | post_completion_revision
supersedes: null | <prior task_work attachment in the same slot>
profiles: [] | [learning] | [software_development] | [...future profiles]
domain: <optional domain such as visual_narrative>
task_mode: <optional domain mode such as comic | animation>

# UI change => required (never not_required). See task-work-document-workflow

# "UI Change Prototype Mandate". conditional only while Detection unresolved.

prototype_requirement: required | not_required | conditional
prototype_condition_result: required | not_required | unresolved | not_applicable
prototype_input_status: not_applicable | awaiting_reference | awaiting_visual_confirmation | ready | stale | blocked

# When required: include derivedFrom baseline prototype_id/version_id/package_sha256.

prototype_inputs: [] | [{"source_entity_type":"task|project","source_entity_id":"<id>","prototype_id":"<id>","version_id":"<id>","version_ordinal":1,"package_attachment_id":"<id>","package_sha256":"<64 lowercase hex>","visually_confirmed":true,"derived_from_prototype_id":"<baseline id|null>","derived_from_version_id":"<id|null>","derived_from_package_sha256":"<64 hex|null>","intended_use":"<purpose>"}]

# Interactive: mainstream-reference-first candidate pool (≥5; brainstorm

# backfill only when mainstream < 5), then promote dual page expressions

# (expr_a + expr_b) with functional parity inside locked Design System;

# mix-and-match per task/page; optional third only for documented

# industry-peer deadlock. Unattended: same protocol then single expr_a.

# Never reopen Design Spec (delta_match / ai_challenger / spec_match) as task

# option ids after Baseline lock.

# Craft Gate must pass before visualConfirmed. See project-artifact-workflows

# "Task Prototype Craft Gate And Option Set" and

# prototype-expression-brainstorm.md. Lint:

# scripts/lint_prototype_expression_brainstorm.py

prototype_option_set:
mode: interactive_dual | interactive_dual_plus_industry_third | unattended_single
design_system_locked: null # confirmed Spec/Baseline option id (required when dual)
expression_brainstorm: null # { status, layer, source_strategy: mainstream_first, scope_mode: same_category|capability_match, scope_mode_rationale, mainstream_references[], brainstorm_backfill[], brainstorm_backfill_reason, candidate_count, promote_count, candidates[], selected, selection_rationale, parity_check, loaded_reference_sha256 }
options: [] # [{ id: expr_a|expr_b|industry_peer_c, contrast_axes: [], rationale: null|string }]
contrast_axes: [] # ≥2 from whitelist when interactive dual/triple
third_option_rationale: null # required when industry_peer_c present
selected_option_id: null # per-task; milestones may mix picks across tasks
craft_checklist:
intent_recorded: false
fidelity_ok: false
real_domain_copy: false
required_states_covered: false
enhancement_notes_ok: false
user_visible_copy_boundary_ok: false # must be true before visualConfirmed; see user-visible-copy-boundary.md
expression_brainstorm_ok: false # must be true before dual visualConfirmed; lint_prototype_expression_brainstorm.py + prototype-expression-brainstorm.md
baseline_fit_ok: false # must be true before visualConfirmed; see prototype-baseline-fit.md
confirmed_chrome_lock_ok: false # true|not_applicable; see prototype-confirmed-chrome-lock.md when siblings are visualConfirmed
craft_status: incomplete | ready # incomplete => task_prototype_craft_incomplete

# When chrome_lock.status=applicable, list confirmed sibling package SHAs.

chrome_lock: null # { status: applicable|not_applicable, family_id, authorities: [], vocabulary: [] }

# After any user-accepted discussion change: write App slots + readback.

# See discussion-writeback-contract + change-impact-fanout +

# prototype-product-truth-writeback (when ui_prototype changes).

# pending/failed/open blocks Plan/Readiness/Execution.

discussion_writeback: [] # [{ at, decision_summary, slots_updated, prototype_id, version_id, package_sha256, content_sha256, superseded, change_impact_status, status: written_and_read_back|pending|failed }]
change_impact: [] # [{ at, decision_summary, decision_class, product_truth_writeback_loaded, contract_loaded, scan_terms, scopes_checked, candidates, status: open|closed|failed }]; lint with lint_change_impact_fanout.py
change_impact_ok: false # must be true before closing a material discussion batch; see change-impact-fanout.md
locked_product_contracts: [] # [{ id, must, source_doc, source_section }]; required when decision_class=product_truth_changing

# Software edits: hard gate from software-structural-budget.md. Non-software

# tasks use not_applicable. Editing code while present_in_plan/missing fails

# closed as structural_forecast_not_shown.

structural_forecast_status: not_applicable | missing | present_in_plan | notice_emitted | reconciled
structural_forecast_notice_emitted_at: null | <ISO-8601 timestamp after user-visible notice>

# Task Integration Test Policy (campaign runs at stage 6). Judge unit tests

# first; add at most 2 integration tests only when insufficient; do not execute

# them inside the feature task. When adding IT, recommend requires/produces.

# Device: recommend local_machine; user confirms or chooses another target.

# Project context Hard Gate: project_snapshot.yaml + project_rules.yaml.

# See project-context-attachments.md. Edits while missing/conflict_pending fail

# closed.

project_context_check_status: not_applicable | missing | checked_no_conflict | conflict_pending | conflict_resolved
project_context_conflict: none | present
project_context_resolution: not_applicable | revise_code | revise_context_yaml | user_confirmed_revise_code | user_confirmed_revise_context_yaml
project_context_decision_emitted: false | true

# copy_change_only: true => no unit/integration/other automated tests

# (copy_change_tests_forbidden). See user-visible-copy-boundary.md.

copy_change_only: false | true

# Prototype → Document Coverage (Analysis / rematch). See prototype-doc-coverage.md.

# Lint: scripts/lint_prototype_doc_coverage.py --kind coverage

prototype_doc_coverage: null | { schema, contract_loaded, prototype_id, version_id, status: not_applicable|pending|complete, rows: [] }

# HTML prototype surface inventory (every task-owned UI surface). Lint: --kind html_coverage

prototype_html_coverage: null | { schema, contract_loaded, prototype_id, version_id, status: not_applicable|pending|complete, surfaces: [] }

# Widget reuse vs project widgets.yaml. Lint: --kind widget_reuse [--widgets path]

prototype_widget_reuse: null | { schema, contract_loaded, catalog_sha256, status: not_applicable|pending|complete, declarations: [] }

# Plan-time prototype vs Task Work truth. Lint: --kind plan_truth

prototype_plan_truth: null | { schema, contract_loaded, prototype_is_source_of_truth: true, status: not_applicable|aligned|conflict, conflicts: [], user_notified, user_resolution, task_work_updated, project_work_updated }

# Prototype Implementation Fidelity (UI tasks). Phase A BEFORE unit tests.

# method must be code_review_guess (code vs prototype; never screenshot/vision).

# questions required when matched or diverged. See prototype-implementation-fidelity.md.

# Lint: scripts/lint_prototype_implementation_fidelity.py

prototype_impl_compare: null | { status: not_applicable|matched|diverged, method: code_review_guess, declaration_emitted: true|false, questions: {ux_better, visual_better, tech_stack_blocked}, decision: keep_implementation|revise_to_prototype|not_applicable, decision_rationale: string, diffs: [] }

unit_test_sufficiency: not_applicable | unassessed | sufficient | insufficient
integration_test_requirement: not_applicable | not_required | required
integration_tests_added_count: 0 | 1 | 2
integration_test_execution: not_applicable | not_run_manual_only | awaiting_campaign_execution | executed_forbidden
integration_test_device_recommendation: not_applicable | local_machine
integration_test_device: not_applicable | unselected | local_machine | simulator_or_emulator | physical_device | remote_farm | other

# Project Work engineering.quality_gates.integration_test_special_requirements

# (see integration-test-special-requirements.md). Required when adding IT.

integration_test_special_requirements_checked: not_applicable | unchecked | checked_none | applied | ignored_forbidden
integration_test_special_requirements_applied: [] # ITR-* ids applied in authored tests

# When editing entitlements / CODE_SIGN_* / keystore / provisioning, declare

# code_signing_strategy (see code-signing-strategy.md). Never ask the user to

# confirm. Lint: scripts/lint_code_signing_strategy.py --require-strategy

# code_signing_strategy: null | { schema, goal, platform, selected, evidence, alternatives_rejected, user_confirmation: not_required, declared_at }

# Recommended orchestration hints for stage-6 campaign (not a runtime claim):

# integration_tests_orchestration_hints:

# - path: <file>

# requires: []

# produces: []

# mutates: []

# destroys: []

analysis_status: draft | awaiting_confirmation | confirmed
analysis_grill_status: not_run | passed | revisions_required | blocked
decision: proceed | needs_input | user_action | split | redefine | defer | abandon | completion_audit
planning_status: not_assessed | not_required | draft | awaiting_confirmation | confirmed

# Software code edits: Hard Gate from plan-design-gate.md. Non-software or

# Analysis-only with no code edit → not_applicable.

plan_design_gate_status: not_applicable | pending | passed
plan_design_diagrams: []
data_disposition: not_applicable | unchanged | extend | breaking

# When Plan invents/changes user-visible copy (see milestone-plan-acceptance-pack):

# plan_copy_locale: zh-Hans

# plan_copy_locale_source: user_explicit | conversation_language

readiness_grill_status: not_run | not_applicable | passed | revisions_required | blocked
execution_authorization: not_requested | awaiting_confirmation | direct_confirmed | delegated_confirmed | denied
execution_actor: ai | human | shared | not_assessed
execution_status_projection: pending_until_completion | human_focus_doing | not_assessed
skill_routing: not_triggered | completed | declined | fallback | failed
card_checkpoint: not_triggered | completed | partial | deferred | conflict | verification_failed
created_at: <local timestamp>
updated_at: <local timestamp>

> Scope notice: This is a pre-execution governance document. It records confirmed Analysis and applicable Planning, not execution progress or actual Delivery.

When `execution_authorization: delegated_confirmed`, include an authorization
receipt with `envelopeId`, `authorizationOwnerTaskId`, `attachmentId`,
`attachmentSha256`, evaluated phase, Plan hash, `receiptVerified=true`, decision,
reason code, and evaluated scope. Do not copy the full envelope into every target
Task Work. Only the controller Task owns the envelope body.

## Reader Summary

<In plain language: the concrete problem or event, affected person/system, and intended result.>

<!-- Include at least one concrete real or plausible example: what happens,
who/what is affected, and why it matters. If the approach has a material
choice or boundary, explain it with a concrete example in the relevant section. -->

## Outcome

## Evidence

## Scope

## Risk

## Next Action
```

This fenced example is the complete shape of an initial draft. The initial
draft is Analysis-only: it must keep `planning_status: not_assessed`,
`analysis_grill_status: not_run`, and `readiness_grill_status: not_run`; it must
not contain `Recommended Approach`, `Execution Plan`, `Execution Nodes`,
`Verification Plan`, `Rollback / Stop Conditions`, or an execution-readiness
claim. Planning content is added only after the Analysis is fully resolved,
explicitly confirmed, and the MCP-bundled Analysis Grill has passed.

Keep machine-stable metadata keys in English. Write the body headings and prose
in the user's language; a host may localize `Reader Summary`, `Outcome`,
`Evidence`, `Scope`, `Risk`, and `Next Action` while preserving their semantics.
Explain necessary professional terms in plain language on first use.

Prototype inputs are exact execution references, never filename/current/latest
hints. `not_required` requires `prototype_condition_result: not_applicable`,
`prototype_input_status: not_applicable`, and an empty list. `required` requires
at least one complete exact reference, visual confirmation, and `ready` before
Readiness can pass. An unresolved `conditional` requirement fails closed.

The persisted Granoflow task description has a separate mandatory five-
dimension prose contract: problem, proposed solution, prerequisites and
readiness, focused-work estimate with basis and uncertainty, and acceptance
condition. Write these dimensions as fluent task copy, never as the five
question headings. For completed historical tasks, use `历史工时未知` when no
reliable focused-work record exists. Optional rationale, theory, or prior
experience belongs in the prose only when it materially improves a decision.
The problem must include a concrete observed failure, user-visible consequence,
or plausible risk scenario; references to documents or existing implementation
are supporting evidence only and cannot replace the scenario. The solution must
describe the intended behavior change, and acceptance must identify evidence
that would show the original failure is resolved.
Every task description and every attached Task Work Document must include at
least one concrete example of the real or plausible case being handled. The
example must identify what happens, who or what is affected, and why it matters;
for example, “一个只看到内部架构术语的接手人无法判断请求何时被截断，也无法
据此验收修复” is a valid example, while “完善流程” is not. When the chosen
solution has a meaningful alternative, trade-off, or boundary, include one or
more examples explaining why this approach is reasonable and why the work stops
at this boundary. Do not add rationale merely to satisfy a quota when no such
choice exists.
Write each problem as a separate natural-language paragraph with a blank line;
use a Markdown table, flowchart, or Mermaid diagram only as optional supporting
structure when a linear paragraph would hide important relationships.
Use Markdown semantically: **bold** decisive claims and acceptance results,
_italicize_ constraints and uncertainty, and use inline code or fenced code
blocks for literal commands, APIs, fields, paths, configuration, logs, and code.
Use headings, lists, tables, blockquotes, or Mermaid only when they improve
navigation or evidence review; do not use formatting as decoration or as a
substitute for prose.
There is no formatting quota. Plain paragraphs are valid when they are the
clearest form; Markdown cannot make generic or unverified content acceptable.
This rule applies to the complete attached Task Work Document, including its
Analysis, Planning, Verification, Evidence, Acceptance, Risk, and Handoff
sections. An attachment that contains the required facts but ignores this
semantic Markdown standard is not a finished document; revise it before
uploading or marking it active.
The Work Document may provide the detailed, confirmed analysis and plan; it does
not replace the task-description contract.

For Task Work specifically, the example must be usable by a cold-start reader:
it should make the failure, risk, or expected result concrete enough to guide
reproduction or inspection. A generic statement such as “处理超时问题” is not
enough; a useful example names the observable situation, such as a request that
is cut off by a fixed limit before the configured operation can finish. If the
plan chooses one implementation or acceptance path over a meaningful
alternative, record a concrete example showing why the chosen path is safer,
clearer, or better aligned with the task boundary. Do not fabricate an example;
use `待确认` or an explicit unknown when the source evidence is insufficient.

Treat the task description as the document's factual seed, not as disposable
input. Preserve its confirmed problem, consequence, outcome, and boundary while
expanding them into executable detail. A document that merely repeats a title,
filename, path, or completion label is not an analysis; a document that adds
unverified implementation facts is invalid.

The five core sections are always present and contain task-specific substance:

- `Outcome`: what becomes true when the task succeeds;
- `Evidence`: what rules out false success;
- `Scope`: a semantic minimum-change budget containing required changes,
  allowed touchpoints, protected surfaces, and the minimum necessary non-goals;
- `Risk`: the material risk, or one evidence-backed low-risk sentence;
- `Next Action`: the state-level next step currently allowed.

`Reader Summary` precedes the five core sections and carries only the minimum
facts a cold reader needs to understand the job. It is not a copy of the task
description and must not repeat all implementation detail.

## Facts And Source Discipline

Task Work uses this source order:

1. user-confirmed task description and current-thread decisions;
2. directly inspected source files, screenshots, logs, or runtime state;
3. confirmed prior Analysis, Plan, Delivery, decisions, and project context;
4. clearly labeled inference;
5. explicit unknown.

Material claims must be traceable to one of the first three sources or labeled
as inference/unknown. A path or document name is provenance, not proof of what
the document contains. Never turn an inference into a confirmed fact merely to
complete the template.

When the task implements or verifies user requirements, read
'requirement-intake-and-traceability.md' and add:

```markdown
## Requirement Traceability

| Requirement ID | Source reference | Task-local interpretation | Disposition | Acceptance / Evidence |
| -------------- | ---------------- | ------------------------- | ----------- | --------------------- |
| R-001          | <stable source>  | <what this task owns>     | adopted     | <ids/evidence>        |
```

Reference the Project Work canonical requirement ids. Do not copy the complete
project ledger into Task Work. Preserve extra requirements, keep inference
labeled, and stop before silently resolving a decision-changing source conflict.

Do not add empty optional headings or repeated `none` sections. Add an optional
section only when its trigger in `task-work-document-workflow.md` fires. When
triggered, use these stable headings:

- `Trigger / Reproduction`
- `Context / Unknowns`
- `Alternatives / Decision`
- `Capability And Skill Routing`
- `Profile Additions`
- `Database / Migration`
- `UI / Manual Acceptance`
- `API / Compatibility / Release`
- `Authorization Matrix`
- `Recommended Approach`
- `Structural Change Forecast`
- `Skill Execution Strategy`
- `Execution Nodes`
- `Dependencies And Handoffs`
- `Write Surfaces And Parallel Safety`
- `Verification Plan`
- `Rollback / Stop Conditions`
- `Knowledge / Card Checkpoint`
- `Granoflow References`
- `Requirement Traceability`
- `Visual Narrative Mode`

Grill headings are forbidden in the rendered Task Work Document. Do not add
`Grill Review`, `Analysis Grill`, `Execution Readiness Grill`, reviewer
findings, or a review ledger. Grill findings must revise the relevant existing
section without leaving process commentary. Preserve only the phase result in
`analysis_grill_status` and `readiness_grill_status`.

Profiles are omission checks, not mandatory rendered sections. Put a triggered
Profile requirement into the most relevant core or optional section. Do not
copy the Profile or an external Skill's method into this document.

For visual-narrative tasks, use `domain: visual_narrative` and load
`visual-narrative-task-work.md`. Use `task_mode: comic` for static work and
`task_mode: animation` only when the user explicitly requests a temporal
extension. These are domain fields, not generic Granoflow profiles.

When `Capability And Skill Routing` is triggered, follow
`external-skill-routing.md` and record only relevant Skills, phase, invocation
mode, necessity, missing behavior, authorization effect, availability,
decision, fallback, and evidence. When it is not triggered,
the compact `skill_routing: not_triggered` metadata is sufficient.

Use the shared routing enums, including `decision: install_offered` and
`result: pending_user_decision`, only for a true `required_capability`. A pending
required-capability decision remains waiting across resume; it is not a
refusal, failure, or fallback. A `preferred_method` or `explicit_only` Skill
must instead use `native_fallback` or `skip_nonblocking` and must not put an
unattended task into waiting.

When card work is triggered, use the canonical lifecycle Card Checkpoint. When
it is not triggered, the compact `card_checkpoint: not_triggered` metadata is
sufficient and the card reference need not be loaded.

When task analysis actually adopts Evidence, Experience, or Knowledge, render
`Granoflow References` as a compact list of App-owned internal links plus one
sentence explaining how each source changes this task. Omit considered,
rejected, stale, and unused results. Rebuild this section from structured
references after every full rewrite; never preserve it by copying old prose.

Planning sections appear only after confirmed Analysis,
`analysis_grill_status: passed`, and explicit permission to enter Planning.
When this task may run beside another task, add `Write Surfaces And Parallel
Safety` with bounded read inputs, exact or responsibly bounded write surfaces,
shared mutable state, external effects, dependencies, and unknowns. This is the
task-local evidence consumed by `parallel-task-execution.md`; it does not decide
portfolio compatibility by itself. AI execution uses `execution_actor: ai` and
`execution_status_projection: pending_until_completion`. Human manual focus
uses `human_focus_doing`.
When `planning_status=confirmed`, include an `Execution Plan` that a cold reader
can follow without the original thread. Each ordinary plan step records:

```markdown
### Step N: <plain-language action + result>

- Performer: agent | user | agent_then_user | shared
- Purpose: <why this step exists>
- Inputs: <materials, files, accounts, people, or prior outputs>
- Action: <direct instructions; commands or interaction steps when relevant>
- Output: <artifact, decision, state change, or prepared material>
- Verification: <low-cost deterministic evidence>
- Stop / Handoff: <when to stop, ask, or pass work onward>
- Expected focused time: <range and basis, or explicit unknown>
```

For software work, every step's `Purpose` must map the action to a confirmed
Outcome or Evidence item. Its `Action` must stay inside the allowed touchpoints,
and `Stop / Handoff` must stop before changing a protected surface. A file or
line-count budget may support review, but it never replaces this semantic
mapping.

when software Planning is required—or `planning_status: not_required` but the
task will still edit code—render the Plan Design Gate package from
`plan-design-gate.md` inside `Recommended Approach` (and related optional
sections): **Markdown verification test cases** traced to Analysis; operation
flowchart; explicit `data_disposition` with basis; task-local external libraries
and concrete capabilities; UI↔data binding when the task has UI. Set
`plan_design_gate_status: pending` while drafting; set `passed` only when the
Gate is complete and confirmed under the interaction contract. Readiness must
not pass while the status is `pending` or the package is incomplete
(`plan_design_gate_missing` / `plan_design_gate_incomplete` /
`plan_test_cases_missing`). Do not leave Execution Plan Actions as hollow
"implement Outcome" steps that omit references to that package.

When software Planning is required—or `planning_status: not_required` but the
task will still edit code—also render `Structural Change Forecast` using
`software-structural-budget.md`. The forecast names expected files and symbols,
current responsibilities and sizes when available, projected change, applicable
limits and sources, split seams, protected surfaces, and why the proposal is the
smallest complete iteration. Vague "related modules" wording without paths fails
the Plan Design Gate even if a Forecast heading exists. Set
`structural_forecast_status: present_in_plan` when the section is complete.
Readiness must not pass while the status remains `missing`. Before the first
edit, show the forecast as a non-confirming notice, then set `notice_emitted` +
timestamp; Delivery requires `reconciled`.

Adapt the `Action` to the performer. An AI-oriented step names files, APIs,
commands, data boundaries, and observable output. A user-oriented step uses
plain instructions, required materials, timing, people, and what to record—for
example, preparation, agenda, questions, notes, and follow-up for a client
visit. Do not force software terminology onto a human task.

Execution steps remain in the attachment and do not automatically become
Granoflow nodes. Create a node only for a high-cost, error-prone, subjective, or
user-selectable intervention/validation gate. Each such optional node records:

```markdown
### Node N: <action + result>

- Preconditions:
- Execution Mode: agent | user_action | agent_then_user_acceptance
- Action:
- Deliverable:
- Delivery Standard:
- Completion Condition:
- Verification Evidence:
- Acceptance: automated | ai_review | user_manual
- Manual acceptance instructions: none | <entry, steps, pass criteria>
- Optional validation node: none | <only when AI/manual validation is costly, error-prone, subjective, or user-selectable>
- Validation node mode/cost/evidence: none | <human | AI | hybrid>; <expected cost>; <required evidence>
- Downstream Startup Requirements:
- Handoff Decision:
- Stop Conditions:
- Knowledge/Card Delta Trigger: none | <trigger>
```

`Execution Mode` describes performance, not ownership. The task always belongs
to the current individual user. The Agent is an execution tool, not the task
owner. Runtime execution status belongs to the latest
task, Granoflow nodes, and the managed summary; this immutable document never
contains `execution_status`.

## Mandatory Two-Stage Grill Integration

The MCP-bundled Grill is a required phase gate, not an optional external Skill.
After Analysis is complete and user-confirmed, run the Analysis Grill over the
checked assumptions, unresolved decision-changing questions, false-success
paths, internal consistency, and—when DB / JSON contracts / shared constants
or capability-critical libraries are in scope—whether an unreasonable project
data attachment or dependency selection was raised with a concrete revision
instead of inherited silently. Apply each finding directly to Outcome,
Evidence, Scope, Risk, Decision, Next Action, Database / Migration, or another
relevant Analysis section. Do not add a Grill heading, findings appendix,
reviewer ledger, or before/after commentary. Planning cannot begin unless the
result is `passed`.

After the Plan discussion is complete and the Plan is user-confirmed as
executable, notify the user that readiness review is starting and that a passing
document will be uploaded but will still require either a separate execution
command or a separately valid delegated `executionAuthorization` grant.
Then run the Execution Readiness Grill, covering at least:

- whether the steps are sufficient to complete the stated Outcome;
- whether prerequisites and upstream outputs are actually ready;
- whether required authorization has been granted for the planned actions;
- whether required accounts, login state, credentials, keys, and secrets are
  available at execution time, recording only presence/readiness and never a
  secret value;
- whether required data, source files, materials, people, and environment are
  available and current;
- whether verification, rollback, stop, and handoff conditions are actionable;
- for software edits: whether the Plan Design Gate is complete and
  `plan_design_gate_status: passed`, including a Markdown verification test
  case table traced to Analysis (else `plan_design_gate_missing` /
  `plan_design_gate_incomplete` / `plan_test_cases_missing`);
- for software edits: whether `Structural Change Forecast` is complete and
  `structural_forecast_status: present_in_plan` (else
  `structural_forecast_missing`); and
- which missing item blocks upload or execution.

Integrate every finding into the relevant Execution Plan, Dependencies And
Handoffs, Authorization Matrix, Verification Plan, or Rollback / Stop
Conditions. The final Task Work body must contain the corrected contract, not a
record of how the Grill corrected it.

After either bundled Grill reaches its phase result, perform a complete clean
rewrite into a new versioned local file. Rebuild the whole document from
confirmed facts and accepted findings; rewrite transitions, remove repetition,
drop stale questions and superseded alternatives, and leave no patch or review
residue. Increment `work_version`, preserve `document_slot` and lineage, update
`updated_at`, and validate the new file before deleting the prior local file.
If the replacement cannot be created or validated, retain the prior file and
return `post_grill_rewrite_failed`.

Only the validated rewritten file and its hash are eligible for attachment
upload. A pre-Grill draft, patch artifact, or findings appendix returns
`post_grill_rewrite_required`. After successful local validation, delete the
old local document; do not keep it beside the replacement as another draft.
App attachment replacement remains transactional and happens only through
upload plus content/hash readback.

Set `readiness_grill_status: passed` only when no execution-blocking unknown is
left. For UI-changing tasks, also require `prototype_requirement: required`,
`prototype_input_status: ready`, and a visually confirmed `ui_prototype`
readback (`derivedFrom` the project Design Baseline when one exists). Otherwise
keep Readiness `blocked` / `ui_prototype_required`. For software tasks that will
edit code, also require a complete `Structural Change Forecast` and
`structural_forecast_status: present_in_plan`; otherwise keep Readiness
`blocked` / `structural_forecast_missing`. Also require the Plan to name the
project-context check against `project_snapshot.yaml` /
`project_rules.yaml` (Hard Gate in `project-context-attachments.md`); execution
later fails as `project_context_check_missing` if that check never ran. For
tasks that will change DB schema, JSON contracts, or shared constants, the Plan
must name the project attachment
file(s) to update; Delivery later fails as `data_artifact_stale` if those
attachments were not updated and read back. A finding that changes Outcome,
Evidence, Scope, Risk, or Decision reopens Analysis and its Grill. A material
Plan change repeats Plan confirmation and the Readiness Grill.
`revisions_required` loops within authoring; `blocked` records the missing
prerequisite without pretending the document is executable.

## Task Work Slot And Revision Rules

Task Work uses two fixed logical slots, not an unlimited attachment history:

| Slot                       | When it exists                                                                                                                        | Update rule                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `execution`                | Always for new Task Work; before completion it is the current execution basis, and after completion it is the actual execution record | While the task is unfinished, every approved change replaces this slot's content and active pointer. Do not create another Task Work attachment for each edit. |
| `post_completion_revision` | Only after a completed task needs its first later correction, clarification, or historical amendment                                  | Create it once from the completed execution record. Every later change replaces this same slot; do not create another post-completion Task Work attachment.    |

The App may store immutable attachment records internally, but the workflow must
keep only the current attachment in each slot active and visible as Task Work.
After replacement content passes quality and hash readback, remove or archive
the superseded attachment according to the supported App operation. A failed
replacement must leave the previous active document intact. A task with more
than two active Task Work attachments fails closed with
`task_work_slot_count_exceeded`.

Use versioned local names while keeping the logical slot stable:

- `task-work-<task-id>-execution-v<work_version>.md`
- `task-work-<task-id>-post-completion-revision-v<work_version>.md`

The `work_version` field increases for every successful post-Grill clean
rewrite, but it does not create a new active slot. After local validation, only
the newest local version remains. The active summary must identify
`document_slot` and the current attachment id.

## Completed Historical Task Branch

When `decision=completion_audit`, the document reconstructs what actually
happened. Replace prospective `Execution Plan` content with:

- `Original Problem Or Event`;
- `Actual Actions`;
- `Actual Evidence`;
- `Outcome And Differences`;
- `Residuals / Unknowns`; and
- `Reusable Next Entry Point`, only when one exists.

Do not invent a future plan, retroactive prerequisites, or estimated execution
steps for completed work. If source evidence is missing, state exactly what
cannot be recovered and do not mark the audit complete.

If a completed task later needs correction, copy the confirmed actual execution
record into `document_slot: post_completion_revision` and describe the change,
reason, new evidence, and remaining uncertainty. Subsequent corrections update
that same post-completion slot. Never create a new prospective execution slot
for a historical correction.

## Cold-Handoff Completion Gate

Before upload or activation, give the document to a hypothetical reader who has
not seen the thread. It fails unless that reader can determine:

- the concrete problem or event and the intended/actual result;
- which statements are facts, inferences, and unknowns;
- who performs each applicable step;
- the inputs, actions, outputs, verification, and stop/handoff conditions; and
- which validation is routine versus an optional costly node.

A document that could be reused unchanged for another task, merely restates the
title/description, or tells the reader to “review related materials” without
naming the required material and decision fails this gate and must not become
the active attachment.
