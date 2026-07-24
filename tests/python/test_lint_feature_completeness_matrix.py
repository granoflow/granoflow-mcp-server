#!/usr/bin/env python3
"""Tests for lint_feature_completeness_matrix.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_feature_completeness_matrix.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_feature_completeness_matrix", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _row(**overrides):
    base = {
        "id": "FCM-001",
        "sot_ref": "R-001",
        "task_local_key": "T1",
        "task_id": None,
        "impl_status": "implemented",
        "test_ref": "tests/test_r001.py",
        "result": "green",
    }
    base.update(overrides)
    return base


def _matrix(**overrides):
    base = {
        "schema": "granoflow_feature_completeness_matrix_v1",
        "status": "green",
        "fail_closed_code": "feature_completeness_matrix_incomplete",
        "rows": [_row()],
    }
    base.update(overrides)
    return base


def _doc(matrix=None, tasks=None):
    doc = {
        "feature_completeness_matrix": matrix if matrix is not None else _matrix(),
    }
    if tasks is not None:
        doc["task_plan"] = {"status": "passed", "tasks": tasks}
    return doc


class LintFeatureCompletenessMatrixTests(unittest.TestCase):
    def test_missing_matrix(self) -> None:
        result = MOD.lint_matrix({}, require_present=True)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("feature_completeness_matrix_missing", codes)

    def test_green_ok(self) -> None:
        result = MOD.lint_matrix(
            _doc(
                tasks=[
                    {
                        "local_key": "T1",
                        "feature_completeness_row_ids": ["FCM-001"],
                    }
                ]
            ),
            expect_min_status="green",
        )
        self.assertTrue(result["ok"], result)

    def test_pending_claiming_green(self) -> None:
        m = _matrix(
            status="green",
            rows=[_row(impl_status="pending", test_ref=None, result="pending")],
        )
        result = MOD.lint_matrix(m, expect_min_status="green")
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("feature_completeness_overclaim_green", codes)

    def test_functional_stub_impl_status(self) -> None:
        m = _matrix(rows=[_row(impl_status="stub", test_ref=None, result="pending")])
        result = MOD.lint_matrix(m, expect_min_status="ready")
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("functional_residual_forbidden", codes)

    def test_deferral_copy_in_prose(self) -> None:
        result = MOD.lint_matrix(
            _matrix(status="ready", rows=[_row(impl_status="pending", result="pending")]),
            expect_min_status="ready",
            prose_blobs=["设置页外观将在后续版本提供。"],
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("functional_residual_forbidden", codes)

    def test_whitelist_error_state_not_forbidden(self) -> None:
        result = MOD.lint_matrix(
            _doc(
                matrix=_matrix(),
                tasks=[
                    {
                        "local_key": "T1",
                        "feature_completeness_row_ids": ["FCM-001"],
                    }
                ],
            ),
            expect_min_status="green",
            prose_blobs=["该文件暂时无法打开，请检查权限。"],
        )
        self.assertTrue(result["ok"], result)

    def test_blocked_external_path_ok(self) -> None:
        m = _matrix(
            status="blocked",
            rows=[
                _row(
                    impl_status="blocked_external",
                    test_ref=None,
                    result="blocked_external",
                )
            ],
        )
        result = MOD.lint_matrix(
            _doc(
                matrix=m,
                tasks=[
                    {
                        "local_key": "T1",
                        "feature_completeness_row_ids": ["FCM-001"],
                    }
                ],
            ),
            expect_min_status="green",
        )
        self.assertTrue(result["ok"], result)

    def test_ready_rejects_draft(self) -> None:
        m = _matrix(
            status="draft",
            rows=[_row(impl_status="pending", test_ref=None, result="pending")],
        )
        result = MOD.lint_matrix(m, expect_min_status="ready")
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("feature_completeness_matrix_incomplete", codes)

    def test_empty_shell_task_fails(self) -> None:
        result = MOD.lint_matrix(
            _doc(
                matrix=_matrix(status="ready"),
                tasks=[{"local_key": "T1", "feature_completeness_row_ids": []}],
            ),
            expect_min_status="ready",
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("feature_completeness_matrix_incomplete", codes)

    def test_implemented_requires_test_ref(self) -> None:
        m = _matrix(rows=[_row(test_ref="", result="green")])
        result = MOD.lint_matrix(m, expect_min_status="green")
        self.assertFalse(result["ok"])
        details = " ".join(e["detail"] for e in result["errors"])
        self.assertIn("test_ref", details)


if __name__ == "__main__":
    unittest.main()
