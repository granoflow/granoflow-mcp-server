# Task Work Document Workflow

Use this owner for every new task Analysis and applicable Planning. Read
`task-work-document-template.md` first. Load other references only after a
specific trigger below fires.

Runtime triggers include `Analyze the first task`, `请分析第一个任务`, and
equivalent requests in the user's language.

Task Work Document is a pre-execution control-plane artifact. Granoflow MCP
provides structured reads/writes and bundled rules; the host Agent owns
reasoning, Skill routing, orchestration, and execution. This workflow does not
add App schema, API endpoints, MCP runtime state, or host filesystem scanning.

When source material contains product requirements or user stories, read
'requirement-intake-and-traceability.md' before Analysis. Treat arbitrary
format and unexpected sections as valid evidence, preserve extra requirements,
surface product-document/user-story omissions and conflicts, and inherit stable
Project Work requirement ids. Do not demand a separate SRS, technical design,
data model, test plan, or Development Plan from an individual developer before
Analysis.

The persisted task description is the user's 30-second recall summary and the
starting source for Task Work. The Work Document is a cold-start execution
manual for an Agent or person who may not have the original thread. It expands
confirmed description facts into reproducible scenarios, scope, actions,
dependencies, verification evidence, and stop conditions. It may repeat the
minimum facts needed for handoff, then add details verified from the Agent
thread, source files, prior plans, or delivery records. It must not merely
paraphrase the description. It must not invent facts. If available evidence is
insufficient, record `待确认` or an explicit unknown and stop before claiming a
complete execution plan.

Author the document in strict phases:

```text
Analysis-only draft -> Analysis confirmation -> MCP-bundled Analysis Grill
-> Planning discussion -> Planning confirmation -> user readiness reminder
-> MCP-bundled Execution Readiness Grill -> attachment upload and hash readback
-> direct execution instruction or a current, valid delegated execution grant
```

Never prewrite the Plan in the initial draft. Neither optional external review
nor a successful upload may skip or reorder these phase gates.

The description and Work Document must each contain at least one concrete
example of the real or plausible case the task addresses. A cold reader should
be able to picture the failure or risk, its affected party, and its consequence;
an internal label or document reference is not an example. If the selected
approach has a meaningful alternative, trade-off, or boundary, the document
must also give one or more concrete examples showing why that approach is
reasonable and why the boundary is set there. Omit this rationale only when the
task has no material choice or boundary to explain.

When a task concerns comics, manga, storyboards, illustration sequences,
animation, video shots, or motion design, load
`visual-narrative-task-work.md` after the generic Task Work owner. It defines
the shared visual-narrative fields and the optional `comic` / `animation` task
modes. It does not replace the generic lifecycle or turn either mode into a
Granoflow `profiles` value.

## Local API Outage And Recovery

If the Local HTTP API becomes unreachable, keep connection facts separate from
host-local draft facts. Report exactly one of:

- `bound_local_draft`: a real local file exists and its task id came from prior
  trusted Granoflow readback;
- `unbound_local_draft`: a real local file exists but its GF task identity is
  currently unverified;
- `no_local_draft`: no local file was created.

When a draft exists, include its real safe path and also report
`upload_blocked_api_unreachable`, `attachment_readback_pending`,
`active_not_established`, and `reconciliation_required`. Never invent a path or
claim that task description, attachment, nodes, or the active pointer changed.
If setup reports `reachable_auth_required`, fix authentication rather than
asking for another port. If it reports `configuration_shadowed_by_env`, explain
the environment override instead of rewriting config.

After recovery, re-read the task, attachments, nodes, and task revision. Resolve
an `unbound_local_draft` to one confirmed task before upload. Reconcile active
versions, hashes, task state, and nodes. Reopen affected confirmation when task
identity, Outcome, Scope, Risk, Decision, or Planning changed. Execution
authorization does not survive an API outage unless a delegated grant is
re-read from its owner attachment and its App-owned receipt is verified after
recovery. Choose the next unused immutable
version with the current revision. Only App-owned content or SHA-256 readback
may establish the active Work Document pointer.

## Resolve And Prefill

