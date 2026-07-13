# Discussed Requirement Task Capture

Read this reference when the user asks the agent to create a Granoflow task from
the requirement currently being discussed. Public README and directory-listing
copy should use English prompt text such as:

```text
Create a task from this requirement
```

At runtime, accept equivalent commands in the user's language, including
`把我们讨论的需求建一个任务`, `插入任务`, and `加入任务`.

## Purpose

This is a quick-capture workflow. Preserve enough context for later analysis
without interrupting the user's current work. Do not write an analysis or plan
document, attach files, split nodes, search history, check duplicates, create
cards, or start executing the task unless the user explicitly asks for that
additional work.

## Default Flow

1. Identify the requirement from the active conversation and explicitly
   referenced files, screenshots, issues, pages, or documents.
2. Use placement already known from the current page or conversation, or run at
   most one bounded project/milestone resolve.
3. Bind the task only when exactly one existing project and exactly one active
   milestone under that project are an unambiguous strong match.
4. For every other default placement state, create the task in inbox/default
   placement by omitting both `projectId` and `milestoneId`.
5. Treat the user's explicit task-creation request as confirmation. Call
   `granoflow_task_create_structured` with `dryRun=false`.
6. Use the task id returned by creation to read the task back. Do not resolve the
   newly created task by title. If a supported field was dropped, patch it once
   and read back by id again.
7. Return exactly one success sentence from [Success Reply](#success-reply).

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

## Minimum Description

The description has no mandatory long template. Preserve only the useful facts
already available:

- trigger: why the task is being recorded now or what was observed;
- outcome: what result or change is wanted;
- clues: user-provided files, pages, materials, errors, constraints, or actors;
- completion signal: a known observable result, or `待分析` when useful and
  genuinely unknown.

The task must remain understandable without reopening the chat, retain the
user's important clues, and contain at least the desired outcome or problem. Do
not invent deadlines, acceptance criteria, implementation details, placement,
or user decisions merely to fill a template.

Lightly adapt what is retained without expanding the workflow:

- learning task: learning goal, material, current difficulty, desired ability;
- software-development task: current behavior, expected behavior, repository,
  file, API, or verification clue;
- general task: trigger, outcome, material constraint, completion signal.

Task-profile classification remains an internal writing aid. It does not create
a persisted field, ask the user questions, or trigger full analysis.

## Supported Fields And Safety

Write only supported fields:

- `title`;
- `description`;
- both `projectId` and `milestoneId` only for strong placement;
- `dueAt` or `remindAt` only when explicitly stated or strongly implied;
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

- No analysis or plan document.
- No attachment or task-node creation.
- No review card or task review.
- No historical retrieval or default duplicate search.
- No project, milestone, or tag creation.
- No background scheduling or task execution.
