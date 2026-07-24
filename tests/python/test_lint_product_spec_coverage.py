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
GRANOREADER_FIXTURE = ROOT / "tests/python/fixtures/granoreader_requirement_integrity.json"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_product_spec_coverage", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def attach_integrity_contracts(coverage: dict) -> None:
    ledger = {
        "schema": "granoflow_source_fact_ledger_v1",
        "facts": [
            {
                "fact_id": "F-001",
                "statement": "User confirms an import and sees its result.",
                "source_ref": "product://import",
                "source_locator": "docs/product.md#import",
                "subject": "user",
                "action": "imports",
                "object": "books",
                "conditions": [],
                "expected_outcomes": ["import result is visible"],
                "failure_outcomes": ["failed items are visible"],
                "platforms": ["macos"],
                "source_kind": "user_stated",
                "disposition": "adopted",
            }
        ],
    }
    ledger_digest = MOD.canonical_source_fact_ledger_sha256(ledger)
    ledger["review"] = {
        "author_id": "project-author",
        "reviewer_id": "product-reviewer",
        "status": "passed",
        "evidence_refs": ["review://source-facts"],
        "reviewed_ledger_sha256": ledger_digest,
    }
    ledger["ledger_sha256"] = ledger_digest
    ledger["status"] = "passed"
    coverage["source_fact_ledger"] = ledger

    traceability = {
        "schema": "granoflow_journey_step_traceability_v1",
        "source_fact_ledger_sha256": ledger_digest,
        "journeys": [
            {
                "journey_id": "J-001",
                "steps": [
                    {
                        "step_id": "J-001-entry",
                        "sequence": 1,
                        "step_type": "entry",
                        "entry_ref": "shelf import entry",
                        "actor": "user",
                        "action": "opens import",
                        "interaction_surface": "in_app_ui",
                        "platform_boundary": "none",
                        "expected_observation": "import confirmation is visible",
                        "source_fact_ids": ["F-001"],
                        "required_test_layers": ["e2e"],
                    },
                    {
                        "step_id": "J-001-action",
                        "sequence": 2,
                        "step_type": "action",
                        "control": "confirm import button",
                        "actor": "user",
                        "action": "confirms import",
                        "interaction_surface": "in_app_ui",
                        "platform_boundary": "none",
                        "expected_observation": "import starts",
                        "source_fact_ids": ["F-001"],
                        "required_test_layers": ["integration", "e2e"],
                    },
                    {
                        "step_id": "J-001-outcome",
                        "sequence": 3,
                        "step_type": "outcome",
                        "actor": "system",
                        "action": "shows imported count",
                        "interaction_surface": "in_app_ui",
                        "platform_boundary": "none",
                        "expected_observation": "result shows imported count",
                        "source_fact_ids": ["F-001"],
                        "required_test_layers": ["e2e"],
                    },
                    {
                        "step_id": "J-001-failure",
                        "sequence": 4,
                        "step_type": "failure",
                        "actor": "system",
                        "action": "shows failed items",
                        "interaction_surface": "in_app_ui",
                        "platform_boundary": "none",
                        "expected_observation": "failure report is visible",
                        "source_fact_ids": ["F-001"],
                        "required_test_layers": ["e2e"],
                    },
                ],
            }
        ],
        "semantic_replay": {
            "status": "passed",
            "missing_fact_ids": [],
            "distorted_fact_ids": [],
            "evidence_refs": ["review://semantic-replay"],
        },
    }
    trace_digest = MOD.canonical_journey_step_traceability_sha256(traceability)
    traceability["review"] = {
        "author_id": "project-author",
        "reviewer_id": "semantic-reviewer",
        "status": "passed",
        "evidence_refs": ["review://journey-steps"],
        "reviewed_traceability_sha256": trace_digest,
    }
    traceability["traceability_sha256"] = trace_digest
    traceability["status"] = "passed"
    coverage["journey_step_traceability"] = traceability

    background_control = {
        "schema": "granoflow_background_activity_control_v1",
        "source_fact_ledger_sha256": ledger_digest,
        "journey_step_traceability_sha256": trace_digest,
        "fact_classifications": [{"fact_id": "F-001", "role": "none"}],
        "activities": [],
        "semantic_replay": {
            "status": "passed",
            "missing_fact_ids": [],
            "unknown_fact_ids": [],
            "evidence_refs": ["review://background-activity-classification"],
        },
    }
    control_digest = MOD.canonical_background_activity_control_sha256(background_control)
    background_control["review"] = {
        "author_id": "project-author",
        "reviewer_id": "interaction-reviewer",
        "status": "passed",
        "evidence_refs": ["review://background-activity-control"],
        "reviewed_control_sha256": control_digest,
    }
    background_control["control_sha256"] = control_digest
    background_control["status"] = "passed"
    coverage["background_activity_control"] = background_control


