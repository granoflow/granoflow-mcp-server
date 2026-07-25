#!/usr/bin/env python3
"""Lint Delivery/implementation card-change notices (RB and all review cards)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ERROR_PRIORITY = (
    "card_change_delivery_notice_missing",
    "reality_boundary_delivery_stale",
    "route_ui_truth_delivery_stale",
    "card_change_delivery_lint_failed",
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


def _notice_items(notice: Any) -> list[dict[str, Any]]:
    if not isinstance(notice, dict):
        return []
    items = notice.get("items")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _applied_card_writes(data: dict[str, Any]) -> bool:
    if data.get("review_card_writes_applied") is True:
        return True
    if data.get("reality_boundary_check_status") == "updated_on_delivery":
        return True
    if data.get("route_ui_truth_check_status") == "updated_on_delivery":
        return True
    notice = data.get("card_change_delivery_notice")
    if isinstance(notice, dict) and notice.get("cards_updated") is True:
        return True
    checkpoint = data.get("card_checkpoint")
    if isinstance(checkpoint, dict):
        if checkpoint.get("change_summary") == "changed":
            return True
        ops = checkpoint.get("operations")
        if isinstance(ops, dict):
            for key in ("created", "updated"):
                value = ops.get(key)
                if isinstance(value, list) and value:
                    return True
        applied = checkpoint.get("applied_operation_ids")
        if isinstance(applied, list) and applied:
            return True
    return False


def lint_delivery_card_change_notice(data: Any) -> dict[str, Any]:
    """Require user-visible Delivery notice when any card/RB write applied."""
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "code": "card_change_delivery_lint_failed",
            "errors": [_err("card_change_delivery_lint_failed", "task work must be an object")],
        }

    rb_will_change = _as_str_list(data.get("reality_boundary_will_change"))
    uit_will_change = _as_str_list(data.get("route_ui_truth_will_change"))
    will_change = sorted(set(rb_will_change) | set(uit_will_change))
    has_changes = bool(will_change) or _applied_card_writes(data)
    notice = data.get("card_change_delivery_notice")
    items = _notice_items(notice)

    if not isinstance(notice, dict):
        errors.append(
            _err(
                "card_change_delivery_notice_missing",
                "Delivery requires card_change_delivery_notice shown to the "
                "user (itemized updates, or none:true with one-line summary)",
            )
        )
        return {
            "ok": False,
            "code": _primary_code(errors),
            "errors": errors,
            "gate": "blocked",
        }

    if notice.get("emitted") is not True or notice.get("shown_to_user") is not True:
        errors.append(
            _err(
                "card_change_delivery_notice_missing",
                "card_change_delivery_notice must set emitted:true and "
                "shown_to_user:true after displaying the notice",
            )
        )

    if not has_changes:
        if notice.get("none") is not True:
            errors.append(
                _err(
                    "card_change_delivery_notice_missing",
                    "when no cards were updated, set none:true and one-line "
                    "summary (e.g. 本次实施无卡片变更)",
                )
            )
        if not _nonempty_str(notice.get("summary")):
            errors.append(
                _err(
                    "card_change_delivery_notice_missing",
                    "none:true Delivery notice requires one-line summary only",
                )
            )
        if notice.get("cards_updated") is True:
            errors.append(
                _err(
                    "card_change_delivery_notice_missing",
                    "none:true Delivery notice must set cards_updated:false",
                )
            )
        if items:
            errors.append(
                _err(
                    "card_change_delivery_notice_missing",
                    "none:true Delivery notice must keep items: []",
                )
            )
        return {
            "ok": not errors,
            "code": _primary_code(errors) if errors else "ok",
            "errors": errors,
            "gate": "passed" if not errors else "blocked",
        }

    if notice.get("none") is True:
        errors.append(
            _err(
                "card_change_delivery_notice_missing",
                "applied card/RB updates forbid none:true",
            )
        )

    if notice.get("cards_updated") is not True:
        errors.append(
            _err(
                "card_change_delivery_notice_missing",
                "card_change_delivery_notice.cards_updated must be true when "
                "cards/Notes were written",
            )
        )

    if not items:
        errors.append(
            _err(
                "card_change_delivery_notice_missing",
                "card_change_delivery_notice.items must list every applied change",
            )
        )
    else:
        noticed_fact_ids: set[str] = set()
        for index, item in enumerate(items):
            prefix = f"card_change_delivery_notice.items[{index}]"
            if not _nonempty_str(item.get("summary")):
                errors.append(
                    _err(
                        "card_change_delivery_notice_missing",
                        f"{prefix}.summary must be a non-empty user-visible line",
                    )
                )
            if not _nonempty_str(item.get("kind")):
                errors.append(
                    _err(
                        "card_change_delivery_notice_missing",
                        f"{prefix}.kind is required",
                    )
                )
            fact_id = str(item.get("fact_id") or "").strip()
            if fact_id:
                noticed_fact_ids.add(fact_id)
            kind = str(item.get("kind") or "").strip()
            if kind in {"reality_boundary", "route_ui_truth"} and not fact_id:
                errors.append(
                    _err(
                        "card_change_delivery_notice_missing",
                        f"{prefix}: {kind} items require fact_id",
                    )
                )
            card_ids = item.get("card_ids")
            if kind in {"reality_boundary", "route_ui_truth"} and not (
                isinstance(card_ids, list) and card_ids
            ):
                errors.append(
                    _err(
                        "card_change_delivery_notice_missing",
                        f"{prefix}: {kind} items require card_ids after update",
                    )
                )

        missing = sorted(set(will_change) - noticed_fact_ids)
        if missing:
            errors.append(
                _err(
                    "card_change_delivery_notice_missing",
                    "Delivery notice missing will_change fact_id(s): " + ", ".join(missing),
                )
            )

    rb_status = str(data.get("reality_boundary_check_status") or "").strip()
    if rb_will_change and rb_status not in {"updated_on_delivery"}:
        errors.append(
            _err(
                "reality_boundary_delivery_stale",
                "will_change requires reality_boundary_check_status "
                "updated_on_delivery after card/index updates",
            )
        )

    uit_status = str(data.get("route_ui_truth_check_status") or "").strip()
    if uit_will_change and uit_status not in {"updated_on_delivery"}:
        errors.append(
            _err(
                "route_ui_truth_delivery_stale",
                "will_change requires route_ui_truth_check_status "
                "updated_on_delivery after card/index updates",
            )
        )

    return {
        "ok": not errors,
        "code": _primary_code(errors) if errors else "ok",
        "errors": errors,
        "gate": "passed" if not errors else "blocked",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task_work",
        type=Path,
        help="Task Work YAML/JSON with Delivery card-change notice fields",
    )
    args = parser.parse_args(argv)
    try:
        result = lint_delivery_card_change_notice(_load(args.task_work))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "card_change_delivery_lint_failed",
            "errors": [_err("card_change_delivery_lint_failed", str(error))],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
