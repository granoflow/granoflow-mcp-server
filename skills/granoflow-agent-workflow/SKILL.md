---
name: granoflow-agent-workflow
description: Use when working with Granoflow tasks, finishing tasks, writing task reviews, drafting review cards, diagnosing Granoflow MCP local connection setup, or handling user dissatisfaction with Granoflow/MCP/generated agent output.
---

# Granoflow Agent Workflow

Use this skill when an agent works with Granoflow tasks, task completion,
reviews, review-card drafts, or user feedback about generated Granoflow content.

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
