#!/usr/bin/env python3
"""Lint unit Plan policy: no copy-existence tests; every operation covered."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CASES_SCHEMA = "granoflow_plan_verification_cases_v1"
OPS_SCHEMA = "granoflow_task_operations_v1"
# Unit cases may only declare behavior. copy_presence is a hard forbid.
VALID_ASSERTS = frozenset({"behavior"})
COPY_ASSERT_RE = re.compile(
    r"find\.text\(|findsOneWidget|findsWidgets|getByText\(|toHaveTextContent\("
    r"|expect\(.*\)\.toContain\(|assertEquals\([^,]+,\s*[\"'][^\"']+[\"']\)",
    re.I,
)
# Signals the test exercises an operation result / state / failure path.
BEHAVIOR_ASSERT_RE = re.compile(
    r"\b(when\(|verify\(|verifyNever|throwA|throwsA|throwsException|"
    r"expectLater|mock|Fake|persist|write|delete|decrypt|encrypt|"
    r"result\.|statusCode|Navigator\.|goNamed|emit\(|blocTest|"
    r"OperationResult|Failure|Success)\b",
    re.I,
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


def extract_operations(data: Any) -> list[str]:
    """Collect operation/action ids from task_operations or screen contracts."""
    ids: list[str] = []
    if not isinstance(data, dict):
        return ids

    ops = data.get("task_operations")
    if isinstance(ops, dict) and isinstance(ops.get("operations"), list):
        for row in ops["operations"]:
            if isinstance(row, dict) and _nonempty_str(row.get("operation_id")):
                ids.append(str(row["operation_id"]).strip())
            elif isinstance(row, str) and row.strip():
                ids.append(row.strip())
    elif data.get("schema") == OPS_SCHEMA and isinstance(data.get("operations"), list):
        for row in data["operations"]:
            if isinstance(row, dict) and _nonempty_str(row.get("operation_id")):
                ids.append(str(row["operation_id"]).strip())
            elif isinstance(row, str) and row.strip():
                ids.append(row.strip())
    elif isinstance(data.get("operations"), list):
        for row in data["operations"]:
            if isinstance(row, dict) and _nonempty_str(
                row.get("operation_id") or row.get("action_id")
            ):
                ids.append(str(row.get("operation_id") or row.get("action_id")).strip())
            elif isinstance(row, str) and row.strip():
                ids.append(row.strip())

    # Screen Content Contract shape
    screens = data.get("screens")
    if isinstance(screens, list):
        for screen in screens:
            if not isinstance(screen, dict):
                continue
            actions = screen.get("actions")
            if not isinstance(actions, list):
                continue
            for action in actions:
                if isinstance(action, dict) and _nonempty_str(action.get("action_id")):
                    ids.append(str(action["action_id"]).strip())

    # Content contract wrapper
    contract = data.get("screen_content_contract")
    if isinstance(contract, dict):
        ids.extend(extract_operations(contract))

    # Dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for item in ids:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def extract_unit_cases(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    block = data.get("plan_verification_cases")
    if isinstance(block, dict) and isinstance(block.get("cases"), list):
        rows = block["cases"]
    elif isinstance(block, list):
        rows = block
    elif (data.get("schema") == CASES_SCHEMA and isinstance(data.get("cases"), list)) or isinstance(
        data.get("cases"), list
    ):
        rows = data["cases"]
    else:
        rows = []

    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        lane = str(row.get("lane") or row.get("kind") or "").strip().lower()
        if lane != "unit":
            continue
        case_id = str(row.get("case_id") or row.get("id") or "").strip()
        if not case_id:
            continue
        op_ids: list[str] = []
        raw_ops = row.get("operation_ids") or row.get("operations")
        if isinstance(raw_ops, list):
            op_ids = [str(x).strip() for x in raw_ops if _nonempty_str(x)]
        elif _nonempty_str(row.get("operation_id")):
            op_ids = [str(row["operation_id"]).strip()]
        elif _nonempty_str(row.get("action_id")):
            op_ids = [str(row["action_id"]).strip()]
        asserts = str(row.get("asserts") or "behavior").strip().lower()
        out.append(
            {
                "case_id": case_id,
                "operation_ids": op_ids,
                "asserts": asserts,
                "test_ref": str(row.get("test_ref") or "").strip(),
            }
        )
    return out


def _scan_unit_test_file(path: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [_err("unit_copy_assertion_forbidden", f"{path}: unreadable ({exc})")]
    has_copy = bool(COPY_ASSERT_RE.search(text))
    has_behavior = bool(BEHAVIOR_ASSERT_RE.search(text))
    if has_copy and not has_behavior:
        errors.append(
            _err(
                "unit_copy_assertion_forbidden",
                f"{path}: unit test asserts user-visible copy/text presence "
                "without behavior/operation assertions",
            )
        )
    elif has_copy and has_behavior:
        # Still forbidden as a unit purpose: copy presence checks belong to
        # prototype/contract review, not unit suites.
        errors.append(
            _err(
                "unit_copy_assertion_forbidden",
                f"{path}: unit tests must not assert user-visible copy "
                "(use keys/semantics/behavior instead)",
            )
        )
    return errors


def lint_plan_unit_policy(
    cases_data: Any,
    operations_data: Any,
    *,
    workspace: Path | None = None,
    require_operations: bool = True,
    scan_tests: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    unit_cases = extract_unit_cases(cases_data)
    operations = extract_operations(operations_data)

    if require_operations and not operations:
        errors.append(
            _err(
                "unit_operation_coverage_incomplete",
                "no operations/action_ids found; provide Screen Content Contract "
                "or task_operations list",
            )
        )

    if not unit_cases and operations:
        errors.append(
            _err(
                "unit_operation_coverage_incomplete",
                "operations exist but no lane=unit Plan cases were authored",
            )
        )

    covered: set[str] = set()
    for case in unit_cases:
        case_id = case["case_id"]
        asserts = case["asserts"]
        if asserts == "copy_presence":
            errors.append(
                _err(
                    "unit_copy_assertion_forbidden",
                    f"{case_id}: unit cases must not assert copy_presence "
                    "(copy is validated via prototype/Content Contract/验收册)",
                )
            )
        elif asserts not in VALID_ASSERTS:
            errors.append(
                _err(
                    "unit_copy_assertion_forbidden",
                    f"{case_id}: unit asserts must be behavior (got {asserts!r})",
                )
            )
        op_ids = case["operation_ids"]
        if not op_ids:
            errors.append(
                _err(
                    "unit_operation_coverage_incomplete",
                    f"{case_id}: unit case requires operation_id or operation_ids "
                    "(every user/system operation must be unit-tested)",
                )
            )
        for op in op_ids:
            covered.add(op)

        if scan_tests and workspace is not None and case["test_ref"]:
            ref = Path(case["test_ref"])
            path = ref if ref.is_absolute() else (workspace / ref)
            if path.is_file():
                errors.extend(_scan_unit_test_file(path.resolve()))
            else:
                errors.append(
                    _err(
                        "unit_operation_coverage_incomplete",
                        f"{case_id}: test_ref missing for scan ({case['test_ref']})",
                    )
                )

    if operations:
        missing = [op for op in operations if op not in covered]
        for op in missing:
            errors.append(
                _err(
                    "unit_operation_coverage_incomplete",
                    f"operation {op} has no lane=unit Plan case",
                )
            )
        # Unknown operation_ids on cases (typos)
        unknown = sorted(covered - set(operations))
        for op in unknown:
            errors.append(
                _err(
                    "unit_operation_coverage_incomplete",
                    f"unit case references unknown operation_id {op}",
                )
            )

    ok = not errors
    code = "ok"
    if not ok:
        priority = [
            "unit_copy_assertion_forbidden",
            "unit_operation_coverage_incomplete",
        ]
        present = {e["code"] for e in errors}
        code = next((c for c in priority if c in present), errors[0]["code"])
    return {
        "ok": ok,
        "code": code,
        "errors": errors,
        "operation_count": len(operations),
        "unit_case_count": len(unit_cases),
        "covered_operation_count": len(covered & set(operations)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        type=Path,
        required=True,
        help="Plan verification cases YAML/JSON",
    )
    parser.add_argument(
        "--operations",
        type=Path,
        required=True,
        help="Screen Content Contract or task_operations YAML/JSON",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Repo root when --scan-tests is set",
    )
    parser.add_argument(
        "--scan-tests",
        action="store_true",
        help="Scan unit test_ref files and forbid copy-existence assertions",
    )
    parser.add_argument(
        "--allow-empty-operations",
        action="store_true",
        help="Do not require an operations inventory (non-UI / no actions)",
    )
    args = parser.parse_args(argv)
    result = lint_plan_unit_policy(
        _load(args.cases),
        _load(args.operations),
        workspace=args.workspace.resolve() if args.workspace else None,
        require_operations=not args.allow_empty_operations,
        scan_tests=args.scan_tests,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
