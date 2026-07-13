---
name: granoflow-agent-workflow
description: Use when working with Granoflow tasks, finishing tasks, waiting for user input, daily reviews, mood or efficiency review notes, task reviews, review cards, long-term work memory, historical decisions, similar past work, Granoflow MCP local connection setup, or user dissatisfaction with Granoflow/MCP/generated agent output.
---

# Granoflow Agent Workflow

Use this skill when an agent works with Granoflow tasks, task completion,
waiting for user decisions or authorization, daily/weekly/monthly review
drafting, review-card drafts, long-term work memory retrieval, local MCP setup,
or user feedback about generated Granoflow content.

Granoflow is a local-first app for planning work, reviewing completed tasks, and
turning durable lessons into review cards. Granoflow MCP connects MCP-capable AI
agents to a local task, review, and long-term work memory layer; it is not a code
analyzer, CI fixer, or repository automation framework.

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
- draft or complete Granoflow daily, weekly, or monthly review content;
- suggest daily review mood or efficiency scores and short notes;
- create review cards from task work;
- diagnose why Granoflow MCP cannot connect to the local app;
- correct, reject, or complain about Granoflow-related generated tasks, reviews,
  cards, plans, MCP behavior, skills, or other agent output.

## Connection First

If the Local HTTP API is unreachable, tell the user briefly what Granoflow is,
link to https://granoflow.com, and explain that the local app must be open with
the Local HTTP API enabled before MCP tools can read or write tasks.

If the user seems to have installed the MCP server without knowing Granoflow,
explain that this MCP server is a bridge to the running Granoflow app, not a
standalone task database or a coding-agent capability booster.

Success criteria:

- The user knows Granoflow is the local app behind this MCP bridge.
- The next action is clear: open Granoflow, enable Local HTTP API, or call a
  setup diagnostic tool.

## Discussed Requirement Task Capture

Use this section when the user asks the agent to `Create a task from this
requirement`, `Create a task from what we discussed`, or an equivalent command
in the user's language. This workflow quickly captures a requirement as a
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
2. Use already-known placement or at most one bounded project/milestone resolve.
3. Bind only when one existing project and one active milestone under that
   project are an unambiguous strong match.
4. Otherwise create the task in inbox/default placement without asking about
   structure. When no explicit inbox field exists, omit both `projectId` and
   `milestoneId`.
5. Keep the description compact: preserve the trigger, desired outcome, and
   user-provided clues needed for later analysis without writing the analysis.
6. The user's explicit task-creation request confirms this write. Skip dry-run,
   planning, nodes, cards, history retrieval, and duplicate search by default.
7. Read back by the task id returned from creation. Patch dropped supported
   fields once, then read back again.
8. On success, reply with exactly one placement sentence defined by the focused
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
blockers, writes and grills analysis/planning documents, executes confirmed safe
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
3. Write an analysis document before execution. Classify every scoped task as
   AI can do now, needs user authorization or input, or user must do, with
   secondary flags for secrets, logins, files, account actions, stale work,
   conflicts, and tool gaps.
4. Grill and revise the analysis before showing it as final.
5. Show the analysis and require user confirmation before moving into
   execution unless the user's instruction explicitly pre-authorizes that exact
   step.
6. For executable work, read `references/task-plan-workflow.md`, write and
   grill the Plan, then execute only after confirmation. That owner reference
   defines immutable Plan attachments, deliverable nodes, handoffs,
   cross-device reconciliation, manual acceptance, and node-driven completion.
7. Attach or safely link the final analysis and plan documents, then update the
   relevant task descriptions with plain-language explanations.
8. For blockers, use the waiting-for-user-input workflow: add a current node on
   the original task, verify local readback, set a 3-minute reminder on the
   original task, create a separate notification task with a 10-minute reminder,
   tell the user to respond by adding a new explicit node under the original
   task, attempt sync when available, and report sync visibility honestly.
9. Write completion evidence back to the document and Granoflow. Finish only
   tasks that are actually done and verified.

Success criteria:

- Every scoped task appears exactly once in the analysis ledger.
- The default scope is unfinished tasks due today, while explicit dates, ranges,
  more-task scopes, and all-task scopes are honored when the user asks.
- Authorization, login, secret, payment, destructive, external-account,
  missing-information, and user-only blockers are visible before execution.
- Analysis and execution plan documents have passed grill review and been
  revised before safe work starts.
