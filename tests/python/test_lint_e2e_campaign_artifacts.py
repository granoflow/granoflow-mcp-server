#!/usr/bin/env python3
"""Tests for lint_e2e_campaign_artifacts.py (E2E-L1–L5 structural gates)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-e2e-test-campaign" / "scripts" / "lint_e2e_campaign_artifacts.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_e2e_campaign_artifacts", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def ok_coverage_matrix() -> dict:
    return {
        "schema": "granoflow_e2e_coverage_matrix_v1",
        "sources_loaded": [
            "project_work.product.primary_user_journeys",
            "project_work.product_spec_coverage.journey_coverage",
            "project_work.acceptance.conditions",
        ],
        "required_journeys": [
            {
                "journey_id": "J-home",
                "title": "打开首页",
                "acceptance_ids": ["A1"],
                "case_ids": ["launch_home"],
                "checkpoint_ids": ["home_loaded"],
                "status": "covered",
                "interaction_surface": "in_app_ui",
                "residual_code": None,
            },
            {
                "journey_id": "J-checkout",
                "title": "结账",
                "acceptance_ids": ["A2"],
                "case_ids": ["checkout"],
                "checkpoint_ids": ["checkout_done"],
                "status": "covered",
                "interaction_surface": "in_app_ui",
                "residual_code": None,
            },
        ],
        "authoring": {
            "tests_written_or_updated": True,
            "paths": [
                "e2e/launch_home_test.dart",
                "e2e/checkout_test.dart",
            ],
        },
    }


def ok_acceptance_outcomes(*, secure_store: bool = False) -> dict:
    rows = [
        {
            "id": "AO-home-ui",
            "statement": "用户打开应用后看到首页",
            "layer": "ui_human_path",
            "evidence_kind": "real_side_effect",
            "status": "closed",
            "case_ids": ["launch_home"],
        },
        {
            "id": "AO-checkout-ui",
            "statement": "用户完成结账主路径",
            "layer": "ui_human_path",
            "evidence_kind": "real_side_effect",
            "status": "closed",
            "case_ids": ["checkout"],
        },
    ]
    payload: dict = {
        "acceptance_outcomes_loaded": True,
        "user_path_claim": "full_user_path",
        "acceptance_outcomes": rows,
    }
    if secure_store:
        rows.append(
            {
                "id": "AO-session-key",
                "statement": "会话密钥已写入系统安全存储",
                "layer": "platform_secure_store",
                "evidence_kind": "host_probe",
                "status": "closed",
                "case_ids": ["launch_home"],
            }
        )
        payload["secure_storage_capability"] = "available"
    return payload


def ok_suite_plan() -> dict:
    plan = {
        "schema": "granoflow_e2e_suite_plan_v1",
        "contract_loaded": True,
        "orchestration_loaded": True,
        "coverage_loaded": True,
        "coverage_matrix": ok_coverage_matrix(),
        "test_layer": "e2e",
        "interaction_fidelity": "human_path",
        "display_mode": "visible_window",
        "run_command": (
            "flutter drive --driver=test_driver/integration_test.dart "
            "--target=integration_test/app_test.dart -d macos"
        ),
        "cases": [
            {
                "id": "launch_home",
                "path": "e2e/launch_home_test.dart",
                "entry_style": "human_path",
            },
            {
                "id": "checkout",
                "path": "e2e/checkout_test.dart",
                "entry_style": "route_shortcut",
                "route_shortcut_justified": (
                    "deep link to checkout after session seeded in prior case"
                ),
            },
        ],
        "order": ["launch_home", "checkout"],
        "checkpoints": [
            {"step_id": "home_loaded", "capture": "screenshot"},
            {"step_id": "checkout_done", "capture": "screenshot"},
        ],
    }
    plan.update(ok_acceptance_outcomes())
    return plan


def ok_campaign_state() -> dict:
    return {
        "schema": "granoflow_e2e_campaign_state_v1",
        "campaign_id": "e1",
        "project_id": "p1",
        "campaign_drive": "agent_auto",
        "integration_gate": "complete",
        "interaction_fidelity": "human_path",
        "screenshot_capability": "available",
        "window_capability": "available",
        "vision_capability": "available",
        "screenshot_policy": "required_if_capable",
        "vision_policy": "on_if_capable",
        "vision_result": "passed",
        "phase": "complete",
        "failures": [],
        "residuals": [],
    }


def ok_prototype_task_reviews(
    *,
    required_task_ids: list[str] | None = None,
    reviews: list[dict] | None = None,
    ai_loop_status: str | None = None,
    user_final_acceptance: bool = False,
) -> dict:
    required = [] if required_task_ids is None else required_task_ids
    if ai_loop_status is None:
        ai_loop_status = "not_applicable" if not required else "complete"
    return {
        "schema": "granoflow_e2e_prototype_task_reviews_v1",
        "inventory_loaded": True,
        "required_task_ids": required,
        "ai_loop_status": ai_loop_status,
        "user_final_acceptance": user_final_acceptance,
        "reviews": [] if reviews is None else reviews,
    }


def ok_prototype_review_row(
    task_id: str = "11111111-1111-1111-1111-111111111111",
    *,
    decision: str = "matched",
    revised_and_recaptured: bool | str = "not_applicable",
    ai_pass: bool | None = None,
    remediation: dict | None = None,
) -> dict:
    if ai_pass is None:
        ai_pass = decision == "matched"
    row = {
        "task_id": task_id,
        "page_id": "S-settings",
        "screenshot_path": f"temp/e2e-campaign/1/screenshots/proto-task-{task_id}.png",
        "prototype_link": "file://tmp/proto-settings.html",
        "shown_to_user": True,
        "questions": {
            "ux_better": False,
            "visual_better": False,
            "tech_stack_blocked": False,
        },
        "ai_pass": ai_pass,
        "decision": decision,
        "decision_rationale": (
            "仅形态适配，对照通过。"
            if decision == "matched"
            else "保留差异：当前实现更符合目标平台导航习惯。"
            if decision == "keep_implementation"
            else "按原型修正中。"
        ),
        "vision_compare": "passed",
        "revised_and_recaptured": revised_and_recaptured,
    }
    if remediation is not None:
        row["remediation"] = remediation
    elif ai_pass is False:
        row["remediation"] = {
            "milestone_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "task_ids": ["bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"],
            "feature_gap": False,
        }
    return row


def ok_evidence_pack() -> dict:
    return {
        "schema": "granoflow_e2e_evidence_pack_v1",
        "screenshot_capability": "available",
        "window_capability": "available",
        "vision_capability": "available",
        "checkpoints": ["home_loaded", "checkout_done"],
        "screenshots": [
            {
                "step_id": "home_loaded",
                "path": "temp/e2e-campaign/1/screenshots/home_loaded.png",
                "shown_to_user": True,
                "capture_surface": "os_window",
            },
            {
                "step_id": "checkout_done",
                "path": "temp/e2e-campaign/1/screenshots/checkout_done.png",
                "shown_to_user": True,
                "capture_surface": "os_window",
            },
        ],
        "prototype_task_reviews": ok_prototype_task_reviews(),
        "silent_temp_ignore_ensured": True,
    }


def ok_closing_summary() -> dict:
    summary = {
        "schema": "granoflow_e2e_campaign_closing_summary_v1",
        "contract_loaded": True,
        "plain_language_loaded": True,
        "audience": "beginner",
        "locale": "zh-Hans",
        "outcome": "green",
        "rounds_completed": 1,
        "code_changed": False,
        "screenshot_capability": "available",
        "window_capability": "available",
        "vision_result": "passed",
        "residuals": [],
        "plain": {
            "headline": "界面端到端检查已经全部通过。",
            "what_we_checked": "像真人一样打开应用并完成主流程点击。",
            "result": "这些界面步骤都通过了。",
            "what_changed_for_you": "应用对你来说没有变化。",
            "leftovers": "没有未完成事项。",
            "next_step": "可以说「项目收尾」。",
            "screenshots_note": "关键步骤截图保存在项目临时文件夹，并已在对话中展示。",
        },
        "evidence_pack": ok_evidence_pack(),
        "markdown_body": """
