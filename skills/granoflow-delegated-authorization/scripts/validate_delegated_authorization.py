#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA = "granoflow_delegated_authorization_v1"
PHASES = {
    "analysisConfirmation",
    "planningPermission",
    "planConfirmation",
    "executionAuthorization",
}
KNOWN_ACTIONS = {
    "local_read",
    "local_versioned_file_create",
    "local_versioned_code_edit",
    "local_format",
    "local_test",
    "gf_task_update",
    "gf_task_attachment_write",
    "gf_task_node_write",
    "gf_task_complete",
    "filesystem_delete_outside_versioned_plan",
    "user_data_delete",
    "approved_asset_overwrite",
    "git_commit",
    "git_push",
    "publish",
    "deploy",
    "login",
    "payment",
    "secret_access",
    "two_factor_authentication",
    "external_message",
}
HARD_FORBIDDEN_ACTIONS = {
    "filesystem_delete_outside_versioned_plan",
    "user_data_delete",
    "approved_asset_overwrite",
    "git_commit",
    "git_push",
    "publish",
    "deploy",
    "login",
    "payment",
    "secret_access",
    "two_factor_authentication",
    "external_message",
}
ENVELOPE_FIELDS = {
    "schema",
    "status",
    "envelopeId",
    "authorizationOwnerTaskId",
    "receiptPolicy",
    "issuedAt",
    "expiresAt",
    "sourceRef",
    "taskIds",
    "phaseGrants",
    "planBindings",
    "allowedRepos",
    "allowedPathGlobs",
    "allowedActions",
    "forbiddenActions",
    "requiredGateFacts",
    "invalidationConditions",
}
FACT_FIELDS = {
    "host",
    "taskId",
    "phase",
    "now",
    "planHash",
    "repo",
    "paths",
    "requestedActions",
    "analysisGrillPassed",
    "planningConfirmed",
    "readinessGrillPassed",
    "unresolvedDecisionCount",
    "scopeEscalated",
    "revoked",
    "stateFresh",
    "receiptVerified",
}
GATE_FIELDS = {
    "analysisGrillPassed",
    "planningConfirmed",
    "readinessGrillPassed",
    "unresolvedDecisionCount",
    "scopeEscalated",
    "stateFresh",
}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class SchemaError(ValueError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a confirmed Granoflow delegated-authorization envelope "
            "against structured current gate facts."
        )
    )
    parser.add_argument("--envelope", type=Path, help="Confirmed envelope JSON file.")
    parser.add_argument("--facts", type=Path, help="Current structured gate-facts JSON file.")
    parser.add_argument(
        "--now",
        help="Override facts.now with an ISO-8601 timestamp for deterministic evaluation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Describe the read-only evaluation without requiring input files.",
    )
    return parser


def require_exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise SchemaError(
            f"{label} fields mismatch: missing={sorted(expected - actual)} "
            f"unknown={sorted(actual - expected)}"
        )


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{label} must be a non-empty string")
    return value


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise SchemaError(f"{label} must be a non-empty list")
    strings = [require_string(item, f"{label}[]") for item in value]
    if len(strings) != len(set(strings)):
        raise SchemaError(f"{label} must not contain duplicates")
    return strings


