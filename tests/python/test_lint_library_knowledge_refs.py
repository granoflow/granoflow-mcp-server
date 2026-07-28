#!/usr/bin/env python3
"""Tests for lint_library_knowledge_refs.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_library_knowledge_refs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_library_knowledge_refs", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def ok_approved(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "name": "drift",
        "capability": "embedded_db",
        "capability_critical": True,
        "knowledge_ref": "LIB-pub-drift",
        "knowledge_link_status": "linked",
        "superseded_by": None,
        "knowledge_gap_reason": None,
    }
    row.update(overrides)
    return row


def ok_project(**overrides: Any) -> dict[str, Any]:
    deps: dict[str, Any] = {"approved": [ok_approved()]}
    deps.update(overrides.get("dependencies", {}))
    block: dict[str, Any] = {"engineering": {"dependencies": deps}}
    block.update({k: v for k, v in overrides.items() if k != "dependencies"})
    return block


class LintLibraryKnowledgeRefsTests(unittest.TestCase):
    def test_missing_block_fails(self) -> None:
        result = MOD.lint_library_knowledge_refs({})
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("library_knowledge_link_incomplete", codes)

    def test_invalid_ref_format(self) -> None:
        data = ok_project()
        data["engineering"]["dependencies"]["approved"][0]["knowledge_ref"] = "drift-note"
        result = MOD.lint_library_knowledge_refs(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("library_knowledge_ref_invalid", codes)

    def test_slug_mismatch_when_linked(self) -> None:
        data = ok_project()
        data["engineering"]["dependencies"]["approved"][0]["knowledge_ref"] = "LIB-pub-other"
        result = MOD.lint_library_knowledge_refs(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("library_knowledge_slug_mismatch", codes)

    def test_gap_requires_reason(self) -> None:
        data = ok_project()
        row = data["engineering"]["dependencies"]["approved"][0]
        row["knowledge_link_status"] = "gap"
        row["knowledge_ref"] = None
        result = MOD.lint_library_knowledge_refs(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("library_knowledge_link_incomplete", codes)

        row["knowledge_gap_reason"] = "Search deferred until App online"
        result = MOD.lint_library_knowledge_refs(data)
        self.assertTrue(result["ok"])

    def test_skeleton_ok_without_ref(self) -> None:
        data = ok_project()
        row = data["engineering"]["dependencies"]["approved"][0]
        row["knowledge_link_status"] = "skeleton"
        row["knowledge_ref"] = None
        result = MOD.lint_library_knowledge_refs(data, require_init_ready=True)
        self.assertTrue(result["ok"])

    def test_init_ready_requires_status_on_critical(self) -> None:
        data = ok_project()
        row = data["engineering"]["dependencies"]["approved"][0]
        row["knowledge_link_status"] = None
        result = MOD.lint_library_knowledge_refs(data, require_init_ready=True)
        self.assertFalse(result["ok"])

    def test_normalize_package_slug(self) -> None:
        self.assertEqual(MOD.normalize_package_slug("flutter_tts"), "flutter-tts")
        self.assertEqual(MOD.expected_knowledge_ref("flutter_tts"), "LIB-pub-flutter-tts")

    def test_superseded_requires_superseded_by(self) -> None:
        data = ok_project()
        row = data["engineering"]["dependencies"]["approved"][0]
        row["knowledge_link_status"] = "superseded"
        row["knowledge_ref"] = "LIB-pub-old-lib"
        result = MOD.lint_library_knowledge_refs(data)
        self.assertFalse(result["ok"])

        row["superseded_by"] = "LIB-pub-drift"
        result = MOD.lint_library_knowledge_refs(data)
        self.assertTrue(result["ok"])

    def test_linked_ok(self) -> None:
        result = MOD.lint_library_knowledge_refs(ok_project(), require_init_ready=True)
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
