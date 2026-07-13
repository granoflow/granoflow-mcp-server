# Deferred Task Review Workflow

Use this only when the user explicitly asks to review a task, including a completed inbox task. Completion does not automatically start deep Review.

## Read And Preview

1. Re-read the latest task, Task Delivery, nodes, taskReview, cards, project/milestone context, and available timing evidence.
2. Empty taskReview may receive one managed block. One valid marker pair may be revised with `review_revision + 1`. Non-marker user/legacy text requires merge-or-replace preview that preserves it by default. Duplicate, missing, reversed, or nested markers fail closed.
3. Separate elapsed time, active work, and acceptance latency. Exact values require telemetry. Transcript-derived values are estimated; gaps over five minutes remain unknown/idle. Parallel tool intervals use wall-clock union. Rework is a labeled subset, never added twice.
4. Present the complete Review plus AI recommendations in one confirmation batch. Do not infer mood, personality, motivation, or subjective scores.

## Resumable Write Order

Use one stable `review_operation_id` and persist step state after each material result:

1. safe taskReview write with latest `expectedUpdatedAt`, then readback;
2. run the Deferred Review Card Checkpoint and delegate search/preview/approval/apply/readback to the sole card authoring owner; resume from earlier phase provenance instead of treating Review as the first card pass;
3. promote only durable project/milestone context;
4. update Completion Summary and perform final readback.

Retry from the latest Granoflow state. Never replay completed steps. A 409 requires re-read and recomputing only the affected diff. If the new state changes confirmation meaning, reconfirm that part.

Completed inbox tasks skip absent project/milestone promotion as `not_applicable`; Review and taskId-based card eligibility continue. Review is complete after confirmed Review body readback; deferred cards/context remain visible but do not reopen the completed task.

Efficiency recommendations must name trigger, action, owner, expected benefit, and validation. Persist derived intervals and short safe evidence references, not raw transcripts or full tool logs.