def _refresh_background_control(coverage: dict) -> None:
    control = coverage["background_activity_control"]
    digest = MOD.canonical_background_activity_control_sha256(control)
    control["control_sha256"] = digest
    control["review"]["reviewed_control_sha256"] = digest


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
            "source_fact_ledger_reviewed": True,
            "every_adopted_fact_mapped": True,
            "every_adopted_journey_step_traced": True,
            "semantic_replay_passed": True,
            "every_adopted_fact_background_activity_classified": True,
            "background_activity_control_reviewed": True,
        },
    }
    base.update(overrides)
    if base.get("status") == "ready":
        attach_integrity_contracts(base)
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
        cov.pop("source_fact_ledger")
        cov.pop("journey_step_traceability")
        cov.pop("background_activity_control")
        result = MOD.lint_coverage(cov)
        self.assertTrue(result["ok"], result)

    def test_ready_requires_background_activity_classification(self) -> None:
        cov = ready_coverage()
        del cov["background_activity_control"]
        result = MOD.lint_coverage(cov)
        self.assertFalse(result["ok"])
        self.assertIn(
            "background_activity_fact_unclassified",
            {hit["code"] for hit in result["hits"]},
        )

    def test_background_activity_requires_write_scope_exit_and_test_layers(self) -> None:
        cov = ready_coverage()
        control = cov["background_activity_control"]
        control["fact_classifications"][0]["role"] = "background_update"
        control["activities"] = [
            {
                "activity_id": "BA-sync",
                "continues_after_user_action": True,
                "user_visible": True,
                "source_fact_ids": ["F-001"],
                "journey_step_ids": ["J-001-action"],
                "background_events": ["progress update"],
                "allowed_background_changes": ["progress"],
                "must_not_change": ["active panel"],
                "controls_that_must_keep_working": ["global navigation"],
                "ways_to_exit": [],
                "required_test_layers": ["e2e"],
            }
        ]
        _refresh_background_control(cov)
        result = MOD.lint_coverage(cov)
        codes = {hit["code"] for hit in result["hits"]}
        self.assertIn("background_activity_exit_missing", codes)
        self.assertIn("component_path_required", codes)

    def test_background_activity_with_disjoint_scope_and_exit_passes(self) -> None:
        cov = ready_coverage()
        control = cov["background_activity_control"]
        control["fact_classifications"][0]["role"] = "background_update"
        control["activities"] = [
            {
                "activity_id": "BA-sync",
                "continues_after_user_action": True,
                "user_visible": True,
                "source_fact_ids": ["F-001"],
                "journey_step_ids": ["J-001-action"],
                "background_events": ["progress update"],
                "allowed_background_changes": ["progress"],
                "must_not_change": ["active panel", "input focus"],
                "controls_that_must_keep_working": ["global navigation"],
                "ways_to_exit": ["cancel"],
                "required_test_layers": ["integration", "e2e"],
            }
        ]
        _refresh_background_control(cov)
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

    def test_ready_legacy_document_reports_migration_gaps(self) -> None:
        cov = ready_coverage()
        del cov["source_fact_ledger"]
        del cov["journey_step_traceability"]
        result = MOD.lint_coverage(cov)
        codes = {hit["code"] for hit in result["hits"]}
        self.assertIn("source_fact_ledger_missing", codes)
        self.assertIn("journey_step_traceability_missing", codes)

    def test_granoreader_generic_import_loses_plus_button_and_picker(self) -> None:
        cov = ready_coverage()
        fixture = json.loads(GRANOREADER_FIXTURE.read_text(encoding="utf-8"))
        fact = cov["source_fact_ledger"]["facts"][0]
        fact.update(fixture["source_fact"])
        ledger = cov["source_fact_ledger"]
        digest = MOD.canonical_source_fact_ledger_sha256(ledger)
        ledger["ledger_sha256"] = digest
        ledger["review"]["reviewed_ledger_sha256"] = digest
        trace = cov["journey_step_traceability"]
        trace["source_fact_ledger_sha256"] = digest
        for step in trace["journeys"][0]["steps"]:
            step["source_fact_ids"] = []
        trace_digest = MOD.canonical_journey_step_traceability_sha256(trace)
        trace["traceability_sha256"] = trace_digest
        trace["review"]["reviewed_traceability_sha256"] = trace_digest

        result = MOD.lint_coverage(cov)
        codes = {hit["code"] for hit in result["hits"]}
        for expected in fixture["expected_fail_codes"][:2]:
            self.assertIn(expected, codes)

    def test_product_expansion_requires_confirmation(self) -> None:
        cov = ready_coverage()
        fact = cov["source_fact_ledger"]["facts"][0]
        fact["source_kind"] = "product_expansion"
        ledger = cov["source_fact_ledger"]
        digest = MOD.canonical_source_fact_ledger_sha256(ledger)
        ledger["ledger_sha256"] = digest
        ledger["review"]["reviewed_ledger_sha256"] = digest
        result = MOD.lint_coverage(cov)
        self.assertIn(
            "product_expansion_requires_user",
            {hit["code"] for hit in result["hits"]},
        )

    def test_os_picker_requires_unit_and_e2e_plus_failure_step(self) -> None:
        cov = ready_coverage()
        steps = cov["journey_step_traceability"]["journeys"][0]["steps"]
        picker = steps[1]
        picker["interaction_surface"] = "os_chrome"
        picker["platform_boundary"] = "plugin"
        picker["required_test_layers"] = ["e2e"]
        picker["failure_modes"] = ["missing_plugin", "cancel"]
        trace = cov["journey_step_traceability"]
        digest = MOD.canonical_journey_step_traceability_sha256(trace)
        trace["traceability_sha256"] = digest
        trace["review"]["reviewed_traceability_sha256"] = digest
        result = MOD.lint_coverage(cov)
        self.assertIn(
            "platform_boundary_test_missing",
            {hit["code"] for hit in result["hits"]},
        )


if __name__ == "__main__":
    unittest.main()
