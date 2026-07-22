# Milestone And Task Deadlines

Read this reference before creating a milestone without an explicit `dueAt`, or
before creating/moving a task into a milestone.

## Milestone creation deadlines

Every new milestone must have a deadline. If the user explicitly provides
`dueAt`, preserve it unchanged. Otherwise call `granoflow_milestone_create`
without `dueAt`; the tool reads the existing milestones and selects the strictly
next Saturday in the user's local time at `23:59:59.000`.

The default is project-aware. If any milestone in the same project has a valid
deadline equal to or later than that candidate Saturday, the tool advances the
candidate by seven-day increments until it is later than every existing
deadline in that project. Milestones in other projects and milestones without a
valid deadline do not affect the result. If the existing milestone schedule
cannot be read, creation without an explicit deadline fails closed; do not guess
or create a milestone with no deadline.

## Task deadlines within milestones

Before creating or moving a task into a milestone, read that milestone's
`dueAt` and choose a task deadline from the task's real urgency, scope,
dependencies, and wording. Unless the user or evidence indicates another
specific date, the normal candidates are today, tomorrow, or the milestone
deadline:

- choose today for explicitly urgent work, work already under way, or a small
  prerequisite that must unblock other near-term work;
- choose tomorrow for a concrete next action that should happen soon but has no
  same-day urgency;
- choose the milestone deadline when there is no nearer timing signal, the work
  may happen at any point in the milestone, or the task represents a milestone
  deliverable.

Do not default every milestone task to today, and do not default every milestone
task to the milestone deadline. A strong explicit or contextual signal may
justify another date. A task inferred from date-only context uses the caller's
local end of day. Never silently assign a task after its milestone deadline. If
the user's explicit date is later, or the milestone is already overdue, expose
the conflict and ask whether to change the task date, milestone deadline, or
placement instead of silently clamping it.

## Success criteria

- Every new milestone has a deadline (explicit or tool-selected).
- Task deadlines respect milestone bounds; conflicts are exposed, not clamped.

## Checkpoints

- Milestone create without `dueAt` only when schedule read succeeds.
- Task placement reads parent `dueAt` before choosing a date.
