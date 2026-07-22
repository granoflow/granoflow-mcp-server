#!/usr/bin/env python3
"""Lint Change Impact Fan-out ledgers for discussion decisions.

Fail closed when a material decision batch claims completion without a closed,
well-formed change_impact ledger (required scopes, dispositions, evidence).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_SCOPES = (
    "product_docs",
    "project_work",
    "milestone_work",
    "tasks",
    "prototypes",
    "notes_cards",
    "experience_knowledge",
)

VALID_DISPOSITIONS = frozenset({"updated", "not_applicable", "deferred"})
VALID_ENTITY_TYPES = frozenset(
    {
        "product_doc",
        "user_story",
        "project_work",
        "milestone_work",
        "task",
        "task_work",
        "prototype",
        "note",
        "card",
        "experience",
        "other",
    }
)
VALID_LEDGER_STATUS = frozenset({"open", "closed", "failed"})
VALID_DECISION_CLASSES = frozenset({"product_truth_changing", "craft_only"})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load_yamlish(path: Path) -> Any:
    """Load YAML if PyYAML is available; else accept JSON."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _extract_ledgers(data: Any) -> list[dict[str, Any]]:
    if data is None:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    if "change_impact" in data:
        raw = data["change_impact"]
        if raw is None:
            return []
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
        if isinstance(raw, dict):
            return [raw]
    # Bare ledger object
    if "decision_summary" in data or "scopes_checked" in data or "candidates" in data:
        return [data]
    return []


def _has_updated_evidence(candidate: dict[str, Any]) -> bool:
    evidence = candidate.get("evidence") or {}
    if not isinstance(evidence, dict):
        evidence = {}
    path = candidate.get("path_or_title")
    if isinstance(path, str) and path.strip():
        # Repo doc / local path counts when paired with any hash or id, or alone
        # for product_doc when SHA fields are null but path is present.
        entity_type = candidate.get("entity_type")
        if entity_type in {"product_doc", "user_story", "other"} and path.strip():
            return True
    for key in (
        "content_sha256",
        "package_sha256",
        "prototype_id",
        "version_id",
    ):
        value = evidence.get(key)
        if isinstance(value, str) and value.strip():
            return True
    entity_id = candidate.get("entity_id")
    if isinstance(entity_id, str) and entity_id.strip() and path:
        return True
    return False


