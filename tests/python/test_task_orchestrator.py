from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "skills" / "granoflow-task-orchestrator" / "scripts" / "route_task_intent.py"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("task_orchestrator", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TaskOrchestratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_capture_shortcuts_override_mature_context_without_starting_work(self) -> None:
        for command in ("gf记 顺便记下导入预览", "gf+ 顺便记下导入预览"):
            with self.subTest(command=command):
                result = self.module.route(
                    {
                        "request": command,
                        "currentWorkRelation": "side_thought",
                        "outcomeClear": True,
                        "boundariesClear": True,
                        "evidenceSufficient": True,
                        "targetAmbiguous": False,
                    }
                )
                self.assertEqual(result["route"], "capture")
                self.assertEqual(result["taskDepth"], "minimal")
                self.assertEqual(result["stopPoint"], "task_readback")
                self.assertEqual(result["duePolicy"], "none")
                self.assertFalse(result["executionAuthorized"])

    def test_incidental_side_thought_defaults_to_undated_inbox_capture(self) -> None:
        result = self.module.route(
            {
                "request": "顺便记一下，以后给导入加预览",
                "currentWorkRelation": "side_thought",
                "imperative": "remember_later",
                "outcomeClear": True,
                "boundariesClear": False,
                "evidenceSufficient": False,
                "timingSignal": "none",
                "placementStrength": "weak",
                "targetAmbiguous": False,
            }
        )
        self.assertEqual(result["route"], "capture")
        self.assertEqual(result["placementPolicy"], "inbox")
        self.assertEqual(result["duePolicy"], "none")
        self.assertEqual(result["reasonCode"], "incidental_side_thought")

    def test_analyze_shortcuts_stop_after_decision_ready_analysis(self) -> None:
        for command in ("gf析 整理刚才的同步兼容讨论", "gf? 整理刚才的同步兼容讨论"):
            with self.subTest(command=command):
                result = self.module.route(
                    {
                        "request": command,
                        "currentWorkRelation": "same_work",
                        "outcomeClear": True,
                        "boundariesClear": True,
                        "evidenceSufficient": True,
                        "targetAmbiguous": False,
                    }
                )
                self.assertEqual(result["route"], "analyze")
                self.assertEqual(result["taskDepth"], "contextual")
                self.assertEqual(result["stopPoint"], "analysis_confirmed_or_blocked")
                self.assertFalse(result["executionAuthorized"])

    def test_run_shortcuts_authorize_only_ready_local_safe_scope(self) -> None:
        for command in ("gf做 完成这个任务", "gf! 完成这个任务"):
            with self.subTest(command=command):
                result = self.module.route(
                    {
                        "request": command,
                        "currentWorkRelation": "same_work",
                        "outcomeClear": True,
                        "boundariesClear": True,
                        "evidenceSufficient": True,
                        "targetAmbiguous": False,
                        "localSafeProfileApproved": True,
                        "analysisGrillPassed": True,
                        "planningConfirmed": True,
                        "readinessGrillPassed": True,
                        "unresolvedDecisionCount": 0,
                        "scopeEscalated": False,
                        "requestedActions": [
                            "gf_task_write",
                            "local_versioned_code_edit",
                            "local_test",
                        ],
                    }
                )
                self.assertEqual(result["route"], "run")
                self.assertEqual(result["taskDepth"], "execution_ready")
                self.assertEqual(result["stopPoint"], "done_readback")
                self.assertEqual(result["authorizationMode"], "gf-local-safe-v1")
                self.assertTrue(result["executionAuthorized"])

    def test_local_safe_profile_never_authorizes_forbidden_actions(self) -> None:
        for action in (
            "publish",
            "git_push",
            "delete",
            "login",
            "secret_2fa",
            "external_message",
        ):
            with self.subTest(action=action):
                result = self.module.route(
                    {
                        "request": "gf做 完成并发布这个任务",
                        "localSafeProfileApproved": True,
                        "analysisGrillPassed": True,
                        "planningConfirmed": True,
                        "readinessGrillPassed": True,
                        "unresolvedDecisionCount": 0,
                        "scopeEscalated": False,
                        "requestedActions": ["local_test", action],
                    }
                )
                self.assertEqual(result["route"], "run")
                self.assertFalse(result["executionAuthorized"])
                self.assertEqual(result["reasonCode"], "forbidden_action")

    def test_local_safe_profile_fails_closed_for_ambiguous_or_undeclared_work(self) -> None:
        base = {
            "request": "gf做 完成这个任务",
            "localSafeProfileApproved": True,
            "analysisGrillPassed": True,
            "planningConfirmed": True,
            "readinessGrillPassed": True,
            "unresolvedDecisionCount": 0,
            "scopeEscalated": False,
        }
        cases = [
            ({"targetAmbiguous": True, "requestedActions": ["local_test"]}, "ambiguous_target"),
            ({"targetAmbiguous": False, "requestedActions": []}, "action_not_declared"),
            (
                {
                    "targetAmbiguous": False,
                    "requestedActions": ["local_test", "unknown_future_action"],
                },
                "unknown_action",
            ),
        ]
        for facts, reason_code in cases:
            with self.subTest(facts=facts):
                result = self.module.route({**base, **facts})
                self.assertEqual(result["route"], "run")
                self.assertFalse(result["executionAuthorized"])
                self.assertEqual(result["reasonCode"], reason_code)

    def test_plan_and_finish_shortcuts_have_distinct_stopping_points(self) -> None:
        cases = [
            ("gf规 拆解这个任务", "plan", "readiness_passed"),
            ("gf> 拆解这个任务", "plan", "readiness_passed"),
            ("gf完 审计刚完成的任务", "finish_audit", "done_readback"),
            ("gf. 审计刚完成的任务", "finish_audit", "done_readback"),
        ]
        for command, route, stop_point in cases:
            with self.subTest(command=command):
                result = self.module.route({"request": command, "targetAmbiguous": False})
                self.assertEqual(result["route"], route)
                self.assertEqual(result["stopPoint"], stop_point)
                self.assertFalse(result["executionAuthorized"])

    def test_plain_language_routes_from_structured_context_facts(self) -> None:
        cases = [
            ({"imperative": "remember_later"}, "capture"),
            (
                {
                    "imperative": "register",
                    "outcomeClear": True,
                    "boundariesClear": True,
                    "evidenceSufficient": True,
                },
                "enrich",
            ),
            ({"imperative": "analyze"}, "analyze"),
            ({"imperative": "plan"}, "plan"),
            ({"imperative": "execute"}, "run"),
            ({"alreadyComplete": True}, "finish_audit"),
        ]
        for facts, expected_route in cases:
            with self.subTest(facts=facts):
                result = self.module.route(
                    {
                        "request": "gf 根据当前上下文处理这个任务",
                        "currentWorkRelation": "same_work",
                        "targetAmbiguous": False,
                        **facts,
                    }
                )
                self.assertEqual(result["route"], expected_route)

    def test_due_date_ladder_uses_evidence_and_allows_no_date(self) -> None:
        cases = [
            ({"explicitDueAt": "2026-09-30T23:59:59+08:00"}, "explicit"),
            ({"dependencyDueAt": "2026-07-21T12:00:00+08:00"}, "dependency"),
            ({"activeBlocking": True, "todayDueAt": "2026-07-17T23:59:59+08:00"}, "today"),
            (
                {"concreteNearAction": True, "tomorrowDueAt": "2026-07-18T23:59:59+08:00"},
                "tomorrow",
            ),
            ({"milestoneDueAt": "2026-07-31T23:59:59+08:00"}, "milestone"),
            ({}, "none"),
        ]
        for facts, reason in cases:
            with self.subTest(facts=facts):
                result = self.module.choose_due_at(facts)
                self.assertEqual(result["reasonCode"], reason)
        self.assertIsNone(self.module.choose_due_at({})["dueAt"])

    def test_cli_help_dry_run_and_structured_route(self) -> None:
        help_result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--facts", help_result.stdout)

        dry_run = subprocess.run(
            [sys.executable, str(SCRIPT), "--dry-run"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(dry_run.returncode, 0)
        self.assertEqual(json.loads(dry_run.stdout)["mode"], "dry-run")

        with tempfile.TemporaryDirectory() as directory:
            facts_path = Path(directory) / "facts.json"
            facts_path.write_text(
                json.dumps(
                    {
                        "request": "gf记 顺便记录这个想法",
                        "currentWorkRelation": "side_thought",
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--facts", str(facts_path)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["route"], "capture")


if __name__ == "__main__":
    unittest.main()
