# E2E Suite Orchestration

How to turn Project Work user journeys into one (or a few) minimal-path
**human_path** UI suites with screenshot checkpoints—**authoring missing tests
as needed**.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-e2e-test-campaign",
  referenceId: "e2e-suite-orchestration"
)
```

Also load `e2e-user-flow-coverage` before claiming `coverage_loaded: true`.

Skipping orchestration fails closed as `e2e_campaign_suite_unorchestrated`.

## Goals

1. **Full user-flow coverage** — Every adopted Project Work journey mapped or
   explicitly deferred (see `e2e-user-flow-coverage`).
2. **Author gaps** — Write UI E2E tests when inventory has no case for a journey.
3. **Minimal path** — Shared session / ordered journeys (launch → core ops →
   settings).
4. **Human path** — Real UI affordances; not service_path-only IT.
5. **Checkpoints** — Non-empty screenshot steps for every covered journey.

## Inventory + Authoring

Collect candidates from:

- Coverage matrix required sources (Project Work journeys, acceptance, etc.)
- Repository `e2e/` trees; Flutter UI `integration_test/` journeys; Playwright
- Project Work `engineering.quality_gates.e2e_tests`
- Task Delivery paths for authored E2E cases

Then **close gaps by writing tests**. Do not treat service_path IT as E2E.

## Suite Plan Schema

```yaml
schema: granoflow_e2e_suite_plan_v1
contract_loaded: true
orchestration_loaded: true
coverage_loaded: true
display_mode: visible_window # default when omitted; headless forbidden
run_command: flutter drive ... # or headed Playwright / visible host driver
# covered journeys in coverage_matrix need interaction_surface
# (in_app_ui|os_chrome|mixed) and os_chrome_verification when OS chrome
coverage_matrix: # granoflow_e2e_coverage_matrix_v1 object
  schema: granoflow_e2e_coverage_matrix_v1
  sources_loaded: []
  required_journeys: []
  authoring:
    tests_written_or_updated: true
    paths: []
ship_bar: market_smoke # market_smoke | form_factor_smoke | full_campaign
host_matrix: # granoflow_verification_host_matrix_v1; see e2e-host-capabilities
  schema: granoflow_verification_host_matrix_v1
  derived_from: []
  concurrency: parallel_when_capable
  hosts: []
test_layer: e2e
interaction_fidelity: human_path
cases: []
order: []
checkpoints: # required non-empty
  - step_id: home_loaded
    capture: screenshot
    vision_criteria: "Home screen with primary nav visible"
```

Lint:

```text
python3 skills/granoflow-e2e-test-campaign/scripts/lint_e2e_campaign_artifacts.py \
  --kind suite_plan --project-work path/to/project-work.yaml path/to/suite-plan.yaml
```

When `host_matrix` is present, every `covered` journey in `coverage_matrix`
**Must** list non-empty `host_ids`. Prefer `parallel_when_capable` when multiple
hosts are `available`.

## Interaction Fidelity

| Value        | Policy                                                                |
| ------------ | --------------------------------------------------------------------- |
| `human_path` | **Default.** Real UI taps/clicks/typing in a **visible** window.      |
| `hybrid`     | Mostly human_path; limited programmatic shortcuts documented in plan. |
| `route_fast` | Faster navigation with explicit justification in plan notes.          |

`service_path` fails closed as wrong layer for this skill. Headless widget tests
and headless browsers fail closed as `e2e_campaign_headless_ui_forbidden` when
any journey is `covered`.

### Entry style

| Value            | Policy                                                        |
| ---------------- | ------------------------------------------------------------- |
| `human_path`     | **Default.** Navigate like a user.                            |
| `route_shortcut` | Needs `route_shortcut_justified` under `human_path` fidelity. |

## Minimal-Path Ordering

DAG from `produces` → `requires` when tokens are present; otherwise keep
journey order that matches daily use. Prefer one shared app session.

## Rewriting Tests

Allowed and expected: merge journeys, shared fixtures, stabilize selectors,
replace route jumps with UI steps for the asserted behavior. Record edits in
the change report. Fix product bugs discovered while wiring coverage under the
campaign auto-drive loop—do not leave broken journeys as silent gaps.
