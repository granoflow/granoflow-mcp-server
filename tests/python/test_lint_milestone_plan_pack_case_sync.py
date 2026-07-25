#!/usr/bin/env python3
"""Tests for lint_milestone_plan_pack_case_sync.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_milestone_plan_pack_case_sync.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_milestone_plan_pack_case_sync", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class LintPackCaseSyncTests(unittest.TestCase):
    def test_not_applicable_when_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                {
                    "doc_type": "milestone_plan_acceptance_pack",
                    "sections": {"test_cases": {"present": False, "basis": "none"}},
                    "body_markdown": "",
                },
            )
            result = MOD.lint_milestone_plan_pack_case_sync(pack, [])
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["code"], "not_applicable")

    def test_sync_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                {
                    "sections": {"test_cases": {"present": True}},
                    "body_markdown": (
                        "| Case ID | lane |\n| --- | --- |\n"
                        "| U1 | unit |\n| I1 | integration |\n| E1 | e2e |\n"
                    ),
                },
            )
            task = _write(
                root / "task.json",
                {
                    "schema": "granoflow_plan_verification_cases_v1",
                    "cases": [
                        {"case_id": "U1", "lane": "unit"},
                        {"case_id": "I1", "lane": "integration"},
                        {"case_id": "E1", "lane": "e2e"},
                    ],
                },
            )
            result = MOD.lint_milestone_plan_pack_case_sync(pack, [task])
            self.assertTrue(result["ok"], result)

    def test_pack_case_missing_from_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                {
                    "sections": {"test_cases": {"present": True}},
                    "body_markdown": "| U1 | unit |\n| X9 | unit |\n",
                },
            )
            task = _write(
                root / "task.json",
                {
                    "schema": "granoflow_plan_verification_cases_v1",
                    "cases": [{"case_id": "U1", "lane": "unit"}],
                },
            )
            result = MOD.lint_milestone_plan_pack_case_sync(pack, [task])
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "pack_case_missing_from_tasks")

    def test_task_case_missing_from_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                {
                    "sections": {"test_cases": {"present": True}},
                    "body_markdown": "| U1 | unit |\n",
                },
            )
            task = _write(
                root / "task.json",
                {
                    "schema": "granoflow_plan_verification_cases_v1",
                    "cases": [
                        {"case_id": "U1", "lane": "unit"},
                        {"case_id": "U2", "lane": "unit"},
                    ],
                },
            )
            result = MOD.lint_milestone_plan_pack_case_sync(pack, [task])
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "task_case_missing_from_pack")

    def test_cli(self) -> None:
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                {
                    "sections": {"test_cases": {"present": False, "basis": "x"}},
                    "body_markdown": "",
                },
            )
            proc = subprocess.run(
                ["python3", str(SCRIPT), str(pack)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
