#!/usr/bin/env python3
"""Forward-test the generic inference expected from the GranoReader defect."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT / "tests" / "python" / "fixtures" / "granoreader_background_activity_forward_test.json"
)


class BackgroundActivityForwardFixtureTests(unittest.TestCase):
    def test_defect_generalizes_to_state_boundary_and_cross_update_route(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        generalized = fixture["expected_generalization"]
        self.assertTrue(generalized["allowed_background_changes"])
        self.assertTrue(generalized["must_not_change"])
        self.assertIn("exit_control", generalized["controls_that_must_keep_working"])
        self.assertEqual(
            generalized["test_sequence"][1:6],
            [
                "first_background_event",
                "protected_user_action",
                "second_background_event",
                "user_action_preserved",
                "exit_action",
            ],
        )
        self.assertEqual(
            set(generalized["required_test_layers"]),
            {"integration", "e2e"},
        )

    def test_special_case_terms_are_absent_from_generic_rules(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        targets = [
            ROOT
            / "skills"
            / "granoflow-project-definition"
            / "scripts"
            / "lint_product_spec_coverage.py",
            ROOT
            / "skills"
            / "granoflow-agent-workflow"
            / "scripts"
            / "lint_test_route_traceability.py",
            ROOT
            / "skills"
            / "granoflow-integration-test-campaign"
            / "scripts"
            / "lint_integration_campaign_artifacts.py",
            ROOT
            / "skills"
            / "granoflow-e2e-test-campaign"
            / "scripts"
            / "lint_e2e_campaign_artifacts.py",
        ]
        generic_rules = "\n".join(path.read_text(encoding="utf-8").lower() for path in targets)
        for term in fixture["forbidden_rule_special_cases"]:
            self.assertNotIn(term, generic_rules)


if __name__ == "__main__":
    unittest.main()
