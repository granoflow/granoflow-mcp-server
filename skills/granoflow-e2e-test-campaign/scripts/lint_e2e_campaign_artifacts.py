#!/usr/bin/env python3
"""Lint E2E Test Campaign structured artifacts.

Validates Suite Plan, Change Report, Campaign State, Evidence Pack, and Closing
Summary JSON/YAML shapes. Structure/enums plus plain-language gates—not prose
snapshots.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SUITE_PLAN_SCHEMA = "granoflow_e2e_suite_plan_v1"
CHANGE_REPORT_SCHEMA = "granoflow_e2e_campaign_change_report_v1"
CAMPAIGN_STATE_SCHEMA = "granoflow_e2e_campaign_state_v1"
EVIDENCE_PACK_SCHEMA = "granoflow_e2e_evidence_pack_v1"
CLOSING_SUMMARY_SCHEMA = "granoflow_e2e_campaign_closing_summary_v1"
COVERAGE_MATRIX_SCHEMA = "granoflow_e2e_coverage_matrix_v1"
HOST_MATRIX_SCHEMA = "granoflow_verification_host_matrix_v1"

COVERED_JOURNEY_STATUSES = frozenset(
    {"covered", "deferred_external", "deferred_manual", "out_of_scope"}
)
DEFERRED_JOURNEY_STATUSES = frozenset({"deferred_external", "deferred_manual", "out_of_scope"})
MANUAL_TEST_RESIDUAL_CODES = frozenset(
    {
        "e2e_campaign_manual_test_required",
        "e2e_campaign_automation_too_hard",
        "manual_test_required",
        "automation_too_hard",
    }
)
MANUAL_REMINDER_MARKERS = ("手工", "手动", "manual")

VALID_SHIP_BARS = frozenset({"market_smoke", "form_factor_smoke", "full_campaign"})
DEFAULT_SHIP_BAR = "market_smoke"
VALID_HOST_KINDS = frozenset(
    {
        "desktop",
        "simulator",
        "emulator",
        "physical_device",
        "remote_farm",
        "browser",
        "other",
    }
)
VALID_HOST_STATUS = frozenset({"unprobed", "available", "unavailable", "deferred_external"})
VALID_CONCURRENCY = frozenset({"sequential", "parallel_when_capable"})
VALID_HOST_PROVIDERS = frozenset(
    {"current_platform", "official_virtual", "third_party_virtual", "external"}
)
VALID_HOST_SELECTION_MODES = frozenset({"interactive", "unattended"})
VALID_HOST_SELECTION_SOURCES = frozenset(
    {"user_selection", "current_platform_default", "ai_fallback"}
)
HOST_UNAVAILABLE_RESIDUAL_CODES = frozenset(
    {
        "e2e_campaign_host_unavailable",
        "verification_host_unavailable",
    }
)
DESKTOP_PLATFORM_TOKENS = frozenset({"macos", "mac", "windows", "win", "linux"})
IOS_PLATFORM_TOKENS = frozenset({"ios", "iphone", "ipad"})
ANDROID_PLATFORM_TOKENS = frozenset({"android"})
WEB_PLATFORM_TOKENS = frozenset({"web", "browser"})

PLAIN_FIELDS = (
    "headline",
    "what_we_checked",
    "result",
    "what_changed_for_you",
    "leftovers",
    "next_step",
    "screenshots_note",
)

REQUIRED_MARKDOWN_HEADINGS = (
    "一句话结论",
    "这次查了什么",
    "结果如何",
    "对你有什么影响",
    "还剩什么没做完",
    "下一步你可以做什么",
)

SCREENSHOTS_HEADING = "关键步骤截图"

JARGON_MARKERS = (
    "campaign_drive",
    "failure_class",
    "phase:",
    "agent_auto",
    "suite_orchestration",
    "e2e_campaign_",
    "screenshot_capability",
    "vision_result",
    "product_code",
    "test_harness",
    "silent_temp_ignore",
    "gitignore",
)

VALID_FIDELITY = frozenset({"human_path", "hybrid", "route_fast"})
WRONG_LAYER_FIDELITY = frozenset({"service_path"})
VALID_BACKGROUND_EVENT_EVIDENCE = frozenset({"state_change", "event_probe", "host_probe"})
VALID_ENTRY = frozenset({"human_path", "route_shortcut"})
VALID_CAPABILITY = frozenset({"available", "unavailable"})
VALID_VISION_RESULT = frozenset({"not_run", "passed", "failed", "skipped"})
VALID_DISPLAY_MODES = frozenset({"visible_window", "headless"})
VALID_INTERACTION_SURFACES = frozenset({"in_app_ui", "os_chrome", "mixed"})
OS_CHROME_SURFACES = frozenset({"os_chrome", "mixed"})
VALID_OS_CHROME_VERIFICATION = frozenset({"real_interaction"})
# Live OS/driver surfaces only; offscreen widget-binding captures are forbidden.
LIVE_CAPTURE_SURFACES = frozenset({"os_window", "driver_viewport"})
FORBIDDEN_CAPTURE_SURFACES = frozenset({"offscreen_test_binding", "headless_canvas"})
VALID_FAILURE_CLASS = frozenset(
    {
        "product_code",
        "test_harness",
        "suite_orchestration",
        "environment_external",
    }
)
VISION_SKIP_RESIDUAL_CODES = frozenset(
    {
        "e2e_campaign_vision_skipped",
        "vision_skipped",
    }
)
SCREENSHOT_UNAVAILABLE_RESIDUAL_CODES = frozenset(
    {
        "e2e_campaign_screenshot_unavailable",
        "screenshot_unavailable",
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
VALID_AO_EVIDENCE = frozenset({"real_side_effect", "host_probe", "test_double"})
VALID_AO_STATUS = frozenset({"closed", "open", "deferred_e2e", "residual"})
VALID_USER_PATH_CLAIM = frozenset({"service_layers_only", "full_user_path"})
VALID_E2E_SCOPES = frozenset({"feature_e2e", "journey_e2e", "full_project_e2e"})
HUMAN_PATH_EXECUTION_SCHEMA = "granoflow_human_path_execution_v1"
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


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def lint_acceptance_outcomes(
    data: dict[str, Any],
    *,
    require_user_path_claim: bool = False,
    campaign_outcome: str | None = None,
    secure_storage_capability: Any = None,
) -> list[dict[str, str]]:
    """Structural gates for E2E Acceptance Outcome matrices."""
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

    seen_ids: set[str] = set()
    has_deferred_or_residual = False
    closed_secure_store = False

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
            if layer == "platform_secure_store":
                closed_secure_store = True
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
        elif claim == "full_user_path" and has_deferred_or_residual:
            errors.append(
                _err(
                    "acceptance_outcome_user_path_overclaim",
                    "user_path_claim=full_user_path requires all acceptance_outcomes closed",
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

    if closed_secure_store:
        cap = (
            secure_storage_capability
            if secure_storage_capability is not None
            else data.get("secure_storage_capability")
        )
        if cap is None:
            errors.append(
                _err(
                    "e2e_campaign_secure_storage_unprobed",
                    "closing platform_secure_store requires secure_storage_capability probe",
                )
            )
        elif cap == "unavailable":
            errors.append(
                _err(
                    "e2e_campaign_secure_storage_unavailable",
                    "cannot close platform_secure_store when "
                    "secure_storage_capability=unavailable",
                )
            )
        elif cap != "available":
            errors.append(
                _err(
                    "e2e_campaign_secure_storage_unprobed",
                    "secure_storage_capability must be available|unavailable",
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
            ".png",
        )
    )


def _looks_jargon_only(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if _has_cjk(stripped):
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
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            step_id = item.get("step_id")
            if isinstance(step_id, str):
                out.append(step_id)
            else:
                return None
        else:
            return None
    return out


def _path_under_temp(path: str) -> bool:
    normalized = path.replace("\\", "/").strip()
    if normalized.startswith("temp/"):
        return True
    return "/temp/" in normalized


def _residual_codes(residuals: list[Any]) -> set[str]:
    codes: set[str] = set()
    for item in residuals:
        if isinstance(item, dict):
            code = item.get("code")
            if isinstance(code, str):
                codes.add(code)
        elif isinstance(item, str):
            codes.add(item)
    return codes


def normalize_ship_bar(value: Any) -> str:
    """Default omitted ship_bar to market_smoke (L9)."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return DEFAULT_SHIP_BAR
    if isinstance(value, str) and value.strip() in VALID_SHIP_BARS:
        return value.strip()
    return DEFAULT_SHIP_BAR


def normalize_display_mode(value: Any) -> str:
    """Default omitted display_mode to visible_window (hard gate)."""
    if isinstance(value, str) and value.strip() in VALID_DISPLAY_MODES:
        return value.strip()
    return "visible_window"


def _coverage_has_covered_journey(matrix: Any) -> bool:
    if not isinstance(matrix, dict):
        return False
    journeys = matrix.get("required_journeys")
    if not isinstance(journeys, list):
        return False
    return any(isinstance(row, dict) and row.get("status") == "covered" for row in journeys)


def looks_headless_run_command(command: Any) -> bool:
    """Detect runners that cannot show a real user-visible window."""
    if not isinstance(command, str) or not command.strip():
        return False
    lowered = " ".join(command.lower().split())
    if "flutter" in lowered and "drive" in lowered:
        return False
    if re.search(r"\bflutter\s+run\b", lowered) and "flutter test" not in lowered:
        return False
    if re.search(r"\bflutter\s+test\b", lowered) or "flutter test" in lowered:
        return True
    if re.search(r"--headless\b", lowered) and not re.search(r"--headed\b", lowered):
        return True
    return "playwright" in lowered and "headless" in lowered and "headed" not in lowered


def lint_visible_window_suite_plan(data: dict[str, Any]) -> list[dict[str, str]]:
    """Fail closed when suite claims covered UI without a visible window."""
    errors: list[dict[str, str]] = []
    raw_mode = data.get("display_mode")
    if raw_mode is not None and raw_mode not in VALID_DISPLAY_MODES:
        errors.append(
            _err(
                "e2e_campaign_headless_ui_forbidden",
                "display_mode must be visible_window|headless (default visible_window)",
            )
        )
        return errors
    display_mode = normalize_display_mode(raw_mode)
    if display_mode == "headless":
        errors.append(
            _err(
                "e2e_campaign_headless_ui_forbidden",
                "display_mode=headless is forbidden for e2e_campaign; "
                "require a real user-visible window",
            )
        )

    has_covered = _coverage_has_covered_journey(data.get("coverage_matrix"))
    run_command = data.get("run_command")
    if has_covered and looks_headless_run_command(run_command):
        errors.append(
            _err(
                "e2e_campaign_headless_ui_forbidden",
                "covered journeys cannot use headless run_command "
                "(e.g. flutter test without drive); use visible-window drivers",
            )
        )
    return errors


def lint_window_required_for_close(
    *,
    screenshot_capability: Any,
    outcome_or_phase: str,
    window_capability: Any = None,
    require_window_field: bool = False,
) -> list[dict[str, str]]:
    """Whole-campaign fail-closed when a live window/screenshot is unavailable."""
    errors: list[dict[str, str]] = []
    if screenshot_capability == "unavailable":
        errors.append(
            _err(
                "e2e_campaign_window_required",
                f"{outcome_or_phase}: screenshot_capability=unavailable fails closed; "
                "e2e requires a real visible window (residuals cannot waive)",
            )
        )
    if require_window_field and window_capability not in VALID_CAPABILITY:
        errors.append(
            _err(
                "e2e_campaign_window_required",
                f"{outcome_or_phase}: window_capability must be available|unavailable "
                "(probe a real on-screen window; residuals cannot waive)",
            )
        )
    elif window_capability == "unavailable":
        errors.append(
            _err(
                "e2e_campaign_window_required",
                f"{outcome_or_phase}: window_capability=unavailable fails closed; "
                "e2e requires a real visible window (residuals cannot waive)",
            )
        )
    return errors


