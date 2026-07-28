#!/usr/bin/env python3
"""Tests for lint_quality_gate_run.py (static hygiene evidence)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_quality_gate_run.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_quality_gate_run", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _pw(
    *,
    full_gate: list[str] | None = None,
    lint: list[str] | None = None,
    format_check: list[str] | None = None,
    type_or_static_check: list[str] | None = None,
    layer_a_scope: str = "full",
) -> dict:
    gates: dict = {"layer_a_scope": layer_a_scope}
    if full_gate is not None:
        gates["full_gate"] = full_gate
    if lint is not None:
        gates["lint"] = lint
    if format_check is not None:
        gates["format_check"] = format_check
    if type_or_static_check is not None:
        gates["type_or_static_check"] = type_or_static_check
    return {"engineering": {"quality_gates": gates}}


def _run(**overrides):
    base = {
        "schema": "granoflow_quality_gate_run_v1",
        "contract_loaded": True,
        "for_stage": "layer_b",
        "source": "full_gate",
        "commands": ["flutter analyze"],
        "scope": "full",
        "exit_code": 0,
        "issue_count": 0,
        "summary": "0 issues",
        "ran_at": "2026-07-28T03:00:00Z",
    }
    base.update(overrides)
    return {"quality_gate_run": base}


class LintQualityGateRunTests(unittest.TestCase):
    def test_require_configured_full_gate_ok(self) -> None:
        result = MOD.lint_quality_gate_run(
            None,
            project_work=_pw(full_gate=["npm run check"]),
            require_configured=True,
        )
        self.assertTrue(result["ok"], result)

    def test_require_configured_empty_fails(self) -> None:
        result = MOD.lint_quality_gate_run(
            None,
            project_work=_pw(),
            require_configured=True,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("quality_gates_unconfigured", codes)

    def test_composed_requires_static_slot(self) -> None:
        result = MOD.resolve_hygiene_commands(
            _pw(lint=["eslint ."], format_check=["prettier --check ."])
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("quality_gates_unconfigured", codes)

    def test_layer_b_green_ok(self) -> None:
        pw = _pw(full_gate=["flutter analyze"])
        result = MOD.lint_quality_gate_run(
            _run(),
            expect_stage="layer_b",
            project_work=pw,
        )
        self.assertTrue(result["ok"], result)

    def test_issue_count_nonzero_fails(self) -> None:
        pw = _pw(full_gate=["flutter analyze"])
        result = MOD.lint_quality_gate_run(
            _run(issue_count=48),
            expect_stage="layer_b",
            project_work=pw,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("static_quality_gate_failed", codes)

    def test_exit_nonzero_fails(self) -> None:
        pw = _pw(full_gate=["flutter analyze"])
        result = MOD.lint_quality_gate_run(
            _run(exit_code=1),
            expect_stage="layer_b",
            project_work=pw,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("static_quality_gate_failed", codes)

    def test_layer_b_task_owned_fails(self) -> None:
        pw = _pw(full_gate=["flutter analyze"])
        result = MOD.lint_quality_gate_run(
            _run(scope="task_owned"),
            expect_stage="layer_b",
            project_work=pw,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("static_quality_gate_scope_invalid", codes)

    def test_layer_a_task_owned_requires_pw(self) -> None:
        pw = _pw(full_gate=["flutter analyze"], layer_a_scope="full")
        result = MOD.lint_quality_gate_run(
            _run(for_stage="layer_a", scope="task_owned"),
            expect_stage="layer_a",
            project_work=pw,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("static_quality_gate_scope_invalid", codes)

    def test_layer_a_task_owned_ok_when_pw_allows(self) -> None:
        pw = _pw(full_gate=["flutter analyze"], layer_a_scope="task_owned")
        result = MOD.lint_quality_gate_run(
            _run(for_stage="layer_a", scope="task_owned"),
            expect_stage="layer_a",
            project_work=pw,
        )
        self.assertTrue(result["ok"], result)

    def test_commands_mismatch_fails(self) -> None:
        pw = _pw(full_gate=["flutter analyze"])
        result = MOD.lint_quality_gate_run(
            _run(commands=["dart analyze"]),
            expect_stage="layer_b",
            project_work=pw,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("static_quality_gate_commands_mismatch", codes)

    def test_missing_run_skipped(self) -> None:
        result = MOD.lint_quality_gate_run({"other": True})
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("static_quality_gate_skipped", codes)

    def test_analyzer_debt_residual_forbidden(self) -> None:
        pw = _pw(full_gate=["flutter analyze"])
        result = MOD.lint_quality_gate_run(
            _run(
                residual={
                    "class": "deferred_cleanup",
                    "basis": "fix warnings later",
                }
            ),
            expect_stage="layer_b",
            project_work=pw,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("static_quality_gate_failed", codes)


if __name__ == "__main__":
    unittest.main()
