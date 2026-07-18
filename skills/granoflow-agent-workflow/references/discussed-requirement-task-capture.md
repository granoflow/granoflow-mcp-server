# Discussed Requirement Task Capture

Read this reference when the user asks the agent to create a Granoflow task from
the requirement currently being discussed. Public README and directory-listing
copy should use English prompt text such as:

```text
Create a task from this requirement
```

At runtime, accept equivalent commands in the user's language, including
`把我们讨论的需求建一个任务`, `插入任务`, and `加入任务`.

Read `granoflow-agent-workflow/task-authoring-quality-contract` first. Its
title, plain-language, analogy, example, and change-evidence rules are mandatory
for this quick path too.

## Purpose

This is a quick-capture workflow. Preserve enough context for later analysis
without interrupting the user's current work. Do not write an analysis or plan
document, attach files, split nodes, search history, check duplicates, create
cards, or start executing the task unless the user explicitly asks for that
additional work.

## Title Standard

The title is the Todo-level next action, not a miniature analysis or document
label. Prefer this shape:

> action verb + clear object or outcome + necessary qualifier

Titles should be concise, specific, and understandable when shown without a
description. Start with an action verb whenever the task represents work to be
done. Do not make `Plan文档`、`分析任务`、`实施计划` or a filename the main title;
describe the action instead. Put rationale, context, prerequisites, estimates,
theory, prior experience, and detailed acceptance in the description or Task
Work attachment.

The title must also communicate the user-facing problem, consequence, or
desired result. An internal implementation phrase or architecture term may be
included only as a qualifier after that meaning is clear; it must not be the
whole title. For example, prefer `修复长请求被固定上限提前截断的问题`
over `实现分层超时与移除静态 agent 限制`. The description must then explain
the concrete failure, the technical cause, the intended behavior change, and
the evidence that will show the user-visible problem is resolved.

The task description is the user-facing factual summary and the first source
for the later Task Work Document. When Task Work is requested, the Agent may
reorganize and expand confirmed description content into execution details, but
must preserve its facts and boundaries. A title, filename, path, or “已完成”
label alone is only a lead; it is not enough evidence to invent a failure
scenario, implementation detail, or acceptance result.

Examples:

- `制定漫画任务模型并隔离项目风格偏好`
- `评审 Task Delivery 工作流`
- `提供 DEK 同步恢复的复现信息或测试授权`

## Default Flow

1. Identify the requirement from the active conversation and explicitly
   referenced files, screenshots, issues, pages, or documents.
2. Derive a concise action-oriented title using the Title Standard; keep
   document type, filename, and detailed rationale out of the title.
3. Use placement already known from the current page or conversation, or run at
   most one bounded project/milestone resolve.
4. Bind the task only when exactly one existing project and exactly one active
   milestone under that project are an unambiguous strong match.
5. For every other default placement state, create the task in inbox/default
   placement by omitting both `projectId` and `milestoneId`.
6. Build `authoringEvidence` from exact, different analogy and example excerpts
   in the description. Treat the user's explicit task-creation request as
   confirmation. Call `granoflow_task_create_structured` with `dryRun=false`,
   omit all historical physical fields, and leave the task `pending`.
7. Use the task id returned by creation to read the task back. Do not resolve the
   newly created task by title. If a supported field was dropped, patch it once
   and read back by id again.
