#!/usr/bin/env python3
"""Lint granoflow_prototype_revision_ledger_v1 (serial multi-draft task UI)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_prototype_revision_ledger_v1"
MAX_DRAFTS = 5
MAX_SELECTION = 3
VALID_MODES = frozenset({"interactive", "unattended"})
VALID_STATUS = frozenset({"in_progress", "ready_for_selection", "accepted", "blocked"})
VALID_STOP = frozenset({"zero_blocking", "max_drafts"})
VALID_SELECTION_MODE = frozenset({"confirm_or_revise", "pick_among", "auto_adopt"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ERROR_PRIORITY = (
    "prototype_revision_ledger_required",
    "prototype_revision_max_drafts",
    "prototype_revision_late_draft_without_blocking",
    "prototype_revision_blocking_residual",
    "prototype_revision_stack_gates_incomplete",
    "prototype_revision_selection_invalid",
    "prototype_revision_lint_failed",
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


def _extract_ledger(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    block = data.get("prototype_revision_ledger")
    if isinstance(block, dict):
        return block
    if data.get("schema") == SCHEMA:
        return data
    return None


def _primary_code(errors: list[dict[str, str]]) -> str:
    if not errors:
        return "ok"
    present = {e["code"] for e in errors}
    for code in ERROR_PRIORITY:
        if code in present:
            return code
    return errors[0]["code"]


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def lint_prototype_revision_ledger(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    ledger = _extract_ledger(data)
    if ledger is None:
        return {
            "ok": False,
            "code": "prototype_revision_ledger_required",
            "errors": [
                _err(
                    "prototype_revision_ledger_required",
                    "prototype_revision_ledger object required",
                )
            ],
        }

    if ledger.get("contract_loaded") is not True:
        errors.append(
            _err(
                "prototype_revision_lint_failed",
                "contract_loaded must be true (load prototype-serial-revision)",
            )
        )
    if ledger.get("schema") != SCHEMA:
        errors.append(
            _err(
                "prototype_revision_lint_failed",
                f"schema must be {SCHEMA}",
            )
        )

    mode = str(ledger.get("mode") or "").strip().lower()
    if mode not in VALID_MODES:
        errors.append(
            _err(
                "prototype_revision_lint_failed",
                "mode must be interactive|unattended",
            )
        )

    status = str(ledger.get("status") or "").strip().lower()
    if status not in VALID_STATUS:
        errors.append(
            _err(
                "prototype_revision_lint_failed",
                "status must be in_progress|ready_for_selection|accepted|blocked",
            )
        )

    drafts = ledger.get("drafts")
    if not isinstance(drafts, list) or not drafts:
        errors.append(
            _err(
                "prototype_revision_ledger_required",
                "drafts must be a non-empty list",
            )
        )
        return {
            "ok": False,
            "code": _primary_code(errors),
            "errors": errors,
        }

    if len(drafts) > MAX_DRAFTS:
        errors.append(
            _err(
                "prototype_revision_max_drafts",
                f"drafts length must be ≤ {MAX_DRAFTS} (got {len(drafts)})",
            )
        )

    seen_ordinals: set[int] = set()
    ordered: list[dict[str, Any]] = []
    for index, row in enumerate(drafts):
        prefix = f"drafts[{index}]"
        if not isinstance(row, dict):
            errors.append(_err("prototype_revision_lint_failed", f"{prefix} must be an object"))
            continue
        ordinal = _as_int(row.get("ordinal"))
        if ordinal is None or ordinal < 1:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"{prefix}.ordinal must be a positive integer",
                )
            )
            continue
        if ordinal in seen_ordinals:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"duplicate draft ordinal {ordinal}",
                )
            )
        seen_ordinals.add(ordinal)
        if ordinal != index + 1:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"{prefix}.ordinal must be {index + 1} (contiguous from 1)",
                )
            )

        blocking_in = _as_int(row.get("blocking_in"))
        blocking_out = _as_int(row.get("blocking_out"))
        if blocking_in is None or blocking_in < 0:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"{prefix}.blocking_in must be a non-negative integer",
                )
            )
            blocking_in = 0
        if blocking_out is None or blocking_out < 0:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"{prefix}.blocking_out must be a non-negative integer",
                )
            )
            blocking_out = 0

        if ordinal == 1 and blocking_in != 0:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    "draft 1 blocking_in must be 0",
                )
            )
        if ordinal >= 4 and blocking_in <= 0:
            errors.append(
                _err(
                    "prototype_revision_late_draft_without_blocking",
                    f"draft {ordinal} requires blocking_in > 0 "
                    "(advisory/nit must not open drafts 4–5)",
                )
            )
        if ordinal >= 2:
            prev = ordered[-1] if ordered else None
            if prev is not None:
                prev_out = _as_int(prev.get("blocking_out"))
                if prev_out is not None and prev_out <= 0:
                    errors.append(
                        _err(
                            "prototype_revision_lint_failed",
                            f"draft {ordinal} exists after prior zero blocking_out "
                            "(must early-stop)",
                        )
                    )
                if (
                    prev_out is not None
                    and prev_out > 0
                    and blocking_in != prev_out
                    and blocking_in <= 0
                ):
                    errors.append(
                        _err(
                            "prototype_revision_late_draft_without_blocking"
                            if ordinal >= 4
                            else "prototype_revision_lint_failed",
                            f"draft {ordinal} blocking_in must be > 0 when "
                            "continuing after residual blocking",
                        )
                    )

        html_paths = row.get("html_paths")
        if not isinstance(html_paths, list) or not html_paths:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"{prefix}.html_paths must be a non-empty list",
                )
            )
        elif not all(_nonempty_str(p) for p in html_paths):
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"{prefix}.html_paths entries must be non-empty strings",
                )
            )

        sha = row.get("package_sha256")
        if sha is not None and not (isinstance(sha, str) and SHA256_RE.fullmatch(sha)):
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    f"{prefix}.package_sha256 must be 64 hex or null",
                )
            )

        if status in {"ready_for_selection", "accepted"}:
            for gate_field in (
                "component_effect_matrix_sha256",
                "stack_realization_notes_sha256",
            ):
                gate_sha = row.get(gate_field)
                if not (isinstance(gate_sha, str) and SHA256_RE.fullmatch(gate_sha)):
                    errors.append(
                        _err(
                            "prototype_revision_stack_gates_incomplete",
                            f"{prefix}.{gate_field} must be 64 hex before "
                            "ready_for_selection|accepted",
                        )
                    )

        ordered.append(row)

    stop_reason = ledger.get("stop_reason")
    if status in {"ready_for_selection", "accepted"}:
        if stop_reason not in VALID_STOP:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    "stop_reason must be zero_blocking|max_drafts when "
                    "ready_for_selection|accepted",
                )
            )
        last = ordered[-1] if ordered else None
        last_out = _as_int(last.get("blocking_out")) if last else None
        if stop_reason == "zero_blocking" and last_out is not None and last_out > 0:
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    "stop_reason=zero_blocking requires last blocking_out=0",
                )
            )
        if stop_reason == "max_drafts" and len(drafts) != MAX_DRAFTS:
            errors.append(
                _err(
                    "prototype_revision_max_drafts",
                    "stop_reason=max_drafts requires exactly 5 drafts",
                )
            )
        if last_out is not None and last_out > 0 and status == "accepted":
            errors.append(
                _err(
                    "prototype_revision_blocking_residual",
                    "accepted forbids residual blocking on the last draft",
                )
            )
        if (
            last_out is not None
            and last_out > 0
            and status == "ready_for_selection"
            and stop_reason == "max_drafts"
        ):
            errors.append(
                _err(
                    "prototype_revision_blocking_residual",
                    "max_drafts with residual blocking must use status=blocked "
                    "(not ready_for_selection)",
                )
            )

    if status == "blocked":
        last = ordered[-1] if ordered else None
        last_out = _as_int(last.get("blocking_out")) if last else None
        if last_out is not None and last_out <= 0 and stop_reason != "max_drafts":
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    "status=blocked expects residual blocking or max_drafts stop",
                )
            )

    surface = ledger.get("selection_surface")
    if not isinstance(surface, dict):
        errors.append(
            _err(
                "prototype_revision_selection_invalid",
                "selection_surface object required",
            )
        )
        surface = {}

    selection_mode = str(surface.get("selection_mode") or "").strip().lower()
    ordinals = surface.get("draft_ordinals")
    recommended = _as_int(surface.get("recommended_ordinal"))
    n = len(drafts)
    expected_surface = list(range(max(1, n - MAX_SELECTION + 1), n + 1))

    if status in {"ready_for_selection", "accepted"}:
        if mode == "unattended":
            if selection_mode != "auto_adopt":
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        "unattended selection_mode must be auto_adopt",
                    )
                )
        elif mode == "interactive":
            if n == 1 and selection_mode != "confirm_or_revise":
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        "single-draft interactive selection_mode must be "
                        "confirm_or_revise (do not force a multi-pick)",
                    )
                )
            if n >= 2 and selection_mode != "pick_among":
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        "multi-draft interactive selection_mode must be pick_among",
                    )
                )

        if not isinstance(ordinals, list) or not ordinals:
            errors.append(
                _err(
                    "prototype_revision_selection_invalid",
                    "selection_surface.draft_ordinals must be a non-empty list",
                )
            )
        else:
            try:
                as_ints = [int(x) for x in ordinals]
            except (TypeError, ValueError):
                as_ints = []
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        "draft_ordinals must be integers",
                    )
                )
            if as_ints and as_ints != expected_surface:
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        f"draft_ordinals must be last min(n,3)={expected_surface} "
                        f"(got {as_ints})",
                    )
                )
            if len(as_ints) > MAX_SELECTION:
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        f"draft_ordinals length must be ≤ {MAX_SELECTION}",
                    )
                )

        if recommended is None or recommended < 1 or recommended > n:
            errors.append(
                _err(
                    "prototype_revision_selection_invalid",
                    "recommended_ordinal must reference an existing draft",
                )
            )
        else:
            last = ordered[-1] if ordered else None
            last_out = _as_int(last.get("blocking_out")) if last else None
            last_ord = _as_int(last.get("ordinal")) if last else None
            if last_out == 0 and last_ord is not None and recommended != last_ord:
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        "recommended_ordinal must be the last zero-blocking draft",
                    )
                )
            if last_out is not None and last_out > 0:
                errors.append(
                    _err(
                        "prototype_revision_blocking_residual",
                        "cannot recommend / ready_for_selection while last "
                        "draft still has blocking findings",
                    )
                )

    if status == "accepted":
        accepted = _as_int(ledger.get("accepted_ordinal"))
        if accepted is None or accepted < 1 or accepted > n:
            errors.append(
                _err(
                    "prototype_revision_selection_invalid",
                    "accepted_ordinal required and must reference a draft",
                )
            )
        elif isinstance(ordinals, list):
            try:
                surface_set = {int(x) for x in ordinals}
            except (TypeError, ValueError):
                surface_set = set()
            if mode == "interactive" and accepted not in surface_set and n > 0:
                errors.append(
                    _err(
                        "prototype_revision_selection_invalid",
                        "accepted_ordinal must be on the selection surface",
                    )
                )
        sha = ledger.get("accepted_package_sha256")
        if not (isinstance(sha, str) and SHA256_RE.fullmatch(sha)):
            errors.append(
                _err(
                    "prototype_revision_lint_failed",
                    "accepted_package_sha256 must be 64 hex",
                )
            )

    return {
        "ok": not errors,
        "code": _primary_code(errors),
        "errors": errors,
        "draft_count": len(drafts),
        "mode": mode or None,
        "status": status or None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task_work",
        type=Path,
        help="Task Work YAML/JSON with prototype_revision_ledger",
    )
    args = parser.parse_args(argv)
    try:
        result = lint_prototype_revision_ledger(_load(args.task_work))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "prototype_revision_lint_failed",
            "errors": [_err("prototype_revision_lint_failed", str(error))],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
