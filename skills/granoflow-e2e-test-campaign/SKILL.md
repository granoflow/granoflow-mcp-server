---
name: granoflow-e2e-test-campaign
description: Final-stage E2E after integration is green—visible-window UI human_path coverage from Project Work, author missing journeys, auto-fix bugs, live-window screenshots under temp/ shown to the user. Headless widget tests forbidden; no window fails closed. Not service_path-only integration.
---

# Granoflow E2E Test Campaign

Use this Skill when the user **requires running** end-to-end UI journeys as a
campaign (for example: `Run e2e campaign`, `开始 E2E 战役`, `开始端到端测试`),
or when the project reaches lifecycle stage `e2e_campaign`.

This is the **final test stage** before `project_complete`: real UI
`human_path` coverage of **daily user operations** declared in Project Work and
related sources, with screenshot delivery under `temp/` and an auto-drive bug
fix loop until green (or green_with_external_residuals).

Cross-module `service_path` integration belongs to
`granoflow-integration-test-campaign` / stage `integration_campaign` **before**
this campaign starts.

After campaign start, the E2E loop is **agent auto-drive** for both
`interactive` and `unattended` project modes: do not ask ordinary phase
confirmations, “run next journey?”, or “capture this screenshot?” questions.

## Not This Skill

| Concern                                                          | Owner                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------------- |
| Task-local: judge unit sufficiency, add ≤2 tests, **do not run** | `granoflow-agent-workflow` Task Integration Test Policy    |
| service_path integration, shared-session I/O without UI          | `granoflow-integration-test-campaign`                      |
| Copy-only / 文字验证: **no** automated tests                     | `user-visible-copy-boundary.md`                            |
| Single-task Analysis/Plan/run                                    | `granoflow-task-orchestrator` + `granoflow-agent-workflow` |
| Create product milestones/tasks portfolio                        | `granoflow-portfolio-orchestrator`                         |

## Activation

Examples:

```text
Run e2e campaign
开始 E2E 战役
开始端到端测试
按 Project Work 补全用户路径并截图交付
```

## Keyword

- `#e2e-campaign`
- `#e2e`
- `#端到端测试`

## Start Gate

**Must** confirm `integration_campaign` is complete before opening round 1.
Read campaign state / lifecycle board; `integration_gate` on durable state
**Must** be `complete`. Starting early fails closed as
`e2e_campaign_integration_gate_incomplete`.

## Progress Board

Each campaign round boundary and the campaign end **Must** emit the Project
Lifecycle Progress Board with stage `e2e_campaign` status (display-only during
the loop). After success, next stage is `project_complete`.

## Mode: Agent Auto-Drive

- Set `campaign_drive: agent_auto` for the whole E2E loop.
- Skip ordinary continue/fix questions; defer only externally impossible items.
- Product and harness bugs discovered while authoring or running journeys are
  fixed under the same auto-drive triage as the campaign contract.

## Screenshots & temp/

E2E **Must** run in a **real user-visible window** (`display_mode: visible_window`,
default when omitted). Headless widget tests (`flutter test` without drive),
Playwright `--headless`, and offscreen test-binding captures are **forbidden**
as covered-journey evidence (`e2e_campaign_headless_ui_forbidden` /
`e2e_campaign_screenshot_not_from_live_window`).

If no visible window can be shown (no display / cannot raise OS window), the
**whole campaign fails closed** as `e2e_campaign_window_required`—residuals
**Must not** waive this into `green` / `green_with_residuals` / `phase: complete`.
Probe and record `window_capability: available|unavailable` separately from
`screenshot_capability` (a PNG alone does not prove a window).

Key-step screenshots **Must** land under:

```text
temp/e2e-campaign/<round>/screenshots/<step_id>.png
```

Each screenshot **Must** set `capture_surface: os_window` or `driver_viewport`
(live surface). `os_window` requires `window_capability: available`. Always show
screenshots to the user when captured.

Covered journeys **Must** set `interaction_surface: in_app_ui|os_chrome|mixed`.
OS chrome / mixed covered rows **Must** set
`os_chrome_verification: real_interaction` or defer as `deferred_manual`.

When the workspace is a git repo and `temp/` is not ignored, the agent
**silently** ensures ignore rules—never teach version-control concepts to the
user. User-facing copy only: screenshots live in the project temp folder and
are viewable in chat.

Policies: `screenshot_policy: required_if_capable`,
`vision_policy: on_if_capable` (capability `available` implies a live window).

## Workflow

