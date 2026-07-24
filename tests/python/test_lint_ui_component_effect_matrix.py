#!/usr/bin/env python3
"""Tests for implementable Task UI component and effect selection."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-project-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_ui_component_effect_matrix import (  # noqa: E402
    candidate_score,
    validate_ui_component_effect_matrix,
)


def _sha(character: str) -> str:
    return character * 64


def candidate(
    candidate_id: str,
    *,
    source: str = "system_recommended",
    decision: str = "selected",
    score: int = 4,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "candidate_id": candidate_id,
        "kind": "widget",
        "role": "primary_action",
        "source": source,
        "stack_disposition": "allowed",
        "compatibility_status": "compatible",
        "functional_equivalence": "passed",
        "behavior_change": False,
        "user_decision": "not_required",
        "accessibility_status": "passed",
        "performance_status": "passed",
        "reduced_motion_status": "not_applicable",
        "fallback_status": "passed",
        "core_experience_benefit": False,
        "new_dependency": False,
        "implementations": [
            {
                "platform_id": "ios",
                "orientation": "portrait",
                "layout_family_id": "mobile_portrait",
                "implementation": "native_button",
                "dependency_ref": "flutter-sdk",
                "support_status": "passed",
                "fallback": "text_button",
            }
        ],
        "scores": {
            "product_fit": score,
            "usability": score,
            "aesthetic": score,
            "performance": score,
            "maintainability": score,
        },
        "decision": decision,
    }
    row["computed_score"] = candidate_score(row)
    return row


def make_record() -> dict[str, Any]:
    return {
        "ui_component_effect_matrix": {
            "schema": "ui_component_effect_matrix_v1",
            "input_shas": {
                "user_selection": _sha("a"),
                "baseline": _sha("b"),
                "widget_catalog": _sha("c"),
                "platform_matrix": _sha("d"),
                "stack_capability": _sha("e"),
                "approved_dependencies": _sha("f"),
            },
            "required_layouts": [
                {
                    "platform_id": "ios",
                    "orientation": "portrait",
                    "layout_family_id": "mobile_portrait",
                }
            ],
            "candidates": [candidate("button-a")],
            "status": "passed",
        }
    }


class UiComponentEffectMatrixTest(unittest.TestCase):
    def test_single_eligible_winner_passes(self) -> None:
        self.assertTrue(validate_ui_component_effect_matrix(make_record())["ok"])

    def test_equivalent_visible_adaptation_passes(self) -> None:
        record = make_record()
        row = record["ui_component_effect_matrix"]["candidates"][0]
        row["source"] = "user_selected"
        row["compatibility_status"] = "adapted"
        row["equivalent_variant_id"] = "button-ios"
        row["mapping_visible"] = True
        self.assertTrue(validate_ui_component_effect_matrix(record)["ok"])

    def test_behavior_change_requires_user_decision(self) -> None:
        record = make_record()
        row = record["ui_component_effect_matrix"]["candidates"][0]
        row["behavior_change"] = True
        row["user_decision"] = "pending"
        row["decision"] = "pending_user_decision"
        result = validate_ui_component_effect_matrix(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "ui_component_effect_user_decision_required"
                for error in result["errors"]
            )
        )

    def test_forbidden_and_unjustified_high_cost_fail(self) -> None:
        forbidden = make_record()
        forbidden["ui_component_effect_matrix"]["candidates"][0]["stack_disposition"] = "forbidden"
        self.assertFalse(validate_ui_component_effect_matrix(forbidden)["ok"])

        expensive = make_record()
        row = expensive["ui_component_effect_matrix"]["candidates"][0]
        row["kind"] = "effect"
        row["stack_disposition"] = "high_cost"
        row["reduced_motion_status"] = "not_applicable"
        self.assertFalse(validate_ui_component_effect_matrix(expensive)["ok"])

    def test_catalog_widget_cannot_be_bypassed(self) -> None:
        record = make_record()
        rows = record["ui_component_effect_matrix"]["candidates"]
        rows[0]["decision"] = "selected"
        rows.append(candidate("catalog-button", source="catalog", decision="rejected"))
        result = validate_ui_component_effect_matrix(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "ui_widget_reuse_bypassed" for error in result["errors"])
        )

    def test_highest_ranked_candidate_must_win(self) -> None:
        record = make_record()
        rows = record["ui_component_effect_matrix"]["candidates"]
        rows[0]["decision"] = "selected"
        rows.append(candidate("button-b", decision="rejected", score=5))
        result = validate_ui_component_effect_matrix(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "ui_component_effect_ranking_invalid" for error in result["errors"]
            )
        )

    def test_selected_candidate_must_cover_all_layouts(self) -> None:
        record = make_record()
        record["ui_component_effect_matrix"]["required_layouts"].append(
            {
                "platform_id": "ios",
                "orientation": "landscape",
                "layout_family_id": "mobile_landscape",
            }
        )
        self.assertFalse(validate_ui_component_effect_matrix(record)["ok"])


if __name__ == "__main__":
    unittest.main()
