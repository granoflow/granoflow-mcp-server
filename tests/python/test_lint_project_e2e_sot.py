#!/usr/bin/env python3
"""Tests for lint_project_e2e_sot.py."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_project_e2e_sot.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_project_e2e_sot", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _base(**overrides: object) -> dict:
    stages = [{"id": sid, "status": "not_started", "evidence": ""} for sid in MOD.STAGE_IDS]
    data: dict = {
        "doc_type": "project_e2e_sot",
        "schema": "granoflow_project_e2e_sot_v1",
        "project_id": "proj-1",
        "status": "active",
        "interaction_mode": "interactive",
        "updated_at": "2026-07-25T00:00:00Z",
        "source_digests": {"project_work": "digest-a"},
        "cross_milestone_integration": "not_applicable",
        "stages": stages,
        "work_items": [],
        "next_step": {"work_item_id": "", "summary": "", "override": None},
        "integration_campaign": {
            "path": "not_started",
            "cross_milestone_journey_check": "not_applicable",
            "evidence_ref": [],
        },
        "e2e_campaign": {
            "coverage_matrix_check": "not_applicable",
            "evidence_ref": [],
        },
    }
    data.update(overrides)
    return data


class LintProjectE2ESotTests(unittest.TestCase):
    def test_minimal_ok(self) -> None:
        result = MOD.lint_project_e2e_sot(_base())
        self.assertTrue(result["ok"], result)

    def test_missing_stage_fails(self) -> None:
        data = _base()
        data["stages"] = data["stages"][:-1]
        result = MOD.lint_project_e2e_sot(data)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any("missing stage" in e["detail"] for e in result["errors"]),
            result,
        )

    def test_analysis_plan_pin(self) -> None:
        data = _base(
            work_items=[
                {
                    "id": "M1.T1.3.1_analysis",
                    "pair": "M1.T1",
                    "seq": "3.1",
                    "status": "done",
                },
                {
                    "id": "M1.T1.3.2_plan",
                    "pair": "M1.T1",
                    "seq": "3.2",
                    "status": "pending",
                },
            ],
            next_step={
                "work_item_id": "M1.T2.3.1_analysis",
                "override": None,
            },
        )
        result = MOD.lint_project_e2e_sot(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("project_e2e_sot_next_step_unpinned", codes)

    def test_pin_satisfied(self) -> None:
        data = _base(
            work_items=[
                {
                    "id": "M1.T1.3.1_analysis",
                    "pair": "M1.T1",
                    "seq": "3.1",
                    "status": "done",
                },
                {
                    "id": "M1.T1.3.2_plan",
                    "pair": "M1.T1",
                    "seq": "3.2",
                    "status": "pending",
                },
            ],
            next_step={
                "work_item_id": "M1.T1.3.2_plan",
                "pinned_by": "analysis_context_affinity",
                "override": None,
            },
        )
        result = MOD.lint_project_e2e_sot(data)
        self.assertTrue(result["ok"], result)

    def test_cross_milestone_gap_blocks_stage_done(self) -> None:
        data = _base()
        for row in data["stages"]:
            if row["id"] == "integration_campaign":
                row["status"] = "done"
        data["integration_campaign"] = {
            "path": "full_unit_and_it",
            "cross_milestone_journey_check": "gap",
            "evidence_ref": [],
        }
        result = MOD.lint_project_e2e_sot(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("cross_milestone_journey_gap", codes)

    def test_e2e_gap_blocks_stage_done(self) -> None:
        data = _base()
        for row in data["stages"]:
            if row["id"] == "e2e_campaign":
                row["status"] = "done"
        data["e2e_campaign"] = {
            "coverage_matrix_check": "gap",
            "evidence_ref": [],
        }
        result = MOD.lint_project_e2e_sot(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_coverage_matrix_gap", codes)

    def test_per_task_implement_forbidden(self) -> None:
        data = _base(
            work_items=[
                {
                    "id": "M1.T1.implement",
                    "status": "pending",
                }
            ],
            next_step={"work_item_id": "M1.T1.implement"},
        )
        result = MOD.lint_project_e2e_sot(data)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any("per-task implement" in e["detail"] for e in result["errors"]),
            result,
        )

    def test_require_digest_match_ok(self) -> None:
        data = _base(
            source_digests={"project_work": "digest-a"},
            source_digest_verification={
                "project_work": {
                    "recorded": "digest-a",
                    "app_readback": "digest-a",
                    "matched": True,
                }
            },
        )
        result = MOD.lint_project_e2e_sot(data, require_digest_match=True)
        self.assertTrue(result["ok"], result)

    def test_require_digest_match_stale(self) -> None:
        data = _base(
            source_digests={"project_work": "digest-a"},
            source_digest_verification={
                "project_work": {
                    "recorded": "digest-a",
                    "app_readback": "digest-b",
                    "matched": True,
                }
            },
        )
        result = MOD.lint_project_e2e_sot(data, require_digest_match=True)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "project_e2e_sot_stale")

    def test_require_digest_match_missing_verification(self) -> None:
        data = _base(source_digests={"project_work": "digest-a"})
        result = MOD.lint_project_e2e_sot(data, require_digest_match=True)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("project_e2e_sot_stale", codes)

    def test_parallel_batches_optional_ok(self) -> None:
        data = _base(
            parallel_batches=[
                {
                    "batch_id": "batch-1",
                    "review_ref": "temp/parallel-batch-batch-1-review-v1.md",
                    "status": "accepted",
                }
            ]
        )
        result = MOD.lint_project_e2e_sot(data)
        self.assertTrue(result["ok"], result)

    def test_parallel_batches_invalid_status(self) -> None:
        data = _base(
            parallel_batches=[
                {
                    "batch_id": "batch-1",
                    "review_ref": "temp/x.md",
                    "status": "done",
                }
            ]
        )
        result = MOD.lint_project_e2e_sot(data)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any("parallel_batches" in e["detail"] for e in result["errors"]),
            result,
        )

    def test_cli_json(self) -> None:
        import subprocess
        import tempfile

        data = _base()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sot.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            proc = subprocess.run(
                ["python3", str(SCRIPT), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
