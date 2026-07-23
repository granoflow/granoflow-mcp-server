#!/usr/bin/env python3
"""Tests for render_markdown_acceptance_html.py probe helpers."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "render_markdown_acceptance_html.py"
)
VENDOR_LUA = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "vendor"
    / "pandoc-ext-diagram"
    / "diagram.lua"
)


def load_module():
    spec = importlib.util.spec_from_file_location("render_markdown_acceptance_html", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class ProbeTests(unittest.TestCase):
    def test_vendor_lua_resolves(self) -> None:
        self.assertTrue(VENDOR_LUA.is_file())
        resolved = MOD.resolve_diagram_lua(None)
        self.assertEqual(resolved, VENDOR_LUA.resolve())

    def test_probe_missing_when_no_binaries(self) -> None:
        with mock.patch.object(MOD, "_which", return_value=None):
            result = MOD.probe_toolchain()
        self.assertEqual(result["status"], "missing")
        self.assertIn("pandoc", result["missing"])
        self.assertIn("mmdc", result["missing"])
        self.assertNotIn("diagram_lua", result["missing"])
        self.assertIn("token", result["token_note"].lower())

    def test_probe_ready_when_binaries_present(self) -> None:
        def fake_which(name: str) -> str | None:
            return f"/usr/bin/{name}" if name in {"pandoc", "mmdc"} else None

        with mock.patch.object(MOD, "_which", side_effect=fake_which):
            result = MOD.probe_toolchain()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["missing"], [])
        self.assertTrue(result["tools"]["diagram_lua"])

    def test_render_reports_missing_without_running_pandoc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "pack.md"
            md.write_text("# hi\n", encoding="utf-8")
            with mock.patch.object(MOD, "_which", return_value=None):
                result = MOD.render_html(md)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "markdown_html_toolchain_missing")
        self.assertIsNone(result["html_path"])
        self.assertTrue(str(result["markdown_file_url"]).startswith("file://"))

    def test_path_to_file_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.html"
            path.write_text("<html></html>", encoding="utf-8")
            url = MOD.path_to_file_url(path)
        self.assertTrue(url.startswith("file://"))
        self.assertTrue(url.endswith("a.html"))


if __name__ == "__main__":
    unittest.main()
