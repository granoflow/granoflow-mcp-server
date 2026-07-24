#!/usr/bin/env python3
"""Validate the user-confirmed screen content and behavior contract."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
BASELINE_STATES = {
    "default",
    "loading",
    "empty",
    "error",
    "offline",
    "permission_denied",
}
ACCEPTANCE = {
    ("user_confirmed", "user"),
    ("unattended_auto_adopted", "unattended_grant"),
}


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        try:
            loader = importlib.import_module("yaml").safe_load
            value = loader(text)
        except ImportError:
            value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("root must be an object")
    return value


def _extract(data: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = data.get(key, data)
    return value if isinstance(value, dict) else None


def canonical_content_contract_sha256(contract: dict[str, Any]) -> str:
    excluded = {
        "content_contract_sha256",
        "confirmation_status",
        "accepted_by",
        "authorization_effect",
    }
    payload = {key: value for key, value in contract.items() if key not in excluded}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def validate_screen_content_contract(
    data: dict[str, Any],
    logic_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = _extract(data, "screen_content_contract")
    logic = _extract(logic_data, "analysis_logic_draft") if logic_data is not None else None
    errors: list[dict[str, str]] = []
    if contract is None:
        return {
            "ok": False,
            "code": "screen_content_contract_required",
            "errors": [
                {
                    "code": "screen_content_contract_required",
                    "detail": "content contract missing",
                }
            ],
        }
    if contract.get("schema") != "granoflow_screen_content_contract_v1":
        errors.append(
            {
                "code": "screen_content_contract_incomplete",
                "detail": "content contract schema invalid",
            }
        )
    for field in ("task_id", "page_definition_brief_ref"):
        if not _nonempty(contract.get(field)):
            errors.append(
                {
                    "code": "screen_content_contract_incomplete",
                    "detail": f"{field} required",
                }
            )
    for field in ("logic_draft_sha256", "page_definition_brief_sha256"):
        if not isinstance(contract.get(field), str) or not HASH_RE.fullmatch(contract[field]):
            errors.append(
                {
                    "code": "screen_content_contract_incomplete",
                    "detail": f"{field} must be a lowercase SHA-256",
                }
            )
    if logic is not None and contract.get("logic_draft_sha256") != logic.get("draft_sha256"):
        errors.append(
            {
                "code": "screen_content_contract_digest_mismatch",
                "detail": "Logic Draft digest is stale",
            }
        )
    for field in ("requirement_refs", "acceptance_refs"):
        if not _nonempty_list(contract.get(field)):
            errors.append(
                {
                    "code": "screen_content_contract_incomplete",
                    "detail": f"{field} must be non-empty",
                }
            )
    screens = contract.get("screens")
    if not isinstance(screens, list) or not screens:
        screens = []
        errors.append(
            {
                "code": "screen_content_contract_incomplete",
                "detail": "screens must be non-empty",
            }
        )
    screen_ids: set[str] = set()
    for index, screen in enumerate(screens):
        if not isinstance(screen, dict):
            continue
        screen_id = screen.get("screen_id")
        if not _nonempty(screen_id) or screen_id in screen_ids:
            errors.append(
                {
                    "code": "screen_content_contract_incomplete",
                    "detail": f"screens[{index}].screen_id missing or duplicate",
                }
            )
        else:
            assert isinstance(screen_id, str)
            screen_ids.add(screen_id)
        for field in ("purpose", "back_behavior"):
            if not _nonempty(screen.get(field)):
                errors.append(
                    {
                        "code": "screen_content_contract_incomplete",
                        "detail": f"screens[{index}].{field} required",
                    }
                )
        for field in (
            "user_roles",
            "entry_conditions",
            "entry_routes",
            "exit_routes",
            "permissions",
            "platform_exceptions",
        ):
            if not isinstance(screen.get(field), list):
                errors.append(
                    {
                        "code": "screen_content_contract_incomplete",
                        "detail": f"screens[{index}].{field} must be a list",
                    }
                )
        for field in ("user_roles", "entry_routes", "permissions"):
            if not _nonempty_list(screen.get(field)):
                errors.append(
                    {
                        "code": "screen_content_contract_incomplete",
                        "detail": f"screens[{index}].{field} required",
                    }
                )
        sections = screen.get("content_sections")
        if not isinstance(sections, list) or not sections:
            errors.append(
                {
                    "code": "screen_content_contract_incomplete",
                    "detail": f"screens[{index}].content_sections required",
                }
            )
            sections = []
        for section_index, section in enumerate(sections):
            if not isinstance(section, dict):
                continue
            fields = section.get("data_fields")
            if (
                not _nonempty(section.get("section_id"))
                or not _nonempty(section.get("role"))
                or not isinstance(section.get("display_order"), int)
                or not isinstance(fields, list)
                or not fields
            ):
                errors.append(
                    {
                        "code": "screen_content_contract_incomplete",
                        "detail": (
                            f"screens[{index}].content_sections[{section_index}] " "is incomplete"
                        ),
                    }
                )
                continue
            for field_index, field in enumerate(fields):
                if not isinstance(field, dict) or any(
                    not _nonempty(field.get(key))
                    for key in ("field_id", "label", "source_ref", "format")
                ):
                    errors.append(
                        {
                            "code": "screen_content_contract_incomplete",
                            "detail": (
                                f"screens[{index}].content_sections[{section_index}]"
                                f".data_fields[{field_index}] incomplete"
                            ),
                        }
                    )
                    continue
                if not isinstance(field.get("required"), bool) or not isinstance(
                    field.get("visibility_rules"), list
                ):
                    errors.append(
                        {
                            "code": "screen_content_contract_incomplete",
                            "detail": f"field {field.get('field_id')!r} rules invalid",
                        }
                    )
        interaction_mode = screen.get("interaction_mode")
        actions = screen.get("actions")
        if interaction_mode not in {"read_only", "interactive"} or not isinstance(actions, list):
            errors.append(
                {
                    "code": "screen_content_contract_incomplete",
                    "detail": f"screens[{index}] interaction mode/actions invalid",
                }
            )
            actions = []
        if interaction_mode == "interactive" and not actions:
            errors.append(
                {
                    "code": "screen_content_contract_incomplete",
                    "detail": f"screens[{index}] interactive screen needs actions",
                }
            )
        for action_index, action in enumerate(actions):
            if (
                not isinstance(action, dict)
                or any(
                    not _nonempty(action.get(key))
                    for key in ("action_id", "label", "result", "failure_behavior")
                )
                or not isinstance(action.get("preconditions"), list)
            ):
                errors.append(
                    {
                        "code": "screen_content_contract_incomplete",
                        "detail": f"screens[{index}].actions[{action_index}] incomplete",
                    }
                )
        states = screen.get("states")
        state_rows = states if isinstance(states, list) else []
        state_ids = {
            row.get("id")
            for row in state_rows
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        missing_states = sorted(BASELINE_STATES - state_ids)
        if missing_states:
            errors.append(
                {
                    "code": "screen_content_contract_state_missing",
                    "detail": f"screens[{index}] states missing: {missing_states}",
                }
            )
        for state_index, state in enumerate(state_rows):
            if not isinstance(state, dict):
                continue
            disposition = state.get("disposition")
            if disposition not in {"covered", "not_applicable"}:
                errors.append(
                    {
                        "code": "screen_content_contract_state_missing",
                        "detail": f"screens[{index}].states[{state_index}] invalid",
                    }
                )
            if disposition == "covered" and not _nonempty(state.get("behavior")):
                errors.append(
                    {
                        "code": "screen_content_contract_state_missing",
                        "detail": f"state {state.get('id')!r} behavior required",
                    }
                )
            if disposition == "not_applicable" and not _nonempty(state.get("rationale")):
                errors.append(
                    {
                        "code": "screen_content_contract_state_missing",
                        "detail": f"state {state.get('id')!r} rationale required",
                    }
                )
        if "default" in state_ids:
            default = next(
                (row for row in state_rows if isinstance(row, dict) and row.get("id") == "default"),
                {},
            )
            if default.get("disposition") != "covered":
                errors.append(
                    {
                        "code": "screen_content_contract_state_missing",
                        "detail": "default state must be covered",
                    }
                )

    checks = contract.get("cross_screen_checks")
    if not isinstance(checks, dict) or any(
        checks.get(key) is not True for key in ("data", "states", "navigation", "permissions")
    ):
        errors.append(
            {
                "code": "screen_content_contract_incomplete",
                "detail": "all cross-screen checks must pass",
            }
        )
    if not isinstance(contract.get("out_of_scope"), list):
        errors.append(
            {
                "code": "screen_content_contract_incomplete",
                "detail": "out_of_scope must be a list",
            }
        )
    accepted = (contract.get("confirmation_status"), contract.get("accepted_by"))
    if accepted not in ACCEPTANCE or contract.get("authorization_effect") != "none":
        errors.append(
            {
                "code": "screen_content_contract_acceptance_required",
                "detail": "content acceptance is missing or inconsistent",
            }
        )
    actual_digest = canonical_content_contract_sha256(contract)
    if contract.get("content_contract_sha256") != actual_digest:
        errors.append(
            {
                "code": "screen_content_contract_digest_mismatch",
                "detail": "content contract digest is stale",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "content_contract_sha256": actual_digest,
        "screen_ids": sorted(screen_ids),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--logic-draft", type=Path)
    args = parser.parse_args(argv)
    try:
        data = _load(args.contract)
        logic = _load(args.logic_draft) if args.logic_draft else None
        result = validate_screen_content_contract(data, logic)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "screen_content_contract_required",
            "errors": [{"code": "screen_content_contract_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
