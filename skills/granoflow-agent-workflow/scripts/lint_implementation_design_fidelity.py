#!/usr/bin/env python3
"""Lint impl_design_fidelity ledgers for Delivery self-check completeness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_impl_design_fidelity_v1"
AXIS_STATUSES = frozenset({"not_applicable", "matched", "diverged"})
MODULAR_STATUSES = frozenset({"matched", "needs_split", "diverged_kept"})
TOP_STATUS = frozenset({"not_applicable", "pending", "complete"})
DECISIONS = frozenset(
    {"matched_all", "revise_to_design", "keep_with_design_writeback", "not_applicable"}
)
DESIGN_AXES = ("data_structures", "flowcharts", "uml_diagrams")


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ImportError:
        data = json.loads(text)
    if isinstance(data, dict) and "impl_design_fidelity" in data:
        return data["impl_design_fidelity"]
    return data


def lint_ledger(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "ok": False,
            "errors": [_err("impl_design_fidelity_lint_failed", "ledger must be a mapping")],
        }

    if data.get("schema") != SCHEMA:
        errors.append(_err("impl_design_fidelity_lint_failed", f"schema must be {SCHEMA}"))
    if data.get("contract_loaded") is not True:
        errors.append(_err("impl_design_fidelity_unread", "contract_loaded must be true"))

    status = data.get("status")
    if status not in TOP_STATUS:
        errors.append(_err("impl_design_fidelity_incomplete", f"bad status: {status!r}"))

    if status == "not_applicable":
        return {"ok": len(errors) == 0, "errors": errors, "status": status}

    if status != "complete":
        errors.append(
            _err("impl_design_fidelity_incomplete", "status must be complete at Delivery")
        )

    if data.get("declaration_emitted") is not True:
        errors.append(_err("impl_design_fidelity_undeclared", "declaration_emitted must be true"))

    decision = data.get("decision")
    if decision not in DECISIONS:
        errors.append(_err("impl_design_fidelity_incomplete", f"bad decision: {decision!r}"))

    axes = data.get("axes")
    if not isinstance(axes, dict):
        errors.append(_err("impl_design_axis_unresolved", "axes missing"))
        return {"ok": False, "errors": errors}

    diverged = False
    for name in DESIGN_AXES:
        axis = axes.get(name)
        if not isinstance(axis, dict) or axis.get("status") not in AXIS_STATUSES:
            errors.append(_err("impl_design_axis_unresolved", f"axis {name} unresolved"))
            continue
        if axis["status"] == "not_applicable" and not str(axis.get("basis") or "").strip():
            errors.append(_err("impl_design_axis_unresolved", f"axis {name} needs basis"))
        if axis["status"] == "diverged":
            diverged = True

    modular = axes.get("modular_split")
    if not isinstance(modular, dict) or modular.get("status") not in MODULAR_STATUSES:
        errors.append(_err("impl_design_modular_split_unresolved", "modular_split unresolved"))
    elif modular.get("status") == "needs_split":
        errors.append(
            _err(
                "impl_design_modular_split_unresolved",
                "modular_split still needs_split at Delivery",
            )
        )
    elif modular.get("status") == "diverged_kept":
        diverged = True

    if diverged or decision == "keep_with_design_writeback":
        if not str(data.get("better_rationale") or "").strip():
            errors.append(
                _err(
                    "impl_design_better_rationale_missing",
                    "better_rationale required when keeping divergence",
                )
            )
        writeback = data.get("design_writeback")
        if not isinstance(writeback, dict) or writeback.get("status") != "written_and_read_back":
            errors.append(
                _err(
                    "impl_design_writeback_missing",
                    "design_writeback.status must be written_and_read_back",
                )
            )
        elif not writeback.get("slots_updated"):
            errors.append(
                _err("impl_design_writeback_missing", "design_writeback.slots_updated empty")
            )
        diffs = data.get("diffs")
        if not isinstance(diffs, list) or not diffs:
            errors.append(
                _err("impl_design_fidelity_incomplete", "diffs required when diverged/kept")
            )

    return {"ok": len(errors) == 0, "errors": errors, "status": status, "decision": decision}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args(argv)
    result = lint_ledger(_load(args.ledger))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
