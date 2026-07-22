#!/usr/bin/env python3
"""Tests for lint_prototype_implementation_fidelity.py."""

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
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_prototype_implementation_fidelity.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_implementation_fidelity", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class LintPrototypeImplementationFidelityTests(unittest.TestCase):
    def test_undeclared_fails(self) -> None:
        data = {
            "prototype_impl_compare": {
                "status": "matched",
                "method": "code_review_guess",
                "declaration_emitted": False,
                "questions": {
                    "ux_better": False,
                    "visual_better": False,
                    "tech_stack_blocked": False,
                },
                "decision": "keep_implementation",
                "decision_rationale": "matches prototype regions",
                "diffs": [],
            }
        }
        result = MOD.lint_prototype_impl_compare(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_impl_compare_undeclared", codes)

    def test_matched_ok(self) -> None:
        data = {
            "prototype_impl_compare": {
                "status": "matched",
                "method": "code_review_guess",
                "declaration_emitted": True,
                "questions": {
                    "ux_better": False,
                    "visual_better": False,
                    "tech_stack_blocked": False,
                },
                "decision": "keep_implementation",
                "decision_rationale": "shell and primary CTA match prototype",
                "diffs": [],
            }
        }
        result = MOD.lint_prototype_impl_compare(data)
        self.assertTrue(result["ok"], result)

    def test_matched_missing_questions_fails(self) -> None:
        data = {
            "prototype_impl_compare": {
                "status": "matched",
                "method": "code_review_guess",
                "declaration_emitted": True,
                "decision": "keep_implementation",
                "decision_rationale": "looks fine",
                "diffs": [],
            }
        }
        result = MOD.lint_prototype_impl_compare(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_impl_compare_three_questions_incomplete", codes)

    def test_screenshot_method_fails(self) -> None:
        data = {
            "prototype_impl_compare": {
                "status": "matched",
                "method": "screenshot_vision",
                "declaration_emitted": True,
                "questions": {
                    "ux_better": False,
                    "visual_better": False,
                    "tech_stack_blocked": False,
                },
                "decision": "keep_implementation",
                "decision_rationale": "n/a",
                "diffs": [],
            }
        }
        result = MOD.lint_prototype_impl_compare(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_impl_compare_wrong_method", codes)

    def test_diverged_without_diffs_fails(self) -> None:
        data = {
            "prototype_impl_compare": {
                "status": "diverged",
                "method": "code_review_guess",
                "declaration_emitted": True,
                "questions": {
                    "ux_better": True,
                    "visual_better": False,
                    "tech_stack_blocked": False,
                },
                "decision": "keep_implementation",
                "decision_rationale": "ux clearer despite visual gap",
                "diffs": [],
            }
        }
        result = MOD.lint_prototype_impl_compare(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_diff_ledger_incomplete", codes)

    def test_diverged_with_diffs_ok(self) -> None:
        data = {
            "prototype_impl_compare": {
                "status": "diverged",
                "method": "code_review_guess",
                "declaration_emitted": True,
                "questions": {
                    "ux_better": False,
                    "visual_better": False,
                    "tech_stack_blocked": True,
                },
                "decision": "keep_implementation",
                "decision_rationale": "native control cannot match CSS blur",
                "diffs": [
                    {
                        "page_id": "S-settings",
                        "summary": "blur panel approximated",
                        "prototype_ref": "ui_prototype#settings",
                        "impl_ref": "lib/settings_page.dart",
                    }
                ],
            }
        }
        result = MOD.lint_prototype_impl_compare(data)
        self.assertTrue(result["ok"], result)

    def test_cli_subprocess(self) -> None:
        payload = {
            "prototype_impl_compare": {
                "status": "not_applicable",
                "method": "code_review_guess",
                "declaration_emitted": False,
                "decision": "not_applicable",
                "decision_rationale": "no UI",
                "diffs": [],
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
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
