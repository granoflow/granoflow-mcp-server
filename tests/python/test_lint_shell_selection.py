#!/usr/bin/env python3
"""Tests for App Shell orientation and Widget Catalog coverage."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-project-definition" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_shell_selection import validate_shell_selection  # noqa: E402


def _sha(character: str) -> str:
    return character * 64


def make_record() -> dict[str, Any]:
    requirements = [
        {"platform_id": "ios", "orientations": ["portrait", "landscape"]},
        {"platform_id": "macos", "orientations": ["landscape"]},
    ]
    layouts = [
        {
            "platform_id": row["platform_id"],
            "orientation": orientation,
            "top_bar_widget_id": "app-shell-top-bar",
            "bottom_navigation_widget_id": "app-shell-bottom-navigation",
        }
        for row in requirements
        for orientation in row["orientations"]
    ]
    candidates = [
        {
            "option_id": f"shell_{letter}",
            "fitted_to_design_spec_option_id": "spec_a",
            "artifact_ref": f"prototype://shell-{letter}.html",
            "artifact_sha256": _sha(str(index + 1)),
            "layouts": layouts,
        }
        for index, letter in enumerate("abc")
    ]
    selected = candidates[0]
    widgets = [
        {
            "role": role,
            "widget_id": widget_id,
            "derived_from_sha256": selected["artifact_sha256"],
            "variants": [
                {
                    "platform_id": layout["platform_id"],
                    "orientation": layout["orientation"],
                }
                for layout in layouts
            ],
        }
        for role, widget_id in (
            ("app_shell.top_bar", "app-shell-top-bar"),
            ("app_shell.bottom_navigation", "app-shell-bottom-navigation"),
        )
    ]
    return {
        "shell_selection": {
            "schema": "granoflow_shell_selection_v2",
            "mode": "interactive_triad",
            "required_layout_families": requirements,
            "candidates": candidates,
            "selected_option_id": selected["option_id"],
            "widget_catalog_projection": {
                "status": "passed",
                "source_shell_artifact_sha256": selected["artifact_sha256"],
                "widgets": widgets,
            },
        }
    }


class ShellSelectionTest(unittest.TestCase):
    def test_required_orientations_and_widget_projection_pass(self) -> None:
        self.assertTrue(validate_shell_selection(make_record())["ok"])

    def test_missing_required_orientation_fails(self) -> None:
        record = make_record()
        record["shell_selection"]["candidates"][1]["layouts"].pop()
        result = validate_shell_selection(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "shell_required_layout_missing" for error in result["errors"])
        )

    def test_each_layout_requires_both_bars(self) -> None:
        record = make_record()
        layout = record["shell_selection"]["candidates"][0]["layouts"][0]
        layout["bottom_navigation_widget_id"] = None
        result = validate_shell_selection(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "shell_bottom_navigation_missing" for error in result["errors"])
        )

    def test_projection_requires_all_variants(self) -> None:
        record = make_record()
        projection = record["shell_selection"]["widget_catalog_projection"]
        projection["widgets"][0]["variants"].pop()
        result = validate_shell_selection(record)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "shell_widget_catalog_projection_invalid"
                for error in result["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
