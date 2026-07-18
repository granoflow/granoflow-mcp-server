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

For software work, every mode shows the current `Structural Change Forecast`
immediately before the first edit. This is an execution notice, not a
confirmation request. Unattended mode continues after the notice and must not
create an artificial confirmation node. A newly discovered touchpoint is
announced before editing and follows the existing scope-drift boundary.

Use `layered_handoff` only after the user explicitly requests it. Every worker
declares one or more capability lanes and acts only when the first unfinished
eligible node matches the explicit contract version:

- `batch_v2` uses `[analysis]`, `[plan]`, `[dev]`, `[test]`,
  `[integration]`, `[user]`, and `[action]`.
- `[analysis]`: problem definition and evidence.
- `[plan]`: architecture and executable plan.
- `[dev]`: implementation and preparation of ordinary/integration tests.
- `[test]`: ordinary unit, type, lint, build, and deterministic test execution.
- `[integration]`: actual integration, screenshot, and runtime evidence capture.
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
is needed. It summarizes:

- code changes;
- database/schema changes or an explicit no-change statement;
- workflow changes;
- the planned-versus-actual minimum-change budget, including required changes,
  allowed touchpoints used, protected surfaces checked, and every unplanned
  delta with its authorization or residual status;
- the planned-versus-actual structural budget from
  `software-structural-budget.md`, including final sizes, limit results,
  responsibility splits, and verified gate commands;
- automated test/static-gate evidence;
- integration status and script static-check evidence;
- screenshot status and only the key screenshots when present.

When integration or screenshots are unnecessary, record `not_required`, a
non-empty reason, and alternative evidence. When scripts are prepared but not
run in the current task, record `planned_not_run`; never label static inspection
as runtime success.

The App owns upload validation, encrypted storage, current replacement, SHA-256
readback and preview. Acceptance binds the exact current SHA. A replacement is
unaccepted until confirmed again. The App Viewer disables JavaScript, network
connections and external navigation. A user may request changes; the resulting
task binds the report attachment id and SHA so later workers know which evidence
was reviewed.

Actual integration or screenshot script execution belongs to a new `[test]`
task. Generating, uploading, previewing or accepting the HTML does not run those
scripts.
