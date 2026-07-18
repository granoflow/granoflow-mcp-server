from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-gfmcp-runner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from gfmcp_api import GranoflowApiError  # noqa: E402
from gfmcp_executor import ExecutorResult, build_prompt  # noqa: E402
from gfmcp_runner import (  # noqa: E402
    DEFAULT_INTERVAL_SECONDS,
    main,
    run_cycle,
    should_poll_immediately,
)
from gfmcp_state import EVENT_LIMIT, StateStore, lease_available  # noqa: E402


class FakeApi:
    def __init__(self, task: dict[str, Any] | None = None) -> None:
        self.current = task
        self.calls: list[str] = []

    def health(self) -> dict[str, Any]:
        self.calls.append("health")
        return {}

    def prepare(self) -> dict[str, Any]:
        self.calls.append("prepare")
        return {}

    def safe_sync(self) -> dict[str, Any]:
        self.calls.append("safe_sync")
        return {}

    def candidates(self) -> list[dict[str, Any]]:
        self.calls.append("candidates")
        return [self.current] if self.current else []

    def task(self, task_id: str) -> dict[str, Any] | None:
        del task_id
        return self.current

    def update_description(self, task_id: str, description: str) -> None:
        del task_id
        assert self.current is not None
        self.current["description"] = description
        self.calls.append("update_description")


class SyncFailureApi(FakeApi):
    def safe_sync(self) -> dict[str, Any]:
        self.calls.append("safe_sync")
        raise GranoflowApiError("sanitized")


class GfmcpRunnerTest(unittest.TestCase):
    def test_default_interval_is_five_minutes(self) -> None:
        self.assertEqual(DEFAULT_INTERVAL_SECONDS, 300)

    def test_dry_run_does_not_prepare_sync_or_execute(self) -> None:
        api = FakeApi({"id": "task-1", "title": "T", "status": "pending"})
        with tempfile.TemporaryDirectory() as directory:
            status = run_cycle(api, StateStore(Path(directory)), Path(directory), "codex", 30, True)
        self.assertEqual(status, "candidate_ready")
        self.assertEqual(api.calls, ["health", "candidates"])

    def test_done_requires_api_readback(self) -> None:
        task = {"id": "task-1", "title": "T", "status": "pending"}
        api = FakeApi(task)

        def complete(*_args: object) -> ExecutorResult:
            task["status"] = "done"
            return ExecutorResult(0)

        with (
            tempfile.TemporaryDirectory() as directory,
            patch("gfmcp_runner.execute", side_effect=complete),
        ):
            status = run_cycle(
                api, StateStore(Path(directory)), Path(directory), "codex", 30, False
            )
            runtime = StateStore(Path(directory)).load()["runtime"]
        self.assertEqual(status, "task_completed")
        self.assertEqual(api.calls[:4], ["health", "prepare", "safe_sync", "candidates"])
        self.assertEqual(runtime["phase"], "verifying")
        self.assertEqual(runtime["currentTaskId"], "task-1")

    def test_only_completed_task_triggers_immediate_recheck(self) -> None:
        self.assertTrue(should_poll_immediately("task_completed"))
        self.assertFalse(should_poll_immediately("no_candidates"))
        self.assertFalse(should_poll_immediately("task_still_pending"))

    def test_runtime_events_are_bounded_and_contain_no_task_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory))
            for index in range(EVENT_LIMIT + 5):
                store.update_runtime("polling", status=f"poll_{index}", task_id="task-1")
            state = store.load()
            self.assertEqual(len(state["events"]), EVENT_LIMIT)
            serialized = str(state)
            self.assertNotIn("description", serialized)
            self.assertNotIn("executor prompt", serialized)

    def test_status_reports_stopped_when_lock_is_not_owned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory))
            store.update_runtime("waiting", status="no_candidates")
            status = store.status()
            self.assertFalse(status["active"])
            self.assertEqual(status["phase"], "stopped")
            self.assertEqual(status["lastKnownPhase"], "waiting")

    def test_interruptible_wait_stops_immediately_after_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory))
            store.directory.mkdir(parents=True, exist_ok=True)
            store.stop_path.write_text("stop\n", encoding="utf-8")
            self.assertFalse(store.interruptible_wait(300))

    def test_status_cli_never_calls_local_api(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch("gfmcp_runner.GranoflowApi") as api:
                result = main(["--status", "--state-dir", directory])
            self.assertEqual(result, 0)
            api.assert_not_called()

    def test_main_rechecks_immediately_after_completion(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            patch("gfmcp_runner.GranoflowApi"),
            patch(
                "gfmcp_runner.run_cycle",
                side_effect=["task_completed", "no_candidates"],
            ) as cycle,
            patch.object(StateStore, "interruptible_wait", return_value=False),
        ):
            result = main(["--state-dir", directory, "--interval-seconds", "300"])
        self.assertEqual(result, 0)
        self.assertEqual(cycle.call_count, 2)

    def test_sync_failure_degrades_to_local_queue(self) -> None:
        task = {"id": "task-1", "title": "T", "status": "pending"}
        api = SyncFailureApi(task)
        with (
            tempfile.TemporaryDirectory() as directory,
            patch("gfmcp_runner.execute", return_value=ExecutorResult(0)),
        ):
            store = StateStore(Path(directory))
            status = run_cycle(api, store, Path(directory), "codex", 30, False)
            self.assertEqual(status, "task_still_pending")
            self.assertEqual(store.load()["lastSyncVisibility"], "unknown_remote_visibility")

    def test_three_same_failures_write_sanitized_blocker(self) -> None:
        task = {"id": "task-1", "title": "T", "description": "D", "status": "pending"}
        api = FakeApi(task)
        with (
            tempfile.TemporaryDirectory() as directory,
            patch("gfmcp_runner.execute", return_value=ExecutorResult(0)),
        ):
            store = StateStore(Path(directory))
            for _ in range(3):
                status = run_cycle(api, store, Path(directory), "codex", 30, False)
                self.assertEqual(status, "task_still_pending")
                state = store.load()
                state["tasks"]["task-1"]["nextRetryAt"] = 0
                state["tasks"]["task-1"]["leaseUntil"] = 0
                store.save(state)
            self.assertIn("已连续 3 次未完成", str(task["description"]))
            self.assertTrue(store.load()["tasks"]["task-1"]["blocked"])

    def test_task_change_releases_block(self) -> None:
        self.assertFalse(
            lease_available(
                {"taskFingerprint": "same", "blocked": True, "leaseUntil": 0}, "same", 10
            )
        )
        self.assertTrue(
            lease_available(
                {"taskFingerprint": "old", "blocked": True, "leaseUntil": 999}, "new", 10
            )
        )

    def test_executor_prompt_preserves_authorization_boundary(self) -> None:
        prompt = build_prompt("task-1")
        self.assertIn("explicit user authorization", prompt)
        self.assertIn("Granoflow API readback", prompt)
        self.assertIn("content/hash-readback Task Delivery", prompt)
        self.assertIn("Plan nodes complete only through NodeService", prompt)
        self.assertIn("Deferred Task Review", prompt)
        self.assertIn("Delivery Card Checkpoint", prompt)
        self.assertIn("not infer approval", prompt)
        self.assertIn("granoflow-delegated-authorization", prompt)
        self.assertIn("validate_delegated_authorization.py", prompt)
        self.assertIn("decision=allowed", prompt)
        self.assertIn("GFMCP tag is eligibility only", prompt)
        self.assertIn("decision=denied", prompt)
        self.assertIn("waiting-for-user-input", prompt)


if __name__ == "__main__":
    unittest.main()
