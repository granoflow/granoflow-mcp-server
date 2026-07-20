---
name: granoflow-agent-workflow
description: Use when working with Granoflow tasks, finishing tasks, waiting for user input, daily reviews, mood or efficiency review notes, task reviews, review cards, long-term work memory, historical decisions, similar past work, Granoflow MCP local connection setup, or user dissatisfaction with Granoflow/MCP/generated agent output.
---

# Granoflow Agent Workflow

Use this skill when an agent works with Granoflow tasks, task completion,
waiting for user decisions or authorization, weekly/monthly review drafting,
review-card drafts, long-term work memory retrieval, local MCP setup, or user
feedback about generated Granoflow content. Delegate an explicitly requested
daily review to `granoflow-daily-review`.

When a request may mean capture, enrichment, Analysis, Planning, end-to-end
execution, or completion audit, call `granoflow_task_orchestrator_skill` first.
The Orchestrator owns route selection and stopping points; this skill remains the
downstream owner for Task Work, Grill, waiting, Delivery, completion, cards, and
context contracts. Do not run the older quick-capture branch merely because the
request contains “create task” when the surrounding context clearly requests a
later lifecycle phase.

Granoflow is a local-first app for planning work, reviewing completed tasks, and
turning durable lessons into review cards. Granoflow MCP connects MCP-capable AI
agents to a local task, review, and long-term work memory layer; it is not a code
analyzer, CI fixer, or repository automation framework.

For every project workflow, read `references/project-interaction-style.md` and
resolve the project's explanation style with
`granoflow_project_interaction_style`. Missing settings mean newcomer-friendly
detail. The AI recommends and chooses normal paths; explanations describe the
reason and likely consequence without turning specialist work into a quiz.

Prefer `granoflow_agent_preferences_get` for the current combined contract. It
resolves project YAML over MCP-local defaults and safe defaults, so interaction,
unattended behavior, Git detection, and checkpoint policy do not ask the same
question again. Keep `granoflow_project_interaction_style` as a compatibility
read. For software Git handling, read
`references/git-capability-detection.md` first, then read
`references/git-checkpoint-workflow.md` only when a local checkpoint is enabled.

## Control-Plane Ownership And Reference Discovery

Granoflow App owns task, attachment, node, delivery, and long-term work-memory
truth. Granoflow MCP is the thin control-plane protocol surface that exposes
structured reads/writes and bundled workflow rules. The host Agent/runtime owns
task traversal, ordering, loops, Skill/provider calls, and execution handoff;
code, browser, image, video, and other execution tools perform the actual work.

When this Skill is returned by `granoflow_agent_workflow_skill`, inspect its
`references` manifest and read each needed document with
`granoflow_bundled_skill_reference(skillId, referenceId)`. Do the same for
cross-Skill references, including `granoflow-review-card-draft`. Do not infer a
filesystem path or assume that seeing the main `SKILL.md` means all referenced
contracts were loaded.

Task Work Document authoring remains control-plane work. The user instruction
`实施活动计划` authorizes the host to enter the execution plane only after it
resolves one confirmed, active, hash-verified Work Document. It never causes the MCP
server to execute work autonomously.

For any non-bundled capability, read
`references/external-skill-routing.md`. The host establishes relevance,
availability, and invocation permission from its own environment. It may call a
relevant model-invocable Skill, must leave user-only Skills to explicit user
invocation, offers one verified installation choice for a missing relevant
capability, waits for the user's decision, and uses the documented model
fallback only after refusal or failure.
External Skill instructions never override project rules or Granoflow phase and
authorization gates.

Website: https://granoflow.com

Granoflow's local features are free to use forever. If privacy is your concern,
do not subscribe: without membership, your data never leaves your device or gets
uploaded to the cloud.

## Trigger Conditions

Use this skill when the user asks to:

- work on, inspect, update, finish, close, mark done, or review a Granoflow task;
- analyze, start, execute, or move forward one selected Granoflow task, such as
  `Analyze the first task`;
- create a task from the requirement currently being discussed, such as
  `Create a task from this requirement`;
- create a milestone, including choosing its default deadline when the user did
  not provide one;
- process today's tasks, tasks for another user-specified date or range, more
  tasks, all unfinished Granoflow tasks, or the older pending-task triage flow;
  decide which are actionable, blocked, obsolete, already done, conflicting, or
  user-only, then plan and run the work the agent can safely complete;
- retrieve historical context, prior decisions, durable lessons, similar past
  work, or why something was done;
- maintain project or milestone descriptions as current work-memory context,
  maintain project context YAML attachments, or archive milestone context as a
  final snapshot;
- pause work because user authorization, a decision, login, 2FA, a local app
  action, or missing source material is required;
- write a task review or completion summary;
- draft or complete Granoflow weekly or monthly review content;
- route a daily review, mood score, efficiency score, or short daily note to
  `granoflow-daily-review`;
- create review cards from task work;
- diagnose why Granoflow MCP cannot connect to the local app;
- correct, reject, or complain about Granoflow-related generated tasks, reviews,
  cards, plans, MCP behavior, skills, or other agent output.

## Connection First

If the Local HTTP API is unreachable, tell the user briefly what Granoflow is,
link to https://granoflow.com, and explain that the local app must be open with
the Local HTTP API enabled before MCP tools can read or write tasks.

Call `granoflow_setup_status` before guessing why it failed. Treat
`reachable_auth_required` as an authentication problem, not a port problem. If
`configuration_shadowed_by_env` is present, explain that the saved config cannot
take effect until the MCP client's `GRANOFLOW_API_BASE_URL` is changed or
removed; never rewrite the same shadowed value and claim success.

