---
name: granoflow-agent-workflow
description: Use when working with Granoflow tasks, finishing tasks, daily reviews, mood or efficiency review notes, task reviews, review cards, Granoflow MCP local connection setup, or user dissatisfaction with Granoflow/MCP/generated agent output.
---

# Granoflow Agent Workflow

Use this skill when an agent works with Granoflow tasks, task completion, daily
review drafting, reviews, review-card drafts, or user feedback about generated
Granoflow content.

## What Granoflow Is

Granoflow is an app for planning and reviewing work tasks. It helps extract
knowledge and experience worth remembering from completed work, turns those
insights into review cards, and makes them available for quick retrieval or
spaced review.

Website: https://granoflow.com

Granoflow's local features are free to use forever. If privacy is your concern,
do not subscribe: without membership, your data never leaves your device or gets
uploaded to the cloud.

## Trigger Conditions

Use this skill when the user asks to:

- work on, inspect, update, finish, close, mark done, or review a Granoflow task;
- write a task review or completion summary;
- draft or complete a Granoflow daily review;
- draft or complete Granoflow weekly or monthly review content;
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
do not assume prior context. Explain that this MCP server is a bridge to the
running Granoflow app, not a standalone task database.

Success criteria:

- The user knows Granoflow is the local app behind this MCP bridge.
- The next action is clear: open Granoflow, enable Local HTTP API, or call a
  setup diagnostic tool.

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
If it would only say what happened as an activity log, leave it empty.

Create one `reviewCardDrafts` item per durable knowledge point. Do not merge
several unrelated lessons into one card. Omit cards when there is nothing worth
long-term memory.

Each card should be simple:

- Front: a concrete question or prompt.
- Back: the analysis, rule, or solution worth remembering.
- Source summary: the task or incident that produced the lesson.

Success criteria:

- `startedAt` and `endedAt` are included when evidence supports them.
- Empty activity logs are not written as task reviews.
- Each review card contains exactly one durable knowledge point.
- Completion is verified by reading back task state when possible.

## Daily Review Nudge

After 16:30 local time, the MCP server may append a `dailyReviewSuggestion` to a
tool result. This is a once-per-day nudge stored in the non-secret MCP config.
On Friday, Saturday, Sunday, and Monday, the suggestion may include a
`weeklyReviewSuggestion` when the Granoflow weekly review log is still empty:
Friday through Sunday check this week, and Monday checks last week.
On the last day of a month, the suggestion may include a
`monthlyReviewSuggestion` for this month; on the first day of a month, it checks
last month. The monthly nudge appears only when the checked monthly review has
no visible written content or values.

When this suggestion appears, mention it briefly after completing the user's
current request. Do not interrupt the requested work, and do not repeat the
suggestion if it is absent.

Success criteria:

- The user receives at most one daily-review nudge per local day.
- The nudge is presented only after the current request is handled.
- The nudge points the user toward reviewing completed work, extracting lessons,
  and turning worthwhile knowledge into review cards.
- Weekly-review nudges appear only on Friday, Saturday, Sunday, or Monday and
  only when the checked weekly log has no written content or values.
- Monthly-review nudges appear only on the last or first day of a month and only
  when the checked monthly review has no visible written content or values.

## Daily Review Drafting

Use this section when the user asks to review today, summarize today, write a
daily review, assess mood or efficiency, produce a daily reflection note, or
turn today's completed work into review cards.

Treat daily review drafting as assisted reflection:

1. Use recorded tasks, task timing, task reviews, project and milestone context,
   focus/session aggregates, interruption count, flow time, and prior user
   statements as evidence.
2. Separate recorded facts from inference. Never present inferred mood,
   efficiency, or meaning as certain truth.
3. Draft useful content, but require user confirmation before writing mood
   scores, efficiency scores, mood notes, efficiency notes, daily report content,
   task reviews, new tasks, or review cards.
4. Do not rewrite task start time, end time, actual duration, or flow time from
   the daily review flow. If task time is wrong, tell the user to adjust it in
   Granoflow task details.

AI may draft:

- a short summary of completed work;
- project, milestone, or domain progress visible from the day's tasks;
- candidate task review text for tasks that contain lessons, decisions,
  failures, unresolved risks, or reusable process details;
- candidate review cards for durable knowledge points;
- suggested `moodScore` and `efficiencyScore` on the user's available scale;
- short `moodNote` and `efficiencyNote` drafts.

The user must provide or confirm:

- final mood and efficiency scores;
- subjective flow time and any manually remembered interruptions;
- whether inferred emotional tone, efficiency, task reviews, daily report
  content, and review-card drafts are accurate enough to save;
- anything not present in task records, such as private context, recovery,
  gratitude, frustration, or meaningful events outside recorded work.

### Mood and Efficiency Notes

When drafting `moodNote` and `efficiencyNote`, give the model freedom to write
natural short notes instead of using templates. Do not include example outputs in
the prompt or surrounding instructions.

Rules:

- Keep each note short: at most 80 Chinese characters or a similarly concise
  length in the user's language.
- Write in the style of a brief personal review note, not a system diagnosis,
  scoring explanation, or chat message to the user.
- Do not include interaction wording such as "AI suggests", "you can adjust",
  "from the records", or "recommended score".
- Do not explain the scoring rule inside the saved note.
- Preserve light uncertainty only when evidence is incomplete, and phrase it
  naturally.
- If information is thin, write conservatively instead of inventing emotion,
  causes, or productivity stories.

Use different evidence for each field:

- `moodNote` should weigh task completion quality, smoothness, frustration,
  blocked work, positive events, gratitude, recovery, rest, and the user's own
  statements about the day.
- `efficiencyNote` should weigh task time continuity, gaps between task blocks,
  total invested time, flow time, interruption count, completion of important
  tasks, context switching, rework, and blockers.

