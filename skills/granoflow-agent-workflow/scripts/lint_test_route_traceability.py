#!/usr/bin/env python3
"""Validate journey-step to test-route fidelity for Granoflow Task Work."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_test_route_traceability_v1"
PROJECT_TRACE_SCHEMA = "granoflow_journey_step_traceability_v1"
PROJECT_BACKGROUND_ACTIVITY_SCHEMA = "granoflow_background_activity_control_v1"
VALID_TEST_LAYERS = frozenset({"unit", "integration", "e2e"})
VALID_PATH_KINDS = frozenset({"service_path", "component_path", "human_path", "os_capability"})
VALID_DOUBLES_POLICIES = frozenset({"allowed", "forbidden", "real_only", "none"})
VALID_BACKGROUND_EVENT_EVIDENCE = frozenset({"state_change", "event_probe", "host_probe"})
VALID_E2E_SCOPES = frozenset({"feature_e2e", "journey_e2e", "full_project_e2e"})
VALID_NAVIGATION_METHODS = frozenset(
    {
        "app_launch",
        "visible_control",
        "os_control",
        "direct_url",
        "deep_link",
        "direct_route",
        "state_injection",
    }
)
FULL_PROJECT_NAVIGATION_METHODS = frozenset({"app_launch", "visible_control", "os_control"})
VALID_HUMAN_ACTIONS = frozenset(
    {
        "launch",
        "tap",
        "click",
        "type",
        "gesture",
        "select",
        "system_interaction",
        "observe",
    }
)
VALID_HUMAN_EVIDENCE = frozenset({"driver_event", "host_event"})


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        try:
            value = importlib.import_module("yaml").safe_load(text)
        except ImportError:
            value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("root must be an object")
    return value


def _extract(data: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = data.get(key, data)
    return value if isinstance(value, dict) else None


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _str_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return None
    return [item.strip() for item in value]


def canonical_test_route_traceability_sha256(value: dict[str, Any]) -> str:
    payload = {
        key: item
        for key, item in value.items()
        if key not in {"traceability_sha256", "status", "review"}
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _project_trace(project_work: dict[str, Any] | None) -> dict[str, Any] | None:
    if project_work is None:
        return None
    coverage = project_work.get("product_spec_coverage")
    if not isinstance(coverage, dict):
        return None
    trace = coverage.get("journey_step_traceability")
    return trace if isinstance(trace, dict) else None


def _project_background_control(
    project_work: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if project_work is None:
        return None
    coverage = project_work.get("product_spec_coverage")
    if not isinstance(coverage, dict):
        return None
    control = coverage.get("background_activity_control")
    return control if isinstance(control, dict) else None


def _project_background_activities(
    project_work: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    control = _project_background_control(project_work)
    if control is None:
        return {}
    return {
        str(row["activity_id"]): row
        for row in control.get("activities", [])
        if isinstance(row, dict) and _nonempty(row.get("activity_id"))
    }


def _post_update_sequence_valid(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    for field in (
        "activity_started",
        "user_action_preserved",
        "exit_action",
        "activity_ended",
    ):
        if not _nonempty(value.get(field)):
            return False
    action = value.get("protected_user_action")
    if not (
        isinstance(action, dict)
        and _nonempty(action.get("control_ref"))
        and _nonempty(action.get("evidence_ref"))
    ):
        return False
    for field in ("first_background_event", "second_background_event"):
        event = value.get(field)
        if not (
            isinstance(event, dict)
            and _nonempty(event.get("signal"))
            and _nonempty(event.get("evidence_ref"))
            and event.get("evidence_kind") in VALID_BACKGROUND_EVENT_EVIDENCE
        ):
            return False
    return True


def _human_interaction_rows_valid(
    value: Any,
    *,
    step_ids: list[str],
) -> bool:
    if not isinstance(value, list) or len(value) != len(step_ids):
        return False
    observed_steps: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            return False
        step_id = item.get("step_id")
        action = item.get("action")
        navigation_method = item.get("navigation_method")
        if (
            not _nonempty(step_id)
            or action not in VALID_HUMAN_ACTIONS
            or navigation_method not in VALID_NAVIGATION_METHODS
            or not _nonempty(item.get("before_observation"))
            or not _nonempty(item.get("after_observation"))
            or item.get("evidence_kind") not in VALID_HUMAN_EVIDENCE
            or not _nonempty(item.get("evidence_ref"))
        ):
            return False
        if action not in {"launch", "observe"} and not _nonempty(item.get("control_ref")):
            return False
        observed_steps.append(str(step_id))
    return observed_steps == step_ids


def _project_steps(
    project_work: dict[str, Any] | None,
) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, set[str]]]:
    steps: dict[str, dict[str, Any]] = {}
    journey_by_step: dict[str, str] = {}
    facts_by_step: dict[str, set[str]] = {}
    trace = _project_trace(project_work)
    if trace is None:
        return steps, journey_by_step, facts_by_step
    for journey in trace.get("journeys", []):
        if not isinstance(journey, dict) or not _nonempty(journey.get("journey_id")):
            continue
        journey_id = str(journey["journey_id"])
        for step in journey.get("steps", []):
            if not isinstance(step, dict) or not _nonempty(step.get("step_id")):
                continue
            step_id = str(step["step_id"])
            steps[step_id] = step
            journey_by_step[step_id] = journey_id
            facts_by_step[step_id] = set(_str_list(step.get("source_fact_ids")) or [])
    return steps, journey_by_step, facts_by_step


def validate_test_route_traceability(
    data: dict[str, Any],
    project_work: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ledger = _extract(data, "test_route_traceability")
    errors: list[dict[str, str]] = []

    def error(code: str, detail: str) -> None:
        errors.append({"code": code, "detail": detail})

    if ledger is None:
        return {
            "ok": False,
            "code": "test_route_traceability_required",
            "errors": [
                {
                    "code": "test_route_traceability_required",
                    "detail": "test_route_traceability missing",
                }
            ],
        }
    if ledger.get("schema") != SCHEMA:
        error("test_route_traceability_required", f"schema must be {SCHEMA}")

    project_trace = _project_trace(project_work)
    project_background_control = _project_background_control(project_work)
    project_activities = _project_background_activities(project_work)
    steps, journey_by_step, facts_by_step = _project_steps(project_work)
    if project_trace is not None:
        if project_trace.get("schema") != PROJECT_TRACE_SCHEMA:
            error(
                "test_route_project_trace_invalid",
                f"Project Work trace schema must be {PROJECT_TRACE_SCHEMA}",
            )
        if ledger.get("journey_step_traceability_sha256") != project_trace.get(
            "traceability_sha256"
        ):
            error(
                "test_route_traceability_digest_mismatch",
                "journey_step_traceability_sha256 is stale",
            )
        coverage = project_work.get("product_spec_coverage") if project_work else None
        fact_ledger = coverage.get("source_fact_ledger") if isinstance(coverage, dict) else None
        if isinstance(fact_ledger, dict) and ledger.get(
            "source_fact_ledger_sha256"
        ) != fact_ledger.get("ledger_sha256"):
            error(
                "test_route_traceability_digest_mismatch",
                "source_fact_ledger_sha256 is stale",
            )
        if project_background_control is not None:
            if project_background_control.get("schema") != PROJECT_BACKGROUND_ACTIVITY_SCHEMA:
                error(
                    "test_route_project_background_activity_invalid",
                    f"Project Work background activity schema must be "
                    f"{PROJECT_BACKGROUND_ACTIVITY_SCHEMA}",
                )
            if ledger.get("background_activity_control_sha256") != project_background_control.get(
                "control_sha256"
            ):
                error(
                    "test_route_traceability_digest_mismatch",
                    "background_activity_control_sha256 is stale",
                )

    rows = ledger.get("rows")
    if not isinstance(rows, list) or not rows:
        rows = []
        error("test_route_traceability_required", "rows must be a non-empty list")

    route_ids: set[str] = set()
    coverage_by_step_layer: dict[tuple[str, str], int] = {}
    coverage_by_activity_layer: dict[tuple[str, str], int] = {}
    unit_failure_coverage: dict[str, set[str]] = {}
    for index, row in enumerate(rows):
        prefix = f"rows[{index}]"
        if not isinstance(row, dict):
            error("test_route_invalid", f"{prefix} must be an object")
            continue
        route_id = row.get("route_id")
        if not _nonempty(route_id) or route_id in route_ids:
            error("test_route_invalid", f"{prefix}.route_id required and unique")
        else:
            route_ids.add(str(route_id))
        layer = row.get("test_layer")
        path_kind = row.get("path_kind")
        step_ids = _str_list(row.get("step_ids"))
        fact_ids = _str_list(row.get("source_fact_ids"))
        if layer not in VALID_TEST_LAYERS:
            error("test_route_invalid", f"{prefix}.test_layer invalid")
        if path_kind not in VALID_PATH_KINDS:
            error("test_route_invalid", f"{prefix}.path_kind invalid")
        if not step_ids:
            error("test_route_invalid", f"{prefix}.step_ids required")
            step_ids = []
        if not fact_ids:
            error("test_route_invalid", f"{prefix}.source_fact_ids required")
            fact_ids = []
        for field in ("requirement_refs", "acceptance_refs", "assertions", "evidence_refs"):
            if not _str_list(row.get(field)):
                error("test_route_invalid", f"{prefix}.{field} must be a non-empty string list")
        if not _nonempty(row.get("test_path")):
            error("test_route_invalid", f"{prefix}.test_path required")
        if row.get("doubles_policy") not in VALID_DOUBLES_POLICIES:
            error("test_route_invalid", f"{prefix}.doubles_policy invalid")
        if row.get("status") != "covered":
            error("test_route_invalid", f"{prefix}.status must be covered")

        if layer == "integration" and path_kind not in {
            "service_path",
            "component_path",
            "os_capability",
        }:
            error(
                "test_route_layer_overclaim",
                f"{prefix}: integration routes must be service_path, "
                "component_path, or os_capability",
            )
        if layer == "e2e" and path_kind == "service_path":
            error(
                "test_route_human_path_overclaim",
                f"{prefix}: service_path cannot satisfy e2e",
            )
        if path_kind == "human_path" and layer != "e2e":
            error(
                "test_route_human_path_overclaim",
                f"{prefix}: human_path belongs to e2e",
            )
        if path_kind == "component_path" and layer != "integration":
            error(
                "test_route_layer_overclaim",
                f"{prefix}: component_path belongs to integration",
            )
        if path_kind == "os_capability":
            if layer not in {"integration", "e2e"}:
                error(
                    "test_route_os_capability_overclaim",
                    f"{prefix}: os_capability requires integration or e2e",
                )
            if row.get("doubles_policy") not in {"forbidden", "real_only"}:
                error(
                    "test_route_test_double_overclaim",
                    f"{prefix}: os_capability forbids test-double closure",
                )
        if layer == "e2e":
            scope = row.get("e2e_scope")
            navigation_method = row.get("navigation_method")
            bypassed_step_ids = _str_list(row.get("bypassed_step_ids"))
            if scope not in VALID_E2E_SCOPES:
                error(
                    "test_route_invalid",
                    f"{prefix}: e2e_scope must be one of {sorted(VALID_E2E_SCOPES)}",
                )
            if navigation_method not in VALID_NAVIGATION_METHODS:
                error(
                    "e2e_campaign_forbidden_navigation_method",
                    f"{prefix}: navigation_method must be one of "
                    f"{sorted(VALID_NAVIGATION_METHODS)}",
                )
            if bypassed_step_ids is None:
                error(
                    "e2e_campaign_shortcut_overclaim",
                    f"{prefix}: bypassed_step_ids must be a string list",
                )
                bypassed_step_ids = []
            if set(step_ids) & set(bypassed_step_ids):
                error(
                    "e2e_campaign_visible_step_bypassed",
                    f"{prefix}: a step cannot be both covered and bypassed",
                )
            if scope == "full_project_e2e":
                if navigation_method not in FULL_PROJECT_NAVIGATION_METHODS:
                    error(
                        "e2e_campaign_forbidden_navigation_method",
                        f"{prefix}: full_project_e2e may use only "
                        "app_launch, visible_control, or os_control",
                    )
                if bypassed_step_ids:
                    error(
                        "e2e_campaign_visible_step_bypassed",
                        f"{prefix}: full_project_e2e cannot bypass user journey steps",
                    )
            elif navigation_method not in FULL_PROJECT_NAVIGATION_METHODS and not bypassed_step_ids:
                error(
                    "e2e_campaign_shortcut_overclaim",
                    f"{prefix}: shortcut navigation must declare bypassed_step_ids",
                )
            if not _human_interaction_rows_valid(
                row.get("human_interactions"),
                step_ids=step_ids,
            ):
                error(
                    "e2e_campaign_human_interaction_evidence_missing",
                    f"{prefix}: every covered step needs ordered driver/host interaction "
                    "evidence; screenshots alone are not interaction evidence",
                )
            if not _nonempty(row.get("entry_ref")) or not _nonempty(row.get("observable_result")):
                error(
                    "test_route_visible_entry_missing",
                    f"{prefix}: e2e requires entry_ref and observable_result",
                )
            if not _str_list(row.get("host_ids")):
                error("test_route_host_missing", f"{prefix}: e2e requires host_ids")

        activity_id = row.get("background_activity_id")
        if activity_id is not None:
            if not _nonempty(activity_id) or activity_id not in project_activities:
                error(
                    "test_route_unknown_background_activity",
                    f"{prefix}: background_activity_id is unknown",
                )
            else:
                activity = project_activities[str(activity_id)]
                required_layers = _str_list(activity.get("required_test_layers")) or []
                if layer in VALID_TEST_LAYERS:
                    coverage_by_activity_layer[(str(activity_id), str(layer))] = (
                        coverage_by_activity_layer.get(
                            (str(activity_id), str(layer)),
                            0,
                        )
                        + 1
                    )
                if layer in {"integration", "e2e"}:
                    sequence = row.get("post_update_sequence")
                    if not _post_update_sequence_valid(sequence):
                        error(
                            "post_update_interaction_test_missing",
                            f"{prefix}: background activity route must start the activity, "
                            "observe two real updates, preserve a user action, and prove exit",
                        )
                    else:
                        assert isinstance(sequence, dict)
                        action = sequence["protected_user_action"]
                        assert isinstance(action, dict)
                        if action["control_ref"] not in (
                            _str_list(activity.get("controls_that_must_keep_working")) or []
                        ):
                            error(
                                "background_event_overwrites_user_state",
                                f"{prefix}: protected control is not declared by the activity",
                            )
                        if sequence["exit_action"] not in (
                            _str_list(activity.get("ways_to_exit")) or []
                        ):
                            error(
                                "activity_exit_not_proven",
                                f"{prefix}: exit action is not declared by the activity",
                            )
                if (
                    layer == "integration"
                    and "integration" in required_layers
                    and path_kind != "component_path"
                ):
                    error(
                        "component_path_required",
                        f"{prefix}: user-visible background activity integration "
                        "requires component_path",
                    )
                if (
                    layer == "e2e"
                    and "e2e" in required_layers
                    and path_kind not in {"human_path", "os_capability"}
                ):
                    error(
                        "test_route_human_path_overclaim",
                        f"{prefix}: background activity e2e requires human_path "
                        "or os_capability",
                    )

        for step_id in step_ids:
            if steps and step_id not in steps:
                error("test_route_unknown_step", f"{prefix}: unknown step_id {step_id}")
                continue
            if step_id in journey_by_step and row.get("journey_id") != journey_by_step[step_id]:
                error(
                    "test_route_journey_mismatch",
                    f"{prefix}: {step_id} does not belong to journey_id",
                )
            if step_id in facts_by_step and not facts_by_step[step_id].issubset(set(fact_ids)):
                error(
                    "test_route_source_fact_missing",
                    f"{prefix}: source facts for {step_id} are incomplete",
                )
            if layer in VALID_TEST_LAYERS:
                coverage_by_step_layer[(step_id, str(layer))] = (
                    coverage_by_step_layer.get((step_id, str(layer)), 0) + 1
                )
            step = steps.get(step_id)
            if step is None:
                continue
            surface = step.get("interaction_surface")
            boundary = step.get("platform_boundary")
            if (
                layer == "e2e"
                and surface in {"in_app_ui", "mixed"}
                and path_kind
                not in {
                    "human_path",
                    "os_capability",
                }
            ):
                error(
                    "test_route_human_path_overclaim",
                    f"{prefix}: user-visible step {step_id} requires human_path",
                )
            if (
                layer == "e2e"
                and (surface == "os_chrome" or boundary in {"plugin", "os"})
                and path_kind != "os_capability"
            ):
                error(
                    "test_route_os_capability_overclaim",
                    f"{prefix}: platform step {step_id} requires os_capability",
                )
            if layer == "unit":
                covered_modes = _str_list(row.get("covered_failure_modes")) or []
                unit_failure_coverage.setdefault(step_id, set()).update(covered_modes)

    for step_id, step in steps.items():
        required_layers = _str_list(step.get("required_test_layers")) or []
        for layer in required_layers:
            if coverage_by_step_layer.get((step_id, layer), 0) == 0:
                error(
                    "test_route_required_layer_missing",
                    f"{step_id} requires test_layer={layer}",
                )
        if step.get("platform_boundary") in {"plugin", "os"}:
            required_modes = set(_str_list(step.get("failure_modes")) or [])
            missing_modes = sorted(required_modes - unit_failure_coverage.get(step_id, set()))
            if missing_modes:
                error(
                    "test_route_boundary_failure_missing",
                    f"{step_id} unit route missing failure modes: {missing_modes}",
                )

    for activity_id, activity in project_activities.items():
        required_layers = _str_list(activity.get("required_test_layers")) or []
        for layer in required_layers:
            if coverage_by_activity_layer.get((activity_id, layer), 0) == 0:
                error(
                    "post_update_interaction_test_missing",
                    f"{activity_id} requires a background activity route for "
                    f"test_layer={layer}",
                )

    digest = canonical_test_route_traceability_sha256(ledger)
    if ledger.get("traceability_sha256") != digest:
        error("test_route_traceability_digest_mismatch", "traceability_sha256 is stale")
    review = ledger.get("review")
    if not (
        isinstance(review, dict)
        and _nonempty(review.get("author_id"))
        and _nonempty(review.get("reviewer_id"))
        and review.get("author_id") != review.get("reviewer_id")
        and review.get("status") == "passed"
        and _str_list(review.get("evidence_refs"))
        and review.get("reviewed_traceability_sha256") == digest
    ):
        error(
            "test_route_review_failed",
            "independent review must pass the current traceability digest",
        )
    if ledger.get("status") != "passed":
        error("test_route_traceability_required", "status must be passed")
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "traceability_sha256": digest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint Task Work test-route traceability and route fidelity"
    )
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--project-work", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_test_route_traceability(
            _load(args.ledger),
            _load(args.project_work) if args.project_work else None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "test_route_traceability_required",
            "errors": [
                {
                    "code": "test_route_traceability_required",
                    "detail": str(error),
                }
            ],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