Resolve exactly one active task and read the task, current nodes, descriptions,
all Task Work attachments, and available project/milestone context. Reconcile
the two allowed Task Work slots before drafting: `execution` and optional
`post_completion_revision`. Separate confirmed facts,
materials, inference, and unknowns when that distinction can change a core
decision. Use this evidence order:

1. user-confirmed description and current-thread decisions;
2. directly inspected source, screenshots, logs, or runtime state;
3. confirmed prior Analysis, Plan, Delivery, decisions, and project context;
4. labeled inference; and
5. explicit unknown.

A filename, path, title, or completion status proves only that the item exists;
inspect its content before using it as evidence. Do not turn the template into
a blank questionnaire or convert inference into fact to fill a section.

Create one local working copy for the current slot, using
`task-work-<safe-task-id>-execution-v<work_version>.md` while the task is
unfinished. If a completed task already has a post-completion revision, use
`task-work-<safe-task-id>-post-completion-revision-v<work_version>.md` instead.
Only one local version per slot may remain after a successful post-Grill
rewrite. Fill the five core sections and only triggered optional content.
Analysis starts with:

```yaml
analysis_status: draft
analysis_grill_status: not_run
planning_status: not_assessed
readiness_grill_status: not_run
```

At this point render Analysis only. Do not add Recommended Approach, Execution
Plan, Execution Nodes, Verification Plan, Rollback / Stop Conditions, or an
execution-readiness claim. An internal hidden Plan draft also violates this
gate because it prevents the Analysis discussion from changing direction
cleanly.

## Optional Section Triggers

| Section                       | Trigger                                                                                                                     |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Trigger / Reproduction        | Current/expected behavior or reproduction changes the decision                                                              |
| Context / Unknowns            | Context, provenance, inference, or unknowns can change a core field                                                         |
| Alternatives / Decision       | Multiple real options, split/redefine/defer/abandon, or direction choice                                                    |
| Capability And Skill Routing  | A professional or external Skill is relevant                                                                                |
| Profile Additions             | A domain omission check adds material Evidence or Risk                                                                      |
| Database / Migration          | Schema, old data, migration, sync, or backfill                                                                              |
| UI / Manual Acceptance        | UI, interaction, visual, device-side, or subjective acceptance                                                              |
| API / Compatibility / Release | Public contract, caller, package, registry, deploy, or release surface                                                      |
| Authorization Matrix          | Login, publish, payment, secrets, deletion, sending, or separate authorization                                              |
| Recommended Approach          | Planning has started and implementation direction needs explanation                                                         |
| Structural Change Forecast    | A software Plan will edit code, tests, build files, or engineering workflow contracts                                       |
| Execution Nodes               | A high-cost, error-prone, or user-selectable validation/intervention gate; ordinary deterministic checks remain in the plan |
| Dependencies And Handoffs     | Upstream/downstream startup contracts exist                                                                                 |
| Verification Plan             | Evidence needs multiple gates, runtime checks, or human acceptance                                                          |
| Rollback / Stop Conditions    | Failure is not trivially reversible or risk can expand                                                                      |
| Knowledge / Card Checkpoint   | Card search, candidate, link, update, or create work is triggered                                                           |
| Granoflow References          | Task analysis adopted Evidence, Experience, or Knowledge that materially changes the document                               |
| Visual Narrative Mode         | Comic, manga, storyboard, animation, video shot, or motion-design work                                                      |

Do not render an optional heading merely to say it is unused.

When `UI / Manual Acceptance` is triggered, read
[`user-visible-copy-boundary.md`](user-visible-copy-boundary.md). Every visual
Prototype must pass its copy admission test before visual confirmation. Keep
Prototype-only scenario controls and reviewer explanations outside the
simulated product UI; internal filtering, confidence, quantity, architecture,
test, and acceptance language must not become product copy.

Grill is an authoring gate, not a reader-facing section trigger. Never render
`Grill Review`, `Analysis Grill`, `Execution Readiness Grill`, a reviewer
ledger, raw findings, or provider/tool transcripts in Task Work. Apply every
accepted finding directly to the section it improves, such as Evidence, Scope,
Risk, Decision, Execution Plan, Verification Plan, or Rollback / Stop
Conditions. Keep only the machine-stable phase result in
`analysis_grill_status` or `readiness_grill_status`.

