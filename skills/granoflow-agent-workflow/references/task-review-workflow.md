# Deferred Task Review Workflow

Use this after task completion when the user explicitly requests a review, an
explicit daily review selects the task, or the current Implementation Learning
Ledger has `review_eligibility: required`. Completion alone does not start deep
Review, but material AI-discovered implementation learning automatically
creates a Review candidate even when the user did not observe the problem.

For a daily-review request, the daily task ledger owns task selection and the
daily skill owns the aggregate confirmation view. This workflow still owns the
Task Review preview, write, and readback: the daily skill does not directly
write the taskReview. Report card outcome separately from the read-back Task
Review body.

## Read And Preview

1. Re-read the latest task, Task Delivery, nodes, taskReview, cards, project/milestone context, available timing evidence, and the exact Implementation Learning Ledger digest when software implementation occurred.
2. Empty taskReview may receive one managed block. One valid marker pair may be revised with `review_revision + 1`. Non-marker user/legacy text requires merge-or-replace preview that preserves it by default. Duplicate, missing, reversed, or nested markers fail closed.
3. Separate elapsed time, active work, and acceptance latency. Exact values require telemetry. Transcript-derived values are estimated; gaps over five minutes remain unknown/idle. Parallel tool intervals use wall-clock union. Rework is a labeled subset, never added twice.
4. When the ledger contains material events, group them by root cause and successful replacement method. Preserve failed approaches only when they explain a reusable future decision; never copy hidden reasoning, raw transcripts, or complete command logs.
5. Present the complete Review plus AI recommendations in one confirmation batch. Do not infer mood, personality, motivation, or subjective scores. A ledger-triggered candidate may await confirmation, but it must remain visible and must not be silently downgraded to `not_required`.

## Resumable Write Order

Use one stable `review_operation_id` and persist step state after each material result:

1. safe taskReview write with latest `expectedUpdatedAt`, then readback;
2. promote only durable project/milestone context;
3. run the Deferred Review Card Checkpoint as the final interactive authoring
   stage and delegate the complete dry-run/open-ended editing/explicit
   approval/apply/readback session to the sole card authoring owner; resume from
   earlier phase provenance instead of treating Review as the first card pass;
4. update Completion Summary with the confirmed or deferred card outcome and
   perform final readback.

In unattended mode, complete the Review and other authorized safe steps first,
then prepare and display the full Note/Card dry-run. Wait for the user to add,
remove, rewrite, split, merge, approve, or defer items in natural language.
Never apply a Note/Card operation from unattended authorization. A requested
edit changes the draft and requires a refreshed preview plus another display;
only a fresh confirmation of explicit operations from that latest preview may
write.

Retry from the latest Granoflow state. Never replay completed steps. A 409 requires re-read and recomputing only the affected diff. If the new state changes confirmation meaning, reconfirm that part.

Completed inbox tasks skip absent project/milestone promotion as `not_applicable`; Review and taskId-based card eligibility continue. Review is complete after confirmed Review body readback; deferred cards/context remain visible but do not reopen the completed task.

Integration, E2E, or user-acceptance remediation appends new material events to
the same logical ledger. After the affected task is green, revise the existing
managed Review with `review_revision + 1`; do not overwrite earlier learning.
A clean first-pass test produces test evidence, not a Task Review requirement.

Efficiency recommendations must name trigger, action, owner, expected benefit, and validation. Persist derived intervals and short safe evidence references, not raw transcripts or full tool logs.