- Final analysis and immutable versioned Plan documents are attached and read
  back when supported, or honestly linked with a recorded upload failure.
- Every Plan node has a deliverable standard and downstream startup contract;
  manual acceptance never blocks later safe execution.
- Granoflow's latest task/node state wins over Agent caches, and NodeService is
  the only parent-task completion path.
- Task descriptions explain the result in the user's language with simple,
  non-jargony wording.
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
7. If YAML content conflicts with project facts, project descriptions, long-term
   rules, or public wording, return a proposal/conflict report instead of
   silently overwriting the rules or wording. Low-risk factual snapshot deltas
   may be reconciled automatically.
8. If MCP is unavailable, do not block unrelated user work. Report that context
   upkeep was skipped or blocked.

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

When the user asks to complete, finish, close, mark done, wrap up, or otherwise
end a task, prefer `granoflow_task_finish` over `granoflow_task_complete`.

Before writing completion data:

1. Infer `startedAt` from the current agent conversation when there is evidence.
2. Infer `endedAt` from the current agent conversation or current completion
   moment.
3. Decide whether there is anything genuinely worth reviewing.
4. Decide whether any durable knowledge points should become review cards.

For tasks the agent has executed or directly helped complete, a factual
`taskReview` may be written automatically when it contains a meaningful
decision, lesson, failure mode, evidence trail, reusable process detail,
verification result, blocker, or important unresolved risk. Keep this automatic
review factual: what was done, key decisions, blockers, verification, and what
would help next time. Do not write inferred mood, personality, motivation,
efficiency, or other subjective judgments into automatic task reviews.

Delegate every review-card search, draft, link, update, preview, confirmation, and write to the bundled `granoflow-review-card-draft` skill. Omit cards when they would only be an activity log.

Automatic task completion review does not change the daily-review synthesis
confirmation gate. Daily review AI imports that update task titles,
`task_review`, daily report content, or planned tasks still require the
app/user confirmation path defined by the review-journal workflow.

After writing meaningful task review content, maintain current project context
when project context tools are available: low-risk factual deltas may update
`project_snapshot.yaml`, while `project_rules.yaml`, public wording, or
positioning conflicts must produce a proposal or conflict report instead of a
silent overwrite.

Load `granoflow-review-card-draft` before any card operation. The local review-card reference is a delegation pointer and legacy background only.

Success criteria:

- `startedAt` and `endedAt` are included when evidence supports them.
- Empty activity logs are not written as task reviews.
- Each review card contains exactly one durable knowledge point.
- Review cards preserve source context when available and omit secrets,
  credentials, private identifiers, and temporary log content.
- Completion is verified by reading back task state when possible.

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

## Task Analysis And Execution

Use this section when the user asks the agent to `Analyze the first task`,
`Start the first task`, name a task, describe a task, or otherwise asks to
analyze, execute, or move forward one selected Granoflow task.

This is a single-task workflow. For date scopes, today's tasks, overdue tasks,
more tasks, or all unfinished tasks, use the due-task workflow instead.

Public README and directory-listing copy should use English-only prompt text,
such as `Analyze the first task`. At runtime, accept equivalent commands in the
user's language and continue explanations, plan summaries, confirmation
prompts, node plans, and final reports in that language by default. For example,
`请分析第一个任务`, `执行第一个任务`, and `处理排在最前面的任务` are localized
triggers accepted inside the skill, not public README or directory copy.

Read `references/task-analysis-execution.md` before applying this branch.

High-level contract:

1. Resolve the intended task before analysis. If `first task` cannot be proven
   from the running app/API order, ask the user to choose.
2. Read task details plus project and milestone descriptions when ids are
   present. Separate task facts, project/milestone context, and AI inference.
3. Prefill Trigger, Outcome, Evidence, Context, Boundaries, Risks, and Decision,
   then present every unresolved directional question once with an AI
   recommendation.
4. Write nothing until the user authorizes the analysis draft. The authorization
   may start Grill but never authorizes planning or execution.
5. Write the base analysis plus a thin general, learning, or software profile;
   preserve the original description and use capability-aware attachment
   fallback.
6. Grill the draft with the bundled protocol or optional installed enhancement.
   Apply accepted findings to the main analysis and stop ordinary Grill after at
   most two rounds.
7. Show the proposed final decision and readiness, then require
   `确认分析终稿` before setting the analysis final.
8. Ask whether to plan only when the confirmed analysis has
   `decision=proceed` and `planning_readiness=yes`.
