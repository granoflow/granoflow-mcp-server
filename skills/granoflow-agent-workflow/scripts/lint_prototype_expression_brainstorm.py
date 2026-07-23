#!/usr/bin/env python3
"""Lint prototype expression_brainstorm records (mainstream-first protocol).

Fail closed when the candidate pool skips mainstream references, pads with
unjustified brainstorm, uses an illegal scope_mode, or promotes the wrong
count / incomplete-scope candidates.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_LAYERS = frozenset({"design_spec", "app_shell", "task_page_expression"})
VALID_SCOPE_MODES = frozenset({"same_category", "capability_match"})
VALID_SOURCES = frozenset({"mainstream", "brainstorm_backfill"})
PROMOTE_BY_LAYER = {
    "design_spec": 3,
    "app_shell": 3,
    "task_page_expression": 2,
}
TASK_THREE_REASONS = frozenset(
    {
        "three_viable_patterns",
        "cross_form_factor_tradeoff",
        "high_risk_interaction_choice",
    }
)


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load_yamlish(path: Path) -> Any:
    """Load YAML if PyYAML is available; else accept JSON."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _extract_record(data: Any) -> dict[str, Any] | None:
    if data is None:
        return None
    if not isinstance(data, dict):
        return None
    if "expression_brainstorm" in data:
        nested = data["expression_brainstorm"]
        if nested is None:
            return None
        if isinstance(nested, dict):
            return nested
        return None
    if "prototype_option_set" in data and isinstance(data["prototype_option_set"], dict):
        nested = data["prototype_option_set"].get("expression_brainstorm")
        if isinstance(nested, dict):
            return nested
        return None
    # Bare record
    if any(
        key in data
        for key in (
            "mainstream_references",
            "scope_mode",
            "source_strategy",
            "candidate_count",
            "candidates",
        )
    ):
        return data
    return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def lint_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    status = record.get("status")
    if status is None:
        # Accept recorded|ok; missing status still fails as incomplete shape
        errors.append(
            _err(
                "prototype_option_brainstorm_missing",
                "expression_brainstorm.status missing",
            )
        )

    layer = record.get("layer")
    if layer not in VALID_LAYERS:
        errors.append(
            _err(
                "prototype_option_brainstorm_incomplete",
                f"layer must be one of {sorted(VALID_LAYERS)} (got {layer!r})",
            )
        )

    strategy = record.get("source_strategy")
    if strategy not in {None, "mainstream_first"}:
        errors.append(
            _err(
                "prototype_option_brainstorm_incomplete",
                f"source_strategy must be mainstream_first (got {strategy!r})",
            )
        )
    if strategy is None:
        errors.append(
            _err(
                "prototype_option_brainstorm_incomplete",
                "source_strategy required (mainstream_first)",
            )
        )

    scope_mode = record.get("scope_mode")
    if scope_mode not in VALID_SCOPE_MODES:
        errors.append(
            _err(
                "prototype_option_scope_mode_invalid",
                f"scope_mode must be same_category|capability_match (got {scope_mode!r})",
            )
        )

    rationale = record.get("scope_mode_rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append(
            _err(
                "prototype_option_brainstorm_incomplete",
                "scope_mode_rationale required",
            )
        )

    mainstream = _as_list(record.get("mainstream_references"))
    backfill = _as_list(record.get("brainstorm_backfill"))
    candidates = _as_list(record.get("candidates"))

    for i, ref in enumerate(mainstream):
        if not isinstance(ref, dict):
            errors.append(
                _err(
                    "prototype_option_brainstorm_incomplete",
                    f"mainstream_references[{i}] must be an object",
                )
            )
            continue
        product = ref.get("product")
        if not isinstance(product, str) or not product.strip():
            errors.append(
                _err(
                    "prototype_option_brainstorm_incomplete",
                    f"mainstream_references[{i}].product required",
                )
            )

    for i, item in enumerate(backfill):
        if not isinstance(item, dict):
            errors.append(
                _err(
                    "prototype_option_brainstorm_incomplete",
                    f"brainstorm_backfill[{i}] must be an object",
                )
            )

    mainstream_count = len([r for r in mainstream if isinstance(r, dict)])
    backfill_count = len([b for b in backfill if isinstance(b, dict)])

    # Prefer unified candidates when present; else derive from mainstream+backfill
    if candidates:
        pool = [c for c in candidates if isinstance(c, dict)]
        for i, cand in enumerate(pool):
            source = cand.get("source")
            if source is not None and source not in VALID_SOURCES:
                errors.append(
                    _err(
                        "prototype_option_brainstorm_incomplete",
                        f"candidates[{i}].source invalid ({source!r})",
                    )
                )
    else:
        pool = [r for r in mainstream if isinstance(r, dict)] + [
            b for b in backfill if isinstance(b, dict)
        ]

    candidate_count = record.get("candidate_count")
    if isinstance(candidate_count, int):
        if candidate_count != len(pool) and pool:
            # Trust explicit count only when it matches pool; else use pool len
            pass
        effective_count = candidate_count if candidate_count >= len(pool) else len(pool)
        if not pool:
            effective_count = candidate_count
    else:
        effective_count = len(pool)
        if candidate_count is not None:
            errors.append(
                _err(
                    "prototype_option_brainstorm_incomplete",
                    f"candidate_count must be int (got {candidate_count!r})",
                )
            )

    if effective_count < 5:
        errors.append(
            _err(
                "prototype_option_brainstorm_incomplete",
                f"candidate pool must be ≥5 (got {effective_count})",
            )
        )

    if mainstream_count >= 5 and backfill_count > 0:
        errors.append(
            _err(
                "prototype_option_mainstream_skip",
                "brainstorm_backfill must be empty when mainstream_count ≥ 5",
            )
        )

    if mainstream_count < 5:
        if backfill_count == 0 and effective_count < 5:
            errors.append(
                _err(
                    "prototype_option_brainstorm_incomplete",
                    "mainstream_count < 5 requires brainstorm_backfill to reach ≥5",
                )
            )
        if backfill_count > 0:
            reason = record.get("brainstorm_backfill_reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(
                    _err(
                        "prototype_option_backfill_unjustified",
                        "brainstorm_backfill_reason required when backfill is used",
                    )
                )

    expected_promote = PROMOTE_BY_LAYER.get(layer) if layer in PROMOTE_BY_LAYER else None
    promote_count = record.get("promote_count")
    industry_third = bool(record.get("industry_peer_third"))
    if layer == "task_page_expression" and promote_count == 3:
        reason = record.get("option_count_reason_code")
        if reason in TASK_THREE_REASONS or industry_third:
            expected_promote = 3
        else:
            errors.append(
                _err(
                    "prototype_option_promote_count_mismatch",
                    "three task options require an allowed option_count_reason_code",
                )
            )

    if expected_promote is not None and promote_count != expected_promote:
        errors.append(
            _err(
                "prototype_option_promote_count_mismatch",
                f"promote_count for {layer} must be {expected_promote} " f"(got {promote_count!r})",
            )
        )

    selected = record.get("selected")
    promoted_ids: set[str] = set()
    if isinstance(selected, dict):
        for _slot, cand_id in selected.items():
            if isinstance(cand_id, str) and cand_id.strip():
                promoted_ids.add(cand_id)

    # Also collect promote_as from pool
    for cand in pool:
        if not isinstance(cand, dict):
            continue
        if cand.get("discarded") is False and cand.get("promote_as"):
            cid = cand.get("id")
            if isinstance(cid, str):
                promoted_ids.add(cid)
        if cand.get("covers_full_scope") is False and (
            cand.get("discarded") is False or cand.get("promote_as")
        ):
            errors.append(
                _err(
                    "prototype_option_brainstorm_incomplete",
                    f"promoted candidate {cand.get('id')!r} has covers_full_scope=false",
                )
            )

    if (
        expected_promote is not None
        and isinstance(selected, dict)
        and len(selected) != expected_promote
    ):
        errors.append(
            _err(
                "prototype_option_promote_count_mismatch",
                f"selected map size must be {expected_promote} " f"(got {len(selected)})",
            )
        )

    parity = record.get("parity_check")
    if not isinstance(parity, dict):
        errors.append(
            _err(
                "prototype_option_brainstorm_incomplete",
                "parity_check object required",
            )
        )
    else:
        for key in ("same_capabilities", "same_data_fields", "same_required_states"):
            if parity.get(key) is not True:
                errors.append(
                    _err(
                        "prototype_option_function_split"
                        if key == "same_capabilities"
                        else "prototype_option_brainstorm_incomplete",
                        f"parity_check.{key} must be true",
                    )
                )

    selection_rationale = record.get("selection_rationale")
    if not isinstance(selection_rationale, str) or not selection_rationale.strip():
        errors.append(
            _err(
                "prototype_option_brainstorm_incomplete",
                "selection_rationale required",
            )
        )

    ok = not errors
    return {
        "ok": ok,
        "errors": errors,
        "code": "ok" if ok else "prototype_expression_brainstorm_lint_failed",
        "mainstream_count": mainstream_count,
        "backfill_count": backfill_count,
        "candidate_count": effective_count,
        "promoted_ids": sorted(promoted_ids),
    }


def lint_document(data: Any) -> dict[str, Any]:
    record = _extract_record(data)
    if record is None:
        return {
            "ok": False,
            "code": "prototype_expression_brainstorm_lint_failed",
            "errors": [
                _err(
                    "prototype_option_brainstorm_missing",
                    "no expression_brainstorm record found",
                )
            ],
        }
    return lint_record(record)


def lint_path(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "ok": False,
            "code": "prototype_expression_brainstorm_lint_failed",
            "errors": [_err("missing_file", str(path))],
        }
    data = _load_yamlish(path)
    result = lint_document(data)
    result["path"] = str(path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "record",
        type=Path,
        help="Path to expression_brainstorm YAML/JSON or Work Document excerpt",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args(argv)

    result = lint_path(args.record)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["ok"]:
            print("ok")
        else:
            print(result["code"], file=sys.stderr)
            for err in result.get("errors", []):
                print(f"{err['code']}: {err['detail']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
