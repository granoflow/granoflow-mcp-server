#!/usr/bin/env python3
"""Validate bidirectional requirement-to-screen-contract traceability."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any


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


def canonical_traceability_sha256(ledger: dict[str, Any]) -> str:
    excluded = {"traceability_sha256", "status", "review"}
    payload = {key: value for key, value in ledger.items() if key not in excluded}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def contract_element_refs(contract: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    screens = contract.get("screens")
    if not isinstance(screens, list):
        return refs
    for screen in screens:
        if not isinstance(screen, dict) or not isinstance(screen.get("screen_id"), str):
            continue
        screen_id = screen["screen_id"]
        refs.add(f"screen:{screen_id}")
        refs.add(f"navigation:{screen_id}")
        refs.add(f"permission:{screen_id}")
        sections = screen.get("content_sections")
        for section in sections if isinstance(sections, list) else []:
            if not isinstance(section, dict):
                continue
            fields = section.get("data_fields")
            for field in fields if isinstance(fields, list) else []:
                if isinstance(field, dict) and isinstance(field.get("field_id"), str):
                    refs.add(f"field:{screen_id}/{field['field_id']}")
                    refs.add(f"data_source:{screen_id}/{field['field_id']}")
        actions = screen.get("actions")
        for action in actions if isinstance(actions, list) else []:
            if isinstance(action, dict) and isinstance(action.get("action_id"), str):
                refs.add(f"action:{screen_id}/{action['action_id']}")
        states = screen.get("states")
        for state in states if isinstance(states, list) else []:
            if isinstance(state, dict) and isinstance(state.get("id"), str):
                refs.add(f"state:{screen_id}/{state['id']}")
    return refs


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def validate_requirement_contract_traceability(
    data: dict[str, Any],
    content_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ledger = _extract(data, "requirement_contract_traceability")
    contract = (
        _extract(content_data, "screen_content_contract") if content_data is not None else None
    )
    errors: list[dict[str, str]] = []
    if ledger is None:
        return {
            "ok": False,
            "code": "requirement_contract_traceability_required",
            "errors": [
                {
                    "code": "requirement_contract_traceability_required",
                    "detail": "traceability ledger missing",
                }
            ],
        }
    if ledger.get("schema") != "granoflow_requirement_contract_traceability_v1":
        errors.append(
            {
                "code": "requirement_contract_traceability_required",
                "detail": "traceability schema invalid",
            }
        )
    if not _nonempty(ledger.get("content_contract_sha256")):
        errors.append(
            {
                "code": "requirement_contract_traceability_required",
                "detail": "content_contract_sha256 required",
            }
        )
    if contract is not None and ledger.get("content_contract_sha256") != contract.get(
        "content_contract_sha256"
    ):
        errors.append(
            {
                "code": "requirement_contract_traceability_digest_mismatch",
                "detail": "Screen Content Contract digest is stale",
            }
        )

    rows = ledger.get("rows")
    if not isinstance(rows, list) or not rows:
        rows = []
        errors.append(
            {
                "code": "requirement_contract_traceability_required",
                "detail": "traceability rows required",
            }
        )
    covered_sources: set[str] = set()
    mapped_elements: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        source_kind = row.get("source_kind")
        source_ref = row.get("source_ref")
        refs = row.get("contract_element_refs")
        if (
            source_kind not in {"requirement", "acceptance", "derived_rule"}
            or not _nonempty(source_ref)
            or row.get("status") != "covered"
            or not _nonempty_list(refs)
        ):
            errors.append(
                {
                    "code": "requirement_contract_unmapped",
                    "detail": f"rows[{index}] must be a covered source mapping",
                }
            )
            continue
        assert isinstance(source_ref, str)
        assert isinstance(refs, list)
        covered_sources.add(source_ref)
        mapped_elements.update(ref for ref in refs if isinstance(ref, str) and bool(ref.strip()))

    expected_sources: set[str] = set()
    expected_elements: set[str] = set()
    if contract is not None:
        for field in ("requirement_refs", "acceptance_refs"):
            values = contract.get(field)
            if isinstance(values, list):
                expected_sources.update(value for value in values if isinstance(value, str))
        expected_elements = contract_element_refs(contract)
    missing_sources = sorted(expected_sources - covered_sources)
    if missing_sources:
        errors.append(
            {
                "code": "requirement_contract_unmapped",
                "detail": f"requirement/acceptance refs unmapped: {missing_sources}",
            }
        )
    missing_elements = sorted(expected_elements - mapped_elements)
    if missing_elements:
        errors.append(
            {
                "code": "contract_element_without_product_basis",
                "detail": f"contract elements lack product basis: {missing_elements}",
            }
        )
    unknown_elements = sorted(mapped_elements - expected_elements)
    if contract is not None and unknown_elements:
        errors.append(
            {
                "code": "requirement_contract_unmapped",
                "detail": f"traceability references unknown elements: {unknown_elements}",
            }
        )

    actual_digest = canonical_traceability_sha256(ledger)
    if ledger.get("traceability_sha256") != actual_digest:
        errors.append(
            {
                "code": "requirement_contract_traceability_digest_mismatch",
                "detail": "traceability digest is stale",
            }
        )
    review = ledger.get("review")
    review_valid = (
        isinstance(review, dict)
        and _nonempty(review.get("author_id"))
        and _nonempty(review.get("reviewer_id"))
        and review.get("author_id") != review.get("reviewer_id")
        and review.get("status") == "passed"
        and _nonempty_list(review.get("evidence_refs"))
        and review.get("reviewed_traceability_sha256") == actual_digest
    )
    if not review_valid:
        errors.append(
            {
                "code": "requirement_contract_review_failed",
                "detail": "independent product review must pass the current digest",
            }
        )
    if ledger.get("status") != "passed":
        errors.append(
            {
                "code": "requirement_contract_traceability_required",
                "detail": "status must be passed",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "traceability_sha256": actual_digest,
        "contract_element_refs": sorted(expected_elements),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--content-contract", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_requirement_contract_traceability(
            _load(args.ledger),
            _load(args.content_contract) if args.content_contract else None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "requirement_contract_traceability_required",
            "errors": [
                {
                    "code": "requirement_contract_traceability_required",
                    "detail": str(error),
                }
            ],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
