#!/usr/bin/env python3
"""Tests for lint_stack_realization_notes.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_stack_realization_notes.py"
)
SHA = "a" * 64
SHA_B = "b" * 64


def load_module():
    spec = importlib.util.spec_from_file_location("lint_stack_realization_notes", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def base_notes(*, disposition: str = "native_supported", note: str | None = None) -> dict:
    row: dict = {
        "role": "bottom_nav",
        "candidate_id": "c1",
        "html_surface": "bottom tab bar with three destinations",
        "stack_realization": "Flutter NavigationBar",
        "disposition": disposition,
        "fallback_or_schematic_note": note,
    }
    return {
        "stack_realization_notes": {
            "schema": "granoflow_stack_realization_notes_v1",
            "contract_loaded": True,
            "stack_id": "flutter",
            "platform_matrix_sha256": SHA,
            "component_effect_matrix_sha256": SHA_B,
            "rows": [row],
        }
    }


def base_matrix(*, selected: bool = True) -> dict:
    return {
        "ui_component_effect_matrix": {
            "schema": "ui_component_effect_matrix_v1",
            "candidates": [
                {
                    "candidate_id": "c1",
                    "role": "bottom_nav",
                    "decision": "selected" if selected else "rejected",
                }
            ],
        }
    }


class LintStackRealizationNotesTests(unittest.TestCase):
    def test_structure_ok_without_matrix(self) -> None:
        result = MOD.lint_stack_realization_notes(base_notes())
        self.assertTrue(result["ok"], result)

    def test_matrix_coverage_ok(self) -> None:
        result = MOD.lint_stack_realization_notes(
            base_notes(),
            matrix_data=base_matrix(),
        )
        self.assertTrue(result["ok"], result)

    def test_missing_selected_coverage_fails(self) -> None:
        notes = base_notes()
        notes["stack_realization_notes"]["rows"][0]["role"] = "other_role"
        result = MOD.lint_stack_realization_notes(notes, matrix_data=base_matrix())
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("stack_realization_notes_coverage_incomplete", codes)

    def test_enhancement_requires_note(self) -> None:
        result = MOD.lint_stack_realization_notes(
            base_notes(disposition="enhancement_schematic", note=None)
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("stack_realization_notes_incomplete", codes)

    def test_enhancement_with_note_ok(self) -> None:
        result = MOD.lint_stack_realization_notes(
            base_notes(
                disposition="enhancement_schematic",
                note="【增强实现】 blur approximated; ship solid AppBar",
            )
        )
        self.assertTrue(result["ok"], result)

    def test_invalid_disposition_fails(self) -> None:
        result = MOD.lint_stack_realization_notes(base_notes(disposition="magic"))
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("stack_realization_notes_disposition_invalid", codes)

    def test_missing_notes_fails(self) -> None:
        result = MOD.lint_stack_realization_notes({"prototype_option_set": {}})
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "stack_realization_notes_required")

    def test_extra_notes_without_selected_fails(self) -> None:
        notes = base_notes()
        notes["stack_realization_notes"]["rows"].append(
            {
                "role": "orphan",
                "candidate_id": "c9",
                "html_surface": "x",
                "stack_realization": "y",
                "disposition": "native_supported",
                "fallback_or_schematic_note": None,
            }
        )
        result = MOD.lint_stack_realization_notes(notes, matrix_data=base_matrix())
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("stack_realization_notes_coverage_incomplete", codes)

    def test_cli_with_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            notes_path = Path(tmp) / "notes.json"
            matrix_path = Path(tmp) / "matrix.json"
            notes_path.write_text(json.dumps(base_notes()), encoding="utf-8")
            matrix_path.write_text(json.dumps(base_matrix()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(notes_path), "--matrix", str(matrix_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
