#!/usr/bin/env python3
"""Tests for lint_prototype_user_copy.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_prototype_user_copy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_user_copy", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


CLEAN = """<!DOCTYPE html><html><body>
<p class="thesis" data-reviewer-only>设计理由：仅按后缀统计（评审说明）</p>
<div class="phone">
  <h1>导入 EPUB</h1>
  <p>已选：…/Books/金庸合集</p>
  <button>开始导入 · 128 本</button>
  <p>开始后不可取消、不可暂停。</p>
</div>
</body></html>
"""

LEAKY = """<!DOCTYPE html><html><body>
<div class="phone">
  <h1>导入 EPUB</h1>
  <p>0 本的类型不显示。本批不会在确认页列出文件名。</p>
  <button>开始导入</button>
</div>
</body></html>
"""

NO_FRAME_LEAK = """<!DOCTYPE html><html><body>
<p>仅按后缀统计，不在导入前计算 MD5。</p>
</body></html>
"""


class LintPrototypeUserCopyTests(unittest.TestCase):
    def test_clean_phone_with_outside_thesis_ok(self) -> None:
        result = MOD.lint_html(CLEAN)
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["productFrameScoped"])

    def test_leaky_phone_fails(self) -> None:
        result = MOD.lint_html(LEAKY)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failCode"], "user_visible_copy_boundary_violation")
        codes = {h["code"] for h in result["hits"]}
        self.assertIn("zero_type_hidden", codes)
        self.assertIn("no_filenames_on_confirm", codes)

    def test_no_frame_body_is_scanned(self) -> None:
        result = MOD.lint_html(NO_FRAME_LEAK)
        self.assertFalse(result["ok"])
        self.assertFalse(result["productFrameScoped"])

    def test_cli_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(LEAKY, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(payload["ok"])

    def test_cli_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(CLEAN, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