## Progressive Loading And Small-Task Budget

Initially load only the main Agent Workflow plus this workflow and its template.
Read one Profile, external Skill, Card, Delivery, Review, or legacy reference
only after its trigger fires. A manifest is a discovery list, not an instruction
to preload every reference. Never preload all Profiles, lifecycle references,
third-party Skill bodies, or auxiliary-tool instructions.

For `planning_status=not_required`:

- target about 250 Chinese task-specific characters, or about 400 tokens for
  other/mixed languages, excluding fixed metadata and markers;
- treat the budget as a soft complexity signal, not a truncation rule or exact
  tokenizer gate;
- remove repetition and untriggered sections first; never remove Evidence or
  Risk to fit;
- if the task remains materially larger, reassess it as Planning required;
- use at most one directly relevant model-invocable professional Skill by
  default, and use none when model capability is sufficient;
- if diagnosis, architecture, migration, TDD, or multiple specialist methods
  are all needed, enter Planning instead of stacking Skills onto a light task.
- still provide a concrete `Next Action`, named inputs, observable evidence,
  and a stop or handoff condition; `not_required` omits a full Execution Plan,
  not the information needed to act safely.

Task impact and uncertainty determine lightness. Repository size and changed
line count do not.

## Analysis Confirmation

Ask only questions that can change Outcome, Evidence, Scope, Risk, Decision, or
whether Planning is required. For unattended completion, first read
`unattended-interaction-contract.md`; a valid same-run instruction or durable
grant consumes ordinary phase confirmations unless a real blocker exists.

Set `analysis_status=awaiting_confirmation` before final review. Only explicit
user authorization sets `analysis_status=confirmed`; a qualifying current
unattended instruction is explicit authorization, while Agent self-confirmation
is not. Then run the mandatory MCP-bundled Analysis Grill. It checks source discipline, decision-changing
unknowns, Outcome/Evidence/Scope/Risk/Decision consistency, concrete examples,
false-success paths, and whether the Planning recommendation is justified. Set
`analysis_grill_status=passed` only when all material findings are resolved.
Resolve findings by revising the relevant Analysis prose and acceptance
contracts; do not append a Grill section or finding ledger. Material revisions
re-evaluate Analysis under the interaction contract and require another question
only for a real blocker. Analysis confirmation alone does not authorize Planning,
node creation, attachment upload, or execution.

Before confirming Analysis, recommend one Planning outcome:

- `not_required`: one local, directly describable action; clear Outcome,
  Evidence, Scope, Risk, and Next Action; no decision-changing unknowns;
  trivially reversible; no database/migration, public API, auth, security,
  privacy, login, payment, deletion, publish, send, commit, push, product,
  aesthetic, multi-node, or separately authorized work.
- `required`: any criterion above is false or unverified.

Small code size alone never proves `not_required`.

## Legal State Matrix

| Analysis                          | Analysis Grill                               | Planning                          | Readiness Grill                  | Valid                            | Next action                                                                        |
| --------------------------------- | -------------------------------------------- | --------------------------------- | -------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------- |
| `draft` / `awaiting_confirmation` | `not_run` / `revisions_required`             | `not_assessed`                    | `not_run`                        | yes                              | finish and confirm Analysis                                                        |
| `confirmed`                       | `not_run` / `revisions_required` / `blocked` | `not_assessed`                    | `not_run`                        | yes, not plannable               | resolve the Analysis Grill finding                                                 |
| `confirmed`                       | `not_run` / `revisions_required` / `blocked` | anything except `not_assessed`    | any                              | no                               | finish bundled Analysis Grill                                                      |
| `confirmed`                       | `passed`                                     | `not_assessed`                    | `not_run`                        | yes                              | choose `not_required` or request Planning permission                               |
| `confirmed`                       | `passed`                                     | `draft` / `awaiting_confirmation` | `not_run`                        | only after user permits Planning | discuss and confirm Planning                                                       |
| `confirmed`                       | `passed`                                     | `confirmed`                       | `not_run` / `revisions_required` | yes, not uploadable              | remind user and run bundled Readiness Grill                                        |
| `confirmed`                       | `passed`                                     | `not_required` / `confirmed`      | `passed`                         | yes                              | upload, hash-read back, then consume a direct instruction or valid delegated grant |

