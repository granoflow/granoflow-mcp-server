#!/usr/bin/env python3
"""Tests for lint_prototype_doc_coverage.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_prototype_doc_coverage.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_doc_coverage", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def ok_coverage_row(**overrides: Any) -> dict:
    row: dict[str, Any] = {
        "page_id": "S-welcome",
        "element_id": "primary_cta",
        "kind": "control",
        "task_work_locus": "locked_product_contracts.primary_cta",
        "project_work_locus": "journeys.J-001.create_cta",
        "coverage": "covered",
        "note": "创建书库",
    }
    row.update(overrides)
    return row


def ok_coverage(**overrides: Any) -> dict:
    block: dict[str, Any] = {
        "schema": "granoflow_prototype_doc_coverage_v1",
        "contract_loaded": True,
        "prototype_id": "proto-1",
        "version_id": "v1",
        "status": "complete",
        "rows": [ok_coverage_row()],
    }
    block.update(overrides)
    return {"prototype_doc_coverage": block}


def ok_plan_truth(**overrides: Any) -> dict:
    block: dict[str, Any] = {
        "schema": "granoflow_prototype_plan_truth_v1",
        "contract_loaded": True,
        "prototype_is_source_of_truth": True,
        "status": "aligned",
        "conflicts": [],
        "user_notified": False,
        "user_resolution": "not_applicable",
        "task_work_updated": "not_applicable",
        "project_work_updated": "not_applicable",
    }
    block.update(overrides)
    return {"prototype_plan_truth": block}


def ok_html_surface(**overrides: Any) -> dict:
    row: dict[str, Any] = {
        "surface_id": "S-settings",
        "kind": "page",
        "label": "Settings",
        "html_prototype_ref": "options/expr_a/settings.html",
        "coverage": "covered",
    }
    row.update(overrides)
    return row


def ok_html_coverage(**overrides: Any) -> dict:
    block: dict[str, Any] = {
        "schema": "granoflow_prototype_html_coverage_v1",
        "contract_loaded": True,
        "prototype_id": "proto-1",
        "version_id": "v1",
        "status": "complete",
        "surfaces": [ok_html_surface()],
    }
    block.update(overrides)
    return {"prototype_html_coverage": block}


def ok_widget_declaration(**overrides: Any) -> dict:
    row: dict[str, Any] = {
        "role": "shell.primary_nav",
        "widget_id": "shell.primary_nav",
        "action": "reused",
        "html_surfaces": ["S-home"],
    }
    row.update(overrides)
    return row


def ok_widget_reuse(**overrides: Any) -> dict:
    block: dict[str, Any] = {
        "schema": "granoflow_prototype_widget_reuse_v1",
        "contract_loaded": True,
        "catalog_sha256": "abc",
        "status": "complete",
        "declarations": [ok_widget_declaration()],
    }
    block.update(overrides)
    return {"prototype_widget_reuse": block}


def sample_widgets_catalog() -> dict:
    return {
        "schema": "granoflow.widgets",
        "widgets": [
            {
                "id": "shell.primary_nav",
                "kind": "chrome",
                "reuse_policy": "must_reuse_when_same_role",
            }
        ],
    }


class LintPrototypeDocCoverageTests(unittest.TestCase):
    def test_complete_ok(self) -> None:
        result = MOD.lint_prototype_doc_coverage(ok_coverage())
        self.assertTrue(result["ok"], result)

    def test_unread_fails(self) -> None:
        data = ok_coverage(contract_loaded=False)
        result = MOD.lint_prototype_doc_coverage(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_doc_coverage_unread", codes)

    def test_missing_row_on_complete_fails(self) -> None:
        data = ok_coverage(rows=[ok_coverage_row(coverage="missing")])
        result = MOD.lint_prototype_doc_coverage(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_doc_coverage_gap", codes)

    def test_conflict_row_on_complete_fails(self) -> None:
        data = ok_coverage(rows=[ok_coverage_row(coverage="conflict")])
        result = MOD.lint_prototype_doc_coverage(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_doc_conflict", codes)

    def test_complete_empty_rows_fails(self) -> None:
        data = ok_coverage(rows=[])
        result = MOD.lint_prototype_doc_coverage(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_doc_coverage_incomplete", codes)

    def test_pending_with_gap_ok_structurally(self) -> None:
        data = ok_coverage(
            status="pending",
            rows=[ok_coverage_row(coverage="missing")],
        )
        result = MOD.lint_prototype_doc_coverage(data)
        self.assertTrue(result["ok"], result)


class LintPrototypeHtmlCoverageTests(unittest.TestCase):
    def test_complete_ok(self) -> None:
        result = MOD.lint_prototype_html_coverage(ok_html_coverage())
        self.assertTrue(result["ok"], result)

    def test_unread_fails(self) -> None:
        data = ok_html_coverage(contract_loaded=False)
        result = MOD.lint_prototype_html_coverage(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_html_coverage_unread", codes)

    def test_missing_surface_on_complete_lists_gaps(self) -> None:
        data = ok_html_coverage(
            surfaces=[
                ok_html_surface(),
                ok_html_surface(
                    surface_id="S-delete-dialog",
                    kind="dialog",
                    coverage="missing",
                    html_prototype_ref="",
                ),
            ]
        )
        result = MOD.lint_prototype_html_coverage(data)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "prototype_html_coverage_gap")
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_html_coverage_gap", codes)
        self.assertIn("S-delete-dialog", result["gaps"])
        summary = [e for e in result["errors"] if e["detail"].startswith("gaps:")]
        self.assertTrue(summary)
        self.assertIn("S-delete-dialog", summary[0]["detail"])

    def test_complete_empty_surfaces_fails(self) -> None:
        data = ok_html_coverage(surfaces=[])
        result = MOD.lint_prototype_html_coverage(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_html_coverage_incomplete", codes)

    def test_pending_with_missing_ok_structurally(self) -> None:
        data = ok_html_coverage(
            status="pending",
            surfaces=[ok_html_surface(coverage="missing", html_prototype_ref="")],
        )
        result = MOD.lint_prototype_html_coverage(data)
        self.assertTrue(result["ok"], result)


class LintPrototypeWidgetReuseTests(unittest.TestCase):
    def test_reused_ok(self) -> None:
        data = ok_widget_reuse()
        result = MOD.lint_prototype_widget_reuse(data, sample_widgets_catalog())
        self.assertTrue(result["ok"], result)

    def test_unread_fails(self) -> None:
        data = ok_widget_reuse(contract_loaded=False)
        result = MOD.lint_prototype_widget_reuse(data, sample_widgets_catalog())
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_widget_reuse_unread", codes)

    def test_new_role_when_catalog_exists_fails(self) -> None:
        data = ok_widget_reuse(
            declarations=[
                ok_widget_declaration(
                    action="new_role",
                    widget_id="shell.primary_nav_v2",
                )
            ]
        )
        result = MOD.lint_prototype_widget_reuse(data, sample_widgets_catalog())
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "widget_reuse_required")

    def test_near_duplicate_same_role_fails(self) -> None:
        data = ok_widget_reuse(
            declarations=[
                ok_widget_declaration(role="shell.primary_nav", widget_id="shell.primary_nav"),
                ok_widget_declaration(role="shell.primary_nav", widget_id="shell.primary_nav_alt"),
            ]
        )
        result = MOD.lint_prototype_widget_reuse(data, sample_widgets_catalog())
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("widget_reuse_required", codes)

    def test_wrong_widget_id_for_catalog_role_fails(self) -> None:
        data = ok_widget_reuse(
            declarations=[
                ok_widget_declaration(
                    widget_id="shell.custom_nav",
                    action="reused",
                )
            ]
        )
        result = MOD.lint_prototype_widget_reuse(data, sample_widgets_catalog())
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "widget_reuse_required")


class LintPrototypePlanTruthTests(unittest.TestCase):
    def test_aligned_ok(self) -> None:
        result = MOD.lint_prototype_plan_truth(ok_plan_truth())
        self.assertTrue(result["ok"], result)

    def test_conflict_pending_fails(self) -> None:
        data = ok_plan_truth(
            status="conflict",
            conflicts=[
                {
                    "page_id": "S-tts",
                    "field": "timer_chips",
                    "prototype_says": "15/30/60/90",
                    "task_work_says": "speed slider only",
                    "recommendation": "Update Task Work + Project Work to include timer chips",
                }
            ],
            user_notified=True,
            user_resolution="pending",
        )
        result = MOD.lint_prototype_plan_truth(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_plan_truth_conflict", codes)

    def test_conflict_unnotified_fails(self) -> None:
        data = ok_plan_truth(
            status="conflict",
            conflicts=[
                {
                    "page_id": "S-tts",
                    "field": "timer_chips",
                    "prototype_says": "15/30/60/90",
                    "task_work_says": "absent",
                    "recommendation": "Add timer chips to Task Work",
                }
            ],
            user_notified=False,
            user_resolution="accepted_doc_update",
            task_work_updated=True,
            project_work_updated="not_applicable",
        )
        result = MOD.lint_prototype_plan_truth(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_plan_truth_unnotified", codes)

    def test_accepted_without_doc_update_fails(self) -> None:
        data = ok_plan_truth(
            status="conflict",
            conflicts=[
                {
                    "page_id": "S-tts",
                    "field": "timer_chips",
                    "prototype_says": "15/30/60/90",
                    "task_work_says": "absent",
                    "recommendation": "Add timer chips to Task Work",
                }
            ],
            user_notified=True,
            user_resolution="accepted_doc_update",
            task_work_updated=False,
            project_work_updated="not_applicable",
        )
        result = MOD.lint_prototype_plan_truth(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_plan_truth_docs_stale", codes)

    def test_accepted_doc_update_ok(self) -> None:
        data = ok_plan_truth(
            status="conflict",
            conflicts=[
                {
                    "page_id": "S-tts",
                    "field": "timer_chips",
                    "prototype_says": "15/30/60/90",
                    "task_work_says": "absent",
                    "recommendation": "Add timer chips to Task Work",
                }
            ],
            user_notified=True,
            user_resolution="accepted_doc_update",
            task_work_updated=True,
            project_work_updated=True,
        )
        result = MOD.lint_prototype_plan_truth(data)
        self.assertTrue(result["ok"], result)

    def test_sot_false_fails(self) -> None:
        data = ok_plan_truth(prototype_is_source_of_truth=False)
        result = MOD.lint_prototype_plan_truth(data)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("prototype_plan_truth_sot_invalid", codes)


if __name__ == "__main__":
    unittest.main()
