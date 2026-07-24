---
name: granoflow-integration-test-campaign
description: Run a standard integration-test campaign—orchestrate a minimal shared-session service_path suite (cross-module real I/O, UI clicks not required), AI auto-drives until green, triage code vs test failures, plain-language closing summary. Not E2E UI/screenshot campaigns and not task-local write-only IT.
---

# Granoflow Integration Test Campaign

Use this Skill when the user **requires running** standard integration tests as a
campaign (for example: `Run integration test campaign`, `开始集成测试战役`,
`无人值守跑集成测试直到全绿`, `开始最终交付`), or when最终交付 uses
`pre_e2e_path: full_unit_and_it` and enters stage `integration_campaign` per
`full-delivery-acceptance` (after full unit suite). Skip this Skill when
`pre_e2e_path: e2e_direct` (exactly one feature milestone).

This stage is **not** end-to-end UI testing. Real taps, screenshots, and vision
belong to `granoflow-e2e-test-campaign` / stage `e2e_campaign` **after** this
campaign is green (or green_with_external_residuals).

After campaign start, the IT loop is **agent auto-drive** for both
`interactive` and `unattended` project modes: do not ask ordinary phase
confirmations, “run next test?”, or “fix this failure?” questions. Loop until
the orchestrated suite is green or a real external blocker is recorded.

## Not This Skill

| Concern                                                          | Owner                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------------- |
| Task-local: judge unit sufficiency, add ≤2 tests, **do not run** | `granoflow-agent-workflow` Task Integration Test Policy    |
| E2E UI path, screenshots, vision                                 | `granoflow-e2e-test-campaign`                              |
| Copy-only / 文字验证: **no** automated tests                     | `user-visible-copy-boundary.md`                            |
| Single-task Analysis/Plan/run                                    | `granoflow-task-orchestrator` + `granoflow-agent-workflow` |
| Create product milestones/tasks portfolio                        | `granoflow-portfolio-orchestrator`                         |

Do not use this Skill to invent copy-string tests or to run tests inside an
ordinary feature task that only _authored_ integration cases.

## Activation

Examples:

```text
Run integration test campaign
Start integration testing until green
开始集成测试战役
无人值守集成测试，按轮次修 bug 直到全过
```

## Keyword

- `#integration-campaign`
- `#integration-test`
- `#集成测试`
- `#最终交付`

## Relationship To Final Delivery

When path selection is unclear, call `granoflow_acceptance_delivery_skill`
first, then load `granoflow-agent-workflow` / `full-delivery-acceptance`. This
Skill is the IT leg of `pre_e2e_path: full_unit_and_it` only. It **does not**
replace per-milestone Layer B (`milestone-integration-acceptance`).

## Progress Board

Each campaign round boundary and the campaign end **Must** emit the Project
Lifecycle Progress Board (`project-lifecycle-progress-board`) with stage
`integration_campaign` status. During the IT loop the board is **display-only**
(no acknowledgement question), including when the project mode is interactive.
After success, next stage is `e2e_campaign` (not `project_complete`).

## Mode: Agent Auto-Drive

- Set `campaign_drive: agent_auto` for the whole IT loop (interactive and
  unattended alike).
- Read `integration-test-campaign-contract.md` and
  `unattended-interaction-contract.md` for solvable vs deferred-external rules.
- Skip ordinary `[confirm]` / “continue suite?” questions inside this stage.
- Externally impossible items are **deferred**—continue solvable work; end with
  a residual report listing what was not executed.

## Workflow

Read `references/integration-test-campaign-contract.md` and
`references/integration-suite-orchestration.md`. Keep resumable campaign state
after every successful step. Lint structured artifacts with
`scripts/lint_integration_campaign_artifacts.py` when written.

1. **Start gate** — Resolve project; collect **integration** suite candidates
   (Project Work `quality_gates.integration_tests`,
   `quality_gates.integration_test_special_requirements`, Delivery paths, repo
   `test/integration/` / `integration_test/` trees). Do **not** inventory
   `e2e/` trees here. Recommend device **`local_machine`**; adopt unless a grant
   names another `integration_test_device`. Default
   `interaction_fidelity: service_path`. Missing suite or device →
   `integration_campaign_suite_unspecified` /
   `integration_campaign_device_unselected`.
   Success criteria:
   - Project resolved; integration suite candidates inventoried (not `e2e/`).
   - `integration_test_device` selected; default `interaction_fidelity: service_path`.
     Checkpoints:
   - Missing suite → `integration_campaign_suite_unspecified`.
   - Missing device → `integration_campaign_device_unselected`.
   - Set `campaign_drive: agent_auto` before the run loop.
