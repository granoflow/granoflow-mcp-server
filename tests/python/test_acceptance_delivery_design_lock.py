#!/usr/bin/env python3
"""Preserve chat-thread acceptance/delivery constraints across polish.

Reads temp/acceptance-delivery-design-lock-v1.json and asserts each constraint's
must_contain tokens still appear in the listed skill files. Prevents generative
or manual polish from silently dropping this thread's requirements.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "temp" / "acceptance-delivery-design-lock-v1.json"


class AcceptanceDeliveryDesignLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))
        status = cls.lock.get("status") or {}
        if status.get("confirmed") is not True:
            raise AssertionError("design lock must be confirmed before polish/check")

    def test_lock_has_constraints(self) -> None:
        constraints = self.lock.get("constraints") or []
        self.assertGreaterEqual(len(constraints), 8)

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

    def test_forbids_old_single_milestone_silence_rule(self) -> None:
        """Regression: do not resurrect 'never prompt final delivery' after 1 milestone."""
        full = (
            ROOT
            / "skills"
            / "granoflow-agent-workflow"
            / "references"
            / "full-delivery-acceptance.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("satisfied_single_milestone", full)
        self.assertNotIn("full_delivery_prompt_forbidden_single_milestone", full)
        self.assertIn("e2e_direct", full)
        self.assertIn("waived_single_milestone", full)


if __name__ == "__main__":
    unittest.main()
