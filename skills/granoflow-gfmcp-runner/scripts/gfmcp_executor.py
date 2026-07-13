from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutorResult:
    exit_code: int
    timed_out: bool = False


def build_prompt(task_id: str) -> str:
    return f"""Execute Granoflow task {task_id} using the granoflow-task-runner skill.
Analyze and classify it before acting. Safe, reversible local workspace work is allowed.
Ask for explicit user authorization before publishing, payment, login, external messages,
destructive changes, secret access, or scope expansion.
If necessary information is missing or execution is truly blocked, write a concise
waiting/blocker note back to this Granoflow task.
Use the existing completion and review-card workflow; review cards require user confirmation.
Do not treat process exit as completion. Finish only through Granoflow and require API
readback to verify status=done.
"""


def execute(task_id: str, workspace: Path, command: str, timeout_seconds: int) -> ExecutorResult:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("executor command must not be empty")
    if argv[0] == "codex" and len(argv) == 1:
        argv.extend(["exec", "-C", str(workspace), "-s", "workspace-write", "-a", "never"])
    argv.append(build_prompt(task_id))
    try:
        completed = subprocess.run(
            argv,
            cwd=workspace,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_seconds,
            check=False,
        )
        return ExecutorResult(completed.returncode)
    except subprocess.TimeoutExpired:
        return ExecutorResult(124, timed_out=True)
