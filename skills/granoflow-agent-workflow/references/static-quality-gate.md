# Static Quality Gate

Language-agnostic **static hygiene** gate for software projects: lint, format
check, and type/static analysis. Examples of stack tools (never hardcode one
stack into Skills):

| Stack hint     | Typical `type_or_static_check`       | Typical `lint` / `format_check`                             |
| -------------- | ------------------------------------ | ----------------------------------------------------------- |
| Flutter / Dart | `flutter analyze` / `dart analyze`   | analyze may cover lint; `dart format --set-exit-if-changed` |
| TypeScript     | `tsc --noEmit` / `npm run typecheck` | eslint; prettier `--check`                                  |
| Python         | mypy / pyright                       | ruff check; ruff format `--check`                           |
| Rust           | `cargo clippy` / `cargo check`       | clippy; `cargo fmt --check`                                 |
| Go             | `go vet`                             | golangci-lint; gofmt                                        |

Prefer a single repository `full_gate` (e.g. `npm run check`) when it already
includes these checks. Do **not** invent a parallel Flutter-only rule in Skills.

## Mandatory Load

Load before claiming Layer A Delivery close, Layer B milestone acceptance, or
最终交付 complete for a software project:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "static-quality-gate"
)
```

Skipping the load when claiming those stages fails closed as
`static_quality_gate_unread`.

## Project Work Lock (init)

During software Project Definition Step 1, Agent **Must** persist executable
commands under `engineering.quality_gates`:

1. **Preferred:** non-empty `full_gate` that the Agent verifies includes lint +
   format + type/static (record that composition in notes or command comments).
2. **Else:** non-empty union of `lint`, `format_check`, and
   `type_or_static_check` (at least one command in `type_or_static_check` **or**
   a `full_gate` that clearly owns static analysis).

Both empty → `quality_gates_unconfigured`. Do not start automated implement.

Optional Project Work field (documented under `quality_gates`):

```yaml
layer_a_scope: full # default; or task_owned when the project explicitly opts in
```

`task_owned` is allowed **only** when Project Work sets `layer_a_scope:
task_owned` with a short basis (large monorepo). Layer B and最终交付 **always**
use `scope: full`.

Also bind the hygiene suite into:

- `required_before.task_completion` — Layer A
- `required_before.milestone_acceptance` — Layer B
- `required_before.project_completion` — 最终交付

Empty `required_before` lists are filled at init by copying the resolved
hygiene command set (or a pointer note that `full_gate` satisfies them).

## When To Run

| Stage            | Required                                                                                  | Scope                                      |
| ---------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------ |
| Layer A Delivery | Yes                                                                                       | `full` by default; `task_owned` only if PW |
| Layer B          | Yes (hard, with IT + matrix)                                                              | **Always `full`**                          |
| 最终交付         | Yes (or reuse Layer B evidence if no code change since that run and evidence still valid) | **Always `full`**                          |

Unit / IT / E2E green **does not** substitute for this gate.

## Evidence Artifact

Record a machine-readable block on Delivery (Layer A), Milestone Work /
`milestone_it_acceptance` (Layer B), or final-delivery closing evidence:

```yaml
quality_gate_run:
  schema: granoflow_quality_gate_run_v1
  contract_loaded: true
  for_stage: layer_a | layer_b | final_delivery
  source: full_gate | composed
  commands:
    - flutter analyze
  scope: full | task_owned
  exit_code: 0
  issue_count: 0
  summary: "0 issues"
  summary_path: null # optional log under temp/
  ran_at: <ISO-8601>
  # Only when tool/host truly cannot run (not “warnings later”):
  # residual: { class: blocked_external, basis: "..." }
```

Lint:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_quality_gate_run.py \
  --run path/to/quality-gate-run.yaml \
  --gate layer_b \
  --project-work path/to/project-work.yaml
```

Project Work config-only:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_quality_gate_run.py \
  --project-work path/to/project-work.yaml \
  --require-configured
```

## Pass / Fail Rules (hard)

1. Commands must match the locked Project Work hygiene suite (`full_gate` or
   composed slots). Invented one-off commands without PW lock →
   `static_quality_gate_commands_mismatch`.
2. `exit_code` Must be `0`.
3. `issue_count` Must be `0`. Tools that emit warnings/info issues with exit 0
   still fail this gate when `issue_count > 0` (treat warnings as failure).
4. Claiming green while skipped → `static_quality_gate_skipped`.
5. Non-zero exit or issues → `static_quality_gate_failed`.
6. Allowed residual class for **not running** is only `blocked_external` (tool
   missing / host cannot execute). Parking analyzer debt as residual →
   `static_quality_gate_failed` / `functional_residual_forbidden`.

## Stage Coupling

- **Layer A:** Delivery / `acceptance_report` Must include a lint-clean
  `quality_gate_run` with `for_stage: layer_a` before task closeout.
- **Layer B:** Milestone acceptance = IT suite green **and** matrix `green`
  **and** lint-clean `quality_gate_run` with `for_stage: layer_b`,
  `scope: full`. See `milestone-integration-acceptance`.
- **最终交付:** Require `for_stage: final_delivery` **or** an explicit reuse
  record pointing at the Layer B run SHA/path with `code_unchanged_since: true`
  and matching commands.

## Fail-Closed Codes

| Code                                    | When                                                             |
| --------------------------------------- | ---------------------------------------------------------------- |
| `static_quality_gate_unread`            | Reference not loaded when claiming a gated stage                 |
| `quality_gates_unconfigured`            | Software PW has empty `full_gate` and empty hygiene slot union   |
| `static_quality_gate_skipped`           | Stage claimed without a `quality_gate_run` block                 |
| `static_quality_gate_failed`            | Non-zero exit, `issue_count > 0`, or analyzer debt as residual   |
| `static_quality_gate_commands_mismatch` | Run commands not derived from locked PW hygiene suite            |
| `static_quality_gate_scope_invalid`     | Layer B / final used `task_owned`, or Layer A used it without PW |
| `static_quality_gate_lint_failed`       | Evidence / PW lint script `ok: false`                            |

## Must Not

- Hardcode `flutter analyze` (or any single stack) into Skill prose as the only
  allowed command.
- Skip static hygiene because unit tests or IT are green.
- Treat “ran analyze” as pass while warnings/issues remain.
- Use Layer A `task_owned` at Layer B or最终交付.
- Ask the user to “ignore warnings for now” as acceptance.
