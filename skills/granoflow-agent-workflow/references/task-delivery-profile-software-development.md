# Task Delivery Software Development Profile

Append to the base Delivery when `profiles` contains `software_development`:

- actual behavior and code/API/schema/UI deltas;
- compatibility, migration, rollback, and release status;
- lint, format, type/static, tests, build, and runtime evidence;
- planned-versus-actual minimum-change budget reconciliation: required changes
  delivered, allowed touchpoints actually used, and protected surfaces checked;
- every unplanned UI, code, API, schema, dependency, or architecture delta,
  classified as an authorized scope change, necessary execution deviation, or
  residual that prevents clean acceptance; and
- actual file/method budget differences from the Plan, as supporting evidence
  rather than a substitute for semantic scope reconciliation;
- actual final file and function/method sizes, soft/hard results, responsibility
  splits, gate commands, and configured versus pending-enforcement status from
  `software-structural-budget.md`;
- data attachment sync: if the task changed DB schema, JSON/structured
  contracts, or shared constants, record the project attachment file names from
  Project Work, the new content SHA/readback, and confirm code matches those
  attachments—otherwise fail Delivery as `data_artifact_stale`;
- structural forecast hard gate: Delivery requires evidence that
  `structural_forecast_status` reached `notice_emitted` before the first edit
  and is `reconciled` here (planned-versus-actual forecast table)—otherwise
  fail as `structural_forecast_not_shown` or `structural_forecast_unreconciled`;
- `acceptance_report` HTML in the project/task acceptance slot covering the
  same reconciliations—otherwise fail as `acceptance_report_missing`;
- project context Hard Gate: Delivery records `project_context_check_status`
  (`checked_no_conflict` or `conflict_resolved`), any conflict summary, and—
  when a conflict existed—either user confirmation or an emitted unattended
  decision (`revise_code` / `revise_context_yaml`). Fail as
  `project_context_check_missing`, `project_context_conflict_unconfirmed`,
  `project_context_decision_not_emitted`, or
  `project_context_check_unreconciled` when violated;
- Prototype document coverage: when a UI prototype was finalized/rematched,
  Delivery / Analysis close must show `prototype_html_coverage.status: complete`
  (no `prototype_html_coverage_gap`), `prototype_widget_reuse.status: complete`
  (no `widget_reuse_required`), and `prototype_doc_coverage.status: complete`
  with no gaps/conflicts (`prototype-doc-coverage.md`);
- Prototype Implementation Fidelity: when the task had a UI `ui_prototype`,
  Delivery must show Phase A `prototype_impl_compare` ran **before unit
  tests** (`method: code_review_guess`, `declaration_emitted: true`, three
  questions answered, closed `diffs` when diverged) per
  `prototype-implementation-fidelity.md`. Fail as
  `prototype_impl_compare_unread`, `prototype_impl_compare_undeclared`,
  `prototype_impl_compare_three_questions_incomplete`,
  `prototype_diff_ledger_incomplete`, `prototype_impl_compare_wrong_method`,
  or `prototype_impl_compare_lint_failed`. E2E Phase B AI loop is reconciled at
  stage `e2e_campaign` evidence—not skipped when diffs exist;
- Task Integration Test Policy: if `copy_change_only: true`, require zero new
  automated tests and copy/visual review evidence only—fail as
  `copy_change_tests_forbidden` otherwise. Else record `unit_test_sufficiency`
  and reason; `integration_tests_added_count` (0–2) with paths; if count > 0
  require `integration_test_execution: not_run_manual_only` or
  `awaiting_campaign_execution`, a user-selected `integration_test_device`
  (recommendation default `local_machine`), recommended
  `requires`/`produces` orchestration hints per added case,
  `integration_test_special_requirements_checked` /
  `integration_test_special_requirements_applied` per
  `integration-test-special-requirements.md`, and acceptance status
  `awaiting_manual_execution` / `awaiting_campaign_execution`. Fail closed as
  `unit_test_sufficiency_unassessed`,
  `integration_test_added_without_insufficiency`,
  `integration_test_cap_exceeded`, `integration_test_executed_by_agent`,
  `integration_test_device_unselected`,
  `integration_test_special_requirements_unchecked`,
  `integration_test_special_requirement_ignored`, or
  `integration_test_special_requirement_as_app_seed` when violated. Never treat
  unrun integration tests as runtime Evidence;
- milestone Plan acceptance pack (when the milestone emitted one): record the
  pack path / version and reconcile `present: true` sections—test-case ticks
  (same Case IDs), `copy_locale` copy inventory, schema/flow notes—per
  `milestone-plan-acceptance-pack.md`. Fail as
  `milestone_plan_acceptance_pack_not_used`,
  `milestone_plan_acceptance_pack_drift`, or
  `milestone_plan_acceptance_pack_delivery_unreconciled` when violated.
- Code signing strategy (`code-signing-strategy.md`): when the task edited
  entitlements, `CODE_SIGN_*` / Team / provisioning, keystore, Authenticode, or
  fixed a signing/entitlement build failure, Delivery **Must** include a
  lint-clean `code_signing_strategy` with `user_confirmation: not_required`
  (probe host → auto-select; prefer free/local for `local_dev_run`). Fail as
  `code_signing_strategy_missing`, `code_signing_strategy_incomplete`,
  `code_signing_user_confirmation_forbidden`, or
  `code_signing_goal_distribution_mismatch` when violated. Do **not** ask the
  user to confirm the scheme.
- Third-party capability matrix (`third-party-capability-matrix.md`): when the
  task implements or claims a **user-visible** third-party capability (TTS,
  push, camera, IAP, maps, …), Delivery **Must** show a Project Work
  `engineering.third_party_capabilities` row with `fallback`,
  `required_platforms`, and `probe_by_platform` updates for platforms touched.
  Do **not** claim “works on all target platforms” / 全平台可用 while any
  required platform remains `unprobed` or `unavailable`. Lint with
  `scripts/lint_third_party_capability_matrix.py`. Fail as
  `third_party_capability_matrix_unloaded`,
  `third_party_capability_matrix_incomplete`,
  `third_party_capability_fallback_missing`,
  `third_party_capability_unprobed`,
  `third_party_capability_overclaim`,
  `third_party_capability_platform_missing`, or
  `third_party_capability_ship_bar_excluded` when violated.
