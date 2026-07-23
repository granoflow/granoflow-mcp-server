#!/usr/bin/env python3
"""Tests for lint_implementation_design_fidelity.py."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_implementation_design_fidelity.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_implementation_design_fidelity", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _matched_ledger(**overrides):
    base = {
        "schema": "granoflow_impl_design_fidelity_v1",
        "contract_loaded": True,
        "status": "complete",
        "declaration_emitted": True,
        "decision": "matched_all",
        "axes": {
            "data_structures": {"status": "matched"},
            "flowcharts": {"status": "matched"},
            "uml_diagrams": {"status": "not_applicable", "basis": "no_uml_in_plan"},
            "modular_split": {"status": "matched"},
        },
        "design_writeback": {"status": "not_applicable", "slots_updated": []},
    }
    base.update(overrides)
    return base


class LintTests(unittest.TestCase):
    def test_matched_ok(self) -> None:
        result = MOD.lint_ledger(_matched_ledger())
        self.assertTrue(result["ok"], result)

    def test_needs_split_fails(self) -> None:
        ledger = _matched_ledger()
        ledger["axes"]["modular_split"] = {"status": "needs_split"}
        result = MOD.lint_ledger(ledger)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("impl_design_modular_split_unresolved", codes)

    def test_keep_requires_rationale_and_writeback(self) -> None:
        ledger = _matched_ledger(
            decision="keep_with_design_writeback",
            better_rationale="",
            diffs=[{"axis": "flowcharts", "summary": "x", "design_ref": "a", "impl_ref": "b"}],
        )
        ledger["axes"]["flowcharts"] = {"status": "diverged"}
        ledger["design_writeback"] = {"status": "pending", "slots_updated": []}
        result = MOD.lint_ledger(ledger)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("impl_design_better_rationale_missing", codes)
        self.assertIn("impl_design_writeback_missing", codes)

    def test_keep_ok_with_writeback(self) -> None:
        ledger = _matched_ledger(
            decision="keep_with_design_writeback",
            better_rationale="Clearer state machine; fewer edge bugs.",
            diffs=[{"axis": "flowcharts", "summary": "x", "design_ref": "a", "impl_ref": "b"}],
            design_writeback={
                "status": "written_and_read_back",
                "slots_updated": ["task_work_execution", "milestone_plan_acceptance_pack"],
                "content_sha256": "abc",
            },
        )
        ledger["axes"]["flowcharts"] = {"status": "diverged"}
        result = MOD.lint_ledger(ledger)
        self.assertTrue(result["ok"], result)

    def test_file_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.yaml"
            path.write_text(
                "schema: granoflow_impl_design_fidelity_v1\n"
                "contract_loaded: true\n"
                "status: not_applicable\n",
                encoding="utf-8",
            )
            result = MOD.lint_ledger(MOD._load(path))
        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
