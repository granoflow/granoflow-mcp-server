#!/usr/bin/env python3
"""Tests for lint_prototype_revision_ledger.py."""

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
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_prototype_revision_ledger.py"
)
SHA = "a" * 64


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_revision_ledger", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


SHA_MATRIX = "b" * 64
SHA_NOTES = "c" * 64


def _draft(
    ordinal: int,
    *,
    blocking_in: int = 0,
    blocking_out: int = 0,
    include_stack_gates: bool = True,
) -> dict:
    row = {
        "ordinal": ordinal,
        "html_paths": [f"/tmp/draft-{ordinal}.html"],
        "package_sha256": SHA,
        "pre_review": {"blocking_count": 0, "advisory_count": 0, "evidence_refs": []},
        "post_review": {
            "blocking_count": blocking_out,
            "advisory_count": 0,
            "evidence_refs": [],
        },
        "blocking_in": blocking_in,
        "blocking_out": blocking_out,
    }
    if include_stack_gates:
        row["component_effect_matrix_sha256"] = SHA_MATRIX
        row["stack_realization_notes_sha256"] = SHA_NOTES
    return row


def base_ok(
    *,
    n: int = 1,
    mode: str = "interactive",
    status: str = "ready_for_selection",
    stop_reason: str = "zero_blocking",
    accepted: bool = False,
) -> dict:
    drafts = []
    for i in range(1, n + 1):
        blocking_in = 0 if i == 1 else 1
        blocking_out = 0 if i == n else 1
        drafts.append(_draft(i, blocking_in=blocking_in, blocking_out=blocking_out))
    surface_start = max(1, n - 2)
    ordinals = list(range(surface_start, n + 1))
    if n == 1:
        selection_mode = "confirm_or_revise"
    elif mode == "unattended":
        selection_mode = "auto_adopt"
    else:
        selection_mode = "pick_among"
    if mode == "unattended":
        selection_mode = "auto_adopt"
    ledger: dict = {
        "schema": "granoflow_prototype_revision_ledger_v1",
        "contract_loaded": True,
        "mode": mode,
        "status": "accepted" if accepted else status,
        "drafts": drafts,
        "stop_reason": stop_reason,
        "selection_surface": {
            "draft_ordinals": ordinals,
            "selection_mode": selection_mode,
            "recommended_ordinal": n,
        },
        "accepted_ordinal": n if accepted else None,
        "accepted_package_sha256": SHA if accepted else None,
    }
    return {"prototype_revision_ledger": ledger}


class LintPrototypeRevisionLedgerTests(unittest.TestCase):
    def test_single_draft_confirm_or_revise_ok(self) -> None:
        result = MOD.lint_prototype_revision_ledger(base_ok(n=1))
        self.assertTrue(result["ok"], result)

    def test_three_draft_surface_last_three(self) -> None:
        data = base_ok(n=4)
        # last min(4,3) = [2,3,4]
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertTrue(result["ok"], result)
        surface = data["prototype_revision_ledger"]["selection_surface"]
        self.assertEqual(surface["draft_ordinals"], [2, 3, 4])
        self.assertEqual(surface["selection_mode"], "pick_among")

    def test_wrong_surface_ordinals_fail(self) -> None:
        data = base_ok(n=4)
        data["prototype_revision_ledger"]["selection_surface"]["draft_ordinals"] = [1, 2, 3]
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_revision_selection_invalid", codes)

    def test_single_draft_forced_pick_fails(self) -> None:
        data = base_ok(n=1)
        data["prototype_revision_ledger"]["selection_surface"]["selection_mode"] = "pick_among"
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_revision_selection_invalid", codes)

    def test_draft4_without_blocking_fails(self) -> None:
        data = base_ok(n=3)
        ledger = data["prototype_revision_ledger"]
        # Force a 4th draft with blocking_in=0
        ledger["drafts"][2]["blocking_out"] = 1
        ledger["drafts"].append(_draft(4, blocking_in=0, blocking_out=0))
        ledger["selection_surface"]["draft_ordinals"] = [2, 3, 4]
        ledger["selection_surface"]["selection_mode"] = "pick_among"
        ledger["selection_surface"]["recommended_ordinal"] = 4
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_revision_late_draft_without_blocking", codes)

    def test_max_five_ok(self) -> None:
        data = base_ok(n=5, stop_reason="zero_blocking")
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertTrue(result["ok"], result)

    def test_six_drafts_fail(self) -> None:
        data = base_ok(n=5)
        ledger = data["prototype_revision_ledger"]
        ledger["drafts"][4]["blocking_out"] = 1
        ledger["drafts"].append(_draft(6, blocking_in=1, blocking_out=0))
        ledger["selection_surface"]["draft_ordinals"] = [4, 5, 6]
        ledger["selection_surface"]["recommended_ordinal"] = 6
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_revision_max_drafts", codes)

    def test_early_stop_required(self) -> None:
        data = base_ok(n=1)
        ledger = data["prototype_revision_ledger"]
        ledger["drafts"][0]["blocking_out"] = 0
        ledger["drafts"].append(_draft(2, blocking_in=1, blocking_out=0))
        ledger["selection_surface"]["draft_ordinals"] = [1, 2]
        ledger["selection_surface"]["selection_mode"] = "pick_among"
        ledger["selection_surface"]["recommended_ordinal"] = 2
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_revision_lint_failed", codes)

    def test_unattended_auto_adopt_ok(self) -> None:
        data = base_ok(n=2, mode="unattended", accepted=True)
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertTrue(result["ok"], result)

    def test_max_drafts_with_blocking_cannot_ready(self) -> None:
        data = base_ok(n=5, stop_reason="max_drafts")
        ledger = data["prototype_revision_ledger"]
        ledger["drafts"][4]["blocking_out"] = 2
        ledger["drafts"][4]["post_review"]["blocking_count"] = 2
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_revision_blocking_residual", codes)

    def test_missing_ledger_fails(self) -> None:
        result = MOD.lint_prototype_revision_ledger({"prototype_option_set": {}})
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "prototype_revision_ledger_required")

    def test_ready_without_stack_gate_shas_fails(self) -> None:
        data = base_ok(n=1)
        draft = data["prototype_revision_ledger"]["drafts"][0]
        del draft["component_effect_matrix_sha256"]
        del draft["stack_realization_notes_sha256"]
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_revision_stack_gates_incomplete", codes)

    def test_in_progress_allows_missing_stack_gate_shas(self) -> None:
        data = base_ok(n=1, status="in_progress")
        data["prototype_revision_ledger"]["stop_reason"] = None
        draft = data["prototype_revision_ledger"]["drafts"][0]
        del draft["component_effect_matrix_sha256"]
        del draft["stack_realization_notes_sha256"]
        result = MOD.lint_prototype_revision_ledger(data)
        self.assertTrue(result["ok"], result)

    def test_cli_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record.json"
            path.write_text(json.dumps({"prototype_option_set": {}}), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
