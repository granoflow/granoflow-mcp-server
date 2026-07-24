# Integration Test Campaign Contract

Provider-neutral loop for **standard integration-test** campaigns (cross-module
real I/O, shared session). Granoflow App/API remains source of truth for
milestones, tasks, and completion.

UI clicks, screenshots, and vision are **out of scope**—see
`granoflow-e2e-test-campaign` / stage `e2e_campaign`.

## Relationship To Task-Local Policy

Ordinary feature tasks follow Task Integration Test Policy: prefer unit tests,
add at most two integration cases when needed, **do not execute** them inside
the feature task, device chosen by the user (recommend local machine). When
those cases are authored, **recommend** recording `requires` / `produces` (and
optional `mutates` / `destroys`) so later orchestration can build a minimal path.

## Relationship To Per-Milestone Layer B

**Feature-milestone acceptance (Layer B)** is owned by
`granoflow-agent-workflow/milestone-integration-acceptance`: milestone-scoped
suite, preflight before implement, user-invisible IT decision, then Experience +
任务回顾 writeback. Reuse this campaign’s **orchestration + agent_auto run**
mechanics for that suite.

This campaign contract’s default stage-`integration_campaign` path is the
**IT leg of最终交付** when `pre_e2e_path: full_unit_and_it` (project has ≥2
feature milestones): portfolio / project-wide hardening after a green **full
unit** suite. It does **not** replace per-feature-milestone Layer B. When the
project has exactly one feature milestone,最终交付 uses `e2e_direct` and
**skips** this stage (`full-delivery-acceptance`).

This campaign contract is also the **execution** path for stage
`integration_campaign`: inventory and orchestrate the suite, run it under
**agent auto-drive**, triage failures, fix product or test code, re-test until
green, and emit a change report when anything was edited.

## Mode-Invariant Auto-Drive

Once the project is in `integration_campaign` (or the user starts this Skill),
set:

```text
campaign_drive: agent_auto
```

This applies for both project `interaction_mode: interactive` and
`unattended`. Do **not** ask ordinary questions such as whether to run the next
case, whether to fix a failure, or whether to continue the suite. Progress
Board remains required but **display-only** (no acknowledgement question) for
the whole IT loop.

Only **externally impossible** items (user-only secret, store approval, host
cannot run the device action) are deferred into residuals; do not freeze the
rest of the campaign.

## Campaign State (resumable)

Persist after each successful step (project attachment, controller task, or
managed summary—host chooses one durable place). Lint with
`scripts/lint_integration_campaign_artifacts.py` when the artifact is written.

```yaml
schema: granoflow_integration_campaign_state_v1
campaign_id: <stable id>
project_id: <id>
campaign_drive: agent_auto
execution_mode: interactive | unattended # project mode; does not weaken auto-drive
interaction_fidelity: service_path # component_path|hybrid when background UI is in scope
integration_test_device_recommendation: local_machine
integration_test_device: local_machine | simulator_or_emulator | physical_device | remote_farm | other
suite_entrypoints: [] # commands or paths before orchestration
suite_plan_ref: null | <attachment id or path>
authorization_ref: <envelope or grant id; never secret values>
fix_schedule: null | inline | deferred_batch | hybrid
fix_schedule_rationale: null | <one-line efficiency reason>
current_round: 1
current_round_milestone_id: null | <id>
phase:
  - awaiting_suite_orchestration
  - awaiting_suite_run
  - clustering_bugs
  - fixing_bugs
  - closing_round
  - complete
  - blocked
failures: []
# each failure: case_id, failure_class, summary
# failure_class: product_code | test_harness | suite_orchestration | environment_external
residuals: []
# e.g. { code: integration_campaign_external_deferred, detail }
round_history: []
# each history row: round, milestone_id, suite_result, bug_task_ids, closed_at
change_report_ref: null | <attachment id or path>
```

Omit E2E UI evidence fields (E2E-only): `vision_acceptance`, `vision_result`,
`vision_capability`, `vision_policy`, `screenshot_capability`,
`screenshot_policy`, `screenshots`, `capture_surface`, `window_capability`.
Presence fails closed as `integration_campaign_vision_not_allowed`.

## Round Machine

```text
open milestone(round N)
  -> orchestrate suite (inventory + Suite Plan; may rewrite tests)
  -> run orchestrated suite under agent_auto + declared integration fidelity
  -> on failure: triage failure_class; choose fix_schedule (inline | deferred_batch | hybrid)
  -> fix product_code and/or test_harness (and orchestration) as classified
  -> re-test affected cases; do not claim green without evidence
  -> if green and changes made: emit change report
  -> if green: campaign complete (or close round with green evidence)
  -> else: finish remaining fixes -> close round -> N = N+1 -> ...
```

Starting a suite run before `contract_loaded` + `orchestration_loaded` on the
Suite Plan fails closed as `integration_campaign_suite_unorchestrated`.

## Suite Orchestration

Read `integration-suite-orchestration.md`. Before the first run of a round:

1. Inventory all authored **integration** tests (Project Work
   `quality_gates.integration_tests`, task Delivery paths, repo IT trees—not
   `e2e/`).
2. Load Project Work `quality_gates.integration_test_special_requirements`
   (`granoflow-agent-workflow/integration-test-special-requirements`). Apply
   matching `fail_closed` rows in Suite Plan
   `special_requirements_loaded` / `special_requirements_applied`. Missing load
   → `integration_campaign_special_requirements_unloaded`; unapplied matching
   rows → `integration_campaign_special_requirement_unapplied`; banned corpus
   substitutes → `integration_campaign_seed_corpus_substituted`.