def lint_ledger(entry: dict[str, Any], *, index: int = 0) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    prefix = f"change_impact[{index}]"

    if entry.get("contract_loaded") is not True:
        errors.append(
            _err(
                "change_impact_unread",
                f"{prefix}: contract_loaded must be true (MCP load required)",
            )
        )

    decision = entry.get("decision_summary")
    if not isinstance(decision, str) or not decision.strip():
        errors.append(
            _err(
                "change_impact_ledger_incomplete",
                f"{prefix}: decision_summary required",
            )
        )

    scopes = entry.get("scopes_checked")
    if not isinstance(scopes, list) or not scopes:
        errors.append(
            _err(
                "change_impact_ledger_incomplete",
                f"{prefix}: scopes_checked must be a non-empty list",
            )
        )
        scopes = []
    else:
        missing = [s for s in REQUIRED_SCOPES if s not in scopes]
        if missing:
            errors.append(
                _err(
                    "change_impact_ledger_incomplete",
                    f"{prefix}: missing required scopes: {', '.join(missing)}",
                )
            )

    scan_terms = entry.get("scan_terms")
    if not isinstance(scan_terms, list):
        errors.append(
            _err(
                "change_impact_ledger_incomplete",
                f"{prefix}: scan_terms must be a list",
            )
        )
        scan_terms = []

    candidates = entry.get("candidates")
    if candidates is None:
        candidates = []
    if not isinstance(candidates, list):
        errors.append(
            _err(
                "change_impact_ledger_incomplete",
                f"{prefix}: candidates must be a list",
            )
        )
        candidates = []

    claimed_none = bool(entry.get("claimed_none"))
    if claimed_none and candidates:
        pending_or_open = [
            c
            for c in candidates
            if isinstance(c, dict)
            and (
                c.get("disposition") is None
                or c.get("status") == "pending"
                or c.get("disposition") not in VALID_DISPOSITIONS
            )
        ]
        if pending_or_open:
            errors.append(
                _err(
                    "change_impact_false_none",
                    f"{prefix}: claimed_none but undispositioned candidates remain",
                )
            )

    if not scan_terms and not claimed_none:
        # Empty scan_terms only allowed when explicitly claiming none after empty scan
        # OR when candidates exist and were dispositioned (terms still preferred).
        if not candidates:
            errors.append(
                _err(
                    "change_impact_ledger_incomplete",
                    f"{prefix}: scan_terms empty without claimed_none or candidates",
                )
            )

    for ci, cand in enumerate(candidates):
        cprefix = f"{prefix}.candidates[{ci}]"
        if not isinstance(cand, dict):
            errors.append(
                _err(
                    "change_impact_ledger_incomplete",
                    f"{cprefix}: must be an object",
                )
            )
            continue

        entity_type = cand.get("entity_type")
        if entity_type not in VALID_ENTITY_TYPES:
            errors.append(
                _err(
                    "change_impact_ledger_incomplete",
                    f"{cprefix}: invalid entity_type {entity_type!r}",
                )
            )

        disposition = cand.get("disposition")
        if disposition not in VALID_DISPOSITIONS:
            errors.append(
                _err(
                    "change_impact_open_targets",
                    f"{cprefix}: disposition missing or invalid ({disposition!r})",
                )
            )
            continue

        if cand.get("status") == "pending":
            errors.append(
                _err(
                    "change_impact_open_targets",
                    f"{cprefix}: status is still pending",
                )
            )

        reason = cand.get("reason")
        if disposition in {"not_applicable", "deferred"}:
            if not isinstance(reason, str) or not reason.strip():
                errors.append(
                    _err(
                        "change_impact_ledger_incomplete",
                        f"{cprefix}: reason required for {disposition}",
                    )
                )

        if disposition == "deferred":
            evidence = cand.get("evidence") or {}
            owner = evidence.get("owner") if isinstance(evidence, dict) else None
            if not isinstance(owner, str) or not owner.strip():
                errors.append(
                    _err(
                        "change_impact_deferred_unapproved",
                        f"{cprefix}: deferred requires evidence.owner "
                        "(and explicit user consent)",
                    )
                )

        if disposition == "updated":
            if not _has_updated_evidence(cand):
                errors.append(
                    _err(
                        "change_impact_updated_missing_evidence",
                        f"{cprefix}: updated requires path/SHA/id evidence",
                    )
                )

    prototype_updated = any(
        isinstance(c, dict)
        and c.get("entity_type") == "prototype"
        and c.get("disposition") == "updated"
        for c in candidates
    )
    decision_class = entry.get("decision_class")
    if prototype_updated:
        if decision_class not in VALID_DECISION_CLASSES:
            errors.append(
                _err(
                    "prototype_product_truth_class_required",
                    f"{prefix}: prototype updated requires decision_class "
                    "product_truth_changing|craft_only "
                    "(default to product_truth_changing when unsure)",
                )
            )
        if entry.get("product_truth_writeback_loaded") is not True:
            errors.append(
                _err(
                    "prototype_product_truth_writeback_unread",
                    f"{prefix}: product_truth_writeback_loaded must be true "
                    "when prototypes are updated",
                )
            )

    if decision_class == "product_truth_changing":
        if entry.get("product_truth_writeback_loaded") is not True:
            errors.append(
                _err(
                    "prototype_product_truth_writeback_unread",
                    f"{prefix}: product_truth_writeback_loaded must be true "
                    "for product_truth_changing",
                )
            )
        product_doc_updated = any(
            isinstance(c, dict)
            and c.get("entity_type") == "product_doc"
            and c.get("disposition") == "updated"
            for c in candidates
        )
        task_work_updated = any(
            isinstance(c, dict)
            and c.get("entity_type") == "task_work"
            and c.get("disposition") == "updated"
            for c in candidates
        )
        if not product_doc_updated or not task_work_updated:
            errors.append(
                _err(
                    "prototype_product_doc_writeback_required",
                    f"{prefix}: product_truth_changing requires product_doc "
                    "and task_work disposition=updated",
                )
            )
        user_story_dispositioned = any(
            isinstance(c, dict)
            and c.get("entity_type") == "user_story"
            and c.get("disposition") in VALID_DISPOSITIONS
            for c in candidates
        )
        if not user_story_dispositioned:
            errors.append(
                _err(
                    "prototype_user_story_disposition_required",
                    f"{prefix}: product_truth_changing requires at least one "
                    "user_story candidate dispositioned "
                    "(not_applicable allowed with reason)",
                )
            )

    status = entry.get("status")
    if status not in VALID_LEDGER_STATUS:
        errors.append(
            _err(
                "change_impact_ledger_incomplete",
                f"{prefix}: status must be open|closed|failed (got {status!r})",
            )
        )
    elif status == "open":
        errors.append(
            _err(
                "change_impact_open_targets",
                f"{prefix}: ledger status is open",
            )
        )
    elif status == "failed":
        errors.append(
            _err(
                "change_impact_open_targets",
                f"{prefix}: ledger status is failed",
            )
        )

    # If any open-target errors already recorded, keep them; if status closed
    # but there were disposition errors, they already failed.
    ok = not errors
    return {
        "ok": ok,
        "index": index,
        "errors": errors,
        "code": "ok" if ok else "change_impact_lint_failed",
    }


def lint_document(data: Any) -> dict[str, Any]:
    ledgers = _extract_ledgers(data)
    if not ledgers:
        return {
            "ok": False,
            "code": "change_impact_lint_failed",
            "errors": [
                _err(
                    "change_impact_ledger_incomplete",
                    "no change_impact ledger found",
                )
            ],
            "results": [],
        }

    results = [lint_ledger(entry, index=i) for i, entry in enumerate(ledgers)]
    errors = [e for r in results for e in r["errors"]]
    ok = all(r["ok"] for r in results)
    return {
        "ok": ok,
        "code": "ok" if ok else "change_impact_lint_failed",
        "errors": errors,
        "results": results,
    }


def lint_path(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "ok": False,
            "code": "change_impact_lint_failed",
            "errors": [_err("missing_file", str(path))],
            "results": [],
        }
    data = _load_yamlish(path)
    result = lint_document(data)
    result["path"] = str(path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ledger",
        type=Path,
        help="Path to change_impact YAML/JSON or Work Document excerpt",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args(argv)

    result = lint_path(args.ledger)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["ok"]:
            print("ok")
        else:
            print(result["code"], file=sys.stderr)
            for err in result.get("errors", []):
                print(f"{err['code']}: {err['detail']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
