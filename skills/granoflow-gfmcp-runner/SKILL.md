---
name: granoflow-gfmcp-runner
description: Poll and safely execute Granoflow tasks carrying the GFMCP tag through the local HTTP API.
---

# Granoflow GFMCP Runner

Use this skill when installing, operating, or diagnosing the optional GFMCP automatic task worker. The worker polls Granoflow every five minutes, considers only pending tasks tagged `GFMCP`, and delegates one eligible task at a time to an authorized local agent.

## Keyword

- `#gfmcp-runner`
- `#gfmcp`
- `#gfmcp-worker`

## Safety Contract

- The tag is an eligibility signal, not blanket authorization.
- Before any phase that needs authorization, re-read the delegated owner receipt
  and run `granoflow-delegated-authorization`'s validator. Continue only on
  `decision=allowed`; `decision=denied` routes to the existing visible waiting
  workflow. The worker never constructs or confirms its own envelope.
- Call `POST /v1/ai-agent/gfmcp/prepare` before polling. Granoflow owns the localized tag description template.
- Call `POST /v1/sync/gfmcp-safe-run` before reading candidates. Granoflow decides whether cloud sync is allowed; guests continue locally and uncertain authorization fails closed.
- Never print API tokens, task bodies, private failure details, or agent transcripts.
- Safe local inspection and reversible workspace edits may proceed. Publishing, payment, login, external messages, destructive changes, secrets, or broadened scope require explicit user authorization.
- Missing necessary information must be written into the task as a concise waiting/blocker note. Do not invent credentials or business choices.
- A task is complete only after Granoflow API readback reports `status=done`. An agent process exit code is not completion evidence.
- A task with Plan nodes must write and content/hash-readback Task Delivery before the final required node, then complete only through NodeService. A node-less compatibility task may use one finish call after its applicable Delivery gate.
- Ordinary completion does not create deep Task Review or a new Card Checkpoint. It consumes the Delivery checkpoint already recorded by the task workflow.
- An unattended worker may read linked cards and record phase candidates, but it cannot infer approval for card writes. Delegate every card search, draft, preview, confirmation, and write to `granoflow-review-card-draft`; record unapproved operations as deferred and never create hidden card drafts or cards.
- An unattended worker never starts a daily review, drafts mood/efficiency notes, or writes a journal. If an interactive user separately requests one, delegate to `granoflow_daily_review_skill`.

## Run

Preview without writes or agent execution:

```bash
npx -y @granoflow/mcp-server gfmcp-runner --dry-run --once
```

Run continuously at the default five-minute interval:

```bash
npx -y @granoflow/mcp-server gfmcp-runner --workspace /absolute/project/path
```

Inspect the real runner process, current phase, last and next check, current task
lease, last result, and bounded recent events:

```bash
granoflow-gfmcp-runner --status
```

Request a graceful stop. The runner finishes its current finite agent execution,
or wakes from its interruptible idle wait, then records `stopped` and exits:

```bash
granoflow-gfmcp-runner --stop
```

The visible phase machine is `idle -> polling -> executing -> verifying`, then
either an immediate recheck after `task_completed` or `waiting` until the next
five-minute check. Only verified completion skips the wait; failures and empty
queues cannot create a hot loop.

Checkpoints:

- Call `POST /v1/ai-agent/gfmcp/prepare` before polling.
- Call `POST /v1/sync/gfmcp-safe-run` before reading candidates; uncertain authorization fails closed.
- `--dry-run --once` must not write or execute agents.
- `--status` must distinguish a live lock owner from stale PID/state data.
- Graceful `--stop` finishes the current execution or wakes idle wait before exit.

The runner uses `GRANOFLOW_API_BASE_URL` and `GRANOFLOW_API_TOKEN` through the local API contract. State, leases, retry fingerprints, and the process lock stay in a private local state directory. See [runtime contract](references/runtime-contract.md).

Codex cron/heartbeat automation is an optional wake-up layer, not proof that a
runner is alive. A scheduler must invoke this runner with `--once` instead of
claiming GFMCP tasks directly, so every entry path shares the process lock,
lease, completion readback, and visible event history.

## Agent Execution

The default executor invokes `codex exec` with a bounded prompt that requires `granoflow-task-runner`. Override the executable with `--executor-command` only when the replacement accepts the generated prompt as its final argument and follows this same safety contract.

If the task instruction uses `gf`, `gf做`, or another lifecycle shortcut, read
`granoflow_task_orchestrator_skill` to resolve the route and stopping point.
The `GFMCP` tag still supplies eligibility only; it cannot activate
`gf-local-safe-v1` or replace a direct current command or validated delegated
receipt.

After three identical unresolved outcomes, the worker writes a stable sanitized blocker section to the task and pauses that task until its task fingerprint changes. Other eligible tasks remain runnable.

Checkpoints:

- Re-read delegated authorization receipt before any phase that needs authorization; continue only on `decision=allowed`.
- Task completion requires Granoflow API readback `status=done`; agent exit code is not proof.
- After three identical unresolved outcomes, write a stable blocker and pause that task until fingerprint changes.

## References

- Read [runtime contract](references/runtime-contract.md) for phase machine, leases, retries, and local state layout.

## Success Criteria

- Poll interval defaults to 300 seconds.
- Only pending `GFMCP` tasks are selected.
- Sync capability is decided by the app, not guessed by the worker.
- Concurrent workers cannot execute the same local queue.
- Retries are bounded and persisted.
- Completion and blocker writeback are observable from the Granoflow Local HTTP API.
- `--status` distinguishes a live lock owner from stale PID/state data.
- A completed task is followed by an immediate queue check; idle queues wait 300 seconds.