def parse_time(value: Any, label: str) -> datetime:
    text = require_string(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise SchemaError(f"{label} must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise SchemaError(f"{label} must include an offset")
    return parsed


def validate_glob(pattern: str) -> None:
    path = PurePosixPath(pattern)
    if path.is_absolute() or ".." in path.parts or "\\" in pattern:
        raise SchemaError("allowed path globs must be relative and cannot escape the repo")
    if pattern in {"*", "**", "**/*"} or pattern.startswith("**/"):
        raise SchemaError("overbroad path glob is not allowed")


def validate_envelope(envelope: Any) -> dict[str, Any]:
    if not isinstance(envelope, dict):
        raise SchemaError("envelope must be an object")
    require_exact_fields(envelope, ENVELOPE_FIELDS, "envelope")
    if envelope["schema"] != SCHEMA or envelope["status"] != "confirmed":
        raise SchemaError("envelope schema or status is invalid")
    if envelope["receiptPolicy"] != "app_readback_external":
        raise SchemaError("receiptPolicy must be app_readback_external")
    for field in ("envelopeId", "authorizationOwnerTaskId", "sourceRef"):
        require_string(envelope[field], field)
    issued = parse_time(envelope["issuedAt"], "issuedAt")
    expires = parse_time(envelope["expiresAt"], "expiresAt")
    if expires <= issued:
        raise SchemaError("expiresAt must be later than issuedAt")

    task_ids = require_string_list(envelope["taskIds"], "taskIds")
    grants = envelope["phaseGrants"]
    if not isinstance(grants, dict):
        raise SchemaError("phaseGrants must be an object")
    require_exact_fields(grants, PHASES, "phaseGrants")
    if not all(isinstance(value, bool) for value in grants.values()):
        raise SchemaError("phase grants must be booleans")

    bindings = envelope["planBindings"]
    if not isinstance(bindings, list) or not bindings:
        raise SchemaError("planBindings must be a non-empty list")
    bound_tasks: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict):
            raise SchemaError("plan binding must be an object")
        require_exact_fields(binding, {"taskIds", "path", "sha256"}, "planBinding")
        ids = require_string_list(binding["taskIds"], "planBinding.taskIds")
        if not set(ids).issubset(task_ids) or bound_tasks.intersection(ids):
            raise SchemaError("plan binding task IDs must be unique members of taskIds")
        bound_tasks.update(ids)
        path = require_string(binding["path"], "planBinding.path")
        if not Path(path).is_absolute() or not HASH_RE.fullmatch(binding["sha256"]):
            raise SchemaError("plan binding path/hash is invalid")
    if bound_tasks != set(task_ids):
        raise SchemaError("every task must have exactly one plan binding")

    repos = require_string_list(envelope["allowedRepos"], "allowedRepos")
    if not all(Path(repo).is_absolute() for repo in repos):
        raise SchemaError("allowedRepos must contain absolute paths")
    globs = envelope["allowedPathGlobs"]
    if not isinstance(globs, dict) or set(globs) != set(repos):
        raise SchemaError("allowedPathGlobs keys must exactly match allowedRepos")
    for repo, patterns in globs.items():
        del repo
        for pattern in require_string_list(patterns, "allowedPathGlobs[]"):
            validate_glob(pattern)

    allowed = set(require_string_list(envelope["allowedActions"], "allowedActions"))
    forbidden = set(require_string_list(envelope["forbiddenActions"], "forbiddenActions"))
    if not allowed.union(forbidden).issubset(KNOWN_ACTIONS):
        raise SchemaError("envelope contains an unknown action")
    if allowed.intersection(forbidden) or not HARD_FORBIDDEN_ACTIONS.issubset(forbidden):
        raise SchemaError("forbidden action boundary is incomplete or contradictory")

    gates = envelope["requiredGateFacts"]
    if not isinstance(gates, dict):
        raise SchemaError("requiredGateFacts must be an object")
    require_exact_fields(gates, GATE_FIELDS, "requiredGateFacts")
    if not isinstance(gates["unresolvedDecisionCount"], int):
        raise SchemaError("unresolvedDecisionCount must be an integer")
    for field in GATE_FIELDS - {"unresolvedDecisionCount"}:
        if not isinstance(gates[field], bool):
            raise SchemaError(f"{field} must be a boolean")
    require_string_list(envelope["invalidationConditions"], "invalidationConditions")
    return envelope


def validate_facts(facts: Any) -> dict[str, Any]:
    if not isinstance(facts, dict):
        raise SchemaError("facts must be an object")
    actual = set(facts)
    required = FACT_FIELDS - {"planHash"}
    if not required.issubset(actual) or not actual.issubset(FACT_FIELDS):
        raise SchemaError("facts contain missing or unknown fields")
    if facts["host"] not in {"codex", "cursor", "claude", "opencode"}:
        raise SchemaError("host is unknown")
    if facts["phase"] not in PHASES:
        raise SchemaError("phase is unknown")
    for field in ("taskId", "repo"):
        require_string(facts[field], field)
    parse_time(facts["now"], "now")
    require_string_list(facts["paths"], "paths")
    require_string_list(facts["requestedActions"], "requestedActions")
    if "planHash" in facts and not HASH_RE.fullmatch(require_string(facts["planHash"], "planHash")):
        raise SchemaError("planHash must be a lowercase SHA-256")
    if not isinstance(facts["unresolvedDecisionCount"], int):
        raise SchemaError("unresolvedDecisionCount must be an integer")
    boolean_fields = {
        "analysisGrillPassed",
        "planningConfirmed",
        "readinessGrillPassed",
        "scopeEscalated",
        "revoked",
        "stateFresh",
        "receiptVerified",
    }
    if not all(isinstance(facts[field], bool) for field in boolean_fields):
        raise SchemaError("gate flags must be booleans")
    return facts


def denied(envelope: Any, facts: Any, reason: str) -> dict[str, Any]:
    envelope_id = envelope.get("envelopeId") if isinstance(envelope, dict) else None
    phase = facts.get("phase") if isinstance(facts, dict) else None
    plan_hash = facts.get("planHash") if isinstance(facts, dict) else None
    return {
        "decision": "denied",
        "envelopeId": envelope_id,
        "phase": phase,
        "planHash": plan_hash,
        "reasonCode": reason,
        "evaluatedScope": None,
    }


def evaluate(envelope: Any, facts: Any) -> dict[str, Any]:
    try:
        envelope = validate_envelope(envelope)
        facts = validate_facts(facts)
    except SchemaError:
        return denied(envelope, facts, "invalid_schema")

    if facts["revoked"]:
        return denied(envelope, facts, "revoked")
    if not facts["stateFresh"] or not facts["receiptVerified"]:
        return denied(envelope, facts, "stale_state")
    if parse_time(facts["now"], "now") >= parse_time(envelope["expiresAt"], "expiresAt"):
        return denied(envelope, facts, "expired")
    if facts["taskId"] not in envelope["taskIds"]:
        return denied(envelope, facts, "scope_drift")
    if not envelope["phaseGrants"][facts["phase"]]:
        return denied(envelope, facts, "phase_not_granted")
    if facts["unresolvedDecisionCount"] != 0:
        return denied(envelope, facts, "unresolved_decision")
    if facts["scopeEscalated"]:
        return denied(envelope, facts, "scope_drift")
    if any(
        facts[field] != envelope["requiredGateFacts"][field]
        for field in GATE_FIELDS - {"unresolvedDecisionCount", "scopeEscalated", "stateFresh"}
    ):
        return denied(envelope, facts, "gate_not_passed")

    if facts["phase"] in {"planConfirmation", "executionAuthorization"}:
        binding = next(
            item for item in envelope["planBindings"] if facts["taskId"] in item["taskIds"]
        )
        if facts.get("planHash") != binding["sha256"]:
            return denied(envelope, facts, "scope_drift")

    repo = facts["repo"]
    if repo not in envelope["allowedRepos"]:
        return denied(envelope, facts, "repo_not_allowed")
    for path in facts["paths"]:
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or ".." in candidate.parts or "\\" in path:
            return denied(envelope, facts, "path_not_allowed")
        if not any(
            fnmatch.fnmatchcase(path, pattern) for pattern in envelope["allowedPathGlobs"][repo]
        ):
            return denied(envelope, facts, "path_not_allowed")

    actions = facts["requestedActions"]
    if any(action not in KNOWN_ACTIONS for action in actions):
        return denied(envelope, facts, "unknown_action")
    if any(action in envelope["forbiddenActions"] for action in actions):
        return denied(envelope, facts, "forbidden_action")
    if any(action not in envelope["allowedActions"] for action in actions):
        return denied(envelope, facts, "action_not_allowed")

    return {
        "decision": "allowed",
        "envelopeId": envelope["envelopeId"],
        "phase": facts["phase"],
        "planHash": facts.get("planHash"),
        "reasonCode": "ok",
        "evaluatedScope": {
            "taskId": facts["taskId"],
            "repo": repo,
            "paths": facts["paths"],
            "requestedActions": actions,
        },
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "mutates_state": False,
                    "planned_actions": [
                        "read confirmed envelope JSON",
                        "read current structured gate facts",
                        "validate schema, receipt freshness, gates, plan, repo, paths, and actions",
                        "emit one stable allowed or denied result",
                    ],
                    "artifacts": [],
                    "warnings": [
                        "The validator does not authenticate the user or read "
                        "Granoflow state itself."
                    ],
                },
                ensure_ascii=False,
            )
        )
        return 0
    if args.envelope is None or args.facts is None:
        parser.error("--envelope and --facts are required unless --dry-run is used")
    try:
        envelope = load_json(args.envelope)
        facts = load_json(args.facts)
    except (OSError, json.JSONDecodeError):
        print(json.dumps(denied(None, None, "invalid_schema")))
        return 0
    if args.now:
        facts["now"] = args.now
    print(json.dumps(evaluate(envelope, facts), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