Load references via MCP (`e2e-test-campaign-contract`,
`e2e-user-flow-coverage`, `e2e-suite-orchestration`, `e2e-host-capabilities`,
`e2e-evidence-pack`, closing summary). Also honor
`granoflow-agent-workflow/prototype-implementation-fidelity` Phase B
(**hard AI loop**): inventory **every** finalized task-level `ui_prototype` as
the loop basis; for each, list clickable prototype link + live screenshot +
three-question `ai_pass` (prototype without screenshot = process error).
`keep_implementation` is **forbidden** until `user_final_acceptance`. Any
`ai_pass: false` → without user confirm, open E2E fix milestone + GF tasks
(feature gaps re-enter Analysis/Plan + tests), then run the **next full**
compare round until all `matched`. Only then ask the user for final
acceptance—do not suggest 「项目收尾」 earlier. Lint with
`scripts/lint_e2e_campaign_artifacts.py` when artifacts are written.

1. **Start gate** — Integration complete; probe `window_capability`,
   screenshot/vision capability and verification hosts (desktop / simulator /
   emulator / browser) from Project Work platforms; default
   `ship_bar: market_smoke`. Confirm a **visible OS/app window** can be raised;
   if not → fail closed (`e2e_campaign_window_required`), do not invent
   headless covered journeys.
   Success criteria:
   - `integration_gate: complete` on durable campaign state.
   - `window_capability`, screenshot/vision capability, and verification hosts
     probed from Project Work platforms.
     Checkpoints:
   - Starting early → `e2e_campaign_integration_gate_incomplete`.
   - No visible window → fail closed (`e2e_campaign_window_required`); never
     substitute headless UI as covered evidence.
2. **Open round milestone** — e.g. `E2E round 1`.
   Success criteria:
   - Round milestone created via `granoflow-milestone-workflow` (not reused
     feature milestone).
   - Lifecycle board emitted with stage `e2e_campaign`.
     Checkpoints:
   - Set `campaign_drive: agent_auto` for the whole loop.
   - Do not ask ordinary round-start confirmations in interactive or unattended
     mode.
3. **Build coverage matrix** — Load Project Work (primary journeys,
   `product_spec_coverage.journey_coverage` adopted rows, acceptance /
   acceptance_coverage, `quality_gates.e2e_tests` / special requirements),
   Design Baseline screens when present, and user-stories sources. Emit
   `granoflow_e2e_coverage_matrix_v1` with `host_ids` when a host matrix
   applies. Missing load → `e2e_campaign_coverage_unloaded`. Incomplete without
   residual → `e2e_campaign_coverage_incomplete`.
   Success criteria:
   - `granoflow_e2e_coverage_matrix_v1` emitted with every adopted journey
     row or explicit deferral.
   - Prototype task inventory loaded for Phase B fidelity loop.
     Checkpoints:
   - Missing Project Work load → `e2e_campaign_coverage_unloaded`.
   - Incomplete matrix without residual → `e2e_campaign_coverage_incomplete`.
   - Lint artifacts with `scripts/lint_e2e_campaign_artifacts.py` when written.
4. **Author missing UI tests** — For every required journey without a
   human_path case, **write or rewrite** E2E tests that drive a **visible**
   window (Flutter `integration_test` + `flutter drive` / headed Playwright /
   host UI driver). **Do not** use `flutter test` widget trees or headless
   browsers as covered evidence. Inventory-only is not enough. Record
   `authoring.tests_written_or_updated` + paths.
   Success criteria:
   - Every required journey has a human_path case authored or `deferred_manual`
     with named residual.
   - `authoring.tests_written_or_updated` records paths for written/updated tests.
     Checkpoints:
   - Headless widget/browser runs forbidden as covered evidence
     (`e2e_campaign_headless_ui_forbidden`).
   - Inventory-only without authoring fails closed before green claim.
5. **Orchestrate Suite Plan** — Minimal shared session; `test_layer: e2e`;
   `display_mode: visible_window` (default); `coverage_loaded: true` + embedded
   `coverage_matrix`; load
   `granoflow-agent-workflow/acceptance-outcome-contract` and emit Acceptance
   Outcomes for user-required real results (close UI / secure-store / session
   layers with real evidence; probe `secure_storage_capability` when needed);
   embed `host_matrix` when platforms require it;
   `concurrency: parallel_when_capable` when multiple hosts available;
   non-empty `checkpoints` for every covered journey. Lint with
   `--project-work`. Running before this fails as
   `e2e_campaign_suite_unorchestrated`.
   Success criteria:
   - Suite Plan present with `test_layer: e2e`, embedded coverage matrix, and
     Acceptance Outcome matrix.
   - Every covered journey has non-empty `checkpoints` and
     `interaction_surface` set.
     Checkpoints:
   - Running before orchestration → `e2e_campaign_suite_unorchestrated`.
   - Lint with `scripts/lint_e2e_campaign_artifacts.py --project-work`.
   - AO rows use real side effects; test doubles fail closed.
