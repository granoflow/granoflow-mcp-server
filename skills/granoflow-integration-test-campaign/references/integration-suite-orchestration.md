# Integration Suite Orchestration

How to turn task-local, disconnected integration tests into one (or a few)
minimal-path **service_path** journeys before a campaign suite run.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-integration-test-campaign",
  referenceId: "integration-suite-orchestration"
)
```

Skipping this load and claiming an orchestrated suite fails closed as
`integration_campaign_suite_unorchestrated` (Suite Plan must set
`orchestration_loaded: true` only after this contract was applied).

## Goals

1. **Minimal path** — Order and merge cases so later steps reuse data and
   session state from earlier ones (create → import → browse → open). Avoid
   “run case → data wrong → tear down → rebuild” loops.
2. **Service path** — Default `interaction_fidelity: service_path`: exercise
   cross-module collaboration through real I/O (filesystem, crypto, catalog,
   repositories, services). **UI taps are not required.** Real UI journeys
   belong to `granoflow-e2e-test-campaign`.
3. **Editable tests** — Rewriting, merging, or splitting test code during
   orchestration is **allowed and expected** when it enables (1) and (2).

## Inventory

Collect candidates from:

- Project Work `engineering.quality_gates.integration_tests`
- Project Work `engineering.quality_gates.integration_test_special_requirements`
  (must load; see `granoflow-agent-workflow/integration-test-special-requirements`)
- Task Delivery / Task Work paths for authored IT (≤2 per feature task)
- Repository trees for integration layer only (`test/integration/`,
  `integration_test/` service journeys). Do **not** treat `e2e/` UI trees as
  integration candidates.

For each case, record at least:

| Field                | Meaning                               |
| -------------------- | ------------------------------------- |
| `id`                 | Stable case id                        |
| `path`               | File or entrypoint                    |
| `requires`           | Tokens that must already exist        |
| `produces`           | Tokens this case creates              |
| `mutates`            | Tokens changed in place               |
| `destroys`           | Tokens removed                        |
| `entry_style`        | `service_path` \| `ui_probe`          |
| `ui_probe_justified` | Required when `entry_style: ui_probe` |

Task-local authoring **should** pre-fill `requires` / `produces` when adding
IT; campaign orchestration fills gaps by reading the tests.

## Minimal-Path Ordering

Build a DAG from `produces` → `requires`. Emit `order` as a topological
journey (or a small set of island journeys when graphs are disconnected).

Rules:

- Every consumer runs after at least one producer of each required token.
- Prefer one shared library/session fixture when safe.
- Push mutually exclusive teardown to the end of the journey.
- Islands that cannot share state keep separate journeys; document why—do not
  silently drop coverage.

Violation → `integration_campaign_order_dependency_violation`.

## Interaction Fidelity

| Value          | Policy                                                                   |
| -------------- | ------------------------------------------------------------------------ |
| `service_path` | **Default / only valid value for this skill.** Real I/O, shared session. |

`human_path`, `hybrid`, and `route_fast` fail closed as
`integration_campaign_fidelity_wrong_layer` (use E2E campaign).

### Entry style

| Value          | Policy                                                               |
| -------------- | -------------------------------------------------------------------- |
| `service_path` | **Default.** Call services/repositories/domain APIs directly.        |
| `ui_probe`     | Rare thin widget mount to assert wiring; needs `ui_probe_justified`. |

`entry_style: human_path` or `route_shortcut` →
`integration_campaign_fidelity_wrong_layer`.

## Rewriting Tests

Allowed edits during orchestration include:

- Merging isolated cases into a multi-step journey file or shared fixture
- Moving seed/setup into earlier journey steps
- Replacing fake corpora with Project Work seed_corpus paths
- Fixing brittle fixtures discovered while wiring the path

Not allowed: deleting coverage without an explicit residual; claiming green
without re-running the orchestrated plan; labeling service journeys as
`human_path`.

## Suite Plan Artifact

```yaml
schema: granoflow_integration_suite_plan_v1
contract_loaded: true
orchestration_loaded: true
special_requirements_loaded: true
special_requirements_applied: [] # ITR-* fail_closed rows that apply to this suite
acceptance_outcomes_loaded: true
user_path_claim: service_layers_only
acceptance_outcomes:
  - id: AO-001
    statement: <user-required real result this suite can prove>
    layer: domain_io
    evidence_kind: real_side_effect
    status: closed # or deferred_e2e for non-domain layers
    case_ids: []
test_layer: integration
interaction_fidelity: service_path
cases: []
order: []
```

Omit vision/screenshot/window fields entirely (E2E-only): `vision_*`,
`screenshot_*`, `screenshots`, `capture_surface`, `window_capability`.

Acceptance Outcomes follow
`granoflow-agent-workflow/acceptance-outcome-contract`: suite technical green
is not enough—closed rows need real side effects; IT must not claim full user
path.

When Project Work lists any `fail_closed` special requirement whose
`applies_when` includes `campaign_suite` or `all_authored_it` (or otherwise
matches inventoried cases), those ids **Must** appear in
`special_requirements_applied`. For `kind: seed_corpus`, seed/import from
`corpus_paths`; do not use `forbidden_substitutes` on the primary path.
`not_app_seed: true` corpora stay fixtures—never create-library app seeds.

Validate with:

```text
python3 skills/granoflow-integration-test-campaign/scripts/lint_integration_campaign_artifacts.py \
  --kind suite_plan --project-work path/to/project-work.yaml path/to/suite-plan.json
```

Attach the plan on the campaign round milestone or Project Work
`quality_gates` suite-plan slot before `awaiting_suite_run`.