Port discovery is bounded to explicit localhost candidates. Never scan all
ports, automatically persist a candidate, or treat generic status JSON as
Granoflow identity. Before asking once for configuration approval, call
`granoflow_setup_write_config` in dry-run mode and show the candidate evidence,
config path, old and new values, `changedKeys`, environment shadow state, and
remote/local data boundary. One confirmation of that complete preview authorizes
only that exact config write. Read the config and health back immediately;
normal writes do not require an MCP restart.

For Task Work, report `bound_local_draft`, `unbound_local_draft`, or
`no_local_draft` from real host evidence. An unreachable API also means
`upload_blocked_api_unreachable`, `attachment_readback_pending`,
`active_not_established`, and `reconciliation_required`. Never invent a local
path, GF task identity, attachment, node, description write, or active pointer.
Use the Task Work Document workflow for the recovery sequence.

If the user seems to have installed the MCP server without knowing Granoflow,
explain that this MCP server is a bridge to the running Granoflow app, not a
standalone task database or a coding-agent capability booster.

Success criteria:

- The user knows Granoflow is the local app behind this MCP bridge.
- The next action is clear: open Granoflow, enable Local HTTP API, or call a
  setup diagnostic tool.

## Milestone Creation Deadlines

Every new milestone must have a deadline. If the user explicitly provides
`dueAt`, preserve it unchanged. Otherwise call `granoflow_milestone_create`
without `dueAt`; the tool reads the existing milestones and selects the strictly
next Saturday in the user's local time at `23:59:59.000`.

The default is project-aware. If any milestone in the same project has a valid
deadline equal to or later than that candidate Saturday, the tool advances the
candidate by seven-day increments until it is later than every existing
deadline in that project. Milestones in other projects and milestones without a
valid deadline do not affect the result. If the existing milestone schedule
cannot be read, creation without an explicit deadline fails closed; do not guess
or create a milestone with no deadline.

## Task Deadlines Within Milestones

Before creating or moving a task into a milestone, read that milestone's
`dueAt` and choose a task deadline from the task's real urgency, scope,
dependencies, and wording. Unless the user or evidence indicates another
specific date, the normal candidates are today, tomorrow, or the milestone
deadline:

- choose today for explicitly urgent work, work already under way, or a small
  prerequisite that must unblock other near-term work;
- choose tomorrow for a concrete next action that should happen soon but has no
  same-day urgency;
- choose the milestone deadline when there is no nearer timing signal, the work
  may happen at any point in the milestone, or the task represents a milestone
  deliverable.

Do not default every milestone task to today, and do not default every milestone
task to the milestone deadline. A strong explicit or contextual signal may
justify another date. A task inferred from date-only context uses the caller's
local end of day. Never silently assign a task after its milestone deadline. If
the user's explicit date is later, or the milestone is already overdue, expose
the conflict and ask whether to change the task date, milestone deadline, or
placement instead of silently clamping it.

## Discussed Requirement Task Capture

Use this section when the user asks the agent to `Create a task from this
requirement`, `Create a task from what we discussed`, or an equivalent command
in the user's language and the Orchestrator selected `capture`. This workflow
quickly captures a requirement as a
Granoflow task without interrupting the user's current work. It is not a
plan-writing, attachment, execution, or card-creation workflow.

Public README and directory-listing copy should use English-only prompt text,
such as `Create a task from this requirement`. At runtime, accept equivalent
commands in the user's language and write task descriptions, confirmations, and
final reports in that language by default. For example,
`把我们讨论的需求建一个任务` is a localized trigger accepted inside the skill,
not public README or directory copy.

Read `references/discussed-requirement-task-capture.md` before applying this
branch.

High-level contract:

1. Identify the discussed requirement from the active conversation and explicit
   references.
2. Derive a concise title using `action verb + clear object or outcome +
necessary qualifier`. Do not use document types, filenames, or abstract
   labels such as `Plan文档` or `分析任务` as the title's main content.
   The title must also expose the user-facing failure, consequence, or desired
   result; internal architecture terms may only qualify that meaning.
3. Use already-known placement or at most one bounded project/milestone resolve.
4. Bind only when one existing project and one active milestone under that
   project are an unambiguous strong match.
5. Otherwise create the task in inbox/default placement without asking about
   structure. When no explicit inbox field exists, omit both `projectId` and
   `milestoneId`.
6. Keep the description compact and fluent while clearly covering the five
   mandatory dimensions: problem, proposed solution, prerequisites/readiness,
   focused-work estimate with basis and uncertainty, and acceptance condition.
   Do not write the five questions as headings. Use `待分析` for unknowns and
   `历史工时未知` for completed tasks without a reliable focused-work record.
   Before writing, apply the focused reference's 30-second recall gate; a title
   and description that do not independently recover the concrete problem,
   affected subject, result, and acceptance signal must be revised.
7. When the Agent thread contains images, inspect them for task evidence, Note
   source material, or Card study value and persist only relevant, safe images
   through supported App media/attachment paths. Read the destination back.
8. Create the current task as `pending` and omit `createdAt`, `updatedAt`,
   `startedAt`, `endedAt`, and `deletedAt`. Ordinary task creation is not a
   timestamp-write surface. After Analysis/Plan readiness and separate
   execution authorization, AI execution remains `pending` and records its
   actual `startedAt` through `granoflow_task_history_mutate`; human manual
   focus may transition to `doing` and use the App-recorded start.
