# Parallel Task Execution

Use this contract whenever an AI agent is asked to execute two or more current
Granoflow tasks. `doing` is a human focus state, not an AI worker lease and not
an execution-admission gate. AI-owned work normally keeps every task `pending`
until its completion owner changes it to `done`.

## 1. Build The Conflict Inventory

Before dispatching workers, read the current Task Work, dependencies, repository
state, and acceptance requirements for every candidate. Record, without
guessing:

- exact or bounded file and directory write surfaces;
- generated files, lockfiles, manifests, version files, and formatter scope;
- App/API records, attachments, nodes, schemas, migrations, and shared fixtures;
- commands that mutate shared state, Git actions, singleton processes, ports,
  credentials, accounts, deployments, and other external effects;
- upstream inputs, downstream handoffs, and user-only decisions;
- acceptance evidence that one worker could invalidate or consume before
  another worker finishes.

An unknown material write surface is a serialization reason. A broad label such
as `the repository`, `tests`, or `docs` is not enough to prove independence.

## 2. Decide Pairwise Compatibility

For every task pair, classify the relationship as:

- `parallel_safe`: write surfaces and side effects are disjoint, neither task
  depends on the other's unfinished output, and their evidence can be verified
  independently;
- `ordered_dependency`: one task consumes a verified output from the other;
- `write_conflict`: both may change the same file, generated artifact, record,
  schema, fixture, or other shared state;
- `side_effect_conflict`: Git, release, deployment, account, credential,
  singleton-runtime, destructive, or external effects cannot safely overlap;
- `unknown`: evidence is insufficient to rule out a conflict.

Only `parallel_safe` pairs may share a batch. `ordered_dependency`, either
conflict class, and `unknown` must be serialized or replanned into genuinely
disjoint ownership. Read/read overlap is safe unless one reader requires a
snapshot that another worker can invalidate.

Record this compact portfolio evidence in Milestone Work:

```yaml
parallel_execution:
  assessment_version: 1
  assessed_from: [<Task Work attachment ids and repository revision>]
  batches:
    - batch_id: batch-1
      task_ids: [<id>, <id>]
      decision: parallel_safe
      shared_read_inputs: []
      disjoint_write_surfaces: [<bounded surfaces>]
      independent_acceptance: [<evidence ids>]
  serialized_edges:
    - from: <task id>
      to: <task id>
      reason: ordered_dependency | write_conflict | side_effect_conflict | unknown
      evidence: <specific fact>
```

Task Work owns each task's local write-surface declaration. Milestone Work owns
the pairwise decision and batch assignment. Do not duplicate full task plans.

## 3. Dispatch The Whole Safe Batch

When the host supports multiple agents or workers, dispatch every task in one
`parallel_safe` batch concurrently. A host capability limit may reduce actual
concurrency, but it must be reported as `host_capacity_limited`, not disguised
as a task conflict. Each worker receives one task, its exact write boundary,
its dependencies, the batch id, and the stop rule for newly discovered overlap.

Before each material write, re-read the relevant revision. If a worker discovers
an unplanned shared write, dependency, or side effect, it must stop that write,
publish the new conflict fact to the supervisor, and replan the affected batch.
Other still-independent workers continue.

## 4. Keep AI Work Pending Until Completion

After Analysis, Planning, readiness, and authorization pass, AI execution uses
this lifecycle:

1. Capture the actual start instant.
2. Keep the task `pending`; never claim the user's sole `doing` focus slot.
3. Write `startedAt` through `granoflow_task_history_mutate` with an update
   reason that identifies AI execution timing, then read the task back. This is
   a timestamp write, not a status transition or completion claim.
4. Execute, verify, write and hash-read back Task Delivery.
5. Complete through the existing owner: finish the last required node and let
   NodeService complete the parent, or use `granoflow_task_finish` for a
   node-less task.
6. Supply the captured `startedAt` and confirmed `endedAt` to the node-less
   completion action. For node-managed completion, use the dedicated historical
   mutation surface after `status=done` only when readback is missing or differs
   from the captured times.
7. Re-read `status=done`, `startedAt`, `endedAt`, Delivery content/SHA, and nodes.

Never set `doing` for AI execution. Never set `done` with an ordinary task
update. Completion evidence and its existing owner remain mandatory. If the
running App lacks `historical_task_mutations_v1`, keep the captured start time in
the worker's bounded execution evidence and pass it to `granoflow_task_finish`
when available; a node-managed task must report `execution_timestamp_write_blocked`
instead of fabricating readback.

Human manual work keeps the normal `pending -> doing -> done` focus lifecycle;
the App continues to own the `doing` transition's automatic start time.

## 5. Acceptance

Parallel execution is accepted only when:

- every pair in a concurrent batch was explicitly classified `parallel_safe`;
- no unplanned overlapping write or external effect occurred;
- each task has independent Delivery, node, status, and timestamp readback;
- combined integration checks pass after all batch members finish;
- a worker summary, process exit, or elapsed time was never treated as task
  completion.
