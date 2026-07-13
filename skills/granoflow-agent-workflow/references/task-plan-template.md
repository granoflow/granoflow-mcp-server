# Task Plan Template

Use this base template after a confirmed analysis final. A project 73/76 may be the Plan SSOT when it contains the same contract.

```markdown
# Task Plan: <title>

task_id: <id>
plan_version: <positive integer>
plan_kind: general | learning | software_development | project_73 | project_76
plan_status: draft
source_analysis: <active analysis final>
supersedes: null | <prior plan attachment>
execution_readiness: <state>

## Analysis Inheritance

- Outcome:
- Final Evidence:
- Boundaries:
- Risks:
- User-confirmed decisions:

## Recommended Approach

## Execution Nodes

### Node N: <action + result>

- Owner: AI | user | both
- Preconditions:
- Action:
- Deliverable:
- Delivery standard:
- Completion condition:
- Verification Evidence:
- Acceptance: automated | ai_review | user_manual
- Manual acceptance instructions: none | <entry, steps, pass criteria>
- Downstream startup requirements:
- Handoff decision:
- Block and stop conditions:

## Dependencies And Handoffs

| Upstream | Downstream | Type | Deliverable | Startup requirement | Evidence |
| -------- | ---------- | ---- | ----------- | ------------------- | -------- |

Types: `execution_required` or `non_blocking_acceptance`.

## Information Readiness

## Authorization Matrix

## Verification Plan

## Failure, Rollback And Stop Conditions

## Granoflow Writeback

## Plan Grill

## Confirmation And Execution Readiness
```

Every node must deliver something observable and sufficient for the next execution node to start. `user_manual` nodes use the title `验收：<object>` in Granoflow and never block later safe execution.
