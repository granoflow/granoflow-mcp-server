#!/usr/bin/env python3
"""Tests for lint_code_signing_strategy.py (CS-01..CS-10)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_code_signing_strategy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_code_signing_strategy", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _local_strategy(**overrides):
    base = {
        "schema": "granoflow_code_signing_strategy_v1",
        "goal": "local_dev_run",
        "platform": "macos",
        "selected": {
            "id": "apple_adhoc_local",
            "label": "Free local / ad-hoc signing (no paid Apple Developer required)",
        },
        "evidence": {"existing_project_sign": 'CODE_SIGN_IDENTITY="-"'},
        "alternatives_rejected": [],
        "user_confirmation": "not_required",
        "declared_at": "2026-07-22T05:00:00Z",
    }
    base.update(overrides)
    return base


def _pw(default_signing_goal=None, include_goal=True):
    gates: dict = {}
    if include_goal and default_signing_goal is not None:
        gates["default_signing_goal"] = default_signing_goal
    elif include_goal and default_signing_goal is None:
        pass
    return {"engineering": {"quality_gates": gates}}


class LintCodeSigningStrategyTests(unittest.TestCase):
    def test_cs01_valid_local_strategy_ok(self) -> None:
        result = MOD.lint_code_signing_strategy(_local_strategy())
        self.assertTrue(result["ok"], result)

    def test_cs02_missing_required_fields_fails(self) -> None:
        for field in ("schema", "goal", "selected", "user_confirmation"):
            with self.subTest(field=field):
                strategy = _local_strategy()
                del strategy[field]
                result = MOD.lint_code_signing_strategy(strategy)
                self.assertFalse(result["ok"], result)
                codes = {err["code"] for err in result["errors"]}
                self.assertIn("code_signing_strategy_incomplete", codes)

    def test_cs03_user_confirmation_required_forbidden(self) -> None:
        result = MOD.lint_code_signing_strategy(_local_strategy(user_confirmation="required"))
        self.assertFalse(result["ok"])
        codes = {err["code"] for err in result["errors"]}
        self.assertIn("code_signing_user_confirmation_forbidden", codes)

    def test_cs04_local_goal_with_distribute_selected_fails(self) -> None:
        result = MOD.lint_code_signing_strategy(
            _local_strategy(
                selected={
                    "id": "distribute_store",
                    "label": "App Store distribution",
                }
            ),
            project_work=_pw(),
        )
        self.assertFalse(result["ok"])
        codes = {err["code"] for err in result["errors"]}
        self.assertIn("code_signing_goal_distribution_mismatch", codes)

    def test_cs05_distribute_goal_with_pw_ok(self) -> None:
        result = MOD.lint_code_signing_strategy(
            _local_strategy(
                goal="distribute_store",
                selected={
                    "id": "distribute_store",
                    "label": "App Store distribution",
                },
            ),
            project_work=_pw(default_signing_goal="distribute_store"),
        )
        self.assertTrue(result["ok"], result)

    def test_cs06_default_signing_goal_omitted_ok(self) -> None:
        result = MOD.lint_default_signing_goal(_pw(include_goal=True))
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["effective_goal"], "local_dev_run")

    def test_cs06b_default_signing_goal_explicit_local_ok(self) -> None:
        result = MOD.lint_default_signing_goal(_pw(default_signing_goal="local_dev_run"))
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["effective_goal"], "local_dev_run")

    def test_cs07_illegal_default_signing_goal_fails(self) -> None:
        result = MOD.lint_default_signing_goal(_pw(default_signing_goal="paid_only"))
        self.assertFalse(result["ok"])
        codes = {err["code"] for err in result["errors"]}
        self.assertIn("code_signing_default_goal_invalid", codes)

    def test_cs08_require_strategy_missing_fails(self) -> None:
        result = MOD.lint_code_signing_strategy(
            None,
            require_strategy=True,
        )
        self.assertFalse(result["ok"])
        codes = {err["code"] for err in result["errors"]}
        self.assertIn("code_signing_strategy_missing", codes)

    def test_cs09_alternatives_rejected_list_ok(self) -> None:
        result = MOD.lint_code_signing_strategy(
            _local_strategy(
                alternatives_rejected=[
                    {
                        "id": "keychain_access_groups_entitlement",
                        "reason": "Requires development certificate; breaks ad-hoc",
                    }
                ]
            )
        )
        self.assertTrue(result["ok"], result)

    def test_cs10_other_local_selected_ids_ok(self) -> None:
        for selected_id in (
            "free_apple_id_device",
            "android_debug_keystore",
            "windows_unsigned_local",
            "other_local_custom",
        ):
            with self.subTest(selected_id=selected_id):
                result = MOD.lint_code_signing_strategy(
                    _local_strategy(
                        selected={
                            "id": selected_id,
                            "label": f"Local path {selected_id}",
                        }
                    )
                )
                self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