def lint_interaction_surface_row(
    row: dict[str, Any],
    *,
    prefix: str,
) -> list[dict[str, str]]:
    """Require interaction_surface on covered journeys; OS chrome needs proof."""
    errors: list[dict[str, str]] = []
    status = row.get("status")
    if status != "covered":
        return errors
    surface = row.get("interaction_surface")
    if surface not in VALID_INTERACTION_SURFACES:
        errors.append(
            _err(
                "e2e_campaign_interaction_surface_missing",
                f"{prefix}: covered requires interaction_surface in "
                f"{sorted(VALID_INTERACTION_SURFACES)}",
            )
        )
        return errors
    if surface in OS_CHROME_SURFACES:
        proof = row.get("os_chrome_verification")
        if proof not in VALID_OS_CHROME_VERIFICATION:
            errors.append(
                _err(
                    "e2e_campaign_os_chrome_unverified",
                    f"{prefix}: interaction_surface={surface} covered requires "
                    "os_chrome_verification=real_interaction "
                    "(or defer as deferred_manual)",
                )
            )
    return errors


def _normalize_platform_token(value: str) -> str:
    return value.strip().lower().replace(" ", "")


def platforms_from_project_work(project_work: Any) -> list[str]:
    if not isinstance(project_work, dict):
        return []
    scope = project_work.get("scope")
    if not isinstance(scope, dict):
        return []
    raw = scope.get("supported_platforms") or []
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append(_normalize_platform_token(item))
        elif isinstance(item, dict):
            name = item.get("id") or item.get("name") or item.get("platform")
            if isinstance(name, str) and name.strip():
                out.append(_normalize_platform_token(name))
    return out


def derive_candidate_host_kinds(platforms: list[str]) -> set[str]:
    """Map product platforms to capability candidates, never mandatory test scope."""
    tokens = {_normalize_platform_token(p) for p in platforms if p and str(p).strip()}
    if not tokens:
        return set()
    kinds: set[str] = set()
    if tokens & DESKTOP_PLATFORM_TOKENS:
        kinds.add("desktop")
    if tokens & IOS_PLATFORM_TOKENS:
        kinds.add("simulator")
    if tokens & ANDROID_PLATFORM_TOKENS:
        kinds.add("emulator")
    if tokens & WEB_PLATFORM_TOKENS and not (
        tokens & (DESKTOP_PLATFORM_TOKENS | IOS_PLATFORM_TOKENS | ANDROID_PLATFORM_TOKENS)
    ):
        kinds.add("browser")
    # Pure web already handled; if only unknown tokens, do not invent desktop.
    return kinds


# Compatibility name for callers. The returned kinds describe discoverable
# candidates; selection, not this set, determines the E2E test scope.
derive_required_host_kinds = derive_candidate_host_kinds


def lint_host_matrix(
    data: Any,
    *,
    platforms: list[str] | None = None,
    require_present: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if data is None:
        candidate_kinds = derive_candidate_host_kinds(platforms or [])
        if require_present or candidate_kinds:
            errors.append(
                _err(
                    "verification_host_matrix_missing",
                    "host_matrix required when platforms imply verification hosts "
                    "or require_present=true",
                )
            )
        return {
            "ok": not errors,
            "code": "ok" if not errors else "verification_host_matrix_lint_failed",
            "errors": errors,
            "hosts_by_id": {},
        }

    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "verification_host_matrix_lint_failed",
            "errors": [_err("verification_host_matrix_missing", "host_matrix must be object")],
            "hosts_by_id": {},
        }

    if data.get("schema") != HOST_MATRIX_SCHEMA:
        errors.append(
            _err(
                "verification_host_matrix_missing",
                f"schema must be {HOST_MATRIX_SCHEMA}",
            )
        )

    concurrency = data.get("concurrency")
    if concurrency is not None and concurrency not in VALID_CONCURRENCY:
        errors.append(
            _err(
                "verification_host_matrix_missing",
                "concurrency must be sequential|parallel_when_capable",
            )
        )

    hosts = data.get("hosts")
    hosts_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(hosts, list):
        errors.append(_err("verification_host_matrix_missing", "hosts must be a list"))
        hosts = []
    for index, host in enumerate(hosts):
        prefix = f"hosts[{index}]"
        if not isinstance(host, dict):
            errors.append(_err("verification_host_matrix_missing", f"{prefix} must be object"))
            continue
        host_id = host.get("id")
        if not _nonempty_str(host_id):
            errors.append(_err("verification_host_matrix_missing", f"{prefix}.id required"))
            continue
        assert isinstance(host_id, str)
        kind = host.get("kind")
        if kind not in VALID_HOST_KINDS:
            errors.append(
                _err(
                    "verification_host_matrix_missing",
                    f"{prefix}.kind must be one of {sorted(VALID_HOST_KINDS)}",
                )
            )
        status = host.get("status")
        if status not in VALID_HOST_STATUS:
            errors.append(
                _err(
                    "verification_host_matrix_missing",
                    f"{prefix}.status must be unprobed|available|unavailable|deferred_external",
                )
            )
        provider = host.get("provider")
        if provider not in VALID_HOST_PROVIDERS:
            errors.append(
                _err(
                    "verification_host_matrix_missing",
                    f"{prefix}.provider must be one of {sorted(VALID_HOST_PROVIDERS)}",
                )
            )
        hosts_by_id[host_id] = host

    selection = data.get("selection")
    selected_host_ids: list[str] = []
    if not isinstance(selection, dict):
        errors.append(
            _err(
                "verification_host_selection_missing",
                "selection must describe how capability candidates became the test scope",
            )
        )
    else:
        mode = selection.get("mode")
        source = selection.get("source")
        if mode not in VALID_HOST_SELECTION_MODES:
            errors.append(
                _err(
                    "verification_host_selection_missing",
                    "selection.mode must be interactive|unattended",
                )
            )
        if source not in VALID_HOST_SELECTION_SOURCES:
            errors.append(
                _err(
                    "verification_host_selection_missing",
                    "selection.source must be user_selection|current_platform_default|ai_fallback",
                )
            )
        selected = _as_str_list(selection.get("selected_host_ids"))
        if selected is None or (platforms and not selected):
            errors.append(
                _err(
                    "verification_host_selection_missing",
                    "selection.selected_host_ids must select at least one available host "
                    "when the project declares platforms",
                )
            )
        else:
            selected_host_ids = selected
        unknown = sorted(set(selected_host_ids) - set(hosts_by_id))
        if unknown:
            errors.append(
                _err(
                    "verification_host_selection_missing",
                    "selected_host_ids not present in hosts: " + ", ".join(unknown),
                )
            )
        current_supported = selection.get("project_includes_current_platform")
        current_host_id = selection.get("current_host_id")
        if not (platforms or []) and not selected_host_ids:
            pass
        elif source == "ai_fallback":
            if current_supported is not False or len(selected_host_ids) != 1:
                errors.append(
                    _err(
                        "verification_host_selection_invalid",
                        "ai_fallback requires project_includes_current_platform=false "
                        "and exactly one selected host",
                    )
                )
        elif source == "current_platform_default" and (
            current_supported is not True or selected_host_ids != [current_host_id]
        ):
            errors.append(
                _err(
                    "verification_host_selection_invalid",
                    "current_platform_default must select only current_host_id",
                )
            )
        if (
            mode == "unattended"
            and current_supported is True
            and source != "current_platform_default"
        ):
            errors.append(
                _err(
                    "verification_host_selection_invalid",
                    "unattended mode must use current_platform_default when the project "
                    "supports the current platform",
                )
            )
        for host_id in selected_host_ids:
            host = hosts_by_id.get(host_id, {})
            if host.get("status") != "available" or host.get("e2e_capable") is not True:
                errors.append(
                    _err(
                        "verification_host_selection_unavailable",
                        f"selected host {host_id} must be available and e2e_capable=true",
                    )
                )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "verification_host_matrix_lint_failed",
        "errors": errors,
        "hosts_by_id": hosts_by_id,
    }


def lint_manual_test_residuals(
    residuals: Any,
    *,
    leftovers: str | None = None,
    outcome: str | None = None,
) -> list[dict[str, str]]:
    """Hard-to-automate drops must remind the user to manual-test the feature."""
    errors: list[dict[str, str]] = []
    residual_list = residuals if isinstance(residuals, list) else []
    manual_rows: list[dict[str, Any]] = []
    for item in residual_list:
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        if isinstance(code, str) and code in MANUAL_TEST_RESIDUAL_CODES:
            manual_rows.append(item)
    if not manual_rows:
        return errors

    if outcome == "green":
        errors.append(
            _err(
                "e2e_campaign_manual_test_reminder_missing",
                "manual-test residuals cannot close as outcome=green; "
                "use green_with_residuals and remind the user",
            )
        )

    for index, row in enumerate(manual_rows):
        feature = row.get("feature")
        if not _nonempty_str(feature):
            errors.append(
                _err(
                    "e2e_campaign_manual_test_reminder_missing",
                    f"manual-test residual[{index}] requires non-empty feature "
                    "(user-facing name of what to hand-test)",
                )
            )

    if not isinstance(leftovers, str) or not leftovers.strip():
        errors.append(
            _err(
                "e2e_campaign_manual_test_reminder_missing",
                "manual-test residuals require plain.leftovers with a hand-test reminder",
            )
        )
    else:
        lowered = leftovers.lower()
        if not any(marker.lower() in lowered for marker in MANUAL_REMINDER_MARKERS):
            errors.append(
                _err(
                    "e2e_campaign_manual_test_reminder_missing",
                    "plain.leftovers must explicitly ask for 手工/手动/manual testing "
                    "when automation was skipped as too hard",
                )
            )
        for row in manual_rows:
            feature = row.get("feature")
            if _nonempty_str(feature):
                assert isinstance(feature, str)
                if feature.strip() not in leftovers:
                    errors.append(
                        _err(
                            "e2e_campaign_manual_test_reminder_missing",
                            "plain.leftovers must name the skipped feature for hand-test: "
                            + feature.strip(),
                        )
                    )
    return errors


def lint_host_availability_residuals(
    host_matrix: Any,
    residuals: Any,
    *,
    outcome: str | None = None,
) -> list[dict[str, str]]:
    """L6/L7: unavailable required hosts need residual; green alone fails."""
    errors: list[dict[str, str]] = []
    if not isinstance(host_matrix, dict):
        return errors
    hosts = host_matrix.get("hosts")
    if not isinstance(hosts, list):
        return errors
    residual_list = residuals if isinstance(residuals, list) else []
    codes = _residual_codes(residual_list)
    selection = host_matrix.get("selection")
    selected_ids = set()
    if isinstance(selection, dict):
        selected_ids = set(_as_str_list(selection.get("selected_host_ids")) or [])
    unavailable_required = [
        h
        for h in hosts
        if isinstance(h, dict) and h.get("id") in selected_ids and h.get("status") == "unavailable"
    ]
    if not unavailable_required:
        return errors
    if not codes & HOST_UNAVAILABLE_RESIDUAL_CODES:
        errors.append(
            _err(
                "e2e_campaign_host_unavailable",
                "required host status=unavailable needs e2e_campaign_host_unavailable "
                "(or verification_host_unavailable) residual",
            )
        )
    if outcome == "green":
        errors.append(
            _err(
                "e2e_campaign_host_unavailable",
                "unavailable host cannot close as outcome=green; "
                "use green_with_residuals or blocked_external",
            )
        )
    return errors


