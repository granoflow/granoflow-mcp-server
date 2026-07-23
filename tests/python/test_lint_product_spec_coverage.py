#!/usr/bin/env python3
"""Tests for lint_product_spec_coverage.py."""

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
    ROOT / "skills" / "granoflow-project-definition" / "scripts" / "lint_product_spec_coverage.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_product_spec_coverage", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def ready_coverage(**overrides):
    base = {
        "status": "ready",
        "screen_detail_registration": {
            "status": "adopted",
            "design_truth_priority": [
                "user_confirmed",
                "from_product_doc",
                "from_user_story",
                "inferred",
                "ai_live_inference",
            ],
            "init_html_policy": "design_spec_and_shell_only",
            "per_screen_hifi_phase": "task_analysis_ui_prototype",
            "missing_screen_fill_phase": "milestone_or_task_decomposition",
        },
        "screen_coverage": [],
        "journey_coverage": [
            {
                "journey_id": "J-001",
                "disposition": "adopted",
                "requirement_ids": ["R-001"],
                "acceptance_ids": ["A1"],
                "screen_ids": ["S-confirm", "S-progress", "S-result"],
                "decomposition": {
                    "pass_completed": True,
                    "operation_flow": {
                        "summary": "Confirm batch → wait progress → review result",
                        "user_operations": [
                            "confirm_batch",
                            "await_progress",
                            "review_result",
                        ],
                        "parallel_groups": [],
                    },
                    "serial_gates": [
                        "after_confirm_before_progress",
                        "after_progress_before_result",
                    ],
                    "parallel_ops_ok": False,
                    "candidate_screens": [
                        "S-confirm",
                        "S-progress",
                        "S-result",
                    ],
                    "conclusion": "split",
                    "concluded_screen_ids": [
                        "S-confirm",
                        "S-progress",
                        "S-result",
                    ],
                    "accepted_split_summary": (
                        "Serial gates: confirm, wait, and result are distinct pages."
                    ),
                    "rejected_split_summary": None,
                },
                "stress_paths": [
                    {
                        "acceptance_id": "A1",
                        "entry": "Open import from shelf",
                        "intermediate": ["Confirm batch", "Watch progress"],
                        "success_exit": "Result shows imported count",
                        "failure_exit": "Result shows failures + report CTA",
                    }
                ],
            }
        ],
        "gap_fills": [],
        "checklist": {
            "every_adopted_journey_decomposition_pass_completed": True,
            "every_adopted_journey_has_decomposition_conclusion": True,
            "every_adopted_acceptance_has_stress_path": True,
            "no_unattended_decision_changing_thin_gap_auto_accept": True,
            "screen_detail_registration_adopted": True,
        },
    }
    base.update(overrides)
    return base


