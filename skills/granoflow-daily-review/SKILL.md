---
name: granoflow-daily-review
description: Use when a user explicitly asks to review, summarize, or journal one day in Granoflow, including mood or efficiency notes. Owns the daily-review display, conversation/confirmation, write, and readback flow.
---

# Granoflow Daily Review

Use this skill for an explicitly requested daily review, such as `review today`,
`summarize today`, `write today's journal`, `做日回顾`, or `帮我写今天的日记`.
It is the single bundled owner for writing a daily review. Other bundled skills
must call `granoflow_daily_review_skill` and delegate here instead of composing
or writing a daily review themselves.

## Required Flow

Read [Daily Review Contract](references/daily-review-contract.md) before work.
Follow these phases in order:

1. **Display**: resolve the requested local date; read only available Granoflow
   evidence and existing daily-review values; build a daily task ledger before
   the diary draft, then show recorded facts, clearly marked inferences, missing
   context, and a draft of every field that could be written.
   Use the default display only when the user gives no format, length, or focus;
   it is not a required form.
2. **Conversation and confirmation**: let the user add, reject, rewrite, or
   approve individual task reviews and daily fields in natural language. A nudge,
   a past preference, or an inferred mood is never write authorization. When the
   user writes freely or supplies a structure, reorganize the draft around that
   expression rather than forcing it back into the default display.
3. **Write and readback**: write only explicitly confirmed fields using the
   App-advertised Local HTTP API surface. Delegate each approved missing Task
   Review to its existing owner, read it back, then write and read back the daily
   review. Do not treat a request success response as proof.
4. **Final Note/Card session**: after diary readback and any separately approved
   Experience/Knowledge work, delegate all supported candidates to
   `granoflow-review-card-draft`. Display the complete App dry-run, let the user
   freely add, reject, rewrite, split, merge, or select items, refresh the
   preview after every draft change, and write only the exact latest-preview
   operations the user confirms. In unattended mode, prepare this stage last
   and wait; never apply Note/Card writes from unattended authorization.

## Ownership Boundaries

- Daily review owns the day's summary, journal/report content when available,
  mood/efficiency suggestions and notes, their confirmed writeback, and the
  orchestration of missing Task Reviews from the daily task ledger.
- It does not directly write `taskReview`, change task time, create or modify
  tasks, create cards, or promote project/milestone context. A daily review
  delegates an approved missing Task Review to the existing Task Review owner.
- The daily task ledger records each relevant task as `already_reviewed`,
  `review_pending_confirmation`, `reviewed_and_readback`, `unavailable`, or
  `deferred_by_user`, plus a separate card outcome. `reviewed_and_readback`
  proves only the Task Review body, not that cards were created or applied.
- Task Review remains deferred from ordinary completion. An explicitly requested
  daily review is a valid review session, but each missing Task Review still
  needs the Task Review preview, confirmation, write, and readback gates. Card
  actions remain delegated to `granoflow-review-card-draft` with their own
  approval path.
- Weekly and monthly reviews remain with `granoflow-agent-workflow`; they may
  consume confirmed daily records as evidence but do not replace this owner.
- After daily-review readback, the user may explicitly approve a separate
  Experience proposal pass. It uses the App-owned Experience preview/apply
  flow and never turns diary prose directly into Experience or Cards.
- Daily review does not implement its own card rules. Its final Note/Card stage
  always delegates to the shared authoring owner, including dry-run,
  open-ended revision, partial confirmation, apply, and practice-ready readback.

## Success Criteria

- The user can see what evidence exists and what is inferred before any write.
- Subjective values and journal content are never persisted without explicit
  confirmation.
- The final report distinguishes confirmed writes, declined fields, unavailable
  fields, and separate deferred follow-ups.
- Any Experience candidates are shown and confirmed separately after diary
  readback; daily review completion never implies their acceptance.
- Any Note/Card candidate is fully displayed at the end and remains zero-write
  until the user explicitly confirms operations from the latest preview.
