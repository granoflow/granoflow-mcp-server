#!/usr/bin/env python3
"""Tests for lint_plan_case_implementation.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_plan_case_implementation.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_plan_case_implementation", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def source_cases() -> dict[str, Any]:
    return {
        "schema": "granoflow_plan_verification_cases_v1",
        "cases": [
            {"case_id": "U1", "lane": "unit"},
            {"case_id": "I1", "lane": "integration"},
            {"case_id": "E1", "lane": "e2e"},
        ],
    }


def ok_ledger(**overrides: Any) -> dict[str, Any]:
    block: dict[str, Any] = {
        "schema": "granoflow_plan_case_implementation_v1",
        "contract_loaded": True,
        "status": "complete",
        "cases": [
            {
                "case_id": "U1",
                "lane": "unit",
                "status": "implemented",
                "test_ref": "test/open_library_test.dart",
                "evidence": "flutter test test/open_library_test.dart # U1",
                "campaign_ref": None,
            },
            {
                "case_id": "I1",
                "lane": "integration",
                "status": "scheduled_campaign",
                "test_ref": "test/integration/open_flow_test.dart",
                "evidence": "authored for milestone IT",
                "campaign_ref": "milestone_it_suite",
            },
            {
                "case_id": "E1",
                "lane": "e2e",
                "status": "scheduled_campaign",
                "test_ref": "integration_test/open_journey_test.dart",
                "evidence": "authored for e2e_campaign",
                "campaign_ref": "e2e_campaign",
            },
        ],
    }
    block.update(overrides)
    return {"plan_case_implementation": block}


class LintPlanCaseImplementationTests(unittest.TestCase):
    def test_layer_a_ok_with_existing_test_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test" / "open_library_test.dart"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("// case U1\nvoid main() {}", encoding="utf-8")
            result = MOD.lint_plan_case_implementation(
                ok_ledger(),
                source_cases(),
                gate="layer_a",
                workspace=root,
            )
            self.assertTrue(result["ok"], result)

    def test_missing_ledger_row_fails(self) -> None:
        ledger = ok_ledger()
        ledger["plan_case_implementation"]["cases"] = [
            c for c in ledger["plan_case_implementation"]["cases"] if c["case_id"] != "U1"
        ]
        result = MOD.lint_plan_case_implementation(ledger, source_cases(), gate="layer_a")
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "plan_case_implementation_gap")

    def test_unit_without_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = MOD.lint_plan_case_implementation(
                ok_ledger(),
                source_cases(),
                gate="layer_a",
                workspace=Path(tmp),
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "plan_case_test_ref_missing")

    def test_unit_file_without_case_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test" / "open_library_test.dart"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("void main() {}", encoding="utf-8")
            ledger = ok_ledger()
            ledger["plan_case_implementation"]["cases"][0]["evidence"] = "ran tests"
            result = MOD.lint_plan_case_implementation(
                ledger, source_cases(), gate="layer_a", workspace=root
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "plan_case_test_ref_unbound")

    def test_layer_b_requires_integration_executed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test" / "open_library_test.dart"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("// U1\n", encoding="utf-8")
            result = MOD.lint_plan_case_implementation(
                ok_ledger(),
                source_cases(),
                gate="layer_b",
                workspace=root,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "plan_case_implementation_gap")

    def test_layer_b_ok_when_integration_executed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test" / "open_library_test.dart"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("// U1\n", encoding="utf-8")
            ledger = ok_ledger()
            for row in ledger["plan_case_implementation"]["cases"]:
                if row["case_id"] == "I1":
                    row["status"] = "executed"
                    row["evidence"] = "milestone IT green for I1"
            result = MOD.lint_plan_case_implementation(
                ledger, source_cases(), gate="layer_b", workspace=root
            )
            self.assertTrue(result["ok"], result)

    def test_e2e_campaign_requires_e2e_executed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test" / "open_library_test.dart"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("// U1\n", encoding="utf-8")
            ledger = ok_ledger()
            for row in ledger["plan_case_implementation"]["cases"]:
                if row["case_id"] == "I1":
                    row["status"] = "executed"
                    row["evidence"] = "I1 green"
            result = MOD.lint_plan_case_implementation(
                ledger, source_cases(), gate="e2e_campaign", workspace=root
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "plan_case_implementation_gap")

    def test_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test" / "open_library_test.dart"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("// U1\n", encoding="utf-8")
            ledger_path = root / "ledger.json"
            cases_path = root / "cases.json"
            ledger_path.write_text(json.dumps(ok_ledger()), encoding="utf-8")
            cases_path.write_text(json.dumps(source_cases()), encoding="utf-8")
            code = MOD.main(
                [
                    "--ledger",
                    str(ledger_path),
                    "--cases",
                    str(cases_path),
                    "--gate",
                    "layer_a",
                    "--workspace",
                    str(root),
                ]
            )
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
