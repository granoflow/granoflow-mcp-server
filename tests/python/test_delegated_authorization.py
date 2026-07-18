from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-delegated-authorization"
    / "scripts"
    / "validate_delegated_authorization.py"
)
TEST_TASK_ID = "task-delegated-authorization-test"
TEST_REPO = "/workspace/granoflow-mcp-server"
TEST_PLAN_HASH = "568c4e182bb62b33a68de19b1c97b1d0706155c42f3a9ae4981f4861842d40d3"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("delegated_authorization", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_envelope() -> dict[str, Any]:
    return {
        "schema": "granoflow_delegated_authorization_v1",
        "status": "confirmed",
        "envelopeId": "delegated-authorization-test-envelope",
        "authorizationOwnerTaskId": TEST_TASK_ID,
        "receiptPolicy": "app_readback_external",
        "issuedAt": "2026-07-17T09:00:00+08:00",
        "expiresAt": "2026-07-18T09:00:00+08:00",
        "sourceRef": "test-fixture",
        "taskIds": [TEST_TASK_ID],
        "phaseGrants": {
            "analysisConfirmation": True,
            "planningPermission": True,
            "planConfirmation": True,
            "executionAuthorization": True,
        },
        "planBindings": [
            {
                "taskIds": [TEST_TASK_ID],
                "path": "/workspace/plan.md",
                "sha256": TEST_PLAN_HASH,
            }
        ],
        "allowedRepos": [TEST_REPO],
        "allowedPathGlobs": {
            TEST_REPO: [
                "skills/granoflow-delegated-authorization/**",
                "tests/python/test_delegated_authorization.py",
            ]
        },
        "allowedActions": ["local_versioned_code_edit", "local_test"],
        "forbiddenActions": [
            "filesystem_delete_outside_versioned_plan",
            "user_data_delete",
            "approved_asset_overwrite",
            "git_commit",
            "git_push",
            "publish",
            "deploy",
            "login",
            "payment",
            "secret_access",
            "two_factor_authentication",
            "external_message",
        ],
        "requiredGateFacts": {
            "analysisGrillPassed": True,
            "planningConfirmed": True,
            "readinessGrillPassed": True,
            "unresolvedDecisionCount": 0,
            "scopeEscalated": False,
            "stateFresh": True,
        },
        "invalidationConditions": ["test fixture invalidated"],
    }


def base_facts(host: str = "codex") -> dict[str, Any]:
    return {
        "host": host,
        "taskId": TEST_TASK_ID,
        "phase": "executionAuthorization",
        "now": "2026-07-17T10:00:00+08:00",
        "planHash": TEST_PLAN_HASH,
        "repo": TEST_REPO,
        "paths": [
            "skills/granoflow-delegated-authorization/SKILL.md",
            "tests/python/test_delegated_authorization.py",
        ],
        "requestedActions": ["local_versioned_code_edit", "local_test"],
        "analysisGrillPassed": True,
        "planningConfirmed": True,
        "readinessGrillPassed": True,
        "unresolvedDecisionCount": 0,
        "scopeEscalated": False,
        "revoked": False,
        "stateFresh": True,
        "receiptVerified": True,
    }


class DelegatedAuthorizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_same_confirmed_scope_is_allowed_for_all_host_fixtures(self) -> None:
        envelope = base_envelope()
        decisions = [
            self.module.evaluate(envelope, base_facts(host))
            for host in ("codex", "cursor", "claude", "opencode")
        ]
        self.assertTrue(all(item["decision"] == "allowed" for item in decisions))
        self.assertEqual({item["reasonCode"] for item in decisions}, {"ok"})
        self.assertEqual(
            {json.dumps(item["evaluatedScope"], sort_keys=True) for item in decisions},
            {json.dumps(decisions[0]["evaluatedScope"], sort_keys=True)},
        )

    def test_expired_revoked_and_stale_receipt_fail_closed(self) -> None:
        cases = [
            ({"now": "2026-07-18T09:00:01+08:00"}, "expired"),
            ({"revoked": True}, "revoked"),
            ({"receiptVerified": False}, "stale_state"),
            ({"stateFresh": False}, "stale_state"),
        ]
        for patch, reason in cases:
            with self.subTest(reason=reason, patch=patch):
                facts = base_facts()
                facts.update(patch)
                result = self.module.evaluate(base_envelope(), facts)
                self.assertEqual(result["decision"], "denied")
                self.assertEqual(result["reasonCode"], reason)

    def test_phase_and_gate_failures_are_stable(self) -> None:
        cases = [
            ({"readinessGrillPassed": False}, "gate_not_passed"),
            ({"unresolvedDecisionCount": 1}, "unresolved_decision"),
            ({"scopeEscalated": True}, "scope_drift"),
        ]
        for patch, reason in cases:
            with self.subTest(reason=reason):
                facts = base_facts()
                facts.update(patch)
                result = self.module.evaluate(base_envelope(), facts)
                self.assertEqual(result["reasonCode"], reason)

        envelope = base_envelope()
        envelope["phaseGrants"]["executionAuthorization"] = False
        result = self.module.evaluate(envelope, base_facts())
        self.assertEqual(result["reasonCode"], "phase_not_granted")

    def test_repo_path_plan_and_actions_must_match(self) -> None:
        cases = [
            ({"repo": "/Users/will/code/unlisted"}, "repo_not_allowed"),
            ({"paths": ["lib/data/drift/database.dart"]}, "path_not_allowed"),
            ({"planHash": "0" * 64}, "scope_drift"),
            ({"requestedActions": ["publish"]}, "forbidden_action"),
            ({"requestedActions": ["invented_action"]}, "unknown_action"),
            ({"requestedActions": ["gf_task_update", "deploy"]}, "forbidden_action"),
        ]
        for patch, reason in cases:
            with self.subTest(reason=reason, patch=patch):
                facts = base_facts()
                facts.update(patch)
                result = self.module.evaluate(base_envelope(), facts)
                self.assertEqual(result["reasonCode"], reason)

    def test_unknown_fields_and_overbroad_globs_are_invalid_schema(self) -> None:
        envelope = base_envelope()
        envelope["agentApproved"] = True
        self.assertEqual(
            self.module.evaluate(envelope, base_facts())["reasonCode"], "invalid_schema"
        )

        envelope = base_envelope()
        envelope["allowedPathGlobs"]["/Users/will/code/granoflow-mcp-server"] = ["**"]
        self.assertEqual(
            self.module.evaluate(envelope, base_facts())["reasonCode"], "invalid_schema"
        )

        facts = base_facts()
        facts["freeTextApproval"] = "yes"
        self.assertEqual(
            self.module.evaluate(base_envelope(), facts)["reasonCode"], "invalid_schema"
        )

    def test_cli_help_dry_run_and_allowed_json(self) -> None:
        help_result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--envelope", help_result.stdout)
        self.assertIn("--facts", help_result.stdout)
        self.assertIn("--now", help_result.stdout)

        dry_run = subprocess.run(
            [sys.executable, str(SCRIPT), "--dry-run"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(dry_run.returncode, 0)
        self.assertEqual(json.loads(dry_run.stdout)["mode"], "dry-run")

        with tempfile.TemporaryDirectory() as directory:
            envelope_path = Path(directory) / "envelope.json"
            facts_path = Path(directory) / "facts.json"
            envelope_path.write_text(json.dumps(base_envelope()), encoding="utf-8")
            facts_path.write_text(json.dumps(base_facts()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--envelope",
                    str(envelope_path),
                    "--facts",
                    str(facts_path),
                    "--now",
                    "2026-07-17T10:00:00+08:00",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["decision"], "allowed")


if __name__ == "__main__":
    unittest.main()
