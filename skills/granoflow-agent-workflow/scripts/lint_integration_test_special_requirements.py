#!/usr/bin/env python3
"""Lint Project Work integration_test_special_requirements rows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_KINDS = frozenset(
    {
        "seed_corpus",
        "fixture_paths",
        "forbidden_substitute",
        "run_constraint",
        "other",
    }
)
VALID_PROVENANCE = frozenset({"user_stated", "recommended", "inferred"})
VALID_ENFORCEMENT = frozenset({"fail_closed", "advisory"})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _rows(project_work: Any) -> list[dict[str, Any]] | None:
    if not isinstance(project_work, dict):
        return None
    engineering = project_work.get("engineering")
    if not isinstance(engineering, dict):
        return []
    quality_gates = engineering.get("quality_gates")
    if not isinstance(quality_gates, dict):
        return []
    rows = quality_gates.get("integration_test_special_requirements")
    if rows is None:
        return []
    if not isinstance(rows, list):
        return None
    return rows


def lint_special_requirements(project_work: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    rows = _rows(project_work)
    if rows is None:
        return {
            "ok": False,
            "code": "integration_test_special_requirements_invalid",
            "errors": [
                _err(
                    "integration_test_special_requirements_invalid",
                    "engineering.quality_gates.integration_test_special_requirements "
                    "must be a list when present",
                )
            ],
        }

    seen: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"integration_test_special_requirements[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "integration_test_special_requirements_invalid",
                    f"{prefix} must be object",
                )
            )
            continue
        # Allow placeholder null row from the template.
        if row.get("id") is None and row.get("statement") is None and row.get("kind") is None:
            continue
        req_id = row.get("id")
        if not isinstance(req_id, str) or not req_id.strip():
            errors.append(
                _err(
                    "integration_test_special_requirements_invalid",
                    f"{prefix}.id required",
                )
            )
        else:
            if req_id in seen:
                errors.append(
                    _err(
                        "integration_test_special_requirements_invalid",
                        f"duplicate id {req_id}",
                    )
                )
            seen.add(req_id)
        kind = row.get("kind")
        if kind not in VALID_KINDS:
            errors.append(
                _err(
                    "integration_test_special_requirements_invalid",
                    f"{prefix}.kind must be one of {sorted(VALID_KINDS)}",
                )
            )
        statement = row.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            errors.append(
                _err(
                    "integration_test_special_requirements_invalid",
                    f"{prefix}.statement required",
                )
            )
        enforcement = row.get("enforcement")
        if enforcement not in VALID_ENFORCEMENT:
            errors.append(
                _err(
                    "integration_test_special_requirements_invalid",
                    f"{prefix}.enforcement must be fail_closed|advisory",
                )
            )
        provenance = row.get("provenance")
        if provenance is not None and provenance not in VALID_PROVENANCE:
            errors.append(
                _err(
                    "integration_test_special_requirements_invalid",
                    f"{prefix}.provenance must be user_stated|recommended|inferred",
                )
            )
        applies = row.get("applies_when")
        if (
            not isinstance(applies, list)
            or not applies
            or any(not isinstance(item, str) or not item.strip() for item in applies)
        ):
            errors.append(
                _err(
                    "integration_test_special_requirements_invalid",
                    f"{prefix}.applies_when must be a non-empty string list",
                )
            )
        if kind == "seed_corpus":
            corpus = row.get("corpus_paths")
            if (
                not isinstance(corpus, list)
                or not corpus
                or any(not isinstance(item, str) or not item.strip() for item in corpus)
            ):
                errors.append(
                    _err(
                        "integration_test_special_requirements_invalid",
                        f"{prefix}.corpus_paths required non-empty for seed_corpus",
                    )
                )
            if row.get("not_app_seed") is True:
                app_seed = row.get("app_seed_paths")
                if app_seed is not None and (
                    not isinstance(app_seed, list)
                    or any(not isinstance(item, str) for item in app_seed)
                ):
                    errors.append(
                        _err(
                            "integration_test_special_requirements_invalid",
                            f"{prefix}.app_seed_paths must be a string list when present",
                        )
                    )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "integration_test_special_requirements_invalid",
        "errors": errors,
        "count": len([row for row in rows if isinstance(row, dict) and row.get("id")]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_work", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.project_work.is_file():
        result = {
            "ok": False,
            "code": "missing_file",
            "errors": [_err("missing_file", str(args.project_work))],
        }
    else:
        result = lint_special_requirements(_load(args.project_work))
        result["path"] = str(args.project_work)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["ok"]:
        print("ok")
    else:
        print(result["code"], file=sys.stderr)
        for err in result.get("errors", []):
            print(f"{err['code']}: {err['detail']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
