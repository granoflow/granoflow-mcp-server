from __future__ import annotations

import json
import os
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Any, TextIO, cast


class RunnerAlreadyActive(RuntimeError):
    pass


EVENT_LIMIT = 50


class StateStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.path = directory / "state.json"
        self.lock_path = directory / "runner.lock"
        self.stop_path = directory / "stop-request"

    def load(self) -> dict[str, Any]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                value.setdefault("version", 2)
                value.setdefault("tasks", {})
                value.setdefault("runtime", {})
                value.setdefault("events", [])
                return value
            return self._empty_state()
        except (FileNotFoundError, json.JSONDecodeError):
            return self._empty_state()

    @staticmethod
    def _empty_state() -> dict[str, Any]:
        return {"version": 2, "tasks": {}, "runtime": {}, "events": []}

    def save(self, state: dict[str, Any]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor, temp_path = tempfile.mkstemp(
            prefix="state-", suffix=".json", dir=self.directory
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(state, stream, indent=2, sort_keys=True)
                stream.write("\n")
            os.replace(temp_path, self.path)
            os.chmod(self.path, 0o600)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def update_runtime(
        self,
        phase: str,
        *,
        status: str | None = None,
        task_id: str | None = None,
        lease_until: float | None = None,
        last_check_at: str | None = None,
        next_check_at: str | None = None,
        pid: int | None = None,
        event: bool = True,
        record_result: bool = True,
    ) -> dict[str, Any]:
        state = self.load()
        runtime = state.setdefault("runtime", {})
        now = utc_timestamp()
        runtime.update(
            {
                "phase": phase,
                "heartbeatAt": now,
                "currentTaskId": task_id,
                "leaseUntil": timestamp_from_epoch(lease_until),
                "nextCheckAt": next_check_at,
            }
        )
        if status is not None and record_result:
            runtime["lastResult"] = status
        if last_check_at is not None:
            runtime["lastCheckAt"] = last_check_at
        if pid is not None:
            runtime["pid"] = pid
            runtime.setdefault("startedAt", now)
        if event:
            events = state.setdefault("events", [])
            entry: dict[str, Any] = {"at": now, "phase": phase}
            if status is not None:
                entry["status"] = status
            if task_id is not None:
                entry["taskId"] = task_id
            events.append(entry)
            state["events"] = events[-EVENT_LIMIT:]
        self.save(state)
        return state

    def runner_active(self) -> bool:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        stream = self.lock_path.open("a+", encoding="utf-8")
        try:
            _lock(stream)
        except RunnerAlreadyActive:
            stream.close()
            return True
        _unlock(stream)
        stream.close()
        return False

    def status(self) -> dict[str, Any]:
        state = self.load()
        runtime = dict(state.get("runtime", {}))
        active = self.runner_active()
        last_known_phase = str(runtime.get("phase") or "stopped")
        return {
            "active": active,
            "phase": last_known_phase if active else "stopped",
            "lastKnownPhase": last_known_phase,
            "pid": runtime.get("pid"),
            "startedAt": runtime.get("startedAt"),
            "heartbeatAt": runtime.get("heartbeatAt"),
            "lastCheckAt": runtime.get("lastCheckAt"),
            "nextCheckAt": runtime.get("nextCheckAt"),
            "currentTaskId": runtime.get("currentTaskId"),
            "leaseUntil": runtime.get("leaseUntil"),
            "lastResult": runtime.get("lastResult"),
            "events": state.get("events", [])[-EVENT_LIMIT:],
        }

    def request_stop(self) -> bool:
        if not self.runner_active():
            return False
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.stop_path.write_text(utc_timestamp() + "\n", encoding="utf-8")
        os.chmod(self.stop_path, 0o600)
        self.update_runtime(
            "stop_requested",
            status="stop_requested",
            next_check_at=None,
        )
        return True

    def stop_requested(self) -> bool:
        return self.stop_path.exists()

    def clear_stop_request(self) -> None:
        with suppress(FileNotFoundError):
            self.stop_path.unlink()

    def interruptible_wait(self, seconds: int, poll_seconds: float = 1.0) -> bool:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if self.stop_requested():
                return False
            time.sleep(min(poll_seconds, max(0.0, deadline - time.monotonic())))
        return not self.stop_requested()

    @contextmanager
    def process_lock(self) -> Iterator[None]:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        stream = self.lock_path.open("a+", encoding="utf-8")
        try:
            _lock(stream)
            yield
        finally:
            _unlock(stream)
            stream.close()


def _lock(stream: TextIO) -> None:
    try:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (ImportError, BlockingIOError) as error:
        if isinstance(error, BlockingIOError):
            raise RunnerAlreadyActive("another GFMCP runner is active") from error
        import msvcrt

        try:
            windows_lock = cast(Any, msvcrt)
            windows_lock.locking(stream.fileno(), windows_lock.LK_NBLCK, 1)
        except OSError as lock_error:
            raise RunnerAlreadyActive("another GFMCP runner is active") from lock_error


def _unlock(stream: TextIO) -> None:
    try:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    except ImportError:
        import msvcrt

        with suppress(OSError):
            windows_lock = cast(Any, msvcrt)
            windows_lock.locking(stream.fileno(), windows_lock.LK_UNLCK, 1)


def lease_available(
    record: dict[str, Any], task_fingerprint: str, now: float | None = None
) -> bool:
    current = time.time() if now is None else now
    if record.get("taskFingerprint") != task_fingerprint:
        return True
    if record.get("blocked") is True:
        return False
    return (
        float(record.get("leaseUntil", 0)) <= current
        and float(record.get("nextRetryAt", 0)) <= current
    )


def utc_timestamp(epoch: float | None = None) -> str:
    value = time.time() if epoch is None else epoch
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(value))


def timestamp_from_epoch(epoch: float | None) -> str | None:
    return utc_timestamp(epoch) if epoch is not None and epoch > 0 else None