def lint_external_device_handoffs(
    host_matrix: Any,
    handoffs: Any,
    *,
    outcome: str | None = None,
) -> list[dict[str, str]]:
    """Non-selected product platforms stay untested and require acknowledgement."""
    if not isinstance(host_matrix, dict):
        return []
    project_platforms = _as_str_list(host_matrix.get("project_platforms")) or []
    selection = host_matrix.get("selection")
    hosts = host_matrix.get("hosts")
    if not isinstance(selection, dict) or not isinstance(hosts, list):
        return []
    selected_ids = set(_as_str_list(selection.get("selected_host_ids")) or [])
    selected_platforms: set[str] = set()
    for host in hosts:
        if not isinstance(host, dict) or host.get("id") not in selected_ids:
            continue
        selected_platforms.update(_as_str_list(host.get("platforms")) or [])
    required = sorted(set(project_platforms) - selected_platforms)
    rows = handoffs if isinstance(handoffs, list) else []
    by_platform = {
        row.get("platform"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("platform"), str)
    }
    errors: list[dict[str, str]] = []
    for platform_id in required:
        row = by_platform.get(platform_id)
        if row is None:
            errors.append(
                _err(
                    "external_device_handoff_missing",
                    f"non-selected platform {platform_id} requires an external-device handoff",
                )
            )
            continue
        if row.get("tested") is not False:
            errors.append(
                _err(
                    "external_device_test_overclaim",
                    f"{platform_id} handoff must preserve tested=false",
                )
            )
        if row.get("handoff") != "user_external_device_test":
            errors.append(
                _err(
                    "external_device_handoff_missing",
                    f"{platform_id} handoff must be user_external_device_test",
                )
            )
        acknowledgement = row.get("acknowledgement")
        if acknowledgement not in {"pending", "acknowledged"}:
            errors.append(
                _err(
                    "external_device_handoff_missing",
                    f"{platform_id} acknowledgement must be pending|acknowledged",
                )
            )
        if outcome in {"green", "green_with_residuals"} and acknowledgement != "acknowledged":
            errors.append(
                _err(
                    "external_device_handoff_unacknowledged",
                    f"{platform_id} handoff must be acknowledged before acceptance completes",
                )
            )
    return errors


def _adopted_journey_ids_from_project_work(project_work: Any) -> list[str]:
    if not isinstance(project_work, dict):
        return []
    ids: list[str] = []
    product = project_work.get("product")
    if isinstance(product, dict):
        primaries = product.get("primary_user_journeys") or []
        if isinstance(primaries, list):
            for index, item in enumerate(primaries):
                if isinstance(item, str) and item.strip():
                    ids.append(item.strip())
                elif isinstance(item, dict):
                    jid = item.get("journey_id") or item.get("id") or item.get("title")
                    if isinstance(jid, str) and jid.strip():
                        ids.append(jid.strip())
                    else:
                        ids.append(f"primary_user_journeys[{index}]")
    coverage = project_work.get("product_spec_coverage")
    if isinstance(coverage, dict):
        rows = coverage.get("journey_coverage") or []
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                disposition = row.get("disposition")
                if disposition in {"needs_clarification", "out_of_scope"}:
                    continue
                if disposition not in {None, "adopted"}:
                    continue
                jid = row.get("journey_id")
                if isinstance(jid, str) and jid.strip():
                    ids.append(jid.strip())
    # Stable unique order
    seen: set[str] = set()
    out: list[str] = []
    for jid in ids:
        if jid not in seen:
            seen.add(jid)
            out.append(jid)
    return out


def _project_journey_steps(project_work: Any) -> dict[str, dict[str, dict[str, Any]]]:
    if not isinstance(project_work, dict):
        return {}
    coverage = project_work.get("product_spec_coverage")
    if not isinstance(coverage, dict):
        return {}
    traceability = coverage.get("journey_step_traceability")
    if (
        not isinstance(traceability, dict)
        or traceability.get("schema") != "granoflow_journey_step_traceability_v1"
    ):
        return {}
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for journey in traceability.get("journeys", []):
        if not isinstance(journey, dict) or not _nonempty_str(journey.get("journey_id")):
            continue
        journey_id = str(journey["journey_id"])
        steps: dict[str, dict[str, Any]] = {}
        for step in journey.get("steps", []):
            if isinstance(step, dict) and _nonempty_str(step.get("step_id")):
                steps[str(step["step_id"])] = step
        out[journey_id] = steps
    return out


def _project_background_activities(project_work: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(project_work, dict):
        return {}
    coverage = project_work.get("product_spec_coverage")
    if not isinstance(coverage, dict):
        return {}
    contract = coverage.get("background_activity_control")
    if (
        not isinstance(contract, dict)
        or contract.get("schema") != "granoflow_background_activity_control_v1"
    ):
        return {}
    return {
        str(row["activity_id"]): row
        for row in contract.get("activities", [])
        if isinstance(row, dict) and _nonempty_str(row.get("activity_id"))
    }


def _lint_post_update_sequence(
    sequence: Any,
    *,
    prefix: str,
    activity: dict[str, Any],
) -> list[dict[str, str]]:
    if not isinstance(sequence, dict):
        return [
            _err(
                "post_update_interaction_test_missing",
                f"{prefix}: from the visible entry, observe two real background "
                "updates with a user action between them and prove it remains effective",
            )
        ]
    errors: list[dict[str, str]] = []
    for field in ("first_background_event", "second_background_event"):
        event = sequence.get(field)
        if (
            not isinstance(event, dict)
            or not _nonempty_str(event.get("signal"))
            or event.get("evidence_kind") not in VALID_BACKGROUND_EVENT_EVIDENCE
            or not _nonempty_str(event.get("evidence_ref"))
        ):
            errors.append(
                _err(
                    "background_event_evidence_missing",
                    f"{prefix}.{field}: identify an observed state/event signal and "
                    "evidence; elapsed time or a fixed wait is not evidence",
                )
            )
    action = sequence.get("protected_user_action")
    controls = set(_as_str_list(activity.get("controls_that_must_keep_working")) or [])
    if (
        not isinstance(action, dict)
        or action.get("control_ref") not in controls
        or not _nonempty_str(action.get("evidence_ref"))
        or not _nonempty_str(sequence.get("user_action_preserved"))
    ):
        errors.append(
            _err(
                "post_update_interaction_test_missing",
                f"{prefix}: after the first update operate a declared protected "
                "control, then prove the second update did not undo that action",
            )
        )
    exit_actions = set(_as_str_list(activity.get("ways_to_exit")) or [])
    if (
        not _nonempty_str(sequence.get("exit_action"))
        or sequence.get("exit_action") not in exit_actions
        or not _nonempty_str(sequence.get("activity_ended"))
    ):
        errors.append(
            _err(
                "activity_exit_not_proven",
                f"{prefix}: use a declared exit action and provide observable proof "
                "that the activity no longer runs or updates the interface",
            )
        )
    if not _nonempty_str(sequence.get("activity_started")):
        errors.append(
            _err(
                "post_update_interaction_test_missing",
                f"{prefix}.activity_started must identify visible start evidence",
            )
        )
    return errors


def _lint_human_path_execution(
    value: Any,
    *,
    project_steps_by_journey: dict[str, dict[str, dict[str, Any]]],
    cases_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    if not isinstance(value, dict) or value.get("schema") != HUMAN_PATH_EXECUTION_SCHEMA:
        return [
            _err(
                "e2e_campaign_human_interaction_evidence_missing",
                "full_project_e2e requires granoflow_human_path_execution_v1",
            )
        ]
    rows = value.get("rows")
    if not isinstance(rows, list) or not rows:
        return [
            _err(
                "e2e_campaign_human_interaction_evidence_missing",
                "human_path_execution.rows must contain the ordered real user actions",
            )
        ]

    errors: list[dict[str, str]] = []
    observed_steps: dict[str, list[tuple[int, int]]] = {}
    sequences: list[int] = []
    for index, row in enumerate(rows):
        prefix = f"human_path_execution.rows[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "e2e_campaign_human_interaction_evidence_missing",
                    f"{prefix} must be an object",
                )
            )
            continue
        sequence = row.get("sequence")
        journey_id = row.get("journey_id")
        step_id = row.get("step_id")
        case_id = row.get("case_id")
        action = row.get("action")
        method = row.get("navigation_method")
        case = cases_by_id.get(str(case_id)) if _nonempty_str(case_id) else None
        step = (
            project_steps_by_journey.get(str(journey_id), {}).get(str(step_id))
            if _nonempty_str(journey_id) and _nonempty_str(step_id)
            else None
        )
        if not isinstance(sequence, int) or sequence < 1:
            errors.append(
                _err(
                    "e2e_campaign_interaction_order_mismatch",
                    f"{prefix}.sequence must be a positive integer",
                )
            )
        else:
            sequences.append(sequence)
        if case is None or case.get("entry_style") != "human_path":
            errors.append(
                _err(
                    "e2e_campaign_human_interaction_evidence_missing",
                    f"{prefix}: case_id must identify a human_path case",
                )
            )
        elif step_id not in (_as_str_list(case.get("journey_step_ids")) or []):
            errors.append(
                _err(
                    "e2e_campaign_human_interaction_evidence_missing",
                    f"{prefix}: case does not claim step_id {step_id}",
                )
            )
        if step is None:
            errors.append(
                _err(
                    "e2e_campaign_human_interaction_evidence_missing",
                    f"{prefix}: journey_id/step_id is not in Project Work",
                )
            )
            continue
        if method not in FULL_PROJECT_NAVIGATION_METHODS:
            errors.append(
                _err(
                    "e2e_campaign_forbidden_navigation_method",
                    f"{prefix}: full-project user steps may use only app_launch, "
                    "visible_control, or os_control",
                )
            )
        surface = step.get("interaction_surface")
        boundary = step.get("platform_boundary")
        if (surface in {"os_chrome", "mixed"} or boundary in {"plugin", "os"}) and (
            method != "os_control" or row.get("evidence_kind") != "host_event"
        ):
            errors.append(
                _err(
                    "e2e_campaign_forbidden_navigation_method",
                    f"{prefix}: OS-bound step requires os_control with host_event evidence",
                )
            )
        if (
            action not in VALID_HUMAN_ACTIONS
            or not _nonempty_str(row.get("before_observation"))
            or not _nonempty_str(row.get("after_observation"))
            or row.get("evidence_kind") not in VALID_HUMAN_EVIDENCE
            or not _nonempty_str(row.get("evidence_ref"))
            or (action not in {"launch", "observe"} and not _nonempty_str(row.get("control_ref")))
        ):
            errors.append(
                _err(
                    "e2e_campaign_human_interaction_evidence_missing",
                    f"{prefix}: name the visible control/action, before and after "
                    "observations, and driver/host event evidence; screenshots alone "
                    "do not prove the interaction",
                )
            )
        project_sequence = step.get("sequence")
        if not isinstance(project_sequence, int) or project_sequence < 1:
            errors.append(
                _err(
                    "e2e_campaign_interaction_order_mismatch",
                    f"{prefix}: Project Work step sequence must be a positive integer",
                )
            )
        elif isinstance(sequence, int):
            observed_steps.setdefault(str(journey_id), []).append((sequence, project_sequence))

    if sequences != list(range(1, len(rows) + 1)):
        errors.append(
            _err(
                "e2e_campaign_interaction_order_mismatch",
                "human_path_execution rows must be in continuous execution order",
            )
        )

    required_steps: set[str] = set()
    observed_step_ids = {
        str(row.get("step_id"))
        for row in rows
        if isinstance(row, dict) and _nonempty_str(row.get("step_id"))
    }
    for journey_id, steps in project_steps_by_journey.items():
        expected = sorted(
            (step["sequence"], step_id)
            for step_id, step in steps.items()
            if "e2e" in (_as_str_list(step.get("required_test_layers")) or [])
            and isinstance(step.get("sequence"), int)
            and step["sequence"] >= 1
        )
        required_steps.update(step_id for _, step_id in expected)
        actual_project_sequences = [
            project_sequence for _, project_sequence in sorted(observed_steps.get(journey_id, []))
        ]
        if actual_project_sequences != [sequence for sequence, _ in expected]:
            errors.append(
                _err(
                    "e2e_campaign_interaction_order_mismatch",
                    f"{journey_id}: interaction rows must preserve Project Work step order",
                )
            )
    missing = sorted(required_steps - observed_step_ids)
    if missing:
        errors.append(
            _err(
                "e2e_campaign_human_interaction_evidence_missing",
                "full-project E2E steps missing real interaction evidence: " + ", ".join(missing),
            )
        )
    return errors


