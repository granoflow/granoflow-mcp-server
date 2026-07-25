#!/usr/bin/env python3
"""Tests for lint_milestone_plan_acceptance_pack.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_milestone_plan_acceptance_pack.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_milestone_plan_acceptance_pack", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()

BODY_WITH_LANES = """
# Milestone Plan Acceptance

## 5. Test cases

### Unit

| ID | Lane | Case | Traces to | Expected | Task |
| --- | ---- | ---- | --------- | -------- | ---- |
| U1 | unit | validates open | Outcome | ok | T1 |

### Integration

| ID | Lane | Case | Traces to | Expected | Task |
| --- | ---- | ---- | --------- | -------- | ---- |
| I1 | integration | open then list | Outcome | ok | T1 |

### E2E

| ID | Lane | Case | Traces to | Expected | Task |
| --- | ---- | ---- | --------- | -------- | ---- |
| E1 | e2e | user opens library | Outcome | ok | T1 |
"""


def ok_pack(**overrides: Any) -> dict[str, Any]:
    pack: dict[str, Any] = {
        "doc_type": "milestone_plan_acceptance_pack",
        "milestone_key": "M1",
        "version": 1,
        "status": "accepted",
        "software_ui_milestone": True,
        "in_scope_task_ids": ["task-1"],
        "sections": {
            "user_copy": {"present": False, "basis": "none"},
            "data_structures": {"present": False, "basis": "none"},
            "flowcharts": {"present": False, "basis": "none"},
            "uml_diagrams": {"present": False, "basis": "none"},
            "test_cases": {"present": True, "basis": ""},
        },
        "prototype_alignment": {
            "schema": "granoflow_milestone_plan_prototype_alignment_v1",
            "status": "aligned",
            "tasks": [
                {
                    "task_id": "task-1",
                    "prototype_package_sha256": "a" * 64,
                    "aligned": True,
                    "evidence": "pack flows match confirmed prototype SHA",
                }
            ],
        },
        "html_render": {
            "status": "tools_missing",
            "html_path": None,
            "html_file_url": None,
            "markdown_path": "/tmp/pack.md",
            "markdown_file_url": "file:///tmp/pack.md",
            "link_emitted": True,
            "tool_probe": {
                "pandoc": False,
                "mmdc": False,
                "diagram_lua": False,
                "plantuml": False,
            },
            "note": "",
        },
        "body_markdown": BODY_WITH_LANES,
    }
    pack.update(overrides)
    return pack


def write_pack(directory: Path, pack: dict[str, Any]) -> Path:
    path = directory / "pack.json"
    path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    return path


class LintMilestonePlanAcceptancePackTests(unittest.TestCase):
    def test_ok_closeout_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_pack(Path(tmp), ok_pack())
            result = MOD.lint_milestone_plan_acceptance_pack(path, require_links=True)
            self.assertTrue(result["ok"], result)

    def test_missing_e2e_lane_fails(self) -> None:
        body = BODY_WITH_LANES.replace("| e2e  |", "| manual |").replace("E1 | e2e", "E1 | manual")
        # remove e2e lane rows entirely
        body = """
## Test cases
| ID | Lane | Case | Traces to | Expected | Task |
| --- | ---- | ---- | --------- | -------- | ---- |
| U1 | unit | x | y | z | T1 |
| I1 | integration | x | y | z | T1 |
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = write_pack(Path(tmp), ok_pack(body_markdown=body))
            result = MOD.lint_milestone_plan_acceptance_pack(path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "milestone_plan_test_lanes_incomplete")

    def test_alignment_false_fails(self) -> None:
        pack = ok_pack()
        pack["prototype_alignment"]["tasks"][0]["aligned"] = False
        with tempfile.TemporaryDirectory() as tmp:
            path = write_pack(Path(tmp), pack)
            result = MOD.lint_milestone_plan_acceptance_pack(path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "milestone_plan_prototype_alignment_failed")

    def test_require_links_without_emit_fails(self) -> None:
        pack = ok_pack()
        pack["html_render"]["link_emitted"] = False
        with tempfile.TemporaryDirectory() as tmp:
            path = write_pack(Path(tmp), pack)
            result = MOD.lint_milestone_plan_acceptance_pack(path, require_links=True)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "plan_acceptance_html_link_required")

    def test_html_ready_missing_file_fails(self) -> None:
        pack = ok_pack()
        pack["html_render"]["status"] = "ready"
        pack["html_render"]["html_file_url"] = "file:///tmp/granoflow-missing-acceptance.html"
        with tempfile.TemporaryDirectory() as tmp:
            path = write_pack(Path(tmp), pack)
            result = MOD.lint_milestone_plan_acceptance_pack(path, require_links=True)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "plan_acceptance_html_link_required")

    def test_html_ready_existing_file_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            html = root / "milestone-plan-acceptance-M1-v1.html"
            html.write_text("<html>ok</html>", encoding="utf-8")
            pack = ok_pack()
            pack["html_render"]["status"] = "ready"
            pack["html_render"]["html_file_url"] = html.resolve().as_uri()
            pack["html_render"]["html_path"] = str(html.resolve())
            path = write_pack(root, pack)
            result = MOD.lint_milestone_plan_acceptance_pack(path, require_links=True)
            self.assertTrue(result["ok"], result)

    def test_draft_without_closeout_skips_lane_requirement(self) -> None:
        pack = ok_pack(
            status="draft",
            body_markdown="## Test cases\n(pending)",
            sections={
                "user_copy": {"present": False, "basis": "none"},
                "data_structures": {"present": False, "basis": "none"},
                "flowcharts": {"present": False, "basis": "none"},
                "uml_diagrams": {"present": False, "basis": "none"},
                "test_cases": {"present": False, "basis": "still_drafting"},
            },
        )
        pack["html_render"]["link_emitted"] = False
        with tempfile.TemporaryDirectory() as tmp:
            path = write_pack(Path(tmp), pack)
            result = MOD.lint_milestone_plan_acceptance_pack(path)
            self.assertTrue(result["ok"], result)

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_pack(root, ok_pack())
            self.assertEqual(MOD.main([str(path), "--require-links"]), 0)
            bad = ok_pack()
            bad["html_render"]["link_emitted"] = False
            bad_dir = root / "bad"
            bad_dir.mkdir()
            bad_path = write_pack(bad_dir, bad)
            self.assertEqual(MOD.main([str(bad_path), "--require-links"]), 1)


if __name__ == "__main__":
    unittest.main()
