#!/usr/bin/env python3
"""Tests for lint_integration_campaign_artifacts.py (TC03–TC14 structural gates)."""

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
    / "granoflow-integration-test-campaign"
    / "scripts"
    / "lint_integration_campaign_artifacts.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_integration_campaign_artifacts", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def ok_acceptance_outcomes(*, with_deferred: bool = False) -> dict:
    rows = [
        {
            "id": "AO-comment-persisted",
            "statement": "评论已真实写入存储并可被后续步骤读取",
            "layer": "domain_io",
            "evidence_kind": "real_side_effect",
            "status": "closed",
            "case_ids": ["add_comment", "browse_comments"],
        }
    ]
    if with_deferred:
        rows.append(
            {
                "id": "AO-comment-ui",
                "statement": "用户在界面完成添加评论",
                "layer": "ui_human_path",
                "evidence_kind": "real_side_effect",
                "status": "deferred_e2e",
                "case_ids": [],
            }
        )
    return {
        "acceptance_outcomes_loaded": True,
        "user_path_claim": "service_layers_only",
        "acceptance_outcomes": rows,
    }


def ok_suite_plan() -> dict:
    plan = {
        "schema": "granoflow_integration_suite_plan_v1",
        "contract_loaded": True,
        "orchestration_loaded": True,
        "special_requirements_loaded": True,
        "special_requirements_applied": [],
        "test_layer": "integration",
        "interaction_fidelity": "service_path",
        "cases": [
            {
                "id": "add_comment",
                "path": "test/integration/add_comment_test.dart",
                "requires": [],
                "produces": ["comment_exists"],
                "mutates": [],
                "destroys": [],
                "entry_style": "service_path",
            },
            {
                "id": "browse_comments",
                "path": "test/integration/browse_comments_test.dart",
                "requires": ["comment_exists"],
                "produces": [],
                "mutates": [],
                "destroys": [],
                "entry_style": "service_path",
            },
            {
                "id": "delete_comment",
                "path": "test/integration/delete_comment_test.dart",
                "requires": ["comment_exists"],
                "produces": [],
                "mutates": [],
                "destroys": ["comment_exists"],
                "entry_style": "service_path",
            },
        ],
        "order": ["add_comment", "browse_comments", "delete_comment"],
    }
    plan.update(ok_acceptance_outcomes())
    return plan


def ok_change_report_changes() -> dict:
    return {
        "schema": "granoflow_integration_campaign_change_report_v1",
        "status": "changes_present",
        "product_changes": [
            {
                "path": "lib/comments/delete.dart",
                "symbols": ["DeleteCommentUseCase"],
            }
        ],
        "test_changes": [],
        "product_behavior_delta": "Delete confirms before removing the comment.",
        "why": "product_code: delete skipped confirmation and left stale list rows",
        "failed_before": [
            {
                "id": "delete_comment",
                "symptom": "list still showed deleted comment",
            }
        ],
        "passed_after_evidence": "orchestrated suite round 2 green; log ref suite-r2",
    }


def ok_change_report_none() -> dict:
    return {
        "schema": "granoflow_integration_campaign_change_report_v1",
        "status": "no_code_changes",
        "product_changes": [],
        "test_changes": [],
        "product_behavior_delta": "none",
        "why": "suite green on first orchestrated run",
        "failed_before": [],
        "passed_after_evidence": "orchestrated suite round 1 green",
    }


def ok_campaign_state() -> dict:
    return {
        "schema": "granoflow_integration_campaign_state_v1",
        "campaign_id": "c1",
        "project_id": "p1",
        "campaign_drive": "agent_auto",
        "interaction_fidelity": "service_path",
        "fix_schedule": "deferred_batch",
        "fix_schedule_rationale": "failures look independent; collect then cluster",
        "phase": "fixing_bugs",
        "failures": [
            {
                "case_id": "delete_comment",
                "failure_class": "product_code",
                "summary": "stale list row",
            }
        ],
    }


