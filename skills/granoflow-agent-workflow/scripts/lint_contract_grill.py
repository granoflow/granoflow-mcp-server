#!/usr/bin/env python3
"""Validate the evidence-backed Granoflow Contract Grill ledger."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_AXES = {
    "requirements",
    "fields",
    "actions",
    "states",
    "navigation",
    "permissions",
    "data_sources",
}


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


def canonical_contract_grill_sha256(grill: dict[str, Any]) -> str:
    excluded = {"grill_sha256", "status"}
    payload = {key: value for key, value in grill.items() if key not in excluded}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def validate_contract_grill(
    data: dict[str, Any],
    content_data: dict[str, Any] | None = None,
    traceability_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    grill = _extract(data, "contract_grill")
    contract = (
        _extract(content_data, "screen_content_contract") if content_data is not None else None
    )
    traceability = (
        _extract(traceability_data, "requirement_contract_traceability")
        if traceability_data is not None
        else None
    )
    errors: list[dict[str, str]] = []
    if grill is None:
        return {
            "ok": False,
            "code": "contract_grill_required",
            "errors": [{"code": "contract_grill_required", "detail": "Contract Grill missing"}],
        }
    if grill.get("schema") != "granoflow_contract_grill_v1":
        errors.append(
            {"code": "contract_grill_required", "detail": "Contract Grill schema invalid"}
        )
    if contract is not None and grill.get("content_contract_sha256") != contract.get(
        "content_contract_sha256"
    ):
        errors.append(
            {
                "code": "contract_grill_digest_mismatch",
                "detail": "Screen Content Contract digest is stale",
            }
        )
    if traceability is not None and grill.get("traceability_sha256") != traceability.get(
        "traceability_sha256"
    ):
        errors.append(
            {
                "code": "contract_grill_digest_mismatch",
                "detail": "requirement traceability digest is stale",
            }
        )
    mode = grill.get("mode")
    if mode not in {"interactive", "unattended"}:
        errors.append(
            {"code": "contract_grill_required", "detail": "mode must be interactive|unattended"}
        )
    questions = grill.get("questions")
    if not isinstance(questions, list) or not questions:
        questions = []
        errors.append({"code": "contract_grill_required", "detail": "questions required"})
    observed_axes: set[str] = set()
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            continue
        axis = question.get("axis")
        if axis in REQUIRED_AXES:
            observed_axes.add(axis)
        expected_source = "user" if mode == "interactive" else "unattended_grant"
        valid = (
            axis in REQUIRED_AXES
            and _nonempty(question.get("id"))
            and _nonempty(question.get("question"))
            and _nonempty(question.get("recommendation"))
            and _nonempty(question.get("rationale"))
            and question.get("disposition") in {"accepted", "revised", "not_applicable"}
            and question.get("answer_source") == expected_source
            and _nonempty_list(question.get("evidence_refs"))
            and question.get("blocking") is False
        )
        if not valid:
            errors.append(
                {
                    "code": "contract_grill_open_questions",
                    "detail": f"questions[{index}] is incomplete or blocking",
                }
            )
    missing_axes = sorted(REQUIRED_AXES - observed_axes)
    checks = grill.get("coverage_axes")
    if (
        missing_axes
        or not isinstance(checks, dict)
        or any(checks.get(axis) is not True for axis in REQUIRED_AXES)
    ):
        errors.append(
            {
                "code": "contract_grill_coverage_incomplete",
                "detail": f"Contract Grill axes missing or failed: {missing_axes}",
            }
        )
    blockers = grill.get("open_blockers")
    if not isinstance(blockers, list) or blockers:
        errors.append(
            {
                "code": "contract_grill_open_questions",
                "detail": "open_blockers must be an empty list",
            }
        )
    if grill.get("authorization_effect") != "none":
        errors.append(
            {
                "code": "contract_grill_required",
                "detail": "authorization_effect must be none",
            }
        )
    actual_digest = canonical_contract_grill_sha256(grill)
    if grill.get("grill_sha256") != actual_digest:
        errors.append(
            {
                "code": "contract_grill_digest_mismatch",
                "detail": "Contract Grill digest is stale",
            }
        )
    if grill.get("status") != "passed":
        errors.append({"code": "contract_grill_required", "detail": "status must be passed"})
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "grill_sha256": actual_digest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("grill", type=Path)
    parser.add_argument("--content-contract", type=Path)
    parser.add_argument("--traceability", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_contract_grill(
            _load(args.grill),
            _load(args.content_contract) if args.content_contract else None,
            _load(args.traceability) if args.traceability else None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "contract_grill_required",
            "errors": [{"code": "contract_grill_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
