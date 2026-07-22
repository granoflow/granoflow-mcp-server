#!/usr/bin/env python3
"""Lint Integration Test Campaign structured artifacts.

Validates Suite Plan, Change Report, Campaign State, and Closing Summary
JSON/YAML shapes. Structure/enums plus closing-summary plain-language gates
(CJK/jargon/path heuristics)—not free-form prose snapshots.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SUITE_PLAN_SCHEMA = "granoflow_integration_suite_plan_v1"
CHANGE_REPORT_SCHEMA = "granoflow_integration_campaign_change_report_v1"
CAMPAIGN_STATE_SCHEMA = "granoflow_integration_campaign_state_v1"
CLOSING_SUMMARY_SCHEMA = "granoflow_integration_campaign_closing_summary_v1"

PLAIN_FIELDS = (
    "headline",
    "what_we_checked",
    "result",
    "what_changed_for_you",
    "leftovers",
    "next_step",
)

REQUIRED_MARKDOWN_HEADINGS = (
    "一句话结论",
    "这次查了什么",
    "结果如何",
    "对你有什么影响",
    "还剩什么没做完",
    "下一步你可以做什么",
)

JARGON_MARKERS = (
    "campaign_drive",
    "failure_class",
    "fix_schedule",
    "phase:",
    "agent_auto",
    "suite_orchestration",
    "integration_campaign_",
    "vision_acceptance",
    "product_code",
    "test_harness",
)

# Integration layer: cross-module real I/O / shared session. UI human_path belongs
# to granoflow-e2e-test-campaign, not this skill.
VALID_FIDELITY = frozenset({"service_path"})
WRONG_LAYER_FIDELITY = frozenset({"human_path", "hybrid", "route_fast"})
VALID_ENTRY = frozenset({"service_path", "ui_probe"})
VALID_FAILURE_CLASS = frozenset(
    {
        "product_code",
        "test_harness",
        "suite_orchestration",
        "environment_external",
    }
)
VALID_FIX_SCHEDULE = frozenset({"inline", "deferred_batch", "hybrid"})

# Screenshot / vision evidence belongs to e2e_campaign only.
FORBIDDEN_E2E_UI_FIELDS = frozenset(
    {
        "vision_acceptance",
        "vision_result",
        "vision_capability",
        "vision_policy",
        "screenshot_capability",
        "screenshot_policy",
        "screenshots",
        "capture_surface",
        "window_capability",
    }
)

# Acceptance Outcome Contract (agent-workflow/acceptance-outcome-contract).
VALID_AO_LAYERS = frozenset(
    {
        "domain_io",
        "platform_secure_store",
        "os_capability",
        "ui_human_path",
        "session_recovery",
    }
)
IT_CLOSABLE_AO_LAYERS = frozenset({"domain_io"})
VALID_AO_EVIDENCE = frozenset({"real_side_effect", "host_probe", "test_double"})
VALID_AO_STATUS = frozenset({"closed", "open", "deferred_e2e", "residual"})
VALID_USER_PATH_CLAIM = frozenset({"service_layers_only", "full_user_path"})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def lint_forbidden_e2e_ui_fields(data: dict[str, Any]) -> list[dict[str, str]]:
    """Reject E2E screenshot/vision fields on integration campaign artifacts."""
    present = sorted(field for field in FORBIDDEN_E2E_UI_FIELDS if field in data)
    if not present:
        return []
    return [
        _err(
            "integration_campaign_vision_not_allowed",
            "vision/screenshot/window fields belong to e2e_campaign; omit "
            + ", ".join(present)
            + " on integration artifacts",
        )
    ]


def lint_acceptance_outcomes(
    data: dict[str, Any],
    *,
    campaign: str,
    require_user_path_claim: bool = False,
    campaign_outcome: str | None = None,
) -> list[dict[str, str]]:
    """Structural gates for Acceptance Outcome matrices (IT or shared shape)."""
    errors: list[dict[str, str]] = []
    if data.get("acceptance_outcomes_loaded") is not True:
        errors.append(
            _err(
                "acceptance_outcomes_unloaded",
                "acceptance_outcomes_loaded must be true after applying "
                "acceptance-outcome-contract",
            )
        )

    rows = data.get("acceptance_outcomes")
    if not isinstance(rows, list) or not rows:
        errors.append(
            _err(
                "acceptance_outcomes_incomplete",
                "acceptance_outcomes must be a non-empty list",
            )
        )
        rows = []

    closable = IT_CLOSABLE_AO_LAYERS if campaign == "integration" else VALID_AO_LAYERS
    seen_ids: set[str] = set()
    has_deferred_or_residual = False

    for index, row in enumerate(rows):
        prefix = f"acceptance_outcomes[{index}]"
        if not isinstance(row, dict):
            errors.append(_err("acceptance_outcomes_incomplete", f"{prefix} must be object"))
            continue
        ao_id = row.get("id")
        if not _nonempty_str(ao_id):
            errors.append(_err("acceptance_outcomes_incomplete", f"{prefix}.id required"))
        else:
            assert isinstance(ao_id, str)
            if ao_id in seen_ids:
                errors.append(
                    _err(
                        "acceptance_outcomes_incomplete",
                        f"duplicate acceptance outcome id {ao_id}",
                    )
                )
            seen_ids.add(ao_id)
        if not _nonempty_str(row.get("statement")):
            errors.append(_err("acceptance_outcomes_incomplete", f"{prefix}.statement required"))
        layer = row.get("layer")
        if layer not in VALID_AO_LAYERS:
            errors.append(
                _err(
                    "acceptance_outcomes_incomplete",
                    f"{prefix}.layer must be one of {sorted(VALID_AO_LAYERS)}",
                )
            )
        evidence = row.get("evidence_kind")
        if evidence not in VALID_AO_EVIDENCE:
            errors.append(
                _err(
                    "acceptance_outcomes_incomplete",
                    f"{prefix}.evidence_kind must be one of {sorted(VALID_AO_EVIDENCE)}",
                )
            )
        status = row.get("status")
        if status not in VALID_AO_STATUS:
            errors.append(
                _err(
                    "acceptance_outcomes_incomplete",
                    f"{prefix}.status must be one of {sorted(VALID_AO_STATUS)}",
                )
            )
            continue
        if status in {"deferred_e2e", "residual"}:
            has_deferred_or_residual = True
        if status == "closed":
            if layer not in closable:
                errors.append(
                    _err(
                        "acceptance_outcome_layer_overclaim",
                        f"{prefix}: {campaign} campaign cannot close layer={layer}",
                    )
                )
            if evidence == "test_double":
                errors.append(
                    _err(
                        "acceptance_outcome_test_double_claim",
                        f"{prefix}: status=closed forbids evidence_kind=test_double",
                    )
                )
            elif evidence not in {"real_side_effect", "host_probe"}:
                errors.append(
                    _err(
                        "acceptance_outcome_test_double_claim",
                        f"{prefix}: status=closed requires real_side_effect|host_probe",
                    )
                )
        if status == "residual" and not _nonempty_str(row.get("residual_code")):
            errors.append(
                _err(
                    "acceptance_outcomes_incomplete",
                    f"{prefix}.residual_code required when status=residual",
                )
            )
        case_ids = row.get("case_ids")
        if case_ids is not None and _as_str_list(case_ids) is None:
            errors.append(
                _err(
                    "acceptance_outcomes_incomplete",
                    f"{prefix}.case_ids must be a string list when present",
                )
            )

    if require_user_path_claim or "user_path_claim" in data:
        claim = data.get("user_path_claim")
        if claim not in VALID_USER_PATH_CLAIM:
            errors.append(
                _err(
                    "acceptance_outcomes_incomplete",
                    f"user_path_claim must be one of {sorted(VALID_USER_PATH_CLAIM)}",
                )
            )
        elif campaign == "integration" and claim == "full_user_path":
            errors.append(
                _err(
                    "acceptance_outcome_user_path_overclaim",
                    "integration_campaign user_path_claim must be service_layers_only",
                )
            )

    if campaign_outcome == "green" and has_deferred_or_residual:
        errors.append(
            _err(
                "acceptance_outcome_overclaim_green",
                "outcome=green forbidden while acceptance_outcomes include "
                "deferred_e2e|residual; use green_with_residuals",
            )
        )

    return errors


def _load_yamlish(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _looks_path_only(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if _has_cjk(stripped):
        return False
    return any(
        token in stripped
        for token in (
            "/",
            "\\",
            ".dart",
            ".ts",
            ".tsx",
            ".js",
            ".py",
            ".kt",
            ".swift",
        )
    )


def _looks_jargon_only(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if _has_cjk(stripped):
        # Still fail if it is almost only machine tokens with a token glued on.
        lowered = stripped.lower()
        return any(marker in lowered for marker in JARGON_MARKERS) and len(stripped) < 24
    lowered = stripped.lower()
    return any(marker in lowered for marker in JARGON_MARKERS) or not any(
        ch.isalpha() and ch.isascii() for ch in stripped
    )


def _as_str_list(value: Any) -> list[str] | None:
    if value is None:
        return []
    if not isinstance(value, list):
        return None
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            return None
        out.append(item)
    return out


def _special_requirements_from_project_work(project_work: Any) -> list[dict[str, Any]]:
    if not isinstance(project_work, dict):
        return []
    engineering = project_work.get("engineering")
    if not isinstance(engineering, dict):
        return []
    quality_gates = engineering.get("quality_gates")
    if not isinstance(quality_gates, dict):
        return []
    rows = quality_gates.get("integration_test_special_requirements")
    if rows is None:
        return []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _required_special_requirement_ids(rows: list[dict[str, Any]]) -> list[str]:
    required: list[str] = []
    for row in rows:
        if row.get("enforcement") != "fail_closed":
            continue
        applies = row.get("applies_when") or []
        if not isinstance(applies, list):
            continue
        labels = {str(item) for item in applies}
        if labels & {"campaign_suite", "all_authored_it"}:
            req_id = row.get("id")
            if isinstance(req_id, str) and req_id.strip():
                required.append(req_id.strip())
    return required


def lint_suite_plan(
    data: Any,
    *,
    project_work: Any | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "integration_campaign_suite_plan_invalid",
            "errors": [
                _err(
                    "integration_campaign_suite_plan_invalid",
                    "suite plan must be object",
                )
            ],
        }

    if data.get("schema") != SUITE_PLAN_SCHEMA:
        errors.append(
            _err(
                "integration_campaign_suite_plan_invalid",
                f"schema must be {SUITE_PLAN_SCHEMA}",
            )
        )

    if data.get("contract_loaded") is not True or data.get("orchestration_loaded") is not True:
        errors.append(
            _err(
                "integration_campaign_suite_unorchestrated",
                "contract_loaded and orchestration_loaded must be true before suite run",
            )
        )

    if data.get("special_requirements_loaded") is not True:
        errors.append(
            _err(
                "integration_campaign_special_requirements_unloaded",
                "special_requirements_loaded must be true after reading Project Work "
                "integration_test_special_requirements",
            )
        )

    applied = data.get("special_requirements_applied")
    if applied is None:
        applied = []
    if not isinstance(applied, list) or any(not isinstance(item, str) for item in applied):
        errors.append(
            _err(
                "integration_campaign_suite_plan_invalid",
                "special_requirements_applied must be a string list",
            )
        )
        applied = []

    if project_work is not None:
        rows = _special_requirements_from_project_work(project_work)
        for req_id in _required_special_requirement_ids(rows):
            if req_id not in applied:
                errors.append(
                    _err(
                        "integration_campaign_special_requirement_unapplied",
                        f"fail_closed special requirement {req_id} must be listed in "
                        "special_requirements_applied",
                    )
                )
        for row in rows:
            if row.get("enforcement") != "fail_closed":
                continue
            if row.get("kind") != "seed_corpus":
                continue
            req_id = row.get("id")
            if not isinstance(req_id, str) or req_id not in applied:
                continue
            corpus = row.get("corpus_paths") or []
            used = data.get("seed_corpus_paths_used")
            if not isinstance(corpus, list) or not corpus:
                errors.append(
                    _err(
                        "integration_campaign_suite_plan_invalid",
                        f"seed_corpus {req_id} in Project Work needs non-empty corpus_paths",
                    )
                )
                continue
            if not isinstance(used, list) or any(not isinstance(item, str) for item in used):
                errors.append(
                    _err(
                        "integration_campaign_seed_corpus_substituted",
                        f"applied seed_corpus {req_id} requires suite plan "
                        "seed_corpus_paths_used string list",
                    )
                )
                continue
            missing = [path for path in corpus if path not in used]
            if missing:
                errors.append(
                    _err(
                        "integration_campaign_seed_corpus_substituted",
                        f"seed_corpus_paths_used missing required paths for {req_id}: "
                        + ", ".join(str(path) for path in missing),
                    )
                )

    if data.get("test_layer") != "integration":
        errors.append(
            _err(
                "integration_campaign_suite_plan_invalid",
                "test_layer must be integration",
            )
        )

    fidelity = data.get("interaction_fidelity")
    if fidelity in WRONG_LAYER_FIDELITY:
        errors.append(
            _err(
                "integration_campaign_fidelity_wrong_layer",
                "human_path|hybrid|route_fast belong to e2e_campaign; "
                "integration suite must use interaction_fidelity=service_path",
            )
        )
    elif fidelity not in VALID_FIDELITY:
        errors.append(
            _err(
                "integration_campaign_fidelity_invalid",
                f"interaction_fidelity must be one of {sorted(VALID_FIDELITY)}",
            )
        )

    errors.extend(lint_forbidden_e2e_ui_fields(data))
    errors.extend(
        lint_acceptance_outcomes(
            data,
            campaign="integration",
            require_user_path_claim=True,
        )
    )

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(
            _err(
                "integration_campaign_suite_plan_invalid",
                "cases must be a non-empty list",
            )
        )
        cases = []

    case_by_id: dict[str, dict[str, Any]] = {}
    produces_index: dict[str, list[str]] = {}
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(
                _err(
                    "integration_campaign_suite_plan_invalid",
                    f"{prefix} must be object",
                )
            )
            continue
        case_id = case.get("id")
        if not _nonempty_str(case_id):
            errors.append(_err("integration_campaign_suite_plan_invalid", f"{prefix}.id required"))
            continue
        assert isinstance(case_id, str)
        if case_id in case_by_id:
            errors.append(
                _err(
                    "integration_campaign_suite_plan_invalid",
                    f"duplicate case id {case_id}",
                )
            )
        case_by_id[case_id] = case
        if not _nonempty_str(case.get("path")):
            errors.append(
                _err("integration_campaign_suite_plan_invalid", f"{prefix}.path required")
            )
        for field in ("requires", "produces", "mutates", "destroys"):
            if _as_str_list(case.get(field)) is None:
                errors.append(
                    _err(
                        "integration_campaign_suite_plan_invalid",
                        f"{prefix}.{field} must be a string list",
                    )
                )
        produces = _as_str_list(case.get("produces")) or []
        for token in produces:
            produces_index.setdefault(token, []).append(case_id)

        entry = case.get("entry_style")
        if entry in {"human_path", "route_shortcut"}:
            errors.append(
                _err(
                    "integration_campaign_fidelity_wrong_layer",
                    f"{prefix}.entry_style {entry} belongs to e2e_campaign; "
                    "use service_path|ui_probe",
                )
            )
        elif entry not in VALID_ENTRY:
            errors.append(
                _err(
                    "integration_campaign_suite_plan_invalid",
                    f"{prefix}.entry_style must be service_path|ui_probe",
                )
            )
        elif entry == "ui_probe" and not _nonempty_str(case.get("ui_probe_justified")):
            errors.append(
                _err(
                    "integration_campaign_ui_probe_unjustified",
                    f"{prefix}: ui_probe requires ui_probe_justified",
                )
            )

    order = data.get("order")
    if not isinstance(order, list) or not all(isinstance(x, str) for x in order):
        errors.append(
            _err(
                "integration_campaign_suite_plan_invalid",
                "order must be a list of case ids",
            )
        )
        order = []
    else:
        order_set = set(order)
        id_set = set(case_by_id)
        if order_set != id_set:
            errors.append(
                _err(
                    "integration_campaign_suite_plan_invalid",
                    "order must list each case id exactly once",
                )
            )
        position = {case_id: i for i, case_id in enumerate(order)}
        for case_id, case in case_by_id.items():
            requires = _as_str_list(case.get("requires")) or []
            for token in requires:
                producers = produces_index.get(token, [])
                if not producers:
                    continue
                consumer_pos = position.get(case_id)
                if consumer_pos is None:
                    continue
                if not any(position.get(pid, -1) < consumer_pos for pid in producers):
                    errors.append(
                        _err(
                            "integration_campaign_order_dependency_violation",
                            f"{case_id} requires {token} but no producer runs earlier",
                        )
                    )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "integration_campaign_suite_plan_lint_failed",
        "errors": errors,
    }


def lint_change_report(
    data: Any,
    *,
    code_changed: bool | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    if data is None:
        if code_changed is True:
            errors.append(
                _err(
                    "integration_campaign_change_report_missing",
                    "code or test changes present but change report missing",
                )
            )
        return {
            "ok": not errors,
            "code": "ok" if not errors else "integration_campaign_change_report_lint_failed",
            "errors": errors,
        }

    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "integration_campaign_change_report_lint_failed",
            "errors": [
                _err(
                    "integration_campaign_change_report_incomplete",
                    "change report must be object",
                )
            ],
        }

    if data.get("schema") != CHANGE_REPORT_SCHEMA:
        errors.append(
            _err(
                "integration_campaign_change_report_incomplete",
                f"schema must be {CHANGE_REPORT_SCHEMA}",
            )
        )

    status = data.get("status")
    if status not in {"no_code_changes", "changes_present"}:
        errors.append(
            _err(
                "integration_campaign_change_report_incomplete",
                "status must be no_code_changes|changes_present",
            )
        )

    product_changes = data.get("product_changes")
    test_changes = data.get("test_changes")
    if not isinstance(product_changes, list) or not isinstance(test_changes, list):
        errors.append(
            _err(
                "integration_campaign_change_report_incomplete",
                "product_changes and test_changes must be lists",
            )
        )
        product_changes = []
        test_changes = []

    if status == "no_code_changes" and (product_changes or test_changes):
        errors.append(
            _err(
                "integration_campaign_change_report_inconsistent",
                "no_code_changes cannot list product_changes or test_changes",
            )
        )

    if status == "changes_present":
        if not product_changes and not test_changes:
            errors.append(
                _err(
                    "integration_campaign_change_report_incomplete",
                    "changes_present requires product_changes or test_changes",
                )
            )
        if not _nonempty_str(data.get("product_behavior_delta")):
            errors.append(
                _err(
                    "integration_campaign_change_report_incomplete",
                    "product_behavior_delta required (use none when tests-only)",
                )
            )
        if not _nonempty_str(data.get("why")):
            errors.append(
                _err(
                    "integration_campaign_change_report_incomplete",
                    "why required",
                )
            )
        failed_before = data.get("failed_before")
        if not isinstance(failed_before, list) or not failed_before:
            errors.append(
                _err(
                    "integration_campaign_change_report_incomplete",
                    "failed_before must be a non-empty list when changes_present",
                )
            )
        else:
            for index, item in enumerate(failed_before):
                if not isinstance(item, dict) or not _nonempty_str(item.get("id")):
                    errors.append(
                        _err(
                            "integration_campaign_change_report_incomplete",
                            f"failed_before[{index}].id required",
                        )
                    )
                elif not _nonempty_str(item.get("symptom")):
                    errors.append(
                        _err(
                            "integration_campaign_change_report_incomplete",
                            f"failed_before[{index}].symptom required",
                        )
                    )
        if not _nonempty_str(data.get("passed_after_evidence")):
            errors.append(
                _err(
                    "integration_campaign_change_report_incomplete",
                    "passed_after_evidence required",
                )
            )

    if code_changed is True and status != "changes_present":
        errors.append(
            _err(
                "integration_campaign_change_report_missing",
                "code_changed=true requires status=changes_present",
            )
        )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "integration_campaign_change_report_lint_failed",
        "errors": errors,
    }


def lint_campaign_state(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "integration_campaign_state_lint_failed",
            "errors": [_err("integration_campaign_state_invalid", "state must be object")],
        }

    if data.get("schema") != CAMPAIGN_STATE_SCHEMA:
        errors.append(
            _err(
                "integration_campaign_state_invalid",
                f"schema must be {CAMPAIGN_STATE_SCHEMA}",
            )
        )

    if data.get("campaign_drive") != "agent_auto":
        errors.append(
            _err(
                "integration_campaign_drive_not_agent_auto",
                "campaign_drive must be agent_auto (interactive and unattended)",
            )
        )

    fidelity = data.get("interaction_fidelity")
    if fidelity in WRONG_LAYER_FIDELITY:
        errors.append(
            _err(
                "integration_campaign_fidelity_wrong_layer",
                "campaign state interaction_fidelity must be service_path for "
                "integration_campaign (UI human_path is e2e_campaign)",
            )
        )
    elif fidelity not in VALID_FIDELITY:
        errors.append(
            _err(
                "integration_campaign_fidelity_invalid",
                f"interaction_fidelity must be one of {sorted(VALID_FIDELITY)}",
            )
        )

    errors.extend(lint_forbidden_e2e_ui_fields(data))

    fix_schedule = data.get("fix_schedule")
    if fix_schedule is not None:
        if fix_schedule not in VALID_FIX_SCHEDULE:
            errors.append(
                _err(
                    "integration_campaign_fix_schedule_invalid",
                    f"fix_schedule must be one of {sorted(VALID_FIX_SCHEDULE)}",
                )
            )
        elif not _nonempty_str(data.get("fix_schedule_rationale")):
            errors.append(
                _err(
                    "integration_campaign_fix_schedule_rationale_missing",
                    "fix_schedule_rationale required when fix_schedule is set",
                )
            )

    failures = data.get("failures") or []
    if failures is None:
        failures = []
    if not isinstance(failures, list):
        errors.append(_err("integration_campaign_state_invalid", "failures must be a list"))
        failures = []
    for index, failure in enumerate(failures):
        prefix = f"failures[{index}]"
        if not isinstance(failure, dict):
            errors.append(_err("integration_campaign_state_invalid", f"{prefix} must be object"))
            continue
        if "failure_class" not in failure:
            errors.append(
                _err(
                    "integration_campaign_failure_class_required",
                    f"{prefix}.failure_class required",
                )
            )
        elif failure.get("failure_class") not in VALID_FAILURE_CLASS:
            errors.append(
                _err(
                    "integration_campaign_failure_class_invalid",
                    f"{prefix}.failure_class invalid",
                )
            )

    residuals = data.get("residuals") or []
    if not isinstance(residuals, list):
        residuals = []
        errors.append(_err("integration_campaign_state_invalid", "residuals must be a list"))

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "integration_campaign_state_lint_failed",
        "errors": errors,
    }


def lint_closing_summary(
    data: Any,
    *,
    campaign_complete: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    if data is None:
        if campaign_complete:
            errors.append(
                _err(
                    "integration_campaign_closing_summary_missing",
                    "campaign complete requires closing summary",
                )
            )
        return {
            "ok": not errors,
            "code": "ok" if not errors else "integration_campaign_closing_summary_lint_failed",
            "errors": errors,
        }

    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "integration_campaign_closing_summary_lint_failed",
            "errors": [
                _err(
                    "integration_campaign_closing_summary_incomplete",
                    "closing summary must be object",
                )
            ],
        }

    if data.get("schema") != CLOSING_SUMMARY_SCHEMA:
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                f"schema must be {CLOSING_SUMMARY_SCHEMA}",
            )
        )
    if data.get("contract_loaded") is not True:
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                "contract_loaded must be true",
            )
        )
    if data.get("plain_language_loaded") is not True:
        errors.append(
            _err(
                "integration_campaign_closing_summary_not_plain",
                "plain_language_loaded must be true (load plain-language contracts)",
            )
        )
    if data.get("audience") != "beginner":
        errors.append(
            _err(
                "integration_campaign_closing_summary_not_plain",
                "audience must be beginner for the durable closing record",
            )
        )

    outcome = data.get("outcome")
    if outcome not in {"green", "green_with_residuals", "blocked_external"}:
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                "outcome must be green|green_with_residuals|blocked_external",
            )
        )

    rounds = data.get("rounds_completed")
    if not isinstance(rounds, int) or rounds < 1:
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                "rounds_completed must be a positive integer",
            )
        )

    code_changed = data.get("code_changed")
    if not isinstance(code_changed, bool):
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                "code_changed must be boolean",
            )
        )

    errors.extend(lint_forbidden_e2e_ui_fields(data))
    errors.extend(
        lint_acceptance_outcomes(
            data,
            campaign="integration",
            require_user_path_claim=True,
            campaign_outcome=outcome if isinstance(outcome, str) else None,
        )
    )

    plain = data.get("plain")
    if not isinstance(plain, dict):
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                "plain object with user-facing fields is required",
            )
        )
        plain = {}

    locale = data.get("locale") or "zh-Hans"
    for field in PLAIN_FIELDS:
        value = plain.get(field)
        if not _nonempty_str(value):
            errors.append(
                _err(
                    "integration_campaign_closing_summary_incomplete",
                    f"plain.{field} required",
                )
            )
            continue
        assert isinstance(value, str)
        if locale.startswith("zh") and not _has_cjk(value):
            errors.append(
                _err(
                    "integration_campaign_closing_summary_not_plain",
                    f"plain.{field} must use everyday Chinese for zh locale",
                )
            )
        if field == "headline" and _looks_jargon_only(value):
            errors.append(
                _err(
                    "integration_campaign_closing_summary_not_plain",
                    "plain.headline must be everyday language, not workflow tokens",
                )
            )
        if field == "what_changed_for_you" and _looks_path_only(value):
            errors.append(
                _err(
                    "integration_campaign_closing_summary_not_plain",
                    "plain.what_changed_for_you must describe user-visible "
                    "impact, not only file paths",
                )
            )

    body = data.get("markdown_body")
    if not _nonempty_str(body):
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                "markdown_body required for user-facing display",
            )
        )
    else:
        assert isinstance(body, str)
        for heading in REQUIRED_MARKDOWN_HEADINGS:
            if heading not in body:
                errors.append(
                    _err(
                        "integration_campaign_closing_summary_incomplete",
                        f"markdown_body missing section heading: {heading}",
                    )
                )

    residuals = data.get("residuals") or []
    if not isinstance(residuals, list):
        residuals = []
        errors.append(
            _err(
                "integration_campaign_closing_summary_incomplete",
                "residuals must be a list",
            )
        )
    leftovers = plain.get("leftovers") if isinstance(plain, dict) else None
    if residuals and isinstance(leftovers, str):
        leftover_l = leftovers.strip()
        if leftover_l in {"没有未完成事项。", "没有未完成事项", "无", "none", "n/a"}:
            errors.append(
                _err(
                    "integration_campaign_closing_summary_residual_unexplained",
                    "residuals present but plain.leftovers claims nothing left",
                )
            )

    if code_changed is True:
        report = data.get("change_report")
        report_ref = data.get("change_report_ref")
        if report is None and not _nonempty_str(report_ref):
            errors.append(
                _err(
                    "integration_campaign_change_report_missing",
                    "code_changed=true requires change_report or change_report_ref",
                )
            )
        elif report is not None:
            nested = lint_change_report(report, code_changed=True)
            if not nested["ok"]:
                errors.extend(nested["errors"])

    if code_changed is False and data.get("change_report") is not None:
        nested = lint_change_report(data.get("change_report"))
        if not nested["ok"]:
            errors.extend(nested["errors"])

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "integration_campaign_closing_summary_lint_failed",
        "errors": errors,
    }


def detect_kind(data: Any) -> str | None:
    if not isinstance(data, dict):
        return None
    schema = data.get("schema")
    if schema == CLOSING_SUMMARY_SCHEMA or "markdown_body" in data and "plain" in data:
        return "closing_summary"
    if schema == SUITE_PLAN_SCHEMA or "cases" in data and "order" in data:
        return "suite_plan"
    if schema == CHANGE_REPORT_SCHEMA or "product_behavior_delta" in data:
        return "change_report"
    if schema == CAMPAIGN_STATE_SCHEMA or "campaign_drive" in data:
        return "campaign_state"
    return None


def lint_document(
    data: Any,
    *,
    kind: str | None = None,
    project_work: Any | None = None,
) -> dict[str, Any]:
    resolved = kind or detect_kind(data)
    if resolved == "suite_plan":
        return lint_suite_plan(data, project_work=project_work)
    if resolved == "change_report":
        return lint_change_report(data)
    if resolved == "campaign_state":
        return lint_campaign_state(data)
    if resolved == "closing_summary":
        return lint_closing_summary(data)
    return {
        "ok": False,
        "code": "integration_campaign_artifact_kind_unknown",
        "errors": [
            _err(
                "integration_campaign_artifact_kind_unknown",
                "could not detect suite_plan|change_report|campaign_state|closing_summary",
            )
        ],
    }


def lint_path(
    path: Path,
    *,
    kind: str | None = None,
    project_work: Any | None = None,
) -> dict[str, Any]:
    if not path.is_file():
        return {
            "ok": False,
            "code": "integration_campaign_artifact_missing",
            "errors": [_err("missing_file", str(path))],
        }
    data = _load_yamlish(path)
    result = lint_document(data, kind=kind, project_work=project_work)
    result["path"] = str(path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="Path to suite plan / change report / state")
    parser.add_argument(
        "--kind",
        choices=(
            "suite_plan",
            "change_report",
            "campaign_state",
            "closing_summary",
            "auto",
        ),
        default="auto",
        help="Artifact kind (default: auto-detect)",
    )
    parser.add_argument(
        "--project-work",
        type=Path,
        default=None,
        help="Optional Project Work YAML/JSON for special-requirements cross-check",
    )
    parser.add_argument(
        "--code-changed",
        action="store_true",
        help="For change_report: require status=changes_present",
    )
    parser.add_argument(
        "--campaign-complete",
        action="store_true",
        help="For closing_summary: treat missing file/object as fail-closed",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args(argv)

    kind = None if args.kind == "auto" else args.kind
    project_work = None
    if args.project_work is not None:
        if not args.project_work.is_file():
            result = {
                "ok": False,
                "code": "integration_campaign_artifact_missing",
                "errors": [_err("missing_file", str(args.project_work))],
                "path": str(args.project_work),
            }
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result["code"], file=sys.stderr)
            return 1
        project_work = _load_yamlish(args.project_work)

    if not args.artifact.is_file():
        if args.campaign_complete or kind == "closing_summary":
            result = lint_closing_summary(None, campaign_complete=True)
            result["path"] = str(args.artifact)
        else:
            result = {
                "ok": False,
                "code": "integration_campaign_artifact_missing",
                "errors": [_err("missing_file", str(args.artifact))],
                "path": str(args.artifact),
            }
    else:
        data = _load_yamlish(args.artifact)
        resolved = kind or detect_kind(data)
        if resolved == "change_report":
            result = lint_change_report(data, code_changed=True if args.code_changed else None)
            result["path"] = str(args.artifact)
        elif resolved == "closing_summary":
            result = lint_closing_summary(data, campaign_complete=bool(args.campaign_complete))
            result["path"] = str(args.artifact)
        elif resolved == "suite_plan":
            result = lint_suite_plan(data, project_work=project_work)
            result["path"] = str(args.artifact)
        else:
            result = lint_path(args.artifact, kind=kind, project_work=project_work)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["ok"]:
            print("ok")
        else:
            print(result["code"], file=sys.stderr)
            for err in result.get("errors", []):
                print(f"{err['code']}: {err['detail']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
