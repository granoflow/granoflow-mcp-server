#!/usr/bin/env python3
"""Tests for lint_prototype_stack.py (Vanilla JS stack lock v1)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_prototype_stack.py"
PACKAGER = ROOT / "skills" / "granoflow-project-definition" / "scripts" / "package_prototype.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_stack", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class LintPrototypeStackTest(unittest.TestCase):
    def test_clean_html_css_js_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                "<!doctype html><html><body>"
                '<button id="open">Open</button>'
                '<div id="sheet" hidden>Sheet</div>'
                '<script src="app.js"></script>'
                "</body></html>",
                encoding="utf-8",
            )
            (root / "app.js").write_text(
                "document.getElementById('open').onclick=()=>{"
                "document.getElementById('sheet').hidden=false;};",
                encoding="utf-8",
            )
            (root / "app.css").write_text("body{margin:0}", encoding="utf-8")
            result = MOD.lint_prototype_stack(root)
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["code"], "ok")

    def test_rejects_tsx(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text("<!doctype html>", encoding="utf-8")
            (root / "App.tsx").write_text("export const App = () => null;", encoding="utf-8")
            result = MOD.lint_prototype_stack(root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_stack_forbidden_language")

    def test_rejects_package_json_with_react(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text("<!doctype html>", encoding="utf-8")
            (root / "package.json").write_text(
                '{"dependencies":{"react":"18.0.0"}}',
                encoding="utf-8",
            )
            result = MOD.lint_prototype_stack(root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_stack_forbidden_toolchain")

    def test_rejects_cdn_react(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                "<!doctype html><html><body>"
                '<script src="https://unpkg.com/react@18/umd/react.production.min.js">'
                "</script></body></html>",
                encoding="utf-8",
            )
            result = MOD.lint_prototype_stack(root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_stack_forbidden_framework")

    def test_package_prototype_rejects_forbidden_stack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "index.html").write_text("<!doctype html>", encoding="utf-8")
            (source / "main.ts").write_text("const x: number = 1;", encoding="utf-8")
            output = root / "out.zip"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PACKAGER),
                    str(source),
                    str(output),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload.get("failCode"), "prototype_stack_forbidden_language")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