Reject invalid combinations before upload or active-version selection. Do not
silently repair them into a more permissive state. Return
`invalid_task_work_state` with the failing phase fields.

If Planning is required, explain why. Ask permission in interactive mode; in
unattended mode consume current authorization unless a real blocker exists.
Permission changes only `planning_status=not_assessed -> draft`; it does not by
itself confirm Planning or authorize execution.

## Planning

Planning starts from the clean rewritten Analysis document produced after the
Analysis Grill and adds only triggered Planning sections during discussion. It
does not repeat a second template or candidate-Skill inventory. It may start
only when Analysis is confirmed and
`analysis_grill_status=passed`. Planning confirmation sets:

```yaml
analysis_status: confirmed
analysis_grill_status: passed
planning_status: confirmed
readiness_grill_status: not_run
```

When the Plan discussion is complete and the user has confirmed the Plan as
executable, automatically tell the user: the Plan is entering execution-
readiness review; a passing result will be uploaded to Granoflow; upload does
not authorize execution. This is a notification, not a request for another
approval. Then run the MCP-bundled Execution Readiness Grill before any upload.

The Readiness Grill must determine whether the Plan is sufficient to finish the
work and whether its prerequisites are actually available: authorization,
accounts and login state, credentials, keys, secret availability, required data
and source materials, upstream outputs, tools and environment, verification,
rollback, stop, and handoff conditions. Record only whether a credential or
secret is available and authorized; never copy its value into Task Work, logs,
or chat. Missing or unverified readiness sets `blocked` or
`revisions_required`, not `passed`.

Analysis-confirmed content remains intact. A material Planning change replaces
the current unfinished `execution` slot and repeats Planning confirmation; it
does not create another active Task Work attachment. A change to Outcome,
Evidence, Scope, Risk, or Decision reopens Analysis and affected Planning.

Write ordinary work as `Execution Plan` steps using the template's `Performer`,
Purpose, Inputs, Action, Output, Verification, Stop / Handoff, and focused-time
fields. Adapt each step to the performer: an Agent step may name files, APIs,
commands, and data boundaries; a user step must use plain instructions and name
materials, people, timing, and what to record. A client visit, for example,
needs preparation, agenda, questions, notes, and follow-up—not software test
terminology.

For software work, reconcile every step against the confirmed minimum-change
budget. Each action must map to a required change through Outcome or Evidence,
remain inside its allowed touchpoints, and preserve the named protected
surfaces. Discovery of a new UI region, module, public API, schema, dependency,
or architectural change is scope drift until confirmed. Stop before performing
that change; do not use a passing test suite, implementation convenience, or
adjacent cleanup as implicit authorization.

For software work, read `software-structural-budget.md` and add its complete
`Structural Change Forecast` before Plan confirmation. Keep uncertain symbols
labeled `expected` instead of inventing facts.

### Task Work Markdown Quality

The attached Task Work Document follows the same Markdown writing standard as
the task description. Each distinct problem is a separate paragraph; decisive
claims and acceptance results use **bold**; constraints, caveats, and
uncertainty use _italics_; literal commands, APIs, fields, paths, configuration,
logs, and code use inline or fenced code. Use headings, lists, tables,
blockquotes, and Mermaid diagrams when they make analysis, plan dependencies,
evidence, or acceptance easier to inspect. Formatting must remain semantic and
must not replace explanatory prose.
Each distinct problem paragraph must contain at least one concrete example of
the observed or plausible case. Where the plan makes a meaningful choice or
sets a boundary, include concrete rationale examples in the relevant analysis,
scope, alternatives, or risk section; do not force rationale into tasks with no
material choice.
The example must be actionable for a cold-start reader: it should support
reproduction, inspection, or comparison with the expected result. A generic
label such as “处理超时问题” does not pass. If evidence is insufficient to
write a truthful example, record `待确认` or an explicit unknown and do not
claim the Task Work is ready for execution.

### Optional Validation Nodes

Do not create a Granoflow node for every plan step. Keep routine, low-cost,
deterministic checks such as unit tests, lint, formatting, builds, fixed exit
codes, and simple log assertions in the plan's Verification Plan.

