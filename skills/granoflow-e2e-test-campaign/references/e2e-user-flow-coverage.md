# E2E User-Flow Coverage

Hard gate for stage `e2e_campaign`: before claiming the suite is orchestrated,
build a **coverage matrix** from Project Work and related sources, **author**
missing UI journeys, then map every in-scope user flow to cases + screenshot
checkpoints.

Load via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-e2e-test-campaign",
  referenceId: "e2e-user-flow-coverage"
)
```

Skipping this load and claiming full user-flow coverage fails closed as
`e2e_campaign_coverage_unloaded`. An incomplete matrix without residuals fails
as `e2e_campaign_coverage_incomplete`.

## Required Sources (Must load)

| Source                  | Where                                                                            | What to extract                                                                                   |
| ----------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Primary journeys        | Project Work `product.primary_user_journeys`                                     | Journey titles / ids                                                                              |
| Spec journey coverage   | `product_spec_coverage.journey_coverage` where `disposition: adopted`            | `journey_id`, `acceptance_ids`, `stress_paths`                                                    |
| Acceptance              | `acceptance.conditions` (+ `acceptance_coverage`)                                | In-scope acceptance ids (skip `manual_acceptance_required: true` only when residual explains why) |
| Quality gates           | `engineering.quality_gates.e2e_tests` and special requirements that apply to E2E | Named E2E entrypoints / seed corpora for UI import                                                |
| User stories            | Project Work `sources` / linked user-stories docs                                | Daily operations called out as in-scope                                                           |
| Design Baseline screens | Project Design Baseline (when present)                                           | Baseline-required screens that users reach in adopted journeys                                    |

Optional but recommended: Task Delivery paths that already authored E2E cases;
milestone Plan acceptance packs for First Ship journeys.

## Acceptance Outcomes

Before marking journeys `covered`, load
`granoflow-agent-workflow/acceptance-outcome-contract` and attach an AO matrix
to the Suite Plan / Closing Summary. User-required real results
(`ui_human_path`, `platform_secure_store`, `session_recovery`, …) must be
`closed` with `real_side_effect` / `host_probe`, or explicitly residual. IT
`domain_io` greens do **not** close these rows. `user_path_claim: full_user_path`
only when every in-scope AO for that claim is closed.

## Authoring Obligation

Inventory alone is **not** enough. When a required journey has no UI case:

1. **Write** a human_path E2E case that drives a **visible** window (Flutter
   `integration_test` + `flutter drive` / headed Playwright / host UI driver)
   and exercises the stress path or primary ops. Do **not** mark journeys
   `covered` with headless `flutter test` or offscreen binding screenshots.
2. Record the new/updated paths under `authoring.paths`.
3. Set `authoring.tests_written_or_updated: true` when any gap was closed by
   new or rewritten tests.
4. Rewriting/merging tests during orchestration remains allowed (same spirit as
   integration campaign).

Do not mark a journey `covered` with a service_path-only integration test or a
headless widget test.

## Coverage Matrix Schema

```yaml
schema: granoflow_e2e_coverage_matrix_v1
sources_loaded: [] # non-empty; at least project_work journeys + acceptance
required_journeys:
  - journey_id: J-001
    title: 打开书库并导入
    acceptance_ids: [A5]
    case_ids: [it-j2-import-ui]
    checkpoint_ids: [bookshelf_after_import]
    host_ids: [desktop_native] # required when suite embeds host_matrix
    required_host_kinds: [] # optional; e.g. [desktop] for platform-unique acceptances
    form_factor: null # phone_portrait | tablet_landscape | desktop_landscape | web | ...
    status: covered # covered | deferred_external | deferred_manual | out_of_scope
    interaction_surface: in_app_ui # required when covered: in_app_ui | os_chrome | mixed
    os_chrome_verification: null # real_interaction when surface is os_chrome|mixed
    residual_code: null
    # When status=deferred_manual (automation too hard / dropped mid-run):
    feature: null # required user-facing name for the hand-test reminder