class LintProductSpecCoverageTests(unittest.TestCase):
    def test_ready_split_ok(self) -> None:
        result = MOD.lint_coverage(ready_coverage())
        self.assertTrue(result["ok"], result)

    def test_keep_cohesive_parallel_ops_ok(self) -> None:
        cov = ready_coverage()
        journey = cov["journey_coverage"][0]
        journey["decomposition"] = {
            "pass_completed": True,
            "operation_flow": {
                "summary": "Fill title and author then save once",
                "user_operations": ["edit_title", "edit_author", "save"],
                "parallel_groups": [["edit_title", "edit_author"]],
            },
            "serial_gates": [],
            "parallel_ops_ok": True,
            "candidate_screens": ["S-edit", "S-edit-confirm-only"],
            "conclusion": "keep_cohesive",
            "concluded_screen_ids": ["S-edit"],
            "accepted_split_summary": None,
            "rejected_split_summary": (
                "Rejected separate confirm page; fields are concurrent with one save."
            ),
        }
        journey["screen_ids"] = ["S-edit"]
        result = MOD.lint_coverage(cov)
        self.assertTrue(result["ok"], result)

    def test_keep_cohesive_requires_rejected_split(self) -> None:
        cov = ready_coverage()
        journey = cov["journey_coverage"][0]
        journey["decomposition"] = {
            "pass_completed": True,
            "operation_flow": {
                "summary": "Toggle setting",
                "user_operations": ["toggle"],
                "parallel_groups": [],
            },
            "serial_gates": [],
            "parallel_ops_ok": True,
            "candidate_screens": ["S-settings", "S-settings-advanced"],
            "conclusion": "keep_cohesive",
            "concluded_screen_ids": ["S-settings"],
            "accepted_split_summary": None,
            "rejected_split_summary": None,
        }
        journey["screen_ids"] = ["S-settings"]
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("flow_decomposition_keep_without_rejected_split", codes)

    def test_keep_with_serial_gates_fails(self) -> None:
        cov = ready_coverage()
        journey = cov["journey_coverage"][0]
        journey["decomposition"]["conclusion"] = "keep_cohesive"
        journey["decomposition"]["rejected_split_summary"] = "would keep"
        journey["decomposition"]["accepted_split_summary"] = None
        journey["decomposition"]["concluded_screen_ids"] = ["S-confirm"]
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("flow_decomposition_keep_with_serial_gates", codes)

    def test_split_without_serial_gate_fails(self) -> None:
        cov = ready_coverage()
        journey = cov["journey_coverage"][0]
        journey["decomposition"]["serial_gates"] = []
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("flow_decomposition_split_without_serial_gate", codes)

    def test_missing_operation_flow_fails(self) -> None:
        cov = ready_coverage()
        del cov["journey_coverage"][0]["decomposition"]["operation_flow"]
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("flow_decomposition_operation_flow_missing", codes)

    def test_missing_pass_fails(self) -> None:
        cov = ready_coverage()
        del cov["journey_coverage"][0]["decomposition"]
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("flow_decomposition_pass_missing", codes)

    def test_missing_stress_path_fails(self) -> None:
        cov = ready_coverage()
        cov["journey_coverage"][0]["stress_paths"] = []
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("journey_stress_path_incomplete", codes)

    def test_unattended_decision_changing_auto_adopt_forbidden(self) -> None:
        cov = ready_coverage(
            gap_fills=[
                {
                    "gap_id": "G-1",
                    "decision_changing": True,
                    "mode": "unattended",
                    "provenance": "agent_recommendation_adopted",
                }
            ]
        )
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("thin_product_doc_gap_requires_user", codes)

    def test_out_of_scope_skips_decomposition(self) -> None:
        cov = ready_coverage()
        cov["journey_coverage"][0]["disposition"] = "out_of_scope"
        del cov["journey_coverage"][0]["decomposition"]
        cov["journey_coverage"][0]["stress_paths"] = []
        cov["status"] = "incomplete"
        result = MOD.lint_coverage(cov)
        self.assertTrue(result["ok"], result)

    def test_cli_fail_closed(self) -> None:
        bad = ready_coverage()
        del bad["journey_coverage"][0]["decomposition"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            path.write_text(json.dumps({"product_spec_coverage": bad}), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(payload["ok"])

    def test_cli_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            path.write_text(
                json.dumps({"product_spec_coverage": ready_coverage()}),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(payload["ok"])

    def test_ready_requires_screen_detail_registration(self) -> None:
        cov = ready_coverage()
        del cov["screen_detail_registration"]
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("screen_detail_registration_missing", codes)

    def test_ui_details_invalid_source_fails(self) -> None:
        cov = ready_coverage(
            screen_coverage=[
                {
                    "screen_id": "S-reader",
                    "disposition": "adopted",
                    "ui_details": [
                        {
                            "detail_id": "bottom_bar",
                            "statement": "Reader has a bottom action bar",
                            "source": "ai_guess",
                        }
                    ],
                }
            ]
        )
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("screen_ui_details_source_invalid", codes)

    def test_ui_details_valid_source_ok(self) -> None:
        cov = ready_coverage(
            screen_coverage=[
                {
                    "screen_id": "S-reader",
                    "disposition": "adopted",
                    "ui_details": [
                        {
                            "detail_id": "bottom_bar",
                            "statement": "Reader has a bottom action bar",
                            "source": "from_product_doc",
                            "source_ref": "docs/product.md#reader",
                        }
                    ],
                }
            ]
        )
        result = MOD.lint_coverage(cov)
        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