def lint_coverage_matrix(
    data: Any,
    *,
    case_ids: set[str] | None = None,
    checkpoint_ids: set[str] | None = None,
    project_work: Any | None = None,
    hosts_by_id: dict[str, dict[str, Any]] | None = None,
    require_host_ids: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "e2e_campaign_coverage_incomplete",
            "errors": [
                _err("e2e_campaign_coverage_incomplete", "coverage_matrix must be object"),
            ],
        }

    if data.get("schema") != COVERAGE_MATRIX_SCHEMA:
        errors.append(
            _err(
                "e2e_campaign_coverage_incomplete",
                f"schema must be {COVERAGE_MATRIX_SCHEMA}",
            )
        )

    sources = data.get("sources_loaded")
    if not isinstance(sources, list) or not sources or any(not isinstance(s, str) for s in sources):
        errors.append(
            _err(
                "e2e_campaign_coverage_unloaded",
                "sources_loaded must be a non-empty string list",
            )
        )
    else:
        joined = " ".join(sources).lower()
        if "project_work" not in joined and "product_spec" not in joined:
            errors.append(
                _err(
                    "e2e_campaign_coverage_unloaded",
                    "sources_loaded must include Project Work journey/acceptance sources",
                )
            )

    journeys = data.get("required_journeys")
    if not isinstance(journeys, list) or not journeys:
        errors.append(
            _err(
                "e2e_campaign_coverage_incomplete",
                "required_journeys must be a non-empty list",
            )
        )
        journeys = []

    matrix_ids: set[str] = set()
    enforce_hosts = require_host_ids or hosts_by_id is not None
    host_catalog = hosts_by_id or {}
    project_steps_by_journey = _project_journey_steps(project_work)

    for index, row in enumerate(journeys):
        prefix = f"required_journeys[{index}]"
        if not isinstance(row, dict):
            errors.append(_err("e2e_campaign_coverage_incomplete", f"{prefix} must be object"))
            continue
        jid = row.get("journey_id")
        if not _nonempty_str(jid):
            errors.append(_err("e2e_campaign_coverage_incomplete", f"{prefix}.journey_id required"))
            continue
        assert isinstance(jid, str)
        matrix_ids.add(jid)
        status = row.get("status")
        if status not in COVERED_JOURNEY_STATUSES:
            errors.append(
                _err(
                    "e2e_campaign_coverage_incomplete",
                    f"{prefix}.status must be "
                    "covered|deferred_external|deferred_manual|out_of_scope",
                )
            )
            continue
        if status == "covered":
            errors.extend(lint_interaction_surface_row(row, prefix=prefix))
            if project_steps_by_journey:
                journey_steps = project_steps_by_journey.get(jid, {})
                step_ids = _as_str_list(row.get("step_ids"))
                if not step_ids:
                    errors.append(
                        _err(
                            "e2e_campaign_step_traceability_missing",
                            f"{prefix}: covered requires step_ids for traced Project Work",
                        )
                    )
                    step_ids = []
                unknown_steps = sorted(set(step_ids) - set(journey_steps))
                if unknown_steps:
                    errors.append(
                        _err(
                            "e2e_campaign_step_traceability_missing",
                            f"{prefix}: unknown journey step ids: {unknown_steps}",
                        )
                    )
                required_e2e_steps = {
                    step_id
                    for step_id, step in journey_steps.items()
                    if "e2e" in (_as_str_list(step.get("required_test_layers")) or [])
                }
                missing_steps = sorted(required_e2e_steps - set(step_ids))
                if missing_steps:
                    errors.append(
                        _err(
                            "e2e_campaign_step_traceability_missing",
                            f"{prefix}: e2e-required steps missing: {missing_steps}",
                        )
                    )
                has_os_step = any(
                    step_id in journey_steps
                    and (
                        journey_steps[step_id].get("interaction_surface") in {"os_chrome", "mixed"}
                        or journey_steps[step_id].get("platform_boundary") in {"plugin", "os"}
                    )
                    for step_id in step_ids
                )
                if has_os_step and row.get("interaction_surface") not in {"os_chrome", "mixed"}:
                    errors.append(
                        _err(
                            "e2e_campaign_os_chrome_unverified",
                            f"{prefix}: OS-bound step requires os_chrome|mixed interaction_surface",
                        )
                    )
            case_list = row.get("case_ids")
            cp_list = row.get("checkpoint_ids")
            if not isinstance(case_list, list) or not case_list:
                errors.append(
                    _err(
                        "e2e_campaign_coverage_incomplete",
                        f"{prefix}: covered requires non-empty case_ids",
                    )
                )
            elif case_ids is not None:
                missing_cases = [c for c in case_list if c not in case_ids]
                if missing_cases:
                    errors.append(
                        _err(
                            "e2e_campaign_coverage_incomplete",
                            f"{prefix}: case_ids not in suite plan: "
                            + ", ".join(map(str, missing_cases)),
                        )
                    )
            if not isinstance(cp_list, list) or not cp_list:
                errors.append(
                    _err(
                        "e2e_campaign_coverage_incomplete",
                        f"{prefix}: covered requires non-empty checkpoint_ids",
                    )
                )
            elif checkpoint_ids is not None:
                missing_cp = [c for c in cp_list if c not in checkpoint_ids]
                if missing_cp:
                    errors.append(
                        _err(
                            "e2e_campaign_coverage_incomplete",
                            f"{prefix}: checkpoint_ids not in suite plan: "
                            f"{', '.join(map(str, missing_cp))}",
                        )
                    )

            host_ids = row.get("host_ids")
            if enforce_hosts:
                if not isinstance(host_ids, list) or not host_ids:
                    errors.append(
                        _err(
                            "verification_host_unassigned_journey",
                            f"{prefix}: covered requires non-empty host_ids "
                            "when host_matrix present",
                        )
                    )
                elif any(not isinstance(h, str) or not h.strip() for h in host_ids):
                    errors.append(
                        _err(
                            "verification_host_unassigned_journey",
                            f"{prefix}: host_ids must be non-empty strings",
                        )
                    )
                elif host_catalog:
                    unknown = [h for h in host_ids if h not in host_catalog]
                    if unknown:
                        errors.append(
                            _err(
                                "verification_host_unassigned_journey",
                                f"{prefix}: host_ids not in host_matrix: "
                                + ", ".join(map(str, unknown)),
                            )
                        )
                    required_kinds = row.get("required_host_kinds") or []
                    if isinstance(required_kinds, list) and required_kinds:
                        assigned_kinds = {
                            host_catalog[h].get("kind") for h in host_ids if h in host_catalog
                        }
                        missing_kinds = [
                            k
                            for k in required_kinds
                            if isinstance(k, str) and k not in assigned_kinds
                        ]
                        if missing_kinds:
                            errors.append(
                                _err(
                                    "verification_host_platform_mismatch",
                                    f"{prefix}: required_host_kinds not satisfied: "
                                    + ", ".join(missing_kinds),
                                )
                            )

        elif status in DEFERRED_JOURNEY_STATUSES:
            residual_code = row.get("residual_code")
            if not _nonempty_str(residual_code):
                errors.append(
                    _err(
                        "e2e_campaign_coverage_incomplete",
                        f"{prefix}: {status} requires residual_code",
                    )
                )
            elif status == "deferred_manual":
                assert isinstance(residual_code, str)
                if residual_code not in MANUAL_TEST_RESIDUAL_CODES:
                    errors.append(
                        _err(
                            "e2e_campaign_manual_test_reminder_missing",
                            f"{prefix}: deferred_manual requires residual_code in "
                            "e2e_campaign_manual_test_required|"
                            "e2e_campaign_automation_too_hard "
                            "(or short aliases)",
                        )
                    )
                if not _nonempty_str(row.get("feature")):
                    errors.append(
                        _err(
                            "e2e_campaign_manual_test_reminder_missing",
                            f"{prefix}: deferred_manual requires feature "
                            "(user-facing name for the hand-test reminder)",
                        )
                    )

    if project_work is not None:
        required = _adopted_journey_ids_from_project_work(project_work)
        missing = [jid for jid in required if jid not in matrix_ids]
        if missing:
            errors.append(
                _err(
                    "e2e_campaign_coverage_incomplete",
                    "Project Work journeys missing from coverage_matrix: " + ", ".join(missing),
                )
            )

    authoring = data.get("authoring")
    if not isinstance(authoring, dict):
        errors.append(
            _err(
                "e2e_campaign_coverage_incomplete",
                "authoring object required (tests_written_or_updated + paths)",
            )
        )
    else:
        if not isinstance(authoring.get("tests_written_or_updated"), bool):
            errors.append(
                _err(
                    "e2e_campaign_coverage_incomplete",
                    "authoring.tests_written_or_updated must be boolean",
                )
            )
        paths = authoring.get("paths")
        if not isinstance(paths, list) or any(not isinstance(p, str) for p in paths):
            errors.append(
                _err(
                    "e2e_campaign_coverage_incomplete",
                    "authoring.paths must be a string list",
                )
            )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "e2e_campaign_coverage_lint_failed",
        "errors": errors,
    }


