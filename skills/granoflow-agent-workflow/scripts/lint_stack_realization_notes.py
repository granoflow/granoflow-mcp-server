#!/usr/bin/env python3
"""Lint granoflow_stack_realization_notes_v1 (stack deliverable map for UI prototypes)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_stack_realization_notes_v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_DISPOSITION = frozenset(
    {
        "native_supported",
        "adapted_fallback",
        "enhancement_schematic",
        "user_accepted_degrade",
    }
)
NEEDS_NOTE = frozenset({"adapted_fallback", "enhancement_schematic", "user_accepted_degrade"})
ERROR_PRIORITY = (
    "stack_realization_notes_required",
    "stack_realization_notes_matrix_mismatch",
    "stack_realization_notes_coverage_incomplete",
    "stack_realization_notes_disposition_invalid",
    "stack_realization_notes_incomplete",
    "stack_realization_notes_lint_failed",
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


def _extract_notes(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    block = data.get("stack_realization_notes")
    if isinstance(block, dict):
        return block
    if data.get("schema") == SCHEMA:
        return data
    return None


def _extract_matrix(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    block = data.get("ui_component_effect_matrix")
    if isinstance(block, dict):
        return block
    if data.get("schema") == "ui_component_effect_matrix_v1":
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


def _selected_keys(matrix: dict[str, Any]) -> list[tuple[str, str | None]]:
    """Return (role, candidate_id) for decision=selected rows."""
    candidates = matrix.get("candidates")
    if not isinstance(candidates, list):
        return []
    keys: list[tuple[str, str | None]] = []
    for row in candidates:
        if not isinstance(row, dict):
            continue
        if row.get("decision") != "selected":
            continue
        role = row.get("role")
        if not _nonempty_str(role):
            continue
        cid = row.get("candidate_id")
        cid_s = str(cid).strip() if _nonempty_str(cid) else None
        keys.append((str(role).strip(), cid_s))
    return keys


def lint_stack_realization_notes(
    data: Any,
    *,
    matrix_data: Any | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    notes = _extract_notes(data)
    if notes is None:
        return {
            "ok": False,
            "code": "stack_realization_notes_required",
            "errors": [
                _err(
                    "stack_realization_notes_required",
                    "stack_realization_notes object required",
                )
            ],
        }

    if notes.get("contract_loaded") is not True:
        errors.append(
            _err(
                "stack_realization_notes_lint_failed",
                "contract_loaded must be true (load stack-realization-notes)",
            )
        )
    if notes.get("schema") != SCHEMA:
        errors.append(
            _err(
                "stack_realization_notes_lint_failed",
                f"schema must be {SCHEMA}",
            )
        )
    if not _nonempty_str(notes.get("stack_id")):
        errors.append(
            _err(
                "stack_realization_notes_incomplete",
                "stack_id required",
            )
        )
    for field in ("platform_matrix_sha256", "component_effect_matrix_sha256"):
        value = notes.get(field)
        if not (isinstance(value, str) and SHA256_RE.fullmatch(value)):
            errors.append(
                _err(
                    "stack_realization_notes_incomplete",
                    f"{field} must be 64 hex",
                )
            )

    rows = notes.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append(
            _err(
                "stack_realization_notes_incomplete",
                "rows must be a non-empty list",
            )
        )
        rows = []

    seen_keys: set[tuple[str, str | None]] = set()
    for index, row in enumerate(rows):
        prefix = f"rows[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "stack_realization_notes_incomplete",
                    f"{prefix} must be an object",
                )
            )
            continue
        role = row.get("role")
        if not _nonempty_str(role):
            errors.append(
                _err(
                    "stack_realization_notes_incomplete",
                    f"{prefix}.role required",
                )
            )
            role_s = ""
        else:
            role_s = str(role).strip()
        cid = row.get("candidate_id")
        cid_s = str(cid).strip() if _nonempty_str(cid) else None
        key = (role_s, cid_s)
        if role_s and key in seen_keys:
            errors.append(
                _err(
                    "stack_realization_notes_incomplete",
                    f"duplicate notes for role/candidate {key!r}",
                )
            )
        if role_s:
            seen_keys.add(key)

        if not _nonempty_str(row.get("html_surface")):
            errors.append(
                _err(
                    "stack_realization_notes_incomplete",
                    f"{prefix}.html_surface required",
                )
            )
        if not _nonempty_str(row.get("stack_realization")):
            errors.append(
                _err(
                    "stack_realization_notes_incomplete",
                    f"{prefix}.stack_realization required",
                )
            )
        disposition = str(row.get("disposition") or "").strip()
        if disposition not in VALID_DISPOSITION:
            errors.append(
                _err(
                    "stack_realization_notes_disposition_invalid",
                    f"{prefix}.disposition must be "
                    "native_supported|adapted_fallback|"
                    "enhancement_schematic|user_accepted_degrade",
                )
            )
        elif disposition in NEEDS_NOTE and not _nonempty_str(row.get("fallback_or_schematic_note")):
            errors.append(
                _err(
                    "stack_realization_notes_incomplete",
                    f"{prefix}.fallback_or_schematic_note required for "
                    f"disposition={disposition}",
                )
            )

    notes_sha = notes.get("notes_sha256")
    if notes_sha is not None and not (
        isinstance(notes_sha, str) and SHA256_RE.fullmatch(notes_sha)
    ):
        errors.append(
            _err(
                "stack_realization_notes_incomplete",
                "notes_sha256 must be 64 hex or null",
            )
        )

    matrix = None
    if matrix_data is not None:
        matrix = _extract_matrix(matrix_data)
        if matrix is None and isinstance(data, dict):
            # Allow matrix nested in the same document
            matrix = _extract_matrix(data)
    elif isinstance(data, dict):
        matrix = _extract_matrix(data)

    if matrix_data is not None and matrix is None:
        errors.append(
            _err(
                "stack_realization_notes_matrix_mismatch",
                "matrix input provided but ui_component_effect_matrix missing",
            )
        )
    elif matrix is not None:
        matrix_digest = None
        # Prefer explicit digest field if present; else accept notes binding only
        for key in ("matrix_sha256", "record_sha256", "sha256"):
            if isinstance(matrix.get(key), str) and SHA256_RE.fullmatch(matrix[key]):
                matrix_digest = matrix[key]
                break
        notes_matrix_sha = notes.get("component_effect_matrix_sha256")
        if (
            matrix_digest is not None
            and isinstance(notes_matrix_sha, str)
            and notes_matrix_sha != matrix_digest
        ):
            errors.append(
                _err(
                    "stack_realization_notes_matrix_mismatch",
                    "component_effect_matrix_sha256 does not match matrix digest",
                )
            )

        selected = _selected_keys(matrix)
        if not selected:
            errors.append(
                _err(
                    "stack_realization_notes_coverage_incomplete",
                    "matrix has no decision=selected candidates to cover",
                )
            )
        else:
            # Match by (role, candidate_id) when notes provide candidate_id;
            # else match by role alone if unique among selected.
            role_counts: dict[str, int] = {}
            for role, _cid in selected:
                role_counts[role] = role_counts.get(role, 0) + 1

            covered: set[tuple[str, str | None]] = set()
            for role, cid in selected:
                matched = False
                if (role, cid) in seen_keys:
                    matched = True
                    covered.add((role, cid))
                elif cid is None and (role, None) in seen_keys:
                    matched = True
                    covered.add((role, None))
                elif role_counts.get(role, 0) == 1:
                    # unique role: allow notes row with same role any/null cid
                    for nrole, ncid in seen_keys:
                        if nrole == role:
                            matched = True
                            covered.add((nrole, ncid))
                            break
                if not matched:
                    errors.append(
                        _err(
                            "stack_realization_notes_coverage_incomplete",
                            f"missing notes for selected matrix role="
                            f"{role!r} candidate_id={cid!r}",
                        )
                    )

            for nrole, ncid in seen_keys:
                if not nrole:
                    continue
                ok_extra = False
                for role, cid in selected:
                    if nrole != role:
                        continue
                    if ncid is None or cid is None or ncid == cid:
                        ok_extra = True
                        break
                if not ok_extra:
                    errors.append(
                        _err(
                            "stack_realization_notes_coverage_incomplete",
                            f"notes row role={nrole!r} candidate_id={ncid!r} "
                            "has no selected matrix candidate",
                        )
                    )

    return {
        "ok": not errors,
        "code": _primary_code(errors),
        "errors": errors,
        "row_count": len(rows) if isinstance(rows, list) else 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "notes",
        type=Path,
        help="YAML/JSON with stack_realization_notes (or bare record)",
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=None,
        help="Optional ui_component_effect_matrix YAML/JSON for coverage checks",
    )
    args = parser.parse_args(argv)
    try:
        notes_data = _load(args.notes)
        matrix_data = _load(args.matrix) if args.matrix is not None else None
        result = lint_stack_realization_notes(notes_data, matrix_data=matrix_data)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "stack_realization_notes_lint_failed",
            "errors": [_err("stack_realization_notes_lint_failed", str(error))],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
