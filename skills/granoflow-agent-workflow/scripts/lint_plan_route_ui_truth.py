#!/usr/bin/env python3
"""Lint Plan Route UI Truth anti-drift: full index review + will_change refs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

VALID_STATUS = frozenset(
    {
        "not_applicable",
        "missing",
        "checked_unchanged",
        "checked_will_change",
        "updated_on_delivery",
    }
)
VALID_DISPOSITION = frozenset({"unrelated", "unchanged", "will_change", "gap"})
RELATED_DISPOSITION = frozenset({"unchanged", "will_change", "gap"})
FACT_ID_RE = re.compile(r"^UIT-[a-z0-9]+(?:-[a-z0-9]+)*$")
ERROR_PRIORITY = (
    "card_change_plan_notice_missing",
    "route_ui_truth_will_change_without_verification",
    "route_ui_truth_check_missing",
    "route_ui_truth_lint_failed",
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


def _primary_code(errors: list[dict[str, str]]) -> str:
    codes = {item["code"] for item in errors}
    for code in ERROR_PRIORITY:
        if code in codes:
            return code
    return errors[0]["code"] if errors else "ok"


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if _nonempty_str(item)]


def _extract_index_fact_ids(snapshot: Any) -> set[str]:
    if not isinstance(snapshot, dict):
        return set()
    rows = snapshot.get("route_ui_truth_index")
    if not isinstance(rows, list):
        return set()
    result: set[str] = set()
    for row in rows:
        if isinstance(row, dict) and _nonempty_str(row.get("fact_id")):
            result.add(str(row["fact_id"]).strip())
    return result


def _notice_items(notice: Any) -> list[dict[str, Any]]:
    if not isinstance(notice, dict):
        return []
    items = notice.get("items")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _planned_card_writes(data: dict[str, Any]) -> bool:
    if data.get("review_card_writes_planned") is True:
        return True
    notice = data.get("card_change_plan_notice")
    if _notice_items(notice):
        return True
    checkpoint = data.get("card_checkpoint")
    if isinstance(checkpoint, dict):
        ops = checkpoint.get("operations")
        if isinstance(ops, dict):
            for key in ("created", "updated", "linked"):
                value = ops.get(key)
                if isinstance(value, list) and value:
                    return True
    return False


def _lint_plan_change_notice(
    data: dict[str, Any],
    *,
    will_change: list[str],
) -> list[dict[str, str]]:
    """Require user-visible Plan notice: itemized changes or one-line none."""
    errors: list[dict[str, str]] = []
    has_changes = bool(will_change) or _planned_card_writes(data)
    notice = data.get("card_change_plan_notice")
    items = _notice_items(notice)

    if not isinstance(notice, dict):
        errors.append(
            _err(
                "card_change_plan_notice_missing",
                "Plan requires card_change_plan_notice shown to the user "
                "(itemized changes, or none:true with one-line summary)",
            )
        )
        return errors

    if notice.get("emitted") is not True or notice.get("shown_to_user") is not True:
        errors.append(
            _err(
                "card_change_plan_notice_missing",
                "card_change_plan_notice must set emitted:true and "
                "shown_to_user:true after displaying the notice",
            )
        )

    if not has_changes:
        if notice.get("none") is not True:
            errors.append(
                _err(
                    "card_change_plan_notice_missing",
                    "when no card changes are planned, set none:true and "
                    "one-line summary (e.g. 本次迭代无卡片变更)",
                )
            )
        if not _nonempty_str(notice.get("summary")):
            errors.append(
                _err(
                    "card_change_plan_notice_missing",
                    "none:true Plan notice requires one-line summary only",
                )
            )
        if items:
            errors.append(
                _err(
                    "card_change_plan_notice_missing",
                    "none:true Plan notice must keep items: []",
                )
            )
        return errors

    if notice.get("none") is True:
        errors.append(
            _err(
                "card_change_plan_notice_missing",
                "planned card/UIT changes forbid none:true",
            )
        )

    if not items:
        errors.append(
            _err(
                "card_change_plan_notice_missing",
                "card_change_plan_notice.items must list every planned change",
            )
        )
        return errors

    noticed_fact_ids: set[str] = set()
    for index, item in enumerate(items):
        prefix = f"card_change_plan_notice.items[{index}]"
        if not _nonempty_str(item.get("summary")):
            errors.append(
                _err(
                    "card_change_plan_notice_missing",
                    f"{prefix}.summary must be a non-empty user-visible line",
                )
            )
        if not _nonempty_str(item.get("kind")):
            errors.append(
                _err(
                    "card_change_plan_notice_missing",
                    f"{prefix}.kind is required",
                )
            )
        if not _nonempty_str(item.get("action")):
            errors.append(
                _err(
                    "card_change_plan_notice_missing",
                    f"{prefix}.action is required",
                )
            )
        fact_id = str(item.get("fact_id") or "").strip()
        if fact_id:
            noticed_fact_ids.add(fact_id)
        kind = str(item.get("kind") or "").strip()
        if kind == "route_ui_truth" and not fact_id:
            errors.append(
                _err(
                    "card_change_plan_notice_missing",
                    f"{prefix}: route_ui_truth items require fact_id",
                )
            )

    missing = sorted(set(will_change) - noticed_fact_ids)
    if missing:
        errors.append(
            _err(
                "card_change_plan_notice_missing",
                "Plan notice missing will_change fact_id(s): " + ", ".join(missing),
            )
        )
    return errors


def lint_plan_route_ui_truth(
    data: Any,
    *,
    snapshot: Any | None = None,
    gate_required: bool = True,
) -> dict[str, Any]:
    """Validate Route UI Truth Plan fields on Task Work-shaped data."""
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "route_ui_truth_lint_failed",
            "errors": [_err("route_ui_truth_lint_failed", "task work must be an object")],
        }

    if not gate_required:
        return {"ok": True, "code": "ok", "errors": [], "gate": "not_applicable"}

    status_raw = data.get("route_ui_truth_check_status")
    status = str(status_raw).strip() if _nonempty_str(status_raw) else ""
    review = data.get("route_ui_truth_index_review")
    fact_ids = _as_str_list(data.get("route_ui_truth_fact_ids"))
    will_change = _as_str_list(data.get("route_ui_truth_will_change"))

    if status == "" or status == "missing":
        errors.append(
            _err(
                "route_ui_truth_check_missing",
                "route_ui_truth_check_status must be set "
                "(not_applicable|checked_unchanged|checked_will_change|"
                "updated_on_delivery)",
            )
        )
        return {
            "ok": False,
            "code": _primary_code(errors),
            "errors": errors,
            "gate": "blocked",
        }

    if status not in VALID_STATUS:
        errors.append(
            _err(
                "route_ui_truth_check_missing",
                f"invalid route_ui_truth_check_status: {status!r}",
            )
        )

    if status == "not_applicable":
        if review is None:
            review = []
        if not isinstance(review, list):
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    "route_ui_truth_index_review must be a list when " "status is not_applicable",
                )
            )
        elif review:
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    "not_applicable requires route_ui_truth_index_review: []",
                )
            )
        if not _nonempty_str(data.get("route_ui_truth_not_applicable_reason")):
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    "not_applicable requires route_ui_truth_not_applicable_reason",
                )
            )
        errors.extend(_lint_plan_change_notice(data, will_change=[]))
        return {
            "ok": not errors,
            "code": _primary_code(errors) if errors else "ok",
            "errors": errors,
            "gate": "not_applicable" if not errors else "blocked",
        }

    if not isinstance(review, list):
        errors.append(
            _err(
                "route_ui_truth_check_missing",
                "route_ui_truth_index_review must be a list",
            )
        )
        return {
            "ok": False,
            "code": _primary_code(errors),
            "errors": errors,
            "gate": "blocked",
        }

    review_fact_ids: set[str] = set()
    derived_related: list[str] = []
    derived_will_change: list[str] = []

    for index, row in enumerate(review):
        prefix = f"route_ui_truth_index_review[{index}]"
        if not isinstance(row, dict):
            errors.append(_err("route_ui_truth_check_missing", f"{prefix} must be an object"))
            continue
        fact_id = str(row.get("fact_id") or "").strip()
        if not fact_id or not FACT_ID_RE.match(fact_id):
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    f"{prefix}.fact_id must match UIT-<slug>",
                )
            )
            continue
        if fact_id in review_fact_ids:
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    f"duplicate fact_id in index_review: {fact_id}",
                )
            )
        review_fact_ids.add(fact_id)

        related = row.get("related")
        if related is not True and related is not False:
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    f"{prefix}.related must be true or false",
                )
            )
            continue

        disposition = str(row.get("disposition") or "").strip()
        if disposition not in VALID_DISPOSITION:
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    f"{prefix}.disposition must be " "unrelated|unchanged|will_change|gap",
                )
            )
            continue

        if related is True and disposition not in RELATED_DISPOSITION:
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    f"{prefix}: related:true requires disposition " "unchanged|will_change|gap",
                )
            )
        if related is False and disposition != "unrelated":
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    f"{prefix}: related:false requires disposition unrelated",
                )
            )

        if related is True:
            derived_related.append(fact_id)
            if disposition == "will_change":
                derived_will_change.append(fact_id)
                refs = _as_str_list(row.get("verification_refs"))
                if not refs:
                    errors.append(
                        _err(
                            "route_ui_truth_will_change_without_verification",
                            f"{prefix} ({fact_id}): will_change requires "
                            "non-empty verification_refs",
                        )
                    )

    if snapshot is not None:
        index_ids = _extract_index_fact_ids(snapshot)
        missing = sorted(index_ids - review_fact_ids)
        if missing:
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    "index_review missing snapshot fact_id(s): " + ", ".join(missing),
                )
            )

    if set(fact_ids) != set(derived_related):
        errors.append(
            _err(
                "route_ui_truth_check_missing",
                "route_ui_truth_fact_ids must equal related:true fact_ids "
                f"(got {fact_ids!r}, expected {derived_related!r})",
            )
        )

    if set(will_change) != set(derived_will_change):
        errors.append(
            _err(
                "route_ui_truth_check_missing",
                "route_ui_truth_will_change must equal disposition=will_change "
                f"rows (got {will_change!r}, expected {derived_will_change!r})",
            )
        )

    for fact_id in will_change:
        if fact_id not in fact_ids:
            errors.append(
                _err(
                    "route_ui_truth_check_missing",
                    f"will_change fact_id not in route_ui_truth_fact_ids: {fact_id}",
                )
            )

    if status == "checked_unchanged" and derived_will_change:
        errors.append(
            _err(
                "route_ui_truth_check_missing",
                "checked_unchanged forbids will_change rows",
            )
        )
    if status == "checked_will_change" and not derived_will_change:
        errors.append(
            _err(
                "route_ui_truth_check_missing",
                "checked_will_change requires at least one will_change row",
            )
        )

    errors.extend(_lint_plan_change_notice(data, will_change=derived_will_change))

    return {
        "ok": not errors,
        "code": _primary_code(errors) if errors else "ok",
        "errors": errors,
        "gate": "passed" if not errors else "blocked",
        "related_fact_ids": derived_related,
        "will_change_fact_ids": derived_will_change,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task_work",
        type=Path,
        help="Task Work YAML/JSON with route_ui_truth_* Plan fields",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Optional project_snapshot.yaml to require full index coverage",
    )
    parser.add_argument(
        "--skip-gate",
        action="store_true",
        help="Skip lint when Plan Design Gate does not apply",
    )
    args = parser.parse_args(argv)
    try:
        snapshot = _load(args.snapshot) if args.snapshot is not None else None
        result = lint_plan_route_ui_truth(
            _load(args.task_work),
            snapshot=snapshot,
            gate_required=not args.skip_gate,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "route_ui_truth_lint_failed",
            "errors": [_err("route_ui_truth_lint_failed", str(error))],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
