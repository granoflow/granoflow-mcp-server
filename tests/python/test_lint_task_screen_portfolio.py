#!/usr/bin/env python3
"""Tests for lint_task_screen_portfolio.py (Milestone task_plan SoT)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_task_screen_portfolio.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_task_screen_portfolio", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def ready_milestone(**overrides):
    base = {
        "document_type": "milestone_work",
        "milestone_id": "m1",
        "task_plan": {
            "status": "passed",
            "key_screen_refs": ["S-reader"],
            "detail_carryforward": {
                "status": "complete",
                "rows": [
                    {
                        "key_screen_id": "S-reader",
                        "detail_id": "bottom_bar",
                        "disposition": "carried",
                        "carried_to_refined_screen": "S-reader",
                        "carried_to_task_local_key": "T1",
                        "rationale": None,
                    }
                ],
            },
            "refined_screens": [
                {
                    "screen_id": "S-reader",
                    "traces_to_key_screen": "S-reader",
                    "provenance": "traces_to_key_screen",
                    "acceptance_ids": ["A1"],
                    "carried_ui_detail_ids": ["bottom_bar"],
                    "split_probe": {
                        "pass_completed": True,
                        "conclusion": "keep_cohesive",
                        "rejected_split_summary": (
                            "Reader chrome + content stay one surface; no serial gate."
                        ),
                        "accepted_split_summary": None,
                        "resulting_screen_ids": [],
                        "rationale": "cite journey J-read keep_cohesive",
                    },
                }
            ],
            "page_journeys": [
                {
                    "journey_id": "MJ-read",
                    "screen_ids": ["S-reader"],
                    "summary": "Open book and read",
                    "acceptance_ids": ["A1"],
                }
            ],
            "tasks": [
                {
                    "local_key": "T1",
                    "task_id": None,
                    "responsibility": "Deliver the reader surface",
                    "screen_ids": ["S-reader"],
                    "acceptance_ids": ["A1"],
                    "depends_on": [],
                    "reopen_policy": "forbidden_without_milestone_task_plan_reopen",
                }
            ],
            "checklist": {
                "every_refined_screen_has_split_probe": True,
                "every_refined_screen_has_task": True,
                "every_task_has_responsibility": True,
                "traces_or_discovered_set": True,
                "every_in_scope_key_page_referenced": True,
                "every_pw_ui_detail_dispositioned": True,
            },
        },
        "task_skeleton": [
            {
                "local_key": "T1",
                "acceptance_ids": ["A1"],
                "screen_ids": ["S-reader"],
                "create_status": "pending",
            }
        ],
    }
    base.update(overrides)
    return base


def sample_project_work():
    return {
        "product_spec_coverage": {
            "screen_coverage": [
                {
                    "screen_id": "S-reader",
                    "disposition": "adopted",
                    "baseline_required": True,
                    "acceptance_ids": ["A1"],
                    "ui_details": [
                        {
                            "detail_id": "bottom_bar",
                            "statement": "Reader has a bottom action bar",
                            "source": "from_product_doc",
                        }
                    ],
                }
            ]
        }
    }


class LintTaskScreenPortfolioTests(unittest.TestCase):
    def test_plan_passed_ok(self) -> None:
        result = MOD.lint_screen_task_portfolio(ready_milestone(), phase="plan_passed")
        self.assertTrue(result["ok"], result)

    def test_missing_task_plan_fails(self) -> None:
        result = MOD.lint_screen_task_portfolio({"milestone_id": "m1"}, phase="plan_passed")
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("milestone_task_plan_incomplete", codes)

    def test_draft_status_fails_plan_passed(self) -> None:
        doc = ready_milestone()
        doc["task_plan"]["status"] = "draft"
        result = MOD.lint_screen_task_portfolio(doc, phase="plan_passed")
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("milestone_task_plan_incomplete", codes)

    def test_missing_split_probe_fails(self) -> None:
        doc = ready_milestone()
        del doc["task_plan"]["refined_screens"][0]["split_probe"]
        result = MOD.lint_screen_task_portfolio(doc, phase="plan_passed")
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("screen_split_probe_incomplete", codes)

    def test_screen_missing_from_tasks_fails(self) -> None:
        doc = ready_milestone()
        doc["task_plan"]["tasks"][0]["screen_ids"] = []
        result = MOD.lint_screen_task_portfolio(doc, phase="plan_passed")
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("task_portfolio_screen_coverage_incomplete", codes)

    def test_portfolio_ready_requires_task_ids(self) -> None:
        doc = ready_milestone()
        result = MOD.lint_screen_task_portfolio(doc, phase="portfolio_ready")
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("task_portfolio_screen_coverage_incomplete", codes)

        doc["task_plan"]["tasks"][0]["task_id"] = "task-1"
        result = MOD.lint_screen_task_portfolio(doc, phase="portfolio_ready")
        self.assertTrue(result["ok"], result)

    def test_not_applicable_ok(self) -> None:
        doc = {"task_plan": {"status": "not_applicable"}}
        result = MOD.lint_screen_task_portfolio(doc, phase="plan_passed")
        self.assertTrue(result["ok"], result)

    def test_detail_carryforward_ok_with_project_work(self) -> None:
        result = MOD.lint_screen_task_portfolio(
            ready_milestone(),
            project_work=sample_project_work(),
            phase="plan_passed",
        )
        self.assertTrue(result["ok"], result)

    def test_missing_detail_carryforward_fails(self) -> None:
        doc = ready_milestone()
        doc["task_plan"]["detail_carryforward"]["rows"] = []
        result = MOD.lint_screen_task_portfolio(
            doc,
            project_work=sample_project_work(),
            phase="plan_passed",
        )
        self.assertFalse(result["ok"])
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("milestone_detail_carryforward_incomplete", codes)

    def test_cli_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mw.json"
            pw = Path(tmp) / "pw.json"
            path.write_text(json.dumps(ready_milestone()), encoding="utf-8")
            pw.write_text(json.dumps(sample_project_work()), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(path),
                    "--phase",
                    "plan_passed",
                    "--project-work",
                    str(pw),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