class LintSuitePlanTests(unittest.TestCase):
    def test_ok_minimal_path_order(self) -> None:
        result = MOD.lint_suite_plan(ok_suite_plan())
        self.assertTrue(result["ok"], result)

    def test_unorchestrated_missing_flags(self) -> None:
        plan = ok_suite_plan()
        plan["orchestration_loaded"] = False
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_suite_unorchestrated", codes)

    def test_consumer_before_producer_fails(self) -> None:
        plan = ok_suite_plan()
        plan["order"] = ["delete_comment", "add_comment", "browse_comments"]
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_order_dependency_violation", codes)

    def test_ui_probe_without_justification_fails(self) -> None:
        plan = ok_suite_plan()
        plan["cases"][2]["entry_style"] = "ui_probe"
        plan["cases"][2]["ui_probe_justified"] = None
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_ui_probe_unjustified", codes)

    def test_ui_probe_with_justification_ok(self) -> None:
        plan = ok_suite_plan()
        plan["cases"][0]["entry_style"] = "ui_probe"
        plan["cases"][0]["ui_probe_justified"] = (
            "thin widget mount only to assert service wiring; no journey clicks"
        )
        result = MOD.lint_suite_plan(plan)
        self.assertTrue(result["ok"], result)

    def test_invalid_fidelity_fails(self) -> None:
        plan = ok_suite_plan()
        plan["interaction_fidelity"] = "telepathy"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_fidelity_invalid", codes)

    def test_human_path_fidelity_wrong_layer(self) -> None:
        plan = ok_suite_plan()
        plan["interaction_fidelity"] = "human_path"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_fidelity_wrong_layer", codes)

    def test_human_path_entry_style_wrong_layer(self) -> None:
        plan = ok_suite_plan()
        plan["cases"][0]["entry_style"] = "human_path"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_fidelity_wrong_layer", codes)

    def test_vision_fields_not_allowed(self) -> None:
        plan = ok_suite_plan()
        plan["vision_acceptance"] = "off"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_vision_not_allowed", codes)

    def test_i1_screenshot_capability_not_allowed_on_suite(self) -> None:
        plan = ok_suite_plan()
        plan["screenshot_capability"] = "available"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_vision_not_allowed", codes)

    def test_i3_suite_without_screenshot_or_vision_fields_ok(self) -> None:
        plan = ok_suite_plan()
        result = MOD.lint_suite_plan(plan)
        self.assertTrue(result["ok"], result)

    def test_special_requirements_unloaded_fails(self) -> None:
        plan = ok_suite_plan()
        del plan["special_requirements_loaded"]
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_special_requirements_unloaded", codes)

    def test_project_work_seed_corpus_must_be_applied(self) -> None:
        plan = ok_suite_plan()
        plan["special_requirements_applied"] = ["ITR-001"]
        plan["seed_corpus_paths_used"] = [
            "docs/mary-shelley_frankenstein.epub",
            "docs/jane-austen_pride-and-prejudice.epub",
        ]
        project_work = {
            "engineering": {
                "quality_gates": {
                    "integration_test_special_requirements": [
                        {
                            "id": "ITR-001",
                            "kind": "seed_corpus",
                            "statement": "use fixed corpus",
                            "corpus_paths": [
                                "docs/mary-shelley_frankenstein.epub",
                                "docs/jane-austen_pride-and-prejudice.epub",
                            ],
                            "not_app_seed": True,
                            "applies_when": ["campaign_suite"],
                            "enforcement": "fail_closed",
                            "provenance": "user_stated",
                        }
                    ]
                }
            }
        }
        result = MOD.lint_suite_plan(plan, project_work=project_work)
        self.assertTrue(result["ok"], result)

    def test_project_work_seed_corpus_unapplied_fails(self) -> None:
        plan = ok_suite_plan()
        project_work = {
            "engineering": {
                "quality_gates": {
                    "integration_test_special_requirements": [
                        {
                            "id": "ITR-001",
                            "kind": "seed_corpus",
                            "statement": "use fixed corpus",
                            "corpus_paths": ["docs/a.epub"],
                            "applies_when": ["campaign_suite"],
                            "enforcement": "fail_closed",
                        }
                    ]
                }
            }
        }
        result = MOD.lint_suite_plan(plan, project_work=project_work)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_special_requirement_unapplied", codes)

    def test_seed_corpus_paths_missing_fails(self) -> None:
        plan = ok_suite_plan()
        plan["special_requirements_applied"] = ["ITR-001"]
        plan["seed_corpus_paths_used"] = ["docs/other.epub"]
        project_work = {
            "engineering": {
                "quality_gates": {
                    "integration_test_special_requirements": [
                        {
                            "id": "ITR-001",
                            "kind": "seed_corpus",
                            "statement": "use fixed corpus",
                            "corpus_paths": ["docs/a.epub"],
                            "applies_when": ["campaign_suite"],
                            "enforcement": "fail_closed",
                        }
                    ]
                }
            }
        }
        result = MOD.lint_suite_plan(plan, project_work=project_work)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_seed_corpus_substituted", codes)