3. Load `granoflow-agent-workflow/acceptance-outcome-contract`. Emit
   `acceptance_outcomes_loaded: true` and an Acceptance Outcome matrix for
   user-required real results. Integration may **close** only `domain_io` with
   `real_side_effect`; `platform_secure_store` / `os_capability` /
   `ui_human_path` / `session_recovery` must be `deferred_e2e` (or residual).
   Set `user_path_claim: service_layers_only`. Overclaim →
   `acceptance_outcome_layer_overclaim` /
   `acceptance_outcome_user_path_overclaim`.
4. Label `requires` / `produces` / `mutates` / `destroys` and entry style
   (`service_path` default; `ui_probe` needs justification and is required for
   a linked visible background activity).
5. Emit a Campaign Suite Plan with `test_layer: integration` and a
   dependency-respecting `order`.
6. **May rewrite or merge test code** so the plan can run without per-case
   seed/rebuild thrash—while still honoring seed_corpus paths. Record test
   edits in the eventual change report.

Default `interaction_fidelity: service_path`; use `component_path` or `hybrid`
for a real component/state owner around controlled external events. UI
`human_path` →
`integration_campaign_fidelity_wrong_layer`.

## Failure Triage

Every recorded failure **Must** set `failure_class`:

| Class                  | Action                                           |
| ---------------------- | ------------------------------------------------ |
| `product_code`         | Fix product code; re-test                        |
| `test_harness`         | Fix tests/fixtures; re-test                      |
| `suite_orchestration`  | Fix Suite Plan / order / shared session; re-test |
| `environment_external` | Defer residual; do not fake green                |

When the failure message is **signing / entitlement / provisioning /
keystore**, load `granoflow-agent-workflow/code-signing-strategy` first: probe
the host, auto-select and declare `code_signing_strategy` (never ask the user),
prefer free/local schemes for `local_dev_run`, then fix product or harness.
Do not “fix” a local-run failure by forcing paid Developer subscription
entitlements.

## Fix Schedule (AI chooses efficiency)

When failures appear, choose and record:

```text
fix_schedule: inline | deferred_batch | hybrid
fix_schedule_rationale: <why this is faster/safer now>
```

| Schedule         | Meaning                                                             |
| ---------------- | ------------------------------------------------------------------- |
| `inline`         | Stop, fix, re-test the affected path, then continue remaining cases |
| `deferred_batch` | Record failures, continue the suite, then cluster and fix           |
| `hybrid`         | Inline for blockers; batch the rest                                 |

Missing rationale when `fix_schedule` is set fails closed as
`integration_campaign_fix_schedule_rationale_missing`.

Bug tasks (when used) still cluster by distinct root cause
(`integration_campaign_bug_clustering_required` if one-task-per-raw-failure
without justification). Inline fixes may skip task creation when the fix is
small and evidenced in campaign state; larger product fixes should still use
quality tasks via `granoflow-task-authoring` / orchestrator.

## Change Report (mandatory when edits exist)

If the campaign changed product code and/or test code, emit
`integration_campaign_change_report` (usually embedded inside the Closing
Summary). Lint schema `granoflow_integration_campaign_change_report_v1`.

Required when `status: changes_present`:

- `product_changes` / `test_changes` (paths and symbols)
- `product_behavior_delta` (observable difference, or `none` for tests-only)
- `why` (ties to `failure_class` + root cause)
- `failed_before` (case id + symptom)
- `passed_after_evidence` (commands / round / log refs)

Missing report when code changed fails closed as
`integration_campaign_change_report_missing`. First-run green with no edits may
use `status: no_code_changes`.

## Closing Summary (mandatory; non-programmer first)

Before `phase: complete`, emit
`granoflow_integration_campaign_closing_summary_v1` per
`integration-campaign-closing-summary.md` and the template. The user-facing
`plain.*` fields and Chinese Markdown sections are required; durable audience is
`beginner`. `plain.next_step` **Must** point at E2E (e.g. 「开始 E2E 战役」),
not project closeout. Missing or jargon-only summaries fail closed as
`integration_campaign_closing_summary_missing` /
`_incomplete` / `_not_plain`. Residuals must be explained in
`plain.leftovers` (`_residual_unexplained` otherwise).

## Device

Recommend `local_machine` at campaign start. Auto-drive adopts the
recommendation when no grant overrides. Changing device mid-campaign requires a
new grant (direction change), not a chat question mid-round.

## Exit

- **Success:** orchestrated suite green with evidence; Closing Summary present
  (plain-language); change report present if edits were made; `phase: complete`.
  Next lifecycle stage is `e2e_campaign`.
- **Deferred external:** record `integration_campaign_external_deferred`,
  continue solvable work, list leftovers in Closing Summary + residual report
  (also when the project mode is interactive—same residual shape).

## Failure Codes

- `integration_campaign_suite_unspecified`
- `integration_campaign_device_unselected`
- `integration_campaign_authorization_missing`
- `integration_campaign_suite_unorchestrated`
- `integration_campaign_order_dependency_violation`
- `integration_campaign_fidelity_wrong_layer`
- `integration_campaign_ui_probe_unjustified`
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