def lint_suite_plan(
    data: Any,
    *,
    project_work: Any | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "e2e_campaign_suite_plan_invalid",
            "errors": [_err("e2e_campaign_suite_plan_invalid", "suite plan must be object")],
        }

    if data.get("schema") != SUITE_PLAN_SCHEMA:
        errors.append(
            _err(
                "e2e_campaign_suite_plan_invalid",
                f"schema must be {SUITE_PLAN_SCHEMA}",
            )
        )

    if data.get("contract_loaded") is not True or data.get("orchestration_loaded") is not True:
        errors.append(
            _err(
                "e2e_campaign_suite_unorchestrated",
                "contract_loaded and orchestration_loaded must be true before suite run",
            )
        )

    if data.get("coverage_loaded") is not True:
        errors.append(
            _err(
                "e2e_campaign_coverage_unloaded",
                "coverage_loaded must be true after e2e-user-flow-coverage applied",
            )
        )

    errors.extend(
        lint_acceptance_outcomes(
            data,
            require_user_path_claim=True,
        )
    )

    if data.get("test_layer") != "e2e":
        errors.append(
            _err(
                "e2e_campaign_suite_plan_invalid",
                "test_layer must be e2e",
            )
        )

    fidelity = data.get("interaction_fidelity")
    if fidelity in WRONG_LAYER_FIDELITY:
        errors.append(
            _err(
                "e2e_campaign_fidelity_invalid",
                "service_path belongs to integration_campaign; use human_path|hybrid|route_fast",
            )
        )
    elif fidelity not in VALID_FIDELITY:
        errors.append(
            _err(
                "e2e_campaign_fidelity_invalid",
                f"interaction_fidelity must be one of {sorted(VALID_FIDELITY)}",
            )
        )
    scope = data.get("e2e_scope")
    if scope == "full_project_e2e" and fidelity != "human_path":
        errors.append(
            _err(
                "e2e_campaign_full_project_requires_human_path",
                "full_project_e2e requires interaction_fidelity=human_path; "
                "hybrid and route_fast cannot close the complete user path",
            )
        )

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(_err("e2e_campaign_suite_plan_invalid", "cases must be a non-empty list"))
        cases = []

    case_by_id: dict[str, dict[str, Any]] = {}
    project_steps_by_journey = _project_journey_steps(project_work)
    project_steps = {
        step_id: (journey_id, step)
        for journey_id, steps in project_steps_by_journey.items()
        for step_id, step in steps.items()
    }
    claimed_step_ids: set[str] = set()
    case_activity_ids: dict[str, list[str]] = {}
    shortcut_bypassed_steps: dict[str, list[str]] = {}
    background_activities = _project_background_activities(project_work)
    required_background_activities = {
        activity_id
        for activity_id, activity in background_activities.items()
        if "e2e" in (_as_str_list(activity.get("required_test_layers")) or [])
    }
    claimed_background_activities: set[str] = set()
    if project_steps:
        if data.get("test_route_traceability_loaded") is not True:
            errors.append(
                _err(
                    "e2e_campaign_test_routes_unloaded",
                    "test_route_traceability_loaded must be true for traced Project Work",
                )
            )
        if scope not in VALID_E2E_SCOPES:
            errors.append(
                _err(
                    "e2e_campaign_scope_invalid",
                    f"e2e_scope must be one of {sorted(VALID_E2E_SCOPES)}",
                )
            )
        elif scope != "full_project_e2e" and data.get("user_path_claim") == "full_user_path":
            errors.append(
                _err(
                    "e2e_campaign_scope_overclaim",
                    f"e2e_scope={scope} cannot claim full_user_path",
                )
            )
    if (
        required_background_activities
        and data.get("background_activity_control_loaded") is not True
    ):
        errors.append(
            _err(
                "post_update_interaction_test_missing",
                "background_activity_control_loaded must be true before running "
                "visible background-activity journeys",
            )
        )
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(_err("e2e_campaign_suite_plan_invalid", f"{prefix} must be object"))
            continue
        case_id = case.get("id")
        if not _nonempty_str(case_id):
            errors.append(_err("e2e_campaign_suite_plan_invalid", f"{prefix}.id required"))
            continue
        assert isinstance(case_id, str)
        case_by_id[case_id] = case
        if not _nonempty_str(case.get("path")):
            errors.append(_err("e2e_campaign_suite_plan_invalid", f"{prefix}.path required"))

        entry = case.get("entry_style")
        if entry not in VALID_ENTRY:
            errors.append(
                _err(
                    "e2e_campaign_suite_plan_invalid",
                    f"{prefix}.entry_style must be human_path|route_shortcut",
                )
            )
        elif entry == "route_shortcut" and not _nonempty_str(case.get("route_shortcut_justified")):
            errors.append(
                _err(
                    "e2e_campaign_route_shortcut_unjustified",
                    f"{prefix}: route_shortcut needs route_shortcut_justified",
                )
            )
        bypassed_step_ids = _as_str_list(case.get("bypassed_step_ids"))
        if entry == "route_shortcut":
            if bypassed_step_ids is None:
                errors.append(
                    _err(
                        "e2e_campaign_shortcut_overclaim",
                        f"{prefix}.bypassed_step_ids must be a string list",
                    )
                )
                bypassed_step_ids = []
            if scope in {"feature_e2e", "journey_e2e"} and not bypassed_step_ids:
                errors.append(
                    _err(
                        "e2e_campaign_shortcut_overclaim",
                        f"{prefix}: feature/journey shortcut must name bypassed_step_ids",
                    )
                )
            if scope == "full_project_e2e" and bypassed_step_ids:
                errors.append(
                    _err(
                        "e2e_campaign_visible_step_bypassed",
                        f"{prefix}: full-project support shortcut cannot bypass "
                        "a Project Work journey step",
                    )
                )
            unknown_bypassed_steps = sorted(set(bypassed_step_ids) - set(project_steps))
            if unknown_bypassed_steps:
                errors.append(
                    _err(
                        "e2e_campaign_shortcut_overclaim",
                        f"{prefix}: bypassed_step_ids must name Project Work steps; "
                        f"unknown ids: {unknown_bypassed_steps}",
                    )
                )
            shortcut_bypassed_steps[case_id] = bypassed_step_ids
        elif bypassed_step_ids:
            errors.append(
                _err(
                    "e2e_campaign_shortcut_overclaim",
                    f"{prefix}: human_path case cannot declare bypassed_step_ids",
                )
            )
        activity_ids = _as_str_list(case.get("background_activity_ids"))
        if required_background_activities and activity_ids is None:
            errors.append(
                _err(
                    "post_update_interaction_test_missing",
                    f"{prefix}.background_activity_ids must be a string list",
                )
            )
            activity_ids = []
        case_activity_ids[case_id] = activity_ids or []
        for activity_id in activity_ids or []:
            activity = background_activities.get(activity_id)
            if activity is None:
                errors.append(
                    _err(
                        "post_update_interaction_test_missing",
                        f"{prefix}: unknown background activity {activity_id}",
                    )
                )
                continue
            claimed_background_activities.add(activity_id)
            if entry != "human_path":
                errors.append(
                    _err(
                        "post_update_interaction_test_missing",
                        f"{prefix}: background activity {activity_id} must start from "
                        "its real visible user entry, not a route shortcut",
                    )
                )
            errors.extend(
                _lint_post_update_sequence(
                    case.get("post_update_sequence"),
                    prefix=prefix,
                    activity=activity,
                )
            )
        if project_steps:
            step_ids = _as_str_list(case.get("journey_step_ids"))
            if step_ids is None:
                errors.append(
                    _err(
                        "e2e_campaign_step_traceability_missing",
                        f"{prefix}.journey_step_ids must be a string list",
                    )
                )
                step_ids = []
            elif not step_ids and not _nonempty_str(case.get("supporting_case_reason")):
                errors.append(
                    _err(
                        "e2e_campaign_step_traceability_missing",
                        f"{prefix}: empty journey_step_ids requires supporting_case_reason",
                    )
                )
            if set(step_ids) & set(bypassed_step_ids or []):
                errors.append(
                    _err(
                        "e2e_campaign_visible_step_bypassed",
                        f"{prefix}: a journey step cannot be both covered and bypassed",
                    )
                )
            if scope == "full_project_e2e" and entry == "route_shortcut":
                if step_ids or activity_ids:
                    errors.append(
                        _err(
                            "e2e_campaign_route_shortcut_claims_user_path",
                            f"{prefix}: full-project route_shortcut is support-only and "
                            "cannot claim journey steps or background activities",
                        )
                    )
                if not _nonempty_str(case.get("supporting_case_reason")):
                    errors.append(
                        _err(
                            "e2e_campaign_shortcut_overclaim",
                            f"{prefix}: support-only shortcut requires supporting_case_reason",
                        )
                    )
            claimed_step_ids.update(step_ids)
            for step_id in step_ids:
                record = project_steps.get(step_id)
                if record is None:
                    errors.append(
                        _err(
                            "e2e_campaign_step_traceability_missing",
                            f"{prefix}: unknown journey step {step_id}",
                        )
                    )
                    continue
                _, step = record
                required_layers = _as_str_list(step.get("required_test_layers")) or []
                if "e2e" not in required_layers:
                    errors.append(
                        _err(
                            "e2e_campaign_step_traceability_missing",
                            f"{prefix}: {step_id} is not declared for e2e",
                        )
                    )
                if step.get("step_type") == "entry" and entry != "human_path":
                    errors.append(
                        _err(
                            "e2e_campaign_visible_entry_missing",
                            f"{prefix}: entry step {step_id} requires entry_style=human_path",
                        )
                    )
                if not _nonempty_str(case.get("entry_ref")) or not _nonempty_str(
                    case.get("observable_result")
                ):
                    errors.append(
                        _err(
                            "e2e_campaign_visible_entry_missing",
                            f"{prefix}: entry_ref and observable_result required",
                        )
                    )

    order = data.get("order")
    if not isinstance(order, list) or not all(isinstance(x, str) for x in order):
        errors.append(_err("e2e_campaign_suite_plan_invalid", "order must be a list of case ids"))
    elif case_by_id and set(order) != set(case_by_id):
        errors.append(
            _err(
                "e2e_campaign_suite_plan_invalid",
                "order must list each case id exactly once",
            )
        )

    checkpoints = data.get("checkpoints")
    checkpoint_ids: set[str] = set()
    if not isinstance(checkpoints, list) or not checkpoints:
        errors.append(
            _err(
                "e2e_campaign_suite_plan_invalid",
                "checkpoints must be a non-empty list (screenshot steps per covered journeys)",
            )
        )
        checkpoints = []
    else:
        for index, checkpoint in enumerate(checkpoints):
            prefix = f"checkpoints[{index}]"
            if not isinstance(checkpoint, dict):
                errors.append(_err("e2e_campaign_suite_plan_invalid", f"{prefix} must be object"))
                continue
            step_id = checkpoint.get("step_id")
            if not _nonempty_str(step_id):
                errors.append(_err("e2e_campaign_suite_plan_invalid", f"{prefix}.step_id required"))
            else:
                assert isinstance(step_id, str)
                checkpoint_ids.add(step_id)
            capture = checkpoint.get("capture")
            if capture != "screenshot":
                errors.append(
                    _err(
                        "e2e_campaign_suite_plan_invalid",
                        f"{prefix}.capture must be screenshot",
                    )
                )

    matrix = data.get("coverage_matrix")
    platforms = platforms_from_project_work(project_work) if project_work is not None else []
    host_matrix = data.get("host_matrix")
    require_matrix = bool(platforms) or host_matrix is not None
    host_lint = lint_host_matrix(
        host_matrix,
        platforms=platforms if platforms else None,
        require_present=require_matrix and bool(platforms),
    )
    if (host_matrix is not None or (require_matrix and bool(platforms))) and not host_lint["ok"]:
        errors.extend(host_lint["errors"])
    hosts_by_id = host_lint.get("hosts_by_id") or {}
    if host_matrix is not None:
        errors.extend(
            lint_host_availability_residuals(
                host_matrix,
                data.get("residuals") or [],
                outcome=None,
            )
        )

    if project_steps:
        required_e2e_steps = {
            step_id
            for step_id, (_, step) in project_steps.items()
            if "e2e" in (_as_str_list(step.get("required_test_layers")) or [])
        }
        declared_shortcuts = {
            step_id
            for bypassed_step_ids in shortcut_bypassed_steps.values()
            for step_id in bypassed_step_ids
        }
        if scope == "full_project_e2e":
            declared_shortcuts = set()
        missing_steps = sorted(required_e2e_steps - claimed_step_ids - declared_shortcuts)
        if missing_steps:
            errors.append(
                _err(
                    "e2e_campaign_step_traceability_missing",
                    "e2e-required journey steps missing from cases: " + ", ".join(missing_steps),
                )
            )

    missing_activities = sorted(required_background_activities - claimed_background_activities)
    if missing_activities:
        errors.append(
            _err(
                "post_update_interaction_test_missing",
                "e2e-required background activities missing from visible user-path "
                "cases: " + ", ".join(missing_activities),
            )
        )

    ship_bar = data.get("ship_bar")
    if ship_bar is not None and ship_bar not in VALID_SHIP_BARS:
        errors.append(
            _err(
                "e2e_campaign_suite_plan_invalid",
                "ship_bar must be market_smoke|form_factor_smoke|full_campaign",
            )
        )
    # L9: omitted ship_bar normalizes to market_smoke (no error).
    _ = normalize_ship_bar(ship_bar)

    errors.extend(lint_visible_window_suite_plan(data))

    concurrency = data.get("concurrency")
    if concurrency is not None and concurrency not in VALID_CONCURRENCY:
        errors.append(
            _err(
                "e2e_campaign_suite_plan_invalid",
                "concurrency must be sequential|parallel_when_capable",
            )
        )

    if matrix is None and _nonempty_str(data.get("coverage_matrix_ref")):
        errors.append(
            _err(
                "e2e_campaign_coverage_incomplete",
                "coverage_matrix_ref present but coverage_matrix object missing; "
                "embed matrix in suite plan for lint, or pass --kind coverage_matrix",
            )
        )
    elif matrix is None:
        errors.append(
            _err(
                "e2e_campaign_coverage_unloaded",
                "coverage_matrix object required on suite plan",
            )
        )
    else:
        nested = lint_coverage_matrix(
            matrix,
            case_ids=set(case_by_id),
            checkpoint_ids=checkpoint_ids,
            project_work=project_work,
            hosts_by_id=hosts_by_id if host_matrix is not None else None,
            require_host_ids=host_matrix is not None,
        )
        if not nested["ok"]:
            errors.extend(nested["errors"])
        if project_steps and data.get("e2e_scope") == "full_project_e2e":
            rows = matrix.get("required_journeys") if isinstance(matrix, dict) else None
            if not isinstance(rows, list) or any(
                not isinstance(row, dict) or row.get("status") != "covered" for row in rows
            ):
                errors.append(
                    _err(
                        "e2e_campaign_scope_overclaim",
                        "full_project_e2e requires every required journey to be covered",
                    )
                )
        matrix_rows = matrix.get("required_journeys") if isinstance(matrix, dict) else []
        covered_case_ids: set[str] = set()
        covered_step_ids: set[str] = set()
        if isinstance(matrix_rows, list):
            for row in matrix_rows:
                if not isinstance(row, dict) or row.get("status") != "covered":
                    continue
                covered_case_ids.update(_as_str_list(row.get("case_ids")) or [])
                covered_step_ids.update(_as_str_list(row.get("step_ids")) or [])
        acceptance_case_ids: set[str] = set()
        acceptance_rows = data.get("acceptance_outcomes")
        if isinstance(acceptance_rows, list):
            for row in acceptance_rows:
                if isinstance(row, dict):
                    acceptance_case_ids.update(_as_str_list(row.get("case_ids")) or [])

        if scope == "full_project_e2e":
            claimed_user_case_ids = (
                covered_case_ids
                | acceptance_case_ids
                | {case_id for case_id, activity_ids in case_activity_ids.items() if activity_ids}
            )
            for case_id in sorted(claimed_user_case_ids):
                case = case_by_id.get(case_id)
                if case is not None and case.get("entry_style") != "human_path":
                    errors.append(
                        _err(
                            "e2e_campaign_route_shortcut_claims_user_path",
                            f"{case_id}: coverage, acceptance, checkpoint-bearing journey, "
                            "or background activity requires a human_path case",
                        )
                    )
        for case_id, bypassed_steps in shortcut_bypassed_steps.items():
            if scope == "full_project_e2e" and (
                case_id in covered_case_ids or case_id in acceptance_case_ids
            ):
                errors.append(
                    _err(
                        "e2e_campaign_route_shortcut_claims_user_path",
                        f"{case_id}: route_shortcut cannot close coverage or acceptance",
                    )
                )
            overlap = sorted(set(bypassed_steps) & covered_step_ids)
            if overlap:
                errors.append(
                    _err(
                        "e2e_campaign_visible_step_bypassed",
                        f"{case_id}: bypassed steps cannot be marked covered: {overlap}",
                    )
                )

    if scope == "full_project_e2e" and project_steps_by_journey:
        errors.extend(
            _lint_human_path_execution(
                data.get("human_path_execution"),
                project_steps_by_journey=project_steps_by_journey,
                cases_by_id=case_by_id,
            )
        )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "e2e_campaign_suite_plan_lint_failed",
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
                    "e2e_campaign_change_report_missing",
                    "code or test changes present but change report missing",
                )
            )
        return {
            "ok": not errors,
            "code": "ok" if not errors else "e2e_campaign_change_report_lint_failed",
            "errors": errors,
        }

    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "e2e_campaign_change_report_lint_failed",
            "errors": [
                _err("e2e_campaign_change_report_incomplete", "change report must be object")
            ],
        }

    if data.get("schema") != CHANGE_REPORT_SCHEMA:
        errors.append(
            _err(
                "e2e_campaign_change_report_incomplete",
                f"schema must be {CHANGE_REPORT_SCHEMA}",
            )
        )

    status = data.get("status")
    if status not in {"no_code_changes", "changes_present"}:
        errors.append(
            _err(
                "e2e_campaign_change_report_incomplete",
                "status must be no_code_changes|changes_present",
            )
        )

    product_changes = data.get("product_changes")
    test_changes = data.get("test_changes")
    if not isinstance(product_changes, list) or not isinstance(test_changes, list):
        errors.append(
            _err(
                "e2e_campaign_change_report_incomplete",
                "product_changes and test_changes must be lists",
            )
        )
        product_changes = []
        test_changes = []

    if status == "no_code_changes" and (product_changes or test_changes):
        errors.append(
            _err(
                "e2e_campaign_change_report_inconsistent",
                "no_code_changes cannot list product_changes or test_changes",
            )
        )

    if status == "changes_present":
        if not product_changes and not test_changes:
            errors.append(
                _err(
                    "e2e_campaign_change_report_incomplete",
                    "changes_present requires product_changes or test_changes",
                )
            )
        if not _nonempty_str(data.get("product_behavior_delta")):
            errors.append(
                _err(
                    "e2e_campaign_change_report_incomplete",
                    "product_behavior_delta required (use none when tests-only)",
                )
            )
        if not _nonempty_str(data.get("why")):
            errors.append(_err("e2e_campaign_change_report_incomplete", "why required"))
        failed_before = data.get("failed_before")
        if not isinstance(failed_before, list) or not failed_before:
            errors.append(
                _err(
                    "e2e_campaign_change_report_incomplete",
                    "failed_before must be a non-empty list when changes_present",
                )
            )
        if not _nonempty_str(data.get("passed_after_evidence")):
            errors.append(
                _err(
                    "e2e_campaign_change_report_incomplete",
                    "passed_after_evidence required",
                )
            )

    if code_changed is True and status != "changes_present":
        errors.append(
            _err(
                "e2e_campaign_change_report_missing",
                "code_changed=true requires status=changes_present",
            )
        )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "e2e_campaign_change_report_lint_failed",
        "errors": errors,
    }


