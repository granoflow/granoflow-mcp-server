from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-persistent-milestone-runner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import milestone_runner as runner  # noqa: E402
from milestone_state import StateStore, task_available  # noqa: E402
from milestone_worker import WorkerReport, WorkerResult, build_prompt, load_report  # noqa: E402
from node_relay import (  # noqa: E402
    ContractVersion,
    ExecutionMode,
    NodeLane,
    eligible_node,
    parse_node_title,
    skippable_confirmations,
)


class FakeApi:
    def __init__(self, tasks: list[dict[str, Any]]) -> None:
        self.task_values = {str(task["id"]): dict(task) for task in tasks}
        self.attachment_values: dict[str, list[dict[str, Any]]] = {}
        self.attachment_readbacks: dict[tuple[str, str], dict[str, Any]] = {}
        self.node_values: dict[str, list[dict[str, Any]]] = {}

    def health(self) -> dict[str, Any]:
        return {"ok": True}

    def tasks(self, milestone_id: str) -> list[dict[str, Any]]:
        del milestone_id
        return [dict(task) for task in self.task_values.values()]

    def task(self, task_id: str) -> dict[str, Any] | None:
        task = self.task_values.get(task_id)
        return dict(task) if task else None

    def attachments(self, task_id: str) -> list[dict[str, Any]]:
        return self.attachment_values.get(task_id, [])

    def attachment(self, task_id: str, attachment_id: str) -> dict[str, Any]:
        return self.attachment_readbacks[(task_id, attachment_id)]

    def nodes(self, task_id: str) -> list[dict[str, Any]]:
        return self.node_values.get(task_id, [])

    def update_description(self, task_id: str, description: str) -> None:
        self.task_values[task_id]["description"] = description
        self.task_values[task_id]["updatedAt"] = f"revision-{len(description)}"

    def update_node(self, task_id: str, node_id: str, updated_at: str, status: str) -> None:
        del updated_at
        for node in self.node_values.get(task_id, []):
            if node.get("id") == node_id:
                node["status"] = status
                return


def authorization(milestone_id: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "schema": "granoflow_milestone_authorization_v1",
        "status": "confirmed",
        "milestoneId": milestone_id,
        "issuedAt": now.isoformat(),
        "expiresAt": (now + timedelta(hours=4)).isoformat(),
        "runtimeAccess": {"required": "full", "observed": "full"},
        "autoConfirmInternalGates": True,
        "requiredExternalCapabilities": ["publish"],
        "externalCapabilities": {
            "publish": {
                "disposition": "interaction_required",
                "taskIds": ["task-1"],
                "credentialRef": None,
            }
        },
        "secretPolicy": {"referenceOnly": True, "persistValues": False},
    }


