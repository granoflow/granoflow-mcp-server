#!/usr/bin/env python3
"""Tests for mcp_skill_orchestrate.py (read-only audit)."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-skill-orchestrator" / "scripts" / "mcp_skill_orchestrate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mcp_skill_orchestrate", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class OrchestrateAuditTests(unittest.TestCase):
    def test_audit_repo_skills_ok(self) -> None:
        audits = [MOD.audit_skill(ROOT, d) for d in MOD.list_skill_dirs(ROOT / "skills")]
        self.assertGreaterEqual(len(audits), 10)
        # Newly added orchestrator skill should be present and structure-ok
        orch = next(a for a in audits if a.skill_id == "granoflow-skill-orchestrator")
        self.assertTrue(orch.ok_structure, orch.findings)
        self.assertIn(orch.recommendation, {"keep", "steward_audit", "manual_review"})

    def test_main_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "report.json"
            md_out = tmp_path / "report.md"
            code = MOD.main(
                [
                    "--repo",
                    str(ROOT),
                    "--skill",
                    "granoflow-skill-orchestrator",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ]
            )
            self.assertEqual(code, 0)
            report = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(report["schema"], MOD.SCHEMA)
            self.assertEqual(report["skill_count"], 1)
            self.assertTrue(report["recommended_plan"]["status"] == "awaiting_human_confirmation")
            self.assertTrue(md_out.is_file())
            self.assertIn("awaiting human confirmation", md_out.read_text(encoding="utf-8"))

    def test_apply_plan_unconfirmed_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.json"
            plan.write_text(json.dumps({"status": "draft"}), encoding="utf-8")
            code = MOD.main(["--repo", str(ROOT), "--apply-plan", str(plan)])
            self.assertEqual(code, 3)

    def test_draft_smell_without_lock_is_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill = repo / "skills" / "demo-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: demo-skill\n"
                "description: A short demo skill for orchestrator unit tests.\n"
                "---\n\n"
                "# Demo\n\n"
                "## Keyword\n\n- `#demo`\n\n"
                "## When to use\n\n- test\n\n"
                "## Workflow\n\n### 1\n\nTODO finish this scaffold.\n\n"
                "## Success Criteria\n\n- done\n",
                encoding="utf-8",
            )
            audit = MOD.audit_skill(repo, skill)
            self.assertTrue(audit.ok_structure)
            self.assertEqual(audit.recommendation, "manual_review")
            self.assertFalse(audit.polish_allowed)


if __name__ == "__main__":
    unittest.main()