def lint_campaign_state(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "e2e_campaign_state_lint_failed",
            "errors": [_err("e2e_campaign_state_invalid", "state must be object")],
        }

    if data.get("schema") != CAMPAIGN_STATE_SCHEMA:
        errors.append(
            _err(
                "e2e_campaign_state_invalid",
                f"schema must be {CAMPAIGN_STATE_SCHEMA}",
            )
        )

    if data.get("campaign_drive") != "agent_auto":
        errors.append(
            _err(
                "e2e_campaign_drive_not_agent_auto",
                "campaign_drive must be agent_auto",
            )
        )

    if data.get("integration_gate") not in {"complete", "waived_single_milestone"}:
        errors.append(
            _err(
                "e2e_campaign_integration_gate_incomplete",
                "integration_gate must be complete|waived_single_milestone before e2e campaign",
            )
        )

    for field in ("screenshot_capability", "vision_capability"):
        value = data.get(field)
        if value not in VALID_CAPABILITY:
            errors.append(
                _err(
                    "e2e_campaign_screenshot_capability_unknown",
                    f"{field} must be available|unavailable",
                )
            )

    window_cap = data.get("window_capability")
    if window_cap is not None and window_cap not in VALID_CAPABILITY:
        errors.append(
            _err(
                "e2e_campaign_screenshot_capability_unknown",
                "window_capability must be available|unavailable",
            )
        )

    if data.get("screenshot_policy") != "required_if_capable":
        errors.append(
            _err(
                "e2e_campaign_state_invalid",
                "screenshot_policy must be required_if_capable",
            )
        )

    if data.get("vision_policy") != "on_if_capable":
        errors.append(_err("e2e_campaign_state_invalid", "vision_policy must be on_if_capable"))

    vision_result = data.get("vision_result")
    if vision_result not in VALID_VISION_RESULT:
        errors.append(
            _err(
                "e2e_campaign_state_invalid",
                "vision_result must be not_run|passed|failed|skipped",
            )
        )

    residuals = data.get("residuals") or []
    if not isinstance(residuals, list):
        errors.append(_err("e2e_campaign_state_invalid", "residuals must be a list"))
        residuals = []

    if vision_result == "skipped":
        codes = _residual_codes(residuals)
        if not codes & VISION_SKIP_RESIDUAL_CODES:
            errors.append(
                _err(
                    "e2e_campaign_vision_skipped_unrecorded",
                    "vision_result skipped requires vision_skipped residual",
                )
            )

    fidelity = data.get("interaction_fidelity")
    if fidelity in WRONG_LAYER_FIDELITY:
        errors.append(
            _err(
                "e2e_campaign_fidelity_invalid",
                "interaction_fidelity must not be service_path for e2e campaign",
            )
        )
    elif fidelity is not None and fidelity not in VALID_FIDELITY:
        errors.append(
            _err(
                "e2e_campaign_fidelity_invalid",
                f"interaction_fidelity must be one of {sorted(VALID_FIDELITY)}",
            )
        )

    failures = data.get("failures") or []
    if failures is None:
        failures = []
    if not isinstance(failures, list):
        errors.append(_err("e2e_campaign_state_invalid", "failures must be a list"))
        failures = []
    for index, failure in enumerate(failures):
        prefix = f"failures[{index}]"
        if not isinstance(failure, dict):
            errors.append(_err("e2e_campaign_state_invalid", f"{prefix} must be object"))
            continue
        if "failure_class" not in failure:
            errors.append(
                _err("e2e_campaign_failure_class_required", f"{prefix}.failure_class required")
            )
        elif failure.get("failure_class") not in VALID_FAILURE_CLASS:
            errors.append(
                _err("e2e_campaign_failure_class_invalid", f"{prefix}.failure_class invalid")
            )

    if data.get("phase") == "complete":
        errors.extend(
            lint_window_required_for_close(
                screenshot_capability=data.get("screenshot_capability"),
                window_capability=window_cap,
                require_window_field=True,
                outcome_or_phase="phase=complete",
            )
        )
        if normalize_display_mode(data.get("display_mode")) == "headless":
            errors.append(
                _err(
                    "e2e_campaign_headless_ui_forbidden",
                    "phase=complete forbids display_mode=headless",
                )
            )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "e2e_campaign_state_lint_failed",
        "errors": errors,
    }


def lint_evidence_pack(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "e2e_campaign_evidence_pack_lint_failed",
            "errors": [_err("e2e_campaign_evidence_pack_invalid", "evidence pack must be object")],
        }

    if data.get("schema") != EVIDENCE_PACK_SCHEMA:
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                f"schema must be {EVIDENCE_PACK_SCHEMA}",
            )
        )

    screenshot_cap = data.get("screenshot_capability")
    if screenshot_cap not in VALID_CAPABILITY:
        errors.append(
            _err(
                "e2e_campaign_screenshot_capability_unknown",
                "screenshot_capability must be available|unavailable on evidence pack",
            )
        )

    window_cap = data.get("window_capability")
    if window_cap not in VALID_CAPABILITY:
        errors.append(
            _err(
                "e2e_campaign_window_required",
                "window_capability must be available|unavailable on evidence pack",
            )
        )

    if data.get("user_facing_git_mention") is True:
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "user_facing_git_mention must be false or omitted",
            )
        )

    screenshots = data.get("screenshots")
    if screenshots is None:
        screenshots = []
    if not isinstance(screenshots, list):
        errors.append(_err("e2e_campaign_evidence_pack_invalid", "screenshots must be a list"))
        screenshots = []

    screenshot_by_step: dict[str, dict[str, Any]] = {}
    has_os_window = False
    for index, shot in enumerate(screenshots):
        prefix = f"screenshots[{index}]"
        if not isinstance(shot, dict):
            errors.append(_err("e2e_campaign_evidence_pack_invalid", f"{prefix} must be object"))
            continue
        step_id = shot.get("step_id")
        if not _nonempty_str(step_id):
            errors.append(_err("e2e_campaign_evidence_pack_invalid", f"{prefix}.step_id required"))
            continue
        assert isinstance(step_id, str)
        path = shot.get("path")
        if _nonempty_str(path):
            assert isinstance(path, str)
            if not _path_under_temp(path):
                errors.append(
                    _err(
                        "e2e_campaign_screenshot_path_not_temp",
                        f"{prefix}.path must be under temp/: {path}",
                    )
                )
        shown = shot.get("shown_to_user")
        if shown is False:
            errors.append(
                _err(
                    "e2e_campaign_evidence_not_shown",
                    f"{prefix}.shown_to_user must be true when screenshot captured",
                )
            )
        if screenshot_cap == "available":
            surface = shot.get("capture_surface")
            if surface in FORBIDDEN_CAPTURE_SURFACES or (
                surface is not None and surface not in LIVE_CAPTURE_SURFACES
            ):
                errors.append(
                    _err(
                        "e2e_campaign_screenshot_not_from_live_window",
                        f"{prefix}.capture_surface must be os_window|driver_viewport "
                        f"(not offscreen/headless); got {surface!r}",
                    )
                )
            elif surface is None:
                errors.append(
                    _err(
                        "e2e_campaign_screenshot_not_from_live_window",
                        f"{prefix}.capture_surface required "
                        "(os_window|driver_viewport) when screenshot_capability available",
                    )
                )
            if surface == "os_window":
                has_os_window = True
        screenshot_by_step[step_id] = shot

    if has_os_window and window_cap != "available":
        errors.append(
            _err(
                "e2e_campaign_window_required",
                "capture_surface=os_window requires window_capability=available",
            )
        )

    checkpoints = _as_str_list(data.get("checkpoints")) or []
    residuals = data.get("residuals") or []
    if not isinstance(residuals, list):
        residuals = []
    residual_codes = _residual_codes(residuals)

    if screenshot_cap == "available":
        for step_id in checkpoints:
            shot = screenshot_by_step.get(step_id)
            if shot is None or not _nonempty_str(shot.get("path")):
                errors.append(
                    _err(
                        "e2e_campaign_screenshot_checkpoint_missing",
                        f"checkpoint {step_id} missing screenshot path when capability available",
                    )
                )
            elif shot.get("shown_to_user") is not True:
                errors.append(
                    _err(
                        "e2e_campaign_evidence_not_shown",
                        f"checkpoint {step_id} must have shown_to_user true",
                    )
                )
    elif (
        screenshot_cap == "unavailable"
        and checkpoints
        and not residual_codes & SCREENSHOT_UNAVAILABLE_RESIDUAL_CODES
        and not screenshots
    ):
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "screenshot_capability unavailable with checkpoints requires "
                "screenshot_unavailable residual",
            )
        )

    errors.extend(_lint_prototype_task_reviews(data.get("prototype_task_reviews")))
    # Legacy list alias — still shape-check when present, but inventory object
    # is the hard Phase B gate.
    errors.extend(_lint_prototype_diff_review(data.get("prototype_diff_review")))

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "e2e_campaign_evidence_pack_lint_failed",
        "errors": errors,
    }


