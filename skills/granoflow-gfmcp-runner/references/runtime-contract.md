# GFMCP Runtime Contract

The worker is an optional Python process shipped with the MCP package. It is not an in-process timer inside the MCP server.

Each cycle performs: health check, GFMCP tag/template preparation, app-owned safe sync, tag-filtered task listing, pending-task selection, local lease acquisition, agent execution, and API readback.

The runner persists a visible phase machine: `idle`, `polling`, `executing`,
`verifying`, `waiting`, and `stopped`. `--status` reports whether the process
lock is currently owned, plus the last known phase, PID, heartbeat, last and
next check, current task id, lease expiry, last stable result code, and at most
50 recent events. Lock ownership is authoritative; a stored PID is diagnostic
only and cannot prove that monitoring is alive.

After API readback verifies `task_completed`, the runner immediately starts a
new cycle. Every other result enters an interruptible wait for the configured
interval, which defaults to 300 seconds. `--stop` writes a private stop request;
it never kills an in-flight agent, but it wakes idle waiting promptly and exits
after the current finite execution boundary.

State is stored atomically as JSON. The process lock prevents two local daemons from owning the queue. A task lease survives crashes until expiry. Retry identity is based on a sanitized outcome fingerprint plus a task-content fingerprint. Editing the task clears a durable blocker.

The worker logs task ids and stable status codes only. It must not log tokens, descriptions, executor prompts, subprocess output, or raw API error bodies.

An external Codex cron or heartbeat may wake the runner with `--once`. It must
not implement a second task-claiming loop in its prompt because bypassing the
runner would also bypass the shared process lock, lease, and event history.

The executor prompt requires the agent to:

1. Load and follow `granoflow-task-runner`.
2. Analyze the selected task before execution.
3. Request authorization for external, destructive, privileged, secret-bearing, or scope-expanding actions.
4. Record necessary questions and real blockers in Granoflow.
5. Read cards when useful, keep unapproved card output as phase candidates or deferred checkpoint data, and delegate authoring to `granoflow-review-card-draft`.
6. Treat API readback as the completion authority.
