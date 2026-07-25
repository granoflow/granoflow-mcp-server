#!/usr/bin/env python3
"""Tests for lint_plan_entry_prototype_acceptance.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_plan_entry_prototype_acceptance.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_plan_entry_prototype_acceptance", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _ledger(html: Path, **overrides: Any) -> dict[str, Any]:
    file_url = html.resolve().as_uri()
    block: dict[str, Any] = {
        "schema": "granoflow_prototype_link_ledger_v1",
        "contract_loaded": True,
        "status": "complete",
        "chat_digest_emitted": True,
        "markdown_digest": f"## Digest\n\n- [Open]({file_url})\n",
        "entries": [
            {
                "title": "Open",
                "absolute_path": str(html.resolve()),
                "file_url": file_url,
            }
        ],
    }
    block.update(overrides)
    return block


def _acceptance(**overrides: Any) -> dict[str, Any]:
    block: dict[str, Any] = {
        "schema": "granoflow_prototype_plan_entry_acceptance_v1",
        "contract_loaded": True,
        "prototype_requirement": "required",
        "status": "accepted",
        "acceptance_source": "verbal",
    }
    block.update(overrides)
    return block


class LintPlanEntryPrototypeAcceptanceTests(unittest.TestCase):
    def test_non_ui_not_required(self) -> None:
        result = MOD.lint_plan_entry_prototype_acceptance({"prototype_requirement": "not_required"})
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["gate"], "not_applicable")

    def test_conditional_false_is_non_ui(self) -> None:
        result = MOD.lint_plan_entry_prototype_acceptance(
            {
                "prototype_requirement": "conditional",
                "prototype_condition_result": False,
            }
        )
        self.assertTrue(result["ok"], result)

    def test_missing_digest_blocks_plan(self) -> None:
        result = MOD.lint_plan_entry_prototype_acceptance(
            {
                "prototype_requirement": "required",
                "prototype_link_ledger": {
                    "schema": "granoflow_prototype_link_ledger_v1",
                    "status": "pending",
                    "entries": [],
                },
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "plan_entry_prototype_acceptance_required")

    def test_digest_without_acceptance_unconfirmed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "a.html"
            html.write_text("<html></html>", encoding="utf-8")
            result = MOD.lint_plan_entry_prototype_acceptance(
                {
                    "prototype_requirement": "required",
                    "prototype_link_ledger": _ledger(html),
                }
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "plan_entry_prototype_unconfirmed")

    def test_verbal_acceptance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "a.html"
            html.write_text("<html></html>", encoding="utf-8")
            result = MOD.lint_plan_entry_prototype_acceptance(
                {
                    "prototype_requirement": "required",
                    "prototype_link_ledger": _ledger(html),
                    "prototype_plan_entry_acceptance": _acceptance(acceptance_source="verbal"),
                }
            )
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["acceptance_source"], "verbal")

    def test_unattended_auto_accept_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "a.html"
            html.write_text("<html></html>", encoding="utf-8")
            result = MOD.lint_plan_entry_prototype_acceptance(
                {
                    "prototype_requirement": "required",
                    "prototype_link_ledger": _ledger(html),
                    "prototype_plan_entry_acceptance": _acceptance(
                        acceptance_source="unattended_auto_accept"
                    ),
                }
            )
            self.assertTrue(result["ok"], result)

    def test_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            html = root / "a.html"
            html.write_text("<html></html>", encoding="utf-8")
            path = root / "task.json"
            path.write_text(
                json.dumps(
                    {
                        "prototype_requirement": "not_required",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(MOD.main([str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
