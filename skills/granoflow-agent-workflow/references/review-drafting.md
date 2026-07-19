# Review Drafting

Read this reference before drafting Granoflow weekly or monthly review content,
task reviews, or review-card candidates. For an explicitly requested daily
review, mood note, efficiency note, or daily journal, call
`granoflow_daily_review_skill`; it is the only bundled daily-review owner.

## Shared Rules

- Use recorded tasks, task timing, task reviews, project and milestone context,
  focus/session aggregates, interruption count, flow time, and prior user
  statements as evidence.
- Separate recorded facts from inference. Never present inferred mood,
  efficiency, or meaning as certain truth.
- Periodic review must be user-initiated. A `dailyReviewSuggestion`,
  `weeklyReviewSuggestion`, or `monthlyReviewSuggestion` is a nudge only; do
  not begin analysis, drafting, scoring, journaling, reporting, or writeback
  from a suggestion alone.
- Never present inferred mood, efficiency, or meaning as certain truth. Daily
  subjective-field confirmation and writeback belong exclusively to
  `granoflow_daily_review_skill`.
- Require user confirmation before writing weekly/monthly content, new tasks,
  or review cards.
- Task Review is user-initiated and deferred by default. Ordinary completion
  writes verified Task Delivery and a Completion Summary with review pending;
  it does not automatically write taskReview or Review Cards. Legacy inline
  Review is allowed only when explicitly requested and approved.
- Daily-review synthesis imports remain a separate confirmed writeback path.
  A daily review cannot update task titles, `task_review`, or planned tasks
  without that other owner's preview and confirmation gate.
- Do not rewrite task start time, end time, actual duration, or flow time from a
  review flow. If task time is wrong, tell the user to adjust it in Granoflow
  task details.
- Candidate Experience should capture durable lessons, decisions, repeated
  failure modes, unresolved risks, or reusable process details. Review Cards
  require a later Knowledge assessment/materialization gate.

## Milestone Focus For Every Periodic Review

Daily, weekly, and monthly reviews include a bounded milestone pass when
milestones are available. Read each active milestone's title, description,
`dueAt`, status, and linked tasks. Report the deadline in local time and classify
it as future, due soon, overdue, missing, or invalid. Treat title/description
wording as signals, not facts, and label each as recorded fact, user-confirmed
interpretation, tentative inference, or unknown.

Return one recommendation per milestone: `accelerate_internal_tasks`,
`continue`, `archive_candidate`, or `needs_user_direction`. Acceleration names
unfinished tasks and blockers but does not silently change status or dates.
Archive candidacy requires readable task/Delivery evidence, milestone-level
integration evidence, and a destination for unfinished work. An empty task
list, old deadline, or worker summary alone never proves archival. Review
recommendations do not authorize writes.

In unattended mode, emit an explicit non-question notice naming the milestone,
deadline classification, signals, evidence, recommendation, and next action.
Continue only when authorization covers the exact action, the App advertises a
safe archive capability for archival, and evidence/readback gates pass.
Otherwise persist a visible blocker; never simulate archive with a status patch
or description update.

## User-Initiated Weekly Or Monthly Review Session

Examples of user initiation include:

- `summarize this week`, `write a weekly report`, `review this week`;
- `review July`, `write a monthly report`, `how did this month go`;
- localized equivalents such as `总结这周`, `写周报`, `回顾 7 月`, or
  `这个月我做得怎么样`.

During the session, keep the interaction loose. Let the user add, reject, or
rewrite context in ordinary language. Before saving, show a draft of the fields
that will be written, then wait for confirmation.

## Weekly Reviews

Weekly review is not a repetition of seven daily reviews. Its job is to step
back and identify what the week says as a pattern through an interactive recall
session, not an automatic weekly report.

Follow this order after the user initiates the session:

1. Display target week dates and the caller's local time zone, then show a
   bounded coverage ledger for available daily reviews, task/task-review and
   delivery records, project or milestone progress, time/focus aggregates, and
   existing weekly content. Mark evidence as available, missing, or unavailable;
   missing records do not prove that nothing happened.
2. Select 3–5 high-information recall cues rather than dumping every task.
   Prefer a consequential delivery or decision, recurring friction/rework/context
   switching, an unusual time/focus distribution, important unrecorded or
   deferred work, and a project or milestone direction change. State the record
   supporting each cue.
3. Discuss one cue at a time with an open question. The user may skip any
   question, reject its premise, or provide free-form context; reorganize the
   draft around that context rather than forcing a questionnaire. Do not seek
   sensitive, relationship, or emotional details unless the user introduces them.
4. Draft weekly `content`, value `score`/`note` candidates, cross-week patterns,
   and candidate next-week experiments from the evidence plus the user's
   additions. Label each material claim as a recorded fact, a user-confirmed
   interpretation, a tentative inference, or unknown. Never turn an inference
   into a fact or diagnose mood, motivation, or mental state.