VALID_PROTO_TRI = frozenset({True, False, "true", "false", "unknown"})
VALID_PROTO_DECISION = frozenset({"matched", "keep_implementation", "revise_to_prototype"})
VALID_AI_LOOP_STATUS = frozenset({"in_progress", "complete", "not_applicable"})
PROTO_COMPARE_HEADING = "原型对照"
PROJECT_CLOSE_MARKERS = ("项目收尾",)


def _as_bool(value: Any) -> bool | None:
    if value is True or value == "true":
        return True
    if value is False or value == "false":
        return False
    return None


def _lint_prototype_task_reviews(
    block: Any,
    *,
    require_ai_loop_complete: bool = False,
) -> list[dict[str, str]]:
    """Validate Phase B prototype_task_reviews (full task inventory + AI loop)."""
    errors: list[dict[str, str]] = []
    if block is None:
        return [
            _err(
                "e2e_prototype_task_inventory_unloaded",
                "prototype_task_reviews required with inventory_loaded: true",
            )
        ]
    if not isinstance(block, dict):
        return [
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "prototype_task_reviews must be an object",
            )
        ]
    if block.get("inventory_loaded") is not True:
        errors.append(
            _err(
                "e2e_prototype_task_inventory_unloaded",
                "prototype_task_reviews.inventory_loaded must be true",
            )
        )
    required = block.get("required_task_ids")
    if required is None:
        errors.append(
            _err(
                "e2e_prototype_task_inventory_unloaded",
                "prototype_task_reviews.required_task_ids required (may be [])",
            )
        )
        required = []
    elif not isinstance(required, list):
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "required_task_ids must be a list",
            )
        )
        required = []
    else:
        for index, tid in enumerate(required):
            if not _nonempty_str(tid):
                errors.append(
                    _err(
                        "e2e_campaign_evidence_pack_invalid",
                        f"required_task_ids[{index}] must be non-empty string",
                    )
                )

    user_final = block.get("user_final_acceptance") is True
    ai_loop_status = block.get("ai_loop_status")
    if ai_loop_status is None:
        # Infer for older packs: empty inventory → not_applicable; else require explicit.
        if isinstance(required, list) and len(required) == 0:
            ai_loop_status = "not_applicable"
        else:
            errors.append(
                _err(
                    "e2e_prototype_ai_loop_incomplete",
                    "prototype_task_reviews.ai_loop_status required "
                    "(in_progress|complete|not_applicable)",
                )
            )
            ai_loop_status = "in_progress"
    elif ai_loop_status not in VALID_AI_LOOP_STATUS:
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "ai_loop_status must be in_progress|complete|not_applicable",
            )
        )

    if (
        isinstance(required, list)
        and len(required) == 0
        and ai_loop_status not in {None, "not_applicable"}
    ):
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "empty required_task_ids must use ai_loop_status: not_applicable",
            )
        )

    if user_final and ai_loop_status not in {"complete", "not_applicable"}:
        errors.append(
            _err(
                "e2e_prototype_user_final_before_ai",
                "user_final_acceptance requires ai_loop_status complete|not_applicable",
            )
        )

    reviews = block.get("reviews")
    if reviews is None:
        reviews = []
    if not isinstance(reviews, list):
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "prototype_task_reviews.reviews must be a list",
            )
        )
        return errors

    covered: set[str] = set()
    any_ai_fail = False
    for index, row in enumerate(reviews):
        prefix = f"prototype_task_reviews.reviews[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "e2e_campaign_evidence_pack_invalid",
                    f"{prefix} must be object",
                )
            )
            continue
        task_id = row.get("task_id")
        if _nonempty_str(task_id):
            covered.add(str(task_id))
        else:
            errors.append(
                _err(
                    "e2e_prototype_task_review_missing",
                    f"{prefix}.task_id required",
                )
            )
        row_errors, ai_pass, decision = _lint_prototype_review_row(
            row,
            prefix,
            require_phase_b=True,
            user_final_acceptance=user_final,
            ai_loop_status=str(ai_loop_status) if ai_loop_status else "in_progress",
        )
        errors.extend(row_errors)
        if ai_pass is False and not (user_final and decision == "keep_implementation"):
            any_ai_fail = True

    for tid in required:
        if _nonempty_str(tid) and str(tid) not in covered:
            errors.append(
                _err(
                    "e2e_prototype_task_review_missing",
                    f"required task_id missing from reviews: {tid}",
                )
            )

    if isinstance(required, list) and len(required) > 0:
        if any_ai_fail and ai_loop_status == "complete":
            errors.append(
                _err(
                    "e2e_prototype_ai_loop_incomplete",
                    "ai_loop_status=complete but at least one review has ai_pass=false",
                )
            )
        if not any_ai_fail and ai_loop_status == "in_progress":
            errors.append(
                _err(
                    "e2e_prototype_ai_loop_incomplete",
                    "all reviews ai_pass=true requires ai_loop_status=complete",
                )
            )
        if require_ai_loop_complete and ai_loop_status != "complete":
            errors.append(
                _err(
                    "e2e_prototype_ai_loop_incomplete",
                    "campaign green/close requires ai_loop_status=complete",
                )
            )
    elif require_ai_loop_complete and ai_loop_status not in {
        "complete",
        "not_applicable",
    }:
        errors.append(
            _err(
                "e2e_prototype_ai_loop_incomplete",
                "campaign green/close requires ai_loop_status complete|not_applicable",
            )
        )

    return errors


def _lint_prototype_review_row(
    row: dict[str, Any],
    prefix: str,
    *,
    require_phase_b: bool,
    user_final_acceptance: bool = False,
    ai_loop_status: str = "in_progress",
) -> tuple[list[dict[str, str]], bool | None, str | None]:
    errors: list[dict[str, str]] = []
    ai_pass_value: bool | None = None
    decision: str | None = None
    page_id = row.get("page_id")
    if not _nonempty_str(page_id):
        errors.append(
            _err(
                "e2e_prototype_diff_screenshot_missing",
                f"{prefix}.page_id required",
            )
        )
    path = row.get("screenshot_path")
    if not _nonempty_str(path):
        errors.append(
            _err(
                "e2e_prototype_diff_screenshot_missing",
                f"{prefix}.screenshot_path required",
            )
        )
    elif isinstance(path, str) and not _path_under_temp(path):
        errors.append(
            _err(
                "e2e_campaign_screenshot_path_not_temp",
                f"{prefix}.screenshot_path must be under temp/: {path}",
            )
        )
    link = row.get("prototype_link")
    if not _nonempty_str(link):
        errors.append(
            _err(
                "e2e_prototype_diff_link_missing",
                f"{prefix}.prototype_link required",
            )
        )
    if row.get("shown_to_user") is not True:
        errors.append(
            _err(
                "e2e_prototype_diff_not_shown",
                f"{prefix}.shown_to_user must be true",
            )
        )

    if not require_phase_b:
        return errors, None, None

    questions = row.get("questions")
    if not isinstance(questions, dict):
        errors.append(
            _err(
                "e2e_prototype_three_questions_incomplete",
                f"{prefix}.questions object required",
            )
        )
    else:
        for key in ("ux_better", "visual_better", "tech_stack_blocked"):
            val = questions.get(key)
            if val not in VALID_PROTO_TRI:
                errors.append(
                    _err(
                        "e2e_prototype_three_questions_incomplete",
                        f"{prefix}.questions.{key} must be true|false|unknown",
                    )
                )

    decision = row.get("decision")
    if decision not in VALID_PROTO_DECISION:
        errors.append(
            _err(
                "e2e_campaign_evidence_pack_invalid",
                f"{prefix}.decision must be matched|keep_implementation|revise_to_prototype",
            )
        )
        decision = None

    if decision == "keep_implementation" and not user_final_acceptance:
        errors.append(
            _err(
                "e2e_prototype_ai_keep_forbidden",
                f"{prefix}.keep_implementation forbidden until user_final_acceptance",
            )
        )

    ai_pass_raw = row.get("ai_pass")
    if "ai_pass" not in row:
        errors.append(
            _err(
                "e2e_prototype_ai_pass_missing",
                f"{prefix}.ai_pass boolean required",
            )
        )
    else:
        ai_pass_value = _as_bool(ai_pass_raw)
        if ai_pass_value is None:
            errors.append(
                _err(
                    "e2e_prototype_ai_pass_missing",
                    f"{prefix}.ai_pass must be true|false",
                )
            )
        elif decision is not None:
            expected_pass = decision == "matched"
            if ai_pass_value != expected_pass:
                errors.append(
                    _err(
                        "e2e_prototype_ai_pass_inconsistent",
                        f"{prefix}.ai_pass must be true iff decision=matched "
                        f"(got ai_pass={ai_pass_raw}, decision={decision})",
                    )
                )

    rationale = row.get("decision_rationale")
    if not _nonempty_str(rationale):
        code = (
            "e2e_prototype_keep_rationale_missing"
            if decision == "keep_implementation"
            else "e2e_campaign_evidence_pack_invalid"
        )
        errors.append(
            _err(
                code,
                f"{prefix}.decision_rationale required "
                "(for keep: why retain a material diff; form-factor-only → matched)",
            )
        )

    if decision == "revise_to_prototype":
        recap = row.get("revised_and_recaptured")
        recap_true = recap is True or recap == "true"
        mid_loop_ok = ai_loop_status == "in_progress" and _remediation_ok(row)
        if not recap_true and not mid_loop_ok:
            errors.append(
                _err(
                    "e2e_prototype_revise_not_recaptured",
                    f"{prefix}.revised_and_recaptured must be true after revise "
                    "(or ai_loop in_progress with remediation.task_ids)",
                )
            )

    user_kept = user_final_acceptance and decision == "keep_implementation"
    if ai_pass_value is False and not user_kept and not _remediation_ok(row):
        errors.append(
            _err(
                "e2e_prototype_remediation_missing",
                f"{prefix}.remediation.task_ids must be non-empty when ai_pass=false",
            )
        )

    return errors, ai_pass_value, decision if isinstance(decision, str) else None


