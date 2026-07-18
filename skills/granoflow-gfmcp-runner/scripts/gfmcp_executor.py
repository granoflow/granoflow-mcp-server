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
The GFMCP tag is eligibility only. Before consuming any delegated phase grant, read the
granoflow-delegated-authorization bundled skill, re-read the owner attachment/hash receipt,
and run validate_delegated_authorization.py with current structured facts. Continue only on
decision=allowed and only for its evaluated scope. On decision=denied or stale/missing state,
apply the waiting-for-user-input contract and write/read back the visible waiting state.
Ask for explicit user authorization before publishing, payment, login, external messages,
destructive changes, secret access, or scope expansion.
If necessary information is missing or execution is truly blocked, write a concise
waiting/blocker note back to this Granoflow task.
Before completion, write and content/hash-readback Task Delivery when the task entered
Plan or execution. Tasks with Plan nodes complete only through NodeService; node-less
compatibility tasks may use one finish call. Record the Delivery Card Checkpoint, but do
not infer approval for card writes or start Deferred Task Review. Do not treat process
exit as completion; require Granoflow API readback to verify status=done.
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