8. Return exactly one success sentence from [Success Reply](#success-reply).

Ordinary capture never writes `createdAt`, `updatedAt`, `startedAt`, `endedAt`,
or `deletedAt`. Discussion is not execution. After Analysis/Plan readiness and
separate execution authorization, start current work by updating the task to
`status=doing`; the App records `startedAt` at that transition. Use
`granoflow_task_history_mutate` only when correcting genuine historical facts,
not as a retry path for current-task capture.

Do not ask the user to choose a project or milestone in the default quick path.
Do not create, restore, reopen, or rename project structure during capture.

## Placement Matrix

| State                                                                              | Default placement                      |
| ---------------------------------------------------------------------------------- | -------------------------------------- |
| One existing project plus one active milestone under it are a strong match         | Bind both ids                          |
| Only the project is clear                                                          | Inbox/default                          |
| Only a milestone is clear, or its project cannot be proven                         | Inbox/default                          |
| Multiple projects or milestones may match                                          | Inbox/default                          |
| Candidate milestone is done, archived, trashed, deleted, stale, or merely thematic | Inbox/default                          |
| Placement requires new, restored, or reopened structure                            | Inbox/default; do not mutate structure |

If the user explicitly names a project or milestone that is missing or
ambiguous, leave the quick path and report the placement problem briefly. That
explicit placement request is not permission to invent structure.

When the running app advertises a first-class inbox field, prefer the app-owned
field. Otherwise inbox/default means omitting both `projectId` and
`milestoneId`.

## Mandatory Description Standard

### Description Job: 30-Second Recall

The description is not the execution manual. Its job is to let the user look at
the task later and recover, within about 30 seconds:

- what actually happened or may happen;
- who or what is affected;
- what result the task seeks or achieved; and
- what observable evidence would count as success.

The later Task Work Document may repeat the minimum facts needed for a
standalone handoff, but it must expand them into execution detail rather than
paraphrasing this description.

The problem portion must be concrete enough to stand alone. It must name at
least one observed failure, confusing behavior, user-visible consequence, or
plausible risk scenario that the task is meant to address. Do not substitute
vague phrases such as “相关目标”, “已有实现”, “关联文档”, “整理流程”, or
“缺少统一记录” unless the description immediately explains what actually
failed, who is affected, and under what circumstances. The solution must state
the intended behavior change, and the acceptance condition must name the
observable evidence that distinguishes success from the original failure.

Every description must include one real analogy. Every description must include at least one concrete example
of the real or plausible situation being addressed. The example should say what the user,
agent, system, or other affected party encounters and why that encounter is a
problem; for example, “用户只看到‘实现分层超时’，无法知道哪个请求会被截断，
也无法判断修复是否生效” is useful, while “完善相关目标” is not. When the
solution involves a meaningful choice, trade-off, or scope boundary, add one or
more examples explaining why this approach is reasonable and why the boundary
belongs here. These examples are part of the task's recall evidence, not
decorative anecdotes. If no meaningful choice or boundary exists, do not invent
a rationale paragraph.

Write each distinct problem as its own natural-language paragraph with a blank
line before the proposed solution. Do not compress several problems into one
comma-separated sentence. When the relationships, alternatives, or failure
paths are difficult to explain linearly, a small Markdown table, flowchart, or
Mermaid diagram may follow the problem paragraph; it supplements the prose and
does not replace it.

Use Markdown semantics to make the prose scannable: **bold** the decisive
problem, intended outcome, or acceptance result; use _italics_ for constraints,
caveats, uncertainty, or conditional advice; use inline code such as
`npm run check`, `startedAt`, API paths, field names, commands, and file paths
for literal technical values; use fenced code blocks for multi-line commands,
configuration, logs, or code. Use headings, lists, tables, blockquotes, and
Mermaid diagrams when they clarify structure or evidence. Formatting must
carry meaning and must not replace a complete natural-language explanation.

Every task description must be a fluent, readable piece of task copy, not a
questionnaire or a list of the five questions. The prose must clearly answer
the five core dimensions: the problem, the proposed solution, prerequisites and
current readiness, focused-work estimate with basis and uncertainty, and the
observable acceptance condition.

The five dimensions are an internal writing contract. Do not expose the question
wording or mandatory numbered headings in the persisted description. Write
`待分析` only where the conversation lacks enough evidence; never invent facts
merely to make the prose sound complete. Use a time range when precision is not
justified, distinguish focused work from elapsed calendar time, and state why
the prerequisites are or are not ready.

Cover unknown dimensions with one short, factual sentence that names the missing
information and when it must be resolved. Do not fill them with generic prose
about “reading related documents”, “clarifying boundaries”, or “recording
evidence”. Quick capture remains quick: it records confirmed facts plus explicit
unknowns and does not perform the later Analysis.

When useful for decision quality, the prose may also explain why the task is
worth doing, why the chosen approach is reasonable, its theoretical or
evidence-based basis, and relevant prior experience. These are optional: omit
them when they do not change understanding, execution, or acceptance.

For completed historical tasks, use `历史工时未知` when no reliable focused-work
record exists. Do not infer actual work time from calendar duration.

Lightly adapt what is retained without expanding the workflow:

- learning task: learning goal, material, current difficulty, desired ability;
- software-development task: current behavior, expected behavior, repository,
  file, API, or verification clue;
- general task: problem, proposed solution, prerequisites and readiness,
  focused-work estimate with basis and uncertainty, acceptance condition.

Task-profile classification remains an internal writing aid. It does not create
a persisted field, ask the user questions, or trigger full analysis.

## Deadline Selection For Milestone Tasks

A task placed in a milestone must have `dueAt`. Read the selected milestone's
deadline before writing, then preserve an explicit user date or infer the most
appropriate date from the conversation. The usual choices are today for urgent
or already-started work, tomorrow for a near-term next action without same-day
urgency, and the milestone deadline when no earlier signal exists or the task is
itself a milestone deliverable. Strong context may justify another date.

Use the caller's local end of day for a date-only inference. Do not assign every
task the same default, do not place a task after the milestone deadline, and do
not silently clamp an explicit conflicting date. If the milestone deadline is
missing, invalid, already passed, or earlier than the user's requested task
date, leave the quick path and report the conflict so the user can change the
task date, milestone deadline, or placement.

## Pre-Write Recall Gate

Before writing, apply the 30-second recall test using only the proposed title and
description. Fail and revise when a reader cannot identify the concrete problem
or event, its impact, the intended or actual result, and the acceptance signal
without opening the thread or attachment.

The following fail the gate:

- a title made primarily from an architecture term, plan label, or filename;
- a description that merely restates the title;
- generic workflow prose that could be pasted onto another task unchanged;
- unexplained professional terminology that hides the user-visible problem;
- Markdown emphasis or tables that decorate an otherwise vague statement.

When a professional term is necessary, explain it in plain language on first
use. Markdown is optional and semantic: emphasize only genuinely important text.
Do not require bold, italics, tables, diagrams, or code blocks when plain prose
is clearer.

## Supported Fields And Safety

Write only supported fields:

- `title`;
- `description`;
- both `projectId` and `milestoneId` only for strong placement;
- `dueAt` for every milestone-bound task, selected by the deadline rules above;
- `dueAt` or `remindAt` for an inbox task only when explicitly stated or
  strongly implied;
- existing catalog tags only when the user supplied them or the surrounding
  workflow already established them.

Never include secret values, OTPs, recovery codes, auth URLs, passwords, tokens,
or hidden chain-of-thought. Task capture never authorizes publishing, payment,
login, external messages, deletion, account changes, or task execution.

## Readback

After creation, read back by returned task id and verify:

- the task exists;
- title and description are present;
- status is appropriate;
- both placement ids match when strong placement was written;
- due, reminder, or existing tags match when supplied;
- no secret value was persisted.
- the read-back title and description still pass the 30-second recall test.

If creation returns no usable task id, readback fails, or a dropped supported
field still cannot be patched, report failure. Do not use a success sentence.

## Success Reply

For strong project and milestone placement, return exactly:

```text
任务已经放入「<项目名>」项目「<里程碑名>」里程碑。
```

For inbox/default placement, return exactly:

```text
任务已收录到收集箱。
```

Do not append a title, task id, description, explanation, suggestion, question,
or next step unless the user explicitly requested more output.

## Exit The Quick Path

Use the corresponding full workflow when the user asks to:

- analyze, plan, attach files, or split nodes during capture;
- execute or complete the new task;
- search for or merge duplicates;
- preview a full description or receive a detailed report;
- place the task into missing, ambiguous, or new project structure.

## Non-Goals

- No Task Work Document.
- No attachment or task-node creation.
- No review card or task review.
- No historical retrieval or default duplicate search.
- No project, milestone, or tag creation.
- No background scheduling or task execution.
