#!/usr/bin/env python3
"""Lint milestone Plan pack Case IDs ↔ Task Work plan case sources."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

SYNC_LANES = frozenset({"unit", "integration", "e2e"})

_HERE = Path(__file__).resolve().parent
_PCI_PATH = _HERE / "lint_plan_case_implementation.py"


def _load_pci():
    spec = importlib.util.spec_from_file_location("lint_plan_case_implementation", _PCI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {_PCI_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PCI = _load_pci()


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _test_cases_present(pack_data: dict[str, Any]) -> bool | None:
    sections = pack_data.get("sections")
    if not isinstance(sections, dict):
        return None
    tc = sections.get("test_cases")
    if not isinstance(tc, dict):
        return None
    present = tc.get("present")
    if isinstance(present, bool):
        return present
    return None


def lint_milestone_plan_pack_case_sync(
    pack_path: Path,
    task_case_paths: list[Path],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    try:
        pack_data = PCI._load(pack_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "code": "pack_case_sync_lint_failed",
            "errors": [_err("pack_case_sync_lint_failed", f"pack load: {exc}")],
        }
    if not isinstance(pack_data, dict):
        return {
            "ok": False,
            "code": "pack_case_sync_lint_failed",
            "errors": [_err("pack_case_sync_lint_failed", "pack root must be an object")],
        }

    present = _test_cases_present(pack_data)
    if present is False:
        return {
            "ok": True,
            "code": "not_applicable",
            "errors": [],
            "pack_case_count": 0,
            "task_case_count": 0,
        }
    if present is None:
        errors.append(
            _err(
                "pack_case_sync_lint_failed",
                "sections.test_cases.present required (true|false)",
            )
        )

    pack_cases = [c for c in PCI._extract_source_cases(pack_data) if c.get("lane") in SYNC_LANES]

    task_union: dict[str, str] = {}
    for path in task_case_paths:
        try:
            data = PCI._load(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(_err("pack_case_sync_lint_failed", f"task case load {path}: {exc}"))
            continue
        for item in PCI._extract_source_cases(data):
            lane = item.get("lane", "")
            if lane not in SYNC_LANES:
                continue
            case_id = item["case_id"]
            if case_id in task_union and task_union[case_id] != lane:
                errors.append(
                    _err(
                        "pack_case_sync_lint_failed",
                        f"task case {case_id} has conflicting lanes "
                        f"{task_union[case_id]} vs {lane}",
                    )
                )
            task_union[case_id] = lane

    if present is True and not task_case_paths:
        errors.append(
            _err(
                "pack_case_sync_lint_failed",
                "task case source paths required when test_cases.present=true",
            )
        )

    pack_by_id = {c["case_id"]: c["lane"] for c in pack_cases}

    if present is True:
        for case_id, lane in pack_by_id.items():
            if case_id not in task_union:
                errors.append(
                    _err(
                        "pack_case_missing_from_tasks",
                        f"pack case {case_id} ({lane}) missing from task sources",
                    )
                )
            elif task_union[case_id] != lane:
                errors.append(
                    _err(
                        "pack_case_missing_from_tasks",
                        f"pack case {case_id} lane {lane} != task lane " f"{task_union[case_id]}",
                    )
                )
        for case_id, lane in task_union.items():
            if case_id not in pack_by_id:
                errors.append(
                    _err(
                        "task_case_missing_from_pack",
                        f"task case {case_id} ({lane}) missing from pack",
                    )
                )

    ok = not errors
    code = "ok"
    if not ok:
        priority = [
            "pack_case_missing_from_tasks",
            "task_case_missing_from_pack",
            "pack_case_sync_lint_failed",
        ]
        present_codes = {e["code"] for e in errors}
        code = next((c for c in priority if c in present_codes), errors[0]["code"])
    return {
        "ok": ok,
        "code": code,
        "errors": errors,
        "pack_case_count": len(pack_by_id),
        "task_case_count": len(task_union),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path, help="Milestone Plan acceptance pack path")
    parser.add_argument(
        "task_cases",
        nargs="*",
        type=Path,
        help="Task Work / Plan case source paths (JSON or Markdown)",
    )
    args = parser.parse_args(argv)
    result = lint_milestone_plan_pack_case_sync(args.pack, list(args.task_cases))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
