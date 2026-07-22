# E2E Test Campaign Contract

Provider-neutral loop for **end-to-end UI** campaigns (real taps/clicks,
human_path journeys, screenshots). Granoflow App/API remains source of truth for
milestones, tasks, and completion.

`service_path` integration campaigns belong to
`granoflow-integration-test-campaign` / stage `integration_campaign` **before**
this stage.

## Visible Window (hard)

E2E **Must** execute in a **user-visible** application/browser window
(`display_mode: visible_window`; default when omitted). Operations in
`interactive` mode **Must** bring the window forward so the user can watch.

Forbidden as covered-journey evidence:

- `flutter test` (widget / unit) without a visible-device `flutter drive` /
  desktop/simulator host session
- Playwright/Cypress `--headless` (or equivalent)
- Screenshots from offscreen test bindings (`capture_surface:
offscreen_test_binding`)

Fail closed:

- `e2e_campaign_headless_ui_forbidden`
- `e2e_campaign_screenshot_not_from_live_window`
- `e2e_campaign_window_required` — no display / cannot raise a window: the
  **whole campaign** fails closed; do **not** close as `green` /
  `green_with_residuals` or `phase: complete` with
  `screenshot_capability: unavailable` (residuals cannot waive)

## Prerequisite: Integration Gate

E2E **Must not** start until integration campaign is complete. On durable state:

```yaml
integration_gate: complete # required before phase leaves awaiting_integration_gate
```

Starting with `integration_gate: incomplete` fails closed as
`e2e_campaign_integration_gate_incomplete`.

## User-Flow Coverage (hard)

Before suite run, load `e2e-user-flow-coverage` and emit
`granoflow_e2e_coverage_matrix_v1` from Project Work journeys/acceptance (+
Design Baseline / user stories / `quality_gates.e2e_tests`). **Author** missing
UI tests for uncovered journeys. Suite Plan **Must** set `coverage_loaded: true`
and embed `coverage_matrix`. Fail closed:

- `e2e_campaign_coverage_unloaded`
- `e2e_campaign_coverage_incomplete`

## Ship Bar + Host Matrix

Default `ship_bar` is `market_smoke` when omitted (see
`e2e-host-capabilities`). Derive `verification_host_matrix` from
`scope.supported_platforms`; allow `parallel_when_capable` for desktop +
simulator/emulator. Assign each covered journey to `host_ids`. Fail closed:

- `verification_host_matrix_missing` — platforms imply hosts but matrix absent
  on suite plan when linting with project work platforms
- `verification_host_unassigned_journey` — covered journey missing `host_ids`
  while matrix present
- `verification_host_platform_mismatch` — `required_host_kinds` not satisfied
- `e2e_campaign_host_unavailable` — required host unavailable without residual
  on close

MCP stays thin: agents use host tools (simulators, desktop drivers); this Skill
does not embed device-farm engines or product-specific journeys.

## Mode-Invariant Auto-Drive

Once the project is in `e2e_campaign` (or the user starts this Skill), set:

```text
campaign_drive: agent_auto
```

Applies for both `interactive` and `unattended`. Do **not** ask ordinary
questions mid-loop. Progress Board is **display-only** for the whole E2E loop.
Bugs found while authoring or running journeys are triaged and fixed under the
same auto-drive rules until green or external residual.

## Campaign State (resumable)

Persist after each successful step. Lint with
`scripts/lint_e2e_campaign_artifacts.py`.

```yaml
schema: granoflow_e2e_campaign_state_v1
campaign_id: <stable id>
project_id: <id>
campaign_drive: agent_auto
execution_mode: interactive | unattended
interaction_fidelity: human_path # default; hybrid allowed
display_mode: visible_window # default when omitted; headless forbidden
integration_gate: complete | incomplete # must be complete to run
screenshot_capability: available | unavailable
window_capability: available | unavailable # independent of screenshots; required when phase=complete
vision_capability: available | unavailable
screenshot_policy: required_if_capable
vision_policy: on_if_capable
vision_result: not_run | passed | failed | skipped
suite_entrypoints: []
suite_plan_ref: null | <attachment id or path>
evidence_pack_ref: null | <attachment id or path>
authorization_ref: <envelope or grant id; never secret values>
current_round: 1
current_round_milestone_id: null | <id>
phase:
  - awaiting_integration_gate
  - awaiting_suite_orchestration
  - awaiting_suite_run
  - capturing_evidence
  - clustering_bugs
  - fixing_bugs
  - closing_round
  - complete
  - blocked
failures: []
# each failure: case_id, failure_class, summary
# failure_class: product_code | test_harness | suite_orchestration | environment_external
residuals: []
# e.g. { code: e2e_campaign_vision_skipped, detail }
#      { code: e2e_campaign_screenshot_unavailable, detail }
#      { code: e2e_campaign_external_deferred, detail }
#      { code: e2e_campaign_manual_test_required, feature, detail }
#      { code: e2e_campaign_automation_too_hard, feature, detail }
round_history: []
change_report_ref: null | <attachment id or path>
```

When `vision_result: skipped`, record a `e2e_campaign_vision_skipped` (or
`vision_skipped`) residual or lint fails closed as
`e2e_campaign_vision_skipped_unrecorded`.

## Round Machine

