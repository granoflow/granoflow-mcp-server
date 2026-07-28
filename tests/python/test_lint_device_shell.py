#!/usr/bin/env python3
"""Tests for lint_device_shell.py and copy_device_shell_assets.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINT = ROOT / "skills" / "granoflow-project-definition" / "scripts" / "lint_device_shell.py"
COPY = ROOT / "skills" / "granoflow-project-definition" / "scripts" / "copy_device_shell_assets.py"
IPHONE_FRAME = (
    ROOT
    / "skills"
    / "granoflow-project-definition"
    / "assets"
    / "device-shells"
    / "iphone-17-pro-portrait"
    / "frame.html"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LINT_MOD = load_module("lint_device_shell", LINT)
COPY_MOD = load_module("copy_device_shell_assets", COPY)


def iphone_html() -> str:
    frame = IPHONE_FRAME.read_text(encoding="utf-8")
    return f"""<!DOCTYPE html><html><head></head><body>
{frame}
</body></html>"""


class LintDeviceShellTests(unittest.TestCase):
    def test_valid_iphone_profile_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mobile.html"
            path.write_text(iphone_html(), encoding="utf-8")
            result = LINT_MOD.lint_paths(
                [path],
                required_profile_ids={"iphone_17_pro_portrait_v1"},
            )
            self.assertTrue(result["ok"], result)

    def test_missing_profile_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bare.html"
            path.write_text("<html><body><div>no shell</div></body></html>", encoding="utf-8")
            result = LINT_MOD.lint_paths(
                [path],
                required_profile_ids={"iphone_17_pro_portrait_v1"},
            )
            self.assertFalse(result["ok"])
            codes = {err["code"] for err in result["errors"]}
            self.assertIn("device_shell_profile_missing", codes)

    def test_layout_families_resolve_defaults_only(self) -> None:
        profiles = LINT_MOD.resolve_required_profiles(
            profile_ids=None,
            layout_family_ids=["mobile_portrait", "desktop_landscape"],
        )
        self.assertEqual(
            profiles,
            {"iphone_17_pro_portrait_v1", "macos_tahoe_window_v1"},
        )

    def test_layout_bindings_override_android_windows(self) -> None:
        profiles = LINT_MOD.resolve_required_profiles(
            profile_ids=None,
            layout_family_ids=["mobile_portrait", "desktop_landscape"],
            layout_bindings={
                "mobile_portrait": "android_phone_portrait_v1",
                "desktop_landscape": "windows_11_window_v1",
            },
        )
        self.assertEqual(
            profiles,
            {"android_phone_portrait_v1", "windows_11_window_v1"},
        )

    def test_tablet_defaults(self) -> None:
        profiles = LINT_MOD.resolve_required_profiles(
            profile_ids=None,
            layout_family_ids=["tablet_portrait", "tablet_landscape"],
        )
        self.assertEqual(
            profiles,
            {"ipad_pro_11_portrait_v1", "ipad_pro_11_landscape_v1"},
        )

    def test_cli_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mobile.html"
            path.write_text(iphone_html(), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(LINT),
                    str(path),
                    "--profiles",
                    "iphone_17_pro_portrait_v1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])


class CopyDeviceShellAssetsTests(unittest.TestCase):
    def test_copy_profiles_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            result = COPY_MOD.copy_profiles(
                dest,
                ["iphone_17_pro_portrait_v1", "macos_tahoe_window_v1"],
            )
            self.assertTrue(result["ok"], result)
            css = dest / "device-shells" / "iphone_17_pro_portrait_v1" / "device-shell.css"
            registry = dest / "device-shells" / "device-shell-registry.json"
            self.assertTrue(css.is_file())
            self.assertTrue(registry.is_file())

    def test_copy_layout_families_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(COPY),
                    "--dest",
                    str(dest),
                    "--layout-families",
                    "mobile_portrait,desktop_landscape",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            android_css = dest / "device-shells" / "android_phone_portrait_v1" / "device-shell.css"
            iphone_css = dest / "device-shells" / "iphone_17_pro_portrait_v1" / "device-shell.css"
            self.assertFalse(android_css.is_file())
            self.assertTrue(iphone_css.is_file())

    def test_unknown_profile_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = COPY_MOD.copy_profiles(Path(tmp), ["does_not_exist_v9"])
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "device_shell_profile_unknown")


if __name__ == "__main__":
    unittest.main()
