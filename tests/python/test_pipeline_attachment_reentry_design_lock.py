#!/usr/bin/env python3
"""Preserve pipeline attachment / re-entry contract tokens across polish."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "temp" / "pipeline-attachment-reentry-design-lock-v1.json"


class PipelineAttachmentReentryDesignLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))
        status = cls.lock.get("status") or {}
        if status.get("confirmed") is not True:
            raise AssertionError("design lock must be confirmed before polish/check")

    def test_lock_has_constraints(self) -> None:
        constraints = self.lock.get("constraints") or []
        self.assertGreaterEqual(len(constraints), 3)

    def test_each_constraint_preserved_in_files(self) -> None:
        missing: list[str] = []
        for item in self.lock.get("constraints") or []:
            cid = item.get("id") or item.get("text", "")[:40]
            needles = item.get("must_contain") or []
            paths = item.get("preserve_in") or []
            if not needles or not paths:
                missing.append(f"{cid}: missing must_contain or preserve_in")
                continue
            blobs: list[str] = []
            for rel in paths:
                path = ROOT / rel
                if not path.is_file():
                    missing.append(f"{cid}: missing file {rel}")
                    continue
                blobs.append(path.read_text(encoding="utf-8"))
            joined = "\n".join(blobs)
            for needle in needles:
                if needle not in joined:
                    missing.append(f"{cid}: {needle!r} not found in {paths}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_hard_gate_wires_pipeline_reference(self) -> None:
        skill = (ROOT / "skills" / "granoflow-agent-workflow" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("pipeline-attachment-and-reentry", skill)
        self.assertIn("pipeline_reentry_skipped", skill)


if __name__ == "__main__":
    unittest.main()