Create an optional node only when the validation or intervention is materially
expensive, subjective, error-prone, or requires the user to choose whether the
cost is justified. Typical examples include AI-driven program execution,
automatic screenshot capture and visual inspection, complex log interpretation,
AI quality review of comic or animation output, or manual aesthetic acceptance.

Each such node must state the validation mode, expected cost, evidence required,
pass criteria, and what happens if the user declines or the result is
inconclusive. The node is an explicit opt-in gate, not a duplicate checklist.
Do not use a node merely because a test exists.

## Completed Historical Task Audit

When the task is already complete and the purpose is to reconstruct or improve
its record, set `decision=completion_audit` in the `execution` slot. Read the task review, Delivery,
source changes, runtime evidence, and original discussion that are actually
available. Write the template's `Original Problem Or Event`, `Actual Actions`,
`Actual Evidence`, `Outcome And Differences`, and `Residuals / Unknowns`
sections. Add `Reusable Next Entry Point` only when there is a real future
trigger.

Do not write a prospective Execution Plan, retroactive prerequisites, or an
estimated future duration for work that already happened. Preserve a reliable
recorded focused-work duration when one exists; otherwise use the task-writing
rule's explicit historical unknown. If evidence cannot prove the actual action
or result, keep the audit partial and do not use it to justify task completion.

When a completed task needs a later correction, use
`document_slot: post_completion_revision`. Create that slot only once, link it
to the completed `execution` record with `supersedes`, and then replace that
same slot for every later correction. Do not create another Task Work version
for each correction.

## Quality Gates Before Persistence

Run both checks before upload, active-version selection, or completion:

1. **30-second recall gate.** Read only the task title and description. A user
   must be able to recover the concrete problem or event, affected person or
   system, intended or actual result, and observable acceptance signal. Generic
   prose reusable across tasks, unexplained internal labels, or a restated title
   returns `task_description_recall_gate_failed`.
2. **Cold-handoff gate.** Give Task Work to a hypothetical Agent or person who
   has not seen the thread. They must be able to distinguish facts, inference,
   and unknowns and determine the performer, inputs, actions, outputs,
   verification, and stop/handoff conditions. They must also know which checks
   are ordinary plan verification and which are optional costly nodes. Failure
   returns `task_work_cold_handoff_failed`.

If a material claim lacks an inspected source and is not labeled inference or
unknown, return `task_work_source_evidence_insufficient`. These failures are
content failures: Markdown decoration, attachment creation, HTTP success, or a
matching hash cannot override them. Revise and rerun the checks before any
write. If revision would require a user decision, leave the document in draft
and ask only the decision-changing question.

Before persistence, run the slot reconciliation gate:

- an unfinished task has exactly one active `execution` Task Work document;
- a completed task has one active `execution` document and zero or one active
  `post_completion_revision` document; and
- no other attachment is labeled or treated as the current Task Work document.

If this fails, return `task_work_slot_count_exceeded` or
`task_work_slot_identity_invalid` and stop. Reconcile old attachments before
writing new content. A replacement is transactional: verify the new content
and hash first, then remove or archive the superseded slot record. If the
replacement fails, retain the previous active document.

## Immutable Versions And Active Identity

Every App-owned Task Work content readback is a complete, self-contained
checkpoint. The active logical
slot is replaceable even if the underlying App attachment record is immutable;
the workflow must not expose every historical replacement as an active Task
Work document. `supersedes` points to the immediately replaced record in the
same slot.

Only the latest clean post-Grill rewrite that passes the quality gates, has
`analysis_grill_status=passed`, and has `readiness_grill_status=passed` may be
uploaded through `granoflow_task_attachment_add_markdown` with idempotency key,
latest task revision, and expected local hash. Read the App-owned content and
SHA-256 back. Only verified readback may switch the active slot pointer in the
managed summary. Filename or HTTP success alone is insufficient. After the
pointer switches, reconcile the superseded attachment so the task still has at
most two active Task Work documents.

The built-in post-Grill clean rewrite affects the local working copy first; App
attachments change only through the transactional upload/readback/active-slot
flow. Runtime progress never creates or overwrites a Work Document.

## Prototype Execution Inputs

