#!/usr/bin/env python3
"""Tests for build_option_contrast_gallery.py."""

from __future__ import annotations

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
    / "granoflow-project-definition"
    / "scripts"
    / "build_option_contrast_gallery.py"
)


def run_script(manifest: dict, *, dry_run: bool = False) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        man = tmp_path / "manifest.json"
        out = tmp_path / "index.html"
        man.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, str(SCRIPT), str(man), str(out)]
        if dry_run:
            cmd.append("--dry-run")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        payload = json.loads(proc.stdout)
        return proc.returncode, payload


VALID = {
    "title": "Test Gallery",
    "design_system_locked": "ai_challenger",
    "tasks": [
        {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "title": "示例任务",
            "screens": ["S-welcome"],
            "contrast_axes": ["information_hierarchy", "interaction_pattern"],
            "visible_diffs": [
                {
                    "axis": "information_hierarchy",
                    "caption": "创建=实心主 CTA vs 打开=次级描边",
                },
                {
                    "axis": "interaction_pattern",
                    "caption": "双入口等权 vs 创建优先",
                },
            ],
            "options": [
                {
                    "id": "expr_a",
                    "summary": "创建优先顶栏",
                    "relative_href": "a/expr_a/index.html",
                },
                {
                    "id": "expr_b",
                    "summary": "双入口并排",
                    "relative_href": "a/expr_b/index.html",
                },
            ],
        }
    ],
}


class BuildOptionContrastGalleryTests(unittest.TestCase):
    def test_dry_run_ok(self) -> None:
        code, payload = run_script(VALID, dry_run=True)
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tasks"], 1)

    def test_write_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            man = tmp_path / "manifest.json"
            out = tmp_path / "index.html"
            man.write_text(json.dumps(VALID, ensure_ascii=False), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(man), str(out)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            html = out.read_text(encoding="utf-8")
            self.assertIn("可见差异", html)
            self.assertIn("创建=实心主 CTA vs 打开=次级描边", html)
            self.assertIn('iframe src="a/expr_a/index.html"', html)

    def test_design_system_reopen_rejected(self) -> None:
        bad = json.loads(json.dumps(VALID))
        bad["tasks"][0]["options"][0]["id"] = "delta_match"
        bad["tasks"][0]["options"][1]["id"] = "ai_challenger"
        code, payload = run_script(bad, dry_run=True)
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "prototype_option_design_system_reopened")

    def test_missing_visible_diffs(self) -> None:
        bad = json.loads(json.dumps(VALID))
        bad["tasks"][0]["visible_diffs"] = []
        code, payload = run_script(bad, dry_run=True)
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "prototype_option_diff_unlabeled")

    def test_single_option_rejected(self) -> None:
        bad = json.loads(json.dumps(VALID))
        bad["tasks"][0]["options"] = bad["tasks"][0]["options"][:1]
        code, payload = run_script(bad, dry_run=True)
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "prototype_option_contrast_gallery_required")


if __name__ == "__main__":
    unittest.main()
