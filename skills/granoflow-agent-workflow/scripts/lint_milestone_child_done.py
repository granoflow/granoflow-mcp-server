#!/usr/bin/env python3
"""Lint: milestone acceptance confirmed ⇒ every in-scope child App status=done."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

EXCLUDED_TASK_STATUS = frozenset({"cancelled", "deleted", "superseded"})
DONE_STATUS = frozenset({"done", "completed"})
PASSED_ACCEPTANCE = frozenset({"passed", "accepted"})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _find_list(value: Any, keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        for key in keys:
            items = value.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        for child in value.values():
            found = _find_list(child, keys)
            if found:
                return found
    return []


def extract_acceptance_status(milestone_work: Any) -> str | None:
    if not isinstance(milestone_work, dict):
        return None
    status = milestone_work.get("acceptance_status")
    if isinstance(status, str) and status.strip():
        return status.strip()
    return None


def extract_in_scope_task_ids(milestone_work: Any) -> set[str] | None:
    """Return explicit in-scope ids from task_plan, or None = all non-excluded."""
    if not isinstance(milestone_work, dict):
        return None
    plan = milestone_work.get("task_plan")
    tasks: list[Any] | None = None
    if isinstance(plan, dict) and isinstance(plan.get("tasks"), list):
        tasks = plan["tasks"]
    elif isinstance(milestone_work.get("in_scope_task_ids"), list):
        return {
            str(x).strip()
            for x in milestone_work["in_scope_task_ids"]
            if isinstance(x, str | int) and str(x).strip()
        }
    if not tasks:
        return None
    ids: set[str] = set()
    for row in tasks:
        if not isinstance(row, dict):
            continue
        for key in ("task_id", "id", "app_task_id"):
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                ids.add(value.strip())
                break
    return ids or None


def lint_milestone_child_done(
    *,
    acceptance_status: str | None,
    tasks: list[dict[str, Any]],
    in_scope_task_ids: set[str] | None = None,
    claim_passed: bool = False,
) -> dict[str, Any]:
    """Fail when Layer B is (claimed) passed but any in-scope child is not done."""
    errors: list[dict[str, str]] = []
    status = (acceptance_status or "").strip().lower()
    must_check = claim_passed or status in PASSED_ACCEPTANCE
    if not must_check:
        return {
            "ok": True,
            "code": "ok",
            "errors": [],
            "checked": False,
            "acceptance_status": acceptance_status,
        }

    pending: list[str] = []
    considered = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("id") or "").strip()
        if not task_id:
            continue
        task_status = str(task.get("status") or "").strip().lower()
        if task_status in EXCLUDED_TASK_STATUS:
            continue
        if in_scope_task_ids is not None and task_id not in in_scope_task_ids:
            continue
        considered += 1
        if task_status not in DONE_STATUS:
            title = str(task.get("title") or "").strip()
            label = f"{task_id}" + (f" ({title})" if title else "")
            pending.append(label)

    if considered == 0:
        errors.append(
            _err(
                "milestone_child_done_lint_failed",
                "no in-scope child tasks to verify while claiming milestone acceptance",
            )
        )
    elif pending:
        errors.append(
            _err(
                "milestone_child_pending_on_acceptance",
                "milestone acceptance confirmed but in-scope children not done: "
                + ", ".join(pending),
            )
        )

    if errors:
        return {
            "ok": False,
            "code": errors[0]["code"],
            "errors": errors,
            "checked": True,
            "acceptance_status": acceptance_status,
            "pending_count": len(pending),
            "considered_count": considered,
        }
    return {
        "ok": True,
        "code": "ok",
        "errors": [],
        "checked": True,
        "acceptance_status": acceptance_status,
        "pending_count": 0,
        "considered_count": considered,
    }


class _ApiError(RuntimeError):
    pass


def _fetch_tasks_for_milestone(
    milestone_id: str,
    *,
    base_url: str | None,
    token: str | None,
) -> list[dict[str, Any]]:
    root = (
        base_url or os.environ.get("GRANOFLOW_API_BASE_URL") or "http://127.0.0.1:56789"
    ).rstrip("/")
    auth = token if token is not None else os.environ.get("GRANOFLOW_API_TOKEN")
    headers = {"Accept": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    request = urllib.request.Request(f"{root}/v1/tasks", headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8") or "{}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise _ApiError("Granoflow Local HTTP API request failed") from error
    if not isinstance(payload, dict) or payload.get("ok") is False:
        raise _ApiError("Granoflow Local HTTP API rejected the request")
    return [
        item for item in _find_list(payload, ("items",)) if item.get("milestoneId") == milestone_id
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--milestone-work",
        type=Path,
        help="Milestone Work YAML/JSON (reads acceptance_status + optional task_plan)",
    )
    parser.add_argument(
        "--tasks-json",
        type=Path,
        help="JSON list or {items:[...]} of App tasks (offline / tests)",
    )
    parser.add_argument(
        "--milestone-id",
        help="Fetch /v1/tasks filtered by milestoneId (requires local App API)",
    )
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument(
        "--claim-passed",
        action="store_true",
        help="Check as if acceptance is being claimed now (even if status not yet passed)",
    )
    parser.add_argument(
        "--acceptance-status",
        default=None,
        help="Override acceptance_status (e.g. passed)",
    )
    args = parser.parse_args(argv)

    milestone_work: Any = {}
    if args.milestone_work is not None:
        try:
            milestone_work = _load(args.milestone_work) or {}
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            result = {
                "ok": False,
                "code": "milestone_child_done_lint_failed",
                "errors": [_err("milestone_child_done_lint_failed", str(exc))],
            }
            print(json.dumps(result, ensure_ascii=False))
            return 1

    acceptance = args.acceptance_status
    if acceptance is None:
        acceptance = extract_acceptance_status(milestone_work)
    in_scope = extract_in_scope_task_ids(milestone_work)

    tasks: list[dict[str, Any]] = []
    try:
        if args.tasks_json is not None:
            raw = _load(args.tasks_json)
            if isinstance(raw, list):
                tasks = [t for t in raw if isinstance(t, dict)]
            elif isinstance(raw, dict):
                tasks = _find_list(raw, ("items", "tasks"))
            else:
                raise ValueError("tasks-json root must be list or object with items")
        elif args.milestone_id:
            tasks = _fetch_tasks_for_milestone(
                args.milestone_id, base_url=args.base_url, token=args.token
            )
        else:
            raise ValueError("provide --tasks-json or --milestone-id")
    except (_ApiError, OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "ok": False,
            "code": "milestone_child_done_lint_failed",
            "errors": [_err("milestone_child_done_lint_failed", str(exc))],
        }
        print(json.dumps(result, ensure_ascii=False))
        return 1

    # When fetching by milestone id, default scope is that milestone's tasks.
    if in_scope is None and args.milestone_id:
        in_scope = {
            str(t.get("id")).strip()
            for t in tasks
            if isinstance(t.get("id"), str) and str(t.get("id")).strip()
        }

    result = lint_milestone_child_done(
        acceptance_status=acceptance,
        tasks=tasks,
        in_scope_task_ids=in_scope,
        claim_passed=args.claim_passed,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
