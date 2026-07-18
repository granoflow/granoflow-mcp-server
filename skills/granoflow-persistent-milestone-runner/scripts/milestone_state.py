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


class StateStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.path = directory / "state.json"
        self.lock_path = directory / "runner.lock"

    def load(self, milestone_id: str) -> dict[str, Any]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(value, dict) and value.get("milestoneId") == milestone_id:
                return value
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return {"version": 1, "milestoneId": milestone_id, "tasks": {}, "attempts": []}

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


def task_available(record: dict[str, Any], fingerprint: str, now: float | None = None) -> bool:
    current = time.time() if now is None else now
    if record.get("taskFingerprint") != fingerprint:
        return True
    if record.get("phase") == "waiting_for_user":
        return False
    return (
        float(record.get("leaseUntil", 0)) <= current
        and float(record.get("nextRetryAt", 0)) <= current
    )


def _lock(stream: TextIO) -> None:
    try:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (ImportError, BlockingIOError) as error:
        if isinstance(error, BlockingIOError):
            raise RunnerAlreadyActive("another milestone runner is active") from error
        import msvcrt

        try:
            cast(Any, msvcrt).locking(stream.fileno(), cast(Any, msvcrt).LK_NBLCK, 1)
        except OSError as lock_error:
            raise RunnerAlreadyActive("another milestone runner is active") from lock_error


def _unlock(stream: TextIO) -> None:
    try:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    except ImportError:
        import msvcrt

        with suppress(OSError):
            cast(Any, msvcrt).locking(stream.fileno(), cast(Any, msvcrt).LK_UNLCK, 1)