The user may use partial confirmation: confirm, edit, reorder, delete, or defer
weekly content, each value score/note, each pattern, and each next-week
experiment independently. Only confirmed fields may be written.

Next-week experiments are candidates, not execution authorization. A task,
reminder, review card, Task Review, or project/milestone rule requires its own
preview/confirmation/write/readback flow; weekly review does not automatically
create tasks, reminders, cards, Task Reviews, or project/milestone changes.

Rules:

- Do not summarize each day one by one unless the user asks for a timeline.
- Prefer patterns, rhythm, repeated blockers, tradeoffs, and next-week decisions
  over exhaustive task listings.
- Keep weekly value notes natural and short enough to be useful in the weekly
  review UI.
- Before writeback, show the target-week coverage, approved weekly content,
  approved value score/note entries, approved patterns, and approved next-week
  experiments separately from deferred or rejected items.
- Save only the approved weekly `content` or value entries, then read them back.

After weekly readback, offer a separate Experience distillation preview based
on the week's confirmed Experience/Evidence and historical vector search. Show
duplicate, conflict, boundary, and degraded-search signals; apply only the
user-approved Experience operations. Do not create Knowledge or Cards merely
because a weekly pattern was identified.

## Monthly Reviews

Monthly review is an interactive recall session about direction and tradeoffs,
not an automatic monthly report or four weekly summaries.

Resolve the target month before reading or drafting: use a user-specified month;
interpret `this month` in the caller's local time zone and `last month` as the
previous complete calendar month; ask the user to choose for another ambiguous
request. Then display target month dates and the caller's local time zone.

Follow this order after the user initiates the session:

1. Show a bounded coverage ledger for available daily/weekly reviews,
   task/task-review and delivery records, project or milestone changes, monthly
   time/focus aggregates, and existing monthly content. Show sources, ranges,
   and only the minimum necessary facts for the current cue; mark evidence as
   available, missing, or unavailable. Missing or unavailable evidence does not
   mean no progress.
2. Select 3–5 high-information recall cues rather than dumping the month's
   tasks. Prefer a direction change, consequential decision or delivery,
   investment structure or cost, recurring friction/rework, unrecorded but
   important work, or project/milestone movement.
3. Discuss one cue at a time with an open prompt. The user may skip any prompt,
   reject its premise, or give a free-form account that replaces the framework.
   Do not seek sensitive, relationship, or emotional details unless the user
   introduces them. With empty or unavailable coverage, begin with the user's
   free-form account instead of inferring inactivity.
4. Draft monthly `content`, month-level direction, investment/cost, repeated
   patterns, and candidate next-month experiments from the evidence plus the
   user's additions. Label each material claim as a recorded fact, a
   user-confirmed interpretation, a tentative inference, or unknown. Never turn
   inference into fact or diagnose motivation, efficiency, mood, or mental state.

When the user has not supplied a structure, offer these skippable discussion
entries, not a required form:

- monthly main thread: what did this month really center on?
- key changes: which decision, turn, or delivery changed direction?
- investment and cost: where did time and attention go, and was it worth it?
- repeated patterns: which friction, rework, or environmental condition recurred?
- unrecorded but important: what mattered but never entered the task system?
- next-month experiments: what should continue, reduce, pause, or be protected?

Let the user reorder, omit, or replace these entries. A candidate next-month
experiment should name its trigger, action, owner, expected benefit, and
verification method, but it is not execution authorization.

The user may use partial confirmation: confirm, edit, reorder, delete, or defer
monthly content, each pattern/interpretation, and each next-month experiment
independently. Only confirmed monthly `content` may be written.

Recognition of a reusable lesson does not create a review card. Tasks, reminders,
review cards, Task Reviews, and project/milestone changes each require their own
preview/confirmation/write/readback flow; monthly review does not automatically
create tasks, reminders, cards, Task Reviews, or project/milestone changes.

Rules:

- Monthly aggregate metrics are read-only. Do not attempt to write task count,
  focus totals, average daily minutes, most active date, or derived metrics.
- Monthly REST and CLI writes may update only `content`.
- Do not turn the month into four weekly summaries unless the user asks for that
  structure.
- Prefer direction, tradeoffs, investment structure, recurring costs, important
  progress, and next-month choices over exhaustive task listings.
- Before writeback, show approved monthly content, approved patterns and
  interpretations, and approved next-month experiments separately from deferred
  or rejected items.
- Save only confirmed monthly `content`, then read it back.

After monthly readback, the same separate Experience preview/apply gate may
summarize month-level patterns and compare them with all historical Experience.
Knowledge assessment and Card materialization remain later, separately approved
operations.