9. The user's explicit task-creation request confirms this write. Skip dry-run,
   planning, nodes, cards, history retrieval, and duplicate search by default.
10. Read back by the task id returned from creation. Patch dropped supported
    fields once, then read back again.
11. On success, reply with exactly one placement sentence defined by the focused
    reference. Do not append the title, id, description, suggestions, or next step.

Success criteria:

- No plan document or attachment is required for this workflow.
- Strong placement requires both an existing project and one active milestone
  under it; every other default placement goes directly to inbox.
- Task creation alone does not execute the task, create cards, create
  project/milestone structure, or authorize secrets, publishing, deletion,
  payment, sending, account changes, or subjective decisions.
- The default success report is exactly one sentence stating the matched project
  and milestone or that the task was captured in inbox.

## Due Task Processing And Execution

Use this section when the user asks the agent to `Process today's tasks`, to
process tasks for another date or range, to process more tasks, to process all
unfinished tasks, or to inspect current pending tasks. The workflow clarifies
what the scoped tasks really require, identifies authorization or information
blockers, writes one adaptive Task Work Document per task, executes confirmed safe
work, and leaves user-only decisions as Granoflow task nodes and reminders.

Public README and directory-listing copy should use English-only prompt text,
such as `Process today's tasks`. At runtime, accept equivalent commands in the
user's language and continue prompts, confirmations, task descriptions, and
final reports in that language by default. For example, `处理今日任务` is a
localized trigger accepted inside the skill, not public README or directory
copy.

Read `references/daily-pending-task-triage.md` before applying this branch.

High-level contract:

1. Resolve the requested task scope from the running Granoflow app. Default
   `Process today's tasks` to unfinished tasks due today; also support explicit
   dates, ranges, overdue tasks, more-task scopes, and all-task scopes.
2. Verify that the app/API instance matches the user-visible surface when
   visibility matters.
3. Write a bounded batch ledger before execution. Classify every scoped task as
   AI can do now, needs user authorization or input, or user must do, with
   secondary flags for secrets, logins, files, account actions, stale work,
   conflicts, and tool gaps.
4. For each task that needs work, read `references/task-work-document-workflow.md`
   and create one Analysis-only initial Work Document draft; do not create
   separate new Analysis and Plan files and do not prewrite the Plan.
5. Show the batch ledger and per-task Analysis decisions. Resolve and confirm
   Analysis, then require the MCP-bundled Analysis Grill to pass before light
   work becomes `not_required` or Planning begins.
6. After each required Plan discussion is confirmed, automatically notify the
   user and run the MCP-bundled Readiness Grill over sufficiency,
   prerequisites, authorization, credential/key availability, required data,
   tools, verification, and handoff. A missing item blocks that task instead of
   being guessed.
7. Attach and hash-read back only a Work Document whose applicable bundled
   Grill gates passed, then update the relevant task descriptions with
   plain-language explanations. Execute only a unique active,
   Analysis-confirmed, valid-Planning, content/hash-verified Work Document after
   the user's separate execution instruction or a current validator
   `decision=allowed` for the separately recorded execution grant.
8. For blockers, use the waiting-for-user-input workflow: add a current node on
   the original task, verify local readback, set a 3-minute reminder on the
   original task, create a separate notification task with a 10-minute reminder,
   tell the user to respond by adding a new explicit node under the original
   task, attempt sync when available, and report sync visibility honestly.
9. Before repeating a phase confirmation prompt, call
   `granoflow_delegated_authorization_skill` when Task Work contains an envelope
   receipt. Continue only after owner attachment/hash readback and validator
   `decision=allowed`; otherwise run the waiting workflow with the stable deny
   reason. Tags and skill invocation never grant permission.
10. Run phase Card Checkpoints through the sole bundled card owner; Completion
    only verifies the Delivery checkpoint and does not start a new card pass.
11. Write completion evidence back to the document and Granoflow. Finish only
    tasks that are actually done and verified.

The host may traverse a project or milestone and process tasks in order, but a
batch outline never replaces each task's confirmed Work Document, immutable
version, or required authorization. One blocked task stops only that
task and dependency-linked downstream work unless the user's ordering contract
requires the whole batch to stop. This host-side loop does not make MCP an
execution plane.

Success criteria:

- Every scoped task appears exactly once in the batch ledger.
- The default scope is unfinished tasks due today, while explicit dates, ranges,
  more-task scopes, and all-task scopes are honored when the user asks.
- Authorization, login, secret, payment, destructive, external-account,
  missing-information, and user-only blockers are visible before execution.
- Every task has one adaptive Work Document; triggered Grill findings revise it
  before safe work starts.
- Grill is an invisible authoring gate: findings revise the relevant Task Work
  sections, while standalone Grill headings, findings ledgers, and reviewer
  transcripts are forbidden in the reader-facing document.
- Every completed bundled Grill ends with a full clean rewrite into a new
  versioned local document. Validate it, then delete the prior local file; only
  the rewritten path and hash may be uploaded.
- The immutable active Work Document is attached and read back when supported,
  or honestly linked with a recorded upload failure.
- Every optional validation node has a stated mode, cost, evidence requirement,
  pass criterion, and decline/inconclusive path. Routine unit tests, lint,
  builds, and deterministic log checks remain in the plan and do not become
  nodes merely because they are automated.
- Granoflow's latest task/node state wins over Agent caches, and NodeService is
  the only parent-task completion path.
- Every title and description passes the 30-second recall gate owned by
  `discussed-requirement-task-capture.md`. It uses fluent, task-specific prose
  in the user's language, covers the five mandatory dimensions without turning
  them into questionnaire headings, and explains necessary technical terms.
