# Task Plan Template

Use this base template after a confirmed analysis final. Local planning-document numbers are repository governance only and never become public task types.

```markdown
# Task Plan: <title>

task_id: <id>
plan_version: <positive integer>
profiles: [] | [learning] | [software_development] | [learning, software_development]
plan_status: draft
source_analysis: <active analysis final>
supersedes: null | <prior plan attachment>
execution_readiness: <state>

> Scope notice: This is the pre-execution plan, not a completion record. Task Delivery governs what was actually delivered.

## Analysis Inheritance

- Outcome:
- Final Evidence:
- Boundaries:
- Risks:
- User-confirmed decisions:

## Recommended Approach

## Knowledge And Card Plan

Use the canonical Card Checkpoint from `../../granoflow-review-card-draft/references/lifecycle-card-checkpoints.md`. Record knowledge inherited from Analysis, expected changes, and the evidence or event that would trigger reconciliation.

## Execution Nodes

### Node N: <action + result>

- Owner: AI | user | both
- Preconditions:
- Action:
- Deliverable:
- Delivery Standard:
- Completion Condition:
- Verification Evidence:
- Acceptance: automated | ai_review | user_manual
- Manual acceptance instructions: none | <entry, steps, pass criteria>
- Downstream Startup Requirements:
- Handoff Decision:
- Stop Conditions:
- Knowledge/Card Delta Trigger: none | <material knowledge, correction, rule, or reusable-experience trigger>

## Dependencies And Handoffs

| Upstream | Downstream | Type | Deliverable | Startup requirement | Evidence |
| -------- | ---------- | ---- | ----------- | ------------------- | -------- |

Types: `execution_required` or `non_blocking_acceptance`.

## Information Readiness

## Authorization Matrix

## Verification Plan

## Failure, Rollback And Stop Conditions

## Granoflow Writeback

- Delivery gate before final required node:
- Completion owner: NodeService | node-less compatibility

## Plan Grill

## Card Checkpoint

## Confirmation And Execution Readiness
```

Every node must deliver something observable and sufficient for the next execution node to start. `user_manual` nodes use the title `验收：<object>` in Granoflow and never block later safe execution.