class PersistentMilestoneRunnerTests(unittest.TestCase):
    def test_batch_v2_exposes_new_lanes_and_rejects_legacy_confirm(self) -> None:
        analysis = parse_node_title("[analysis] 分析", ContractVersion.BATCH_V2)
        integration = parse_node_title("[integration] 截图验收", ContractVersion.BATCH_V2)
        user = parse_node_title("[user] 最终确认", ContractVersion.BATCH_V2)
        assert analysis is not None
        assert integration is not None
        assert user is not None
        self.assertEqual(analysis.lane, NodeLane.ANALYSIS)
        self.assertEqual(integration.lane, NodeLane.INTEGRATION)
        self.assertEqual(user.lane, NodeLane.USER)
        self.assertIsNone(parse_node_title("[confirm] 旧确认", ContractVersion.BATCH_V2))
        self.assertIsNone(parse_node_title("[integration] 旧集成", ContractVersion.LEGACY_V1))

    def test_batch_v2_never_skips_user_or_claims_action(self) -> None:
        nodes = [
            {"id": "dev", "title": "[dev] 实现", "status": "finished"},
            {"id": "test", "title": "[test] 普通测试", "status": "finished"},
            {"id": "user", "title": "[user] 用户确认", "status": "pending"},
            {"id": "action", "title": "[action] 外部动作", "status": "pending"},
        ]
        self.assertIsNone(
            eligible_node(
                nodes,
                ExecutionMode.UNATTENDED,
                {NodeLane.USER},
                ContractVersion.BATCH_V2,
            )
        )
        self.assertEqual(
            skippable_confirmations(nodes, ContractVersion.BATCH_V2),
            [],
        )

    def test_node_prefixes_route_by_capability_not_model_name(self) -> None:
        dev = parse_node_title("[dev] 实现服务")
        test = parse_node_title("[test] 运行验收")
        self.assertIsNotNone(dev)
        self.assertIsNotNone(test)
        assert dev is not None and test is not None
        self.assertEqual(dev.lane, NodeLane.DEV)
        self.assertEqual(test.label, "运行验收")
        self.assertIsNone(parse_node_title("实现服务"))

    def test_layered_handoff_selects_first_lane_node_after_prior_nodes_finish(self) -> None:
        nodes = [
            {"id": "plan", "title": "[plan] 冻结契约", "status": "finished"},
            {"id": "dev", "title": "[dev] 实现", "status": "pending"},
            {"id": "test", "title": "[test] 运行集成测试", "status": "pending"},
        ]
        selected = eligible_node(nodes, ExecutionMode.LAYERED_HANDOFF, {NodeLane.DEV})
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["id"], "dev")
        self.assertIsNone(eligible_node(nodes, ExecutionMode.LAYERED_HANDOFF, {NodeLane.TEST}))

    def test_unattended_treats_confirmation_as_skipped_but_never_claims_action(self) -> None:
        nodes = [
            {"id": "dev", "title": "[dev] 实现", "status": "finished"},
            {"id": "confirm", "title": "[confirm] 人工确认", "status": "pending"},
            {"id": "test", "title": "[test] 编排验收脚本", "status": "pending"},
            {"id": "action", "title": "[action] 发布", "status": "pending"},
        ]
        selected = eligible_node(nodes, ExecutionMode.UNATTENDED, {NodeLane.TEST})
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["id"], "test")
        nodes[2]["status"] = "finished"
        self.assertIsNone(eligible_node(nodes, ExecutionMode.UNATTENDED, set(NodeLane)))

    def test_only_leading_pending_confirmations_are_safe_to_auto_finish(self) -> None:
        nodes = [
            {"id": "plan", "title": "[plan] 计划", "status": "finished"},
            {"id": "confirm", "title": "[confirm] 确认计划", "status": "pending"},
            {"id": "dev", "title": "[dev] 实现", "status": "pending"},
            {"id": "later", "title": "[confirm] 验收", "status": "pending"},
        ]
        self.assertEqual([node["id"] for node in skippable_confirmations(nodes)], ["confirm"])

    def test_authorization_requires_full_access_and_complete_external_matrix(self) -> None:
        value = authorization("mile-1")
        self.assertEqual(runner.validate_authorization(value, "mile-1"), "ok")

        value["runtimeAccess"]["observed"] = "workspace"
        self.assertEqual(
            runner.validate_authorization(value, "mile-1"),
            "runtime_full_access_required",
        )
        value = authorization("mile-1")
        value["externalCapabilities"] = {}
        self.assertEqual(
            runner.validate_authorization(value, "mile-1"),
            "external_capability_matrix_incomplete",
        )

    def test_granted_external_capability_requires_only_a_reference(self) -> None:
        value = authorization("mile-1")
        value["externalCapabilities"]["publish"] = {
            "disposition": "granted",
            "taskIds": ["task-1"],
            "credentialRef": None,
        }
        self.assertEqual(
            runner.validate_authorization(value, "mile-1"),
            "external_credential_reference_required",
        )
        value["externalCapabilities"]["publish"]["credentialRef"] = "os-keychain:publish"
        self.assertEqual(runner.validate_authorization(value, "mile-1"), "ok")

    def test_completion_requires_accepted_delivery_matching_hash_and_finished_nodes(self) -> None:
        task = {"id": "task-1", "status": "done", "title": "Task"}
        api = FakeApi([task])
        content = "document_type: task_delivery\nacceptance_status_as_of: accepted\n"
        api.attachment_values["task-1"] = [
            {"id": "delivery-1", "displayName": "task-delivery-task-1-v1.md"}
        ]
        api.attachment_readbacks[("task-1", "delivery-1")] = {
            "content": content,
            "contentSha256": hashlib.sha256(content.encode()).hexdigest(),
        }
        api.node_values["task-1"] = [{"status": "finished"}]
        self.assertEqual(runner.completion_evidence(api, task), (True, "accepted"))

        api.attachment_readbacks[("task-1", "delivery-1")]["contentSha256"] = "0" * 64
        self.assertEqual(
            runner.completion_evidence(api, task),
            (False, "task_delivery_hash_mismatch"),
        )

    def test_worker_summary_never_bypasses_completion_gate(self) -> None:
        task = {"id": "task-1", "status": "pending", "title": "Task", "updatedAt": "1"}
        api = FakeApi([task])
        result = WorkerResult(0, False, WorkerReport("complete", "claimed", True, None))
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory))
            state = store.load("mile-1")
            state["tasks"]["task-1"] = {
                "taskFingerprint": runner.task_fingerprint(task),
                "phase": "running",
            }
            self.assertEqual(
                runner.record_outcome(api, store, state, task, result, "task_still_pending"),
                "retry_wait",
            )
            self.assertEqual(store.load("mile-1")["tasks"]["task-1"]["stagnationCount"], 1)

    def test_stagnation_replans_then_waits_and_task_change_resumes(self) -> None:
        task = {
            "id": "task-1",
            "status": "pending",
            "title": "Task",
            "description": "work",
            "updatedAt": "1",
        }
        api = FakeApi([task])
        result = WorkerResult(1, False, None)
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory))
            state = store.load("mile-1")
            state["tasks"]["task-1"] = {
                "taskFingerprint": runner.task_fingerprint(task),
                "phase": "running",
            }
            phases = []
            current = task
            for _ in range(4):
                phases.append(runner.record_outcome(api, store, state, current, result, "exit"))
                current = api.task("task-1") or current
            self.assertEqual(
                phases, ["retry_wait", "retry_wait", "replan_required", "waiting_for_user"]
            )
            record = state["tasks"]["task-1"]
            self.assertFalse(task_available(record, runner.task_fingerprint(current), now=10**12))
            changed = dict(current, title="Task with user input")
            self.assertTrue(task_available(record, runner.task_fingerprint(changed), now=10**12))

    def test_attempt_history_is_bounded(self) -> None:
        task = {"id": "task-1", "status": "pending", "title": "Task", "updatedAt": "1"}
        api = FakeApi([task])
        result = WorkerResult(1, False, None)
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory))
            state = store.load("mile-1")
            state["tasks"]["task-1"] = {
                "taskFingerprint": runner.task_fingerprint(task),
                "phase": "running",
            }
            for _ in range(130):
                runner.record_outcome(api, store, state, task, result, "same")
            self.assertEqual(len(state["attempts"]), runner.ATTEMPT_LIMIT)

    def test_authorization_change_releases_wait_and_other_task_can_run(self) -> None:
        blocked = {"id": "task-1", "status": "pending", "title": "Blocked", "updatedAt": "1"}
        ready = {"id": "task-2", "status": "pending", "title": "Ready", "updatedAt": "1"}
        api = FakeApi([blocked, ready])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = StateStore(root / "state")
            state = store.load("mile-1")
            state["authorizationFingerprint"] = "old"
            state["tasks"]["task-1"] = {
                "taskFingerprint": runner.task_fingerprint(blocked),
                "phase": "waiting_for_user",
                "nextRetryAt": 10**12,
            }
            store.save(state)
            auth_path = root / "auth.json"
            auth_path.write_text(json.dumps(authorization("mile-1")), encoding="utf-8")
            seen: list[str] = []

            def fake_worker(
                _milestone_id: str,
                task_id: str,
                *_args: Any,
                **_kwargs: Any,
            ) -> WorkerResult:
                seen.append(task_id)
                return WorkerResult(1, False, None)

            with patch.object(runner, "execute_worker", side_effect=fake_worker):
                runner.run_cycle(api, store, "mile-1", root, "worker", auth_path, 2, 1, False)
            self.assertEqual(seen, ["task-1"])

            waiting = store.load("mile-1")
            waiting["tasks"]["task-1"]["phase"] = "waiting_for_user"
            waiting["tasks"]["task-1"]["nextRetryAt"] = 10**12
            waiting["authorizationFingerprint"] = hashlib.sha256(auth_path.read_bytes()).hexdigest()
            store.save(waiting)
            seen.clear()
            with patch.object(runner, "execute_worker", side_effect=fake_worker):
                runner.run_cycle(api, store, "mile-1", root, "worker", auth_path, 2, 1, False)
            self.assertEqual(seen, ["task-2"])

    def test_unattended_cycle_finishes_confirmation_and_assigns_dev_node(self) -> None:
        task = {
            "id": "task-1",
            "status": "pending",
            "title": "Relay",
            "updatedAt": "2026-07-18T10:00:00+00:00",
        }
        api = FakeApi([task])
        api.node_values["task-1"] = [
            {
                "id": "confirm-1",
                "title": "[confirm] 确认计划",
                "status": "pending",
                "updatedAt": "2026-07-18T10:00:00+00:00",
            },
            {
                "id": "dev-1",
                "title": "[dev] 实现",
                "status": "pending",
                "updatedAt": "2026-07-18T10:00:01+00:00",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = StateStore(root / "state")
            auth_path = root / "auth.json"
            auth_path.write_text(json.dumps(authorization("mile-1")), encoding="utf-8")
            assignment: dict[str, Any] = {}

            def fake_worker(
                _milestone_id: str,
                task_id: str,
                *_args: Any,
                **kwargs: Any,
            ) -> WorkerResult:
                assignment.update(kwargs)
                api.update_node(task_id, "dev-1", "revision", "finished")
                return WorkerResult(0, False, None)

            with patch.object(runner, "execute_worker", side_effect=fake_worker):
                status = runner.run_cycle(
                    api,
                    store,
                    "mile-1",
                    root,
                    "worker",
                    auth_path,
                    2,
                    1,
                    False,
                    ExecutionMode.UNATTENDED,
                    {NodeLane.DEV},
                )

            self.assertEqual(api.node_values["task-1"][0]["status"], "finished")
            self.assertEqual(assignment["execution_mode"], "unattended")
            self.assertEqual(assignment["lane"], "dev")
            self.assertEqual(assignment["node_id"], "dev-1")
            self.assertEqual(status, "task_accepted")

    def test_worker_report_is_strict_and_public_prompt_is_provider_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": "granoflow_worker_report_v1",
                        "disposition": "continue",
                        "attemptFingerprint": "strategy-a",
                        "newEvidence": False,
                        "checkpointRef": None,
                    }
                ),
                encoding="utf-8",
            )
            self.assertIsNotNone(load_report(path))
            value = json.loads(path.read_text())
            value["secret"] = "forbidden"
            path.write_text(json.dumps(value), encoding="utf-8")
            self.assertIsNone(load_report(path))

        prompt = build_prompt("mile-1", "task-1", "execute").lower()
        for forbidden in ("luna", "terra", " sol "):
            self.assertNotIn(forbidden, prompt)


if __name__ == "__main__":
    unittest.main()