## 一句话结论
界面端到端检查已经全部通过。

## 这次查了什么
像真人一样打开应用并完成主流程点击。

## 结果如何
这些界面步骤都通过了。

## 对你有什么影响
应用对你来说没有变化。

## 关键步骤截图
已在对话中展示主界面和结账步骤截图。

## 还剩什么没做完
没有未完成事项。

## 下一步你可以做什么
可以说「项目收尾」。
""",
    }
    summary.update(ok_acceptance_outcomes())
    # Empty inventory: allow 项目收尾 only with user_final_acceptance.
    summary["evidence_pack"]["prototype_task_reviews"] = ok_prototype_task_reviews(
        user_final_acceptance=True,
    )
    return summary


class LintSuitePlanTests(unittest.TestCase):
    def test_ok_happy_path(self) -> None:
        result = MOD.lint_suite_plan(ok_suite_plan())
        self.assertTrue(result["ok"], result)

    def test_route_shortcut_without_justification_fails(self) -> None:
        plan = ok_suite_plan()
        plan["cases"][1].pop("route_shortcut_justified")
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_route_shortcut_unjustified", codes)

    def test_coverage_unloaded_fails(self) -> None:
        plan = ok_suite_plan()
        plan["coverage_loaded"] = False
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_coverage_unloaded", codes)

    def test_covered_journey_without_checkpoint_fails(self) -> None:
        plan = ok_suite_plan()
        plan["coverage_matrix"]["required_journeys"][0]["checkpoint_ids"] = []
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_coverage_incomplete", codes)

    def test_project_work_journey_missing_fails(self) -> None:
        plan = ok_suite_plan()
        project_work = {
            "product": {"primary_user_journeys": []},
            "product_spec_coverage": {
                "journey_coverage": [
                    {
                        "journey_id": "J-missing",
                        "disposition": "adopted",
                        "title": "未覆盖旅程",
                    }
                ]
            },
        }
        result = MOD.lint_suite_plan(plan, project_work=project_work)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_coverage_incomplete", codes)

    def test_deferred_journey_with_residual_ok(self) -> None:
        plan = ok_suite_plan()
        plan["coverage_matrix"]["required_journeys"].append(
            {
                "journey_id": "J-store",
                "title": "应用商店支付",
                "acceptance_ids": [],
                "case_ids": [],
                "checkpoint_ids": [],
                "status": "deferred_external",
                "residual_code": "e2e_campaign_external_deferred",
            }
        )
        project_work = {
            "product_spec_coverage": {
                "journey_coverage": [
                    {"journey_id": "J-home", "disposition": "adopted"},
                    {"journey_id": "J-checkout", "disposition": "adopted"},
                    {"journey_id": "J-store", "disposition": "adopted"},
                ]
            }
        }
        result = MOD.lint_suite_plan(plan, project_work=project_work)
        self.assertTrue(result["ok"], result)


class LintCampaignStateTests(unittest.TestCase):
    def test_ok_happy_path(self) -> None:
        result = MOD.lint_campaign_state(ok_campaign_state())
        self.assertTrue(result["ok"], result)

    def test_e2e_l1_integration_gate_incomplete_fails(self) -> None:
        state = ok_campaign_state()
        state["integration_gate"] = "incomplete"
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_integration_gate_incomplete", codes)

    def test_vision_skipped_needs_residual(self) -> None:
        state = ok_campaign_state()
        state["vision_result"] = "skipped"
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_vision_skipped_unrecorded", codes)


class LintEvidencePackTests(unittest.TestCase):
    def test_ok_happy_path(self) -> None:
        result = MOD.lint_evidence_pack(ok_evidence_pack())
        self.assertTrue(result["ok"], result)

    def test_e2e_l2_checkpoint_without_path_fails(self) -> None:
        pack = ok_evidence_pack()
        pack["screenshots"] = pack["screenshots"][:1]
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_screenshot_checkpoint_missing", codes)

    def test_e2e_l3_capability_unavailable_with_residual_passes(self) -> None:
        # Mid-flight evidence may record unavailable for debugging; closing still
        # fail-closed via campaign state / closing summary gates.
        pack = {
            "schema": "granoflow_e2e_evidence_pack_v1",
            "screenshot_capability": "unavailable",
            "window_capability": "unavailable",
            "checkpoints": ["home_loaded"],
            "screenshots": [],
            "prototype_task_reviews": ok_prototype_task_reviews(),
            "residuals": [{"code": "e2e_campaign_screenshot_unavailable", "detail": "headless CI"}],
        }
        result = MOD.lint_evidence_pack(pack)
        self.assertTrue(result["ok"], result)

    def test_e2e_l5_screenshot_path_not_under_temp_fails(self) -> None:
        pack = ok_evidence_pack()
        pack["screenshots"][0]["path"] = "screenshots/home_loaded.png"
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_screenshot_path_not_temp", codes)

    def test_shown_to_user_false_fails(self) -> None:
        pack = ok_evidence_pack()
        pack["screenshots"][0]["shown_to_user"] = False
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_evidence_not_shown", codes)

    def test_prototype_diff_review_ok(self) -> None:
        pack = ok_evidence_pack()
        pack["prototype_diff_review"] = [
            {
                "page_id": "S-settings",
                "screenshot_path": "temp/e2e-campaign/1/screenshots/proto-diff-S-settings.png",
                "prototype_link": "file://tmp/proto-settings.html",
                "shown_to_user": True,
                "vision_compare": "skipped",
                "vision_decision": "skipped",
            }
        ]
        result = MOD.lint_evidence_pack(pack)
        self.assertTrue(result["ok"], result)

    def test_prototype_diff_missing_link_fails(self) -> None:
        pack = ok_evidence_pack()
        pack["prototype_diff_review"] = [
            {
                "page_id": "S-settings",
                "screenshot_path": "temp/e2e-campaign/1/screenshots/proto-diff-S-settings.png",
                "prototype_link": "",
                "shown_to_user": True,
            }
        ]
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_diff_link_missing", codes)

    def test_prototype_diff_not_shown_fails(self) -> None:
        pack = ok_evidence_pack()
        pack["prototype_diff_review"] = [
            {
                "page_id": "S-settings",
                "screenshot_path": "temp/e2e-campaign/1/screenshots/proto-diff-S-settings.png",
                "prototype_link": "file://tmp/proto-settings.html",
                "shown_to_user": False,
            }
        ]
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_diff_not_shown", codes)

    def test_prototype_task_inventory_missing_fails(self) -> None:
        pack = ok_evidence_pack()
        del pack["prototype_task_reviews"]
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_task_inventory_unloaded", codes)

    def test_prototype_task_review_covers_required_ids(self) -> None:
        tid = "22222222-2222-2222-2222-222222222222"
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[ok_prototype_review_row(tid)],
            ai_loop_status="complete",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertTrue(result["ok"], result)

    def test_prototype_task_review_missing_required_id_fails(self) -> None:
        tid = "22222222-2222-2222-2222-222222222222"
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[],
            ai_loop_status="in_progress",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_task_review_missing", codes)

    def test_prototype_three_questions_incomplete_fails(self) -> None:
        tid = "33333333-3333-3333-3333-333333333333"
        row = ok_prototype_review_row(tid)
        del row["questions"]["tech_stack_blocked"]
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="complete",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_three_questions_incomplete", codes)

    def test_prototype_ai_keep_forbidden_in_ai_loop(self) -> None:
        tid = "44444444-4444-4444-4444-444444444444"
        row = ok_prototype_review_row(tid, decision="keep_implementation")
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="in_progress",
            user_final_acceptance=False,
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_ai_keep_forbidden", codes)

    def test_prototype_keep_rationale_missing_at_user_final_fails(self) -> None:
        tid = "44444444-4444-4444-4444-444444444445"
        row = ok_prototype_review_row(tid, decision="keep_implementation")
        row["decision_rationale"] = ""
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="complete",
            user_final_acceptance=True,
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_keep_rationale_missing", codes)
        # keep with empty rationale also breaks ai_pass consistency / complete rules;
        # primary assertion is rationale code.

    def test_prototype_revise_not_recaptured_without_remediation_fails(self) -> None:
        tid = "55555555-5555-5555-5555-555555555555"
        row = ok_prototype_review_row(
            tid,
            decision="revise_to_prototype",
            revised_and_recaptured=False,
        )
        row.pop("remediation", None)
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="in_progress",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertTrue(
            {
                "e2e_prototype_revise_not_recaptured",
                "e2e_prototype_remediation_missing",
            }
            & codes
        )

    def test_prototype_revise_in_progress_with_remediation_ok(self) -> None:
        tid = "66666666-6666-6666-6666-666666666666"
        row = ok_prototype_review_row(
            tid,
            decision="revise_to_prototype",
            revised_and_recaptured=False,
            remediation={
                "milestone_id": "m1",
                "task_ids": ["t-fix-1"],
                "feature_gap": True,
            },
        )
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="in_progress",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertTrue(result["ok"], result)

    def test_prototype_matched_form_factor_ok(self) -> None:
        tid = "77777777-7777-7777-7777-777777777777"
        row = ok_prototype_review_row(tid, decision="matched")
        row["decision_rationale"] = "仅横竖屏与桌面/移动形态差异，不计入保真度差异。"
        row["form_factor_carveout_applied"] = True
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="complete",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertTrue(result["ok"], result)

    def test_prototype_ai_pass_missing_fails(self) -> None:
        tid = "88888888-8888-8888-8888-888888888888"
        row = ok_prototype_review_row(tid)
        del row["ai_pass"]
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="complete",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_ai_pass_missing", codes)

    def test_prototype_ai_pass_inconsistent_fails(self) -> None:
        tid = "99999999-9999-9999-9999-999999999999"
        row = ok_prototype_review_row(tid, decision="matched", ai_pass=False)
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="in_progress",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_ai_pass_inconsistent", codes)

    def test_prototype_complete_with_fail_row_fails(self) -> None:
        tid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1"
        row = ok_prototype_review_row(
            tid,
            decision="revise_to_prototype",
            revised_and_recaptured=False,
        )
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="complete",
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_ai_loop_incomplete", codes)

    def test_prototype_user_final_before_ai_fails(self) -> None:
        tid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2"
        row = ok_prototype_review_row(
            tid,
            decision="revise_to_prototype",
            revised_and_recaptured=False,
        )
        pack = ok_evidence_pack()
        pack["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[row],
            ai_loop_status="in_progress",
            user_final_acceptance=True,
        )
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_user_final_before_ai", codes)


class LintClosingSummaryTests(unittest.TestCase):
    def test_ok_happy_path(self) -> None:
        result = MOD.lint_closing_summary(ok_closing_summary())
        self.assertTrue(result["ok"], result)

    def test_project_close_before_user_final_fails(self) -> None:
        summary = ok_closing_summary()
        summary["evidence_pack"]["prototype_task_reviews"] = ok_prototype_task_reviews(
            user_final_acceptance=False,
        )
        summary["plain"]["next_step"] = "可以说「项目收尾」。"
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_closing_summary_ai_loop", codes)

    def test_prototype_compare_heading_required_when_inventory_nonempty(self) -> None:
        tid = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        summary = ok_closing_summary()
        summary["evidence_pack"]["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[ok_prototype_review_row(tid)],
            ai_loop_status="complete",
            user_final_acceptance=True,
        )
        # ok_closing_summary body has no 原型对照
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_closing_summary_screenshots_missing", codes)

    def test_green_with_ai_loop_incomplete_fails(self) -> None:
        tid = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        summary = ok_closing_summary()
        summary["plain"]["next_step"] = "请先做原型对照最终验收。"
        summary["evidence_pack"]["prototype_task_reviews"] = ok_prototype_task_reviews(
            required_task_ids=[tid],
            reviews=[
                ok_prototype_review_row(
                    tid,
                    decision="revise_to_prototype",
                    revised_and_recaptured=False,
                )
            ],
            ai_loop_status="in_progress",
            user_final_acceptance=False,
        )
        summary["markdown_body"] = summary["markdown_body"].replace(
            "## 关键步骤截图\n已在对话中展示主界面和结账步骤截图。\n",
            (
                "## 关键步骤截图\n已在对话中展示主界面和结账步骤截图。\n\n"
                "## 原型对照\n对照循环进行中。\n"
            ),
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_prototype_ai_loop_incomplete", codes)

    def test_e2e_l4_missing_screenshots_heading_fails(self) -> None:
        summary = ok_closing_summary()
        summary["markdown_body"] = summary["markdown_body"].replace(
            "## 关键步骤截图\n已在对话中展示主界面和结账步骤截图。\n", ""
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_closing_summary_screenshots_missing", codes)

    def test_e2e_l3_capability_unavailable_closing_fails_window_required(self) -> None:
        """Updated for visible-window hard gate (T8): unavailable cannot close green*."""
        summary = ok_closing_summary()
        summary["screenshot_capability"] = "unavailable"
        summary["plain"]["screenshots_note"] = "当前环境无法截图。"
        summary["markdown_body"] = summary["markdown_body"].replace(
            "## 关键步骤截图\n已在对话中展示主界面和结账步骤截图。\n", ""
        )
        summary["evidence_pack"] = {
            "schema": "granoflow_e2e_evidence_pack_v1",
            "screenshot_capability": "unavailable",
            "checkpoints": ["home_loaded"],
            "screenshots": [],
            "residuals": [{"code": "screenshot_unavailable", "detail": "no display capture"}],
        }
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)


def ok_host_matrix(*hosts: dict) -> dict:
    return {
        "schema": "granoflow_verification_host_matrix_v1",
        "derived_from": ["scope.supported_platforms"],
        "concurrency": "parallel_when_capable",
        "primary_form_factors": [],
        "hosts": list(hosts),
        "assignment_policy": "journey_at_least_one_capable_host",
    }


class HostMatrixAndShipBarTests(unittest.TestCase):
    """L1–L4, L6–L10 structural gates (L5 skipped as too fuzzy)."""

    def test_l1_web_only_requires_browser_not_mobile(self) -> None:
        kinds = MOD.derive_required_host_kinds(["web"])
        self.assertEqual(kinds, {"browser"})
        self.assertNotIn("simulator", kinds)
        self.assertNotIn("emulator", kinds)

    def test_l2_multi_platform_requires_desktop_sim_emu(self) -> None:
        kinds = MOD.derive_required_host_kinds(["ios", "android", "macos"])
        self.assertEqual(kinds, {"simulator", "emulator", "desktop"})

    def test_l9_omitted_ship_bar_defaults_market_smoke(self) -> None:
        self.assertEqual(MOD.normalize_ship_bar(None), "market_smoke")
        self.assertEqual(MOD.normalize_ship_bar(""), "market_smoke")
        self.assertEqual(MOD.normalize_ship_bar("full_campaign"), "full_campaign")

    def test_l10_empty_platforms_do_not_invent_desktop(self) -> None:
        self.assertEqual(MOD.derive_required_host_kinds([]), set())
        result = MOD.lint_host_matrix(
            ok_host_matrix(),
            platforms=[],
            require_present=False,
        )
        self.assertTrue(result["ok"], result)

    def test_l3_covered_without_host_ids_fails_when_matrix_present(self) -> None:
        plan = ok_suite_plan()
        plan["host_matrix"] = ok_host_matrix(
            {
                "id": "desktop_native",
                "kind": "desktop",
                "platforms": ["macos"],
                "status": "available",
            }
        )
        plan["concurrency"] = "parallel_when_capable"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("verification_host_unassigned_journey", codes)

    def test_l4_required_host_kind_mismatch_fails(self) -> None:
        plan = ok_suite_plan()
        plan["host_matrix"] = ok_host_matrix(
            {
                "id": "ios_simulator",
                "kind": "simulator",
                "platforms": ["ios"],
                "status": "available",
            },
            {
                "id": "desktop_native",
                "kind": "desktop",
                "platforms": ["macos"],
                "status": "available",
            },
        )
        for row in plan["coverage_matrix"]["required_journeys"]:
            row["host_ids"] = ["ios_simulator"]
            row["required_host_kinds"] = ["desktop"]
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("verification_host_platform_mismatch", codes)

    def test_l8_parallel_concurrency_accepted(self) -> None:
        plan = ok_suite_plan()
        plan["ship_bar"] = "market_smoke"
        plan["concurrency"] = "parallel_when_capable"
        plan["host_matrix"] = ok_host_matrix(
            {
                "id": "desktop_native",
                "kind": "desktop",
                "platforms": ["macos"],
                "status": "available",
            },
            {
                "id": "ios_simulator",
                "kind": "simulator",
                "platforms": ["ios"],
                "status": "available",
            },
        )
        for row in plan["coverage_matrix"]["required_journeys"]:
            row["host_ids"] = ["desktop_native"]
        result = MOD.lint_suite_plan(plan)
        self.assertTrue(result["ok"], result)

    def test_l6_unavailable_host_without_residual_fails(self) -> None:
        matrix = ok_host_matrix(
            {
                "id": "ios_simulator",
                "kind": "simulator",
                "platforms": ["ios"],
                "status": "unavailable",
            }
        )
        errors = MOD.lint_host_availability_residuals(matrix, residuals=[], outcome=None)
        codes = {e["code"] for e in errors}
        self.assertIn("e2e_campaign_host_unavailable", codes)

    def test_l7_unavailable_host_with_residual_allows_green_with_residuals(self) -> None:
        summary = ok_closing_summary()
        summary["outcome"] = "green_with_residuals"
        summary["host_matrix"] = ok_host_matrix(
            {
                "id": "ios_simulator",
                "kind": "simulator",
                "platforms": ["ios"],
                "status": "unavailable",
            }
        )
        summary["residuals"] = [
            {
                "code": "e2e_campaign_host_unavailable",
                "detail": "iOS simulator not installed",
            }
        ]
        summary["plain"]["leftovers"] = "本机没有 iOS 模拟器，相关检查先记下，其余主流程已通过。"
        # Keep markdown leftovers section consistent enough for residual unexplained gate
        summary["markdown_body"] = summary["markdown_body"].replace(
            "没有未完成事项。",
            "本机没有 iOS 模拟器，相关检查先记下。",
        )
        result = MOD.lint_closing_summary(summary)
        self.assertTrue(result["ok"], result)

    def test_l6_unavailable_host_green_outcome_fails(self) -> None:
        summary = ok_closing_summary()
        summary["outcome"] = "green"
        summary["host_matrix"] = ok_host_matrix(
            {
                "id": "ios_simulator",
                "kind": "simulator",
                "platforms": ["ios"],
                "status": "unavailable",
            }
        )
        summary["residuals"] = [{"code": "e2e_campaign_host_unavailable", "detail": "missing sim"}]
        summary["plain"]["leftovers"] = "缺少 iOS 模拟器。"
        summary["markdown_body"] = summary["markdown_body"].replace(
            "没有未完成事项。",
            "缺少 iOS 模拟器。",
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_host_unavailable", codes)

    def test_platforms_imply_matrix_missing_on_suite(self) -> None:
        plan = ok_suite_plan()
        project_work = {
            "scope": {"supported_platforms": ["ios", "android"]},
            "product": {"primary_user_journeys": ["J-home", "J-checkout"]},
        }
        result = MOD.lint_suite_plan(plan, project_work=project_work)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("verification_host_matrix_missing", codes)


class ManualTestDeferralTests(unittest.TestCase):
    """Difficulty-based skip / mid-run drop + closing hand-test reminder."""

    def test_deferred_manual_requires_feature_and_manual_residual(self) -> None:
        matrix = ok_coverage_matrix()
        matrix["required_journeys"][1] = {
            "journey_id": "J-checkout",
            "title": "结账",
            "acceptance_ids": ["A2"],
            "case_ids": [],
            "checkpoint_ids": [],
            "status": "deferred_manual",
            "residual_code": "e2e_campaign_manual_test_required",
            "feature": "结账页优惠码",
        }
        result = MOD.lint_coverage_matrix(matrix)
        self.assertTrue(result["ok"], result)

    def test_deferred_manual_without_feature_fails(self) -> None:
        matrix = ok_coverage_matrix()
        matrix["required_journeys"][1] = {
            "journey_id": "J-checkout",
            "title": "结账",
            "status": "deferred_manual",
            "residual_code": "e2e_campaign_automation_too_hard",
        }
        result = MOD.lint_coverage_matrix(matrix)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_manual_test_reminder_missing", codes)

    def test_closing_manual_residual_requires_named_hand_test_leftovers(self) -> None:
        summary = ok_closing_summary()
        summary["outcome"] = "green_with_residuals"
        summary["residuals"] = [
            {
                "code": "e2e_campaign_manual_test_required",
                "feature": "桌面托盘最近 5 本",
                "detail": "OS tray hooks unstable in harness",
            }
        ]
        summary["plain"]["leftovers"] = (
            "请你手工测试「桌面托盘最近 5 本」：最小化主窗后从托盘点最近书籍能否继续阅读。"
        )
        summary["markdown_body"] = summary["markdown_body"].replace(
            "没有未完成事项。",
            "请你手工测试「桌面托盘最近 5 本」。",
        )
        result = MOD.lint_closing_summary(summary)
        self.assertTrue(result["ok"], result)

    def test_closing_manual_residual_green_outcome_fails(self) -> None:
        summary = ok_closing_summary()
        summary["outcome"] = "green"
        summary["residuals"] = [
            {
                "code": "e2e_campaign_automation_too_hard",
                "feature": "系统听书锁屏播控",
                "detail": "no reliable Now Playing driver",
            }
        ]
        summary["plain"]["leftovers"] = "请手工测试系统听书锁屏播控。"
        summary["markdown_body"] = summary["markdown_body"].replace(
            "没有未完成事项。",
            "请手工测试系统听书锁屏播控。",
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_manual_test_reminder_missing", codes)

    def test_closing_manual_residual_missing_feature_name_in_leftovers_fails(self) -> None:
        summary = ok_closing_summary()
        summary["outcome"] = "green_with_residuals"
        summary["residuals"] = [
            {
                "code": "manual_test_required",
                "feature": "桌面托盘最近 5 本",
                "detail": "skipped",
            }
        ]
        summary["plain"]["leftovers"] = "还有一些项目需要手工测试。"
        summary["markdown_body"] = summary["markdown_body"].replace(
            "没有未完成事项。",
            "还有一些项目需要手工测试。",
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_manual_test_reminder_missing", codes)


class VisibleWindowGateTests(unittest.TestCase):
    """T1–T9: visible_window hard gate; unavailable fails closed for the campaign."""

    def test_t1_visible_window_with_flutter_drive_ok(self) -> None:
        plan = ok_suite_plan()
        plan["display_mode"] = "visible_window"
        plan["run_command"] = (
            "flutter drive --driver=test_driver/integration_test.dart "
            "--target=integration_test/app_test.dart -d macos"
        )
        result = MOD.lint_suite_plan(plan)
        self.assertTrue(result["ok"], result)

    def test_t2_omitted_display_mode_defaults_visible_window_ok(self) -> None:
        plan = ok_suite_plan()
        plan.pop("display_mode", None)
        self.assertEqual(MOD.normalize_display_mode(None), "visible_window")
        result = MOD.lint_suite_plan(plan)
        self.assertTrue(result["ok"], result)

    def test_t3_display_mode_headless_fails(self) -> None:
        plan = ok_suite_plan()
        plan["display_mode"] = "headless"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_headless_ui_forbidden", codes)

    def test_t4_flutter_test_run_command_with_covered_fails(self) -> None:
        plan = ok_suite_plan()
        plan["run_command"] = "flutter test test/e2e/market_smoke_ui_journey_test.dart"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_headless_ui_forbidden", codes)

    def test_t5_offscreen_capture_surface_fails(self) -> None:
        pack = ok_evidence_pack()
        pack["screenshots"][0]["capture_surface"] = "offscreen_test_binding"
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_screenshot_not_from_live_window", codes)

    def test_t6_os_window_capture_surface_ok(self) -> None:
        pack = ok_evidence_pack()
        for shot in pack["screenshots"]:
            shot["capture_surface"] = "os_window"
        result = MOD.lint_evidence_pack(pack)
        self.assertTrue(result["ok"], result)

    def test_t7_complete_state_screenshot_unavailable_fails(self) -> None:
        state = ok_campaign_state()
        state["phase"] = "complete"
        state["screenshot_capability"] = "unavailable"
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)

    def test_t8_closing_green_screenshot_unavailable_fails(self) -> None:
        summary = ok_closing_summary()
        summary["screenshot_capability"] = "unavailable"
        summary["outcome"] = "green"
        summary["plain"]["screenshots_note"] = "无法截图。"
        summary["markdown_body"] = summary["markdown_body"].replace(
            "## 关键步骤截图\n已在对话中展示主界面和结账步骤截图。\n", ""
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)

    def test_t9_residual_cannot_waive_missing_window(self) -> None:
        summary = ok_closing_summary()
        summary["screenshot_capability"] = "unavailable"
        summary["outcome"] = "green_with_residuals"
        summary["residuals"] = [
            {
                "code": "e2e_campaign_screenshot_unavailable",
                "detail": "no display",
            },
            {
                "code": "e2e_campaign_host_unavailable",
                "feature": "桌面窗口",
                "detail": "cannot show window",
            },
        ]
        summary["plain"]["leftovers"] = "本机无法弹出窗口。"
        summary["plain"]["screenshots_note"] = "无法截图。"
        summary["markdown_body"] = (
            summary["markdown_body"]
            .replace(
                "## 关键步骤截图\n已在对话中展示主界面和结账步骤截图。\n",
                "",
            )
            .replace("没有未完成事项。", "本机无法弹出窗口。")
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)


class AcceptanceOutcomeGateTests(unittest.TestCase):
    """AO gates: user-required real results cannot be closed via test doubles."""

    def test_ao_unloaded_fails(self) -> None:
        plan = ok_suite_plan()
        del plan["acceptance_outcomes_loaded"]
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("acceptance_outcomes_unloaded", codes)

    def test_ao_test_double_claim_fails(self) -> None:
        plan = ok_suite_plan()
        plan["acceptance_outcomes"][0]["evidence_kind"] = "test_double"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("acceptance_outcome_test_double_claim", codes)

    def test_ao_secure_store_unprobed_fails(self) -> None:
        plan = ok_suite_plan()
        plan.update(ok_acceptance_outcomes(secure_store=True))
        del plan["secure_storage_capability"]
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_secure_storage_unprobed", codes)

    def test_ao_secure_store_probed_ok(self) -> None:
        plan = ok_suite_plan()
        plan.update(ok_acceptance_outcomes(secure_store=True))
        result = MOD.lint_suite_plan(plan)
        self.assertTrue(result["ok"], result)

    def test_ao_secure_store_unavailable_fails(self) -> None:
        plan = ok_suite_plan()
        plan.update(ok_acceptance_outcomes(secure_store=True))
        plan["secure_storage_capability"] = "unavailable"
        result = MOD.lint_suite_plan(plan)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_secure_storage_unavailable", codes)


class WindowCapabilityGateTests(unittest.TestCase):
    """W1–W5: independent window_capability probe fail-closed."""

    def test_w1_complete_state_window_unavailable_fails(self) -> None:
        state = ok_campaign_state()
        state["phase"] = "complete"
        state["window_capability"] = "unavailable"
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)

    def test_w2_closing_green_with_residuals_window_unavailable_fails(self) -> None:
        summary = ok_closing_summary()
        summary["window_capability"] = "unavailable"
        summary["outcome"] = "green_with_residuals"
        summary["residuals"] = [
            {
                "code": "e2e_campaign_host_unavailable",
                "feature": "桌面窗口",
                "detail": "no window",
            }
        ]
        summary["plain"]["leftovers"] = "本机无法弹出窗口。"
        summary["markdown_body"] = summary["markdown_body"].replace(
            "没有未完成事项。",
            "本机无法弹出窗口。",
        )
        result = MOD.lint_closing_summary(summary)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)

    def test_w3_os_window_with_window_unavailable_fails(self) -> None:
        pack = ok_evidence_pack()
        pack["window_capability"] = "unavailable"
        for shot in pack["screenshots"]:
            shot["capture_surface"] = "os_window"
        result = MOD.lint_evidence_pack(pack)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)

    def test_w4_window_and_screenshot_available_ok(self) -> None:
        state = ok_campaign_state()
        pack = ok_evidence_pack()
        summary = ok_closing_summary()
        self.assertTrue(MOD.lint_campaign_state(state)["ok"], state)
        self.assertTrue(MOD.lint_evidence_pack(pack)["ok"], pack)
        self.assertTrue(MOD.lint_closing_summary(summary)["ok"], summary)

    def test_w5_complete_state_missing_window_capability_fails(self) -> None:
        state = ok_campaign_state()
        state["phase"] = "complete"
        state.pop("window_capability", None)
        result = MOD.lint_campaign_state(state)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_window_required", codes)


class OsChromeVerificationTests(unittest.TestCase):
    """C1–C5: interaction_surface + os_chrome_verification on covered journeys."""

    def test_c1_covered_missing_interaction_surface_fails(self) -> None:
        matrix = ok_coverage_matrix()
        matrix["required_journeys"][0].pop("interaction_surface", None)
        result = MOD.lint_coverage_matrix(matrix)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_interaction_surface_missing", codes)

    def test_c2_os_chrome_covered_without_verification_fails(self) -> None:
        matrix = ok_coverage_matrix()
        matrix["required_journeys"][0]["interaction_surface"] = "os_chrome"
        matrix["required_journeys"][0].pop("os_chrome_verification", None)
        result = MOD.lint_coverage_matrix(matrix)
        self.assertFalse(result["ok"])
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("e2e_campaign_os_chrome_unverified", codes)

    def test_c3_os_chrome_with_real_interaction_ok(self) -> None:
        matrix = ok_coverage_matrix()
        matrix["required_journeys"][0]["interaction_surface"] = "os_chrome"
        matrix["required_journeys"][0]["os_chrome_verification"] = "real_interaction"
        result = MOD.lint_coverage_matrix(matrix)
        self.assertTrue(result["ok"], result)

    def test_c4_in_app_ui_without_os_chrome_field_ok(self) -> None:
        matrix = ok_coverage_matrix()
        matrix["required_journeys"][0]["interaction_surface"] = "in_app_ui"
        matrix["required_journeys"][0].pop("os_chrome_verification", None)
        result = MOD.lint_coverage_matrix(matrix)
        self.assertTrue(result["ok"], result)

    def test_c5_deferred_manual_without_interaction_surface_ok(self) -> None:
        matrix = ok_coverage_matrix()
        matrix["required_journeys"][1] = {
            "journey_id": "J-tray",
            "title": "桌面托盘最近书籍",
            "acceptance_ids": ["A9"],
            "case_ids": [],
            "checkpoint_ids": [],
            "status": "deferred_manual",
            "residual_code": "e2e_campaign_manual_test_required",
            "feature": "桌面托盘最近书籍",
        }
        result = MOD.lint_coverage_matrix(matrix)
        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
