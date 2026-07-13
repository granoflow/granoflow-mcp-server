# Task Delivery Workflow

Task Delivery is the immutable, versioned record of what this task actually delivered. It is required before completion for work that entered Plan or Execution and is not a Task Review.

1. Re-read the task, nodes, description, attachments, Analysis, Plan, and current evidence.
2. Select base plus composable profiles. Determine the highest `task-delivery-vNN.md`; use the next version.
3. Record actual deliverables, evidence, Analysis/Plan deltas, acceptance state, residuals, handoff, and traceability.
4. Load the sole card authoring owner and run the Delivery Card Checkpoint. Reconcile cards with actual output; keep unapproved or unverifiable work explicit as deferred, conflict, or `verification_failed`.
5. Compute SHA-256 and upload with stable idempotency key, `expectedTaskUpdatedAt`, and expected hash.
6. Same filename/version plus same hash is an idempotent retry. Same filename/version plus different hash is a conflict: re-read and create a later version or stop. Never overwrite or delete the conflicting record.
7. Read content or App-owned trusted hash back. Filename-only list and HTTP success do not pass.
8. Update the Task Completion Summary managed block with a read-only Delivery Card Checkpoint summary. Acceptance-only changes update nodes/summary, not immutable Delivery.
9. Node-backed task: finish the last required node and let NodeService complete the parent. Node-less task: use the compatibility finish once. Stop when readback is already `done`.

Secret-scan persisted content. Do not copy raw transcripts, full tool logs, credentials, OTPs, auth URLs, or unrelated personal data.
