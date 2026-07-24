from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-e2e-test-campaign" / "scripts" / "probe_execution_hosts.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe_execution_hosts", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOD = load_module()


def hosts() -> list[dict]:
    return [
        {
            "id": "macos_current",
            "kind": "desktop",
            "provider": "current_platform",
            "platforms": ["macos"],
            "status": "available",
            "e2e_capable": True,
        },
        {
            "id": "ios_official",
            "kind": "simulator",
            "provider": "official_virtual",
            "platforms": ["ios"],
            "status": "available",
            "e2e_capable": True,
        },
        {
            "id": "android_third_party",
            "kind": "other",
            "provider": "third_party_virtual",
            "platforms": ["android"],
            "status": "available",
            "e2e_capable": True,
        },
    ]


class SelectionTests(unittest.TestCase):
    def test_interactive_no_selection_tests_only_current_platform(self) -> None:
        result = MOD.select_hosts(
            hosts(),
            project_platforms=["macos", "ios", "android"],
            primary_platform="ios",
            mode="interactive",
            selected_host_ids=[],
            current="macos",
        )
        self.assertEqual(result["source"], "current_platform_default")
        self.assertEqual(result["selected_host_ids"], ["macos_current"])

    def test_unattended_tests_only_current_platform(self) -> None:
        result = MOD.select_hosts(
            hosts(),
            project_platforms=["macos", "ios"],
            primary_platform="ios",
            mode="unattended",
            selected_host_ids=[],
            current="macos",
        )
        self.assertEqual(result["selected_host_ids"], ["macos_current"])

    def test_mobile_only_uses_primary_official_simulator(self) -> None:
        result = MOD.select_hosts(
            hosts(),
            project_platforms=["ios", "android"],
            primary_platform="ios",
            mode="unattended",
            selected_host_ids=[],
            current="macos",
        )
        self.assertEqual(result["source"], "ai_fallback")
        self.assertEqual(result["selected_host_ids"], ["ios_official"])

    def test_interactive_user_can_select_installed_third_party_vm(self) -> None:
        result = MOD.select_hosts(
            hosts(),
            project_platforms=["android"],
            primary_platform="android",
            mode="interactive",
            selected_host_ids=["android_third_party"],
            current="macos",
        )
        self.assertEqual(result["source"], "user_selection")
        self.assertEqual(result["selected_host_ids"], ["android_third_party"])

    def test_unattended_ignores_optional_user_selection_input(self) -> None:
        result = MOD.select_hosts(
            hosts(),
            project_platforms=["macos", "ios"],
            primary_platform="ios",
            mode="unattended",
            selected_host_ids=["ios_official"],
            current="macos",
        )
        self.assertEqual(result["source"], "current_platform_default")
        self.assertEqual(result["selected_host_ids"], ["macos_current"])


if __name__ == "__main__":
    unittest.main()
