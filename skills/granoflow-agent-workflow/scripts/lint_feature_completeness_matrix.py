#!/usr/bin/env python3
"""Lint feature_completeness_matrix ledgers (Milestone Work owned slice)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_feature_completeness_matrix_v1"
TOP_STATUS = frozenset({"draft", "ready", "green", "blocked"})
IMPL_STATUS = frozenset({"pending", "implemented", "blocked_external"})
ROW_RESULT = frozenset({"pending", "green", "blocked_external"})

# User-visible functional deferral copy (not host/error state).
FORBIDDEN_DEFERRAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"后续版本提供"),
    re.compile(r"将在后续版本"),
    re.compile(r"deferred[_\s-]?feature", re.I),
    re.compile(r"coming in a (?:later|future) (?:version|release)", re.I),
    re.compile(r"available in a (?:later|future) (?:version|release)", re.I),
)

# Product error / capability states that must not trip deferral scan.
WHITELIST_PROSE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"暂时无法打开"),
    re.compile(r"temporarily unable to open", re.I),
    re.compile(r"blocked_external"),
)


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ImportError:
        data = json.loads(text)
    return data


def extract_matrix(data: Any) -> Any:
    """Return matrix mapping, or None if absent."""
    if data is None:
        return None
    if isinstance(data, dict) and "feature_completeness_matrix" in data:
        return data["feature_completeness_matrix"]
    if isinstance(data, dict) and data.get("schema") == SCHEMA:
        return data
    return None


def extract_task_plan_tasks(data: Any) -> list[dict[str, Any]] | None:
    if not isinstance(data, dict):
        return None
    plan = data.get("task_plan")
    if isinstance(plan, dict) and isinstance(plan.get("tasks"), list):
        return [t for t in plan["tasks"] if isinstance(t, dict)]
    if isinstance(data.get("tasks"), list):
        return [t for t in data["tasks"] if isinstance(t, dict)]
    return None


def scan_functional_deferral_copy(blobs: list[str] | None) -> list[dict[str, str]]:
    """Return functional_residual_forbidden hits from prose blobs.

    Whitelist patterns (e.g. host error copy 「暂时无法打开」) never match the
    forbidden deferral regexes; they are documented for callers and future
    patterns. Deferral copy always fails closed when present.
    """
    errors: list[dict[str, str]] = []
    if not blobs:
        return errors
    _ = WHITELIST_PROSE_PATTERNS  # documented allowlist; not used to suppress hits
    for i, blob in enumerate(blobs):
        if not isinstance(blob, str) or not blob.strip():
            continue
        for pat in FORBIDDEN_DEFERRAL_PATTERNS:
            if pat.search(blob):
                snippet = blob.strip().replace("\n", " ")[:120]
                errors.append(
                    _err(
                        "functional_residual_forbidden",
                        f"blob[{i}] deferral copy: {snippet}",
                    )
                )
                break
    return errors


def lint_matrix(
    data: Any,
    *,
    require_present: bool = True,
    expect_min_status: str | None = None,
    task_plan_tasks: list[dict[str, Any]] | None = None,
    prose_blobs: list[str] | None = None,
) -> dict[str, Any]:
    """Lint a matrix or a document containing one.

    expect_min_status:
      - ready: status must be ready|green|blocked (not draft)
      - green: status must be green (blocked allowed only if all rows blocked_external)
    """
    errors: list[dict[str, str]] = []
    matrix = extract_matrix(data)
    if matrix is None:
        if require_present:
            errors.append(
                _err(
                    "feature_completeness_matrix_missing",
                    "feature_completeness_matrix required",
                )
            )
        errors.extend(scan_functional_deferral_copy(prose_blobs))
        return {"ok": len(errors) == 0, "errors": errors, "status": None}

    if not isinstance(matrix, dict):
        return {
            "ok": False,
            "errors": [
                _err(
                    "feature_completeness_matrix_incomplete",
                    "matrix must be a mapping",
                )
            ],
            "status": None,
        }

    if matrix.get("schema") != SCHEMA:
        errors.append(
            _err(
                "feature_completeness_matrix_incomplete",
                f"schema must be {SCHEMA}",
            )
        )

    status = matrix.get("status")
    if status not in TOP_STATUS:
        errors.append(
            _err(
                "feature_completeness_matrix_incomplete",
                f"bad status: {status!r}",
            )
        )

    rows = matrix.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append(
            _err(
                "feature_completeness_matrix_incomplete",
                "rows must be a non-empty list",
            )
        )
        errors.extend(scan_functional_deferral_copy(prose_blobs))
        return {"ok": False, "errors": errors, "status": status}

    row_ids: list[str] = []
    task_keys_from_rows: set[str] = set()
    pending_or_incomplete = False
    all_blocked_external = True

    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"rows[{idx}] must be a mapping",
                )
            )
            pending_or_incomplete = True
            all_blocked_external = False
            continue

        rid = str(row.get("id") or "").strip()
        if not rid:
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"rows[{idx}].id required",
                )
            )
            pending_or_incomplete = True
        else:
            row_ids.append(rid)

        sot_ref = str(row.get("sot_ref") or "").strip()
        task_local_key = str(row.get("task_local_key") or "").strip()
        if not sot_ref:
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"rows[{idx}].sot_ref required",
                )
            )
            pending_or_incomplete = True
        if not task_local_key:
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"rows[{idx}].task_local_key required",
                )
            )
            pending_or_incomplete = True
        else:
            task_keys_from_rows.add(task_local_key)

        impl_raw = row.get("impl_status")
        if impl_raw in ("stub", "deferred_feature"):
            errors.append(
                _err(
                    "functional_residual_forbidden",
                    f"rows[{idx}].impl_status={impl_raw!r} is not allowed",
                )
            )
            pending_or_incomplete = True
            all_blocked_external = False
            impl = None
        elif impl_raw not in IMPL_STATUS:
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"rows[{idx}].impl_status illegal: {impl_raw!r}",
                )
            )
            pending_or_incomplete = True
            all_blocked_external = False
            impl = None
        else:
            impl = impl_raw
            if impl == "pending":
                pending_or_incomplete = True
                all_blocked_external = False
            elif impl != "blocked_external":
                all_blocked_external = False

        result = row.get("result")
        if result not in ROW_RESULT:
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"rows[{idx}].result illegal: {result!r}",
                )
            )
            pending_or_incomplete = True
        elif result == "pending":
            pending_or_incomplete = True

        if impl == "implemented":
            test_ref = str(row.get("test_ref") or "").strip()
            if not test_ref:
                errors.append(
                    _err(
                        "feature_completeness_matrix_incomplete",
                        f"rows[{idx}].test_ref required when implemented",
                    )
                )
                pending_or_incomplete = True

        if (
            impl == "blocked_external"
            and expect_min_status == "green"
            and result != "blocked_external"
        ):
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"rows[{idx}] blocked_external must have result blocked_external",
                )
            )

    if expect_min_status == "ready":
        if status == "draft":
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    "status must be ready|green|blocked for ready gate",
                )
            )
        # ready requires sot_ref + task_local_key on every row (already checked)

    if expect_min_status == "green":
        if status == "green":
            if pending_or_incomplete:
                errors.append(
                    _err(
                        "feature_completeness_overclaim_green",
                        "status green while rows pending/incomplete",
                    )
                )
            for idx, row in enumerate(rows):
                if not isinstance(row, dict):
                    continue
                impl = row.get("impl_status")
                result = row.get("result")
                if impl == "pending" or result == "pending":
                    errors.append(
                        _err(
                            "feature_completeness_overclaim_green",
                            f"rows[{idx}] still pending under status green",
                        )
                    )
                elif impl == "implemented" and result != "green":
                    if result != "blocked_external":
                        errors.append(
                            _err(
                                "feature_completeness_overclaim_green",
                                f"rows[{idx}] implemented but result={result!r}",
                            )
                        )
        elif status == "blocked":
            if not all_blocked_external:
                errors.append(
                    _err(
                        "feature_completeness_matrix_incomplete",
                        "status blocked only when every row is blocked_external",
                    )
                )
        else:
            errors.append(
                _err(
                    "feature_completeness_matrix_incomplete",
                    f"status must be green (or all-blocked) for green gate, got {status!r}",
                )
            )

    # Align with task_plan.tasks when provided
    tasks = task_plan_tasks
    if tasks is None and isinstance(data, dict):
        tasks = extract_task_plan_tasks(data)
    if tasks is not None:
        plan_keys: set[str] = set()
        for t in tasks:
            lk = str(t.get("local_key") or "").strip()
            if lk:
                plan_keys.add(lk)
            row_cover = t.get("feature_completeness_row_ids")
            if not isinstance(row_cover, list) or not row_cover:
                errors.append(
                    _err(
                        "feature_completeness_matrix_incomplete",
                        f"task {lk or t!r} must cover ≥1 matrix row "
                        "(feature_completeness_row_ids)",
                    )
                )
            else:
                for rid in row_cover:
                    if str(rid) not in row_ids:
                        errors.append(
                            _err(
                                "feature_completeness_matrix_incomplete",
                                f"task {lk} references unknown row id {rid!r}",
                            )
                        )
        for key in task_keys_from_rows:
            if key not in plan_keys:
                errors.append(
                    _err(
                        "feature_completeness_matrix_incomplete",
                        f"matrix task_local_key {key!r} missing from task_plan.tasks",
                    )
                )

    errors.extend(scan_functional_deferral_copy(prose_blobs))
    # Deduplicate identical codes+details
    seen: set[tuple[str, str]] = set()
    uniq: list[dict[str, str]] = []
    for e in errors:
        key = (e["code"], e["detail"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)

    return {"ok": len(uniq) == 0, "errors": uniq, "status": status}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="YAML/JSON matrix or Milestone Work doc")
    parser.add_argument(
        "--expect",
        choices=("present", "ready", "green"),
        default="present",
        help="Gate: present | ready | green",
    )
    parser.add_argument(
        "--prose",
        type=Path,
        action="append",
        default=[],
        help="Optional Delivery/notes file to scan for deferral copy (repeatable)",
    )
    args = parser.parse_args(argv)
    data = _load(args.path)
    expect_min = None if args.expect == "present" else args.expect
    blobs = [p.read_text(encoding="utf-8") for p in args.prose]
    result = lint_matrix(
        data,
        require_present=True,
        expect_min_status=expect_min,
        prose_blobs=blobs or None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
