#!/usr/bin/env python3
"""Tests for lint_third_party_capability_matrix.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_third_party_capability_matrix.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_third_party_capability_matrix", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def ok_row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "capability": "tts",
        "library": "example_tts",
        "user_visible": True,
        "required_platforms": ["ios", "android"],
        "probe_method": "runtime_call",
        "fallback": "Show TTS unavailable; reading continues",
        "in_ship_bar": True,
        "probe_by_platform": {"ios": "available", "android": "available"},
        "ao_ids": ["AO-tts"],
        "residual_code": None,
    }
    row.update(overrides)
    return row


def ok_matrix(**overrides: Any) -> dict[str, Any]:
    block: dict[str, Any] = {
        "schema": "granoflow_third_party_capabilities_v1",
        "contract_loaded": True,
        "status": "complete",
        "no_user_visible_third_party_declaration": None,
        "rows": [ok_row()],
    }
    block.update(overrides)
    return {"third_party_capabilities": block}


class LintThirdPartyCapabilityMatrixTests(unittest.TestCase):
    def test_missing_block_fails(self) -> None:
        result = MOD.lint_third_party_capability_matrix({})
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("third_party_capability_matrix_unloaded", codes)

    def test_not_applicable_requires_declaration(self) -> None:
        data = ok_matrix(status="not_applicable", rows=[])
        result = MOD.lint_third_party_capability_matrix(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("third_party_capability_matrix_incomplete", codes)

        data = ok_matrix(
            status="not_applicable",
            rows=[],
            no_user_visible_third_party_declaration=(
                "No user-visible third-party host capabilities"
            ),
        )
        result = MOD.lint_third_party_capability_matrix(data)
        self.assertTrue(result["ok"], result)

    def test_user_visible_requires_fallback(self) -> None:
        data = ok_matrix(rows=[ok_row(fallback="")])
        result = MOD.lint_third_party_capability_matrix(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("third_party_capability_fallback_missing", codes)

    def test_missing_probe_key_when_complete(self) -> None:
        data = ok_matrix(rows=[ok_row(probe_by_platform={"ios": "available"})])
        result = MOD.lint_third_party_capability_matrix(data, require_complete=True)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("third_party_capability_platform_missing", codes)

    def test_unprobed_under_full_platform_claim(self) -> None:
        data = ok_matrix(
            rows=[
                ok_row(
                    probe_by_platform={
                        "ios": "available",
                        "android": "unprobed",
                    }
                )
            ]
        )
        result = MOD.lint_third_party_capability_matrix(data, claim_full_platform=True)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("third_party_capability_unprobed", codes)
        self.assertIn("third_party_capability_overclaim", codes)

    def test_unavailable_under_full_platform_claim(self) -> None:
        data = ok_matrix(
            rows=[
                ok_row(
                    probe_by_platform={
                        "ios": "available",
                        "android": "unavailable",
                    }
                )
            ]
        )
        result = MOD.lint_third_party_capability_matrix(data, claim_full_platform=True)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("third_party_capability_overclaim", codes)

    def test_ship_bar_excluded_needs_residual(self) -> None:
        data = ok_matrix(
            rows=[
                ok_row(
                    in_ship_bar=False,
                    residual_code=None,
                    ship_bar_leftover=None,
                )
            ]
        )
        result = MOD.lint_third_party_capability_matrix(data, require_complete=True)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("third_party_capability_ship_bar_excluded", codes)

        data = ok_matrix(
            rows=[
                ok_row(
                    in_ship_bar=False,
                    residual_code="deferred_manual_tts_desktop",
                )
            ]
        )
        result = MOD.lint_third_party_capability_matrix(data, require_complete=True)
        self.assertTrue(result["ok"], result)

    def test_engineering_nested_path_ok(self) -> None:
        data = {
            "engineering": {"third_party_capabilities": ok_matrix()["third_party_capabilities"]}
        }
        result = MOD.lint_third_party_capability_matrix(data)
        self.assertTrue(result["ok"], result)

    def test_complete_ok(self) -> None:
        result = MOD.lint_third_party_capability_matrix(ok_matrix(), require_complete=True)
        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
