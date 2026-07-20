# Integration Test Campaign Contract

Provider-neutral loop for unattended integration-test campaigns. Granoflow
App/API remains source of truth for milestones, tasks, and completion.

## Relationship To Task-Local Policy

Ordinary feature tasks follow Task Integration Test Policy: prefer unit tests,
add at most two integration cases when needed, **do not execute** them, device
chosen by the user (recommend local machine).

This campaign contract is the opposite **execution** path: the user explicitly
starts a campaign to **run** the suite, fix bugs, and re-run until green, with
**no ordinary manual intervention**.

## Campaign State (resumable)

Persist after each successful step (project attachment, controller task, or
managed summary—host chooses one durable place):

```yaml
campaign_id: <stable id>
project_id: <id>
execution_mode: unattended
integration_test_device_recommendation: local_machine
integration_test_device: local_machine | simulator_or_emulator | physical_device | remote_farm | other
suite_entrypoints: [] # commands or paths
authorization_ref: <envelope or grant id; never secret values>
current_round: 1
current_round_milestone_id: null | <id>
phase:
  - awaiting_suite_run
  - clustering_bugs
  - fixing_bugs
  - closing_round
  - complete
  - blocked
round_history: []
# each history row: round, milestone_id, suite_result, bug_task_ids, closed_at
```

## Round Machine

```text
open milestone(round N)
  -> run FULL suite
  -> if green: campaign complete
  -> else: cluster bugs -> create one task per bug
  -> fix all bug tasks to done (unattended)
  -> close round milestone
  -> N = N+1 -> open milestone(round N) -> ...
```

## Full Suite Rule

Before any fix task is created in a round, every suite entrypoint must have a
run attempt recorded (pass/fail/crash). Stopping after the first failure to
avoid running the rest fails closed as
`integration_campaign_round_suite_incomplete` unless the process crashed; then
record the crash and cluster from partial output.

## Bug Clustering Rule

Group failing assertions/cases that share one root cause into **one** bug task.
Evidence for clustering (logs, stack frames, same module/regression) must appear
in the bug task Analysis. One-task-per-failure without justification fails
closed as `integration_campaign_bug_clustering_required`.

## Unattended Fix Loop

For each bug task, use the existing task lifecycle owners under the campaign
grant:

1. Analysis + Analysis Grill (auto-adopt recommendations; no user_only batch
   unless a real blocker).
2. Plan + Readiness as required.
3. Structural Change Forecast hard gate still applies for code edits.
4. Unit/lint/type/build gates run as usual.
5. Delivery + done readback before the next bug, or in parallel only when
   `parallel-task-execution` allows and the campaign grant permits.

Do not ask the user to re-confirm Plan/execution between bugs in the same
authorized campaign.

## Device

Recommend `local_machine` at campaign start. Unattended start adopts the
recommendation when the grant does not override. Changing device mid-campaign
requires a new grant (direction change), not a chat question mid-round.

## Exit

- **Success:** a round completes with zero failing entrypoints and evidence
  attached; `phase: complete`.
- **Deferred external:** device/secret/store walls → record
  `integration_campaign_external_deferred`, continue other solvable bug tasks /
  rounds when possible, and include the item in the final Unattended Residual
  Report. Do not fake green and do not freeze the whole campaign on one
  external item.