6. **Run + capture** — Agent auto-drive **in the visible window** (bring to
   front under user gaze in interactive mode); capture live-window screenshots
   to `temp/`; **show** screenshots to the user.
   Success criteria:
   - Journeys executed under `display_mode: visible_window` with
     `campaign_drive: agent_auto`.
   - Key-step screenshots land under `temp/e2e-campaign/<round>/screenshots/`
     with `capture_surface: os_window|driver_viewport`.
     Checkpoints:
   - Screenshots shown to user when capable (`e2e_campaign_evidence_not_shown`).
   - Off-window or headless captures → `e2e_campaign_screenshot_not_from_live_window`.
   - OS chrome / mixed rows need `os_chrome_verification: real_interaction` or
     defer as `deferred_manual`.
7. **Triage and fix** — `product_code` | `test_harness` | `suite_orchestration`
   | `environment_external`; fix and re-test; re-capture affected screenshots;
   cluster bug tasks when needed.
   Success criteria:
   - Every failure has `failure_class` and fix evidence after re-test.
   - Prototype Phase B loop: all finalized task prototypes reviewed with link +
     screenshot + three questions + `ai_pass`; AI loop complete before user final.
     Checkpoints:
   - `ai_pass: false` → open E2E fix milestone + GF tasks; re-run full compare
     round under agent_auto.
   - `keep_implementation` forbidden until `user_final_acceptance`.
   - Re-capture affected screenshots after fixes.
8. **Round / campaign close** — Green (or green_with_residuals) + Closing
   Summary with 「关键步骤截图」 when capable; `plain.next_step` → 项目收尾.
   Unavailable required hosts need residual + plain leftovers. Missing live
   window → **fail closed** (not green_with_residuals).
   Success criteria:
   - Plain-language Closing Summary emitted; lifecycle board shows next stage
     `project_complete` only after user final acceptance.
   - Residuals explain unavailable hosts and manual-test reminders when
     `deferred_manual`.
     Checkpoints:
   - Missing Closing Summary or AI loop incomplete → fail closed (listed codes).
   - Missing live window cannot become `green_with_residuals`.
   - 「项目收尾」 only after prototype AI loop complete + user final acceptance.

## Success Criteria

- Integration gate complete.
- Coverage matrix loaded from Project Work (+ listed sources); every adopted
  journey covered or explicitly deferred with residual (`deferred_manual` when
  automation is too hard, with a Closing Summary hand-test reminder).
- Acceptance Outcome matrix present; closed rows use real side effects / host
  probes (not test doubles); `full_user_path` only when all in-scope AOs closed.
- Missing journeys authored as UI human_path tests before green claim—or marked
  `deferred_manual` with feature-named manual-test residual (never silent).
- Suite orchestrated; screenshots under `temp/` shown to user when capable.
- `prototype_task_reviews` inventory loaded; every finalized task-level
  prototype reviewed in a full compare loop (link + screenshot + three
  questions + `ai_pass`)—no omissions; AI loop `complete` before user final.
- Any AI fail auto-remediated (milestone + GF tasks; feature gaps via
  Analysis/Plan) and re-run in a subsequent full round under agent_auto.
- Bugs found in-loop fixed and re-tested under agent_auto.
- Plain-language Closing Summary; 「项目收尾」 only after user final acceptance.

## Failure Codes

- `e2e_campaign_integration_gate_incomplete`
- `e2e_campaign_coverage_unloaded`
- `e2e_campaign_coverage_incomplete`
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
- `e2e_campaign_interaction_surface_missing`
- `e2e_campaign_os_chrome_unverified`
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
- `acceptance_outcomes_unloaded`
- `acceptance_outcomes_incomplete`
- `acceptance_outcome_test_double_claim`
- `acceptance_outcome_overclaim_green`
- `acceptance_outcome_user_path_overclaim`
- `e2e_campaign_secure_storage_unprobed`
- `e2e_campaign_secure_storage_unavailable`
- `third_party_capability_matrix_unloaded`
- `third_party_capability_matrix_incomplete`
- `third_party_capability_fallback_missing`
- `third_party_capability_unprobed`
- `third_party_capability_overclaim`
- `third_party_capability_platform_missing`
- `third_party_capability_ship_bar_excluded`
