# Persistent Runtime Contract

One runner process owns one milestone-local process lock. Each selected task receives a bounded lease. While a worker runs, the supervisor refreshes `heartbeatAt` and `leaseUntil`; after a crash, another process may recover only after lease expiry.

State is atomically replaced in a private `0700` directory with a `0600` JSON file. It contains milestone/task ids, task fingerprints, lease times, phases, bounded attempt records, and evidence hashes. It never contains task descriptions, worker prompts, subprocess output, credentials, or raw reports.

In `layered_handoff`, each distinct sorted lane set uses its own process-lock
scope on the same machine. This permits a `[dev]` worker and a `[test]` worker to
poll concurrently without letting two processes with the same lane set run.
Granoflow node order and status remain the eligibility truth; the local lock is
only a same-device duplicate-execution defense, not a cross-device lease.

Node titles use an explicit contract version. `legacy_v1` keeps
`[plan]`, `[dev]`, `[test]`, `[confirm]`, and `[action]`; `batch_v2`
uses `[analysis]`, `[plan]`, `[dev]`, `[test]`, `[integration]`,
`[user]`, and `[action]`. Unknown or missing versions/prefixes fail closed
for the new contract. An unfinished `[user]` or `[action]` is never
automatically skipped or claimed by the public runner. Legacy tasks retain
their original `[confirm]` compatibility behavior and are not migrated by
guessing from a title.

## Runtime States

`ready -> running -> retry_wait -> replan_required -> waiting_for_user | accepted`

- `retry_wait`: the attempt produced no accepted completion and is cooling down.
- `replan_required`: three consecutive attempts produced no new evidence; the next worker must diagnose prior strategy classes and choose a materially different path.
- `waiting_for_user`: the replan attempt still produced no new evidence, or the worker reported missing permission/input. The task remains blocked until its Granoflow fingerprint or authorization manifest changes.
- `accepted`: the App/API task is done, Task Delivery is readable with a valid SHA-256 and accepted status, and every returned node is finished.

The runner scans past blocked/cooling tasks and may execute another eligible task. A task count or worker summary never closes the milestone; the normal milestone workflow still owns integration readiness and closure.

## Recovery And Stop Rules

- An expired lease is recoverable; an active lease is not stolen.
- A changed task fingerprint clears task-local retry/wait state.
- Attempt history is capped at 100 records.
- A missing or expired authorization manifest stops execution but not dry-run inspection.
- API evidence errors fail closed.
- Cancellation, revoked authorization, or proven unsafe continuation stops new workers while preserving state for inspection.
