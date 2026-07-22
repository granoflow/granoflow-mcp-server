#!/usr/bin/env python3
"""Tests for lint_app_icon_source_gate.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_app_icon_source_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_app_icon_source_gate", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class LintAppIconSourceGateTests(unittest.TestCase):
    def test_unresolved_missing_icon_fails(self) -> None:
        data = {
            "product": {
                "app_icon": {
                    "applicability": "required",
                    "applicability_basis": "ios and android App",
                    "document_scan_status": "missing",
                    "source_choice": "unresolved",
                    "asset_path": None,
                    "license_note": None,
                    "user_decision_recorded": False,
                }
            }
        }
        result = MOD.lint_app_icon(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("app_icon_source_unresolved", codes)

    def test_not_applicable_ok(self) -> None:
        data = {
            "product": {
                "app_icon": {
                    "applicability": "not_applicable",
                    "applicability_basis": "CLI library only",
                    "document_scan_status": "not_scanned",
                    "source_choice": "not_applicable",
                    "user_decision_recorded": False,
                }
            }
        }
        result = MOD.lint_app_icon(data)
        self.assertTrue(result["ok"], result)

    def test_user_provided_ok(self) -> None:
        data = {
            "product": {
                "app_icon": {
                    "applicability": "required",
                    "applicability_basis": "desktop App",
                    "document_scan_status": "missing",
                    "source_choice": "user_provided",
                    "asset_path": "assets/icon.png",
                    "license_note": None,
                    "user_decision_recorded": True,
                }
            }
        }
        result = MOD.lint_app_icon(data)
        self.assertTrue(result["ok"], result)

    def test_cli_subprocess(self) -> None:
        payload = {
            "product": {
                "app_icon": {
                    "applicability": "not_applicable",
                    "applicability_basis": "web only",
                    "source_choice": "not_applicable",
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pw.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
