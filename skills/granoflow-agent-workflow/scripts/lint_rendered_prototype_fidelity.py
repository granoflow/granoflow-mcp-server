#!/usr/bin/env python3
"""Validate rendered prototype fidelity for every required layout family."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-f]{64}$")


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


def validate_rendered_fidelity(
    data: dict[str, Any],
    bundle_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ledger = _extract(data, "rendered_prototype_fidelity")
    bundle = (
        _extract(bundle_data, "responsive_prototype_bundle") if bundle_data is not None else None
    )
    errors: list[dict[str, str]] = []
    if ledger is None:
        return {
            "ok": False,
            "code": "rendered_fidelity_required",
            "errors": [{"code": "rendered_fidelity_required", "detail": "ledger missing"}],
        }
    if ledger.get("schema") != "granoflow_rendered_prototype_fidelity_v1":
        errors.append({"code": "rendered_fidelity_required", "detail": "fidelity schema invalid"})
    if ledger.get("status") != "passed":
        errors.append({"code": "rendered_fidelity_required", "detail": "status must be passed"})
    if ledger.get("authorization_effect") != "none":
        errors.append(
            {
                "code": "rendered_fidelity_required",
                "detail": "authorization_effect must be none",
            }
        )
    if bundle is not None and ledger.get("prototype_bundle_sha256") != bundle.get("bundle_sha256"):
        errors.append(
            {
                "code": "rendered_fidelity_required",
                "detail": "Prototype Bundle digest is stale",
            }
        )

    bundle_variants = bundle.get("variants", []) if bundle is not None else []
    required = {row.get("layout_family_id") for row in bundle_variants if isinstance(row, dict)}
    rows = ledger.get("rows")
    if not isinstance(rows, list):
        rows = []
    observed: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        layout_id = row.get("layout_family_id")
        if isinstance(layout_id, str) and layout_id:
            observed.add(layout_id)
        for field in (
            "prototype_screenshot_ref",
            "implementation_screenshot_ref",
        ):
            if not isinstance(row.get(field), str) or not row[field]:
                errors.append(
                    {
                        "code": "rendered_fidelity_layout_missing",
                        "detail": f"rows[{index}].{field} required",
                    }
                )
        for field in (
            "prototype_screenshot_sha256",
            "implementation_screenshot_sha256",
        ):
            if not isinstance(row.get(field), str) or not HASH_RE.fullmatch(row[field]):
                errors.append(
                    {
                        "code": "rendered_fidelity_layout_missing",
                        "detail": f"rows[{index}].{field} invalid",
                    }
                )
        metric = row.get("numeric_metric")
        if (
            not isinstance(metric, dict)
            or not isinstance(metric.get("name"), str)
            or not isinstance(metric.get("value"), int | float)
            or not isinstance(metric.get("threshold"), int | float)
            or metric["value"] > metric["threshold"]
            or metric.get("passed") is not True
        ):
            errors.append(
                {
                    "code": "rendered_fidelity_numeric_failed",
                    "detail": f"rows[{index}] numeric metric failed",
                }
            )
        if row.get("ai_visual_status") != "passed":
            errors.append(
                {
                    "code": "rendered_fidelity_ai_failed",
                    "detail": f"rows[{index}] AI visual review did not pass",
                }
            )
        region_diffs = row.get("region_diffs")
        if not isinstance(region_diffs, list):
            region_diffs = []
        for diff_index, diff in enumerate(region_diffs):
            if not isinstance(diff, dict):
                continue
            disposition = diff.get("disposition")
            if disposition not in {"matched", "approved_native_exception"}:
                errors.append(
                    {
                        "code": "rendered_fidelity_ai_failed",
                        "detail": f"rows[{index}].region_diffs[{diff_index}] unresolved",
                    }
                )
            if disposition == "approved_native_exception" and (
                diff.get("approved") is not True
                or not isinstance(diff.get("platform_contract_ref"), str)
                or not diff["platform_contract_ref"]
            ):
                errors.append(
                    {
                        "code": "rendered_fidelity_exception_unapproved",
                        "detail": f"rows[{index}].region_diffs[{diff_index}] unapproved",
                    }
                )
        if row.get("recapture_complete") is not True:
            errors.append(
                {
                    "code": "rendered_fidelity_required",
                    "detail": f"rows[{index}] recapture is incomplete",
                }
            )

    missing = sorted(item for item in required - observed if isinstance(item, str))
    if missing:
        errors.append(
            {
                "code": "rendered_fidelity_layout_missing",
                "detail": f"required fidelity rows missing: {missing}",
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
        result = validate_rendered_fidelity(data, bundle)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "rendered_fidelity_required",
            "errors": [{"code": "rendered_fidelity_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
