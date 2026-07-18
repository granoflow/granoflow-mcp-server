from __future__ import annotations

import re
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")


def user_eligible(manifest: dict[str, Any]) -> tuple[bool, str]:
    disposition = manifest.get("integrationDisposition")
    if disposition == "not_required":
        if manifest.get("reason") and manifest.get("alternativeEvidence"):
            return True, "integration_not_required"
        return False, "integration_not_required_evidence_missing"
    if disposition != "required":
        return False, "integration_waiting"
    if manifest.get("outcome") != "passed":
        return False, "integration_not_passed"
    report_sha = manifest.get("reportSha256")
    if not isinstance(report_sha, str) or not SHA256.fullmatch(report_sha):
        return False, "acceptance_report_sha_missing"
    if manifest.get("current") is not True:
        return False, "acceptance_attempt_not_current"
    return True, "integration_passed"


def rework_nodes(reason: str) -> list[dict[str, str]]:
    return [
        {"title": f"[dev] 修复验收失败：{reason}"},
        {"title": "[test] 验证普通测试回归"},
        {"title": "[integration] 重新运行集成与截图验收"},
        {"title": "[user] 用户重新确认"},
    ]