authoring:
  tests_written_or_updated: true
  paths: [integration_test/human_path_import_journey_test.dart]
```

Rules:

- Every adopted Project Work journey **Must** appear once.
- `status: covered` requires non-empty `case_ids` and non-empty
  `checkpoint_ids` (screenshot steps for that journey).
- `status: covered` **Must** set `interaction_surface`:
  - `in_app_ui` — taps/typing inside the app window (injected folder pickers with
    `route_shortcut_justified` count as in-app)
  - `os_chrome` — tray / menu bar / notification center / system share sheet /
    **uninjected** OS file dialogs
  - `mixed` — both in-app and OS chrome in one journey
- When `interaction_surface` is `os_chrome` or `mixed` and status is `covered`,
  **Must** set `os_chrome_verification: real_interaction` (real host gesture).
  If OS chrome cannot be driven reliably → `deferred_manual` + residual; never
  claim `covered` without proof (`e2e_campaign_os_chrome_unverified`).
- When the Suite Plan embeds `host_matrix` (or Project Work declares
  `verification_host_matrix` / non-empty `supported_platforms` for this
  campaign), each `covered` row **Must** have non-empty `host_ids` pointing at
  matrix hosts — else `verification_host_unassigned_journey`.
- When `required_host_kinds` is non-empty, every listed kind **Must** appear on
  at least one assigned host — else `verification_host_platform_mismatch`.
- `status: deferred_external` / `out_of_scope` requires non-empty
  `residual_code` and matching residual on campaign state / closing summary.
- `status: deferred_manual` — automation judged too hard to author or keep
  running (including mid-campaign drop). Requires:
  - `residual_code` in `e2e_campaign_manual_test_required` /
    `e2e_campaign_automation_too_hard` (short aliases allowed)
  - non-empty `feature` (everyday name of the capability)
  - Closing Summary residual + `plain.leftovers` **Must** remind the user to
    **hand-test that named feature** (see `e2e-campaign-closing-summary`)
- Unmapped required journeys → `e2e_campaign_coverage_incomplete`.

## Difficulty Gate (authoring + mid-run)

Implementation difficulty is a **valid** reason to skip or drop an E2E case:

1. **Before authoring:** if a reliable human_path harness would be
   disproportionately hard (fragile OS chrome, no driver hooks, one-off hardware),
   mark `deferred_manual` instead of inventing a flaky test. Do **not** mark
   OS chrome journeys `covered` without `os_chrome_verification: real_interaction`.
2. **During the campaign:** if a case was planned/`covered` but proves too hard
   or unstable to automate, **May** remove it from the runnable suite, set
   `deferred_manual`, and continue other journeys under `agent_auto`.
3. **Never silent:** every such skip must carry residual + feature name; Closing
   Summary **Must** tell the user to hand-test that specific feature.
4. Difficulty for _whether_ to defer remains **agent judgment**; lint enforces
   residual / reminder shape **and** OS chrome verification fields when covered.

## Suite Plan Link

Suite Plan **Must** set:

```yaml
coverage_loaded: true
coverage_matrix: <matrix object> # or coverage_matrix_ref: path
ship_bar: market_smoke # default when omitted at campaign time
host_matrix: <granoflow_verification_host_matrix_v1> # when multi-host / platforms set
concurrency: parallel_when_capable # optional mirror of host_matrix.concurrency
```

Lint:

```text
python3 skills/granoflow-e2e-test-campaign/scripts/lint_e2e_campaign_artifacts.py \
  --kind suite_plan --project-work path/to/project-work.yaml path/to/suite-plan.yaml
```

## Bug Loop

Coverage gaps discovered while writing or running journeys are **product or
harness bugs** when the UI cannot complete the flow. Classify, fix under
`agent_auto`, re-test, and re-capture screenshots—same triage as the E2E
campaign contract. Do not close the campaign with silent uncovered journeys.
