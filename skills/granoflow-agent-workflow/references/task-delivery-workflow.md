# Task Delivery Workflow

Task completion has a hard precondition: the task must contain an App-owned,
readable, content/hash-verified Task Work Document attachment, or the complete
legacy pair of verified Task Analysis and Task Plan attachments. No completion
path may mark the task done without one of these document records. Task Delivery
is the immutable, versioned record of what this task actually delivered. It is
required before completion for work that entered Execution and is not a Task
Review, including `planning_status=not_required` work.

Time reconciliation is part of completion evidence: `startedAt` is the actual
entry into Execution. AI work captures and writes it while remaining `pending`;
human manual focus normally receives it from the App's `doing` transition.
`endedAt` is the confirmed completion point. The earlier task discussion,
capture, Analysis, or Planning time is not execution time and must not be
substituted. If a timestamp correction is genuinely required, use the
dedicated historical mutation surface with evidence and readback.

1. Re-read the task, nodes, description, attachments, active Work Document, and current evidence. For legacy work, read the verified Analysis and Plan instead. Stop with `task_analysis_plan_attachment_required` when the required document attachment is absent.
2. Select base plus composable profiles. Determine the highest `task-delivery-vNN.md`; use the next version.
3. New Delivery writes only `source_work_document` and records actual deliverables, evidence, Work Document deltas, acceptance state, residuals, handoff, and traceability. Legacy Delivery may read existing `source_analysis` and `source_plan`; never add those fields to a new Delivery.
4. Load the sole card authoring owner and run the Delivery Card Checkpoint. Reconcile cards with actual output; keep unapproved or unverifiable work explicit as deferred, conflict, or `verification_failed`.
5. Compute SHA-256 and upload with stable idempotency key, `expectedTaskUpdatedAt`, and expected hash.
6. Same filename/version plus same hash is an idempotent retry. Same filename/version plus different hash is a conflict: re-read and create a later version or stop. Never overwrite or delete the conflicting record.
7. Read content or App-owned trusted hash back. Filename-only list and HTTP success do not pass.
8. For `software_development` (or any task that edited code/tests/build files): verify the Hard Gate from `software-structural-budget.md`—`structural_forecast_notice_emitted_at` was set before edits, Delivery contains planned-versus-actual forecast reconciliation with `structural_forecast_status: reconciled`, and an `acceptance_report` HTML exists with content/hash readback. Fail closed with `structural_forecast_not_shown`, `structural_forecast_unreconciled`, or `acceptance_report_missing` instead of marking done. Also verify project context Hard Gate from `project-context-attachments.md`: check ran; conflicts resolved with user confirmation (interactive) or an emitted decision notice (unattended)—fail closed on `project_context_check_missing`, `project_context_conflict_unconfirmed`, `project_context_decision_not_emitted`, or `project_context_check_unreconciled`. Also verify Task Integration Test Policy: if `copy_change_only`, no automated tests were added/run (`copy_change_tests_forbidden` otherwise); else `unit_test_sufficiency` assessed; at most 2 integration tests and only when insufficient; `integration_test_execution: not_run_manual_only` and a user-selected `integration_test_device` (recommended `local_machine`) when any were added—fail closed on `unit_test_sufficiency_unassessed`, `integration_test_added_without_insufficiency`, `integration_test_cap_exceeded`, `integration_test_executed_by_agent`, or `integration_test_device_unselected`.
9. Update the Task Completion Summary managed block with a read-only Delivery Card Checkpoint summary. Acceptance-only changes update nodes/summary, not immutable Delivery.
10. Node-backed task: verify the required document attachment, finish the last required node, and let NodeService complete the parent. Node-less task, including light `planning_status=not_required` work: verify the required document attachment, create and read back Delivery first, then use the compatibility finish once. Stop when readback is already `done`.

Secret-scan persisted content. Do not copy raw transcripts, full tool logs, credentials, OTPs, auth URLs, or unrelated personal data.