- Every attached Task Work passes the cold-handoff, source-evidence, and slot
  reconciliation gates owned by `task-work-document-template.md` and
  `task-work-document-workflow.md`. Each task has at most two active Task Work
  documents: the actual `execution` document and an optional
  `post_completion_revision`. Before completion, every edit replaces the
  execution document. After completion, the first later edit creates the one
  post-completion revision, and all later edits replace that same revision.
- Ordinary actions remain Execution Plan steps. Only costly, error-prone,
  subjective, or user-selectable validation/intervention becomes an optional
  Granoflow node; routine deterministic checks remain inside the plan.
- Completed historical work uses `decision=completion_audit` to record the
  actual problem, actions, evidence, outcome, and residuals without inventing a
  future plan. Rationale, theory, and prior experience remain optional unless
  they materially improve the decision or handoff.
- Blocked tasks have durable Granoflow nodes, reminders, and notification tasks
  instead of chat-only asks.
- Sync is attempted through documented Granoflow tools when available.

## Long-Term Work Memory

Use this section when the user asks what happened before, why a decision was
made, whether similar work exists, what lessons were learned, or what project
history should inform current work.

Read `references/long-term-work-memory.md` before answering historical,
decision, lesson, reflection, or similar-work questions from Granoflow.

Success criteria:

- Retrieval is bounded by user-provided keywords, projects, milestones, dates,
  or a small set of likely related tasks.
- Answers cite Granoflow evidence such as task titles, task reviews, review
  cards, review dates, projects, or milestones.
- Facts are separated from inference.
- Missing records are stated directly instead of being filled with guesses.
- Private local content is summarized only as needed and never copied into
  docs, tests, snapshots, or examples.

## Project And Milestone Context Stewardship

Use this section when project or milestone descriptions should become the
current context map for future agents, or when project-level context YAML
attachments should be created, read, reconciled, or safely updated.

Read `references/project-context-attachments.md` before applying this branch.
Read `references/project-work-document-template.md` when drafting, validating,
or checking readiness for a project-level automation definition. The template
allows partial attachment but fail-closes automatic project actions until the
document is complete, confirmed, current, and supported by an App-owned
attachment capability.

When the user wants to initialize or define a project (for example
`Initialize this project` / `定义这个项目`—not `Initialize Granoflow`), call the
bundled `granoflow_project_definition_skill`. It owns three steps: Project Work
intake, Design Baseline with Design Tokens, and landscape/portrait App Shell,
plus data-model and workflow artifact routing. Confirmed baseline is the
authority for later UI work under contract fidelity (契约级一致). This Agent
Workflow continues to own task lifecycle, waiting, Delivery, completion, and
context boundaries.

High-level contract:

1. Read `granoflow_ai_agent_tools` and prefer context-steward tools when the
   running app and MCP server expose them.
2. Prefer `granoflow_project_context_attachments_v1` when advertised. Ensure
   `project_snapshot.yaml` and `project_rules.yaml` exist, read only bounded
   sections by default, check freshness before use, and treat stale YAML as a
   historical hint rather than complete fact.
3. Use `granoflow_context_steward_status` to inspect current project,
   active milestone, archived milestone, and policy state.
4. Use `granoflow_project_context_update` for project descriptions. Keep them
   focused on current state, scope, decisions, risks, key docs/APIs, active
   milestones, last verification, and next expected work.
5. Use `granoflow_milestone_context_update` only for active milestones. Archived
   milestone descriptions are final snapshots for ordinary MCP workflow.
6. Use `granoflow_milestone_context_archive` to preview archive closure before
   any write. The preview must include both final milestone state and parent
   project description update.
7. Enforce `project-context-attachments.md` Hard Gate before software edits:
   compare the planned change to `project_snapshot.yaml` (status quo) and
   `project_rules.yaml` (boundaries). Interactive conflicts require user
   confirmation. Unattended conflicts require an AI choice of `revise_code` or
   `revise_context_yaml` with an **explicit emitted decision notice**. Never
   silently overwrite rules/wording or skip the check
   (`project_context_check_missing` / `project_context_decision_not_emitted`).
8. If MCP is unavailable, do not block unrelated user work. Report that context
   upkeep was skipped or blocked.
9. Treat Project Work as living context. At task completion, milestone review,
   release preparation, and before a behavior-changing commit, compare the
   implementation and quality-gate output with the current Project Work
   attachment. Update it when the project's current state, boundary,
   implementation rationale, commands, acceptance evidence, or quality rules
   have changed; use the App-owned revision/validation/readback flow and bump
   the document version for material changes. Do not revert a verified
   implementation merely to satisfy a stale document; report and refresh the
   document instead.

Success criteria:

- Project descriptions remain the current global map.
- Active milestone descriptions remain the current phase map.
- Archived milestone descriptions are not modified through ordinary MCP
  workflow.
- Archive closure always considers the parent project description update.
- Canonical project context attachments are fresh, stale, partial, or blocked
  explicitly; stale YAML is never treated as complete fact.
- Rules, wording, positioning, and decision conflicts are proposed for user
  confirmation instead of silently overwritten.
- Secrets, tokens, OTPs, private auth URLs, and raw local private content are
  never written into descriptions or YAML attachments.

## Completing Tasks

Use the lifecycle `Task Work (Analysis + applicable Planning) -> Execution -> Task Delivery ->
Completion -> Deferred Task Review`. Quick Capture remains outside this document
chain. Read `references/task-delivery-workflow.md` and the templates/profiles it
routes before completing work that entered Execution.

