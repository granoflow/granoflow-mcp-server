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
- Task Integration Test Policy: if `copy_change_only: true`, require zero new
  automated tests and copy/visual review evidence only—fail as
  `copy_change_tests_forbidden` otherwise. Else record `unit_test_sufficiency`
  and reason; `integration_tests_added_count` (0–2) with paths; if count > 0
  require `integration_test_execution: not_run_manual_only`, a user-selected
  `integration_test_device` (recommendation default `local_machine`), and
  acceptance status `awaiting_manual_execution`. Fail closed as
  `unit_test_sufficiency_unassessed`,
  `integration_test_added_without_insufficiency`,
  `integration_test_cap_exceeded`, `integration_test_executed_by_agent`, or
  `integration_test_device_unselected` when violated. Never treat unrun
  integration tests as runtime Evidence.
