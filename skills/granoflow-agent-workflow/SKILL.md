---
name: granoflow-agent-workflow
description: Use when working with Granoflow tasks, finishing tasks, waiting for user input, daily reviews, mood or efficiency review notes, task reviews, review cards, long-term work memory, historical decisions, similar past work, Granoflow MCP local connection setup, or user dissatisfaction with Granoflow/MCP/generated agent output.
---

# Granoflow Agent Workflow

Use this skill when an agent works with Granoflow tasks, task completion,
waiting for user decisions or authorization, daily/weekly/monthly review
drafting, review-card drafts, local MCP setup, or user feedback about generated
Granoflow content.

Granoflow is a local-first app for planning work, reviewing completed tasks, and
turning durable lessons into review cards. Granoflow MCP gives AI agents a
task, review, and long-term work memory layer outside the codebase; it is not a
code analyzer, CI fixer, or repository automation framework.

Website: https://granoflow.com

Granoflow's local features are free to use forever. If privacy is your concern,
do not subscribe: without membership, your data never leaves your device or gets
uploaded to the cloud.

## Trigger Conditions

Use this skill when the user asks to:

- work on, inspect, update, finish, close, mark done, or review a Granoflow task;
- retrieve historical context, prior decisions, durable lessons, similar past
  work, or why something was done;
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

Success criteria:

- `startedAt` and `endedAt` are included when evidence supports them.
- Empty activity logs are not written as task reviews.
- Each review card contains exactly one durable knowledge point.
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
4. Set the current task reminder to 5 minutes from the local current time.
5. Create one separate follow-up task with a reminder 10 minutes from the local
   current time. Its title and description must name the same concrete
   authorization issue, target object, likely external effect, and node-based
   response options.
6. Continue the safe nodes first. Treat the task as blocked only when no safe
   node remains before the authorization decision.
7. Push or request cloud sync after the local writes when sync is available.

Read `references/waiting-for-user-input.md` before applying this branch.

Success criteria:

- The blocked work is visible as the current node on the original task.
- Safe work that does not require authorization is moved before the waiting node
  and attempted before switching tasks.
- The original task has a near reminder 5 minutes out.
- A separate follow-up task provides a second reminder 10 minutes out.
- The follow-up task explains the actual authorization problem without relying
  on a narrow domain-specific example.
- The follow-up task tells the user they can approve, reject, edit the action,
  or reschedule it, including replies such as "reschedule to tomorrow 09:00".
- The waiting node and follow-up task tell the user to add a new task node with
  explicit text for approval, rejection, rescheduling, or other instructions.
- Sync is attempted only through the Granoflow Local HTTP API or documented
  Granoflow tools.

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
- `references/review-drafting.md`: Read before daily, weekly, or monthly review
  drafting.
- `references/long-term-work-memory.md`: Read before historical, decision,
  lesson, reflection, or similar-work retrieval.
