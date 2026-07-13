# Task Plan Workflow

Use this owner workflow after `analysis_status=finalized`, `decision=proceed`, and `planning_readiness=yes`. Read [task-plan-template.md](task-plan-template.md), then append zero or more profiles in the fixed order learning, software development.

## Lifecycle

`draft -> grill_in_progress -> awaiting_confirmation -> confirmed -> executing -> awaiting_manual_acceptance | blocked | completed`

Do not execute before explicit Plan confirmation. Plan confirmation authorizes only operations named in the Authorization Matrix; publishing, sending, payment, login, secrets, deletion, and other irreversible actions retain their own gates.

## Author And Confirm

1. Re-read the latest Granoflow task, nodes, description, attachments, project/milestone context, active analysis final, and its Card Checkpoint.
2. Inherit Outcome, Evidence, Boundaries, Risks, and user decisions without silently changing them.
3. Write 3–7 major nodes. Each node needs a concrete deliverable, a testable delivery standard, Evidence, and a handoff proving downstream startup readiness.
4. Mark manual acceptance as an independent `user_manual` node titled `验收：<object>` with `non_blocking_acceptance` dependencies.
5. Load the sole card authoring owner, run the Plan Card Checkpoint, and record the Knowledge And Card Plan. Plan confirmation does not approve future Execution card operations.
6. Grill dependencies, authorization, false-success paths, rollback, manual acceptance, cross-device changes, and task completion.
7. Obtain explicit confirmation.
8. Save an immutable `task-plan-vNN.md`, upload it with `granoflow_task_attachment_add_markdown` using an idempotency key, task revision, and expected local hash, then read the attachment content/hash back. A filename-only list or HTTP success is insufficient. Point the description summary to the single active version. A material amendment creates the next version and records `supersedes`; progress alone does not rewrite the attachment.

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
2. when its Knowledge/Card Delta Trigger fired, run the Execution Card Checkpoint; otherwise record that no node-level checkpoint was triggered;
3. verify downstream execution startup requirements;
4. call `granoflow_task_node_update` with the latest revision and `status=finished`;
5. list nodes and confirm the persisted status;
6. update only the controlled description summary;
7. continue to the next safe execution node.

User manual acceptance remains pending and does not block later safe nodes. The user may finish acceptance on any synced device. Before every write, use Granoflow's latest state rather than an Agent cache.

## Task Completion

For a node-backed task, create and verify the versioned Task Delivery, including its Card Checkpoint, before finishing the final required execution node. NodeService is the only completion path: when every active required node becomes `finished`, Granoflow completes the parent task. Do not call a second completion endpoint. Re-read the task and require the persisted completed state.

For a genuinely node-less compatibility task, `granoflow_task_finish` may complete the task after its applicable Delivery gate. Completion reads and summarizes the Delivery Card Checkpoint; it does not create a new checkpoint, Task Review, or card-write batch. A Delivery checkpoint may be explicitly deferred without blocking completion. Legacy inline review parameters are used only when the user explicitly requested and approved inline review.

If the user finishes the last manual node later, normal Granoflow sync and parent-task propagation complete the task without a resident Agent. Deferred Task Review is a separate later workflow and never blocks completion.

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
