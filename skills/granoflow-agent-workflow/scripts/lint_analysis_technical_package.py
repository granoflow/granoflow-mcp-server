#!/usr/bin/env python3
"""Validate final logical technical reconciliation for UI Task Analysis."""

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
RECONCILIATION_AXES = {
    "fields",
    "actions",
    "states",
    "navigation",
    "permissions",
    "data_sources",
}
FORBIDDEN_PHYSICAL_KEYS = {
    "tables",
    "columns",
    "indexes",
    "ddl",
    "migration_steps",
    "api_endpoints",
    "classes",
    "implementation_sequence",
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


def canonical_technical_package_sha256(package: dict[str, Any]) -> str:
    excluded = {
        "technical_package_sha256",
        "status",
        "review",
        "final_verifier",
        "final_acceptance_status",
        "accepted_by",
        "authorization_effect",
    }
    payload = {key: value for key, value in package.items() if key not in excluded}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _find_forbidden_physical_keys(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in FORBIDDEN_PHYSICAL_KEYS:
                found.append(child_path)
            found.extend(_find_forbidden_physical_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_find_forbidden_physical_keys(child, f"{path}[{index}]"))
    return found


def validate_analysis_technical_package(
    data: dict[str, Any],
    logic_data: dict[str, Any] | None = None,
    content_data: dict[str, Any] | None = None,
    platform_data: dict[str, Any] | None = None,
    bundle_data: dict[str, Any] | None = None,
    semantic_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    package = _extract(data, "analysis_technical_package")
    logic = _extract(logic_data, "analysis_logic_draft") if logic_data is not None else None
    content = (
        _extract(content_data, "screen_content_contract") if content_data is not None else None
    )
    platform = (
        _extract(platform_data, "platform_support_matrix") if platform_data is not None else None
    )
    bundle = (
        _extract(bundle_data, "responsive_prototype_bundle") if bundle_data is not None else None
    )
    semantic = (
        _extract(semantic_data, "contract_prototype_semantic_review")
        if semantic_data is not None
        else None
    )
    errors: list[dict[str, str]] = []
    if package is None:
        return {
            "ok": False,
            "code": "analysis_technical_package_required",
            "errors": [
                {
                    "code": "analysis_technical_package_required",
                    "detail": "technical package missing",
                }
            ],
        }
    if package.get("schema") != "granoflow_analysis_technical_package_v1":
        errors.append(
            {
                "code": "analysis_technical_package_required",
                "detail": "technical package schema invalid",
            }
        )
    for field in (
        "logic_draft_sha256",
        "content_contract_sha256",
        "platform_matrix_sha256",
        "prototype_bundle_sha256",
        "contract_prototype_semantic_review_sha256",
        "behavior_summary_sha256",
    ):
        if not isinstance(package.get(field), str) or not HASH_RE.fullmatch(package[field]):
            errors.append(
                {
                    "code": "analysis_technical_package_required",
                    "detail": f"{field} must be a lowercase SHA-256",
                }
            )
    expected_hashes = (
        ("logic_draft_sha256", logic, "draft_sha256"),
        ("content_contract_sha256", content, "content_contract_sha256"),
        ("platform_matrix_sha256", platform, "matrix_sha256"),
        ("prototype_bundle_sha256", bundle, "bundle_sha256"),
        (
            "contract_prototype_semantic_review_sha256",
            semantic,
            "semantic_review_sha256",
        ),
    )
    for field, source, source_field in expected_hashes:
        if source is not None and package.get(field) != source.get(source_field):
            errors.append(
                {
                    "code": "analysis_technical_package_digest_mismatch",
                    "detail": f"{field} differs from current source",
                }
            )
    for field in (
        "operation_flows",
        "state_model",
        "permission_model",
        "ui_data_bindings",
        "platform_behavior",
        "technical_risks",
    ):
        if not isinstance(package.get(field), list):
            errors.append(
                {
                    "code": "analysis_technical_package_required",
                    "detail": f"{field} must be a list",
                }
            )
    for field in (
        "operation_flows",
        "state_model",
        "permission_model",
        "ui_data_bindings",
    ):
        if not _nonempty_list(package.get(field)):
            errors.append(
                {
                    "code": "analysis_technical_package_required",
                    "detail": f"{field} must be non-empty",
                }
            )
    disposition = package.get("schema_impact")
    if (
        not isinstance(disposition, dict)
        or disposition.get("disposition")
        not in {"not_applicable", "unchanged", "extend", "breaking"}
        or not _nonempty(disposition.get("summary"))
    ):
        errors.append(
            {
                "code": "analysis_technical_package_required",
                "detail": "schema_impact disposition and summary required",
            }
        )
    logical_model = package.get("logical_data_model")
    if not isinstance(logical_model, list):
        errors.append(
            {
                "code": "analysis_technical_package_required",
                "detail": "logical_data_model must be a list",
            }
        )
    forbidden = _find_forbidden_physical_keys(
        {
            "logical_data_model": logical_model,
            "schema_impact": disposition,
            "operation_flows": package.get("operation_flows"),
            "state_model": package.get("state_model"),
            "ui_data_bindings": package.get("ui_data_bindings"),
        }
    )
    if forbidden:
        errors.append(
            {
                "code": "analysis_technical_package_physical_design_forbidden",
                "detail": f"physical Planning keys found: {sorted(forbidden)}",
            }
        )
    reconciliation = package.get("reconciliation")
    rows = reconciliation.get("rows") if isinstance(reconciliation, dict) else None
    observed_axes = {
        row.get("axis")
        for row in rows or []
        if isinstance(row, dict) and row.get("status") in {"matched", "revised"}
    }
    reconciliation_valid = (
        isinstance(reconciliation, dict)
        and reconciliation.get("status") == "passed"
        and isinstance(rows, list)
        and RECONCILIATION_AXES.issubset(observed_axes)
        and all(
            isinstance(row, dict)
            and row.get("status") in {"matched", "revised"}
            and _nonempty_list(row.get("evidence_refs"))
            for row in rows
        )
    )
    if not reconciliation_valid:
        errors.append(
            {
                "code": "analysis_technical_package_reconciliation_failed",
                "detail": "all product-behavior axes require evidence-backed reconciliation",
            }
        )
    if not _nonempty(package.get("behavior_summary_ref")):
        errors.append(
            {
                "code": "analysis_technical_package_required",
                "detail": "behavior_summary_ref required",
            }
        )

    actual_digest = canonical_technical_package_sha256(package)
    if package.get("technical_package_sha256") != actual_digest:
        errors.append(
            {
                "code": "analysis_technical_package_digest_mismatch",
                "detail": "technical package digest is stale",
            }
        )
    review = package.get("review")
    review_valid = (
        isinstance(review, dict)
        and _nonempty(review.get("author_id"))
        and _nonempty(review.get("reviewer_id"))
        and review.get("author_id") != review.get("reviewer_id")
        and review.get("status") == "passed"
        and _nonempty_list(review.get("evidence_refs"))
        and review.get("reviewed_technical_package_sha256") == actual_digest
    )
    if not review_valid:
        errors.append(
            {
                "code": "analysis_technical_package_review_failed",
                "detail": "independent engineering review must pass current digest",
            }
        )
    verifier = package.get("final_verifier")
    verifier_valid = (
        isinstance(verifier, dict)
        and isinstance(review, dict)
        and _nonempty(review.get("author_id"))
        and _nonempty(review.get("reviewer_id"))
        and _nonempty(verifier.get("verifier_id"))
        and verifier.get("verifier_id") not in {review.get("author_id"), review.get("reviewer_id")}
        and verifier.get("status") == "passed"
        and verifier.get("verified_technical_package_sha256") == actual_digest
        and _nonempty_list(verifier.get("evidence_refs"))
    )
    if not verifier_valid:
        errors.append(
            {
                "code": "analysis_technical_package_verifier_failed",
                "detail": "independent final verifier must pass current digest",
            }
        )
    accepted = (
        package.get("final_acceptance_status"),
        package.get("accepted_by"),
    )
    if (
        accepted not in ACCEPTANCE
        or package.get("authorization_effect") != "none"
        or (
            bundle is not None
            and accepted
            != (
                bundle.get("final_acceptance_status"),
                bundle.get("accepted_by"),
            )
        )
    ):
        errors.append(
            {
                "code": "analysis_behavior_acceptance_required",
                "detail": "behavior acceptance must match the Bundle and grant no authority",
            }
        )
    if package.get("status") != "passed":
        errors.append(
            {
                "code": "analysis_technical_package_required",
                "detail": "status must be passed",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "technical_package_sha256": actual_digest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--logic-draft", type=Path)
    parser.add_argument("--content-contract", type=Path)
    parser.add_argument("--platform-matrix", type=Path)
    parser.add_argument("--prototype-bundle", type=Path)
    parser.add_argument("--semantic-review", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_analysis_technical_package(
            _load(args.package),
            _load(args.logic_draft) if args.logic_draft else None,
            _load(args.content_contract) if args.content_contract else None,
            _load(args.platform_matrix) if args.platform_matrix else None,
            _load(args.prototype_bundle) if args.prototype_bundle else None,
            _load(args.semantic_review) if args.semantic_review else None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "analysis_technical_package_required",
            "errors": [{"code": "analysis_technical_package_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
