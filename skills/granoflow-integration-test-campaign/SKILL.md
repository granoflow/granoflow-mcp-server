---
name: granoflow-integration-test-campaign
description: Run an unattended integration-test campaign—one milestone per round, execute the full suite first, cluster failures into one bug task each, fix through Analysis/execution, then open the next round until all tests pass. Not the task-local write-only integration policy.
---

# Granoflow Integration Test Campaign

Use this Skill when the user **requires running** integration tests as a
campaign (for example: `Run integration test campaign`, `开始集成测试战役`,
`无人值守跑集成测试直到全绿`).

This Skill is **naturally unattended**: after campaign start authorization, do
not ask for ordinary phase confirmations, device re-picks, or manual test
clicks. Loop until the suite is green or a real external blocker is recorded.

## Not This Skill

| Concern                                                          | Owner                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------------- |
| Task-local: judge unit sufficiency, add ≤2 tests, **do not run** | `granoflow-agent-workflow` Task Integration Test Policy    |
| Copy-only / 文字验证: **no** automated tests                     | `user-visible-copy-boundary.md`                            |
| Single-task Analysis/Plan/run                                    | `granoflow-task-orchestrator` + `granoflow-agent-workflow` |
| Create product milestones/tasks portfolio                        | `granoflow-portfolio-orchestrator`                         |

Do not use this Skill to invent copy-string tests or to run tests inside an
ordinary feature task that only _authored_ manual-run integration cases.

## Activation

Examples:

```text
Run integration test campaign
Start unattended integration testing until green
开始集成测试战役
无人值守集成测试，按轮次修 bug 直到全过
```

## Mode: Unattended By Default

- Set campaign `execution_mode: unattended` for the whole loop.
- An explicit unattended declaration authorizes every **solvable** campaign
  step (full suite run, bug clustering, Analysis/fix/Delivery). Read
  `unattended-interaction-contract.md`.
- Skip ordinary `[confirm]` / phase confirmation questions.
- Items that are **externally impossible** (no device/runtime, missing
  user-only secret, store approval) are **deferred**—do not freeze the rest of
  the round or sibling bug tasks. Continue solvable work; end with an
  Unattended Residual Report listing what was not executed.
- Do not pause for the user to manually click through the suite.

## Workflow

Read `references/integration-test-campaign-contract.md` and keep resumable
campaign state after every successful step.

1. **Start gate** — Resolve project; collect the integration suite entrypoints
   (from Project Work `quality_gates.integration_tests`, campaign brief, or
   explicit paths). Recommend device **`local_machine`**; under unattended
   start, adopt that recommendation unless the grant already names another
   `integration_test_device`. Missing suite or device →
   `integration_campaign_suite_unspecified` /
   `integration_campaign_device_unselected`.
2. **Open round milestone** — Each test round is its **own** milestone
   (via `granoflow-milestone-workflow`), named for the round
   (e.g. `Integration test round 1`). Do not reuse a feature milestone as the
   round container.
3. **Run the full suite first** — Execute **all** listed integration tests in
   this round before creating fix tasks. Partial “fix the first failure and
   stop the suite” is forbidden unless the runner hard-crashes; then record
   crash evidence and still cluster from what ran.
4. **Cluster bugs** — Multiple failures often share one root cause. Analyze
   logs/assertions and emit **one bug per distinct root cause**, not one task
   per failing test case. Creating one task per raw failure without clustering
   fails closed as `integration_campaign_bug_clustering_required`.
5. **Author and finish bug tasks** — For each bug, create a quality task
   (`granoflow-task-authoring` / orchestrator), then run Analysis → Plan →
   execution → Delivery → done through `granoflow-task-orchestrator` /
   `granoflow-agent-workflow` under the campaign unattended grant. Ordinary
   unit/lint/build gates apply; do **not** apply the task-local “do not run
   integration tests” rule to **this campaign’s suite runs** (those runs are
   owned by this Skill). Copy-only bugs still follow `copy_change_tests_forbidden`
   (fix by copy review, not new string tests).
6. **Round close** — When every bug task in the round is `done` (App readback),
   close or mark the round milestone complete with suite evidence attached.
7. **Next round** — Open **round N+1** as a **new** milestone, run the **full**
   suite again, and repeat from step 3.
8. **Campaign done** — Stop when a round’s full suite is green (zero failures)
   with recorded commands/evidence. Emit a short campaign summary (rounds,
   bugs fixed, final suite SHA/log refs).

## Delegates To

| Step                           | Skill / contract                                                      |
| ------------------------------ | --------------------------------------------------------------------- |
| Round milestone create         | `granoflow-milestone-workflow`                                        |
| Bug task create                | `granoflow-task-authoring`                                            |
| Bug Analysis / fix / Delivery  | `granoflow-task-orchestrator` + `granoflow-agent-workflow`            |
| Long-running worker (optional) | `granoflow-persistent-milestone-runner`                               |
| Unattended grants              | `granoflow-delegated-authorization` / unattended-interaction-contract |

## Success Criteria

- One milestone per round; full suite run before fix tasks.
- Failures clustered into distinct bug tasks; each bug driven to done.
- Loops until a green full-suite round; no ordinary manual intervention.
- Campaign authorization and device are explicit; secrets never stored in
  Task Work.

## Failure Codes

- `integration_campaign_suite_unspecified`
- `integration_campaign_device_unselected`
- `integration_campaign_authorization_missing`
- `integration_campaign_bug_clustering_required`
- `integration_campaign_round_suite_incomplete`
- `integration_campaign_external_deferred` (item parked; peers continue)
