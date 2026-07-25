#!/usr/bin/env python3
"""Lint Delivery milestone_plan_pack_reconcile vs accepted Plan pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_milestone_plan_pack_reconcile_v1"
SECTION_KEYS = (
    "user_copy",
    "data_structures",
    "flowcharts",
    "uml_diagrams",
    "test_cases",
)
VALID_RECONCILE_STATUS = frozenset({"pending", "complete"})
VALID_SECTION_STATUS = frozenset({"matched", "drifted", "n_a"})
ACCEPTED_PACK_STATUS = frozenset({"accepted"})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end < 0:
            raise ValueError("YAML frontmatter closing --- missing")
        fm = text[3:end].strip("\n")
        body = text[end + 4 :]
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(fm) or {}
        except ImportError:
            data = json.loads(fm)
        if not isinstance(data, dict):
            raise ValueError("frontmatter must be a mapping")
        data = dict(data)
        data.setdefault("body_markdown", body)
        return data
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ImportError:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("document root must be an object")
    return data


def _extract_reconcile(data: dict[str, Any]) -> Any:
    if "milestone_plan_pack_reconcile" in data:
        return data.get("milestone_plan_pack_reconcile")
    if data.get("schema") == SCHEMA:
        return data
    return None


def lint_milestone_plan_pack_delivery_reconcile(
    delivery_path: Path,
    pack_path: Path,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    try:
        delivery = _load(delivery_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "code": "milestone_plan_acceptance_pack_delivery_unreconciled",
            "errors": [
                _err(
                    "milestone_plan_acceptance_pack_delivery_unreconciled",
                    f"delivery load: {exc}",
                )
            ],
        }
    try:
        pack = _load(pack_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "code": "milestone_plan_acceptance_pack_not_used",
            "errors": [
                _err(
                    "milestone_plan_acceptance_pack_not_used",
                    f"pack load: {exc}",
                )
            ],
        }

    pack_status = pack.get("status")
    if pack_status not in ACCEPTED_PACK_STATUS:
        # Unattended grant may set accepted_by without status yet — require accepted.
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_not_used",
                f"pack status must be accepted, got {pack_status!r}",
            )
        )

    reconcile = _extract_reconcile(delivery)
    if reconcile is None:
        return {
            "ok": False,
            "code": "milestone_plan_acceptance_pack_delivery_unreconciled",
            "errors": [
                _err(
                    "milestone_plan_acceptance_pack_delivery_unreconciled",
                    "milestone_plan_pack_reconcile block required",
                )
            ],
        }
    if not isinstance(reconcile, dict):
        return {
            "ok": False,
            "code": "milestone_plan_acceptance_pack_delivery_unreconciled",
            "errors": [
                _err(
                    "milestone_plan_acceptance_pack_delivery_unreconciled",
                    "milestone_plan_pack_reconcile must be an object",
                )
            ],
        }

    if reconcile.get("schema") != SCHEMA:
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_delivery_unreconciled",
                f"schema must be {SCHEMA}",
            )
        )

    if reconcile.get("contract_loaded") is not True:
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_not_used",
                "contract_loaded must be true",
            )
        )
    if not _nonempty_str(reconcile.get("pack_path")):
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_not_used",
                "pack_path required",
            )
        )
    if reconcile.get("pack_status") not in ACCEPTED_PACK_STATUS:
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_not_used",
                "reconcile.pack_status must be accepted",
            )
        )
    if reconcile.get("status") not in VALID_RECONCILE_STATUS:
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_delivery_unreconciled",
                "reconcile.status must be pending|complete",
            )
        )
    if reconcile.get("status") != "complete":
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_delivery_unreconciled",
                "reconcile.status must be complete for Delivery close",
            )
        )

    pack_sections = pack.get("sections")
    if not isinstance(pack_sections, dict):
        pack_sections = {}

    sections = reconcile.get("sections")
    if not isinstance(sections, dict):
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_delivery_unreconciled",
                "reconcile.sections object required",
            )
        )
        sections = {}

    any_drifted = False
    for key in SECTION_KEYS:
        pack_sec = pack_sections.get(key)
        present = False
        if isinstance(pack_sec, dict) and pack_sec.get("present") is True:
            present = True
        row = sections.get(key)
        if present:
            if not isinstance(row, dict):
                errors.append(
                    _err(
                        "milestone_plan_acceptance_pack_delivery_unreconciled",
                        f"sections.{key} required when pack present=true",
                    )
                )
                continue
            if row.get("applicable") is not True:
                errors.append(
                    _err(
                        "milestone_plan_acceptance_pack_delivery_unreconciled",
                        f"sections.{key}.applicable must be true when pack present",
                    )
                )
            status = row.get("status")
            if status not in {"matched", "drifted"}:
                errors.append(
                    _err(
                        "milestone_plan_acceptance_pack_delivery_unreconciled",
                        f"sections.{key}.status must be matched|drifted when applicable",
                    )
                )
            if status == "drifted":
                any_drifted = True
        elif isinstance(row, dict):
            status = row.get("status")
            if status is not None and status not in VALID_SECTION_STATUS:
                errors.append(
                    _err(
                        "milestone_plan_acceptance_pack_delivery_unreconciled",
                        f"sections.{key}.status invalid",
                    )
                )

    if any_drifted and not _nonempty_str(reconcile.get("drift_writeback_ref")):
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_drift",
                "drift_writeback_ref required when any section status=drifted",
            )
        )

    ok = not errors
    code = "ok"
    if not ok:
        priority = [
            "milestone_plan_acceptance_pack_drift",
            "milestone_plan_acceptance_pack_not_used",
            "milestone_plan_acceptance_pack_delivery_unreconciled",
        ]
        present_codes = {e["code"] for e in errors}
        code = next((c for c in priority if c in present_codes), errors[0]["code"])
    return {"ok": ok, "code": code, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path, help="Delivery Markdown/JSON path")
    parser.add_argument(
        "--pack",
        type=Path,
        required=True,
        help="Accepted milestone Plan acceptance pack path",
    )
    args = parser.parse_args(argv)
    result = lint_milestone_plan_pack_delivery_reconcile(args.delivery, args.pack)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
