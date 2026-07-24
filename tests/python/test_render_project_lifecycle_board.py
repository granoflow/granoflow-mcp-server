#!/usr/bin/env python3
"""Tests for render_project_lifecycle_board.py."""

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
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "render_project_lifecycle_board.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("render_project_lifecycle_board", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()

STAGE_IDS = list(MOD.STAGE_IDS)


def base_board(*, mode: str = "interactive") -> dict:
    confirm = "display_only" if mode == "unattended" else "required"
    stages = []
    for i, sid in enumerate(STAGE_IDS):
        if i < 2:
            status = "done"
        elif i == 2:
            status = "in_progress"
        else:
            status = "not_started"
        stages.append(
            {
                "id": sid,
                "status": status,
                "evidence": f"evidence-{sid}",
            }
        )
    return {
        "project_id": "p1",
        "project_title": "Demo",
        "interaction_mode": mode,
        "board_confirmation": confirm,
        "updated_at": "2026-07-22T05:33:00Z",
        "contract_loaded": True,
        "stages": stages,
        "milestones": [
            {
                "key": "M1",
                "title": "First Ship",
                "analysis": "done",
                "plan": "in_progress",
                "implement": "not_started",
                "note": "Plan Gate pending",
            }
        ],
        "next_action": {
            "stage_id": "milestone_analysis",
            "summary": "完成当前里程碑剩余 Analysis 确认",
            "owner_skill": "granoflow-task-orchestrator",
            "needs_user_confirmation": mode == "interactive",
        },
        "blockers": [],
    }


class RenderBoardTests(unittest.TestCase):
    def test_interactive_ok(self) -> None:
        result = MOD.validate_and_render(base_board(mode="interactive"))
        self.assertTrue(result["ok"], result)
        self.assertIn("项目进度板", result["markdown"])
        self.assertIn("下一步", result["markdown"])
        self.assertEqual(result["earliest_incomplete"], "milestone_analysis")

    def test_pipeline_order_label_rendered(self) -> None:
        board = base_board(mode="interactive")
        board["pipeline_order"] = {
            "mode": "breadth_first",
            "decided_at": "2026-07-25T00:00:00Z",
            "decided_by": "user",
        }
        result = MOD.validate_and_render(board)
        self.assertTrue(result["ok"], result)
        self.assertIn("先全部分析", result["markdown"])
        self.assertIn("breadth_first", result["markdown"])

    def test_unattended_requires_display_only(self) -> None:
        board = base_board(mode="unattended")
        board["board_confirmation"] = "required"
        result = MOD.validate_and_render(board)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failCode"], "project_lifecycle_board_render_failed")

    def test_unattended_forbids_confirm_flag(self) -> None:
        board = base_board(mode="unattended")
        board["next_action"]["needs_user_confirmation"] = True
        result = MOD.validate_and_render(board)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failCode"], "project_lifecycle_board_confirm_in_unattended")

    def test_stage_skip_detected(self) -> None:
        board = base_board(mode="interactive")
        for row in board["stages"]:
            if row["id"] == "milestone_implement":
                row["status"] = "done"
        board["next_action"]["stage_id"] = "milestone_analysis"
        result = MOD.validate_and_render(board)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failCode"], "project_lifecycle_stage_skip")

    def test_missing_stage(self) -> None:
        board = base_board(mode="interactive")
        board["stages"] = board["stages"][:-1]
        result = MOD.validate_and_render(board)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failCode"], "project_lifecycle_board_incomplete_stages")

    def test_cli_ok(self) -> None:
        board = {"project_lifecycle_board": base_board(mode="interactive")}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "board.json"
            path.write_text(json.dumps(board), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])

    def test_single_project_milestone_allows_e2e_direct(self) -> None:
        """Project has 1 feature milestone: skip stage 6, next_action → e2e."""
        board = base_board(mode="interactive")
        for row in board["stages"]:
            if row["id"] in {
                "project_init",
                "milestones_created",
                "milestone_analysis",
                "milestone_plan",
                "milestone_implement",
            }:
                row["status"] = "done"
            else:
                row["status"] = "not_started"
        board["session_delivery"] = {
            "schema": "granoflow_session_delivery_v1",
            "milestones_touched_count": 1,
            "milestones_touched": ["M1"],
            "project_feature_milestone_count": 1,
            "pre_e2e_path": "e2e_direct",
            "status": "in_progress",
            "prompt_full_delivery": True,
            "other_milestones": [],
            "recommendation": "项目仅一个功能里程碑：跳过项目级 IT，直接全面 E2E。",
        }
        board["next_action"] = {
            "stage_id": "e2e_campaign",
            "summary": "开始最终交付：直接跑全项目 E2E。",
            "owner_skill": "granoflow-e2e-test-campaign",
            "needs_user_confirmation": False,
        }
        result = MOD.validate_and_render(board)
        self.assertTrue(result["ok"], result)
        self.assertIn("最终交付（本会话）", result["markdown"])
        self.assertIn("e2e_direct", result["markdown"])

    def test_optional_entry_kind_and_reentry_section(self) -> None:
        """Optional entry_kind/reentry must not break existing boards; render 回轨 when set."""
        board = base_board(mode="interactive")
        result = MOD.validate_and_render(board)
        self.assertTrue(result["ok"], result)
        self.assertNotIn("### 回轨", result["markdown"])

        board["entry_kind"] = "midstream_change"
        board["reentry"] = {
            "from_stage": "milestone_implement",
            "change_class": "task_local",
            "writeback_status": "written_and_read_back",
            "reason": "用户确认改了验收口径，已写回并退回 Analysis。",
        }
        board["next_action"]["summary"] = "已把刚才确认的改动写回真源；下一步回到 Analysis。"
        result = MOD.validate_and_render(board)
        self.assertTrue(result["ok"], result)
        self.assertIn("入口：`midstream_change`", result["markdown"])
        self.assertIn("### 回轨", result["markdown"])
        self.assertIn("task_local", result["markdown"])
        self.assertIn("written_and_read_back", result["markdown"])

        board["reentry"] = "not-an-object"
        result = MOD.validate_and_render(board)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failCode"], "project_lifecycle_board_render_failed")

    def test_e2e_direct_invalid_when_multiple_milestones(self) -> None:
        board = base_board(mode="interactive")
        for row in board["stages"]:
            if row["id"] in {
                "project_init",
                "milestones_created",
                "milestone_analysis",
                "milestone_plan",
                "milestone_implement",
            }:
                row["status"] = "done"
            else:
                row["status"] = "not_started"
        board["session_delivery"] = {
            "schema": "granoflow_session_delivery_v1",
            "milestones_touched_count": 1,
            "milestones_touched": ["M1"],
            "project_feature_milestone_count": 2,
            "pre_e2e_path": "e2e_direct",
            "status": "in_progress",
            "prompt_full_delivery": True,
            "other_milestones": [],
            "recommendation": "bad",
        }
        board["next_action"] = {
            "stage_id": "e2e_campaign",
            "summary": "开始 E2E",
            "owner_skill": "granoflow-e2e-test-campaign",
            "needs_user_confirmation": False,
        }
        result = MOD.validate_and_render(board)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failCode"], "full_delivery_session_fields_missing")


if __name__ == "__main__":
    unittest.main()
