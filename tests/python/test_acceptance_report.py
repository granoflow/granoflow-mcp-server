from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-persistent-milestone-runner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from acceptance_report import build_report, validate_manifest, validate_report_html  # noqa: E402


def manifest() -> dict[str, object]:
    return {
        "schema": "granoflow_acceptance_report_v1",
        "title": "节点接力验收",
        "generatedAt": "2026-07-18T12:00:00+08:00",
        "summary": "实现完成，真实集成运行留给后续测试任务。",
        "changes": {
            "code": ["新增 lane 选择器"],
            "database": ["无 schema 变化"],
            "workflow": ["增加三种执行模式"],
        },
        "verification": {
            "automated": [
                {"name": "Python unit tests", "status": "passed", "evidence": "11 tests"}
            ],
            "integration": {
                "status": "not_required",
                "reason": "本任务只编排脚本，不运行脚本。",
                "scripts": [{"path": "scripts/acceptance.sh", "check": "shellcheck passed"}],
            },
            "screenshots": {
                "status": "not_required",
                "reason": "没有用户界面运行要求。",
                "items": [],
            },
        },
    }


class AcceptanceReportTests(unittest.TestCase):
    def test_report_is_self_contained_even_without_screenshots(self) -> None:
        html = build_report(validate_manifest(manifest()), Path.cwd())
        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("not_required", html)
        self.assertIn("没有用户界面运行要求", html)
        self.assertNotIn("<script", html.lower())
        self.assertEqual(validate_report_html(html), "ok")

    def test_report_escapes_text_and_embeds_only_declared_local_images(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "proof.png"
            image.write_bytes(b"\x89PNG\r\n\x1a\nproof")
            value = manifest()
            value["summary"] = "<script>alert(1)</script>"
            verification = value["verification"]
            assert isinstance(verification, dict)
            screenshots = verification["screenshots"]
            assert isinstance(screenshots, dict)
            screenshots.update(
                {
                    "status": "passed",
                    "reason": "关键流程已截图。",
                    "items": [{"path": "proof.png", "caption": "关键 <画面>"}],
                }
            )
            html = build_report(validate_manifest(value), root)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
            self.assertIn("data:image/png;base64,", html)
            self.assertIn("关键 &lt;画面&gt;", html)
            self.assertEqual(validate_report_html(html), "ok")

    def test_manifest_requires_explicit_not_required_reason(self) -> None:
        value = manifest()
        verification = value["verification"]
        assert isinstance(verification, dict)
        integration = verification["integration"]
        assert isinstance(integration, dict)
        integration["reason"] = ""
        with self.assertRaisesRegex(ValueError, "integration.reason"):
            validate_manifest(value)

    def test_manifest_round_trip_is_json_serializable(self) -> None:
        self.assertEqual(
            json.loads(json.dumps(validate_manifest(manifest())))["schema"],
            "granoflow_acceptance_report_v1",
        )


if __name__ == "__main__":
    unittest.main()