9. Planning and execution consume the analysis final and retain existing user
   authorization, waiting, node, evidence, and readback boundaries.

Success criteria:

- The selected task is resolved or the user is asked to disambiguate.
- Project and milestone descriptions are used as context when available, with
  explicit gap codes when unavailable or orphaned.
- Analysis separates lifecycle status, decision, and planning readiness.
- The user sees one recommendation-backed decision batch before any draft write.
- A bundled Grill works without third-party skills, and accepted findings revise
  the analysis body.
- Plans consume a user-confirmed analysis final and still pass plan Grill before
  execution confirmation.
- User-facing explanations use plain language, examples, or analogies when
  helpful.
- No execution or writeback happens before explicit confirmation.
- Retrieval uses app-owned Granoflow context/memory surfaces, not MCP-side
  embedding or database access.
- Non-AI-completable tasks get confirmed user-action nodes or a documented
  fallback field, verified by readback.

## Review Drafting

Use this section when the user asks to review today, summarize today, write a
daily/weekly/monthly review, assess mood or efficiency, or turn completed work
into review cards.

Treat review drafting as assisted reflection. Periodic daily, weekly, and
monthly review must be user-initiated; a suggestion or nudge is not permission
to start the review. Use recorded Granoflow evidence, separate facts from
inference, and require user confirmation before writing subjective scores,
notes, daily/weekly/monthly review content, new tasks, or review cards.

Accept localized natural-language triggers in the user's language. Examples
include `review today`, `write today's journal`, `summarize this week`,
`write a weekly report`, `review July`, `做日回顾`, `帮我写今天的日记`,
`总结这周`, `写周报`, `回顾 7 月`, and `这个月我做得怎么样`.

Keep the interaction loose: talk with the user naturally, let them add, reject,
or rewrite context, then show a draft of the final fields before saving. For
daily reviews this includes mood score, efficiency score, one-sentence summary,
and journal/report content when available. For weekly reviews, prefer patterns,
rhythm, repeated blockers, tradeoffs, and next-week adjustments over a seven-day
task list. For monthly reviews, prefer direction, tradeoffs, investment
structure, and next-month choices over four weekly summaries.

Read `references/review-drafting.md` before drafting daily, weekly, or monthly
review content.

Success criteria:

- AI drafts accelerate the review without pretending to know the user's inner
  state.
- Scores, notes, and review content are saved only after user confirmation.
- Candidate reviews and review cards contain durable lessons rather than plain
  activity logs.
- Weekly and monthly reviews describe patterns, direction, and tradeoffs rather
  than exhaustive task listings.

## Daily Review Nudge

After 16:30 local time, the MCP server may append a `dailyReviewSuggestion` to a
tool result. This is a once-per-day nudge stored in the non-secret MCP config.
On Friday, Saturday, Sunday, and Monday, it may also include a
`weeklyReviewSuggestion` when the checked weekly review is empty. On the last or
first day of a month, it may include a `monthlyReviewSuggestion` when the
checked monthly review has no visible written content or values.

When this suggestion appears, mention it briefly after completing the user's
current request. Do not interrupt the requested work, and do not repeat the
suggestion if it is absent.

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

- `references/waiting-for-user-input.md`: Read when work is blocked on a
  user-only action and the agent must create reminders.
- `references/discussed-requirement-task-capture.md`: Read when the user asks to
  create a task from the requirement currently being discussed.
- `references/daily-pending-task-triage.md`: Read when the user asks to review
  all unfinished tasks, classify blockers, write analysis/plans, adversarially review the plan,
  execute safe tasks, and preserve user-only decisions as task nodes.
- `references/task-analysis-execution.md`: Read when the user asks to analyze,
  start, execute, or move forward one selected Granoflow task.
- `references/task-analysis-template.md`: Single base template for all task
  analyses.
- `references/task-analysis-profile-learning.md`: Thin section-8 profile for
  learning tasks.
- `references/task-analysis-profile-software-development.md`: Thin section-8
  profile for software-development tasks.
- `references/review-card-authoring.md`: Read before creating review-card
  drafts from completed task work.
- `references/review-drafting.md`: Read before daily, weekly, or monthly review
  drafting.
- `references/long-term-work-memory.md`: Read before historical, decision,
  lesson, reflection, or similar-work retrieval.
- `references/project-context-attachments.md`: Read before project context YAML
  attachment creation, bounded reading, reconcile, or update.
