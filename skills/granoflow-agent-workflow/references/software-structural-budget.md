# Software Structural Budget

Use this reference as the single owner for software-project structural limits.
Project Definition, Task Work Planning, execution handoff, Delivery, and
acceptance reports reference this contract instead of copying their own numeric
policy.

## Project Init Selection

Complete structural-budget selection during software Project Definition or
repository initialization. This is not the `Initialize Granoflow` first-run
installation flow.

Use this precedence:

1. explicit user limits;
2. stricter repository rules, lint configuration, CI, hooks, or documented
   project commands;
3. official ecosystem guidance with an actual numeric rule;
4. mainstream ecosystem convention; and
5. the Granoflow fallback profile below.

Do not claim that an ecosystem has an official line limit when its linter merely
offers a configurable rule. When the user has not supplied a limit, selecting
and recording a reasonable technical default does not require confirmation.
Show the selected values, source, and any adjustment as an initialization
notice, then continue.

Use physical lines for the fallback profile:

| Role              | File soft/hard | Function or method soft/hard |
| ----------------- | -------------- | ---------------------------- |
| production source | 400 / 600      | 60 / 100                     |
| tests             | 700 / 1000     | 100 / 150                    |

An Agent may tighten or slightly relax a fallback for a language or file role
only when it records the exact values and reason. It must never relax an
existing repository hard rule. Generated code, vendored code, lock files,
snapshots, and migration dumps are exempt only when their detection and reason
are recorded; ordinary source does not become exempt because it is difficult to
split.

Project Work must persist:

- `selection_mode` and `threshold_source`;
- `measurement=physical_lines`;
- selected file and function/method soft and hard limits by role;
- exclusions and their detection rule;
- legacy violation policy;
- enforcement status and real gate commands; and
- the initialization notice timestamp or evidence reference.

Use `configured` only when an executable repository gate exists and was
verified. Use `recorded_pending_enforcement` when Project Definition can record
the policy but the current action does not authorize repository writes. When
repository initialization does authorize writes, prefer the existing linter or
unified project script and add the least invasive compatible gate. Never report
a documented number as an installed gate.

For this MCP server, the configured enforcement entrypoint is `npm run check`.
Its lint stage must enforce the hard physical-line limits for ordinary source
and tests. The lint result is a structural test result, not permission to split
code mechanically: a failure requires a responsibility-based redesign and a
new or updated Structural Change Forecast before the next edit.

## Soft, Hard, And Legacy Semantics

- Soft-limit crossing requires a split decision or a recorded responsibility-
  based reason to keep the unit together.
- A new file, function, or method must not exceed its hard limit.
- Directly modified legacy code already above a hard limit must not grow. Split
  the touched responsibility when that can be done inside the confirmed scope;
  otherwise record the residual and stop before claiming structural closure.
- Unrelated legacy violations do not authorize a whole-repository cleanup and
  do not block a narrowly scoped task by themselves.

Split only along a real seam such as domain responsibility, protocol or
serialization, storage or IO, side effect, UI composition, or policy decision.
Mechanical line splitting, random helper extraction, wrapper-only indirection,
and moving code without reducing responsibility are threshold bypasses.

## Hard Gate (fail closed)

Any software task that will edit code, tests, build files, or engineering
workflow contracts **must** complete this gate. Soft reminders are not enough.

| Phase                                                 | Required state                                                                                                                                                                | Fail closed                        |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Before `readiness_grill_status: passed`               | Task Work contains a complete `Structural Change Forecast` section; set `structural_forecast_status: present_in_plan`                                                         | `structural_forecast_missing`      |
| Immediately before the **first** code/test/build edit | Show that forecast to the user as a non-confirming notice in the same turn, then set `structural_forecast_status: notice_emitted` and `structural_forecast_notice_emitted_at` | `structural_forecast_not_shown`    |
| Before Delivery / acceptance closure                  | Reconcile planned vs actual forecast; set `structural_forecast_status: reconciled`                                                                                            | `structural_forecast_unreconciled` |
| Software Delivery with code change                    | Upload `acceptance_report` HTML with structural + minimum-change reconciliation                                                                                               | `acceptance_report_missing`        |

