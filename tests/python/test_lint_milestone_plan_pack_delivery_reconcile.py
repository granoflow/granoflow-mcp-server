#!/usr/bin/env python3
"""Tests for lint_milestone_plan_pack_delivery_reconcile.py."""

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
    / "lint_milestone_plan_pack_delivery_reconcile.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "lint_milestone_plan_pack_delivery_reconcile", SCRIPT
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _accepted_pack(**section_present: bool) -> dict:
    sections = {
        key: {"present": section_present.get(key, False), "basis": ""} for key in MOD.SECTION_KEYS
    }
    return {
        "doc_type": "milestone_plan_acceptance_pack",
        "status": "accepted",
        "sections": sections,
    }


def _ok_reconcile() -> dict:
    return {
        "schema": "granoflow_milestone_plan_pack_reconcile_v1",
        "contract_loaded": True,
        "pack_path": "temp/milestone-plan-acceptance-M1-v1.md",
        "pack_status": "accepted",
        "pack_content_sha256": "abc",
        "status": "complete",
        "sections": {
            "user_copy": {"applicable": True, "status": "matched"},
            "data_structures": {"applicable": False, "status": "n_a"},
            "flowcharts": {"applicable": False, "status": "n_a"},
            "uml_diagrams": {"applicable": False, "status": "n_a"},
            "test_cases": {"applicable": True, "status": "matched"},
        },
        "drift_writeback_ref": None,
    }


class LintPackDeliveryReconcileTests(unittest.TestCase):
    def test_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                _accepted_pack(user_copy=True, test_cases=True),
            )
            delivery = _write(
                root / "delivery.json",
                {"milestone_plan_pack_reconcile": _ok_reconcile()},
            )
            result = MOD.lint_milestone_plan_pack_delivery_reconcile(delivery, pack)
            self.assertTrue(result["ok"], result)

    def test_missing_reconcile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(root / "pack.json", _accepted_pack(test_cases=True))
            delivery = _write(root / "delivery.json", {"notes": "done"})
            result = MOD.lint_milestone_plan_pack_delivery_reconcile(delivery, pack)
            self.assertFalse(result["ok"])
            self.assertEqual(
                result["code"],
                "milestone_plan_acceptance_pack_delivery_unreconciled",
            )

    def test_drift_requires_writeback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                _accepted_pack(user_copy=True, test_cases=True),
            )
            block = _ok_reconcile()
            block["sections"]["user_copy"] = {
                "applicable": True,
                "status": "drifted",
            }
            block["drift_writeback_ref"] = None
            delivery = _write(
                root / "delivery.json",
                {"milestone_plan_pack_reconcile": block},
            )
            result = MOD.lint_milestone_plan_pack_delivery_reconcile(delivery, pack)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "milestone_plan_acceptance_pack_drift")

    def test_pack_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack_data = _accepted_pack(test_cases=True)
            pack_data["status"] = "draft"
            pack = _write(root / "pack.json", pack_data)
            delivery = _write(
                root / "delivery.json",
                {"milestone_plan_pack_reconcile": _ok_reconcile()},
            )
            result = MOD.lint_milestone_plan_pack_delivery_reconcile(delivery, pack)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "milestone_plan_acceptance_pack_not_used")

    def test_cli(self) -> None:
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write(
                root / "pack.json",
                _accepted_pack(user_copy=True, test_cases=True),
            )
            delivery = _write(
                root / "delivery.json",
                {"milestone_plan_pack_reconcile": _ok_reconcile()},
            )
            proc = subprocess.run(
                ["python3", str(SCRIPT), str(delivery), "--pack", str(pack)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