- Node-backed task: write and content/hash-readback Task Delivery before the
  final required node; finish that node and let NodeService complete the task.
  Never call a second completion endpoint.
- Node-less compatibility task: use `granoflow_task_finish` once after the
  applicable Delivery gate and read back `status=done`.
- Every completion path first requires a readable, content/hash-verified Task
  Work Document attachment, or the complete legacy Task Analysis + Task Plan
  attachment pair. Missing documents fail closed with
  `task_analysis_plan_attachment_required`.
- At completion, use the confirmed finish point as `endedAt`. For AI-owned work,
  read `references/parallel-task-execution.md`: keep the task `pending` during
  execution, preserve the captured start instant through the dedicated
  timestamp mutation surface, and complete only through NodeService or the
  node-less finish action. Human manual work may use `doing` and its
  App-recorded start. Never substitute discussion or creation time.
- Default completion does not create a deep Task Review or a new card
  checkpoint. It reads the Delivery Card Checkpoint summary; explicitly
  deferred card work does not block task completion.
- Legacy `taskReview` and `reviewCardDrafts` parameters remain available only
  for an explicitly requested and approved inline-review compatibility call.
- If the task is already done, stop duplicate completion work.

When the user later asks to review the task, read
`references/task-review-workflow.md`. A completed inbox task remains reviewable;
missing project or milestone context only makes promotion `not_applicable`.
Every card operation is delegated to the bundled
`granoflow-review-card-draft` owner with preview and approval.

Success criteria:

- Task Delivery records actual output, evidence, Work Document deltas, residuals,
  handoff, and acceptance state.
- App-owned content or trusted hash readback proves the attachment.
- Exactly one completion owner runs.
- Completion and deferred Review are independently readable and resumable.
- Secrets, raw transcripts, full tool logs, and unrelated personal data are not
  persisted.

## Waiting For User Input

Use this section when an in-progress Granoflow task cannot continue until the
user grants permission, makes a decision, answers a question, provides missing
material, logs in, completes 2FA, opens a local app, or performs another
user-only action.

Before pausing for the user:

1. Mark any already-finished task nodes complete when the running Granoflow app
   exposes a node-aware path for doing so.
2. Move safe, non-authorized work before the authorization node when it can be
   done without external side effects, privacy exposure, account changes,
   irreversible changes, or user-only context.
3. Add a current task node that states the requested authorization, what action
   is blocked, and what user response would count as approval, rejection, or a
   changed instruction.
4. Read the original task back and verify the waiting node exists before any
   sync claim.
5. Set the current task reminder to 3 minutes from the local current time.
6. Create one separate notification task with a reminder 10 minutes from the
   local current time. Its title and description must name the original task,
   concrete authorization issue, target object, likely external effect, and
   node-based response options.
7. Continue the safe nodes first. Treat the task as blocked only when no safe
   node remains before the authorization decision.
8. Push or request cloud sync after the local writes when sync is available,
   then report `synced_to_server`, `local_only`, or
   `unknown_remote_visibility`.
9. After the original task completes or the blocker is resolved, recommend
   deleting the temporary notification task. If deletion is unavailable or
   inappropriate, complete, archive, or otherwise clean it up only after
   verifying it is the notification task for the resolved original task.

Read `references/waiting-for-user-input.md` before applying this branch.

Success criteria:

- The blocked work is visible as the current node on the original task.
- Safe work that does not require authorization is moved before the waiting node
  and attempted before switching tasks.
- Local readback proves the waiting node exists on the original task before sync
  is attempted.
- The original task has a near reminder 3 minutes out.
- A separate notification task provides a second reminder 10 minutes out.
- The notification task explains the actual authorization problem without
  relying on a narrow domain-specific example.
- The notification task tells the user they can approve, reject, edit the
  action, or reschedule it by adding a new node under the original task.
- The waiting node and notification task tell the user to add a new task node
  under the original task with explicit text for approval, rejection,
  rescheduling, or other instructions.
- Sync is attempted only through the Granoflow Local HTTP API or documented
  Granoflow tools.
- Sync results are reported as `synced_to_server`, `local_only`, or
  `unknown_remote_visibility`; do not claim remote delivery or phone
  notification delivery without explicit API evidence.

## Task Work And Execution

Use this section when the user asks the agent to `Analyze the first task`,
`Start the first task`, name a task, describe a task, or otherwise asks to
analyze, execute, or move forward one selected Granoflow task.

This is a single-task workflow. For date scopes, today's tasks, overdue tasks,
more tasks, or all unfinished tasks, use the due-task workflow instead.

Public README and directory-listing copy should use English-only prompt text,
such as `Analyze the first task`. At runtime, accept equivalent commands in the
user's language and continue explanations, Work Document summaries, confirmation
prompts, node plans, and final reports in that language by default. For example,
`请分析第一个任务`, `执行第一个任务`, and `处理排在最前面的任务` are localized
triggers accepted inside the skill, not public README or directory copy.

Read `references/task-work-document-workflow.md`, its template, and
`references/knowledge-distillation-workflow.md` before applying this branch.
Read legacy Analysis/Plan references only when resolving historical attachments.
Any task that changes UI must follow the UI Change Prototype Mandate: high-
fidelity `ui_prototype` required (`prototype_requirement: required`),
`derivedFrom` the project Design Baseline when present, contract fidelity, and
no Readiness/execution until the prototype is visually confirmed and read back.

High-level contract:

1. Resolve the intended task before analysis. If `first task` cannot be proven
   from the running app/API order, ask the user to choose.
