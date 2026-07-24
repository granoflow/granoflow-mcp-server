#!/usr/bin/env python3
"""Validate implementable Task UI component/effect choices and ranking."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "ui_component_effect_matrix_v1"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
SCORE_FIELDS = {
    "product_fit": 30,
    "usability": 25,
    "aesthetic": 25,
    "performance": 10,
    "maintainability": 10,
}


def _hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.fullmatch(value) is not None


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _layout_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("platform_id")),
        str(row.get("orientation")),
        str(row.get("layout_family_id")),
    )


def candidate_score(candidate: dict[str, Any]) -> int | None:
    scores = candidate.get("scores")
    if not isinstance(scores, dict):
        return None
    values: dict[str, int] = {}
    for field in SCORE_FIELDS:
        value = scores.get(field)
        if not isinstance(value, int) or not 0 <= value <= 5:
            return None
        values[field] = value
    return sum(values[field] * weight for field, weight in SCORE_FIELDS.items())


def _eligible(candidate: dict[str, Any], required_keys: set[tuple[str, str, str]]) -> bool:
    implementations = candidate.get("implementations")
    implementation_rows = implementations if isinstance(implementations, list) else []
    implementation_keys = {_layout_key(row) for row in implementation_rows if isinstance(row, dict)}
    return (
        candidate.get("stack_disposition") != "forbidden"
        and candidate.get("compatibility_status") in {"compatible", "adapted"}
        and candidate.get("functional_equivalence") == "passed"
        and candidate.get("accessibility_status") == "passed"
        and candidate.get("performance_status") == "passed"
        and implementation_keys == required_keys
    )


def validate_ui_component_effect_matrix(data: dict[str, Any]) -> dict[str, Any]:
    record = data.get("ui_component_effect_matrix", data)
    errors: list[dict[str, str]] = []

    def hit(code: str, detail: str) -> None:
        errors.append({"code": code, "detail": detail})

    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        return {
            "ok": False,
            "code": "ui_component_effect_matrix_required",
            "errors": [
                {
                    "code": "ui_component_effect_matrix_required",
                    "detail": f"record schema must be {SCHEMA}",
                }
            ],
        }

    input_shas = record.get("input_shas")
    required_inputs = {
        "user_selection",
        "baseline",
        "widget_catalog",
        "platform_matrix",
        "stack_capability",
        "approved_dependencies",
    }
    if not isinstance(input_shas, dict) or any(
        not _hash(input_shas.get(field)) for field in required_inputs
    ):
        hit("ui_component_effect_matrix_required", "all input SHA values required")

    layouts = record.get("required_layouts")
    required_keys = (
        {_layout_key(row) for row in layouts if isinstance(row, dict)}
        if isinstance(layouts, list)
        else set()
    )
    if not isinstance(layouts, list) or not layouts or len(required_keys) != len(layouts):
        hit("ui_component_effect_matrix_required", "required layouts invalid")

    candidates = record.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        hit("ui_component_effect_matrix_required", "candidates required")
        candidates = []
    ids = [row.get("candidate_id") for row in candidates if isinstance(row, dict)]
    if len(ids) != len(candidates) or len(ids) != len(set(ids)):
        hit("ui_component_effect_matrix_required", "candidate ids must be unique")

    by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        if not isinstance(candidate, dict) or not _text(candidate.get("role")):
            hit("ui_component_effect_matrix_required", "candidate role missing")
            continue
        candidate_id = candidate.get("candidate_id")
        by_role[candidate["role"]].append(candidate)
        score = candidate_score(candidate)
        if score is None or candidate.get("computed_score") != score:
            hit("ui_component_effect_ranking_invalid", f"{candidate_id} score invalid")

        decision = candidate.get("decision")
        if (
            candidate.get("compatibility_status") == "incompatible"
            and candidate.get("source") == "user_selected"
            and decision != "pending_user_decision"
        ):
            hit(
                "ui_component_effect_user_decision_required",
                f"{candidate_id} incompatible user choice needs a decision",
            )
        if candidate.get("compatibility_status") == "adapted" and (
            not _text(candidate.get("equivalent_variant_id"))
            or candidate.get("mapping_visible") is not True
            or candidate.get("behavior_change") is not False
        ):
            hit("ui_component_effect_incompatible", f"{candidate_id} adaptation invalid")
        if (
            candidate.get("behavior_change") is True
            and candidate.get("user_decision") != "confirmed"
        ):
            hit(
                "ui_component_effect_user_decision_required",
                f"{candidate_id} behavior change unconfirmed",
            )
        if candidate.get("stack_disposition") == "forbidden" and decision == "selected":
            hit("ui_component_effect_incompatible", f"{candidate_id} forbidden")

        implementations = candidate.get("implementations")
        implementation_rows = implementations if isinstance(implementations, list) else []
        implementation_keys = {
            _layout_key(row) for row in implementation_rows if isinstance(row, dict)
        }
        if decision == "selected" and implementation_keys != required_keys:
            hit("ui_component_effect_incompatible", f"{candidate_id} layout coverage missing")
        for implementation in implementation_rows:
            if not isinstance(implementation, dict):
                continue
            if implementation.get("support_status") != "passed":
                hit("ui_component_effect_incompatible", f"{candidate_id} support failed")
            if not _text(implementation.get("fallback")):
                hit("ui_component_effect_fallback_missing", f"{candidate_id} fallback missing")

        if decision == "selected":
            if not _eligible(candidate, required_keys):
                hit("ui_component_effect_incompatible", f"{candidate_id} hard gate failed")
            if (
                candidate.get("kind") == "effect"
                and candidate.get("reduced_motion_status") != "passed"
            ):
                hit(
                    "ui_component_effect_fallback_missing",
                    f"{candidate_id} reduced motion missing",
                )
            if candidate.get("stack_disposition") == "high_cost" and not all(
                (
                    candidate.get("core_experience_benefit") is True,
                    candidate.get("performance_status") == "passed",
                    candidate.get("reduced_motion_status") == "passed",
                    candidate.get("fallback_status") == "passed",
                )
            ):
                hit(
                    "ui_component_effect_high_cost_unjustified",
                    f"{candidate_id} high-cost requirements missing",
                )

    for role, rows in by_role.items():
        eligible = [row for row in rows if _eligible(row, required_keys)]
        selected = [row for row in rows if row.get("decision") == "selected"]
        catalog = [row for row in eligible if row.get("source") == "catalog"]
        if catalog and not any(row in catalog for row in selected):
            hit("ui_widget_reuse_bypassed", f"{role} bypasses Catalog Widget")
            continue
        if not catalog and eligible:
            ranked = sorted(
                eligible,
                key=lambda row: (
                    -(candidate_score(row) or 0),
                    row.get("new_dependency") is True,
                    str(row.get("candidate_id")),
                ),
            )
            if len(selected) != 1 or selected[0] is not ranked[0]:
                hit("ui_component_effect_ranking_invalid", f"{role} winner invalid")

    if any(row.get("decision") == "pending_user_decision" for row in candidates):
        hit("ui_component_effect_user_decision_required", "pending user decision remains")
    if record.get("status") != "passed":
        hit("ui_component_effect_matrix_required", "matrix status must be passed")

    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("root must be an object")
        result = validate_ui_component_effect_matrix(value)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "ui_component_effect_matrix_required",
            "errors": [{"code": "ui_component_effect_matrix_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