class LintChangeReportTests(unittest.TestCase):
    def test_changes_present_ok(self) -> None:
        result = MOD.lint_change_report(ok_change_report_changes())
        self.assertTrue(result["ok"], result)

    def test_no_code_changes_ok(self) -> None:
        result = MOD.lint_change_report(ok_change_report_none())
        self.assertTrue(result["ok"], result)

    def test_code_changed_requires_report(self) -> None:
        result = MOD.lint_change_report(
            None,
            code_changed=True,
        )
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_change_report_missing", codes)

    def test_changes_present_missing_behavior_delta(self) -> None:
        report = ok_change_report_changes()
        report["product_behavior_delta"] = ""
        result = MOD.lint_change_report(report)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_change_report_incomplete", codes)

    def test_changes_present_missing_failed_before(self) -> None:
        report = ok_change_report_changes()
        report["failed_before"] = []
        result = MOD.lint_change_report(report)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_change_report_incomplete", codes)

    def test_no_code_changes_with_product_diff_fails(self) -> None:
        report = ok_change_report_none()
        report["product_changes"] = [{"path": "lib/x.dart", "symbols": []}]
        result = MOD.lint_change_report(report)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_change_report_inconsistent", codes)


class LintCampaignStateTests(unittest.TestCase):
    def test_ok_state(self) -> None:
        result = MOD.lint_campaign_state(ok_campaign_state())
        self.assertTrue(result["ok"], result)

    def test_drive_must_be_agent_auto(self) -> None:
        state = ok_campaign_state()
        state["campaign_drive"] = "ask_user"
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_drive_not_agent_auto", codes)

    def test_failure_class_required(self) -> None:
        state = ok_campaign_state()
        state["failures"][0].pop("failure_class")
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_failure_class_required", codes)

    def test_invalid_failure_class(self) -> None:
        state = ok_campaign_state()
        state["failures"][0]["failure_class"] = "vibes"
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_failure_class_invalid", codes)

    def test_fix_schedule_needs_rationale(self) -> None:
        state = ok_campaign_state()
        state["fix_schedule_rationale"] = ""
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_fix_schedule_rationale_missing", codes)

    def test_vision_fields_not_allowed_on_state(self) -> None:
        state = ok_campaign_state()
        state["vision_acceptance"] = "off"
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_vision_not_allowed", codes)

    def test_i2_screenshots_array_not_allowed_on_state(self) -> None:
        state = ok_campaign_state()
        state["screenshots"] = [
            {"step_id": "x", "path": "temp/integration-campaign/x.png"},
        ]
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_vision_not_allowed", codes)


def ok_closing_summary() -> dict:
    summary = {
        "schema": "granoflow_integration_campaign_closing_summary_v1",
        "contract_loaded": True,
        "plain_language_loaded": True,
        "audience": "beginner",
        "locale": "zh-Hans",
        "outcome": "green",
        "rounds_completed": 1,
        "code_changed": True,
        "plain": {
            "headline": "集成测试已经全部通过。",
            "what_we_checked": ("按模块协作顺序检查了：添加评论、读取评论列表、删除评论。"),
            "result": "以上检查都通过了，没有卡住的步骤。",
            "what_changed_for_you": (
                "删除评论前会多一步确认，避免误删。" "（以前点删除可能直接消失。）"
            ),
            "leftovers": "没有未完成事项。",
            "next_step": "可以说「开始 E2E 战役」继续界面路径检查。",
        },
        "change_report": ok_change_report_changes(),
        "markdown_body": """
## 一句话结论
集成测试已经全部通过。

## 这次查了什么
按模块协作顺序检查了：添加评论、读取评论列表、删除评论。

## 结果如何
以上检查都通过了。

## 对你有什么影响
删除评论前会多一步确认，避免误删。

## 还剩什么没做完
没有未完成事项。

## 下一步你可以做什么
可以说「开始 E2E 战役」。

## 给开发者看的细节
见 change_report。
""",
    }
    summary.update(ok_acceptance_outcomes())
    return summary


