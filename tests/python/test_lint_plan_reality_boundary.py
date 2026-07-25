#!/usr/bin/env python3
"""Tests for lint_plan_reality_boundary.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_plan_reality_boundary.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_plan_reality_boundary", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _none_plan_notice(summary: str = "本次迭代无卡片变更") -> dict[str, Any]:
    return {
        "emitted": True,
        "shown_to_user": True,
        "none": True,
        "summary": summary,
        "items": [],
    }


def _row(
    fact_id: str,
    *,
    related: bool,
    disposition: str,
    verification_refs: list[str] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "fact_id": fact_id,
        "related": related,
        "disposition": disposition,
        "note_id": "note-" + fact_id,
        "card_ids": ["card-" + fact_id],
        "verification_refs": verification_refs or [],
    }
    return row


class LintPlanRealityBoundaryTests(unittest.TestCase):
    def test_not_applicable_ok(self) -> None:
        result = MOD.lint_plan_reality_boundary(
            {
                "reality_boundary_check_status": "not_applicable",
                "reality_boundary_index_review": [],
                "reality_boundary_not_applicable_reason": "empty index; no RB themes",
                "reality_boundary_fact_ids": [],
                "reality_boundary_will_change": [],
                "card_change_plan_notice": _none_plan_notice(),
            }
        )
        self.assertTrue(result["ok"], result)

    def test_missing_status_fails(self) -> None:
        result = MOD.lint_plan_reality_boundary({})
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "reality_boundary_check_missing")

    def test_full_unchanged_ok(self) -> None:
        result = MOD.lint_plan_reality_boundary(
            {
                "reality_boundary_check_status": "checked_unchanged",
                "reality_boundary_fact_ids": ["RB-library-encryption"],
                "reality_boundary_will_change": [],
                "reality_boundary_index_review": [
                    _row(
                        "RB-library-encryption",
                        related=True,
                        disposition="unchanged",
                    ),
                    _row("RB-sample-book", related=False, disposition="unrelated"),
                ],
                "card_change_plan_notice": _none_plan_notice(),
            }
        )
        self.assertTrue(result["ok"], result)

    def test_unchanged_without_none_notice_fails(self) -> None:
        result = MOD.lint_plan_reality_boundary(
            {
                "reality_boundary_check_status": "checked_unchanged",
                "reality_boundary_fact_ids": ["RB-library-encryption"],
                "reality_boundary_will_change": [],
                "reality_boundary_index_review": [
                    _row(
                        "RB-library-encryption",
                        related=True,
                        disposition="unchanged",
                    ),
                ],
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "card_change_plan_notice_missing")

    def _plan_notice(self, fact_id: str) -> dict[str, Any]:
        return {
            "emitted": True,
            "shown_to_user": True,
            "items": [
                {
                    "kind": "reality_boundary",
                    "action": "update",
                    "fact_id": fact_id,
                    "note_id": "note-" + fact_id,
                    "card_ids": ["card-" + fact_id],
                    "summary": f"本次迭代将更新 {fact_id} 的现状/边界",
                }
            ],
        }

    def test_will_change_without_refs_fails(self) -> None:
        result = MOD.lint_plan_reality_boundary(
            {
                "reality_boundary_check_status": "checked_will_change",
                "reality_boundary_fact_ids": ["RB-library-encryption"],
                "reality_boundary_will_change": ["RB-library-encryption"],
                "reality_boundary_index_review": [
                    _row(
                        "RB-library-encryption",
                        related=True,
                        disposition="will_change",
                        verification_refs=[],
                    ),
                ],
                "card_change_plan_notice": self._plan_notice("RB-library-encryption"),
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["code"],
            "reality_boundary_will_change_without_verification",
        )

    def test_will_change_without_notice_fails(self) -> None:
        result = MOD.lint_plan_reality_boundary(
            {
                "reality_boundary_check_status": "checked_will_change",
                "reality_boundary_fact_ids": ["RB-library-encryption"],
                "reality_boundary_will_change": ["RB-library-encryption"],
                "reality_boundary_index_review": [
                    _row(
                        "RB-library-encryption",
                        related=True,
                        disposition="will_change",
                        verification_refs=["TC-ENC-01"],
                    ),
                ],
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "card_change_plan_notice_missing")

    def test_will_change_with_refs_ok(self) -> None:
        result = MOD.lint_plan_reality_boundary(
            {
                "reality_boundary_check_status": "checked_will_change",
                "reality_boundary_fact_ids": ["RB-library-encryption"],
                "reality_boundary_will_change": ["RB-library-encryption"],
                "reality_boundary_index_review": [
                    _row(
                        "RB-library-encryption",
                        related=True,
                        disposition="will_change",
                        verification_refs=["TC-ENC-01"],
                    ),
                ],
                "card_change_plan_notice": self._plan_notice("RB-library-encryption"),
            }
        )
        self.assertTrue(result["ok"], result)

    def test_snapshot_requires_full_enumeration(self) -> None:
        result = MOD.lint_plan_reality_boundary(
            {
                "reality_boundary_check_status": "checked_unchanged",
                "reality_boundary_fact_ids": ["RB-library-encryption"],
                "reality_boundary_will_change": [],
                "reality_boundary_index_review": [
                    _row(
                        "RB-library-encryption",
                        related=True,
                        disposition="unchanged",
                    ),
                ],
                "card_change_plan_notice": _none_plan_notice(),
            },
            snapshot={
                "reality_boundary_index": [
                    {"fact_id": "RB-library-encryption"},
                    {"fact_id": "RB-sample-book"},
                ]
            },
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "reality_boundary_check_missing")
        self.assertTrue(
            any("RB-sample-book" in err["detail"] for err in result["errors"]),
            result,
        )

    def test_gate_not_required_skips(self) -> None:
        result = MOD.lint_plan_reality_boundary({}, gate_required=False)
        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
