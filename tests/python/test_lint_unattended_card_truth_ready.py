#!/usr/bin/env python3
"""Tests for lint_unattended_card_truth_ready.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_unattended_card_truth_ready.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_unattended_card_truth_ready", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class LintUnattendedCardTruthReadyTests(unittest.TestCase):
    def test_empty_ok_without_requires(self) -> None:
        result = MOD.lint_unattended_card_truth_ready(
            snapshot={"route_ui_truth_index": [], "reality_boundary_index": []}
        )
        self.assertTrue(result["ok"], result)

    def test_require_uit_index_blocks_empty(self) -> None:
        result = MOD.lint_unattended_card_truth_ready(
            snapshot={"route_ui_truth_index": []},
            require_uit_index=True,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "card_truth_batch_gate_blocked")

    def test_valid_uit_index_passes(self) -> None:
        result = MOD.lint_unattended_card_truth_ready(
            snapshot={
                "route_ui_truth_index": [
                    {"fact_id": "UIT-bookshelf", "note_id": "n1", "card_ids": ["c1"]}
                ]
            },
            require_uit_index=True,
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["uit_index_count"], 1)

    def test_placeholder_note_id_blocked(self) -> None:
        result = MOD.lint_unattended_card_truth_ready(
            snapshot={
                "route_ui_truth_index": [
                    {"fact_id": "UIT-bookshelf", "note_id": "REPLACE", "card_ids": []}
                ]
            },
            require_uit_index=True,
        )
        self.assertFalse(result["ok"])

    def test_field_media_required(self) -> None:
        caps = {"resources": {"review-note": ["field-media.upload"]}}
        ok = MOD.lint_unattended_card_truth_ready(
            snapshot={},
            capabilities=caps,
            require_field_media=True,
        )
        self.assertTrue(ok["ok"], ok)
        bad = MOD.lint_unattended_card_truth_ready(
            snapshot={},
            capabilities={"resources": {}},
            require_field_media=True,
        )
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["field_media_capability"], "missing")

    def test_gate_passed_required(self) -> None:
        missing = MOD.lint_unattended_card_truth_ready(
            snapshot={},
            require_gate_passed=True,
        )
        self.assertEqual(missing["code"], "card_truth_batch_gate_missing")
        passed = MOD.lint_unattended_card_truth_ready(
            snapshot={},
            gate={"status": "passed", "summary": "batch done"},
            require_gate_passed=True,
        )
        self.assertTrue(passed["ok"], passed)


if __name__ == "__main__":
    unittest.main()