class LintClosingSummaryTests(unittest.TestCase):
    def test_ok_plain_summary(self) -> None:
        result = MOD.lint_closing_summary(ok_closing_summary())
        self.assertTrue(result["ok"], result)

    def test_missing_summary_when_complete(self) -> None:
        result = MOD.lint_closing_summary(None, campaign_complete=True)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_closing_summary_missing", codes)

    def test_jargon_only_headline_fails(self) -> None:
        summary = ok_closing_summary()
        summary["plain"]["headline"] = "phase: complete / campaign_drive agent_auto"
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_closing_summary_not_plain", codes)

    def test_path_only_user_impact_fails(self) -> None:
        summary = ok_closing_summary()
        summary["plain"]["what_changed_for_you"] = "lib/comments/delete.dart"
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_closing_summary_not_plain", codes)

    def test_code_changed_requires_embedded_change_report(self) -> None:
        summary = ok_closing_summary()
        summary.pop("change_report")
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_change_report_missing", codes)

    def test_missing_markdown_section_fails(self) -> None:
        summary = ok_closing_summary()
        summary["markdown_body"] = "## 一句话结论\n过了\n"
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_closing_summary_incomplete", codes)

    def test_no_code_changes_ok(self) -> None:
        summary = ok_closing_summary()
        summary["code_changed"] = False
        summary["change_report"] = ok_change_report_none()
        summary["plain"]["what_changed_for_you"] = (
            "应用对你来说没有变化；这次只整理了自动检查的顺序。"
        )
        result = MOD.lint_closing_summary(summary)
        self.assertTrue(result["ok"], result)

    def test_residuals_need_plain_leftovers(self) -> None:
        summary = ok_closing_summary()
        summary["outcome"] = "green_with_residuals"
        summary["residuals"] = [
            {"code": "integration_campaign_external_deferred", "detail": "needs device"}
        ]
        summary["plain"]["leftovers"] = "没有未完成事项。"
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_closing_summary_residual_unexplained", codes)

    def test_vision_fields_not_allowed_on_closing(self) -> None:
        summary = ok_closing_summary()
        summary["vision_acceptance"] = "off"
        summary["vision_result"] = "not_run"
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("integration_campaign_vision_not_allowed", codes)

    def test_ao_unloaded_fails(self) -> None:
        plan = ok_suite_plan()
        del plan["acceptance_outcomes_loaded"]
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("acceptance_outcomes_unloaded", codes)

    def test_ao_layer_overclaim_fails(self) -> None:
        plan = ok_suite_plan()
        plan["acceptance_outcomes"][0]["layer"] = "platform_secure_store"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("acceptance_outcome_layer_overclaim", codes)

    def test_ao_test_double_claim_fails(self) -> None:
        plan = ok_suite_plan()
        plan["acceptance_outcomes"][0]["evidence_kind"] = "test_double"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("acceptance_outcome_test_double_claim", codes)

    def test_ao_deferred_blocks_plain_green(self) -> None:
        summary = ok_closing_summary()
        summary.update(ok_acceptance_outcomes(with_deferred=True))
        summary["outcome"] = "green"
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("acceptance_outcome_overclaim_green", codes)

    def test_ao_deferred_green_with_residuals_ok(self) -> None:
        summary = ok_closing_summary()
        summary.update(ok_acceptance_outcomes(with_deferred=True))
        summary["outcome"] = "green_with_residuals"
        summary["residuals"] = [
            {
                "code": "acceptance_outcome_deferred_e2e",
                "detail": "ui_human_path deferred to e2e",
            }
        ]
        summary["plain"]["leftovers"] = "界面点击路径还要在 E2E 战役里再查。"
        summary["plain"]["result"] = "服务层检查通过了，还有界面路径留给下一步。"
        result = MOD.lint_closing_summary(summary)
        self.assertTrue(result["ok"], result)

    def test_ao_full_user_path_claim_fails_on_it(self) -> None:
        plan = ok_suite_plan()
        plan["user_path_claim"] = "full_user_path"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("acceptance_outcome_user_path_overclaim", codes)


class CliTests(unittest.TestCase):
    def test_cli_suite_plan_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.json"
            path.write_text(json.dumps(ok_suite_plan()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--kind", "suite_plan", "--json", str(path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
