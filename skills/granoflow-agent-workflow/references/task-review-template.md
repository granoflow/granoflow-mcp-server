# Task Review Base Template

```markdown
<!-- granoflow-task-review:v1:start -->

review_revision: <positive integer>
timezone: <IANA timezone>
attribution_method: telemetry | bounded_transcript_estimate | mixed | unavailable
evidence_coverage_ratio: <0..1 | unknown>
review_operation_id: <stable id>
review_trigger: user_requested | daily_review | implementation_learning | integration_remediation | e2e_remediation | user_acceptance_remediation
implementation_learning_ledger_sha256: <sha256 | not_applicable>
review_steps:
review_write: completed | deferred | confirmation_required | failed | unchanged
cards: completed | deferred | confirmation_required | failed | unchanged | not_applicable
project_context: completed | deferred | confirmation_required | failed | unchanged | not_applicable
milestone_context: completed | deferred | confirmation_required | failed | unchanged | not_applicable
completion_summary: completed | deferred | confirmation_required | failed | unchanged

> Scope notice: This reviews this task's process. Use Task Delivery for its result and verified living context for current project state.

## Outcome Assessment

## Time Analysis

Separate elapsed time, active work, and acceptance latency.

## Time Evidence And Confidence

## Rework And Waste

## AI Implementation Learning

Summarize material observable events by problem, supported root cause,
replacement method, validation evidence, reusable trigger, and applicability
boundary. Do not include hidden reasoning or routine command noise.

### Failed Or Replaced Approaches

### Successful New Methods

### Validation And Reuse Boundaries

## What Worked

## Efficiency Problems

## Next-Time Adjustments

## Knowledge And Experience

## Review Card Results

### Deferred Review Card Checkpoint

Use the canonical `card_checkpoint` record from `../../granoflow-review-card-draft/references/lifecycle-card-checkpoints.md`. This final audit resumes from earlier phase evidence; it is not the first bulk-card pass.

## Project/Milestone Context Promotion

## Residual Risks And Follow-ups

<!-- granoflow-task-review:v1:end -->
```

Profiles add domain-specific evidence; they never replace the base.
