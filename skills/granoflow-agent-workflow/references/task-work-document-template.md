# Task Work Document Template

Use this as the only Task Work template for new Granoflow task work. It combines
confirmed Analysis and applicable Planning in one document family. Do not create
separate new Task Analysis or Task Plan files. A task may have at most two active
`document_type: task_work` attachments: one actual execution document and, only
when needed, one post-completion revision.

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
analysis_status: draft | awaiting_confirmation | confirmed
analysis_grill_status: not_run | passed | revisions_required | blocked
decision: proceed | needs_input | user_action | split | redefine | defer | abandon | completion_audit
planning_status: not_assessed | not_required | draft | awaiting_confirmation | confirmed
readiness_grill_status: not_run | not_applicable | passed | revisions_required | blocked
skill_routing: not_triggered | completed | declined | fallback | failed
card_checkpoint: not_triggered | completed | partial | deferred | conflict | verification_failed
created_at: <local timestamp>
updated_at: <local timestamp>

> Scope notice: This is a pre-execution governance document. It records confirmed Analysis and applicable Planning, not execution progress or actual Delivery.

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
- `Scope`: the work and the minimum necessary non-goals;
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
- `Skill Execution Strategy`
- `Execution Nodes`
- `Dependencies And Handoffs`
- `Verification Plan`
- `Rollback / Stop Conditions`
- `Knowledge / Card Checkpoint`
- `Granoflow References`
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
mode, availability, decision, fallback, and evidence. When it is not triggered,
the compact `skill_routing: not_triggered` metadata is sufficient.

Use the shared routing enums, including `decision: install_offered` and
`result: pending_user_decision`. A pending decision remains waiting across
resume; it is not a refusal, failure, or fallback.

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
paths, and internal consistency. Apply each finding directly to Outcome,
Evidence, Scope, Risk, Decision, Next Action, or another relevant Analysis
section. Do not add a Grill heading, findings appendix, reviewer ledger, or
before/after commentary. Planning cannot begin unless the result is `passed`.

After the Plan discussion is complete and the Plan is user-confirmed as
executable, notify the user that readiness review is starting and that a passing
document will be uploaded but will still require a separate execution command.
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
  and
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
left. A finding that changes Outcome, Evidence, Scope, Risk, or Decision reopens
Analysis and its Grill. A material Plan change repeats Plan confirmation and the
Readiness Grill. `revisions_required` loops within authoring; `blocked` records
the missing prerequisite without pretending the document is executable.

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
