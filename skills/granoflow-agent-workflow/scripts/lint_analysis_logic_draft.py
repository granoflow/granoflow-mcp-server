#!/usr/bin/env python3
"""Validate the pre-prototype Task Analysis logic draft."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
DATA_DISPOSITIONS = {"not_applicable", "unchanged", "extend", "breaking"}


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        try:
            loader = importlib.import_module("yaml").safe_load
            value = loader(text)
        except ImportError:
            value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("root must be an object")
    return value


def _extract(data: dict[str, Any]) -> dict[str, Any] | None:
    value = data.get("analysis_logic_draft", data)
    return value if isinstance(value, dict) else None


def canonical_logic_draft_sha256(draft: dict[str, Any]) -> str:
    excluded = {"draft_sha256", "status", "review"}
    payload = {key: value for key, value in draft.items() if key not in excluded}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def validate_analysis_logic_draft(data: dict[str, Any]) -> dict[str, Any]:
    draft = _extract(data)
    errors: list[dict[str, str]] = []
    if draft is None:
        return {
            "ok": False,
            "code": "analysis_logic_draft_required",
            "errors": [{"code": "analysis_logic_draft_required", "detail": "draft missing"}],
        }
    if draft.get("schema") != "granoflow_analysis_logic_draft_v1":
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "logic draft schema invalid",
            }
        )
    for field in ("task_id", "data_disposition_basis"):
        if not _nonempty(draft.get(field)):
            errors.append(
                {
                    "code": "analysis_logic_draft_incomplete",
                    "detail": f"{field} required",
                }
            )
    for field in (
        "source_refs",
        "workflows",
        "state_model",
        "permissions",
        "platform_constraints",
        "feasibility_findings",
        "open_blockers",
    ):
        if not isinstance(draft.get(field), list):
            errors.append(
                {
                    "code": "analysis_logic_draft_incomplete",
                    "detail": f"{field} must be a list",
                }
            )
    if not _nonempty_list(draft.get("source_refs")):
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "source_refs must be non-empty",
            }
        )
    system_type = draft.get("system_type")
    if system_type not in {"existing", "greenfield"}:
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "system_type must be existing|greenfield",
            }
        )
    if system_type == "existing" and not _nonempty_list(draft.get("existing_system_evidence")):
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "existing systems require current code/schema/API evidence",
            }
        )
    if system_type == "greenfield" and not _nonempty(draft.get("greenfield_basis")):
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "greenfield_basis required",
            }
        )
    disposition = draft.get("data_disposition")
    if disposition not in DATA_DISPOSITIONS:
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "data_disposition invalid",
            }
        )
    entities = draft.get("domain_entities")
    if not isinstance(entities, list) or (not entities and disposition != "not_applicable"):
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "domain_entities required unless data is not applicable",
            }
        )
    for field in ("workflows", "state_model", "permissions"):
        if not _nonempty_list(draft.get(field)):
            errors.append(
                {
                    "code": "analysis_logic_draft_incomplete",
                    "detail": f"{field} must be non-empty",
                }
            )
    blockers = draft.get("open_blockers")
    if isinstance(blockers, list) and blockers:
        errors.append(
            {
                "code": "analysis_logic_draft_blocking_findings",
                "detail": "open blocking findings remain",
            }
        )

    actual_digest = canonical_logic_draft_sha256(draft)
    if draft.get("draft_sha256") != actual_digest:
        errors.append(
            {
                "code": "analysis_logic_draft_digest_mismatch",
                "detail": "logic draft digest is stale",
            }
        )
    review = draft.get("review")
    review_valid = (
        isinstance(review, dict)
        and _nonempty(review.get("author_id"))
        and _nonempty(review.get("reviewer_id"))
        and review.get("author_id") != review.get("reviewer_id")
        and review.get("status") == "passed"
        and _nonempty_list(review.get("evidence_refs"))
        and review.get("reviewed_draft_sha256") == actual_digest
    )
    if not review_valid:
        errors.append(
            {
                "code": "analysis_logic_draft_review_failed",
                "detail": "independent review must pass the current digest",
            }
        )
    if draft.get("status") != "prototype_ready":
        errors.append(
            {
                "code": "analysis_logic_draft_incomplete",
                "detail": "status must be prototype_ready",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "draft_sha256": actual_digest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_analysis_logic_draft(_load(args.draft))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "analysis_logic_draft_required",
            "errors": [{"code": "analysis_logic_draft_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
