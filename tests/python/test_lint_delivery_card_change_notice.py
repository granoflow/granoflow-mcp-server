#!/usr/bin/env python3
"""Tests for lint_delivery_card_change_notice.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_delivery_card_change_notice.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_delivery_card_change_notice", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class LintDeliveryCardChangeNoticeTests(unittest.TestCase):
    def test_no_changes_ok(self) -> None:
        result = MOD.lint_delivery_card_change_notice(
            {
                "reality_boundary_check_status": "checked_unchanged",
                "reality_boundary_will_change": [],
                "card_change_delivery_notice": {
                    "emitted": True,
                    "shown_to_user": True,
                    "none": True,
                    "cards_updated": False,
                    "summary": "本次实施无卡片变更",
                    "items": [],
                },
            }
        )
        self.assertTrue(result["ok"], result)

    def test_no_changes_without_none_notice_fails(self) -> None:
        result = MOD.lint_delivery_card_change_notice(
            {
                "reality_boundary_check_status": "checked_unchanged",
                "reality_boundary_will_change": [],
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "card_change_delivery_notice_missing")

    def test_will_change_without_notice_fails(self) -> None:
        result = MOD.lint_delivery_card_change_notice(
            {
                "reality_boundary_will_change": ["RB-library-encryption"],
                "reality_boundary_check_status": "updated_on_delivery",
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "card_change_delivery_notice_missing")

    def test_will_change_with_notice_ok(self) -> None:
        notice: dict[str, Any] = {
            "emitted": True,
            "shown_to_user": True,
            "cards_updated": True,
            "items": [
                {
                    "kind": "reality_boundary",
                    "action": "update",
                    "fact_id": "RB-library-encryption",
                    "note_id": "n1",
                    "card_ids": ["c1"],
                    "summary": "已更新书库加密边界卡",
                }
            ],
        }
        result = MOD.lint_delivery_card_change_notice(
            {
                "reality_boundary_will_change": ["RB-library-encryption"],
                "reality_boundary_check_status": "updated_on_delivery",
                "card_change_delivery_notice": notice,
            }
        )
        self.assertTrue(result["ok"], result)

    def test_applied_without_updated_status_stale(self) -> None:
        result = MOD.lint_delivery_card_change_notice(
            {
                "reality_boundary_will_change": ["RB-library-encryption"],
                "reality_boundary_check_status": "checked_will_change",
                "card_change_delivery_notice": {
                    "emitted": True,
                    "shown_to_user": True,
                    "cards_updated": True,
                    "items": [
                        {
                            "kind": "reality_boundary",
                            "action": "update",
                            "fact_id": "RB-library-encryption",
                            "card_ids": ["c1"],
                            "summary": "updated",
                        }
                    ],
                },
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "reality_boundary_delivery_stale")

    def test_uit_will_change_with_notice_ok(self) -> None:
        result = MOD.lint_delivery_card_change_notice(
            {
                "route_ui_truth_will_change": ["UIT-bookshelf"],
                "route_ui_truth_check_status": "updated_on_delivery",
                "reality_boundary_will_change": [],
                "card_change_delivery_notice": {
                    "emitted": True,
                    "shown_to_user": True,
                    "cards_updated": True,
                    "items": [
                        {
                            "kind": "route_ui_truth",
                            "action": "update",
                            "fact_id": "UIT-bookshelf",
                            "note_id": "n-uit",
                            "card_ids": ["c-uit"],
                            "summary": "已更新书架界面真相卡与反面截图",
                        }
                    ],
                },
            }
        )
        self.assertTrue(result["ok"], result)

    def test_uit_will_change_without_updated_status_stale(self) -> None:
        result = MOD.lint_delivery_card_change_notice(
            {
                "route_ui_truth_will_change": ["UIT-bookshelf"],
                "route_ui_truth_check_status": "checked_will_change",
                "card_change_delivery_notice": {
                    "emitted": True,
                    "shown_to_user": True,
                    "cards_updated": True,
                    "items": [
                        {
                            "kind": "route_ui_truth",
                            "action": "update",
                            "fact_id": "UIT-bookshelf",
                            "card_ids": ["c-uit"],
                            "summary": "updated",
                        }
                    ],
                },
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "route_ui_truth_delivery_stale")


if __name__ == "__main__":
    unittest.main()
