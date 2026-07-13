# Task Delivery Base Template

```markdown
# Task Delivery: <task title>

document_type: task_delivery
schema_version: 1
task_id: <id>
profiles: [] | [learning] | [software_development] | [learning, software_development]
delivery_version: <positive integer>
delivery_status: draft | delivered | delivered_with_residuals | awaiting_manual_acceptance | superseded
source_analysis: <attachment reference>
source_plan: <attachment reference>
supersedes: null | <prior attachment>
delivered_at: <timestamp>
based_on_task_updated_at: <timestamp>
content_sha256: <sha256>
acceptance_status_as_of: accepted | partially_accepted | awaiting_manual_acceptance | not_required

> Scope notice: This records this task's delivery as of delivered_at. Later work may change it; verify current state against living context and actual evidence.

## Final Outcome

## Deliverables

## Differences From Analysis

## Differences From Plan

## Card Reconciliation And Card Checkpoint

Use the canonical `card_checkpoint` record from `../../granoflow-review-card-draft/references/lifecycle-card-checkpoints.md` to reconcile cards with actual delivery. Record accepted, overturned, and deferred knowledge without persisting a preview token.

For each Analysis or Plan knowledge expectation that differs from delivery, record:

- Expected knowledge or card state:
- Actual delivery evidence:
- Disposition: accepted | superseded | deferred
- Card operation IDs: none | <operation ids>
- Owner and next entry point: none | <owner and action>

## Actual Change Surface

## Verification Evidence

## Manual Acceptance

## Residuals And Deferred Work

## Handoff And Usage

## Traceability
```

Each deliverable records its location or identifier, status, evidence, and use. Classify deltas as assumption invalidation, scope change, execution deviation, or evidence change. Keep the base complete; profiles only add requirements.
