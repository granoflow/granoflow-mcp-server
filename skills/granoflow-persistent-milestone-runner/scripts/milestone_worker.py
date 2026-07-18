from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

REPORT_SCHEMA = "granoflow_worker_report_v1"
DISPOSITIONS = {
    "continue",
    "retry_wait",
    "replan_required",
    "waiting_for_permission",
    "waiting_for_user",
    "blocked",
    "complete",
}


@dataclass(frozen=True)
class WorkerReport:
    disposition: str
    attempt_fingerprint: str
    new_evidence: bool
    checkpoint_ref: str | None = None


@dataclass(frozen=True)
class WorkerResult:
    exit_code: int
    timed_out: bool
    report: WorkerReport | None


def build_prompt(
    milestone_id: str,
    task_id: str,
    mode: str,
    *,
    execution_mode: str = "interactive",
    lane: str | None = None,
    node_id: str | None = None,
    node_title: str | None = None,
) -> str:
    assignment = (
        f"Assigned node is {node_id}: {node_title}. Responsible lane is [{lane}].\n"
        if node_id and lane and node_title
        else "No explicit node lane was assigned; use the normal interactive Task Work flow.\n"
    )
    return f"""Continue Granoflow milestone {milestone_id}, task {task_id}.
Load the Granoflow milestone, agent-workflow, delegated-authorization,
and persistent-runner contracts.
Thread execution mode is {execution_mode}; runner attempt mode is {mode}.
{assignment}Re-read the current task, attachments, nodes, and authorization manifest.
Report the thread execution mode before work. Do not claim to know the current
model or reasoning tier; routing comes from the user or host configuration.
Do not treat a final response, summary, process exit, or self-reported completion
as task completion. Continue all safe independent work, verify actual acceptance
evidence, and write Task Delivery before completion. If prior attempts stagnated,
diagnose attempted strategy classes and choose a materially different
evidence-backed path. When user input or external permission is required,
preserve a resumable interaction node and checkpoint.
Do not invoke a specific provider or model unless a separate user Skill supplied that routing.
Optionally write the strict provider-neutral report to GRANOFLOW_MILESTONE_REPORT_PATH.
"""


def load_report(path: Path) -> WorkerReport | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict) or set(value) != {
        "schema",
        "disposition",
        "attemptFingerprint",
        "newEvidence",
        "checkpointRef",
    }:
        return None
    if value["schema"] != REPORT_SCHEMA or value["disposition"] not in DISPOSITIONS:
        return None
    fingerprint = value["attemptFingerprint"]
    checkpoint = value["checkpointRef"]
    if not isinstance(fingerprint, str) or not fingerprint or len(fingerprint) > 160:
        return None
    if not isinstance(value["newEvidence"], bool):
        return None
    if checkpoint is not None and (not isinstance(checkpoint, str) or len(checkpoint) > 200):
        return None
    return WorkerReport(value["disposition"], fingerprint, value["newEvidence"], checkpoint)


def execute_worker(
    milestone_id: str,
    task_id: str,
    mode: str,
    workspace: Path,
    command: str,
    report_path: Path,
    authorization_path: Path,
    timeout_seconds: int,
    heartbeat_seconds: int,
    heartbeat: Callable[[], None],
    execution_mode: str = "interactive",
    lane: str | None = None,
    node_id: str | None = None,
    node_title: str | None = None,
) -> WorkerResult:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("worker command must not be empty")
    argv.append(
        build_prompt(
            milestone_id,
            task_id,
            mode,
            execution_mode=execution_mode,
            lane=lane,
            node_id=node_id,
            node_title=node_title,
        )
    )
    env = os.environ.copy()
    env.update(
        {
            "GRANOFLOW_MILESTONE_ID": milestone_id,
            "GRANOFLOW_TASK_ID": task_id,
            "GRANOFLOW_MILESTONE_REPORT_PATH": str(report_path),
            "GRANOFLOW_MILESTONE_RUN_MODE": mode,
            "GRANOFLOW_MILESTONE_AUTHORIZATION_PATH": str(authorization_path),
            "GRANOFLOW_EXECUTION_MODE": execution_mode,
            "GRANOFLOW_NODE_LANE": lane or "",
            "GRANOFLOW_NODE_ID": node_id or "",
        }
    )
    process = subprocess.Popen(
        argv,
        cwd=workspace,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + timeout_seconds
    next_heartbeat = time.monotonic()
    timed_out = False
    while process.poll() is None:
        current = time.monotonic()
        if current >= deadline:
            timed_out = True
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            break
        if current >= next_heartbeat:
            heartbeat()
            next_heartbeat = current + heartbeat_seconds
        time.sleep(min(0.25, heartbeat_seconds))
    exit_code = 124 if timed_out else int(process.returncode or 0)
    return WorkerResult(exit_code, timed_out, load_report(report_path))