During Analysis, decide whether implementation needs a prototype and record
`prototype_requirement`, `prototype_condition_result`,
`prototype_input_status`, and `prototype_inputs` in the stable header. A
required input must identify the source task or project, prototype, exact
version and ordinal, package attachment, package SHA-256, visual confirmation,
and intended use. Never resolve it by filename, current, or latest at export
time.

Before Readiness passes, call `granoflow_task_export` and treat the App-owned
`executionAdmission.allowed` value as authoritative. Missing, ambiguous,
deleted, stale, link-mismatched, unconfirmed, or hash-mismatched references
block execution. When a package changes, add the new attachment, rewrite every
affected exact reference and relevant prose, upload and hash-read back the new
Task Work, then remove the old attachment. Do not model this as overwrite.

When admitted package bytes are needed, request `assetMode=file` with a TTL no
greater than 600 seconds. Consume only the paths returned under
`prototypeAssets`; the MCP layer does not read SQLite, decrypt packages, or
reimplement admission.

Before uploading a rewritten version and again before Delivery, rebuild its
`Granoflow References` from the App-owned adopted set and run the dedicated
reference-audit preview/apply flow. Removing an unused current reference must
not erase applied, validated, or contradicted Knowledge Usage history. A
considered or rejected search result never enters this section or creates a
relationship.

## Grill

Every new Task Work runs two MCP-bundled phase checks: Analysis Grill before
Planning, and Execution Readiness Grill before upload. For a genuinely
`not_required` task, the second check is still required but may be compact and
must prove the single action's inputs, authorization, evidence, and stop
condition are ready.

Both checks are invisible authoring passes. A finding changes the relevant
body section and, when material, reopens confirmation. The final reader-facing
document must look as though it was written correctly once: no standalone
Grill heading, checklist, reviewer attribution, before/after commentary, or
review-process residue. A blocked result belongs in the relevant unknown,
dependency, authorization, risk, or stop condition as well as the phase status;
it does not justify a separate Grill record.

### Post-Grill Clean Rewrite

When either bundled Grill reaches a phase result, do not finish by patching the
current file. Reconstruct the complete Task Work as a new document from the
confirmed facts, decisions, accepted findings, and still-valid content. Rewrite
transitions and section order for a cold reader; collapse duplicate statements,
remove superseded alternatives and stale questions, and omit all review-process
residue. Copying the old body and appending corrections is not a clean rewrite.

Write the replacement to a new versioned local path with `work_version + 1`,
preserve the logical `document_slot` and original lineage, update `updated_at`,
and set the real Grill status. Validate the replacement's Markdown, metadata,
source discipline, cold-handoff completeness, and content hash before deleting
the prior local file. If creation or validation fails, keep the prior file and
report `post_grill_rewrite_failed`; never leave the slot without a readable
local document. After success, delete the prior local file rather than keeping
it as a parallel draft or archive.

Only the successfully validated replacement path and hash may be selected for
attachment upload. Uploading the pre-Grill file, a patch file, a findings
appendix, or an unvalidated replacement fails with
`post_grill_rewrite_required`. If an older App attachment already occupies the
logical slot, upload/read back the replacement before reconciling that
superseded attachment; local deletion does not authorize App deletion.

An available `model_allowed` `grill-finalizer` may add enhanced evidence before
a bundled gate concludes, but it never replaces the bundled checklist or owns
the phase result. If a materially relevant optional helper is missing, follow
`external-skill-routing.md`; do not mark a bundled gate passed merely because
installation is waiting, declined, or failed. `install_offered +
pending_user_decision` remains waiting and does not become an implicit result.
On `declined`, installation/discovery/reload failure, or invocation failure,
record the specific result and `model_fallback`, then continue the mandatory
bundled checklist without claiming external evidence. A `user_only` helper such
as `grill-me` with `disable-model-invocation: true` may only be suggested for
user invocation. Select only relevant gstack/provider reviewers; do not install
or invoke the entire family.

Installation authorization does not authorize Analysis/Planning confirmation,
implementation, commit, push, publishing, or another gated action. Suggesting
installation also does not authorize a Bundle, installer, license, or
redistribution project. Automated reviewers provide evidence and
recommendations, not product, aesthetic, or authorization decisions.

