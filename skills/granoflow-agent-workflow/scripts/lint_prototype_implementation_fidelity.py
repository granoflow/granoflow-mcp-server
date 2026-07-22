#!/usr/bin/env python3
"""Lint prototype_impl_compare ledgers (implement-time code-guess compare)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_STATUS = frozenset({"not_applicable", "matched", "diverged"})
VALID_DECISION = frozenset({"keep_implementation", "revise_to_prototype", "not_applicable"})
VALID_TRI = frozenset({"true", "false", "unknown", True, False})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _ledger(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    if "prototype_impl_compare" in data:
        raw = data["prototype_impl_compare"]
        return raw if isinstance(raw, dict) else None
    if "status" in data and "method" in data:
        return data
    return None


def _tri_ok(value: Any) -> bool:
    if value is None:
        return True
    return value in VALID_TRI


def lint_prototype_impl_compare(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    ledger = _ledger(data)
    if ledger is None:
        return {
            "ok": False,
            "code": "prototype_impl_compare_lint_failed",
            "errors": [
                _err(
                    "prototype_impl_compare_lint_failed",
                    "prototype_impl_compare object required",
                )
            ],
        }

    status = ledger.get("status")
    if status not in VALID_STATUS:
        errors.append(
            _err(
                "prototype_impl_compare_lint_failed",
                "status must be not_applicable|matched|diverged",
            )
        )
        return {
            "ok": False,
            "code": "prototype_impl_compare_lint_failed",
            "errors": errors,
        }

    if status == "not_applicable":
        ok = not errors
        return {
            "ok": ok,
            "code": "ok" if ok else "prototype_impl_compare_lint_failed",
            "errors": errors,
        }

    method = ledger.get("method")
    if method != "code_review_guess":
        detail = (
            "method must be code_review_guess at Phase A "
            "(code vs prototype; not screenshot/vision)"
        )
        if isinstance(method, str) and any(
            token in method.lower() for token in ("screenshot", "vision", "ocr", "image_compare")
        ):
            detail = "Phase A forbids screenshot/vision compare; " "use method=code_review_guess"
        errors.append(_err("prototype_impl_compare_wrong_method", detail))

    if ledger.get("declaration_emitted") is not True:
        errors.append(
            _err(
                "prototype_impl_compare_undeclared",
                "declaration_emitted must be true when compare applies",
            )
        )

    decision = ledger.get("decision")
    if decision not in VALID_DECISION:
        errors.append(
            _err(
                "prototype_impl_compare_lint_failed",
                "decision must be keep_implementation|revise_to_prototype|not_applicable",
            )
        )
    elif decision == "not_applicable":
        errors.append(
            _err(
                "prototype_impl_compare_lint_failed",
                "decision not_applicable only valid when status is not_applicable",
            )
        )
    elif status == "matched" and decision != "keep_implementation":
        errors.append(
            _err(
                "prototype_impl_compare_lint_failed",
                "status=matched requires decision=keep_implementation",
            )
        )

    rationale = ledger.get("decision_rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append(
            _err(
                "prototype_impl_compare_lint_failed",
                "decision_rationale required when compare applies",
            )
        )

    # Phase A: three questions required for matched and diverged (code compare,
    # never screenshot/vision). Screenshot methods already fail wrong_method.
    questions = ledger.get("questions")
    if not isinstance(questions, dict):
        errors.append(
            _err(
                "prototype_impl_compare_three_questions_incomplete",
                "questions object required when Phase A compare applies",
            )
        )
    else:
        for key in ("ux_better", "visual_better", "tech_stack_blocked"):
            if (
                key not in questions
                or questions.get(key) is None
                or not _tri_ok(questions.get(key))
            ):
                errors.append(
                    _err(
                        "prototype_impl_compare_three_questions_incomplete",
                        f"questions.{key} must be true|false|unknown",
                    )
                )

    if status == "diverged":
        diffs = ledger.get("diffs")
        if not isinstance(diffs, list) or not diffs:
            errors.append(
                _err(
                    "prototype_diff_ledger_incomplete",
                    "diffs must be a non-empty list when status=diverged",
                )
            )
        else:
            for index, row in enumerate(diffs):
                prefix = f"diffs[{index}]"
                if not isinstance(row, dict):
                    errors.append(
                        _err(
                            "prototype_diff_ledger_incomplete",
                            f"{prefix} must be object",
                        )
                    )
                    continue
                page_id = row.get("page_id")
                summary = row.get("summary")
                if not isinstance(page_id, str) or not page_id.strip():
                    errors.append(
                        _err(
                            "prototype_diff_ledger_incomplete",
                            f"{prefix}.page_id required",
                        )
                    )
                if not isinstance(summary, str) or not summary.strip():
                    errors.append(
                        _err(
                            "prototype_diff_ledger_incomplete",
                            f"{prefix}.summary required",
                        )
                    )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "prototype_impl_compare_lint_failed",
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Compare ledger YAML/JSON path")
    args = parser.parse_args(argv)
    result = lint_prototype_impl_compare(_load(args.path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
