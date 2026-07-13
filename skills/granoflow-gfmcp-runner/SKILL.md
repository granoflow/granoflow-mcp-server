---
name: granoflow-gfmcp-runner
description: Poll and safely execute Granoflow tasks carrying the GFMCP tag through the local HTTP API.
---

# Granoflow GFMCP Runner

Use this skill when installing, operating, or diagnosing the optional GFMCP automatic task worker. The worker polls Granoflow every five minutes, considers only pending tasks tagged `GFMCP`, and delegates one eligible task at a time to an authorized local agent.

## Safety Contract

- The tag is an eligibility signal, not blanket authorization.
- Call `POST /v1/ai-agent/gfmcp/prepare` before polling. Granoflow owns the localized tag description template.
- Call `POST /v1/sync/gfmcp-safe-run` before reading candidates. Granoflow decides whether cloud sync is allowed; guests continue locally and uncertain authorization fails closed.
- Never print API tokens, task bodies, private failure details, or agent transcripts.
- Safe local inspection and reversible workspace edits may proceed. Publishing, payment, login, external messages, destructive changes, secrets, or broadened scope require explicit user authorization.
- Missing necessary information must be written into the task as a concise waiting/blocker note. Do not invent credentials or business choices.
- A task is complete only after Granoflow API readback reports `status=done`. An agent process exit code is not completion evidence.
- Record only review-card candidates or wait-state nodes. Delegate every card search, draft, preview, confirmation, and write to `granoflow-review-card-draft`; never create hidden card drafts or cards.

## Run

Preview without writes or agent execution:

```bash
granoflow-gfmcp-runner --dry-run --once
```

Run continuously at the default five-minute interval:

```bash
granoflow-gfmcp-runner --workspace /absolute/project/path
```

The runner uses `GRANOFLOW_API_BASE_URL` and `GRANOFLOW_API_TOKEN` through the local API contract. State, leases, retry fingerprints, and the process lock stay in a private local state directory. See [runtime contract](references/runtime-contract.md).

## Agent Execution

The default executor invokes `codex exec` with a bounded prompt that requires `granoflow-task-runner`. Override the executable with `--executor-command` only when the replacement accepts the generated prompt as its final argument and follows this same safety contract.

After three identical unresolved outcomes, the worker writes a stable sanitized blocker section to the task and pauses that task until its task fingerprint changes. Other eligible tasks remain runnable.

## Success Criteria

- Poll interval defaults to 300 seconds.
- Only pending `GFMCP` tasks are selected.
- Sync capability is decided by the app, not guessed by the worker.
- Concurrent workers cannot execute the same local queue.
- Retries are bounded and persisted.
- Completion and blocker writeback are observable from the Granoflow Local HTTP API.
