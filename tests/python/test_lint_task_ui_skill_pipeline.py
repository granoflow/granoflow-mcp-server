#!/usr/bin/env python3
"""Tests for evidenced Task UI design capability routing."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-project-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_task_ui_skill_pipeline import (  # noqa: E402
    ALL_CAPABILITIES,
    validate_task_ui_skill_pipeline,
)


def _sha(character: str) -> str:
    return character * 64


def make_record() -> dict[str, Any]:
    capabilities = []
    for index, capability_id in enumerate(sorted(ALL_CAPABILITIES)):
        applicable = capability_id != "advanced_motion_authoring"
        row: dict[str, Any] = {
            "capability_id": capability_id,
            "condition_status": "applicable" if applicable else "not_applicable",
        }
        if applicable:
            review = capability_id not in {
                "ui_expression_exploration",
                "high_fidelity_html_authoring",
            }
            row["selected_provider"] = {
                "provider_id": "native-host",
                "kind": "native",
                "availability": "available",
                "invocation_mode": "native",
                "mutation_policy": "review_only" if review else "artifact_only",
                "mutation_authorization": "none",
                "result": "model_fallback",
                "discovery_evidence": "host capability observed",
                "input_sha256": _sha(str((index % 8) + 1)),
                "output_artifact_sha256": _sha(str(((index + 1) % 8) + 1)),
                "authorization_effect": "none",
            }
        capabilities.append(row)
    return {
        "task_ui_skill_pipeline": {
            "schema": "task_ui_skill_pipeline_v1",
            "platform_ids": ["ios"],
            "stack_kinds": ["flutter"],
            "advanced_motion_required": False,
            "input_shas": {
                "baseline": _sha("a"),
                "widget_catalog": _sha("b"),
                "platform_matrix": _sha("c"),
                "component_effect_matrix": _sha("d"),
            },
            "capabilities": capabilities,
            "status": "passed",
        }
    }


def capability(record: dict[str, Any], capability_id: str) -> dict[str, Any]:
    rows = record["task_ui_skill_pipeline"]["capabilities"]
    return next(row for row in rows if row["capability_id"] == capability_id)


class TaskUiSkillPipelineTest(unittest.TestCase):
    def test_native_evidenced_fallback_passes(self) -> None:
        self.assertTrue(validate_task_ui_skill_pipeline(make_record())["ok"])

    def test_missing_capability_provider_blocks(self) -> None:
        record = make_record()
        capability(record, "visual_quality_audit").pop("selected_provider")
        result = validate_task_ui_skill_pipeline(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "task_ui_skill_capability_missing" for error in result["errors"])
        )

    def test_final_review_cannot_mutate(self) -> None:
        record = make_record()
        provider = capability(record, "final_design_review")["selected_provider"]
        provider["mutation_authorization"] = "write"
        result = validate_task_ui_skill_pipeline(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "task_ui_skill_invocation_unsafe" for error in result["errors"])
        )

    def test_gsap_requires_web_stack(self) -> None:
        record = make_record()
        row = capability(record, "advanced_motion_authoring")
        row["condition_status"] = "applicable"
        row["selected_provider"] = {
            **capability(record, "visual_quality_audit")["selected_provider"],
            "provider_id": "gsap-core",
            "mutation_policy": "review_only",
        }
        record["task_ui_skill_pipeline"]["advanced_motion_required"] = True
        result = validate_task_ui_skill_pipeline(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "task_ui_skill_invocation_unsafe" for error in result["errors"])
        )

    def test_apple_design_requires_apple_platform(self) -> None:
        record = make_record()
        record["task_ui_skill_pipeline"]["platform_ids"] = ["android"]
        provider = capability(record, "platform_design_guidance")["selected_provider"]
        provider["provider_id"] = "apple-design"
        result = validate_task_ui_skill_pipeline(record)
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
