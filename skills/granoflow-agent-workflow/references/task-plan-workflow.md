# Task Plan Workflow

Use this owner workflow after `analysis_status=finalized`, `decision=proceed`, and `planning_readiness=yes`. Read [task-plan-template.md](task-plan-template.md) and the matching learning or software-development profile.

## Lifecycle

`draft -> grill_in_progress -> awaiting_confirmation -> confirmed -> executing -> awaiting_manual_acceptance | blocked | completed`

Do not execute before explicit Plan confirmation. Plan confirmation authorizes only operations named in the Authorization Matrix; publishing, sending, payment, login, secrets, deletion, and other irreversible actions retain their own gates.

## Author And Confirm

1. Re-read the latest Granoflow task, nodes, description, attachments, project/milestone context, and active analysis final.
2. Inherit Outcome, Evidence, Boundaries, Risks, and user decisions without silently changing them.
3. Write 3–7 major nodes. Each node needs a concrete deliverable, a testable delivery standard, Evidence, and a handoff proving downstream startup readiness.
4. Mark manual acceptance as an independent `user_manual` node titled `验收：<object>` with `non_blocking_acceptance` dependencies.
5. Grill dependencies, authorization, false-success paths, rollback, manual acceptance, cross-device changes, and task completion.
6. Obtain explicit confirmation.
7. Save an immutable `task-plan-vNN.md`, upload it with `granoflow_task_attachment_add_markdown`, list attachments to verify it, and point the description summary to the single active version. A material amendment creates the next version and records `supersedes`; progress alone does not rewrite the attachment.

## Granoflow Nodes

Read the latest task and call `granoflow_task_node_batch_create` with a stable Plan-version idempotency key and `expectedTaskUpdatedAt`. The batch must be atomic. Plan Node N maps to exactly one Granoflow node.

Before every node start or mutation, after any wait, and before task completion:

1. re-read task, nodes, attachments, and description;
2. accept compatible user/cross-device changes;
3. stop duplicate work when a node is already `finished`;
4. enter Plan amendment when a change alters scope, dependencies, standards, or final Evidence;
5. on HTTP 409 `task_state_conflict`, re-read and reconcile instead of replaying the old payload.

After executing a node:

1. verify its delivery standard and Evidence;
2. verify downstream execution startup requirements;
3. call `granoflow_task_node_update` with the latest revision and `status=finished`;
4. list nodes and confirm the persisted status;
5. update only the controlled description summary;
6. continue to the next safe execution node.

User manual acceptance remains pending and does not block later safe nodes. When AI work is exhausted, write the factual review-so-far and use `awaiting_manual_acceptance`. The user may finish acceptance on any synced device.

## Task Completion

NodeService is the only completion path. Write the factual task review before finishing the last AI node. When every active required node becomes `finished`, Granoflow's existing node-progress service completes the parent task. Do not call a second task-completion endpoint. Re-read the task and require the persisted completed state.

If the user finishes the last manual node later, normal Granoflow sync and parent-task propagation complete the task without a resident Agent. A later Agent may append a review amendment, but review polish never blocks completion.

## Description Summary

Maintain at most one marker block and preserve all text outside it:

```text
<!-- granoflow-plan-summary:start -->
- 状态: <runtime status>
- Plan: <active attachment id/name or safe path>
- Plan 版本: <vNN>
- Supersedes: 无 | <prior attachment>
- 文档状态: attached | local_reference | attachment_upload_failed
- 执行就绪: <state>
- 当前节点: 无 | <Node N: title>
- 节点进度: <finished>/<total>
- 待手工验收: 无 | <count and titles>
- 缺失信息: 无 | <summary>
- 待授权: 无 | <summary>
- 下一步: <state-level action>
<!-- granoflow-plan-summary:end -->
```

Invalid, duplicate, reversed, or nested markers return `plan_summary_markers_invalid` and stop automatic description writes.
