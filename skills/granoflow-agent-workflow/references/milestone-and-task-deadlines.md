# Milestone And Task Deadlines

Read this reference before creating a milestone without an explicit `dueAt`, or
before creating/moving a task into a milestone.

## Milestone creation deadlines

Every new milestone must have a deadline. If the user explicitly provides
`dueAt`, preserve it unchanged. Otherwise call `granoflow_milestone_create`
without `dueAt`; the tool reads the existing milestones. The first milestone in
that project uses today in the user's local time at `23:59:59.000`. Each later
milestone uses at least the local calendar day after the latest valid project
deadline.

The fallback is project-aware and strictly increasing. Existing deadlines in
other projects and invalid or absent deadlines do not affect it. When all valid
project deadlines are before today, the next inferred deadline is today. If the
existing milestone schedule cannot be read, creation without an explicit
deadline fails closed; do not guess or create a milestone with no deadline.

## Task deadlines within milestones

Before creating or moving a task into a milestone, the shared MCP task-write
runtime reads that milestone's `dueAt`. An explicit valid task deadline is
preserved when it is not later than the milestone. When task `dueAt` is omitted,
the runtime copies the milestone deadline and reports
`deadlineResolution.source: inherited_milestone` in its result.

Agents may still choose a justified earlier date from explicit user wording,
dependencies, active blocking work, or a concrete near action. Supply that date
explicitly so the readback records `deadlineResolution.source: explicit`.

Never silently assign a task after its milestone deadline. An invalid parent
deadline, unreadable parent, invalid explicit task date, or explicit date later
than the parent fails before the App write. Ask whether to change the task
date, milestone deadline, or placement instead of silently clamping it.

## Success criteria

- Every new milestone has a deadline (explicit or tool-selected).
- Task deadlines respect milestone bounds; conflicts are exposed, not clamped.

## Checkpoints

- Milestone create without `dueAt` only when schedule read succeeds.
- Shared Task write resolves parent `dueAt` before every milestone placement.
