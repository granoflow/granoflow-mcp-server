# Thread Execution Modes And Acceptance Reports

## Mode Selection

Use `interactive` when the user did not explicitly choose another mode. Do not
ask the user to select a mode for ordinary work.

Use `unattended` only after the user explicitly requests it. At execution start,
report the mode and declare responsible node lanes, allowed actions, stop
conditions, and handoff. Skip ordinary artificial confirmation nodes, including
an orchestration-only confirmation node. Do not skip a real external action:
login, payment, secrets, publish, deploy, destructive change, or external
communication remains `[action]` and requires its actual authority/input.

Read `unattended-interaction-contract.md` and apply its zero-interruption
invariant to the whole run. A same-run direct instruction and a durable
delegated envelope have different persistence, but both use the same blocker
classification and waiting behavior.

For software work, every mode enforces the Hard Gate in
`software-structural-budget.md`: show the current `Structural Change Forecast`
immediately before the first edit, stamp
`structural_forecast_status: notice_emitted`, then edit. This is an execution
notice, not a confirmation request. Unattended mode continues after the notice
and must not create an artificial confirmation node—but skipping the notice or
stamp fails closed as `structural_forecast_not_shown`. A newly discovered
touchpoint is announced before editing and follows the existing scope-drift
boundary.

Use `layered_handoff` only after the user explicitly requests it. Every worker
declares one or more capability lanes and acts only when the first unfinished
eligible node matches the explicit contract version:

- `batch_v2` uses `[analysis]`, `[plan]`, `[dev]`, `[test]`,
  `[integration]`, `[user]`, and `[action]`.
- `[analysis]`: problem definition and evidence.
- `[plan]`: architecture and executable plan.
- `[dev]`: implementation, unit tests, and—only when unit tests are
  insufficient for this task—authoring at most 2 new integration tests
  (do not run those integration tests; see Task Integration Test Policy).
- `[test]`: ordinary unit, type, lint, build, and other deterministic
  non-integration test execution.
- `[integration]`: milestone/cross-task runtime or screenshot evidence when
  separately planned; **not** a license for the Agent to execute the task's
  newly added integration tests (those remain manual).
- `[user]`: real user acceptance; never automatically skipped.
- `[action]`: external or privileged action; never impersonated or claimed.

The old `legacy_v1` contract remains readable for existing tasks:
`[plan]`, `[dev]`, `[test]`, `[confirm]`, and `[action]`. A legacy
`[confirm]` may retain its historical unattended behavior; it must never be
silently reinterpreted as batch_v2 `[user]`.

Prefixes describe responsibilities, never provider/model names. An Agent cannot
reliably identify its own model or reasoning tier. The user or host configuration
chooses models, including a low-cost coding worker and a separate test executor.

When asked, explain the modes in those terms and give the smallest command or
node example that fits the user's intended workflow.

## Eligibility

In explicit unattended/layered modes, unknown or missing prefixes fail closed.
The runner must read the explicit contract version from the current,
hash-verified Task Work before selecting a batch_v2 node.
Select the first pending node only after every preceding required node is
finished. Granoflow App/API node order and status are truth. A Python polling
worker may use same-device process locks and leases, but they are not a
cross-device consistency mechanism.

## Acceptance Report

Every implementation produces a self-contained acceptance HTML in the
`acceptance_report` logical slot, whether or not integration/screenshot testing
is needed. Missing report after code changes fails closed as
`acceptance_report_missing`. It summarizes:

- code changes;
- database/schema changes or an explicit no-change statement;
- workflow changes;
- the planned-versus-actual minimum-change budget, including required changes,
  allowed touchpoints used, protected surfaces checked, and every unplanned
  delta with its authorization or residual status;
- the planned-versus-actual structural budget from
  `software-structural-budget.md`, including final sizes, limit results,
  responsibility splits, and verified gate commands;
- automated test/static-gate evidence (unit/lint/type/build as run by the Agent);
- integration status per Task Integration Test Policy: `not_required` when unit
  tests suffice; or `awaiting_campaign_execution` /
  `awaiting_manual_execution` with paths, recommended `requires`/`produces`,
  recommended `local_machine`, and user-selected `integration_test_device`
  when 1–2 tests were added; never Agent-claimed integration runtime success
  from the feature task;
- screenshot status and only the key screenshots when present.

When integration tests are unnecessary, record `not_required` with the unit-
sufficiency reason. When up to two integration tests were added for this task,
record `awaiting_campaign_execution` (stage-6 campaign auto-drives later)—not
Agent `planned_not_run` as a substitute for the task-local do-not-run rule.
Never label static inspection of an integration script as runtime success.

The App owns upload validation, encrypted storage, current replacement, SHA-256
readback and preview. Acceptance binds the exact current SHA. A replacement is
unaccepted until confirmed again. The App Viewer disables JavaScript, network
connections and external navigation. A user may request changes; the resulting
task binds the report attachment id and SHA so later workers know which evidence
was reviewed.

Task-local integration tests added under the Task Integration Test Policy are
**not** executed inside the feature task; stage `integration_campaign` /
`granoflow-integration-test-campaign` orchestrates and auto-drives them later.
UI E2E screenshots belong to stage `e2e_campaign` /
`granoflow-e2e-test-campaign` (paths under `temp/`). Other screenshot/runtime
evidence still follows its own Plan. Generating, uploading, previewing, or
accepting the HTML does not run integration or E2E campaign scripts.
