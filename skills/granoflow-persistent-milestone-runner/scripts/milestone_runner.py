#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from batch_gate import (
    freeze_batch,
    preparation_complete,
    prepared_task_ids,
    set_disposition,
)
from milestone_api import GranoflowApi, GranoflowApiError
from milestone_state import RunnerAlreadyActive, StateStore, task_available
from milestone_worker import WorkerResult, execute_worker
from node_relay import (
    ContractVersion,
    ExecutionMode,
    NodeLane,
    eligible_node,
    parse_node_title,
    skippable_confirmations,
)

DEFAULT_INTERVAL_SECONDS = 300
ATTEMPT_LIMIT = 100
STATUS_MARKER = "\n\n---\nGranoflow 持久执行状态："
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class RunnerApi(Protocol):
    def health(self) -> dict[str, Any]: ...
    def tasks(self, milestone_id: str) -> list[dict[str, Any]]: ...
    def task(self, task_id: str) -> dict[str, Any] | None: ...
    def attachments(self, task_id: str) -> list[dict[str, Any]]: ...
    def attachment(self, task_id: str, attachment_id: str) -> dict[str, Any]: ...
    def nodes(self, task_id: str) -> list[dict[str, Any]]: ...
    def update_node(self, task_id: str, node_id: str, updated_at: str, status: str) -> None: ...
    def update_description(self, task_id: str, description: str) -> None: ...


