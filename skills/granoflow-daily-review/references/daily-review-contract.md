# Daily Review Contract

## Preconditions

- The user actively initiated a daily review. `dailyReviewSuggestion` is a
  nudge only and never begins display, drafting, scoring, or writing by itself.
- Resolve the date from the user's request; otherwise use the local current
  date and say so.
- Verify the running Granoflow Local HTTP API and inspect advertised daily
  review read/write, task read/export, Task Review update/readback, and timing
  evidence capabilities before proposing a write. If unavailable, show a
  non-persistent draft and state the blocker.

## 1. Display

Build a daily task ledger before drafting the diary. A relevant task has an
actual activity interval overlapping the user's local day, a Task Delivery,
Completion, or Task Review written that day, or explicit user inclusion. A task
that is only due that day is not included without activity evidence.

For every ledger task, read bounded evidence: task timing, Task Delivery, nodes,
current Task Review, task review/card outcome when available, project/milestone
context, and user statements supplied in this conversation. Do not read hidden
history or infer private events.

Display separately:

- recorded facts;
- inferences, with uncertainty;
- missing or user-only context;
- the daily task ledger, with task id/title, inclusion evidence, review status,
  and card outcome;
- a proposed field table containing mood score, efficiency score, one-sentence
  summary when supported, mood note, efficiency note, and journal/report
  content when supported.

Do not convert weak evidence into emotion, productivity stories, task changes,
or durable knowledge.

### Task Review coverage

Classify every ledger task as `already_reviewed`,
`review_pending_confirmation`, `reviewed_and_readback`, `unavailable`, or
`deferred_by_user`. Reuse a legal, read-back Task Review without rewriting it.
For an empty or safely creatable Task Review, prepare it with the existing
Deferred Task Review workflow and show it in the daily-review confirmation batch.

The daily review does not directly write `taskReview`: after the user approves a
specific task, delegate to the Task Review owner for its preview, confirmed
write, and readback. Marker parsing failures, revision conflicts, unavailable
capabilities, or declined approval fail closed. Do not report those tasks as
reviewed; retain their reason in the ledger and diary coverage summary.

`reviewed_and_readback` means only that the Task Review body was safely written
and read back. Show card outcome separately. Cards remain the Task Review card
owner's controlled operation, and a deferred or unavailable card outcome does
not undo a read-back Task Review.

### Default display

When the user gives no format, length, or focus, begin with this discussion
structure:

```text
Today's summary
- Progress and completion:
- Main friction or change:

Efficiency note
- Work rhythm and output:
- One adjustment to try:

Mood note
- Overall feeling:
- Influences or recovery/support:

Free record
- Anything the user wants to keep:
```

This is a default display, not a required form or fixed saved template. If the
user supplies a structure, edits fields, or writes freely, reorganize the draft
around the user's expression. The summary and free record become journal/report
`content` only when the user confirms that content and the App supports it; the
display headings themselves do not need to be saved.

The diary has two layers: the complete daily task ledger provides coverage, while
the journal/report `content` summarizes only key progress, friction, changes,
and rework. Do not repeat every task in prose when the ledger already carries
the complete inventory.

## 2. Conversation and Explicit Confirmation

Let the user naturally amend the draft. Ask only for information needed to make
the requested review useful. The user must explicitly confirm every value that
will be written; partial confirmation writes only the named fields.

For saved notes, use concise personal-review language: at most 80 Chinese
characters or a similarly concise length in the user's language. Do not save
phrases such as “AI suggests” or a scoring explanation.

`moodNote` weighs smoothness, frustration, recovery, positive events, rest, and
the user's own statements. `efficiencyNote` weighs work continuity, gaps,
focus, interruptions, important-task completion, rework, and blockers. Keep
these distinct; neither is certain merely because task data exists. Efficiency
is not task count, and a blocker is not proof of low efficiency. Do not diagnose
the user's mood or invent a cause for it.

For the diary's friction, change, and experience analysis, distinguish active
work, idle/unknown time, acceptance latency, and context switching when evidence
allows. Compare Analysis/Plan with Task Delivery for scope, assumption, evidence,
or execution changes. Treat repeated result corrections, Delivery versions,
reopened nodes, and explicit Task Review rework evidence as rework evidence.
For a task with repeated correction or high rework evidence, explain its trigger,
root cause, time/attention cost, next adjustment, and reusable lesson. Mark the
field `unavailable` or `unknown` when a task timeline or revision evidence is
not advertised; never infer rework from a timestamp alone.

## 3. Write and Readback

Before writing, re-show the exact approved field set. Write through the
running App's supported Local HTTP API only. First delegate each approved missing
Task Review and read it back; then synthesize from the resulting ledger, write
the approved daily fields, and read back the requested date. Report each ledger
task and approved field as persisted, unavailable, conflict, failed, or deferred.

If a mood/efficiency field or journal/report `content` is unavailable, retain it
only as a non-persistent draft and say so. Do not create a new field, silently
discard confirmed content, or write it through an unrelated endpoint.

Never from this flow:

- rewrite task start/end times, actual duration, or flow time;
- directly write `taskReview` or alter task titles/status;
- create a task, card, or project/milestone context entry;
- bypass another owner's preview and confirmation gate.

Offer such actions only as separately named follow-ups after daily-review
readback. If the user accepts a card follow-up, call
`granoflow_review_card_draft_skill`; if the user accepts task review, route to
`granoflow_agent_workflow_skill`.

If the user wants lessons distilled, call the public Knowledge Distillation
workflow after diary readback. Preview Experience candidates from the day's
confirmed Task Reviews and Evidence, display all candidates, and apply only the
approved subset. Experience is independent of the diary and may later be linked
to many Tasks. Do not create Cards from raw diary prose or raw Experience; Card
work begins only after a separate Knowledge assessment and materialization gate.
