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

## Delivery Reconciliation

Task Delivery and the acceptance report must compare forecast with actual:

- files and symbols changed, added, or intentionally left unchanged;
- actual final sizes and soft/hard results;
- planned splits and the responsibility they now own;
- every unplanned touchpoint and its authorization or residual state;
- gate commands actually run and their results; and
- configured versus `recorded_pending_enforcement` status.

A green test suite does not erase a structural hard-limit failure, and a line
count does not replace semantic minimum-change or real user-surface evidence.