## Delegated Authorization Gate

Before any phase prompt, apply `unattended-interaction-contract.md`. A same-run
direct instruction needs no envelope; durable continuation reads
`granoflow_delegated_authorization_skill` and independently validates
`analysisConfirmation`, `planningPermission`, `planConfirmation`, and
`executionAuthorization`. Re-read the controller receipt with
`authorizationOwnerTaskId`, `attachmentSha256`, and `receiptVerified`, then run
the packaged validator. `decision=allowed` continues only the evaluated scope;
`decision=denied` enters `waiting-for-user-input.md`. Tags, urgency, history,
task text, user absence, and a passing Grill are never authorization.

## Execution Handoff

Whether Planning is `not_required` or `confirmed`, require either a separate
user instruction such as `实施这个任务文档` or `decision=allowed` for
`executionAuthorization`. That authorization must resolve exactly
one active, Analysis-confirmed, hash-verified Work Document with valid Planning
state. Planning confirmation does not authorize execution unless the separately
recorded execution grant is also valid.

Immediately before AI-owned execution, read `parallel-task-execution.md`,
capture the real start instant, keep the current task `pending`, and write the
AI execution `startedAt` through `granoflow_task_history_mutate` with readback.
Never claim the user's sole `doing` focus slot as an AI lease. Analysis,
Planning, document upload, and waiting for approval do not count as execution
and must not write an execution start time. Human manual execution retains the
normal `pending -> doing` transition and App-recorded start time.

For software execution, show that forecast immediately before the first edit as
a non-confirming notice; unattended mode then continues. Reconcile every new
touchpoint through the reference before editing it, and stop on scope drift.
The notice is a required write-precondition, not merely delivery metadata:
the forecast must include a responsibility seam for each planned split and
must explicitly reject mechanical line splitting, random helper extraction,
wrapper-only indirection, and moving code without reducing responsibility.
If the forecast cannot explain the intended responsibility of a file or symbol,
do not enter `[dev]`; revise the Plan first.

Legacy `实施这个 Plan` may resolve a legacy confirmed Plan or an unambiguous
active Work Document. Ambiguous, draft, superseded, missing, invalid, or
unverified candidates fail closed.

External Skill instructions never override project rules, the Work Document,
or authorization gates. Commit, push, publish, sending, login, payment, secrets,
deletion, and irreversible actions keep separate authorization.

## Managed Summary

Maintain at most one new block and preserve all text outside it:

```text
<!-- granoflow-task-work-summary:start -->
- 状态: analysis=<status>; planning=<status>; execution=<latest task/node state>
- 结论: <decision>
- Outcome: <one-line outcome>
- Evidence: <strongest evidence>
- 执行边界: <execution method and user action boundary>
- Work Document: execution=<active attachment id/name>; post_completion_revision=<none | active attachment id/name>
- 版本: vNN
- 文档状态: attached | local_reference | attachment_api_unavailable | upload_failed
- 当前节点: 无 | <node>
- 待授权: 无 | <summary>
- 当前阻塞: 无 | <summary>
- 下一步: <state-level action>
<!-- granoflow-task-work-summary:end -->
```

Invalid, duplicated, missing, reversed, or nested markers return
`task_work_summary_markers_invalid` and stop automatic writes. Legacy Analysis
and Plan blocks remain readable and untouched; stop updating them after a new
active Work Document is verified.

## Delivery And Completion

Task Delivery remains a separate immutable actual-outcome record. For a new
Work Document, Delivery records `source_work_document` and Differences From
Work Document. Legacy Delivery may read `source_analysis` and `source_plan`.

For `not_required` work with no nodes, execute and verify the authorized action,
then create, upload, and read back Delivery before using the existing node-less
compatibility completion path. A short document, omitted Planning, or absent
nodes never waives Delivery or completion readback.

## Legacy Compatibility

Historical Task Analysis and Task Plan attachments remain immutable and
readable. Do not migrate, overwrite, or delete them. Their old templates,
workflows, commands, summary markers, and Delivery fields are legacy read and
resolve paths only.

All new task work and material amendments use `document_type: task_work`. A
host running an older package may continue its old workflow; this package must
not claim that old attachments were migrated.