```text
verify integration_gate complete
  -> probe screenshot_capability + vision_capability
  -> open milestone(round N)
  -> orchestrate suite (inventory + Suite Plan + checkpoints)
  -> run orchestrated human_path journeys under agent_auto
  -> capture screenshots to temp/e2e-campaign/<round>/screenshots/<step_id>.png
  -> Phase B: inventory ALL finalized prototypes as loop basis
  -> for each: show clickable prototype_link + live screenshot + three-question ai_pass
  -> vision-verify when vision_capability available
  -> always show screenshots to user in chat
  -> on product/harness failure: triage failure_class; fix; re-test; re-capture
  -> if any ai_pass=false: (no user confirm) open E2E fix milestone + GF tasks
       (feature_gap ⇒ Analysis+Plan + author tests) → N = N+1 → full compare again
  -> emit evidence pack; silent temp/ ignore when git repo requires it
  -> if AI loop complete and changes made: emit change report
  -> if AI loop complete: ask user final acceptance (not 「项目收尾」 yet)
  -> after user_final_acceptance: campaign complete
```

When a journey/`flutter run`/`drive` failure is **signing / entitlement /
provisioning / keystore**, load
`granoflow-agent-workflow/code-signing-strategy` before other product churn:
probe host → auto-select → declare `code_signing_strategy` (`user_confirmation:
not_required`). Prefer free/local schemes under default `local_dev_run`; do not
push paid Developer subscription as the first fix for local visible-window
runs.

Starting a suite run before `contract_loaded` + `orchestration_loaded` on the
Suite Plan fails closed as `e2e_campaign_suite_unorchestrated`.

## Evidence & Screenshots

See `e2e-evidence-pack.md`. Paths **Must** include a `temp/` segment.
User-facing copy never mentions git; agent may set
`silent_temp_ignore_ensured: true` internally.

## Change Report

When product or test code changed, emit
`granoflow_e2e_campaign_change_report_v1` (same field shape as integration
change report). Missing when edits exist → `e2e_campaign_change_report_missing`.

## Closing Summary

Before `phase: complete`, emit `granoflow_e2e_campaign_closing_summary_v1` per
`e2e-campaign-closing-summary.md`. When `screenshot_capability: available`,
`markdown_body` **Must** include heading 「关键步骤截图」 and `plain.screenshots_note`.
When `required_task_ids` is non-empty, also include 「原型对照」 listing every
prototype link + screenshot + AI pass. `plain.next_step` may point at
「项目收尾」 **only** when `user_final_acceptance: true`; after AI loop complete
but before user gate, ask for final prototype acceptance instead
(`e2e_campaign_closing_summary_ai_loop` if violated).

## Exit

- **Success:** orchestrated suite green; Phase B AI loop `complete`; user final
  acceptance recorded; evidence pack present; screenshots shown when capable;
  Closing Summary present; `phase: complete`. Next lifecycle stage is
  `project_complete`.
- **Deferred external / capability gaps:** record residuals (`vision_skipped`,
  `screenshot_unavailable`, `external_deferred`, `host_unavailable`); explain in
  `plain.leftovers` and `plain.screenshots_note`.
- **Hard-to-automate / mid-run drop:** mark journey `deferred_manual` with
  residual `e2e_campaign_manual_test_required` (or
  `e2e_campaign_automation_too_hard`) + `feature`; Closing Summary **Must**
  remind the user to hand-test that named feature (`plain.leftovers`). Do not
  invent flaky automation to force coverage.

## Failure Codes

- `e2e_campaign_integration_gate_incomplete`
- `e2e_campaign_suite_unspecified`
- `e2e_campaign_suite_unorchestrated`
- `e2e_campaign_fidelity_invalid`
- `e2e_campaign_route_shortcut_unjustified`
- `e2e_campaign_screenshot_capability_unknown`
- `e2e_campaign_screenshot_checkpoint_missing`
- `e2e_campaign_screenshot_path_not_temp`
- `e2e_campaign_screenshot_not_from_live_window`
- `e2e_campaign_headless_ui_forbidden`
- `e2e_campaign_window_required`
- `e2e_campaign_evidence_not_shown`
- `e2e_prototype_task_inventory_unloaded`
- `e2e_prototype_task_review_missing`
- `e2e_prototype_three_questions_incomplete`
- `e2e_prototype_ai_pass_missing`
- `e2e_prototype_ai_pass_inconsistent`
- `e2e_prototype_ai_keep_forbidden`
- `e2e_prototype_ai_loop_incomplete`
- `e2e_prototype_remediation_missing`
- `e2e_prototype_keep_rationale_missing`
- `e2e_prototype_revise_not_recaptured`
- `e2e_prototype_diff_screenshot_missing`
- `e2e_prototype_diff_link_missing`
- `e2e_prototype_diff_not_shown`
- `e2e_prototype_user_final_before_ai`
- `e2e_campaign_closing_summary_ai_loop`
- `e2e_campaign_vision_skipped_unrecorded`
- `e2e_campaign_drive_not_agent_auto`
- `e2e_campaign_failure_class_required`
- `e2e_campaign_change_report_missing`
- `e2e_campaign_closing_summary_missing`
- `e2e_campaign_closing_summary_incomplete`
- `e2e_campaign_closing_summary_not_plain`
- `e2e_campaign_closing_summary_screenshots_missing`
- `e2e_campaign_closing_summary_residual_unexplained`
- `e2e_campaign_manual_test_reminder_missing`
- `e2e_campaign_external_deferred`
