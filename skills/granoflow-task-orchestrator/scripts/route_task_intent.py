#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

CAPTURE_PREFIXES = ("gf记", "gf+")
ANALYZE_PREFIXES = ("gf析", "gf?")
RUN_PREFIXES = ("gf做", "gf!")
PLAN_PREFIXES = ("gf规", "gf>")
FINISH_PREFIXES = ("gf完", "gf.")
FORBIDDEN_ACTIONS = {
    "publish",
    "deploy",
    "git_commit",
    "git_push",
    "delete",
    "login",
    "payment",
    "secret_2fa",
    "external_message",
    "approved_asset_overwrite",
    "scope_expansion",
}
LOCAL_SAFE_ACTIONS = {
    "gf_task_read",
    "gf_task_write",
    "gf_task_work_write",
    "gf_node_write",
    "gf_delivery_write",
    "gf_task_complete",
    "local_versioned_code_edit",
    "local_lint",
    "local_format",
    "local_typecheck",
    "local_build",
    "local_test",
    "local_package_dry_run",
}


def choose_due_at(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("explicitDueAt"):
        return {"dueAt": payload["explicitDueAt"], "reasonCode": "explicit"}
    if payload.get("dependencyDueAt"):
        return {"dueAt": payload["dependencyDueAt"], "reasonCode": "dependency"}
    if payload.get("activeBlocking") is True and payload.get("todayDueAt"):
        return {"dueAt": payload["todayDueAt"], "reasonCode": "today"}
    if payload.get("concreteNearAction") is True and payload.get("tomorrowDueAt"):
        return {"dueAt": payload["tomorrowDueAt"], "reasonCode": "tomorrow"}
    if payload.get("milestoneDueAt"):
        return {"dueAt": payload["milestoneDueAt"], "reasonCode": "milestone"}
    return {"dueAt": None, "reasonCode": "none"}


def route(payload: dict[str, Any]) -> dict[str, Any]:
    request = str(payload.get("request") or "").strip()
    if request.startswith(CAPTURE_PREFIXES):
        return {
            "route": "capture",
            "taskDepth": "minimal",
            "stopPoint": "task_readback",
            "placementPolicy": "inbox",
            "duePolicy": "none",
            "executionAuthorized": False,
            "reasonCode": "explicit_capture_override",
        }
    if request.startswith(ANALYZE_PREFIXES):
        return {
            "route": "analyze",
            "taskDepth": "contextual",
            "stopPoint": "analysis_confirmed_or_blocked",
            "placementPolicy": "resolve_strong_pair_or_inbox",
            "duePolicy": "infer_from_timing_facts",
            "executionAuthorized": False,
            "reasonCode": "explicit_analyze_override",
        }
    if request.startswith(PLAN_PREFIXES):
        return {
            "route": "plan",
            "taskDepth": "contextual",
            "stopPoint": "readiness_passed",
            "placementPolicy": "resolve_strong_pair_or_inbox",
            "duePolicy": "infer_from_timing_facts",
            "executionAuthorized": False,
            "reasonCode": "explicit_plan_override",
        }
    if request.startswith(FINISH_PREFIXES):
        return {
            "route": "finish_audit",
            "taskDepth": "execution_ready",
            "stopPoint": "done_readback",
            "placementPolicy": "preserve_current",
            "duePolicy": "preserve_current",
            "executionAuthorized": False,
            "reasonCode": "explicit_finish_audit_override",
        }
    if request.startswith(RUN_PREFIXES):
        requested_actions = set(payload.get("requestedActions") or [])
        forbidden_requested = bool(requested_actions & FORBIDDEN_ACTIONS)
        unknown_requested = bool(requested_actions - LOCAL_SAFE_ACTIONS - FORBIDDEN_ACTIONS)
        target_ambiguous = payload.get("targetAmbiguous") is not False
        gates_ready = all(
            (
                bool(requested_actions),
                not target_ambiguous,
                payload.get("localSafeProfileApproved") is True,
                payload.get("analysisGrillPassed") is True,
                payload.get("planningConfirmed") is True,
                payload.get("readinessGrillPassed") is True,
                payload.get("unresolvedDecisionCount") == 0,
                payload.get("scopeEscalated") is False,
                not forbidden_requested,
                not unknown_requested,
            )
        )
        return {
            "route": "run",
            "taskDepth": "execution_ready",
            "stopPoint": "done_readback",
            "placementPolicy": "resolve_strong_pair_or_inbox",
            "duePolicy": "infer_from_timing_facts",
            "authorizationMode": "gf-local-safe-v1",
            "executionAuthorized": gates_ready,
            "reasonCode": (
                "local_safe_ready"
                if gates_ready
                else "forbidden_action"
                if forbidden_requested
                else "ambiguous_target"
                if target_ambiguous
                else "action_not_declared"
                if not requested_actions
                else "unknown_action"
                if unknown_requested
                else "gate_not_passed"
            ),
        }
    if payload.get("currentWorkRelation") == "side_thought":
        return {
            "route": "capture",
            "taskDepth": "minimal",
            "stopPoint": "task_readback",
            "placementPolicy": "inbox",
            "duePolicy": "none",
            "executionAuthorized": False,
            "reasonCode": "incidental_side_thought",
        }
    if payload.get("alreadyComplete") is True:
        return {
            "route": "finish_audit",
            "taskDepth": "execution_ready",
            "stopPoint": "done_readback",
            "placementPolicy": "preserve_current",
            "duePolicy": "preserve_current",
            "executionAuthorized": False,
            "reasonCode": "completion_evidence_present",
        }

    imperative = payload.get("imperative")
    if imperative == "remember_later":
        return {
            "route": "capture",
            "taskDepth": "minimal",
            "stopPoint": "task_readback",
            "placementPolicy": "inbox",
            "duePolicy": "none",
            "executionAuthorized": False,
            "reasonCode": "remember_later",
        }
    if imperative == "register":
        mature = all(
            (
                payload.get("outcomeClear") is True,
                payload.get("boundariesClear") is True,
                payload.get("evidenceSufficient") is True,
            )
        )
        return {
            "route": "enrich" if mature else "capture",
            "taskDepth": "contextual" if mature else "minimal",
            "stopPoint": "task_readback",
            "placementPolicy": "resolve_strong_pair_or_inbox" if mature else "inbox",
            "duePolicy": "infer_from_timing_facts" if mature else "none",
            "executionAuthorized": False,
            "reasonCode": "mature_discussion" if mature else "insufficient_context",
        }
    if imperative == "analyze":
        return {
            "route": "analyze",
            "taskDepth": "contextual",
            "stopPoint": "analysis_confirmed_or_blocked",
            "placementPolicy": "resolve_strong_pair_or_inbox",
            "duePolicy": "infer_from_timing_facts",
            "executionAuthorized": False,
            "reasonCode": "semantic_analyze_request",
        }
    if imperative == "plan":
        return {
            "route": "plan",
            "taskDepth": "contextual",
            "stopPoint": "readiness_passed",
            "placementPolicy": "resolve_strong_pair_or_inbox",
            "duePolicy": "infer_from_timing_facts",
            "executionAuthorized": False,
            "reasonCode": "semantic_plan_request",
        }
    if imperative == "execute":
        return {
            "route": "run",
            "taskDepth": "execution_ready",
            "stopPoint": "done_readback",
            "placementPolicy": "resolve_strong_pair_or_inbox",
            "duePolicy": "infer_from_timing_facts",
            "authorizationMode": "direct_or_delegated",
            "executionAuthorized": False,
            "reasonCode": "gates_pending",
        }
    raise ValueError("unsupported routing facts")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route structured Granoflow task intent facts.")
    parser.add_argument("--facts", type=Path, help="JSON file with routing facts.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Describe the read-only routing operation."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "mutates_state": False,
                    "planned_actions": ["read structured facts", "return route decision"],
                    "artifacts": [],
                    "warnings": [],
                }
            )
        )
        return 0
    if args.facts is None:
        raise SystemExit("--facts is required unless --dry-run is used")
    payload = json.loads(args.facts.read_text(encoding="utf-8"))
    print(json.dumps(route(payload), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
