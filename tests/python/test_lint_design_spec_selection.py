#!/usr/bin/env python3
"""Tests for the two-round Design Spec selection contract."""

from __future__ import annotations

import sys
import unittest
from itertools import combinations
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-project-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_design_spec_selection import (  # noqa: E402
    DIMENSIONS,
    complete_selection_code,
    derive_seed,
    parse_selection_code,
    validate_design_spec_selection,
)


def _sha(character: str) -> str:
    return character * 64


def make_record(count: int = 3) -> dict[str, Any]:
    fit_sha = _sha("a")
    master_seed = "seed-127"
    code = "1a2b3c4d5a6b"
    recommendations = ("a", "b", "c", "d", "a", "b")
    dimensions = [
        {
            "number": number,
            "id": dimension_id,
            "recommended": recommended,
            "options": [
                {
                    "value": value,
                    "fit_status": "passed",
                    "materially_distinct_status": "passed",
                }
                for value in "abcd"
            ],
        }
        for (number, dimension_id), recommended in zip(
            DIMENSIONS,
            recommendations,
            strict=True,
        )
    ]
    ids = [f"spec_{letter}" for letter in "abc"[:count]]
    candidates = [
        {
            "option_id": option_id,
            "derived_seed": derive_seed(
                master_seed=master_seed,
                product_fit_sha256=fit_sha,
                selection_code=code,
                identity=f"spec:{option_id}",
                algorithm_version=1,
            ),
            "artifact_ref": f"prototype://{option_id}.html",
            "artifact_sha256": _sha(str(index + 1)),
            "fit_status": "passed",
            "coverage_status": "passed",
        }
        for index, option_id in enumerate(ids)
    ]
    pairwise = [
        {
            "left": left,
            "right": right,
            "axes": ["neutral_temperature", "type_scale", "component_emphasis"],
            "status": "passed",
        }
        for left, right in combinations(ids, 2)
    ]
    record = {
        "schema": "granoflow_design_spec_selection_v2",
        "mode": "interactive_two_round",
        "product_fit_envelope": {
            "status": "passed",
            "input_sha256": fit_sha,
            "source_refs": ["project-work://product-doc"],
            "allowed_directions": ["calm"],
            "excluded_directions": ["neon"],
        },
        "generation": {
            "algorithm": "hmac-sha256",
            "algorithm_version": 1,
            "master_seed": master_seed,
            "product_fit_sha256": fit_sha,
        },
        "direction_round": {
            "artifact_ref": "prototype://direction.html",
            "artifact_sha256": _sha("b"),
            "quality_status": "passed",
            "asset_policy": "html_css_inline_svg_only",
            "dimensions": dimensions,
            "selection_code_input": code,
            "selection_code_canonical": code,
            "completed_selections": [
                {"number": number, "value": value, "source": "user"}
                for number, value in zip(range(1, 7), "abcdab", strict=True)
            ],
        },
        "spec_round": {
            "candidate_count": count,
            "reduction_reason_code": "insufficient_distinct_third" if count == 2 else None,
            "comparison_artifact_ref": "prototype://comparison.html",
            "comparison_artifact_sha256": _sha("c"),
            "quality_status": "passed",
            "asset_policy": "html_css_inline_svg_only",
            "candidates": candidates,
            "pairwise_differences": pairwise,
        },
        "selected_option_id": ids[0],
        "seed": candidates[0]["derived_seed"],
        "candidates": candidates,
        "provenance": "user_selected",
    }
    return {"design_spec_selection": record}


class SelectionCodeTest(unittest.TestCase):
    def test_partial_code_is_completed_in_numeric_order(self) -> None:
        canonical, completed = complete_selection_code(
            "4c1b",
            {1: "a", 2: "b", 3: "c", 4: "d", 5: "a", 6: "b"},
        )
        self.assertEqual(canonical, "1b2b3c4c5a6b")
        self.assertEqual(completed[1]["source"], "system_recommended")

    def test_duplicate_or_malformed_code_fails(self) -> None:
        for code in ("1a1b", "1a-2b", "7a", "1z"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                parse_selection_code(code)

    def test_seed_derivation_is_stable_and_input_sensitive(self) -> None:
        args = {
            "master_seed": "seed-1",
            "product_fit_sha256": _sha("a"),
            "selection_code": "1a2b3c4d5a6b",
            "identity": "spec:spec_a",
            "algorithm_version": 1,
        }
        first = derive_seed(**args)
        self.assertEqual(first, derive_seed(**args))
        args["identity"] = "spec:spec_b"
        self.assertNotEqual(first, derive_seed(**args))


class DesignSpecSelectionTest(unittest.TestCase):
    def test_three_and_justified_two_candidate_records_pass(self) -> None:
        self.assertTrue(validate_design_spec_selection(make_record(3))["ok"])
        self.assertTrue(validate_design_spec_selection(make_record(2))["ok"])

    def test_two_candidates_require_reduction_reason(self) -> None:
        record = make_record(2)
        record["design_spec_selection"]["spec_round"]["reduction_reason_code"] = None
        result = validate_design_spec_selection(record)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "design_spec_candidate_count_invalid")

    def test_unsuitable_direction_option_fails(self) -> None:
        record = make_record()
        option = record["design_spec_selection"]["direction_round"]["dimensions"][0]["options"][0]
        option["fit_status"] = "failed"
        result = validate_design_spec_selection(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "design_direction_candidate_insufficient"
                for error in result["errors"]
            )
        )

    def test_incomplete_difference_matrix_fails(self) -> None:
        record = make_record()
        record["design_spec_selection"]["spec_round"]["pairwise_differences"].pop()
        result = validate_design_spec_selection(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "design_spec_candidate_difference_insufficient"
                for error in result["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
