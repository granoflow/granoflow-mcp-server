# Provider-neutral Worker Report

The runner sets these environment variables for each worker:

- `GRANOFLOW_MILESTONE_ID`
- `GRANOFLOW_TASK_ID`
- `GRANOFLOW_MILESTONE_REPORT_PATH`
- `GRANOFLOW_MILESTONE_RUN_MODE=execute|replan|completion_audit`
- `GRANOFLOW_MILESTONE_AUTHORIZATION_PATH`
- `GRANOFLOW_EXECUTION_MODE=interactive|unattended|layered_handoff`
- `GRANOFLOW_NODE_LANE` (empty in ordinary interactive work)
- `GRANOFLOW_NODE_ID` (empty when no explicit node is assigned)

A worker may atomically write this optional JSON report:

```json
{
  "schema": "granoflow_worker_report_v1",
  "disposition": "continue",
  "attemptFingerprint": "stable-sanitized-strategy-id",
  "newEvidence": true,
  "checkpointRef": "task-or-node-reference"
}
```

Allowed dispositions are `continue`, `retry_wait`, `replan_required`, `waiting_for_permission`, `waiting_for_user`, `blocked`, and `complete`.

The report controls scheduling hints only. Even `disposition=complete` cannot complete or accept a task. The runner independently re-reads Granoflow. Reports must not include free-form transcripts, secrets, task bodies, or credentials. A user Skill may choose a worker and produce this report, but it cannot change the acceptance predicate.
