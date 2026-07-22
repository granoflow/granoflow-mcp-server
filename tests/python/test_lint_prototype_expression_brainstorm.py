#!/usr/bin/env python3
"""Tests for lint_prototype_expression_brainstorm.py."""

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
    / "lint_prototype_expression_brainstorm.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_expression_brainstorm", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _ref(i: int, *, discarded: bool = False, promote_as: str | None = None) -> dict:
    item: dict = {
        "id": f"r{i}",
        "product": f"Product{i}",
        "surface": "reader chrome",
        "transferable_axes": ["density", "chrome_pattern"],
        "thesis": f"thesis {i}",
        "covers_full_scope": True,
        "discarded": discarded,
    }
    if promote_as:
        item["promote_as"] = promote_as
        item["discarded"] = False
    return item


def _cand(
    i: int,
    *,
    source: str = "mainstream",
    discarded: bool = True,
    promote_as: str | None = None,
    covers: bool = True,
) -> dict:
    item: dict = {
        "id": f"c{i}",
        "source": source,
        "thesis": f"thesis {i}",
        "covers_full_scope": covers,
        "discarded": discarded,
    }
    if promote_as:
        item["promote_as"] = promote_as
        item["discarded"] = False
    if discarded:
        item["discard_reason"] = "not selected"
    return item


def base_task_ok(*, mainstream_n: int = 5, backfill_n: int = 0) -> dict:
    mainstream = [_ref(i) for i in range(1, mainstream_n + 1)]
    backfill = []
    for i in range(1, backfill_n + 1):
        backfill.append(
            {
                "id": f"b{i}",
                "thesis": f"backfill {i}",
                "covers_full_scope": True,
                "discarded": True,
                "discard_reason": "not selected",
            }
        )
    total = mainstream_n + backfill_n
    candidates = []
    for i in range(1, total + 1):
        source = "mainstream" if i <= mainstream_n else "brainstorm_backfill"
        promote = None
        discarded = True
        if i == 1:
            promote = "expr_a"
            discarded = False
        elif i == 2:
            promote = "expr_b"
            discarded = False
        candidates.append(_cand(i, source=source, discarded=discarded, promote_as=promote))
    record: dict = {
        "status": "recorded",
        "layer": "task_page_expression",
        "source_strategy": "mainstream_first",
        "scope_mode": "same_category",
        "scope_mode_rationale": "rich ebook reader peers",
        "mainstream_references": mainstream,
        "brainstorm_backfill": backfill,
        "brainstorm_backfill_reason": (
            "only three close peers; invented two presentation theses" if backfill_n else None
        ),
        "candidate_count": total,
        "promote_count": 2,
        "candidates": candidates,
        "selected": {"expr_a": "c1", "expr_b": "c2"},
        "selection_rationale": "best density and chrome fit for our Scope",
        "parity_check": {
            "same_capabilities": True,
            "same_data_fields": True,
            "same_required_states": True,
        },
        "loaded_reference_sha256": "abc",
    }
    return {"expression_brainstorm": record}


class LintPrototypeExpressionBrainstormTests(unittest.TestCase):
    def test_t1_five_mainstream_no_backfill_ok(self) -> None:
        result = MOD.lint_document(base_task_ok(mainstream_n=5, backfill_n=0))
        self.assertTrue(result["ok"], result)

    def test_t2_three_mainstream_two_backfill_ok(self) -> None:
        result = MOD.lint_document(base_task_ok(mainstream_n=3, backfill_n=2))
        self.assertTrue(result["ok"], result)

    def test_t3_mainstream_ge5_with_backfill_fails(self) -> None:
        data = base_task_ok(mainstream_n=5, backfill_n=0)
        data["expression_brainstorm"]["brainstorm_backfill"] = [
            {
                "id": "b1",
                "thesis": "extra",
                "covers_full_scope": True,
                "discarded": True,
                "discard_reason": "pad",
            }
        ]
        data["expression_brainstorm"]["candidate_count"] = 6
        data["expression_brainstorm"]["candidates"].append(_cand(6, source="brainstorm_backfill"))
        result = MOD.lint_document(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_option_mainstream_skip", codes)

    def test_t4_short_pool_without_backfill_fails(self) -> None:
        data = base_task_ok(mainstream_n=3, backfill_n=0)
        data["expression_brainstorm"]["candidate_count"] = 3
        data["expression_brainstorm"]["candidates"] = data["expression_brainstorm"]["candidates"][
            :3
        ]
        data["expression_brainstorm"]["brainstorm_backfill"] = []
        data["expression_brainstorm"]["brainstorm_backfill_reason"] = None
        result = MOD.lint_document(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_option_brainstorm_incomplete", codes)

    def test_t5_ambiguous_default_capability_match_ok(self) -> None:
        data = base_task_ok(mainstream_n=5, backfill_n=0)
        data["expression_brainstorm"]["scope_mode"] = "capability_match"
        data["expression_brainstorm"]["scope_mode_rationale"] = "ambiguous_default_capability_match"
        result = MOD.lint_document(data)
        self.assertTrue(result["ok"], result)

    def test_t6_illegal_scope_mode_fails(self) -> None:
        data = base_task_ok()
        data["expression_brainstorm"]["scope_mode"] = "foobar"
        result = MOD.lint_document(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_option_scope_mode_invalid", codes)

    def test_t7_promote_count_mismatch_fails(self) -> None:
        data = base_task_ok()
        data["expression_brainstorm"]["promote_count"] = 3
        data["expression_brainstorm"]["selected"] = {
            "expr_a": "c1",
            "expr_b": "c2",
            "industry_peer_c": "c3",
        }
        result = MOD.lint_document(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_option_promote_count_mismatch", codes)

        spec = base_task_ok()
        spec["expression_brainstorm"]["layer"] = "design_spec"
        spec["expression_brainstorm"]["promote_count"] = 2
        spec["expression_brainstorm"]["selected"] = {
            "spec_match": "c1",
            "ai_challenger_a": "c2",
        }
        result2 = MOD.lint_document(spec)
        self.assertFalse(result2["ok"])
        codes2 = {e["code"] for e in result2["errors"]}
        self.assertIn("prototype_option_promote_count_mismatch", codes2)

    def test_t8_promoted_incomplete_scope_fails(self) -> None:
        data = base_task_ok()
        data["expression_brainstorm"]["candidates"][0]["covers_full_scope"] = False
        result = MOD.lint_document(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_option_brainstorm_incomplete", codes)

    def test_t9_capability_match_cross_category_ok(self) -> None:
        data = base_task_ok(mainstream_n=5, backfill_n=0)
        data["expression_brainstorm"]["scope_mode"] = "capability_match"
        data["expression_brainstorm"]["scope_mode_rationale"] = (
            "TTS chrome: podcast and reader players share the capability"
        )
        for ref in data["expression_brainstorm"]["mainstream_references"]:
            ref["surface"] = "playback chrome"
        result = MOD.lint_document(data)
        self.assertTrue(result["ok"], result)

    def test_t10_missing_record_fails(self) -> None:
        result = MOD.lint_document({"prototype_option_set": {}})
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_option_brainstorm_missing", codes)

    def test_backfill_without_reason_fails(self) -> None:
        data = base_task_ok(mainstream_n=3, backfill_n=2)
        data["expression_brainstorm"]["brainstorm_backfill_reason"] = None
        result = MOD.lint_document(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_option_backfill_unjustified", codes)

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