def task_fingerprint(task: dict[str, Any]) -> str:
    safe = {key: task.get(key) for key in ("id", "title", "description", "status", "updatedAt")}
    return hashlib.sha256(
        json.dumps(safe, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _find_value(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = _find_value(child, key)
            if found is not None:
                return found
    return None


def validate_authorization(value: Any, milestone_id: str, now: datetime | None = None) -> str:
    if not isinstance(value, dict):
        return "authorization_missing"
    required = {
        "schema",
        "status",
        "milestoneId",
        "issuedAt",
        "expiresAt",
        "runtimeAccess",
        "autoConfirmInternalGates",
        "requiredExternalCapabilities",
        "externalCapabilities",
        "secretPolicy",
    }
    if set(value) != required:
        return "authorization_invalid"
    if (
        value["schema"] != "granoflow_milestone_authorization_v1"
        or value["status"] != "confirmed"
        or value["milestoneId"] != milestone_id
        or value["autoConfirmInternalGates"] is not True
    ):
        return "authorization_invalid"
    runtime = value["runtimeAccess"]
    if not isinstance(runtime, dict) or runtime != {"required": "full", "observed": "full"}:
        return "runtime_full_access_required"
    secret = value["secretPolicy"]
    if not isinstance(secret, dict) or secret != {"referenceOnly": True, "persistValues": False}:
        return "authorization_invalid"
    try:
        issued = datetime.fromisoformat(str(value["issuedAt"]).replace("Z", "+00:00"))
        expires = datetime.fromisoformat(str(value["expiresAt"]).replace("Z", "+00:00"))
    except ValueError:
        return "authorization_invalid"
    if issued.tzinfo is None or expires.tzinfo is None or expires <= issued:
        return "authorization_invalid"
    current = now or datetime.now().astimezone()
    if current >= expires:
        return "authorization_expired"
    names = value["requiredExternalCapabilities"]
    capabilities = value["externalCapabilities"]
    if (
        not isinstance(names, list)
        or len(names) != len(set(names))
        or not all(isinstance(name, str) and name for name in names)
        or not isinstance(capabilities, dict)
        or set(capabilities) != set(names)
    ):
        return "external_capability_matrix_incomplete"
    for entry in capabilities.values():
        if not isinstance(entry, dict) or set(entry) != {"disposition", "taskIds", "credentialRef"}:
            return "authorization_invalid"
        disposition = entry["disposition"]
        if disposition not in {"granted", "excluded", "interaction_required"}:
            return "authorization_invalid"
        if not isinstance(entry["taskIds"], list) or not all(
            isinstance(item, str) and item for item in entry["taskIds"]
        ):
            return "authorization_invalid"
        credential = entry["credentialRef"]
        if disposition == "granted":
            if not isinstance(credential, str) or not credential:
                return "external_credential_reference_required"
        elif credential is not None:
            return "authorization_invalid"
    return "ok"


def load_authorization(path: Path | None) -> tuple[Any, str]:
    if path is None:
        return None, "missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None, "unreadable"


def completion_evidence(api: RunnerApi, task: dict[str, Any]) -> tuple[bool, str]:
    task_id = str(task.get("id") or "")
    if task.get("status") != "done":
        return False, "task_still_pending"
    attachments = api.attachments(task_id)
    deliveries = [
        item
        for item in attachments
        if re.match(r"^task-delivery-.*\.md$", str(item.get("displayName") or ""), re.I)
    ]
    if not deliveries:
        return False, "task_delivery_missing"
    delivery = sorted(
        deliveries, key=lambda item: (str(item.get("createdAt") or ""), str(item.get("id") or ""))
    )[-1]
    attachment_id = delivery.get("id")
    if not isinstance(attachment_id, str) or not attachment_id:
        return False, "task_delivery_readback_missing"
    readback = api.attachment(task_id, attachment_id)
    content = _find_value(readback, "content")
    digest = _find_value(readback, "contentSha256")
    if not isinstance(content, str) or not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
        return False, "task_delivery_readback_missing"
    if hashlib.sha256(content.encode("utf-8")).hexdigest() != digest:
        return False, "task_delivery_hash_mismatch"
    if "document_type: task_delivery" not in content or not re.search(
        r"^acceptance_status_as_of:\s*accepted\s*$", content, re.M
    ):
        return False, "task_delivery_not_accepted"
    nodes = api.nodes(task_id)
    if any(node.get("status") != "finished" for node in nodes):
        return False, "task_nodes_incomplete"
    return True, "accepted"


def task_preparation_disposition(
    api: RunnerApi, task: dict[str, Any]
) -> tuple[str, str, str | None, ContractVersion]:
    task_id = str(task.get("id") or "")
    attachments = api.attachments(task_id)
    candidates = [
        item
        for item in attachments
        if item.get("logicalSlot") == "task_work_execution"
        or re.match(r"^task-work-.*-execution-v\d+\.md$", str(item.get("displayName") or ""), re.I)
    ]
    if not candidates:
        # Pre-Task-Work tasks are legacy_v1 and must retain their historical
        # runner behavior. New batch_v2 tasks carry the explicit attachment
        # contract and are blocked when that evidence is missing.
        return "prepared", "legacy_task_without_task_work", None, ContractVersion.LEGACY_V1
    current = sorted(
        candidates,
        key=lambda item: (str(item.get("createdAt") or ""), str(item.get("id") or "")),
    )[-1]
    attachment_id = current.get("id")
    if not isinstance(attachment_id, str) or not attachment_id:
        return (
            "skipped_waiting",
            "task_work_attachment_id_missing",
            "read current Task Work",
            ContractVersion.BATCH_V2,
        )
    readback = api.attachment(task_id, attachment_id)
    content = _find_value(readback, "content")
    digest = _find_value(readback, "contentSha256")
    if not isinstance(content, str) or not isinstance(digest, str):
        return (
            "skipped_waiting",
            "task_work_readback_missing",
            "read Task Work content and SHA",
            ContractVersion.BATCH_V2,
        )
    contract_version = (
        ContractVersion.BATCH_V2
        if re.search(r"^workflow_contract_version:\s*batch_v2\s*$", content, re.M)
        else ContractVersion.LEGACY_V1
    )
    required = {
        "analysis_status": "confirmed",
        "analysis_grill_status": "passed",
        "planning_status": "confirmed",
        "readiness_grill_status": "passed",
    }
    for key, expected in required.items():
        if not re.search(rf"^{re.escape(key)}:\s*{re.escape(expected)}\s*$", content, re.M):
            return (
                "skipped_waiting",
                f"{key}_{expected}_missing",
                f"set {key}={expected}",
                contract_version,
            )
    if (
        "prototype_requirement: required" in content
        and "prototype_input_status: ready" not in content
    ):
        return (
            "skipped_waiting",
            "prototype_not_ready",
            "accept the required HTML prototype",
            contract_version,
        )
    return "prepared", "task_work_ready", None, contract_version


def _write_status_note(
    api: RunnerApi, task: dict[str, Any], phase: str, count: int
) -> dict[str, Any]:
    task_id = str(task["id"])
    description = str(task.get("description") or "").split(STATUS_MARKER, 1)[0]
    if phase == "replan_required":
        message = f"连续 {count} 次没有产生新证据，下一次必须重新诊断并采用不同策略。"
    else:
        message = f"连续 {count} 次没有产生新证据，已停在可恢复交互节点；补充任务信息或授权后继续。"
    api.update_description(task_id, f"{description}{STATUS_MARKER} {message}")
    return api.task(task_id) or task


def record_outcome(
    api: RunnerApi,
    store: StateStore,
    state: dict[str, Any],
    task: dict[str, Any],
    result: WorkerResult,
    reason: str,
) -> str:
    task_id = str(task["id"])
    fingerprint = task_fingerprint(task)
    tasks = state.setdefault("tasks", {})
    previous = tasks.get(task_id, {}) if isinstance(tasks, dict) else {}
    report = result.report
    evidence_advanced = bool(previous.get("taskFingerprint")) and (
        previous.get("taskFingerprint") != fingerprint
    )
    outcome_source = report.attempt_fingerprint if report else reason
    outcome_fingerprint = hashlib.sha256(outcome_source.encode("utf-8")).hexdigest()
    stagnation = 0 if evidence_advanced else int(previous.get("stagnationCount", 0)) + 1
    same_outcome = (
        int(previous.get("sameOutcomeCount", 0)) + 1
        if previous.get("outcomeFingerprint") == outcome_fingerprint
        else 1
    )
    disposition = report.disposition if report else "retry_wait"
    if disposition in {"waiting_for_permission", "waiting_for_user", "blocked"} or stagnation >= 4:
        phase = "waiting_for_user"
    elif stagnation >= 3 or disposition == "replan_required":
        phase = "replan_required"
    else:
        phase = "retry_wait"
    retry_delay = 0 if phase == "replan_required" else min(3600, 60 * (2 ** max(0, stagnation - 1)))
    record = {
        "taskFingerprint": fingerprint,
        "phase": phase,
        "stagnationCount": stagnation,
        "sameOutcomeCount": same_outcome,
        "outcomeFingerprint": outcome_fingerprint,
        "nextRetryAt": time.time() + retry_delay,
        "leaseUntil": 0,
        "heartbeatAt": time.time(),
    }
    tasks[task_id] = record
    attempts = state.setdefault("attempts", [])
    attempts.append(
        {
            "taskId": task_id,
            "taskFingerprint": fingerprint,
            "outcomeFingerprint": outcome_fingerprint,
            "disposition": disposition,
            "evidenceAdvanced": evidence_advanced,
            "exitCode": result.exit_code,
            "timedOut": result.timed_out,
            "phase": phase,
            "at": time.time(),
        }
    )
    state["attempts"] = attempts[-ATTEMPT_LIMIT:]
    if phase in {"replan_required", "waiting_for_user"}:
        updated = _write_status_note(api, task, phase, stagnation)
        record["taskFingerprint"] = task_fingerprint(updated)
    store.save(state)
    return phase


def run_cycle(
    api: RunnerApi,
    store: StateStore,
    milestone_id: str,
    workspace: Path,
    worker_command: str | None,
    authorization_path: Path | None,
    timeout_seconds: int,
    heartbeat_seconds: int,
    dry_run: bool,
    execution_mode: ExecutionMode = ExecutionMode.INTERACTIVE,
    lanes: set[NodeLane] | None = None,
) -> str:
    api.health()
    state = store.load(milestone_id)
    authorization, authorization_fingerprint = load_authorization(authorization_path)
    if not dry_run:
        decision = validate_authorization(authorization, milestone_id)
        if decision != "ok":
            return decision
        authorization_changed = (
            bool(state.get("authorizationFingerprint"))
            and state.get("authorizationFingerprint") != authorization_fingerprint
        )
        state["authorizationFingerprint"] = authorization_fingerprint
        if authorization_changed:
            for record in state.get("tasks", {}).values():
                if isinstance(record, dict) and record.get("phase") == "waiting_for_user":
                    record["phase"] = "retry_wait"
                    record["nextRetryAt"] = 0
        if not worker_command:
            return "worker_command_required"
    tasks = api.tasks(milestone_id)
    if not tasks:
        return "no_milestone_tasks"
    batch = state.get("batch")
    if not isinstance(batch, dict) or batch.get("milestoneId") != milestone_id:
        batch = freeze_batch(
            milestone_id,
            f"{milestone_id}-{int(time.time())}",
            tasks,
        )
        state["batch"] = batch
    snapshot_ids = set(str(task_id) for task_id in batch.get("taskIds", []))
    for task in tasks:
        task_id = task.get("id")
        if not isinstance(task_id, str) or task_id not in snapshot_ids:
            continue
        record = batch.get("tasks", {}).get(task_id, {})
        if isinstance(record, dict) and record.get("disposition") == "unclassified":
            disposition, reason, resume_condition, contract_version = task_preparation_disposition(
                api, task
            )
            set_disposition(batch, task_id, disposition, reason, resume_condition)
            batch["tasks"][task_id]["contractVersion"] = contract_version.value
    if not preparation_complete(batch):
        state["batch"] = batch
        store.save(state)
        return "batch_preparing"
    prepared_ids = prepared_task_ids(batch)
    task_state = state.setdefault("tasks", {})
    accepted = 0
    candidate: dict[str, Any] | None = None
    candidate_node: dict[str, Any] | None = None
    for task in tasks:
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            continue
        if task_id not in prepared_ids:
            continue
        if task.get("status") == "done":
            ok, _ = completion_evidence(api, task)
            if ok:
                task_state[task_id] = {
                    "taskFingerprint": task_fingerprint(task),
                    "phase": "accepted",
                    "leaseUntil": 0,
                    "nextRetryAt": 0,
                }
                accepted += 1
                continue
        fingerprint = task_fingerprint(task)
        record = task_state.get(task_id, {}) if isinstance(task_state, dict) else {}
        if record.get("taskFingerprint") != fingerprint:
            record = {}
            task_state[task_id] = record
        if candidate is None and task_available(record, fingerprint):
            task_nodes = api.nodes(task_id)
            contract_version = ContractVersion(
                str(
                    batch.get("tasks", {})
                    .get(task_id, {})
                    .get("contractVersion", ContractVersion.LEGACY_V1.value)
                )
            )
            if execution_mode is ExecutionMode.UNATTENDED and not dry_run:
                for confirmation in skippable_confirmations(task_nodes, contract_version):
                    node_id = confirmation.get("id")
                    updated_at = confirmation.get("updatedAt")
                    if not isinstance(node_id, str) or not isinstance(updated_at, str):
                        raise GranoflowApiError("Confirmation node lacks optimistic revision data")
                    api.update_node(task_id, node_id, updated_at, "finished")
                    confirmation["status"] = "finished"
            if execution_mode is ExecutionMode.INTERACTIVE or not task_nodes:
                candidate = task
            else:
                selected = eligible_node(
                    task_nodes,
                    execution_mode,
                    lanes or set(),
                    contract_version,
                )
                if selected is not None:
                    candidate = task
                    candidate_node = selected
    store.save(state)
    if accepted == len(tasks):
        return "milestone_tasks_accepted"
    if candidate is None:
        return "no_eligible_tasks"
    if dry_run:
        return "candidate_ready"
    task_id = str(candidate["id"])
    parsed_node = (
        parse_node_title(str(candidate_node.get("title") or "")) if candidate_node else None
    )
    record = task_state.get(task_id, {})
    mode = (
        "completion_audit"
        if candidate.get("status") == "done"
        else "replan"
        if record.get("phase") == "replan_required"
        else "execute"
    )
    now = time.time()
    record.update(
        {
            "taskFingerprint": task_fingerprint(candidate),
            "phase": "running",
            "leaseUntil": now + timeout_seconds + heartbeat_seconds * 2,
            "heartbeatAt": now,
        }
    )
    task_state[task_id] = record
    store.save(state)

    def heartbeat() -> None:
        current = time.time()
        record["heartbeatAt"] = current
        record["leaseUntil"] = current + timeout_seconds + heartbeat_seconds * 2
        store.save(state)

    report_path = store.directory / f"worker-report-{task_id}.json"
    try:
        report_path.unlink(missing_ok=True)
        result = execute_worker(
            milestone_id,
            task_id,
            mode,
            workspace,
            worker_command or "",
            report_path,
            authorization_path or Path("."),
            timeout_seconds,
            heartbeat_seconds,
            heartbeat,
            execution_mode=execution_mode.value,
            lane=parsed_node.lane.value if parsed_node else None,
            node_id=str(candidate_node.get("id")) if candidate_node else None,
            node_title=str(candidate_node.get("title")) if candidate_node else None,
        )
    finally:
        report_path.unlink(missing_ok=True)
    readback = api.task(task_id) or candidate
    if candidate_node is not None:
        current_nodes = api.nodes(task_id)
        target = next(
            (node for node in current_nodes if node.get("id") == candidate_node.get("id")),
            None,
        )
        ok = target is not None and target.get("status") == "finished"
        evidence_reason = "node_accepted" if ok else "assigned_node_still_pending"
    else:
        ok, evidence_reason = completion_evidence(api, readback)
    if ok:
        task_state[task_id] = {
            "taskFingerprint": task_fingerprint(readback),
            "phase": "accepted",
            "leaseUntil": 0,
            "nextRetryAt": 0,
        }
        store.save(state)
        return "task_accepted"
    reason = (
        "worker_timeout"
        if result.timed_out
        else f"worker_exit_{result.exit_code}"
        if result.exit_code
        else evidence_reason
    )
    return record_outcome(api, store, state, readback, result, reason)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Persistently run one Granoflow milestone with a provider-neutral worker."
    )
    parser.add_argument("--milestone-id", required=True)
    parser.add_argument("--authorization-manifest", type=Path)
    parser.add_argument(
        "--worker-command", default=os.environ.get("GRANOFLOW_MILESTONE_WORKER_COMMAND")
    )
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument(
        "--state-dir", type=Path, default=Path.home() / ".local" / "state" / "granoflow-milestones"
    )
    parser.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    parser.add_argument("--timeout-seconds", type=int, default=2700)
    parser.add_argument("--heartbeat-seconds", type=int, default=30)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--execution-mode",
        choices=[mode.value for mode in ExecutionMode],
        default=ExecutionMode.INTERACTIVE.value,
    )
    parser.add_argument(
        "--lane",
        action="append",
        choices=[lane.value for lane in NodeLane if lane is not NodeLane.ACTION],
        default=[],
        help="Repeat for every node lane owned by this worker in layered_handoff mode.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if min(args.interval_seconds, args.timeout_seconds, args.heartbeat_seconds) < 1:
        raise SystemExit("interval, timeout, and heartbeat must be positive")
    execution_mode = ExecutionMode(args.execution_mode)
    lanes = {NodeLane(value) for value in args.lane}
    if execution_mode is ExecutionMode.LAYERED_HANDOFF and not lanes:
        raise SystemExit("layered_handoff requires at least one --lane")
    if execution_mode is ExecutionMode.UNATTENDED and not lanes:
        lanes = {NodeLane.PLAN, NodeLane.DEV, NodeLane.TEST}
    scope = "interactive" if not lanes else "-".join(sorted(lane.value for lane in lanes))
    store = StateStore(args.state_dir / args.milestone_id / scope)
    api = GranoflowApi()
    try:
        with store.process_lock():
            while True:
                try:
                    status = run_cycle(
                        api,
                        store,
                        args.milestone_id,
                        args.workspace.resolve(),
                        args.worker_command,
                        args.authorization_manifest,
                        args.timeout_seconds,
                        args.heartbeat_seconds,
                        args.dry_run,
                        execution_mode,
                        lanes,
                    )
                    print(
                        json.dumps({"ok": True, "status": status, "milestoneId": args.milestone_id})
                    )
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
