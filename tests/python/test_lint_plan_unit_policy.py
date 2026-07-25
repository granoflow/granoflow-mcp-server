#!/usr/bin/env python3
"""Tests for lint_plan_unit_policy.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_plan_unit_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_plan_unit_policy", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def operations() -> dict[str, Any]:
    return {
        "screen_content_contract": {
            "screens": [
                {
                    "interaction_mode": "interactive",
                    "actions": [
                        {
                            "action_id": "open.submit",
                            "label": "打开",
                            "result": "library_open",
                            "failure_behavior": "retry",
                            "preconditions": [],
                        },
                        {
                            "action_id": "open.cancel",
                            "label": "取消",
                            "result": "dismiss",
                            "failure_behavior": "none",
                            "preconditions": [],
                        },
                    ],
                }
            ]
        }
    }


def ok_cases(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "schema": "granoflow_plan_verification_cases_v1",
        "cases": [
            {
                "case_id": "U-submit",
                "lane": "unit",
                "operation_id": "open.submit",
                "asserts": "behavior",
                "test_ref": "test/open_submit_test.dart",
            },
            {
                "case_id": "U-cancel",
                "lane": "unit",
                "operation_id": "open.cancel",
                "asserts": "behavior",
                "test_ref": "test/open_cancel_test.dart",
            },
            {
                "case_id": "I1",
                "lane": "integration",
                "operation_id": "open.submit",
                "asserts": "behavior",
            },
        ],
    }
    data.update(overrides)
    return data


class LintPlanUnitPolicyTests(unittest.TestCase):
    def test_ok_covers_all_operations(self) -> None:
        result = MOD.lint_plan_unit_policy(ok_cases(), operations())
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["covered_operation_count"], 2)

    def test_copy_presence_forbidden(self) -> None:
        cases = ok_cases()
        cases["cases"][0]["asserts"] = "copy_presence"
        result = MOD.lint_plan_unit_policy(cases, operations())
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "unit_copy_assertion_forbidden")

    def test_missing_operation_coverage(self) -> None:
        cases = ok_cases()
        cases["cases"] = [cases["cases"][0]]  # only submit
        result = MOD.lint_plan_unit_policy(cases, operations())
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "unit_operation_coverage_incomplete")

    def test_unit_without_operation_id(self) -> None:
        cases = ok_cases()
        del cases["cases"][0]["operation_id"]
        result = MOD.lint_plan_unit_policy(cases, operations())
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "unit_operation_coverage_incomplete")

    def test_scan_forbids_find_text_unit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = root / "test" / "open_submit_test.dart"
            bad = root / "test" / "open_cancel_test.dart"
            good.parent.mkdir(parents=True)
            good.write_text(
                "void main() { when(repo.open()).thenReturn(ok); verify(repo.open()); }\n",
                encoding="utf-8",
            )
            bad.write_text(
                "void main() { expect(find.text('取消'), findsOneWidget); }\n",
                encoding="utf-8",
            )
            result = MOD.lint_plan_unit_policy(
                ok_cases(),
                operations(),
                workspace=root,
                scan_tests=True,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "unit_copy_assertion_forbidden")

    def test_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases_path = root / "cases.json"
            ops_path = root / "ops.json"
            cases_path.write_text(json.dumps(ok_cases()), encoding="utf-8")
            ops_path.write_text(json.dumps(operations()), encoding="utf-8")
            code = MOD.main(["--cases", str(cases_path), "--operations", str(ops_path)])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
