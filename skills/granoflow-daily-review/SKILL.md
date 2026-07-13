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
   evidence and existing daily-review values; show recorded facts, clearly marked
   inferences, missing context, and a draft of every field that could be written.
   Use the default display only when the user gives no format, length, or focus;
   it is not a required form.
2. **Conversation and confirmation**: let the user add, reject, rewrite, or
   approve individual fields in natural language. A nudge, a past preference, or
   an inferred mood is never write authorization. When the user writes freely
   or supplies a structure, reorganize the draft around that expression rather
   than forcing it back into the default display.
3. **Write and readback**: write only explicitly confirmed fields using the
   App-advertised Local HTTP API surface, then read back and report what actually
   persisted. Do not treat a request success response as proof.

## Ownership Boundaries

- Daily review owns the day's summary, journal/report content when available,
  mood/efficiency suggestions and notes, and their confirmed writeback.
- It does not write `taskReview`, change task time, create or modify tasks,
  create cards, or promote project/milestone context.
- Candidate task reviews or durable lessons may be displayed as separate
  follow-up recommendations. A Task Review remains user-initiated and deferred;
  any card action delegates to `granoflow-review-card-draft` with its own
  preview, approval, apply, and readback gates.
- Weekly and monthly reviews remain with `granoflow-agent-workflow`; they may
  consume confirmed daily records as evidence but do not replace this owner.

## Success Criteria

- The user can see what evidence exists and what is inferred before any write.
- Subjective values and journal content are never persisted without explicit
  confirmation.
- The final report distinguishes confirmed writes, declined fields, unavailable
  fields, and separate deferred follow-ups.
