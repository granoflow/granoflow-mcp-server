#!/usr/bin/env python3
"""Validate the Project platform support matrix and its canonical digest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_PLATFORM_IDS = frozenset({"ios", "android", "macos", "windows"})
VALID_SUPPORT = frozenset({"supported", "not_supported", "deferred"})
VALID_ACCEPTANCE = {
    ("user_confirmed", "user"),
    ("unattended_auto_adopted", "unattended_grant"),
}


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml

        value = yaml.safe_load(text)
    except ImportError:
        value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("root must be an object")
    return value


def _extract(data: dict[str, Any]) -> dict[str, Any] | None:
    if "platform_support_matrix" in data:
        value = data["platform_support_matrix"]
        return value if isinstance(value, dict) else None
    return data


def canonical_matrix_sha256(matrix: dict[str, Any]) -> str:
    payload = {key: value for key, value in matrix.items() if key != "matrix_sha256"}
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def validate_platform_support_matrix(data: dict[str, Any]) -> dict[str, Any]:
    matrix = _extract(data)
    errors: list[dict[str, str]] = []
    if matrix is None:
        return {
            "ok": False,
            "code": "platform_support_matrix_required",
            "errors": [{"code": "platform_support_matrix_required", "detail": "matrix missing"}],
        }
    if matrix.get("schema") != "granoflow_platform_support_v1":
        errors.append(
            {
                "code": "platform_support_matrix_incomplete",
                "detail": "schema must be granoflow_platform_support_v1",
            }
        )

    layouts = matrix.get("layout_families")
    layout_ids: set[str] = set()
    if not isinstance(layouts, list) or not layouts:
        errors.append(
            {
                "code": "platform_support_matrix_incomplete",
                "detail": "layout_families must be non-empty",
            }
        )
        layouts = []
    for index, layout in enumerate(layouts):
        if not isinstance(layout, dict):
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": f"layout_families[{index}] must be an object",
                }
            )
            continue
        layout_id = layout.get("id")
        viewport = layout.get("reference_viewport")
        if not _nonempty(layout_id):
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": f"layout_families[{index}].id required",
                }
            )
        else:
            assert isinstance(layout_id, str)
            layout_ids.add(layout_id)
        if layout.get("orientation") not in {"portrait", "landscape", "adaptive"}:
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": f"layout_families[{index}].orientation invalid",
                }
            )
        if not isinstance(viewport, dict) or any(
            not isinstance(viewport.get(key), int | float) or viewport[key] <= 0
            for key in ("width", "height", "dpr")
        ):
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": f"layout_families[{index}].reference_viewport invalid",
                }
            )

    if matrix.get("primary_layout_family") not in layout_ids:
        errors.append(
            {
                "code": "platform_support_matrix_incomplete",
                "detail": "primary_layout_family must reference a layout family",
            }
        )

    platforms = matrix.get("platforms")
    platform_rows: dict[str, dict[str, Any]] = {}
    if not isinstance(platforms, list):
        platforms = []
    for index, row in enumerate(platforms):
        if not isinstance(row, dict) or not _nonempty(row.get("id")):
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": f"platforms[{index}] id required",
                }
            )
            continue
        platform_rows[row["id"]] = row

    missing = sorted(REQUIRED_PLATFORM_IDS - set(platform_rows))
    if missing:
        errors.append(
            {
                "code": "platform_support_matrix_incomplete",
                "detail": f"required platform rows missing: {missing}",
            }
        )

    for platform_id, row in platform_rows.items():
        support = row.get("support_status")
        if support not in VALID_SUPPORT:
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": f"{platform_id}.support_status invalid",
                }
            )
            continue
        if support != "supported":
            if not _nonempty(row.get("rationale")):
                errors.append(
                    {
                        "code": "platform_support_matrix_incomplete",
                        "detail": f"{platform_id}.rationale required for {support}",
                    }
                )
            continue
        for field in (
            "min_os_version",
            "device_classes",
            "architectures",
            "layout_family_ids",
            "orientations",
            "source_refs",
            "required_test_versions",
        ):
            value = row.get(field)
            valid = _nonempty(value) if field == "min_os_version" else _nonempty_list(value)
            if not valid:
                errors.append(
                    {
                        "code": "platform_support_matrix_incomplete",
                        "detail": f"{platform_id}.{field} required",
                    }
                )
        target_sdk = row.get("target_sdk_version")
        if not _nonempty(target_sdk) and not _nonempty(row.get("target_sdk_not_applicable_reason")):
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": f"{platform_id}.target SDK or not-applicable reason required",
                }
            )
        if platform_id == "android" and (
            not isinstance(row.get("min_api_level"), int) or row["min_api_level"] < 1
        ):
            errors.append(
                {
                    "code": "platform_support_matrix_incomplete",
                    "detail": "android.min_api_level required",
                }
            )
        for layout_id in row.get("layout_family_ids", []):
            if layout_id not in layout_ids:
                errors.append(
                    {
                        "code": "platform_support_matrix_incomplete",
                        "detail": f"{platform_id} references unknown layout {layout_id!r}",
                    }
                )
        if platform_id in {"macos", "windows"}:
            window = row.get("window_constraints")
            if not isinstance(window, dict) or any(
                key not in window
                for key in ("minimum_size", "default_size", "resizable", "fullscreen")
            ):
                errors.append(
                    {
                        "code": "platform_support_matrix_incomplete",
                        "detail": f"{platform_id}.window_constraints incomplete",
                    }
                )

    acceptance = (matrix.get("confirmation_status"), matrix.get("accepted_by"))
    if acceptance not in VALID_ACCEPTANCE:
        errors.append(
            {
                "code": "platform_support_matrix_incomplete",
                "detail": "confirmation status and accepted_by are inconsistent",
            }
        )

    actual_digest = canonical_matrix_sha256(matrix)
    if matrix.get("matrix_sha256") != actual_digest:
        errors.append(
            {
                "code": "platform_support_matrix_digest_mismatch",
                "detail": "recorded matrix digest does not match current content",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "matrix_sha256": actual_digest,
        "required_layout_family_ids": sorted(
            {
                layout_id
                for row in platform_rows.values()
                if row.get("support_status") == "supported"
                for layout_id in row.get("layout_family_ids", [])
            }
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_platform_support_matrix(_load(args.path))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "platform_support_matrix_required",
            "errors": [{"code": "platform_support_matrix_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
