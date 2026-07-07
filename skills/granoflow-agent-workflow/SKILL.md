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
- create a task from the requirement currently being discussed, such as
  `Create a task from this requirement`;
- process today's tasks, tasks for another user-specified date or range, more
  tasks, all unfinished Granoflow tasks, or the older pending-task triage flow;
  decide which are actionable, blocked, obsolete, already done, conflicting, or
  user-only, then plan and run the work the agent can safely complete;
- retrieve historical context, prior decisions, durable lessons, similar past
  work, or why something was done;
- maintain project or milestone descriptions as current work-memory context, or
  archive milestone context as a final snapshot;
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
in the user's language. This workflow captures a lower-priority requirement as a
Granoflow task. It is not a plan-writing, attachment, execution, or card-creation
workflow.

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
2. Inspect existing projects and active milestones.
3. If an existing project and active milestone are a strong match, create the
   task directly. The user's explicit task-creation request is confirmation for
   that task write.
4. If no clear project or milestone fits, decide whether the task is temporary
   or worth preserving.
5. Create temporary tasks in inbox/default placement without inventing structure.
   When no explicit inbox field exists, omit `projectId` and `milestoneId`.
6. For worth-preserving tasks with no clear home, suggest the project/milestone
   structure and wait for user confirmation before assigning or creating it.
7. Keep the description compact but useful enough to reopen later.
8. Read the task back. If supported fields such as `description`, `projectId`,
   or `milestoneId` were dropped by create, patch them and read back again.

Success criteria:

- No plan document or attachment is required for this workflow.
- Strong placement uses only existing active milestones, never archived, done,
  trashed, deleted, stale, or merely thematic milestones.
- Task creation alone does not execute the task, create cards, create
  project/milestone structure, or authorize secrets, publishing, deletion,
  payment, sending, account changes, or subjective decisions.
- The final report states the task id or visible reference and whether it was
  placed in a project, milestone, or inbox/default location.

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
6. For executable work, write a plan document, run a grill/adversarial review
   pass, revise the plan, then execute only the confirmed safe portion.
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
- Final analysis and plan documents are attached when supported, or honestly
  linked with a recorded tool gap.
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
current context map for future agents.

High-level contract:

1. Read `granoflow_ai_agent_tools` and prefer context-steward tools when the
   running app and MCP server expose them.
2. Use `granoflow_context_steward_status` to inspect current project,
   active milestone, archived milestone, and policy state.
3. Use `granoflow_project_context_update` for project descriptions. Keep them
   focused on current state, scope, decisions, risks, key docs/APIs, active
   milestones, last verification, and next expected work.
4. Use `granoflow_milestone_context_update` only for active milestones. Archived
   milestone descriptions are final snapshots for ordinary MCP workflow.
5. Use `granoflow_milestone_context_archive` to preview archive closure before
   any write. The preview must include both final milestone state and parent
   project description update.
6. If MCP is unavailable, do not block unrelated user work. Report that context
   upkeep was skipped or blocked.

Success criteria:

- Project descriptions remain the current global map.
- Active milestone descriptions remain the current phase map.
- Archived milestone descriptions are not modified through ordinary MCP
  workflow.
- Archive closure always considers the parent project description update.
- Secrets, tokens, OTPs, private auth URLs, and raw local private content are
  never written into descriptions.

## Completing Tasks

When the user asks to complete, finish, close, mark done, wrap up, or otherwise
end a task, prefer `granoflow_task_finish` over `granoflow_task_complete`.

Before writing completion data:

1. Infer `startedAt` from the current agent conversation when there is evidence.
2. Infer `endedAt` from the current agent conversation or current completion
   moment.
3. Decide whether there is anything genuinely worth reviewing.
4. Decide whether any durable knowledge points should become review cards.

Write `taskReview` only when it contains a meaningful decision, lesson, failure
mode, evidence trail, reusable process detail, or important unresolved risk.
Create one `reviewCardDrafts` item per durable knowledge point. Omit reviews and
cards when they would only be an activity log.

Read `references/review-card-authoring.md` before creating review cards from a
task. It defines card-worthiness, experience cards, language-learning cards,
source preservation, self-review, note fields, and fallback behavior.

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

## Review Drafting

Use this section when the user asks to review today, summarize today, write a
daily/weekly/monthly review, assess mood or efficiency, or turn completed work
into review cards.

Treat review drafting as assisted reflection. Use recorded Granoflow evidence,
separate facts from inference, and require user confirmation before writing
subjective scores, notes, review content, task reviews, new tasks, or review
cards.

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

Success criteria:

- The user receives at most one daily-review nudge per local day.
- The nudge is presented only after the current request is handled.
- Weekly and monthly nudges appear only on their eligible days and only when the
  checked review is empty.

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
- Keep preview and confirmation gates explicit before meaningful writes.
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
- `references/review-card-authoring.md`: Read before creating review-card
  drafts from completed task work.
- `references/review-drafting.md`: Read before daily, weekly, or monthly review
  drafting.
- `references/long-term-work-memory.md`: Read before historical, decision,
  lesson, reflection, or similar-work retrieval.
