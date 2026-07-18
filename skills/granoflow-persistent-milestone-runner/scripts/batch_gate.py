from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

PREPARATION_TERMINAL_STATES = {"prepared", "skipped_waiting"}


def task_fingerprint(task: dict[str, Any]) -> str:
    value = {key: task.get(key) for key in ("id", "title", "description", "status", "updatedAt")}
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def freeze_batch(milestone_id: str, batch_id: str, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "version": 1,
        "milestoneId": milestone_id,
        "batchId": batch_id,
        "taskIds": [str(task["id"]) for task in tasks if task.get("id")],
        "tasks": {
            str(task["id"]): {
                "fingerprint": task_fingerprint(task),
                "disposition": "unclassified",
                "reason": None,
                "resumeCondition": None,
            }
            for task in tasks
            if task.get("id")
        },
        "phase": "preparing",
    }


def set_disposition(
    batch: dict[str, Any],
    task_id: str,
    disposition: str,
    reason: str,
    resume_condition: str | None = None,
) -> None:
    if disposition not in PREPARATION_TERMINAL_STATES:
        raise ValueError(f"invalid preparation disposition: {disposition}")
    record = batch.setdefault("tasks", {}).get(task_id)
    if not isinstance(record, dict):
        raise KeyError(f"task is not in batch snapshot: {task_id}")
    record.update(
        {
            "disposition": disposition,
            "reason": reason,
            "resumeCondition": resume_condition,
        }
    )


def preparation_complete(batch: dict[str, Any]) -> bool:
    records = batch.get("tasks")
    return (
        isinstance(records, dict)
        and bool(records)
        and all(
            isinstance(record, dict) and record.get("disposition") in PREPARATION_TERMINAL_STATES
            for record in records.values()
        )
    )


def prepared_task_ids(batch: dict[str, Any]) -> set[str]:
    records = batch.get("tasks")
    if not isinstance(records, dict):
        return set()
    return {
        task_id
        for task_id, record in records.items()
        if isinstance(record, dict) and record.get("disposition") == "prepared"
    }