2. **Open round milestone** — Each test round is its **own** milestone
   (via `granoflow-milestone-workflow`), named for the round
   (e.g. `Integration test round 1`). Do not reuse a feature milestone as the
   round container.
   Success criteria:
   - Dedicated round milestone created and named for the round number.
   - Lifecycle board emitted with stage `integration_campaign`.
     Checkpoints:
   - Do not reuse a feature milestone as the round container.
   - Board is display-only during the IT loop (no acknowledgement question).
3. **Orchestrate the suite** — Inventory IT; load and apply Project Work
   special requirements and, when present, journey-step traceability; load
   `granoflow-agent-workflow/acceptance-outcome-contract` and emit an
   Acceptance Outcome matrix (`domain_io` closeable only;
   `user_path_claim: service_layers_only`); label requires/produces; emit
   Suite Plan with `test_layer: integration`, dependency-respecting order, and
   `special_requirements_*` fields. For traced Project Work, set
   `test_route_traceability_loaded: true` and map each case through
   `journey_step_ids`; service-path cases may cover only steps that declare
   `integration` in `required_test_layers`. A visible background activity uses
   `component_path` (or a hybrid suite), mounts the real component/state owner,
   injects two controlled external events, acts on a protected control between
   them, and proves exit. **Rewrite/merge tests as needed** for minimal
   shared-session paths without violating seed corpora.
   Running before orchestration fails closed as
   `integration_campaign_suite_unorchestrated`.
   Success criteria:
   - Suite Plan with `test_layer: integration` and embedded special requirements.
   - Acceptance Outcome matrix present; IT closes only `domain_io` layers.
     Checkpoints:
   - Running before orchestration → `integration_campaign_suite_unorchestrated`.
   - No vision/screenshot/window fields on IT artifacts.
   - Lint with `scripts/lint_integration_campaign_artifacts.py` when written.
4. **Run the orchestrated suite** — Execute under `agent_auto`. Prefer shared
   session journeys over isolated seed/rebuild; when a `seed_corpus`
   requirement applies, import from its `corpus_paths`. On failure, set
   `failure_class` (`product_code` | `test_harness` | `suite_orchestration` |
   `environment_external`) and choose `fix_schedule`
   (`inline` | `deferred_batch` | `hybrid`) with a one-line rationale.
   Success criteria:
   - Orchestrated suite executed under `campaign_drive: agent_auto`.
   - Shared-session journeys preferred; seed corpora imported from declared paths.
     Checkpoints:
   - Every failure has `failure_class` and `fix_schedule` with rationale.
   - Seed corpus substitution → `integration_campaign_seed_corpus_substituted`.
   - Externally impossible items deferred; solvable work continues.
5. **Triage and fix** — Fix product and/or test code per class; re-test
   affected cases. Cluster into bug tasks when root causes are distinct and
   non-trivial (`integration_campaign_bug_clustering_required` if one task per
   raw failure without justification). Copy-only bugs still follow
   `copy_change_tests_forbidden`.
   Success criteria:
   - Fixes re-tested to green or recorded as external residual.
   - Change report present when code/tests were edited.
     Checkpoints:
   - One task per raw failure without justification →
     `integration_campaign_bug_clustering_required`.
   - Copy-only fixes: no new automated tests (`copy_change_tests_forbidden`).
   - Bug tasks via `granoflow-task-authoring`; fixes via task orchestrator.
6. **Round close** — When the orchestrated suite is green (or every bug task
   in the round is `done` with suite evidence), close the round milestone.
   Success criteria:
   - Orchestrated suite green or every round bug task `done` with evidence.
   - Round milestone closed with suite readback.
     Checkpoints:
   - Incomplete round suite → `integration_campaign_round_suite_incomplete`.
   - Persist resumable campaign state after successful step.
