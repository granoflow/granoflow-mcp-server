#!/usr/bin/env python3
"""Lint prototype coverage ledgers: doc, HTML surface, widget reuse, plan truth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

COVERAGE_SCHEMA = "granoflow_prototype_doc_coverage_v1"
HTML_COVERAGE_SCHEMA = "granoflow_prototype_html_coverage_v1"
WIDGET_REUSE_SCHEMA = "granoflow_prototype_widget_reuse_v1"
PLAN_TRUTH_SCHEMA = "granoflow_prototype_plan_truth_v1"
VALID_COVERAGE_STATUS = frozenset({"not_applicable", "pending", "complete"})
VALID_SURFACE_KIND = frozenset(
    {"page", "dialog", "modal", "sheet", "popover", "toast", "panel", "other"}
)
VALID_SURFACE_COVERAGE = frozenset({"covered", "missing"})
VALID_WIDGET_ACTION = frozenset({"reused", "new_role"})
VALID_ROW_KIND = frozenset({"page", "control", "state", "copy", "flow"})
VALID_ROW_COVERAGE = frozenset({"covered", "missing", "conflict"})
VALID_PLAN_STATUS = frozenset({"not_applicable", "aligned", "conflict"})
VALID_USER_RESOLUTION = frozenset({"not_applicable", "pending", "accepted_doc_update"})


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


def _extract(data: Any, key: str) -> Any:
    if not isinstance(data, dict):
        return None
    if key in data:
        return data.get(key)
    if data.get("schema") in {
        COVERAGE_SCHEMA,
        HTML_COVERAGE_SCHEMA,
        WIDGET_REUSE_SCHEMA,
        PLAN_TRUTH_SCHEMA,
    }:
        return data
    return None


def lint_prototype_doc_coverage(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    block = _extract(data, "prototype_doc_coverage")
    if block is None:
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": [
                _err(
                    "prototype_doc_coverage_lint_failed",
                    "prototype_doc_coverage object required",
                )
            ],
        }
    if not isinstance(block, dict):
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": [
                _err(
                    "prototype_doc_coverage_lint_failed",
                    "prototype_doc_coverage must be an object",
                )
            ],
        }

    if block.get("contract_loaded") is not True:
        errors.append(
            _err(
                "prototype_doc_coverage_unread",
                "contract_loaded must be true",
            )
        )

    status = block.get("status")
    if status not in VALID_COVERAGE_STATUS:
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "status must be not_applicable|pending|complete",
            )
        )
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": errors,
        }

    if status == "not_applicable":
        return {
            "ok": not errors,
            "code": "ok" if not errors else "prototype_doc_coverage_lint_failed",
            "errors": errors,
        }

    if not _nonempty_str(block.get("prototype_id")):
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "prototype_id required when coverage applies",
            )
        )

    rows = block.get("rows")
    if not isinstance(rows, list):
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "rows must be a list",
            )
        )
        rows = []

    if status == "complete" and not rows:
        errors.append(
            _err(
                "prototype_doc_coverage_incomplete",
                "status=complete requires non-empty rows when coverage applies",
            )
        )

    for index, row in enumerate(rows):
        prefix = f"rows[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix} must be object",
                )
            )
            continue
        if not _nonempty_str(row.get("page_id")):
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.page_id required",
                )
            )
        kind = row.get("kind")
        if kind not in VALID_ROW_KIND:
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.kind must be page|control|state|copy|flow",
                )
            )
        coverage = row.get("coverage")
        if coverage not in VALID_ROW_COVERAGE:
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.coverage must be covered|missing|conflict",
                )
            )
        elif status == "complete":
            if coverage == "missing":
                errors.append(
                    _err(
                        "prototype_doc_coverage_gap",
                        f"{prefix}.coverage=missing forbidden when status=complete",
                    )
                )
            if coverage == "conflict":
                errors.append(
                    _err(
                        "prototype_doc_conflict",
                        f"{prefix}.coverage=conflict forbidden when status=complete",
                    )
                )
        if not _nonempty_str(row.get("task_work_locus")):
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.task_work_locus required",
                )
            )
        if not _nonempty_str(row.get("project_work_locus")):
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.project_work_locus required "
                    "(use not_applicable:<reason> when Project Work out of scope)",
                )
            )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "prototype_doc_coverage_lint_failed",
        "errors": errors,
    }


def _catalog_roles(catalog: dict[str, Any]) -> dict[str, str]:
    """Map role/id -> canonical widget id from widgets.yaml."""
    roles: dict[str, str] = {}
    widgets = catalog.get("widgets")
    if not isinstance(widgets, list):
        return roles
    for item in widgets:
        if not isinstance(item, dict):
            continue
        widget_id = item.get("id")
        if not isinstance(widget_id, str) or not widget_id.strip():
            continue
        widget_id = widget_id.strip()
        roles[widget_id] = widget_id
        role = item.get("role")
        if isinstance(role, str) and role.strip():
            roles[role.strip()] = widget_id
    return roles


def lint_prototype_html_coverage(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    block = _extract(data, "prototype_html_coverage")
    if block is None:
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": [
                _err(
                    "prototype_html_coverage_unread",
                    "prototype_html_coverage object required when UI applies",
                )
            ],
        }
    if not isinstance(block, dict):
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": [
                _err(
                    "prototype_doc_coverage_lint_failed",
                    "prototype_html_coverage must be an object",
                )
            ],
        }

    if block.get("contract_loaded") is not True:
        errors.append(
            _err(
                "prototype_html_coverage_unread",
                "contract_loaded must be true",
            )
        )

    status = block.get("status")
    if status not in VALID_COVERAGE_STATUS:
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "status must be not_applicable|pending|complete",
            )
        )
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": errors,
        }

    if status == "not_applicable":
        return {
            "ok": not errors,
            "code": "ok" if not errors else "prototype_doc_coverage_lint_failed",
            "errors": errors,
        }

    if not _nonempty_str(block.get("prototype_id")):
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "prototype_id required when html coverage applies",
            )
        )

    surfaces = block.get("surfaces")
    if not isinstance(surfaces, list):
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "surfaces must be a list",
            )
        )
        surfaces = []

    if status == "complete" and not surfaces:
        errors.append(
            _err(
                "prototype_html_coverage_incomplete",
                "status=complete requires non-empty surfaces when UI applies",
            )
        )

    gap_ids: list[str] = []
    for index, row in enumerate(surfaces):
        prefix = f"surfaces[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix} must be object",
                )
            )
            continue
        surface_id = row.get("surface_id")
        if not isinstance(surface_id, str) or not surface_id.strip():
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.surface_id required",
                )
            )
            surface_id = f"<index:{index}>"
        else:
            surface_id = surface_id.strip()
        kind = row.get("kind")
        if kind not in VALID_SURFACE_KIND:
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.kind must be page|dialog|modal|sheet|popover|toast|panel|other",
                )
            )
        coverage = row.get("coverage")
        if coverage not in VALID_SURFACE_COVERAGE:
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.coverage must be covered|missing",
                )
            )
        elif status == "complete":
            html_ref = row.get("html_prototype_ref")
            if coverage == "missing" or not _nonempty_str(html_ref):
                gap_ids.append(surface_id)
                errors.append(
                    _err(
                        "prototype_html_coverage_gap",
                        f"{prefix} surface_id={surface_id}: missing high-fidelity HTML prototype",
                    )
                )

    if status == "complete" and gap_ids:
        errors.append(
            _err(
                "prototype_html_coverage_gap",
                "gaps: " + ", ".join(gap_ids),
            )
        )

    ok = not errors
    primary = "ok"
    if not ok:
        codes = {e["code"] for e in errors}
        if "prototype_html_coverage_gap" in codes:
            primary = "prototype_html_coverage_gap"
        elif "prototype_html_coverage_incomplete" in codes:
            primary = "prototype_html_coverage_incomplete"
        elif "prototype_html_coverage_unread" in codes:
            primary = "prototype_html_coverage_unread"
        else:
            primary = "prototype_doc_coverage_lint_failed"
    return {"ok": ok, "code": primary, "errors": errors, "gaps": gap_ids}


def lint_prototype_widget_reuse(
    data: Any,
    widgets_catalog: Any | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    block = _extract(data, "prototype_widget_reuse")
    if block is None:
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": [
                _err(
                    "prototype_widget_reuse_unread",
                    "prototype_widget_reuse object required when widgets.yaml exists",
                )
            ],
        }
    if not isinstance(block, dict):
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": [
                _err(
                    "prototype_doc_coverage_lint_failed",
                    "prototype_widget_reuse must be an object",
                )
            ],
        }

    if block.get("contract_loaded") is not True:
        errors.append(
            _err(
                "prototype_widget_reuse_unread",
                "contract_loaded must be true",
            )
        )

    status = block.get("status")
    if status not in VALID_COVERAGE_STATUS:
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "status must be not_applicable|pending|complete",
            )
        )
        return {
            "ok": False,
            "code": "prototype_doc_coverage_lint_failed",
            "errors": errors,
        }

    if status == "not_applicable":
        return {
            "ok": not errors,
            "code": "ok" if not errors else "prototype_doc_coverage_lint_failed",
            "errors": errors,
        }

    declarations = block.get("declarations")
    if not isinstance(declarations, list):
        errors.append(
            _err(
                "prototype_doc_coverage_lint_failed",
                "declarations must be a list",
            )
        )
        declarations = []

    catalog_block = widgets_catalog
    if catalog_block is None and isinstance(data, dict):
        catalog_block = data.get("widgets_catalog")
    roles: dict[str, str] = {}
    if isinstance(catalog_block, dict):
        roles = _catalog_roles(catalog_block)

    role_to_widget: dict[str, str] = {}
    for index, row in enumerate(declarations):
        prefix = f"declarations[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix} must be object",
                )
            )
            continue
        role = row.get("role")
        widget_id = row.get("widget_id")
        action = row.get("action")
        if not isinstance(role, str) or not role.strip():
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.role required",
                )
            )
            continue
        role = role.strip()
        if not isinstance(widget_id, str) or not widget_id.strip():
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.widget_id required",
                )
            )
            continue
        widget_id = widget_id.strip()
        if action not in VALID_WIDGET_ACTION:
            errors.append(
                _err(
                    "prototype_doc_coverage_lint_failed",
                    f"{prefix}.action must be reused|new_role",
                )
            )
            continue

        if role in role_to_widget and role_to_widget[role] != widget_id:
            errors.append(
                _err(
                    "widget_reuse_required",
                    f"{prefix}: near-duplicate role={role} widget_ids "
                    f"{role_to_widget[role]!r} vs {widget_id!r}",
                )
            )
        else:
            role_to_widget[role] = widget_id

        if roles and role in roles:
            expected = roles[role]
            if action == "new_role" or widget_id != expected:
                rationale = row.get("rationale")
                if action == "new_role" or not _nonempty_str(rationale):
                    errors.append(
                        _err(
                            "widget_reuse_required",
                            f"{prefix}: role={role} must reuse catalog widget "
                            f"{expected!r} (got {widget_id!r}, action={action})",
                        )
                    )
        elif widget_id in roles and widget_id != roles[widget_id]:
            errors.append(
                _err(
                    "widget_reuse_required",
                    f"{prefix}: widget_id={widget_id!r} must match catalog id "
                    f"{roles[widget_id]!r} for role={role}",
                )
            )

    if status == "complete" and roles and not declarations:
        errors.append(
            _err(
                "widget_reuse_required",
                "status=complete requires declarations when widgets catalog exists",
            )
        )

    ok = not errors
    primary = "ok"
    if not ok:
        codes = {e["code"] for e in errors}
        if "widget_reuse_required" in codes:
            primary = "widget_reuse_required"
        elif "prototype_widget_reuse_unread" in codes:
            primary = "prototype_widget_reuse_unread"
        else:
            primary = "prototype_doc_coverage_lint_failed"
    return {"ok": ok, "code": primary, "errors": errors}


def lint_prototype_plan_truth(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    block = _extract(data, "prototype_plan_truth")
    if block is None:
        return {
            "ok": False,
            "code": "prototype_plan_truth_conflict",
            "errors": [
                _err(
                    "prototype_plan_truth_conflict",
                    "prototype_plan_truth object required when Plan reviews UI prototype",
                )
            ],
        }
    if not isinstance(block, dict):
        return {
            "ok": False,
            "code": "prototype_plan_truth_conflict",
            "errors": [
                _err(
                    "prototype_plan_truth_conflict",
                    "prototype_plan_truth must be an object",
                )
            ],
        }

    if block.get("contract_loaded") is not True:
        errors.append(
            _err(
                "prototype_doc_coverage_unread",
                "prototype_plan_truth.contract_loaded must be true",
            )
        )

    status = block.get("status")
    if status not in VALID_PLAN_STATUS:
        errors.append(
            _err(
                "prototype_plan_truth_conflict",
                "status must be not_applicable|aligned|conflict",
            )
        )
        return {
            "ok": False,
            "code": "prototype_plan_truth_conflict",
            "errors": errors,
        }

    if status == "not_applicable":
        return {
            "ok": not errors,
            "code": "ok" if not errors else "prototype_plan_truth_conflict",
            "errors": errors,
        }

    if block.get("prototype_is_source_of_truth") is not True:
        errors.append(
            _err(
                "prototype_plan_truth_sot_invalid",
                "prototype_is_source_of_truth must be true",
            )
        )

    conflicts = block.get("conflicts")
    if conflicts is None:
        conflicts = []
    if not isinstance(conflicts, list):
        errors.append(
            _err(
                "prototype_plan_truth_conflict",
                "conflicts must be a list",
            )
        )
        conflicts = []

    if status == "aligned" and conflicts:
        errors.append(
            _err(
                "prototype_plan_truth_conflict",
                "status=aligned requires empty conflicts",
            )
        )
    if status == "conflict" and not conflicts:
        errors.append(
            _err(
                "prototype_plan_truth_conflict",
                "status=conflict requires non-empty conflicts",
            )
        )

    for index, row in enumerate(conflicts):
        prefix = f"conflicts[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "prototype_plan_truth_conflict",
                    f"{prefix} must be object",
                )
            )
            continue
        for key in ("page_id", "field", "prototype_says", "task_work_says", "recommendation"):
            if not _nonempty_str(row.get(key)):
                errors.append(
                    _err(
                        "prototype_plan_truth_conflict",
                        f"{prefix}.{key} required",
                    )
                )

    resolution = block.get("user_resolution")
    if resolution not in VALID_USER_RESOLUTION:
        errors.append(
            _err(
                "prototype_plan_truth_conflict",
                "user_resolution must be not_applicable|pending|accepted_doc_update",
            )
        )

    if status == "aligned":
        if resolution not in {None, "not_applicable"}:
            errors.append(
                _err(
                    "prototype_plan_truth_conflict",
                    "status=aligned requires user_resolution=not_applicable",
                )
            )
    elif status == "conflict":
        if block.get("user_notified") is not True:
            errors.append(
                _err(
                    "prototype_plan_truth_unnotified",
                    "user_notified must be true when status=conflict",
                )
            )
        if resolution == "pending":
            errors.append(
                _err(
                    "prototype_plan_truth_conflict",
                    "user_resolution=pending blocks Plan Design Gate passed",
                )
            )
        elif resolution == "accepted_doc_update":
            if block.get("task_work_updated") is not True:
                errors.append(
                    _err(
                        "prototype_plan_truth_docs_stale",
                        "task_work_updated must be true after accepted_doc_update",
                    )
                )
            pw = block.get("project_work_updated")
            if pw is not True and pw != "not_applicable":
                errors.append(
                    _err(
                        "prototype_plan_truth_docs_stale",
                        "project_work_updated must be true|not_applicable "
                        "after accepted_doc_update",
                    )
                )
    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "prototype_plan_truth_conflict",
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        choices=("coverage", "html_coverage", "widget_reuse", "plan_truth"),
        required=True,
        help="Which ledger to lint",
    )
    parser.add_argument("path", type=Path, help="YAML/JSON ledger path")
    parser.add_argument(
        "--widgets",
        type=Path,
        default=None,
        help="Project widgets.yaml for --kind widget_reuse cross-check",
    )
    args = parser.parse_args(argv)
    data = _load(args.path)
    widgets_catalog = _load(args.widgets) if args.widgets else None
    if args.kind == "coverage":
        result = lint_prototype_doc_coverage(data)
    elif args.kind == "html_coverage":
        result = lint_prototype_html_coverage(data)
    elif args.kind == "widget_reuse":
        result = lint_prototype_widget_reuse(data, widgets_catalog)
    else:
        result = lint_prototype_plan_truth(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
