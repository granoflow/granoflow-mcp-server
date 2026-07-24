#!/usr/bin/env python3
"""Validate two-round Design Spec selection records."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_design_spec_selection_v2"
DIMENSIONS = (
    (1, "color"),
    (2, "density"),
    (3, "shape"),
    (4, "typography"),
    (5, "layering"),
    (6, "layout"),
)
VALUES = ("a", "b", "c", "d")
PAIR_RE = re.compile(r"([1-6])([a-d])")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_selection_code(value: str) -> dict[int, str]:
    if not isinstance(value, str) or not value:
        raise ValueError("selection code is empty")
    matches = list(PAIR_RE.finditer(value))
    if not matches or "".join(match.group(0) for match in matches) != value:
        raise ValueError("selection code must contain only [1-6][a-d] pairs")
    selected: dict[int, str] = {}
    for match in matches:
        number = int(match.group(1))
        if number in selected:
            raise ValueError(f"dimension {number} is repeated")
        selected[number] = match.group(2)
    return selected


def complete_selection_code(
    value: str,
    recommendations: dict[int, str],
) -> tuple[str, list[dict[str, Any]]]:
    selected = parse_selection_code(value)
    completed: list[dict[str, Any]] = []
    for number, _ in DIMENSIONS:
        choice = selected.get(number, recommendations.get(number))
        if choice not in VALUES:
            raise ValueError(f"dimension {number} has no valid recommendation")
        completed.append(
            {
                "number": number,
                "value": choice,
                "source": "user" if number in selected else "system_recommended",
            }
        )
    canonical = "".join(f"{item['number']}{item['value']}" for item in completed)
    return canonical, completed


def derive_seed(
    *,
    master_seed: str,
    product_fit_sha256: str,
    selection_code: str,
    identity: str,
    algorithm_version: int,
) -> str:
    message = "|".join(
        (
            str(algorithm_version),
            product_fit_sha256,
            selection_code,
            identity,
        )
    )
    return hmac.new(
        master_seed.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()


def _hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.fullmatch(value) is not None


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_design_spec_selection(data: dict[str, Any]) -> dict[str, Any]:
    record = data.get("design_spec_selection", data)
    errors: list[dict[str, str]] = []

    def hit(code: str, detail: str) -> None:
        errors.append({"code": code, "detail": detail})

    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        return {
            "ok": False,
            "code": "design_direction_round_required",
            "errors": [
                {
                    "code": "design_direction_round_required",
                    "detail": f"record schema must be {SCHEMA}",
                }
            ],
        }

    mode = record.get("mode")
    if mode not in {"interactive_two_round", "unattended_single"}:
        hit("design_direction_round_required", "mode invalid")

    fit = record.get("product_fit_envelope")
    fit_sha = fit.get("input_sha256") if isinstance(fit, dict) else None
    if (
        not isinstance(fit, dict)
        or fit.get("status") != "passed"
        or not _hash(fit_sha)
        or not isinstance(fit.get("source_refs"), list)
        or not fit.get("source_refs")
    ):
        hit("design_fit_envelope_required", "passed fit envelope with sources/SHA required")
    elif not all(
        isinstance(fit.get(field), list) for field in ("allowed_directions", "excluded_directions")
    ):
        hit("design_fit_envelope_required", "allowed/excluded directions must be lists")

    generation = record.get("generation")
    master_seed = generation.get("master_seed") if isinstance(generation, dict) else None
    algorithm_version = (
        generation.get("algorithm_version") if isinstance(generation, dict) else None
    )
    if (
        not isinstance(generation, dict)
        or generation.get("algorithm") != "hmac-sha256"
        or not _text(master_seed)
        or not isinstance(algorithm_version, int)
        or algorithm_version < 1
        or generation.get("product_fit_sha256") != fit_sha
    ):
        hit("design_generation_reproducibility_missing", "generation record invalid")

    direction_value = record.get("direction_round")
    direction = direction_value if isinstance(direction_value, dict) else {}
    dimensions = direction.get("dimensions")
    recommendations: dict[int, str] = {}
    if not isinstance(direction_value, dict) or not isinstance(dimensions, list):
        hit("design_direction_round_required", "direction round missing")
        dimensions = []
    if mode == "interactive_two_round":
        if not _text(direction.get("artifact_ref")) or not _hash(direction.get("artifact_sha256")):
            hit("design_direction_round_required", "direction HTML ref/SHA missing")
        if (
            direction.get("quality_status") != "passed"
            or direction.get("asset_policy") != "html_css_inline_svg_only"
        ):
            hit("design_round_html_quality_failed", "direction HTML quality invalid")

    if len(dimensions) != 6:
        hit("design_direction_round_required", "exactly six dimensions required")
    else:
        for row, (number, dimension_id) in zip(dimensions, DIMENSIONS, strict=True):
            if (
                not isinstance(row, dict)
                or row.get("number") != number
                or row.get("id") != dimension_id
            ):
                hit("design_direction_round_required", f"dimension {number} invalid")
                continue
            recommended = row.get("recommended")
            if recommended in VALUES:
                recommendations[number] = recommended
            else:
                hit("design_direction_round_required", f"dimension {number} recommendation invalid")
            options = row.get("options")
            if not isinstance(options, list) or len(options) != 4:
                hit("design_direction_candidate_insufficient", f"dimension {number} needs 4")
                continue
            if [option.get("value") for option in options] != list(VALUES):
                hit("design_direction_candidate_insufficient", f"dimension {number} values invalid")
            if any(option.get("fit_status") != "passed" for option in options):
                hit("design_direction_candidate_insufficient", f"dimension {number} fit failed")
            if any(option.get("materially_distinct_status") != "passed" for option in options):
                hit(
                    "design_spec_candidate_difference_insufficient",
                    f"dimension {number} distinction failed",
                )

    try:
        selection_code_input = direction.get("selection_code_input")
        if not isinstance(selection_code_input, str):
            raise TypeError("selection code input must be a string")
        canonical, completed = complete_selection_code(
            selection_code_input,
            recommendations,
        )
        if direction.get("selection_code_canonical") != canonical:
            hit("design_selection_code_invalid", "canonical code mismatch")
        if direction.get("completed_selections") != completed:
            hit("design_selection_code_invalid", "completed selections mismatch")
    except (TypeError, ValueError) as error:
        canonical = ""
        hit("design_selection_code_invalid", str(error))

    spec_round_value = record.get("spec_round")
    spec_round = spec_round_value if isinstance(spec_round_value, dict) else {}
    candidates = spec_round.get("candidates")
    if not isinstance(candidates, list):
        candidates = []
    count = spec_round.get("candidate_count")
    expected_counts = {2, 3} if mode == "interactive_two_round" else {1}
    if count not in expected_counts or count != len(candidates):
        hit("design_spec_candidate_count_invalid", "candidate count invalid")
    if mode == "interactive_two_round":
        if count == 2 and spec_round.get("reduction_reason_code") != "insufficient_distinct_third":
            hit("design_spec_candidate_count_invalid", "two candidates need reduction reason")
        if count == 3 and spec_round.get("reduction_reason_code") is not None:
            hit("design_spec_candidate_count_invalid", "three candidates need no reason")
        if not _text(spec_round.get("comparison_artifact_ref")) or not _hash(
            spec_round.get("comparison_artifact_sha256")
        ):
            hit("design_spec_candidate_count_invalid", "comparison HTML ref/SHA missing")
        if (
            spec_round.get("quality_status") != "passed"
            or spec_round.get("asset_policy") != "html_css_inline_svg_only"
        ):
            hit("design_round_html_quality_failed", "comparison HTML quality invalid")

    ids: list[str] = []
    for candidate in candidates:
        option_id = candidate.get("option_id") if isinstance(candidate, dict) else None
        if not _text(option_id):
            hit("design_spec_candidate_count_invalid", "candidate id missing")
            continue
        ids.append(str(option_id))
        if candidate.get("fit_status") != "passed" or candidate.get("coverage_status") != "passed":
            hit("design_fit_envelope_required", f"{option_id} fit/coverage failed")
        if not _text(candidate.get("artifact_ref")) or not _hash(candidate.get("artifact_sha256")):
            hit("design_spec_candidate_count_invalid", f"{option_id} artifact invalid")
        if (
            _text(master_seed)
            and _hash(fit_sha)
            and canonical
            and isinstance(algorithm_version, int)
        ):
            assert isinstance(master_seed, str)
            assert isinstance(fit_sha, str)
            expected_seed = derive_seed(
                master_seed=master_seed,
                product_fit_sha256=fit_sha,
                selection_code=canonical,
                identity=f"spec:{option_id}",
                algorithm_version=algorithm_version,
            )
            if candidate.get("derived_seed") != expected_seed:
                hit("design_generation_reproducibility_missing", f"{option_id} seed mismatch")
    if len(ids) != len(set(ids)):
        hit("design_spec_candidate_count_invalid", "candidate ids not unique")

    if mode == "interactive_two_round" and count in {2, 3}:
        expected_pairs = {frozenset(pair) for pair in combinations(ids, 2)}
        rows = spec_round.get("pairwise_differences", [])
        actual_pairs: set[frozenset[str]] = set()
        for row in rows if isinstance(rows, list) else []:
            pair = frozenset((str(row.get("left")), str(row.get("right"))))
            actual_pairs.add(pair)
            axes = row.get("axes")
            if row.get("status") != "passed" or not isinstance(axes, list) or len(set(axes)) < 3:
                hit(
                    "design_spec_candidate_difference_insufficient",
                    "candidate pair needs 3 passed axes",
                )
        if actual_pairs != expected_pairs:
            hit("design_spec_candidate_difference_insufficient", "pair matrix incomplete")

    selected_id = record.get("selected_option_id")
    if selected_id is not None and selected_id not in ids:
        hit("design_spec_candidate_count_invalid", "selected option invalid")
    selected = next(
        (candidate for candidate in candidates if candidate.get("option_id") == selected_id),
        None,
    )
    if selected is not None and record.get("seed") != selected.get("derived_seed"):
        hit("design_generation_reproducibility_missing", "selected seed mirror mismatch")
    if record.get("candidates") != candidates:
        hit("design_spec_candidate_count_invalid", "candidate mirror mismatch")

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
        result = validate_design_spec_selection(value)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "design_direction_round_required",
            "errors": [{"code": "design_direction_round_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
