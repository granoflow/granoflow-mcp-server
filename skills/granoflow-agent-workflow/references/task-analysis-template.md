# Task Analysis Base Template

Use this as the single base structure for Granoflow task analysis. Profiles add
only section 8 content; they do not duplicate this template.

```markdown
# Task Analysis: <task title>

analysis_status: <status>
task_id: <task id>
task_type: general | learning | software_development
purpose: general | learning
created_at: <local timestamp>
updated_at: <local timestamp>
decision: proceed | needs_input | user_action | split | redefine | defer | abandon | completion_audit
planning_readiness: yes | no

## 1. Trigger：触发与问题

## 2. Outcome：期望结果

## 3. Evidence：成功证据

### Final evidence

### Supporting evidence

### Insufficient signals

## 4. Context：事实、材料、推断与未知信息

### Confirmed facts

### Materials and evidence

### AI inference

### Unknown information

## 5. Boundaries：范围、责任与限制

### In scope

### Out of scope

### AI / user responsibility

### Constraints and dependencies

## 6. Risks：风险、假设与阻塞

## 7. Decision：分析结论

### Recommendation and rationale

### Alternatives considered

### State-level next action

## 8. Profile 补充分析

## 9. Grill Review

### Closed questions

### User-confirmed decisions

### Changes caused by Grill

### Unresolved questions

## 10. Planning Readiness
```

Keep every base section. Simple tasks may use one or two sentences per section.
Write `当前无` or `待确认` with a reason when necessary. Do not copy chat
transcripts or hidden reasoning. Analysis stops at state-level next actions;
implementation `How` belongs in the plan.
