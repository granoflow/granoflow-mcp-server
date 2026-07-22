#!/usr/bin/env python3
"""Tests for lint_change_impact_fanout.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_change_impact_fanout.py"

REQUIRED_SCOPES = [
    "product_docs",
    "project_work",
    "milestone_work",
    "tasks",
    "prototypes",
    "notes_cards",
    "experience_knowledge",
]


def load_module():
    spec = importlib.util.spec_from_file_location("lint_change_impact_fanout", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def closed_ok_ledger() -> dict:
    return {
        "at": "2026-07-21T13:00:00Z",
        "decision_summary": "Bottom nav four icons; comment entry leaves settings",
        "contract_loaded": True,
        "scan_terms": ["底栏", "评论", "阅读设置"],
        "scopes_checked": list(REQUIRED_SCOPES),
        "candidates": [
            {
                "entity_type": "product_doc",
                "entity_id": None,
                "path_or_title": "docs/11-product-V02.md",
                "hit_summary": "§5.9 bottom bar",
                "disposition": "updated",
                "reason": None,
                "evidence": {"content_sha256": None},
                "status": "done",
            },
            {
                "entity_type": "task_work",
                "entity_id": "9c4a43ac-9650-43de-af5b-2de5f1b39d5d",
                "path_or_title": "阅读设置 Task Work",
                "hit_summary": "settings had comment button",
                "disposition": "updated",
                "reason": None,
                "evidence": {
                    "content_sha256": "abc123",
                },
                "status": "done",
            },
            {
                "entity_type": "card",
                "entity_id": "card-1",
                "path_or_title": "unrelated card",
                "hit_summary": "mentions 评论 elsewhere",
                "disposition": "not_applicable",
                "reason": "About library sync comments, not reader chrome",
                "evidence": {},
                "status": "done",
            },
        ],
        "status": "closed",
    }


def product_truth_prototype_ledger() -> dict:
    ledger = closed_ok_ledger()
    ledger["decision_summary"] = "Finish-chapter control requires visible text label"
    ledger["decision_class"] = "product_truth_changing"
    ledger["product_truth_writeback_loaded"] = True
    ledger["scan_terms"] = ["播完本章再停", "听书"]
    ledger["candidates"] = [
        {
            "entity_type": "prototype",
            "entity_id": "proto-tts",
            "path_or_title": "听书 ui_prototype",
            "hit_summary": "icon-only finish-chapter row",
            "disposition": "updated",
            "reason": None,
            "evidence": {
                "prototype_id": "proto-tts",
                "version_id": "v2",
                "package_sha256": "deadbeef",
            },
            "status": "done",
        },
        {
            "entity_type": "product_doc",
            "entity_id": None,
            "path_or_title": "docs/11-product-V02.md",
            "hit_summary": "§5.9 finish-chapter presentation",
            "disposition": "updated",
            "reason": None,
            "evidence": {},
            "status": "done",
        },
        {
            "entity_type": "task_work",
            "entity_id": "92f92cc1-tts",
            "path_or_title": "听书 Task Work",
            "hit_summary": "locked_product_contracts for visible label",
            "disposition": "updated",
            "reason": None,
            "evidence": {"content_sha256": "abc123"},
            "status": "done",
        },
        {
            "entity_type": "user_story",
            "entity_id": None,
            "path_or_title": "docs/12-user-stories-V01.md",
            "hit_summary": "US-010 listen controls",
            "disposition": "updated",
            "reason": None,
            "evidence": {},
            "status": "done",
        },
    ]
    return ledger


def craft_only_prototype_ledger() -> dict:
    return {
        "at": "2026-07-21T13:00:00Z",
        "decision_summary": "TTS timer row spacing rematch only",
        "decision_class": "craft_only",
        "product_truth_writeback_loaded": True,
        "contract_loaded": True,
        "scan_terms": ["听书", "定时"],
        "scopes_checked": list(REQUIRED_SCOPES),
        "candidates": [
            {
                "entity_type": "prototype",
                "entity_id": "proto-tts",
                "path_or_title": "听书 ui_prototype",
                "hit_summary": "spacing between timer chips",
                "disposition": "updated",
                "reason": None,
                "evidence": {
                    "prototype_id": "proto-tts",
                    "package_sha256": "cafe",
                },
                "status": "done",
            },
            {
                "entity_type": "product_doc",
                "entity_id": None,
                "path_or_title": "docs/11-product-V02.md",
                "hit_summary": "§5.9 already encodes timer chips",
                "disposition": "not_applicable",
                "reason": "Craft-only; §5.9 already requires icon+15/30/60/90",
                "evidence": {},
                "status": "done",
            },
            {
                "entity_type": "user_story",
                "entity_id": None,
                "path_or_title": "docs/12-user-stories-V01.md",
                "hit_summary": "US-010",
                "disposition": "not_applicable",
                "reason": "No journey/entry change",
                "evidence": {},
                "status": "done",
            },
        ],
        "status": "closed",
    }


class LintChangeImpactFanoutTests(unittest.TestCase):
    def test_closed_ledger_ok(self) -> None:
        result = MOD.lint_document({"change_impact": [closed_ok_ledger()]})
        self.assertTrue(result["ok"], result)

    def test_unread_fails(self) -> None:
        ledger = closed_ok_ledger()
        ledger["contract_loaded"] = False
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("change_impact_unread", codes)

    def test_missing_scope_fails(self) -> None:
        ledger = closed_ok_ledger()
        ledger["scopes_checked"] = ["tasks", "prototypes"]
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("change_impact_ledger_incomplete", codes)

    def test_open_status_fails(self) -> None:
        ledger = closed_ok_ledger()
        ledger["status"] = "open"
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("change_impact_open_targets", codes)

    def test_updated_without_evidence_fails(self) -> None:
        ledger = closed_ok_ledger()
        ledger["candidates"][1]["evidence"] = {}
        ledger["candidates"][1]["path_or_title"] = None
        ledger["candidates"][1]["entity_id"] = None
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("change_impact_updated_missing_evidence", codes)

    def test_deferred_without_owner_fails(self) -> None:
        ledger = closed_ok_ledger()
        ledger["candidates"].append(
            {
                "entity_type": "milestone_work",
                "entity_id": "m1",
                "path_or_title": "M3 work",
                "hit_summary": "needs later rewrite",
                "disposition": "deferred",
                "reason": "user asked to wait",
                "evidence": {},
                "status": "done",
            }
        )
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("change_impact_deferred_unapproved", codes)

    def test_false_none_fails(self) -> None:
        ledger = closed_ok_ledger()
        ledger["claimed_none"] = True
        ledger["candidates"][0]["disposition"] = None
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("change_impact_false_none", codes)

    def test_cli_ok_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
            path.write_text(
                json.dumps({"change_impact": [closed_ok_ledger()]}),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])

    def test_cli_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
            path.write_text(json.dumps({"change_impact": []}), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)

    def test_product_truth_prototype_ok(self) -> None:
        result = MOD.lint_document({"change_impact": [product_truth_prototype_ledger()]})
        self.assertTrue(result["ok"], result)

    def test_craft_only_prototype_ok(self) -> None:
        result = MOD.lint_document({"change_impact": [craft_only_prototype_ledger()]})
        self.assertTrue(result["ok"], result)

    def test_prototype_updated_without_class_fails(self) -> None:
        ledger = product_truth_prototype_ledger()
        del ledger["decision_class"]
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_product_truth_class_required", codes)

    def test_product_truth_without_product_doc_fails(self) -> None:
        ledger = product_truth_prototype_ledger()
        ledger["candidates"] = [
            c for c in ledger["candidates"] if c["entity_type"] != "product_doc"
        ]
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_product_doc_writeback_required", codes)

    def test_product_truth_without_user_story_fails(self) -> None:
        ledger = product_truth_prototype_ledger()
        ledger["candidates"] = [c for c in ledger["candidates"] if c["entity_type"] != "user_story"]
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_user_story_disposition_required", codes)

    def test_prototype_without_writeback_load_fails(self) -> None:
        ledger = craft_only_prototype_ledger()
        ledger["product_truth_writeback_loaded"] = False
        result = MOD.lint_ledger(ledger)
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_product_truth_writeback_unread", codes)


if __name__ == "__main__":
    unittest.main()
