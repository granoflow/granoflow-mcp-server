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
- Candidate task reviews and review cards should capture durable lessons,
  decisions, repeated failure modes, unresolved risks, or reusable process
  details.

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

## Monthly Reviews

Monthly review is about direction and tradeoffs. It should help the user see
what they repeatedly gave time, attention, emotion, and patience to during the
month.

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
- Prefer direction, tradeoffs, investment structure, recurring costs, important
  progress, and next-month choices over exhaustive task listings.
- Save monthly `content` only after user confirmation.
- Before writeback, show the monthly content draft, theme/interpretation, and
  continue/reduce/pause/protect suggestions.
