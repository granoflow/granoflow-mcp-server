#!/usr/bin/env python3
"""Unit tests for lint_milestone_child_done.py (milestone acceptance ⇒ child done)."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_milestone_child_done.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_milestone_child_done", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class LintMilestoneChildDoneTests(unittest.TestCase):
    def test_skip_when_acceptance_not_passed(self) -> None:
        result = MOD.lint_milestone_child_done(
            acceptance_status="partial",
            tasks=[{"id": "t1", "status": "pending", "title": "A"}],
        )
        self.assertTrue(result["ok"])
        self.assertFalse(result["checked"])

    def test_passed_requires_all_done(self) -> None:
        result = MOD.lint_milestone_child_done(
            acceptance_status="passed",
            tasks=[
                {"id": "t1", "status": "done", "title": "A"},
                {"id": "t2", "status": "pending", "title": "B"},
            ],
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "milestone_child_pending_on_acceptance")

    def test_passed_all_done_ok(self) -> None:
        result = MOD.lint_milestone_child_done(
            acceptance_status="passed",
            tasks=[
                {"id": "t1", "status": "done"},
                {"id": "t2", "status": "done"},
            ],
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["considered_count"], 2)

    def test_excludes_cancelled(self) -> None:
        result = MOD.lint_milestone_child_done(
            acceptance_status="passed",
            tasks=[
                {"id": "t1", "status": "done"},
                {"id": "t2", "status": "cancelled"},
            ],
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["considered_count"], 1)

    def test_claim_passed_without_status(self) -> None:
        result = MOD.lint_milestone_child_done(
            acceptance_status=None,
            claim_passed=True,
            tasks=[{"id": "t1", "status": "pending"}],
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "milestone_child_pending_on_acceptance")

    def test_in_scope_filter(self) -> None:
        result = MOD.lint_milestone_child_done(
            acceptance_status="passed",
            in_scope_task_ids={"t1"},
            tasks=[
                {"id": "t1", "status": "done"},
                {"id": "t2", "status": "pending"},
            ],
        )
        self.assertTrue(result["ok"], result)

    def test_cli_tasks_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mw = root / "mw.yaml"
            tasks = root / "tasks.json"
            mw.write_text("acceptance_status: passed\n", encoding="utf-8")
            tasks.write_text(
                json.dumps(
                    {
                        "items": [
                            {"id": "a", "status": "done", "title": "A"},
                            {"id": "b", "status": "done", "title": "B"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            code = MOD.main(
                [
                    "--milestone-work",
                    str(mw),
                    "--tasks-json",
                    str(tasks),
                ]
            )
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
