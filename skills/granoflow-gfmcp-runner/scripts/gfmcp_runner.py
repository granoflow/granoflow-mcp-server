#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Protocol

from gfmcp_api import GranoflowApi, GranoflowApiError
from gfmcp_executor import execute
from gfmcp_state import RunnerAlreadyActive, StateStore, lease_available

DEFAULT_INTERVAL_SECONDS = 300
BLOCK_MARKER = "\n\n---\nGFMCP 自动执行状态："


class RunnerApi(Protocol):
    def health(self) -> dict[str, Any]: ...

    def prepare(self) -> dict[str, Any]: ...

    def safe_sync(self) -> dict[str, Any]: ...

    def candidates(self) -> list[dict[str, Any]]: ...

    def task(self, task_id: str) -> dict[str, Any] | None: ...

    def update_description(self, task_id: str, description: str) -> None: ...


def task_fingerprint(task: dict[str, Any]) -> str:
    safe = {key: task.get(key) for key in ("id", "title", "description", "status", "tagSlugs")}
    return hashlib.sha256(
        json.dumps(safe, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def record_failure(
    api: RunnerApi, store: StateStore, state: dict[str, Any], task: dict[str, Any], reason: str
) -> None:
    task_id = str(task["id"])
    tasks = state.setdefault("tasks", {})
    previous = tasks.get(task_id, {}) if isinstance(tasks, dict) else {}
    fingerprint = task_fingerprint(task)
    count = (
        int(previous.get("failureCount", 0)) + 1
        if previous.get("reason") == reason and previous.get("taskFingerprint") == fingerprint
        else 1
    )
    blocked = count >= 3
    next_retry = time.time() + min(3600, 300 * (2 ** (count - 1)))
    tasks[task_id] = {
        "taskFingerprint": fingerprint,
        "reason": reason,
        "failureCount": count,
        "nextRetryAt": next_retry,
        "leaseUntil": 0,
        "blocked": blocked,
    }
    store.save(state)
    if blocked:
        current = api.task(task_id) or task
        description = str(current.get("description") or "").split(BLOCK_MARKER, 1)[0]
        note = (
            f"{BLOCK_MARKER} 已连续 {count} 次未完成（{reason}）。请补充信息或修改任务后自动重试。"
        )
        api.update_description(task_id, description + note)
        updated = api.task(task_id)
        if updated:
            tasks[task_id]["taskFingerprint"] = task_fingerprint(updated)
            store.save(state)


def run_cycle(
    api: RunnerApi,
    store: StateStore,
    workspace: Path,
    executor_command: str,
    timeout_seconds: int,
    dry_run: bool,
) -> str:
    api.health()
    state = store.load()
    if not dry_run:
        api.prepare()
        try:
            sync_result = api.safe_sync()
            sync_data = sync_result.get("data")
            visibility = sync_data.get("visibility") if isinstance(sync_data, dict) else None
            state["lastSyncVisibility"] = visibility or "unknown_remote_visibility"
        except GranoflowApiError:
            state["lastSyncVisibility"] = "unknown_remote_visibility"
        store.save(state)
    candidates = api.candidates()
    if not candidates:
        return "no_candidates"
    tasks_state = state.setdefault("tasks", {})
    for task in candidates:
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            continue
        fingerprint = task_fingerprint(task)
        record = tasks_state.get(task_id, {}) if isinstance(tasks_state, dict) else {}
        if not lease_available(record, fingerprint):
            continue
        if dry_run:
            return "candidate_ready"
        tasks_state[task_id] = {
            **record,
            "taskFingerprint": fingerprint,
            "leaseUntil": time.time() + timeout_seconds + 60,
        }
        store.save(state)
        result = execute(task_id, workspace, executor_command, timeout_seconds)
        readback = api.task(task_id)
        if readback and readback.get("status") == "done":
            tasks_state.pop(task_id, None)
            store.save(state)
            return "task_completed"
        reason = (
            "executor_timeout"
            if result.timed_out
            else f"executor_exit_{result.exit_code}"
            if result.exit_code
            else "task_still_pending"
        )
        record_failure(api, store, state, readback or task, reason)
        return reason
    return "no_eligible_candidates"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Poll and safely execute GFMCP-tagged Granoflow tasks."
    )
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    parser.add_argument(
        "--state-dir", type=Path, default=Path.home() / ".local" / "state" / "granoflow-gfmcp"
    )
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--executor-command", default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=2700)
    args = parser.parse_args(argv)
    if args.interval_seconds < 1 or args.timeout_seconds < 1:
        parser.error("interval and timeout must be positive")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    store = StateStore(args.state_dir)
    api = GranoflowApi()
    try:
        with store.process_lock():
            while True:
                try:
                    status = run_cycle(
                        api,
                        store,
                        args.workspace.resolve(),
                        args.executor_command,
                        args.timeout_seconds,
                        args.dry_run,
                    )
                    print(json.dumps({"ok": True, "status": status}))
                except GranoflowApiError:
                    print(
                        json.dumps({"ok": False, "status": "local_api_unavailable"}),
                        file=sys.stderr,
                    )
                    if args.once:
                        return 1
                if args.once:
                    return 0
                time.sleep(args.interval_seconds)
    except RunnerAlreadyActive:
        print(json.dumps({"ok": False, "status": "runner_already_active"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