Rules:

1. Do **not** open, write, or patch repository files for implementation while
   `structural_forecast_status` is `missing`, `not_applicable` (when software
   edits are in scope), or `present_in_plan`. Only `notice_emitted` (or later
   `reconciled`) authorizes the first edit.
2. `planning_status: not_required` does **not** waive the gate. Light software
   work still needs a compact forecast covering every file/symbol that will
   change.
3. Unattended / `gf做` / delegated authorization does **not** waive display or
   status updates. Show the notice, stamp `notice_emitted`, then continue.
4. A forecast that only cites line counts, or proposes mechanical
   one-file-per-helper extraction, is not execution-ready: revise before
   Readiness may pass.
5. Hosts that can enforce tool policy should refuse edit tools until
   `notice_emitted`; Skill text alone still fails closed with the codes above
   when the Agent skips the gate.

Before the first edit of every software task, the agent must display a
Structural Change Forecast as a non-confirming notice. The forecast must state
the current and intended responsibility of every touched or new file and
symbol, the real seam for each split, the projected size, and why the proposed
shape is the smallest complete iteration. The agent must revise the forecast
before editing when the readiness review finds a hard split, mixed
responsibilities, or an unexplained boundary.

## Planning Forecast

Before executing a software Plan, inspect the current repository and render one
`Structural Change Forecast` containing:

- every expected existing and new file;
- the class, function, method, component, test, or document section expected to
  change;
- its current responsibility and current measured size when available;
- the intended change and projected size or delta;
- the applicable soft/hard limit and source;
- the responsibility seam used if a split is expected;
- why this is the smallest complete iteration; and
- protected files, symbols, APIs, schemas, dependencies, and user-visible
  surfaces that must remain unchanged.

This forecast is an execution notice, not a user-confirmation gate. After a
confirmed Plan and passing Readiness Grill, show it and continue. Unattended
mode does not suppress the notice and must not create an artificial confirmation
node for it.

Exact symbol names may remain `expected` when discovery is incomplete. Do not
invent certainty. During execution, announce a newly necessary file or symbol
before changing it and update the forecast. Continue without confirmation only
when it remains inside the confirmed Outcome, allowed touchpoints, structural
budget, and authorization. A new module, public API, schema, dependency,
architecture boundary, or protected surface is scope drift and keeps the
existing confirmation rules.

## Directory Structure Ownership (Project Work lock)

When Project Work has a confirmed `engineering.directory_structure` (software
init Engineering Acceptance Pack accepted), later software tasks **Must** place
new paths under declared `roots` / ownership rules.

1. Structural Change Forecast entries for **new** files must cite the owning
   root and module when Project Work locks exist.
2. Inventing a new **top-level** root (or violating `forbidden_catch_all_names`
   without an recorded exception) is out of bounds: revise the forecast, or
   reopen Project Work / regenerate the Engineering Acceptance Pack—do not
   silently scaffold a parallel layout.
3. Leaf growth inside an existing root is allowed when the forecast states the
   responsibility seam; do not treat empty historical `roots` as permission to
   invent structure when locks are present.

## Delivery Reconciliation

Task Delivery and the acceptance report must compare forecast with actual:

- files and symbols changed, added, or intentionally left unchanged;
- actual final sizes and soft/hard results;
- planned splits and the responsibility they now own;
- every unplanned touchpoint and its authorization or residual state;
- gate commands actually run and their results; and
- configured versus `recorded_pending_enforcement` status.

Set `structural_forecast_status: reconciled` only after that comparison is
written into Delivery (and the acceptance report when software profiles apply).
Missing comparison, missing `notice_emitted` evidence, or a green test suite
used as a substitute for reconciliation fails closed as
`structural_forecast_unreconciled`. A line count does not replace semantic
minimum-change or real user-surface evidence.
