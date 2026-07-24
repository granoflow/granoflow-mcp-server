#!/usr/bin/env python3
"""Validate responsive Prototype Bundle coverage, acceptance, and digest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
THREE_REASONS = frozenset(
    {
        "three_viable_patterns",
        "cross_form_factor_tradeoff",
        "high_risk_interaction_choice",
    }
)


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


def _extract(data: dict[str, Any], key: str) -> dict[str, Any] | None:
    if key in data:
        value = data[key]
        return value if isinstance(value, dict) else None
    return data


def canonical_bundle_sha256(bundle: dict[str, Any]) -> str:
    excluded = {
        "bundle_sha256",
        "final_acceptance_status",
        "accepted_by",
        "authorization_effect",
    }
    payload = {key: value for key, value in bundle.items() if key not in excluded}
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _required_layouts(matrix: dict[str, Any] | None) -> set[str]:
    if matrix is None:
        return set()
    rows = matrix.get("platforms")
    if not isinstance(rows, list):
        return set()
    return {
        layout_id
        for row in rows
        if isinstance(row, dict) and row.get("support_status") == "supported"
        for layout_id in row.get("layout_family_ids", [])
        if isinstance(layout_id, str)
    }


def validate_responsive_prototype_bundle(
    data: dict[str, Any],
    platform_data: dict[str, Any] | None = None,
    content_data: dict[str, Any] | None = None,
    logic_data: dict[str, Any] | None = None,
    *,
    lifecycle: str = "active",
) -> dict[str, Any]:
    bundle = _extract(data, "responsive_prototype_bundle")
    matrix = (
        _extract(platform_data, "platform_support_matrix") if platform_data is not None else None
    )
    content = (
        _extract(content_data, "screen_content_contract") if content_data is not None else None
    )
    logic = _extract(logic_data, "analysis_logic_draft") if logic_data is not None else None
    errors: list[dict[str, str]] = []
    if bundle is None:
        return {
            "ok": False,
            "code": "responsive_prototype_bundle_required",
            "errors": [
                {
                    "code": "responsive_prototype_bundle_required",
                    "detail": "bundle missing",
                }
            ],
        }
    schema = bundle.get("schema")
    if schema not in {
        "granoflow_responsive_prototype_bundle_v1",
        "granoflow_responsive_prototype_bundle_v2",
    }:
        errors.append(
            {
                "code": "responsive_prototype_bundle_required",
                "detail": "bundle schema invalid",
            }
        )
    if schema == "granoflow_responsive_prototype_bundle_v1" and lifecycle != "historical_read_only":
        errors.append(
            {
                "code": "responsive_prototype_bundle_upgrade_required",
                "detail": "active or reopened UI tasks require Bundle v2",
            }
        )
    if schema == "granoflow_responsive_prototype_bundle_v2":
        for field in (
            "analysis_logic_draft_sha256",
            "screen_content_contract_sha256",
        ):
            if not isinstance(bundle.get(field), str) or not HASH_RE.fullmatch(bundle[field]):
                errors.append(
                    {
                        "code": "responsive_prototype_content_mismatch",
                        "detail": f"{field} must be a lowercase SHA-256",
                    }
                )
        if content is not None and bundle.get("screen_content_contract_sha256") != content.get(
            "content_contract_sha256"
        ):
            errors.append(
                {
                    "code": "responsive_prototype_content_mismatch",
                    "detail": "Screen Content Contract digest is stale",
                }
            )
        if logic is not None and bundle.get("analysis_logic_draft_sha256") != logic.get(
            "draft_sha256"
        ):
            errors.append(
                {
                    "code": "responsive_prototype_content_mismatch",
                    "detail": "Analysis Logic Draft digest is stale",
                }
            )
    for field in (
        "platform_matrix_sha256",
        "baseline_package_sha256",
        "widget_catalog_input_sha256",
    ):
        if not isinstance(bundle.get(field), str) or not HASH_RE.fullmatch(bundle[field]):
            errors.append(
                {
                    "code": "responsive_prototype_bundle_required",
                    "detail": f"{field} must be a lowercase SHA-256",
                }
            )
    if matrix is not None and bundle.get("platform_matrix_sha256") != matrix.get("matrix_sha256"):
        errors.append(
            {
                "code": "responsive_prototype_digest_mismatch",
                "detail": "platform matrix digest is stale",
            }
        )

    option_count = bundle.get("option_count_decision")
    expected_count = 2 if option_count == "two" else 3 if option_count == "three" else 0
    if expected_count == 0:
        errors.append(
            {
                "code": "responsive_prototype_option_count_invalid",
                "detail": "option_count_decision must be two|three",
            }
        )
    reason = bundle.get("option_count_reason_code")
    if option_count == "three" and reason not in THREE_REASONS:
        errors.append(
            {
                "code": "responsive_prototype_option_count_invalid",
                "detail": "three options require an allowed reason code",
            }
        )
    if option_count == "two" and reason not in {None, ""}:
        errors.append(
            {
                "code": "responsive_prototype_option_count_invalid",
                "detail": "two options must not carry a three-option reason",
            }
        )

    selection = bundle.get("selection_round")
    options: list[Any] = []
    if not isinstance(selection, dict):
        errors.append(
            {
                "code": "responsive_prototype_bundle_required",
                "detail": "selection_round required",
            }
        )
    else:
        raw_options = selection.get("options")
        options = raw_options if isinstance(raw_options, list) else []
        if len(options) != expected_count:
            errors.append(
                {
                    "code": "responsive_prototype_option_count_invalid",
                    "detail": f"selection_round must contain {expected_count} options",
                }
            )
        option_ids: set[str] = set()
        artifact_hashes: set[str] = set()
        for index, option in enumerate(options):
            if not isinstance(option, dict):
                continue
            option_id = option.get("id")
            artifact_sha = option.get("html_sha256")
            axes = option.get("contrast_axes")
            parity = option.get("parity")
            if isinstance(option_id, str) and option_id:
                option_ids.add(option_id)
            if isinstance(artifact_sha, str) and HASH_RE.fullmatch(artifact_sha):
                artifact_hashes.add(artifact_sha)
            if not isinstance(axes, list) or len(axes) < 2:
                errors.append(
                    {
                        "code": "responsive_prototype_option_count_invalid",
                        "detail": f"selection option[{index}] needs two contrast axes",
                    }
                )
            if not isinstance(parity, dict) or any(
                parity.get(key) is not True
                for key in ("capabilities", "data", "states", "behavior")
            ):
                errors.append(
                    {
                        "code": "responsive_prototype_cross_layout_failed",
                        "detail": f"selection option[{index}] parity incomplete",
                    }
                )
        if len(option_ids) != len(options) or len(artifact_hashes) != len(options):
            errors.append(
                {
                    "code": "responsive_prototype_option_count_invalid",
                    "detail": "option ids and artifact hashes must be distinct",
                }
            )
        if bundle.get("selected_option_id") not in option_ids:
            errors.append(
                {
                    "code": "responsive_prototype_bundle_required",
                    "detail": "selected_option_id must reference an option",
                }
            )
        if selection.get("layout_family_id") != bundle.get("primary_layout_family"):
            errors.append(
                {
                    "code": "responsive_prototype_bundle_required",
                    "detail": "selection round must use primary layout family",
                }
            )

    variants = bundle.get("variants")
    if not isinstance(variants, list) or not variants:
        variants = []
        errors.append(
            {
                "code": "responsive_prototype_layout_missing",
                "detail": "variants must be non-empty",
            }
        )
    variant_ids: set[str] = set()
    for index, variant in enumerate(variants):
        if not isinstance(variant, dict):
            continue
        layout_id = variant.get("layout_family_id")
        if isinstance(layout_id, str) and layout_id:
            variant_ids.add(layout_id)
        viewport = variant.get("viewport")
        if (
            not isinstance(viewport, dict)
            or any(
                not isinstance(viewport.get(key), int | float) or viewport[key] <= 0
                for key in ("width", "height", "dpr")
            )
            or not isinstance(variant.get("platform_ids"), list)
            or not variant["platform_ids"]
        ):
            errors.append(
                {
                    "code": "responsive_prototype_layout_missing",
                    "detail": f"variant[{index}] viewport/platforms incomplete",
                }
            )
        for field in ("html_ref", "screenshot_ref"):
            if not isinstance(variant.get(field), str) or not variant[field]:
                errors.append(
                    {
                        "code": "responsive_prototype_layout_missing",
                        "detail": f"variant[{index}].{field} required",
                    }
                )
        for field in ("html_sha256", "screenshot_sha256"):
            if not isinstance(variant.get(field), str) or not HASH_RE.fullmatch(variant[field]):
                errors.append(
                    {
                        "code": "responsive_prototype_layout_missing",
                        "detail": f"variant[{index}].{field} invalid",
                    }
                )

    required_layouts = _required_layouts(matrix)
    missing_layouts = sorted(required_layouts - variant_ids)
    if missing_layouts:
        errors.append(
            {
                "code": "responsive_prototype_layout_missing",
                "detail": f"required layouts missing: {missing_layouts}",
            }
        )
    if bundle.get("primary_layout_family") not in variant_ids:
        errors.append(
            {
                "code": "responsive_prototype_layout_missing",
                "detail": "primary layout variant missing",
            }
        )

    checks = bundle.get("cross_layout_checks")
    if not isinstance(checks, dict) or any(
        checks.get(key) is not True
        for key in ("functional", "data", "states", "navigation", "widgets")
    ):
        errors.append(
            {
                "code": "responsive_prototype_cross_layout_failed",
                "detail": "all cross-layout checks must pass",
            }
        )
    if bundle.get("cross_layout_consistency_status") != "passed":
        errors.append(
            {
                "code": "responsive_prototype_cross_layout_failed",
                "detail": "cross_layout_consistency_status must be passed",
            }
        )
    if (
        not isinstance(bundle.get("widget_promotion_ref"), str)
        or not bundle["widget_promotion_ref"]
    ):
        errors.append(
            {
                "code": "widget_promotion_required",
                "detail": "widget_promotion_ref required",
            }
        )

    accepted = (
        bundle.get("final_acceptance_status"),
        bundle.get("accepted_by"),
    )
    if accepted not in {
        ("user_confirmed", "user"),
        ("unattended_auto_adopted", "unattended_grant"),
    }:
        errors.append(
            {
                "code": "responsive_prototype_final_acceptance_required",
                "detail": "final acceptance status is inconsistent",
            }
        )
    if bundle.get("authorization_effect") != "none":
        errors.append(
            {
                "code": "responsive_prototype_final_acceptance_required",
                "detail": "authorization_effect must be none",
            }
        )

    actual_digest = canonical_bundle_sha256(bundle)
    if bundle.get("bundle_sha256") != actual_digest:
        errors.append(
            {
                "code": "responsive_prototype_digest_mismatch",
                "detail": "bundle digest does not match current content",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "bundle_sha256": actual_digest,
        "required_layout_family_ids": sorted(required_layouts),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--platform-matrix", type=Path)
    parser.add_argument("--content-contract", type=Path)
    parser.add_argument("--logic-draft", type=Path)
    parser.add_argument(
        "--lifecycle",
        choices=("active", "historical_read_only"),
        default="active",
    )
    args = parser.parse_args(argv)
    try:
        data = _load(args.bundle)
        matrix = _load(args.platform_matrix) if args.platform_matrix else None
        content = _load(args.content_contract) if args.content_contract else None
        logic = _load(args.logic_draft) if args.logic_draft else None
        result = validate_responsive_prototype_bundle(
            data,
            matrix,
            content,
            logic,
            lifecycle=args.lifecycle,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "responsive_prototype_bundle_required",
            "errors": [{"code": "responsive_prototype_bundle_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
