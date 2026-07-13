# Review Drafting

Read this reference before drafting Granoflow daily, weekly, or monthly review
content, mood or efficiency notes, task reviews, or review-card candidates.

## Shared Rules

- Use recorded tasks, task timing, task reviews, project and milestone context,
  focus/session aggregates, interruption count, flow time, and prior user
  statements as evidence.
- Separate recorded facts from inference. Never present inferred mood,
  efficiency, or meaning as certain truth.
- Periodic daily, weekly, and monthly review must be user-initiated. A
  `dailyReviewSuggestion`, `weeklyReviewSuggestion`, or
  `monthlyReviewSuggestion` is a nudge only; do not begin analysis, drafting,
  scoring, journaling, reporting, or writeback from a suggestion alone.
- Require user confirmation before writing mood scores, efficiency scores, mood
  notes, efficiency notes, daily report content, weekly/monthly content, new
  tasks, or review cards.
- Task Review is user-initiated and deferred by default. Ordinary completion
  writes verified Task Delivery and a Completion Summary with review pending;
  it does not automatically write taskReview or Review Cards. Legacy inline
  Review is allowed only when explicitly requested and approved.
- Daily-review synthesis imports remain a separate confirmed writeback path:
  updating task titles, `task_review`, daily report content, or planned tasks
  from that flow still requires the app/user confirmation gate.
- Do not rewrite task start time, end time, actual duration, or flow time from a
  review flow. If task time is wrong, tell the user to adjust it in Granoflow
  task details.
- Candidate task reviews and review cards should capture durable lessons,
  decisions, repeated failure modes, unresolved risks, or reusable process
  details.

## User-Initiated Review Session

Examples of user initiation include:

- `review today`, `write today's journal`, `summarize today`;
- `summarize this week`, `write a weekly report`, `review this week`;
- `review July`, `write a monthly report`, `how did this month go`;
- localized equivalents such as `做日回顾`, `帮我写今天的日记`, `总结这周`,
  `写周报`, `回顾 7 月`, or `这个月我做得怎么样`.

During the session, keep the interaction loose. Let the user add, reject, or
rewrite context in ordinary language. Before saving, show a draft of the fields
that will be written, then wait for confirmation.

## Daily Reviews

AI may draft:

- a short summary of completed work;
- project, milestone, or domain progress visible from the day's tasks;
- candidate task review text for tasks that contain lessons, decisions,
  failures, unresolved risks, or reusable process details;
- candidate review cards for durable knowledge points;
- suggested `moodScore` and `efficiencyScore` on the user's available scale;
- a one-sentence summary when the running app/API exposes such a field or the
  caller needs a compact diary headline;
- short `moodNote` and `efficiencyNote` drafts.

The user must provide or confirm:

- final mood and efficiency scores;
- the final one-sentence summary when present;
- subjective flow time and any manually remembered interruptions;
- whether inferred emotional tone, efficiency, task reviews, daily report
  content, and review-card drafts are accurate enough to save;
- anything not present in task records, such as private context, recovery,
  gratitude, frustration, or meaningful events outside recorded work.

### Mood And Efficiency Notes

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

Before writeback, show the draft mood score, efficiency score, one-sentence
summary when present, mood note, efficiency note, and journal/report content.
Save only after the user confirms or edits the draft.

## Weekly Reviews

Weekly review is not a repetition of seven daily reviews. Its job is to step
back and identify what the week says as a pattern.

AI may draft:

- weekly `content` from completed tasks, daily reviews, task reviews, project
  and milestone progress, time and focus aggregates, and user statements;
- candidate weekly value `score` and `note` entries for values exposed by the
  running Granoflow app;
- patterns across the week, such as repeated blockers, rework, context
  switching, protected focus, neglected directions, or unexpectedly steady
  progress;
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
- Prefer patterns, rhythm, repeated blockers, tradeoffs, and next-week decisions
  over exhaustive task listings.
- Keep weekly value notes natural and short enough to be useful in the weekly
  review UI.
- Save weekly `content` or value entries only after user confirmation.
- Before writeback, show the weekly content draft, value score/note drafts, and
  candidate next-week adjustments.

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
