#!/usr/bin/env python3
"""Lint Plan Entry Gate: UI prototypes accepted (or N/A) before Planning starts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_prototype_plan_entry_acceptance_v1"
LEDGER_SCHEMA = "granoflow_prototype_link_ledger_v1"
VALID_REQUIREMENT = frozenset({"required", "not_required", "conditional", "not_applicable"})
NON_UI_REQUIREMENT = frozenset({"not_required", "not_applicable"})
VALID_STATUS = frozenset({"not_applicable", "pending_links", "pending_acceptance", "accepted"})
VALID_SOURCE = frozenset({"none", "verbal", "app_visual_confirmed", "unattended_auto_accept"})
ACCEPTED_SOURCES = frozenset({"verbal", "app_visual_confirmed", "unattended_auto_accept"})
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((file://[^)\s]+)\)")
ERROR_PRIORITY = (
    "plan_entry_prototype_acceptance_required",
    "plan_entry_prototype_unconfirmed",
    "plan_entry_prototype_acceptance_lint_failed",
)


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _extract_acceptance(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    block = data.get("prototype_plan_entry_acceptance")
    if isinstance(block, dict):
        return block
    if data.get("schema") == SCHEMA:
        return data
    # Nested under ledger (allowed shorthand)
    ledger = data.get("prototype_link_ledger")
    if isinstance(ledger, dict):
        nested = ledger.get("plan_entry_acceptance")
        if isinstance(nested, dict):
            return nested
    return None


def _extract_ledger(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    ledger = data.get("prototype_link_ledger")
    if isinstance(ledger, dict):
        return ledger
    if data.get("schema") == LEDGER_SCHEMA:
        return data
    return None


def _resolve_requirement(data: dict[str, Any], acceptance: dict[str, Any] | None) -> str:
    raw = None
    if acceptance is not None and _nonempty_str(acceptance.get("prototype_requirement")):
        raw = str(acceptance["prototype_requirement"]).strip().lower()
    elif _nonempty_str(data.get("prototype_requirement")):
        raw = str(data["prototype_requirement"]).strip().lower()
    if raw is None:
        return "required"  # fail closed: unknown UI-ish until declared N/A
    if raw not in VALID_REQUIREMENT:
        return "invalid"
    if raw == "conditional":
        result = data.get("prototype_condition_result")
        if acceptance is not None and "prototype_condition_result" in acceptance:
            result = acceptance.get("prototype_condition_result")
        if result is False:
            return "not_applicable"
        return "required"
    return raw


def _ledger_has_auditable_digest(ledger: dict[str, Any] | None) -> tuple[bool, str]:
    if ledger is None:
        return False, "prototype_link_ledger missing"
    if ledger.get("status") == "not_applicable":
        return True, "ledger not_applicable"
    if ledger.get("status") != "complete":
        return False, "prototype_link_ledger.status must be complete"
    if ledger.get("chat_digest_emitted") is not True:
        return False, "chat_digest_emitted must be true (auditable links in chat)"
    digest = ledger.get("markdown_digest")
    if not _nonempty_str(digest):
        return False, "markdown_digest required"
    assert isinstance(digest, str)
    urls = {m.group(1).strip() for m in MARKDOWN_LINK_RE.finditer(digest)}
    if not urls:
        return False, "markdown_digest must contain absolute file:// Markdown links"
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not entries:
        return False, "prototype_link_ledger.entries must be non-empty"
    entry_urls = {
        str(row.get("file_url")).strip()
        for row in entries
        if isinstance(row, dict) and _nonempty_str(row.get("file_url"))
    }
    missing = sorted(entry_urls - urls)
    if missing:
        return False, f"digest missing entry file_url(s): {missing}"
    return True, "ok"


def _primary_code(errors: list[dict[str, str]]) -> str:
    if not errors:
        return "ok"
    present = {e["code"] for e in errors}
    for code in ERROR_PRIORITY:
        if code in present:
            return code
    return errors[0]["code"]


def lint_plan_entry_prototype_acceptance(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "plan_entry_prototype_acceptance_lint_failed",
            "errors": [
                _err(
                    "plan_entry_prototype_acceptance_lint_failed",
                    "root must be an object (Task Work excerpt)",
                )
            ],
        }

    acceptance = _extract_acceptance(data)
    ledger = _extract_ledger(data)
    requirement = _resolve_requirement(data, acceptance)

    if requirement == "invalid":
        return {
            "ok": False,
            "code": "plan_entry_prototype_acceptance_lint_failed",
            "errors": [
                _err(
                    "plan_entry_prototype_acceptance_lint_failed",
                    "prototype_requirement must be "
                    "required|not_required|conditional|not_applicable",
                )
            ],
        }

    if requirement in NON_UI_REQUIREMENT:
        if acceptance is not None:
            status = acceptance.get("status")
            if status not in {None, "not_applicable", "accepted"}:
                errors.append(
                    _err(
                        "plan_entry_prototype_acceptance_lint_failed",
                        "non-UI tasks must use status not_applicable " f"(got {status!r})",
                    )
                )
        return {
            "ok": not errors,
            "code": _primary_code(errors),
            "errors": errors,
            "prototype_requirement": requirement,
            "gate": "not_applicable",
        }

    # UI-required path
    auditable_ok, audit_detail = _ledger_has_auditable_digest(ledger)
    if not auditable_ok:
        errors.append(
            _err(
                "plan_entry_prototype_acceptance_required",
                "before Plan entry, emit Prototype Link Digest with absolute "
                f"file:// links ({audit_detail}); then obtain acceptance "
                "(verbal | app visualConfirmed | unattended auto_accept)",
            )
        )
        return {
            "ok": False,
            "code": "plan_entry_prototype_acceptance_required",
            "errors": errors,
            "prototype_requirement": requirement,
            "gate": "pending_links",
        }

    if acceptance is None:
        errors.append(
            _err(
                "plan_entry_prototype_unconfirmed",
                "auditable links exist but prototype_plan_entry_acceptance "
                "is missing; record status=accepted with source "
                "verbal|app_visual_confirmed|unattended_auto_accept "
                "(or wait for interactive user acceptance)",
            )
        )
        return {
            "ok": False,
            "code": "plan_entry_prototype_unconfirmed",
            "errors": errors,
            "prototype_requirement": requirement,
            "gate": "pending_acceptance",
        }

    if "prototype_plan_entry_acceptance" in data:
        if acceptance.get("contract_loaded") is not True:
            errors.append(
                _err(
                    "plan_entry_prototype_acceptance_lint_failed",
                    "contract_loaded must be true",
                )
            )
        if acceptance.get("schema") != SCHEMA:
            errors.append(
                _err(
                    "plan_entry_prototype_acceptance_lint_failed",
                    f"schema must be {SCHEMA}",
                )
            )

    status = acceptance.get("status")
    source = str(acceptance.get("acceptance_source") or acceptance.get("source") or "none")
    source = source.strip().lower()
    if status not in VALID_STATUS:
        errors.append(
            _err(
                "plan_entry_prototype_acceptance_lint_failed",
                "status must be not_applicable|pending_links|" "pending_acceptance|accepted",
            )
        )
    if source not in VALID_SOURCE:
        errors.append(
            _err(
                "plan_entry_prototype_acceptance_lint_failed",
                "acceptance_source must be none|verbal|"
                "app_visual_confirmed|unattended_auto_accept",
            )
        )

    if status != "accepted":
        errors.append(
            _err(
                "plan_entry_prototype_unconfirmed",
                f"status must be accepted before Plan entry (got {status!r}); "
                "interactive: wait for verbal or App visual confirmation; "
                "unattended: auto_accept only after auditable digest",
            )
        )
    elif source not in ACCEPTED_SOURCES:
        errors.append(
            _err(
                "plan_entry_prototype_unconfirmed",
                "accepted requires acceptance_source "
                "verbal|app_visual_confirmed|unattended_auto_accept",
            )
        )

    return {
        "ok": not errors,
        "code": _primary_code(errors),
        "errors": errors,
        "prototype_requirement": requirement,
        "gate": "accepted" if not errors else "blocked",
        "acceptance_source": source if status == "accepted" else source,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task_work",
        type=Path,
        help="Task Work YAML/JSON with prototype_requirement + ledger + acceptance",
    )
    args = parser.parse_args(argv)
    try:
        result = lint_plan_entry_prototype_acceptance(_load(args.task_work))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "plan_entry_prototype_acceptance_lint_failed",
            "errors": [
                _err("plan_entry_prototype_acceptance_lint_failed", str(error)),
            ],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