7. **Next round** — If not yet green after fixes, open **round N+1**,
   re-orchestrate if the suite changed, run again.
   Success criteria:
   - New round milestone opened when fixes did not yet yield green.
   - Suite re-orchestrated when inventory or requirements changed.
     Checkpoints:
   - Re-orchestrate before run when suite composition changed.
   - Continue agent_auto without ordinary continue/fix questions.
8. **Campaign done + Closing Summary** — Stop on a green orchestrated suite
   (or green_with_residuals). **Must** emit the beginner plain-language
   Closing Summary (`integration-campaign-closing-summary` + template) before
   claiming complete. Point `plain.next_step` at E2E (e.g. 「开始 E2E 战役」),
   not project closeout. Lint with
   `scripts/lint_integration_campaign_artifacts.py --kind closing_summary`.
   Success criteria:
   - Green orchestrated suite (or `green_with_residuals` with explained leftovers).
   - Plain-language Closing Summary lint-clean; `plain.next_step` points to E2E.
     Checkpoints:
   - Missing/incomplete Closing Summary → listed fail-closed codes.
   - Next stage is `e2e_campaign`, not `project_complete`.
   - Deferred externals recorded with plain leftover explanation.

## Delegates To

| Step                           | Skill / contract                                                      |
| ------------------------------ | --------------------------------------------------------------------- |
| Round milestone create         | `granoflow-milestone-workflow`                                        |
| Bug task create                | `granoflow-task-authoring`                                            |
| Bug Analysis / fix / Delivery  | `granoflow-task-orchestrator` + `granoflow-agent-workflow`            |
| Long-running worker (optional) | `granoflow-persistent-milestone-runner`                               |
| Unattended / deferred rules    | `granoflow-delegated-authorization` / unattended-interaction-contract |
| Next stage after green         | `granoflow-e2e-test-campaign`                                         |

## Success Criteria

- Suite orchestrated (`test_layer: integration` +
  `service_path|component_path|hybrid`) before run.
- Traced Project Work integration steps map to Suite Plan cases; service paths
  never claim UI-only or E2E-only journey steps.
- DAG/shared-session minimization removes repeated setup and teardown only; it
  never converts service/component evidence into a user-path claim.
- Acceptance Outcome matrix present; IT closes only `domain_io` with real side
  effects; deferred platform/UI/session AOs force `green_with_residuals`.
- Agent auto-drive for the IT loop in both interaction modes.
- Failures classified; fixes re-tested to green.
- No vision/screenshot/window fields on IT artifacts
  (`vision_*`, `screenshot_*`, `screenshots`, `capture_surface`,
  `window_capability`).
- Plain-language Closing Summary present; next step points to E2E.
- Change report present when code/tests were edited.

## Failure Codes

- `integration_campaign_suite_unspecified`
- `integration_campaign_device_unselected`
- `integration_campaign_authorization_missing`
- `integration_campaign_suite_unorchestrated`
- `integration_campaign_special_requirements_unloaded`
- `integration_campaign_special_requirement_unapplied`
- `integration_campaign_seed_corpus_substituted`
- `integration_campaign_order_dependency_violation`
- `integration_campaign_fidelity_wrong_layer`
- `integration_campaign_test_routes_unloaded`
- `integration_campaign_step_traceability_missing`
- `integration_campaign_human_path_overclaim`
- `integration_campaign_ui_probe_unjustified`
- `component_path_required`
- `post_update_interaction_test_missing`
- `background_event_evidence_missing`
- `activity_exit_not_proven`
- `integration_campaign_vision_not_allowed`
- `integration_campaign_drive_not_agent_auto`
- `integration_campaign_failure_class_required`
- `integration_campaign_fix_schedule_rationale_missing`
- `integration_campaign_bug_clustering_required`
- `integration_campaign_round_suite_incomplete`
- `integration_campaign_change_report_missing`
- `integration_campaign_closing_summary_missing`
- `integration_campaign_closing_summary_incomplete`
- `integration_campaign_closing_summary_not_plain`
- `integration_campaign_closing_summary_residual_unexplained`
- `integration_campaign_external_deferred`
- `acceptance_outcomes_unloaded`
- `acceptance_outcomes_incomplete`
- `acceptance_outcome_layer_overclaim`
- `acceptance_outcome_test_double_claim`
- `acceptance_outcome_overclaim_green`
- `acceptance_outcome_user_path_overclaim`