def _remediation_ok(row: dict[str, Any]) -> bool:
    rem = row.get("remediation")
    if not isinstance(rem, dict):
        return False
    task_ids = rem.get("task_ids")
    if not isinstance(task_ids, list) or not task_ids:
        return False
    return all(_nonempty_str(tid) for tid in task_ids)


def _lint_prototype_diff_review(rows: Any) -> list[dict[str, str]]:
    """Validate optional legacy Phase B prototype_diff_review rows."""
    errors: list[dict[str, str]] = []
    if rows is None:
        return errors
    if not isinstance(rows, list):
        return [
            _err(
                "e2e_campaign_evidence_pack_invalid",
                "prototype_diff_review must be a list when present",
            )
        ]
    for index, row in enumerate(rows):
        prefix = f"prototype_diff_review[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "e2e_campaign_evidence_pack_invalid",
                    f"{prefix} must be object",
                )
            )
            continue
        row_errors, _, _ = _lint_prototype_review_row(row, prefix, require_phase_b=False)
        errors.extend(row_errors)
    return errors


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
                    "e2e_campaign_closing_summary_missing",
                    "campaign complete requires closing summary",
                )
            )
        return {
            "ok": not errors,
            "code": "ok" if not errors else "e2e_campaign_closing_summary_lint_failed",
            "errors": errors,
        }

    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "e2e_campaign_closing_summary_lint_failed",
            "errors": [
                _err("e2e_campaign_closing_summary_incomplete", "closing summary must be object")
            ],
        }

    if data.get("schema") != CLOSING_SUMMARY_SCHEMA:
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
                f"schema must be {CLOSING_SUMMARY_SCHEMA}",
            )
        )
    if data.get("contract_loaded") is not True:
        errors.append(
            _err("e2e_campaign_closing_summary_incomplete", "contract_loaded must be true")
        )
    if data.get("plain_language_loaded") is not True:
        errors.append(
            _err(
                "e2e_campaign_closing_summary_not_plain",
                "plain_language_loaded must be true",
            )
        )
    if data.get("audience") != "beginner":
        errors.append(
            _err(
                "e2e_campaign_closing_summary_not_plain",
                "audience must be beginner",
            )
        )

    screenshot_cap = data.get("screenshot_capability")
    if screenshot_cap not in VALID_CAPABILITY:
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
                "screenshot_capability must be available|unavailable",
            )
        )

    window_cap = data.get("window_capability")
    if window_cap is not None and window_cap not in VALID_CAPABILITY:
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
                "window_capability must be available|unavailable",
            )
        )

    outcome = data.get("outcome")
    if outcome not in {"green", "green_with_residuals", "blocked_external"}:
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
                "outcome must be green|green_with_residuals|blocked_external",
            )
        )
    elif outcome in {"green", "green_with_residuals"}:
        # Whole-campaign fail-closed: residuals cannot waive missing live window.
        errors.extend(
            lint_window_required_for_close(
                screenshot_capability=screenshot_cap,
                window_capability=window_cap,
                require_window_field=True,
                outcome_or_phase=f"outcome={outcome}",
            )
        )

    errors.extend(
        lint_acceptance_outcomes(
            data,
            require_user_path_claim=True,
            campaign_outcome=outcome if isinstance(outcome, str) else None,
        )
    )

    rounds = data.get("rounds_completed")
    if not isinstance(rounds, int) or rounds < 1:
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
                "rounds_completed must be a positive integer",
            )
        )

    code_changed = data.get("code_changed")
    if not isinstance(code_changed, bool):
        errors.append(
            _err("e2e_campaign_closing_summary_incomplete", "code_changed must be boolean")
        )

    plain = data.get("plain")
    if not isinstance(plain, dict):
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
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
                    "e2e_campaign_closing_summary_incomplete",
                    f"plain.{field} required",
                )
            )
            continue
        assert isinstance(value, str)
        if locale.startswith("zh") and not _has_cjk(value):
            errors.append(
                _err(
                    "e2e_campaign_closing_summary_not_plain",
                    f"plain.{field} must use everyday Chinese for zh locale",
                )
            )
        if field == "headline" and _looks_jargon_only(value):
            errors.append(
                _err(
                    "e2e_campaign_closing_summary_not_plain",
                    "plain.headline must be everyday language",
                )
            )
        if field == "what_changed_for_you" and _looks_path_only(value):
            errors.append(
                _err(
                    "e2e_campaign_closing_summary_not_plain",
                    "plain.what_changed_for_you must describe user-visible impact",
                )
            )

    body = data.get("markdown_body")
    if not _nonempty_str(body):
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
                "markdown_body required for user-facing display",
            )
        )
    else:
        assert isinstance(body, str)
        for heading in REQUIRED_MARKDOWN_HEADINGS:
            if heading not in body:
                errors.append(
                    _err(
                        "e2e_campaign_closing_summary_incomplete",
                        f"markdown_body missing section heading: {heading}",
                    )
                )
        if screenshot_cap == "available" and SCREENSHOTS_HEADING not in body:
            errors.append(
                _err(
                    "e2e_campaign_closing_summary_screenshots_missing",
                    f"markdown_body missing section heading: {SCREENSHOTS_HEADING}",
                )
            )

    residuals = data.get("residuals") or []
    if not isinstance(residuals, list):
        residuals = []
        errors.append(_err("e2e_campaign_closing_summary_incomplete", "residuals must be a list"))
    leftovers = plain.get("leftovers") if isinstance(plain, dict) else None
    if residuals and isinstance(leftovers, str):
        leftover_l = leftovers.strip()
        if leftover_l in {"没有未完成事项。", "没有未完成事项", "无", "none", "n/a"}:
            errors.append(
                _err(
                    "e2e_campaign_closing_summary_residual_unexplained",
                    "residuals present but plain.leftovers claims nothing left",
                )
            )

    host_matrix = data.get("host_matrix")
    if host_matrix is not None:
        errors.extend(
            lint_host_availability_residuals(
                host_matrix,
                residuals,
                outcome=outcome if isinstance(outcome, str) else None,
            )
        )
        errors.extend(
            lint_external_device_handoffs(
                host_matrix,
                data.get("external_device_handoffs"),
                outcome=outcome if isinstance(outcome, str) else None,
            )
        )

    errors.extend(
        lint_manual_test_residuals(
            residuals,
            leftovers=leftovers if isinstance(leftovers, str) else None,
            outcome=outcome if isinstance(outcome, str) else None,
        )
    )

    evidence = data.get("evidence_pack")
    evidence_ref = data.get("evidence_pack_ref")
    if evidence is None and not _nonempty_str(evidence_ref):
        errors.append(
            _err(
                "e2e_campaign_closing_summary_incomplete",
                "evidence_pack or evidence_pack_ref required",
            )
        )
    elif evidence is not None:
        nested = lint_evidence_pack(evidence)
        if not nested["ok"]:
            errors.extend(nested["errors"])
        # Green outcomes require AI loop complete + gate next_step wording.
        if outcome in {"green", "green_with_residuals"} and isinstance(evidence, dict):
            proto = evidence.get("prototype_task_reviews")
            errors.extend(
                _lint_prototype_task_reviews(
                    proto,
                    require_ai_loop_complete=True,
                )
            )
            if isinstance(proto, dict):
                required = proto.get("required_task_ids") or []
                user_final = proto.get("user_final_acceptance") is True
                next_step = plain.get("next_step") if isinstance(plain, dict) else None
                if (
                    isinstance(required, list)
                    and required
                    and isinstance(body, str)
                    and PROTO_COMPARE_HEADING not in body
                ):
                    errors.append(
                        _err(
                            "e2e_campaign_closing_summary_screenshots_missing",
                            f"markdown_body missing section heading: {PROTO_COMPARE_HEADING}",
                        )
                    )
                if isinstance(next_step, str):
                    mentions_close = any(m in next_step for m in PROJECT_CLOSE_MARKERS)
                    if mentions_close and not user_final:
                        errors.append(
                            _err(
                                "e2e_campaign_closing_summary_ai_loop",
                                "plain.next_step must not suggest 「项目收尾」 "
                                "before user_final_acceptance",
                            )
                        )

    if code_changed is True:
        report = data.get("change_report")
        report_ref = data.get("change_report_ref")
        if report is None and not _nonempty_str(report_ref):
            errors.append(
                _err(
                    "e2e_campaign_change_report_missing",
                    "code_changed=true requires change_report or change_report_ref",
                )
            )
        elif report is not None:
            nested = lint_change_report(report, code_changed=True)
            if not nested["ok"]:
                errors.extend(nested["errors"])

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "e2e_campaign_closing_summary_lint_failed",
        "errors": errors,
    }


def detect_kind(data: Any) -> str | None:
    if not isinstance(data, dict):
        return None
    schema = data.get("schema")
    if schema == CLOSING_SUMMARY_SCHEMA or (
        "markdown_body" in data
        and "plain" in data
        and "screenshots_note" in (data.get("plain") or {})
    ):
        return "closing_summary"
    if schema == EVIDENCE_PACK_SCHEMA or (
        "screenshots" in data and schema != CLOSING_SUMMARY_SCHEMA
    ):
        return "evidence_pack"
    if schema == HOST_MATRIX_SCHEMA or (
        "hosts" in data and "assignment_policy" in data and "cases" not in data
    ):
        return "host_matrix"
    if schema == COVERAGE_MATRIX_SCHEMA or "required_journeys" in data:
        return "coverage_matrix"
    if schema == SUITE_PLAN_SCHEMA or ("cases" in data and "order" in data):
        return "suite_plan"
    if schema == CHANGE_REPORT_SCHEMA or "product_behavior_delta" in data:
        return "change_report"
    if schema == CAMPAIGN_STATE_SCHEMA or ("campaign_drive" in data and "integration_gate" in data):
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
    if resolved == "coverage_matrix":
        return lint_coverage_matrix(data, project_work=project_work)
    if resolved == "host_matrix":
        platforms = platforms_from_project_work(project_work) if project_work is not None else []
        return lint_host_matrix(data, platforms=platforms or None)
    if resolved == "change_report":
        return lint_change_report(data)
    if resolved == "campaign_state":
        return lint_campaign_state(data)
    if resolved == "evidence_pack":
        return lint_evidence_pack(data)
    if resolved == "closing_summary":
        return lint_closing_summary(data)
    return {
        "ok": False,
        "code": "e2e_campaign_artifact_kind_unknown",
        "errors": [
            _err(
                "e2e_campaign_artifact_kind_unknown",
                "could not detect suite_plan|coverage_matrix|host_matrix|change_report|"
                "campaign_state|evidence_pack|closing_summary",
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
            "code": "e2e_campaign_artifact_missing",
            "errors": [_err("missing_file", str(path))],
        }
    data = _load_yamlish(path)
    result = lint_document(data, kind=kind, project_work=project_work)
    result["path"] = str(path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="Path to campaign artifact")
    parser.add_argument(
        "--kind",
        choices=(
            "suite_plan",
            "coverage_matrix",
            "host_matrix",
            "change_report",
            "campaign_state",
            "evidence_pack",
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
        help="Optional Project Work YAML/JSON for journey coverage cross-check",
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
                "code": "e2e_campaign_artifact_missing",
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
                "code": "e2e_campaign_artifact_missing",
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
        elif resolved == "coverage_matrix":
            result = lint_coverage_matrix(data, project_work=project_work)
            result["path"] = str(args.artifact)
        elif resolved == "host_matrix":
            platforms = (
                platforms_from_project_work(project_work) if project_work is not None else []
            )
            result = lint_host_matrix(data, platforms=platforms or None)
            result["path"] = str(args.artifact)
        elif resolved == "evidence_pack":
            result = lint_evidence_pack(data)
            result["path"] = str(args.artifact)
        elif resolved == "campaign_state":
            result = lint_campaign_state(data)
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
