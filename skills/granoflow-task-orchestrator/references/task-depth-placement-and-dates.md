# Task Depth, Placement, And Dates

Read this when creating or enriching a task. Description depth, placement, and
deadline are independent decisions: a rich task may still belong in inbox, and
an inbox task may intentionally have no deadline.

## Description Depth

### `minimal`

Use for incidental capture. Preserve only facts needed to remember the item:

- concise Outcome or problem;
- why it was captured now;
- useful file, page, person, error, or source-task clue already provided;
- `待分析` when the completion signal is genuinely unknown.

Do not create A, P, nodes, cards, or invented acceptance criteria.

### `contextual`

Use when the discussion already established useful context. Add only known
facts:

- Trigger and intended Outcome;
- inspected Evidence and explicit unknowns;
- confirmed boundaries and material risks;
- one concrete example;
- observable completion signal;
- relation to the current task, if this arose during other work;
- recommended next phase.

### `execution_ready`

Use only for `run` or `finish_audit`. It adds the active A/P/D references,
authorization mode, verification evidence, stop conditions, and the correct
completion owner. The Task Work owner still writes the formal lifecycle
document; the Orchestrator does not maintain a competing template.

## Placement

Bind both `projectId` and `milestoneId` only when one existing project and one
active milestone under it are an unambiguous strong pair. Otherwise omit both
and use inbox. Do not create, reopen, or repair project structure on the capture
path.

Always prefer inbox for:

- a side thought unrelated to the active task;
- someday/later wording;
- weak or multiple placement candidates;
- an inactive, done, archived, trashed, or stale milestone;
- a task whose context is too weak to schedule safely.

Record an `originTaskId` or plain source relation when a new task was captured
during another task. This is context, not a dependency or authorization grant.

## Due-Date Ladder

Apply the first supported fact:

1. user's explicit date;
2. real dependency date;
3. today for active blocking work already being executed;
4. tomorrow for one concrete near action without same-day urgency;
5. active milestone deadline for a milestone deliverable;
6. no `dueAt` when no timing fact exists.

Never infer urgency from the surrounding task when the new item is merely a
side thought. Never silently put a task after its milestone deadline.

The deterministic helper `choose_due_at` accepts precomputed offset-aware date
values. Calendar calculation and local timezone ownership remain with the host
or Granoflow App.

## Examples

- “9 月底再做” uses the explicit September deadline even if captured today.
- A release-blocking local fix already in progress uses today.
- “下次优化一下图标” without a project or timing signal stays in inbox with
  no deadline; inventing tomorrow would create false urgency.
