#!/usr/bin/env python3
"""Tests for lint_plan_route_ui_truth.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_plan_route_ui_truth.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_plan_route_ui_truth", SCRIPT)
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


class LintPlanRouteUiTruthTests(unittest.TestCase):
    def test_not_applicable_ok(self) -> None:
        result = MOD.lint_plan_route_ui_truth(
            {
                "route_ui_truth_check_status": "not_applicable",
                "route_ui_truth_index_review": [],
                "route_ui_truth_not_applicable_reason": "empty index; no RB themes",
                "route_ui_truth_fact_ids": [],
                "route_ui_truth_will_change": [],
                "card_change_plan_notice": _none_plan_notice(),
            }
        )
        self.assertTrue(result["ok"], result)

    def test_missing_status_fails(self) -> None:
        result = MOD.lint_plan_route_ui_truth({})
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "route_ui_truth_check_missing")

    def test_full_unchanged_ok(self) -> None:
        result = MOD.lint_plan_route_ui_truth(
            {
                "route_ui_truth_check_status": "checked_unchanged",
                "route_ui_truth_fact_ids": ["UIT-library-encryption"],
                "route_ui_truth_will_change": [],
                "route_ui_truth_index_review": [
                    _row(
                        "UIT-library-encryption",
                        related=True,
                        disposition="unchanged",
                    ),
                    _row("UIT-sample-book", related=False, disposition="unrelated"),
                ],
                "card_change_plan_notice": _none_plan_notice(),
            }
        )
        self.assertTrue(result["ok"], result)

    def test_unchanged_without_none_notice_fails(self) -> None:
        result = MOD.lint_plan_route_ui_truth(
            {
                "route_ui_truth_check_status": "checked_unchanged",
                "route_ui_truth_fact_ids": ["UIT-library-encryption"],
                "route_ui_truth_will_change": [],
                "route_ui_truth_index_review": [
                    _row(
                        "UIT-library-encryption",
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
                    "kind": "route_ui_truth",
                    "action": "update",
                    "fact_id": fact_id,
                    "note_id": "note-" + fact_id,
                    "card_ids": ["card-" + fact_id],
                    "summary": f"本次迭代将更新 {fact_id} 的现状/边界",
                }
            ],
        }

    def test_will_change_without_refs_fails(self) -> None:
        result = MOD.lint_plan_route_ui_truth(
            {
                "route_ui_truth_check_status": "checked_will_change",
                "route_ui_truth_fact_ids": ["UIT-library-encryption"],
                "route_ui_truth_will_change": ["UIT-library-encryption"],
                "route_ui_truth_index_review": [
                    _row(
                        "UIT-library-encryption",
                        related=True,
                        disposition="will_change",
                        verification_refs=[],
                    ),
                ],
                "card_change_plan_notice": self._plan_notice("UIT-library-encryption"),
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["code"],
            "route_ui_truth_will_change_without_verification",
        )

    def test_will_change_without_notice_fails(self) -> None:
        result = MOD.lint_plan_route_ui_truth(
            {
                "route_ui_truth_check_status": "checked_will_change",
                "route_ui_truth_fact_ids": ["UIT-library-encryption"],
                "route_ui_truth_will_change": ["UIT-library-encryption"],
                "route_ui_truth_index_review": [
                    _row(
                        "UIT-library-encryption",
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
        result = MOD.lint_plan_route_ui_truth(
            {
                "route_ui_truth_check_status": "checked_will_change",
                "route_ui_truth_fact_ids": ["UIT-library-encryption"],
                "route_ui_truth_will_change": ["UIT-library-encryption"],
                "route_ui_truth_index_review": [
                    _row(
                        "UIT-library-encryption",
                        related=True,
                        disposition="will_change",
                        verification_refs=["TC-ENC-01"],
                    ),
                ],
                "card_change_plan_notice": self._plan_notice("UIT-library-encryption"),
            }
        )
        self.assertTrue(result["ok"], result)

    def test_snapshot_requires_full_enumeration(self) -> None:
        result = MOD.lint_plan_route_ui_truth(
            {
                "route_ui_truth_check_status": "checked_unchanged",
                "route_ui_truth_fact_ids": ["UIT-library-encryption"],
                "route_ui_truth_will_change": [],
                "route_ui_truth_index_review": [
                    _row(
                        "UIT-library-encryption",
                        related=True,
                        disposition="unchanged",
                    ),
                ],
                "card_change_plan_notice": _none_plan_notice(),
            },
            snapshot={
                "route_ui_truth_index": [
                    {"fact_id": "UIT-library-encryption"},
                    {"fact_id": "UIT-sample-book"},
                ]
            },
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "route_ui_truth_check_missing")
        self.assertTrue(
            any("UIT-sample-book" in err["detail"] for err in result["errors"]),
            result,
        )

    def test_gate_not_required_skips(self) -> None:
        result = MOD.lint_plan_route_ui_truth({}, gate_required=False)
        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
