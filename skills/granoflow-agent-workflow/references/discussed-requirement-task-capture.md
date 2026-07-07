# Discussed Requirement Task Capture

Read this reference when the user asks the agent to create a Granoflow task from
the requirement currently being discussed. Public README and directory-listing
copy should use English prompt text such as `Create a task from this
requirement`. At runtime, accept equivalent commands in the user's language. For
example, `把我们讨论的需求建一个任务` is a localized trigger accepted inside
the skill, not public README or directory copy.

Public prompt:

```text
Create a task from this requirement
```

This workflow is for quick capture. Do not write a plan document, attach a plan,
create review cards, or start executing the task.

## Contract

1. Identify the requirement from the active conversation and any explicitly
   referenced task, file, screenshot, issue, or document.
2. Inspect existing projects and active milestones before writing.
3. If an existing project and active milestone are a strong match, create the
   task directly. The user's explicit task-creation request is confirmation for
   that task write.
4. If the project is clear but the milestone is weak or absent, use project-only
   or default placement when supported. Ask before assigning to a weak milestone
   or creating a new milestone.
5. If no project or milestone clearly fits, classify the task as temporary or
   worth preserving.
6. Create temporary tasks in inbox/default placement without inventing project
   structure.
7. For worth-preserving tasks with no clear home, suggest a project/milestone
   structure and wait for user confirmation before assigning or creating that
   structure.
8. Read the created task back. If supported fields were dropped by create, patch
   the missing fields and read back again.

## Placement Strength

Use `strong` only when the requirement clearly belongs to an existing project and
an active milestone under that project.

Do not treat a milestone as strong when it is done, archived, trashed, deleted,
stale, or only thematically similar.

Use `medium` when the project is clear but the milestone is weak or absent. If
the app/API has no project-only placement, ask before using a weak milestone.

Use `weak` when no project or milestone clearly owns the task.

## Inbox Or Default Placement

When the app/API has no explicit inbox field, create an inbox/default task by
omitting `projectId` and `milestoneId`. If the running app later advertises a
first-class inbox/default placement field, use the app-owned field instead.

## Temporary Versus Worth Preserving

Temporary tasks include:

- one-off reminders;
- short-lived cleanup;
- scratch notes;
- low future value after completion;
- no durable project, product, customer, release, research, or learning context.

Worth-preserving tasks include requirements that affect:

- a product, API, schema, skill, manual, release, or user workflow;
- future context for another agent;
- a decision, design issue, or known capability gap;
- an ongoing workstream whose exact project/milestone is unclear;
- acceptance evidence that should survive beyond the chat.

## Description Shape

Write a compact task description, not a full implementation plan. For product,
API, skill, or docs work, prefer:

```text
背景:
- ...

目标:
- ...

验收证据:
- ...

注意:
- ...

简单描述:
- ...
```

Use fewer sections for small temporary tasks.

Do not include hidden chain-of-thought, invented deadlines, secret values, OTPs,
recovery codes, auth URLs, private tokens, or private credentials. Secret names
such as `OPENAI_API_KEY` may be named when they are needed, but secret values
must not be written into tasks.

## Create And Readback

Use documented Granoflow MCP tools or Local HTTP API paths. Write only supported
fields:

- `title`
- `description`
- `projectId` when placement is strong or confirmed
- `milestoneId` when placement is strong or confirmed
- `dueAt` or `remindAt` only when stated or strongly implied
- `status` when supported

After creating, read back and verify:

- task id;
- title;
- description presence;
- status;
- due/reminder values if written;
- project and milestone placement if written;
- no secret value was persisted.

If `description`, `projectId`, `milestoneId`, or another supported field was
dropped by create, patch the missing field and read back once more before
reporting success.

## Confirmation Rules

No extra confirmation is needed when:

- the user explicitly asked to create the task;
- the requirement is clear;
- an existing project and active milestone are a strong match; and
- the write only records the task without executing it.

Confirmation is required before:

- creating a new project or milestone;
- assigning a worth-preserving task to an uncertain project or milestone;
- using a weak milestone;
- writing data that may expose private content beyond what the user requested.

## Non-Goals

- Do not write a plan document first.
- Do not attach a plan document.
- Do not create review cards.
- Do not start task execution.
- Do not imply background scheduling.
- Do not create project or milestone structure without confirmation.
- Do not approve secrets, publishing, deletion, payment, sending, account
  changes, or subjective decisions through task creation alone.
