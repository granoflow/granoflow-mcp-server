#!/usr/bin/env python3
"""Lint Unattended Card-Truth Batch Gate readiness (RB/UIT + field-media)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ERROR_PRIORITY = (
    "card_truth_batch_gate_blocked",
    "card_truth_batch_gate_missing",
    "card_truth_ready_lint_failed",
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


def _index_rows(snapshot: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(snapshot, dict):
        return []
    rows = snapshot.get(key)
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _valid_index_row(row: dict[str, Any]) -> bool:
    return _nonempty_str(row.get("fact_id")) and _nonempty_str(row.get("note_id"))


def _field_media_available(capabilities: Any) -> bool | None:
    if capabilities is None:
        return None
    root = capabilities
    if isinstance(root, dict) and isinstance(root.get("data"), dict):
        root = root["data"]
    if not isinstance(root, dict):
        return False
    resources = root.get("resources")
    if not isinstance(resources, dict):
        return False
    actions = resources.get("review-note")
    if not isinstance(actions, list):
        return False
    return "field-media.upload" in {str(item) for item in actions}


def lint_unattended_card_truth_ready(
    *,
    snapshot: Any,
    gate: Any | None = None,
    capabilities: Any | None = None,
    require_uit_index: bool = False,
    require_rb_index: bool = False,
    require_field_media: bool = False,
    require_gate_passed: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    rb_rows = _index_rows(snapshot, "reality_boundary_index")
    uit_rows = _index_rows(snapshot, "route_ui_truth_index")
    rb_valid = [row for row in rb_rows if _valid_index_row(row)]
    uit_valid = [row for row in uit_rows if _valid_index_row(row)]

    field_media = _field_media_available(capabilities)

    if require_rb_index and not rb_valid:
        errors.append(
            _err(
                "card_truth_batch_gate_blocked",
                "require-rb-index but reality_boundary_index has no note_id rows",
            )
        )
    if require_uit_index and not uit_valid:
        errors.append(
            _err(
                "card_truth_batch_gate_blocked",
                "require-uit-index but route_ui_truth_index has no note_id rows "
                "(run interactive UIT seed batch first)",
            )
        )
    if require_field_media:
        if field_media is None:
            errors.append(
                _err(
                    "card_truth_batch_gate_blocked",
                    "require-field-media but capabilities were not provided",
                )
            )
        elif field_media is False:
            errors.append(
                _err(
                    "card_truth_batch_gate_blocked",
                    "App does not advertise review-note: field-media.upload "
                    "(rebuild/restart Granoflow)",
                )
            )

    gate_status = ""
    if isinstance(gate, dict):
        gate_status = str(gate.get("status") or "").strip()
    if require_gate_passed:
        if gate_status == "":
            errors.append(
                _err(
                    "card_truth_batch_gate_missing",
                    "card_truth_batch_gate.status required before unattended "
                    "whole-project/final-delivery",
                )
            )
        elif gate_status not in {"passed", "not_applicable"}:
            errors.append(
                _err(
                    "card_truth_batch_gate_blocked",
                    f"card_truth_batch_gate.status must be passed|not_applicable, "
                    f"got {gate_status!r}",
                )
            )

    # Invalid placeholder rows (e.g. note_id: REPLACE) fail when present.
    for label, rows in (
        ("reality_boundary_index", rb_rows),
        ("route_ui_truth_index", uit_rows),
    ):
        for row in rows:
            note_id = str(row.get("note_id") or "").strip()
            if note_id.upper() == "REPLACE" or note_id.lower() == "pending":
                errors.append(
                    _err(
                        "card_truth_batch_gate_blocked",
                        f"{label} fact_id={row.get('fact_id')!r} has placeholder note_id",
                    )
                )

    return {
        "ok": not errors,
        "code": _primary_code(errors) if errors else "ok",
        "errors": errors,
        "rb_index_count": len(rb_valid),
        "uit_index_count": len(uit_valid),
        "field_media_capability": (
            "available"
            if field_media is True
            else ("missing" if field_media is False else "unknown")
        ),
        "gate_status": gate_status or None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument(
        "--gate",
        type=Path,
        default=None,
        help="YAML/JSON with card_truth_batch_gate object (or whole task-work)",
    )
    parser.add_argument(
        "--capabilities",
        type=Path,
        default=None,
        help="JSON dump of GET /v1/capabilities",
    )
    parser.add_argument("--require-uit-index", action="store_true")
    parser.add_argument("--require-rb-index", action="store_true")
    parser.add_argument("--require-field-media", action="store_true")
    parser.add_argument("--require-gate-passed", action="store_true")
    args = parser.parse_args(argv)

    try:
        snapshot = _load(args.snapshot)
        gate_doc = _load(args.gate) if args.gate is not None else None
        gate = None
        if isinstance(gate_doc, dict):
            gate = gate_doc.get("card_truth_batch_gate", gate_doc)
        capabilities = _load(args.capabilities) if args.capabilities is not None else None
        result = lint_unattended_card_truth_ready(
            snapshot=snapshot,
            gate=gate,
            capabilities=capabilities,
            require_uit_index=args.require_uit_index,
            require_rb_index=args.require_rb_index,
            require_field_media=args.require_field_media,
            require_gate_passed=args.require_gate_passed,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "card_truth_ready_lint_failed",
            "errors": [_err("card_truth_ready_lint_failed", str(error))],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
