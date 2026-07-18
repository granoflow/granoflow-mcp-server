from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-persistent-milestone-runner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from acceptance_attempt import rework_nodes, user_eligible  # noqa: E402


class AcceptanceAttemptTests(unittest.TestCase):
    def test_failed_integration_never_unlocks_user(self) -> None:
        eligible, reason = user_eligible(
            {
                "integrationDisposition": "required",
                "outcome": "failed",
                "reportSha256": "a" * 64,
                "current": True,
            }
        )
        self.assertFalse(eligible)
        self.assertEqual(reason, "integration_not_passed")

    def test_current_passed_report_unlocks_user(self) -> None:
        eligible, reason = user_eligible(
            {
                "integrationDisposition": "required",
                "outcome": "passed",
                "reportSha256": "a" * 64,
                "current": True,
            }
        )
        self.assertTrue(eligible)
        self.assertEqual(reason, "integration_passed")

    def test_failure_adds_a_new_traceable_rework_chain(self) -> None:
        self.assertEqual(
            [node["title"] for node in rework_nodes("窄屏按钮遮挡")],
            [
                "[dev] 修复验收失败：窄屏按钮遮挡",
                "[test] 验证普通测试回归",
                "[integration] 重新运行集成与截图验收",
                "[user] 用户重新确认",
            ],
        )
