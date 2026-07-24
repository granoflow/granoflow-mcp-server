#!/usr/bin/env python3
"""Validate project Widget Catalog promotion and App readback evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_DISPOSITIONS = frozenset({"reused", "promoted", "task_local"})


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("root must be an object")
    return value


def _extract(data: dict[str, Any], key: str) -> dict[str, Any] | None:
    if key in data:
        value = data[key]
        return value if isinstance(value, dict) else None
    return data


def validate_widget_promotion(
    data: dict[str, Any],
    bundle_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ledger = _extract(data, "widget_promotion")
    bundle = (
        _extract(bundle_data, "responsive_prototype_bundle") if bundle_data is not None else None
    )
    errors: list[dict[str, str]] = []
    if ledger is None:
        return {
            "ok": False,
            "code": "widget_promotion_required",
            "errors": [{"code": "widget_promotion_required", "detail": "ledger missing"}],
        }
    if ledger.get("schema") != "granoflow_widget_promotion_v1":
        errors.append({"code": "widget_promotion_required", "detail": "widget schema invalid"})
    status = ledger.get("status")
    if status not in {"passed", "not_applicable"}:
        errors.append(
            {
                "code": "widget_promotion_required",
                "detail": "status must be passed|not_applicable",
            }
        )
    if status == "not_applicable":
        if not isinstance(ledger.get("rationale"), str) or not ledger["rationale"].strip():
            errors.append(
                {
                    "code": "widget_promotion_required",
                    "detail": "not_applicable requires rationale",
                }
            )
        return {
            "ok": not errors,
            "code": "ok" if not errors else errors[0]["code"],
            "errors": errors,
        }

    for field in (
        "source_prototype_bundle_sha256",
        "catalog_before_sha256",
        "catalog_after_sha256",
        "app_readback_sha256",
    ):
        value = ledger.get(field)
        if not isinstance(value, str) or not HASH_RE.fullmatch(value):
            errors.append(
                {
                    "code": "widget_promotion_required",
                    "detail": f"{field} must be a lowercase SHA-256",
                }
            )
    if bundle is not None and ledger.get("source_prototype_bundle_sha256") != bundle.get(
        "bundle_sha256"
    ):
        errors.append(
            {
                "code": "widget_promotion_required",
                "detail": "source Prototype Bundle digest is stale",
            }
        )
    if bundle is not None and ledger.get("catalog_before_sha256") != bundle.get(
        "widget_catalog_input_sha256"
    ):
        errors.append(
            {
                "code": "widget_catalog_stale",
                "detail": "catalog_before_sha256 differs from bundle input",
            }
        )
    if ledger.get("catalog_after_sha256") != ledger.get("app_readback_sha256"):
        errors.append(
            {
                "code": "widget_promotion_readback_mismatch",
                "detail": "catalog write and App readback SHA differ",
            }
        )

    decisions = ledger.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        errors.append(
            {
                "code": "widget_promotion_required",
                "detail": "passed promotion requires decisions",
            }
        )
        decisions = []
    roles: dict[str, str] = {}
    promoted = False
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            continue
        widget_id = decision.get("widget_id")
        role = decision.get("role")
        disposition = decision.get("disposition")
        if not isinstance(widget_id, str) or not widget_id:
            errors.append(
                {
                    "code": "widget_promotion_required",
                    "detail": f"decisions[{index}].widget_id required",
                }
            )
        if not isinstance(role, str) or not role:
            errors.append(
                {
                    "code": "widget_promotion_required",
                    "detail": f"decisions[{index}].role required",
                }
            )
            continue
        if disposition not in VALID_DISPOSITIONS:
            errors.append(
                {
                    "code": "widget_promotion_required",
                    "detail": f"decisions[{index}].disposition invalid",
                }
            )
        if role in roles and roles[role] != widget_id:
            errors.append(
                {
                    "code": "widget_promotion_required",
                    "detail": f"role {role!r} maps to multiple widget ids",
                }
            )
        elif isinstance(widget_id, str):
            roles[role] = widget_id
        if disposition == "task_local" and (
            not isinstance(decision.get("rationale"), str) or not decision["rationale"].strip()
        ):
            errors.append(
                {
                    "code": "widget_promotion_required",
                    "detail": f"decisions[{index}] task_local requires rationale",
                }
            )
        if disposition == "promoted":
            promoted = True
        if (
            decision.get("changes_locked_contract") is True
            and ledger.get("baseline_reopened") is not True
        ):
            errors.append(
                {
                    "code": "widget_locked_contract_baseline_reopen_required",
                    "detail": f"decisions[{index}] changes a locked contract",
                }
            )

    if promoted and ledger.get("catalog_before_sha256") == ledger.get("catalog_after_sha256"):
        errors.append(
            {
                "code": "widget_promotion_readback_mismatch",
                "detail": "promoted widgets require a changed catalog SHA",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--prototype-bundle", type=Path)
    args = parser.parse_args(argv)
    try:
        data = _load(args.ledger)
        bundle = _load(args.prototype_bundle) if args.prototype_bundle else None
        result = validate_widget_promotion(data, bundle)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "widget_promotion_required",
            "errors": [{"code": "widget_promotion_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