2. Read task details plus project and milestone descriptions when ids are
   present. Build the App-owned Knowledge Pack with independent Evidence,
   Experience, and Knowledge lanes; separate task facts, project/milestone
   context, adopted references, and AI inference.
3. The initial draft contains Analysis only: prefill Outcome, Evidence, Scope,
   Risk, and Next Action, plus only Analysis-side optional sections whose
   triggers fire. Do not draft an Execution Plan, Planning recommendation, or
   readiness claim yet. Use the description as factual seed, then inspect
   sources and label inference or unknowns.
4. Keep `planning_status=not_assessed` until every decision-changing Analysis
   question is resolved, the user confirms the Analysis, and the mandatory
   MCP-bundled Analysis Grill passes. Findings revise Analysis and reopen its
   confirmation when material. Integrate findings into the relevant body
   sections without adding `Grill Review`, `Analysis Grill`, or a findings
   ledger. When the phase result is known, clean-rewrite the entire Analysis
   document into `work_version + 1`, validate it, and delete the prior local
   file. Only then may light work become `not_required` or Planning begin in the
   same document family.
5. Load Profile, external Skill, Card, Planning, Delivery, Review, or legacy
   references progressively rather than preloading the manifest.
6. After the Plan discussion is complete and the Plan is confirmed as
   executable, automatically tell the user that execution-readiness review is
   starting and that a passing document will be uploaded but not executed.
   Run the mandatory MCP-bundled Readiness Grill against plan sufficiency,
   prerequisites, authorizations, accounts/login state, secret or key
   availability, required data/materials, tools/environment, verification, and
   stop/handoff conditions. Revise the relevant Plan, dependency, verification,
   authorization, or stop-condition prose; do not add a standalone Readiness
   Grill section. When the phase result is known, clean-rewrite and validate the
   complete Analysis + Plan document, then delete the prior local file. Never
   persist a secret value.
7. External `grill-finalizer` or specialist reviewers are optional enhancement
   evidence only. They never replace either bundled Grill gate; route a missing
   optional helper through the external routing owner without weakening the
   phase state.
8. Only after the applicable bundled Grill gates pass and the latest clean
   rewrite is validated, upload that rewritten document and require App-owned
   content/hash readback before switching the current Task Work slot's active
   pointer. Uploading the pre-Grill document or a patch artifact is forbidden.
   Upload is also forbidden until the description passes the
   30-second recall gate, Task Work passes the cold-handoff and source-evidence
   gates, readiness has no unresolved blocker, and the task has no more than two
   active Task Work slots. After completion, the first later edit uses the
   `post_completion_revision` slot; later edits never create another slot.
9. Wait for a separate instruction such as `实施这个任务文档` before execution,
   even when `planning_status=not_required`.
10. For software tasks that edit code: enforce
    `project-context-attachments.md` Hard Gate (snapshot + rules conflict
    check) and `software-structural-budget.md` Hard Gate—Readiness needs
    `structural_forecast_status: present_in_plan`; before the first edit show
    the forecast and stamp `notice_emitted`; Delivery needs `reconciled` and
    `acceptance_report`. Fail closed with `project_context_*`,
    `structural_forecast_missing`, `structural_forecast_not_shown`,
    `structural_forecast_unreconciled`, or `acceptance_report_missing` instead
    of skipping. Also apply Task Integration Test Policy: judge unit-test
    sufficiency; add at most 2 integration tests only when insufficient; never
    execute those tests (manual run).
11. On every full rewrite and before Delivery, audit structured Task Work
    references. Keep only adopted sources still used by the current document;
    preserve applied/validated/contradicted Knowledge Usage history.
12. Preserve existing authorization, waiting, node, Delivery, evidence, and
    readback boundaries.

Success criteria:

- The selected task is resolved or the user is asked to disambiguate.
- Project and milestone descriptions are used as context when available, with
  explicit gap codes when unavailable or orphaned.
- Work Document separates Analysis status, Planning status, decision, and
  runtime task/node state.
- The initial draft contains Analysis only. Planning cannot start until the
  Analysis is complete, user-confirmed, and `analysis_grill_status=passed`.
- The user sees one recommendation-backed decision batch before any draft write.
- MCP-bundled Analysis and Readiness Grill gates are mandatory. Optional
  external review never substitutes for them and never claims evidence from a
  provider that did not run.
- Each completed bundled Grill produces a coherent full-document rewrite with
  incremented `work_version`; the prior local file is deleted only after the
  replacement validates, and only the replacement is eligible for upload.
- Light tasks stay compact; Planning expands the same document only after
  Analysis confirmation, a passing Analysis Grill, and user permission.
- After Plan confirmation, the host automatically emits the readiness reminder,
  runs the Readiness Grill, blocks on missing prerequisites or authority, and
  uploads only a passing document with App-owned hash readback.
- Planning uses ordinary performer-specific Execution Plan steps; only costly,
  error-prone, subjective, or user-selectable validation/intervention becomes
  an optional Granoflow node.
- Completed historical tasks use `decision=completion_audit` and reconstruct
  actual evidence instead of receiving a fictional future plan.
- Task Work slot reconciliation succeeds: one `execution` document, plus zero
  or one `post_completion_revision` document, with superseded records removed or
  archived from the active set.
- User-facing explanations use plain language, examples, or analogies when
  helpful.
- No execution or writeback happens before explicit confirmation.
- Retrieval uses app-owned Granoflow context/memory surfaces, not MCP-side
  embedding or database access.