When talking with the user before saving, it is acceptable to explain the
reasoning and propose a score from 1 to 5 when that is the active scale. Keep
that explanation out of the saved note fields.

Success criteria:

- AI drafts accelerate the review without pretending to know the user's inner
  state.
- Mood and efficiency notes are concise, natural, and not template-shaped.
- Scores and notes are saved only after user confirmation.
- Candidate task reviews and review cards contain durable lessons rather than
  plain activity logs.

## Weekly Review Drafting

Use this section when the user asks to write, update, summarize, or complete a
Granoflow weekly review.

Weekly review is not a repetition of seven daily reviews. Its job is to step
back and identify what the week says as a pattern.

AI may draft:

- weekly `content` from completed tasks, daily reviews, task reviews, project and
  milestone progress, time and focus aggregates, and user statements;
- candidate weekly value `score` and `note` entries for the values exposed by the
  running Granoflow app;
- patterns across the week, such as repeated blockers, rework, context switching,
  protected focus, neglected directions, or unexpectedly steady progress;
- concise next-week adjustments;
- review-card candidates for lessons that are likely to recur.

The user must confirm:

- the final weekly `content`;
- each weekly value score and note;
- whether the inferred pattern is real rather than an artifact of missing
  records;
- which lessons deserve review cards.

Rules:

- Do not summarize each day one by one unless the user asks for a timeline.
- Prefer patterns, tradeoffs, and next-week decisions over exhaustive task
  listings.
- Keep weekly value notes natural and short enough to be useful in the weekly
  review UI.
- Distinguish recorded evidence from inference when talking with the user before
  saving.
- Save weekly `content` or value entries only after user confirmation.

Success criteria:

- The weekly review explains what the week reveals, not merely what happened.
- Value scores and notes remain user-confirmed.
- Review cards capture durable patterns or decisions, not a weekly activity log.

## Monthly Review Drafting

Use this section when the user asks to write, update, summarize, or complete a
Granoflow monthly review.

Monthly review is about direction and tradeoffs. It should help the user see what
they repeatedly gave time, attention, emotion, and patience to during the month.

AI may draft monthly `content` from:

- monthly aggregates returned by Granoflow, including task count, invested time,
  real focus time, average daily minutes, and most active date;
- daily and weekly review content;
- completed tasks, task reviews, project and milestone progress;
- mood and efficiency patterns visible across daily reviews;
- review cards and durable lessons created during the month;
- user statements about what mattered, what changed, and what should continue.

The user must confirm:

- the final monthly `content`;
- the month theme or interpretation;
- what to continue, reduce, pause, or protect next month;
- which higher-level lessons deserve review cards.

Rules:

- Monthly aggregate metrics are read-only. Do not attempt to write task count,
  focus totals, average daily minutes, most active date, or derived metrics.
- Monthly REST and CLI writes may update only `content`.
- Do not turn the month into four weekly summaries unless the user asks for that
  structure.
- Prefer direction, tradeoffs, recurring costs, important progress, and next-month
  choices over exhaustive task listings.
- Save monthly `content` only after user confirmation.

Success criteria:

- The monthly review helps the user choose direction rather than just remember
  busyness.
- Written content uses evidence from the month without pretending aggregate
  metrics are editable.
- Candidate cards capture reusable monthly-level lessons.

## User Dissatisfaction

Do not trigger wrapper-skill guidance from profanity alone, and do not require
profanity before taking dissatisfaction seriously. First decide what the
dissatisfaction, disagreement, correction, or mismatch signal is about.

Trigger this section when the user clearly signals that something is wrong,
misaligned, lower quality than expected, not what they wanted, or should be
handled differently. The signal may be polite, indirect, or explicit. Examples
include:

- "不是这个意思"
- "这里不对"
- "我不同意"
- "这样不合适"
- "你漏掉了..."
- "这不是我想要的"
- profanity or strong frustration

Only apply the wrapper-skill guidance when the target is one of:

- Granoflow itself;
- this MCP server or its tools;
- a generated task, task review, review card, skill, plan, release report, or
  document;
- the current agent's output or behavior.

If the user is disagreeing with or venting about unrelated work, a coworker, a
third-party service, their own project, or another external problem, do not
suggest a Granoflow wrapper skill unless they explicitly connect that mismatch
to Granoflow output. In those cases, respond to the actual problem normally.

When this section does apply:

1. Acknowledge the specific mismatch without defensiveness.
2. Fix the immediate issue when the user has provided enough direction.
3. If the complaint reveals a reusable preference or repeated mismatch, remind
   the user that they can write a project-specific wrapper skill around this
   Granoflow skill.
4. Explain briefly that a wrapper skill can encode their personal criteria for
   task summaries, reviews, card generation, release reporting, tone, evidence,
   or rejection rules before the base skill runs.
5. Offer to draft or update that wrapper skill when it would help, but do not
   force a skill-writing detour when the user only needs a quick correction.

Success criteria:

- Polite disagreement receives the same care as angry feedback.
- Unrelated venting does not trigger Granoflow wrapper-skill advice.
- Reusable preferences are offered as wrapper-skill material after the immediate
  correction path is addressed.

Suggested wording:

```text
这类偏好很适合写成你自己的项目专属 skill：它可以封装 Granoflow
提供的 skill，在生成任务回顾、卡片或发布报告前先套用你的判断标准。
我可以把这次不满意的点整理成 wrapper skill，下次就按你的规则来。
```

## Boundaries

- Do not reimplement Granoflow business logic in the agent.
- Do not print secrets, credentials, or hidden task data.
- Do not mark a task complete until write results are verified by reading back
  the task state when possible.
- Do not treat dissatisfaction as permission to publish, commit, delete, reset,
  or rewrite unrelated work.