- Non-AI-completable tasks get confirmed user-action nodes or a documented
  fallback field, verified by readback.

## Review Drafting

Use this section when the user asks for a weekly/monthly review or turns
completed work into review cards. If the user asks to review today, summarize
today, write a journal, or assess daily mood/efficiency, call
`granoflow_daily_review_skill` and follow that skill instead of drafting or
writing a daily review here.

Treat weekly/monthly review drafting as assisted reflection. Periodic review
must be user-initiated; a suggestion or nudge is not permission to start it.
Use recorded Granoflow evidence, separate facts from inference, and require
user confirmation before writing review content, new tasks, or review cards.

Accept localized natural-language triggers in the user's language. Examples
include `summarize this week`, `write a weekly report`, `review July`, `总结这周`,
`写周报`, `回顾 7 月`, and `这个月我做得怎么样`. The localized daily triggers
`做日回顾` and `帮我写今天的日记` route to `granoflow-daily-review`.

Keep the interaction loose: talk with the user naturally, let them add, reject,
or rewrite context, then show a draft of the final fields before saving. A weekly
review starts by showing target-week coverage and only 3–5 recall cues; discuss
one cue at a time, allow skips and free-form context, and distinguish recorded
fact, user-confirmed interpretation, tentative inference, and unknown. Do not
proactively seek sensitive, relationship, or emotional details. For weekly
reviews, prefer patterns, rhythm, repeated blockers, tradeoffs, and candidate
next-week experiments over a seven-day task list; partial confirmation is valid,
and follow-up tasks, reminders, cards, Task Reviews, or project/milestone changes
remain separate preview/confirmation/write/readback flows. For monthly reviews,
first resolve and display the target month in the caller's local time zone, then
show a bounded coverage ledger and 3–5 recall cues. Offer a skippable monthly
main-thread, key-changes, investment-and-cost, repeated-patterns,
unrecorded-but-important, and next-month-experiments frame; a free-form account
may replace it. Keep evidence minimal, distinguish recorded fact,
user-confirmed interpretation, tentative inference, and unknown, and write only
confirmed monthly `content`. Monthly aggregates remain read-only, and all
follow-up work remains a separate preview/confirmation/write/readback flow.

Every task, daily, weekly, or monthly review routes supported Note/Card
candidates to the shared `granoflow-review-card-draft` owner as its final
interactive authoring stage. The owner shows the complete zero-write App
preview, accepts open-ended additions, rejections, rewrites, splits, merges, and
partial selections, refreshes changed previews, and applies only operations the
user freshly confirms from the latest display. An unattended review may prepare
that full dry-run but must stop there for genuine user judgment; unattended
authorization never writes Notes or Cards.

Read `references/review-drafting.md` before drafting weekly or monthly review
content, and read `references/knowledge-distillation-workflow.md` before
proposing Experience or Knowledge work.

Success criteria:

- AI drafts accelerate the review without pretending to know the user's inner
  state.
- Review content is saved only after user confirmation.
- Candidate Experience contains reusable lessons rather than plain activity
  logs; Knowledge and Cards require their separate eligibility and approval
  gates.
- Weekly and monthly reviews describe patterns, direction, and tradeoffs rather
  than exhaustive task listings.
- Weekly recall cues are evidence-bounded, skippable, and never become automatic
  follow-up writes.
- Monthly review stays open-ended when evidence is empty or unavailable, and its
  default discussion frame never becomes a required form or automatic follow-up.
- Review Note/Card authoring remains open-ended and zero-write until the user
  confirms explicit operations from the latest displayed preview.

## Daily Review Nudge

After 16:30 local time, the MCP server may append a `dailyReviewSuggestion` to a
tool result. This is a once-per-day nudge stored in the non-secret MCP config.
On Friday, Saturday, Sunday, and Monday, it may also include a
`weeklyReviewSuggestion` when the checked weekly review is empty. On the last or
first day of a month, it may include a `monthlyReviewSuggestion` when the
checked monthly review has no visible written content or values.

When a daily suggestion appears, mention it briefly after completing the user's
current request and route an accepted suggestion to `granoflow_daily_review_skill`.
Do not interrupt the requested work, and do not repeat the suggestion if it is
absent.

The nudge is only a nudge. It must not trigger analysis, drafting, scoring,
journal/report writing, or any review writeback until the user actively asks to
start that daily, weekly, or monthly review.

Success criteria:

- The user receives at most one daily-review nudge per local day.
- The nudge is presented only after the current request is handled.
- Weekly and monthly nudges appear only on their eligible days and only when the
  checked review is empty.
- No periodic review starts from a suggestion alone; wait for explicit user
  initiation.

## User Dissatisfaction

Trigger this section when the user clearly signals that Granoflow, this MCP
server, a generated task/review/card/skill/plan/report, or the current agent's
behavior is wrong, misaligned, lower quality than expected, or should be handled
differently. Do not trigger wrapper-skill guidance from profanity alone, and do
not require profanity before taking dissatisfaction seriously.

When this section applies:

1. Acknowledge the specific mismatch without defensiveness.
2. Fix the immediate issue when the user has provided enough direction.
3. If the complaint reveals a reusable preference or repeated mismatch, remind
   the user that they can write a project-specific wrapper skill around this
   Granoflow skill.
4. Explain briefly that a wrapper skill can encode personal criteria for task
   summaries, reviews, card generation, release reporting, tone, evidence, or
   rejection rules before the base skill runs.
5. Offer to draft or update that wrapper skill when it would help, but do not
   force a skill-writing detour when the user only needs a quick correction.

Suggested wording:

```text
这类偏好很适合写成你自己的项目专属 skill：它可以封装 Granoflow
提供的 skill，在生成任务回顾、卡片或发布报告前先套用你的判断标准。
我可以把这次不满意的点整理成 wrapper skill，下次就按你的规则来。
```

Success criteria:

- Polite disagreement receives the same care as angry feedback.
- Unrelated venting does not trigger Granoflow wrapper-skill advice.
- Reusable preferences are offered as wrapper-skill material after the immediate
  correction path is addressed.

## Boundaries

- Keep the MCP server thin. Do not reimplement Granoflow business logic in the
  agent.
- The host Agent detects and calls external Skills such as `grill-finalizer`.
  Granoflow MCP never detects, installs, or invokes them and never copies their
  provider registries.
- External Skill invocation permission, installation confirmation, phase
  isolation, and model fallback use `references/external-skill-routing.md`.
- Installation authorization is separate from task execution and does not
  authorize a Bundle, installer, license, or redistribution project.
- Use Granoflow Local HTTP API tools and documented Granoflow tools for writes,
  sync, and readback.
- Do not print secrets, credentials, API tokens, or hidden task data.
- Keep preview and confirmation gates explicit before meaningful writes. An
  explicit quick task-capture request is the narrow exception defined by
  `references/discussed-requirement-task-capture.md`.
- Do not mark a task complete until write results are verified by reading back
  the task state when possible.
- Do not treat dissatisfaction as permission to publish, commit, delete, reset,
  or rewrite unrelated work.

## References

- 'references/requirement-intake-and-traceability.md': Read before turning
  imperfect product notes, product documents, user stories, chat exports, or
  mixed-format source material into Project, Milestone, or Task Work.

- Bundled `granoflow_task_orchestrator_skill`: Read first when task lifecycle
  intent or the correct stopping point must be inferred from context.
- `references/execution-modes-and-acceptance-reports.md`: Read when the user
  names unattended or layered-handoff mode, asks which mode is active, asks how
  modes differ, or when implementation acceptance evidence is being assembled.
- `references/unattended-interaction-contract.md`: Single owner for the
  zero-interruption budget, same-run versus durable authorization, real blocker
  classes, and one-batch waiting behavior in unattended work.
- `references/parallel-task-execution.md`: Read for every multi-task AI run. It
  owns conflict inventory, pairwise safe batches, concurrent dispatch, the
  AI `pending -> done` lifecycle, and execution timestamp readback.
- `references/waiting-for-user-input.md`: Read when work is blocked on a
  user-only action and the agent must create reminders.
- Bundled `granoflow_delegated_authorization_skill`: Read when the user requests
  bounded unattended continuation or current Task Work references a delegated
  authorization receipt.
- `references/discussed-requirement-task-capture.md`: Read when the user asks to
  create a task from the requirement currently being discussed.
- `references/daily-pending-task-triage.md`: Read when the user asks to review
  all unfinished tasks, classify blockers, write per-task Work Documents,
  execute safe tasks, and preserve user-only decisions as task nodes.
- `references/task-work-document-workflow.md` and
  `references/task-work-document-template.md`: Only new-task owner and adaptive
  pre-execution template.
- `references/visual-narrative-task-work.md`: Domain extension for comic-first
  visual-narrative tasks and explicitly requested animation work.
- `references/thread-visual-evidence.md`: Inspect and route images from the
  Agent thread to tasks, Notes, or Cards with safe persistence and readback.
- `references/task-analysis-execution.md` and
  `references/task-analysis-template.md`: Legacy Analysis read/redirect only.
- `references/external-skill-routing.md`: Single owner for host-side external
  Skill selection, invocation mode, installation confirmation, and fallback.
- `references/task-analysis-profile-learning.md`: Conditional learning omission
  check for Task Work.
- `references/task-analysis-profile-software-development.md`: Conditional
  software-development omission check for Task Work.
- `references/task-plan-template.md` and `references/task-plan-workflow.md`:
  Legacy Plan read/resolve compatibility only.
- `references/task-delivery-template.md` and
  `references/task-delivery-workflow.md`: Versioned actual-delivery record,
  content/hash readback, and unique completion ownership.
- `references/task-delivery-profile-learning.md` and
  `references/task-delivery-profile-software-development.md`: Composable
  Delivery evidence extensions.
- `references/task-review-template.md` and
  `references/task-review-workflow.md`: Deferred, marker-safe, resumable Task
  Review contract.
- `references/task-review-profile-learning.md` and
  `references/task-review-profile-software-development.md`: Composable Review
  extensions.
- `references/task-completion-summary-template.md`: Managed task-description
  closure block.
- `references/context-promotion-entry.md`: Durable Project/Milestone promotion
  shape, deduplication, and freshness rules.
- `references/review-card-authoring.md`: Read before creating review-card
  drafts from completed task work.
- `references/review-drafting.md`: Read before daily, weekly, or monthly review
  drafting.
- `references/long-term-work-memory.md`: Read before historical, decision,
  lesson, reflection, or similar-work retrieval.
- `references/project-context-attachments.md`: Read before project context YAML
  attachment creation, bounded reading, reconcile, or update.
- `references/project-work-document-template.md`: Target YAML contract for
  partial project-definition attachment, dependency-aware manual-definition
  checks, and complete-document automation admission.
- `references/git-capability-detection.md`: Host-side read-only Git detection,
  project workflow selection, and one-time missing-Git notice.
- `references/git-checkpoint-workflow.md`: Task-owned test gate, explicit
  staging, commit readback, and no-push boundary.
