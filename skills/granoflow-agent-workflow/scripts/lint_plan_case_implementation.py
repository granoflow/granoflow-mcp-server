#!/usr/bin/env python3
"""Lint plan verification cases → implementation ledger (no forgotten cases)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_plan_case_implementation_v1"
CASES_SCHEMA = "granoflow_plan_verification_cases_v1"
VALID_LEDGER_STATUS = frozenset({"pending", "complete"})
VALID_CASE_STATUS = frozenset(
    {
        "implemented",
        "scheduled_campaign",
        "executed",
        "blocked_by_dependency",
        "missing",
    }
)
VALID_LANES = frozenset({"unit", "integration", "e2e", "widget", "manual"})
AUTOMATED_LAYER_A = frozenset({"unit", "widget"})
CAMPAIGN_LANES = frozenset({"integration", "e2e"})
VALID_GATES = frozenset({"layer_a", "layer_b", "e2e_campaign"})
LANE_ROW_RE = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*(unit|integration|e2e|widget|manual)\s*\|",
    re.IGNORECASE | re.MULTILINE,
)


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load(path: Path) -> Any:
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
        except ImportError as exc:
            raise ValueError("PyYAML required for Markdown frontmatter") from exc
        if not isinstance(data, dict):
            raise ValueError("frontmatter must be a mapping")
        data = dict(data)
        data.setdefault("body_markdown", body)
        return data
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _extract_ledger(data: Any) -> Any:
    if not isinstance(data, dict):
        return None
    if "plan_case_implementation" in data:
        return data.get("plan_case_implementation")
    if data.get("schema") == SCHEMA:
        return data
    return None


def _extract_source_cases(data: Any) -> list[dict[str, str]]:
    """Return [{case_id, lane}, ...] from structured list or Markdown tables."""
    if not isinstance(data, dict):
        return []
    out: list[dict[str, str]] = []
    block = data.get("plan_verification_cases")
    if isinstance(block, dict) and isinstance(block.get("cases"), list):
        rows = block["cases"]
    elif isinstance(block, list):
        rows = block
    elif data.get("schema") == CASES_SCHEMA and isinstance(data.get("cases"), list):
        rows = data["cases"]
    else:
        rows = None

    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            case_id = str(row.get("case_id") or row.get("id") or "").strip()
            lane = str(row.get("lane") or row.get("kind") or "").strip().lower()
            if case_id and lane:
                out.append({"case_id": case_id, "lane": lane})

    body = data.get("body_markdown") or data.get("_body") or ""
    if _nonempty_str(body):
        for match in LANE_ROW_RE.finditer(str(body)):
            case_id = match.group(1).strip()
            lane = match.group(2).strip().lower()
            # Skip header-like cells
            if case_id.lower() in {"id", "case id", "case_id"}:
                continue
            out.append({"case_id": case_id, "lane": lane})

    # Dedupe by case_id (first wins)
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in out:
        if item["case_id"] in seen:
            continue
        seen.add(item["case_id"])
        unique.append(item)
    return unique


def _resolve_test_ref(test_ref: str, workspace: Path | None) -> Path | None:
    path = Path(test_ref.strip())
    if path.is_absolute():
        return path
    if workspace is None:
        return None
    return (workspace / path).resolve()


def lint_plan_case_implementation(
    ledger_data: Any,
    source_data: Any,
    *,
    gate: str = "layer_a",
    workspace: Path | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if gate not in VALID_GATES:
        return {
            "ok": False,
            "code": "plan_case_implementation_lint_failed",
            "errors": [_err("plan_case_implementation_lint_failed", f"invalid gate {gate}")],
        }

    source_cases = _extract_source_cases(source_data)
    if not source_cases:
        return {
            "ok": False,
            "code": "plan_case_source_missing",
            "errors": [
                _err(
                    "plan_case_source_missing",
                    "no plan verification cases found (plan_verification_cases or Markdown lanes)",
                )
            ],
        }

    for item in source_cases:
        if item["lane"] not in VALID_LANES:
            errors.append(
                _err(
                    "plan_case_implementation_lint_failed",
                    f"source case {item['case_id']} has invalid lane {item['lane']}",
                )
            )

    ledger = _extract_ledger(ledger_data)
    if ledger is None:
        return {
            "ok": False,
            "code": "plan_case_implementation_missing",
            "errors": [
                _err(
                    "plan_case_implementation_missing",
                    "plan_case_implementation object required",
                )
            ],
        }
    if not isinstance(ledger, dict):
        return {
            "ok": False,
            "code": "plan_case_implementation_lint_failed",
            "errors": [
                _err(
                    "plan_case_implementation_lint_failed",
                    "plan_case_implementation must be an object",
                )
            ],
        }

    if ledger.get("contract_loaded") is not True:
        errors.append(
            _err(
                "plan_case_implementation_unread",
                "contract_loaded must be true",
            )
        )
    if ledger.get("schema") != SCHEMA:
        errors.append(
            _err(
                "plan_case_implementation_lint_failed",
                f"schema must be {SCHEMA}",
            )
        )

    top_status = ledger.get("status")
    if top_status not in VALID_LEDGER_STATUS:
        errors.append(
            _err(
                "plan_case_implementation_lint_failed",
                "status must be pending|complete",
            )
        )

    rows = ledger.get("cases")
    if not isinstance(rows, list) or not rows:
        errors.append(
            _err(
                "plan_case_implementation_incomplete",
                "cases must be a non-empty list",
            )
        )
        rows = []

    by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        prefix = f"cases[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "plan_case_implementation_incomplete",
                    f"{prefix} must be an object",
                )
            )
            continue
        case_id = str(row.get("case_id") or "").strip()
        lane = str(row.get("lane") or "").strip().lower()
        status = row.get("status")
        if not case_id:
            errors.append(
                _err(
                    "plan_case_implementation_incomplete",
                    f"{prefix}.case_id required",
                )
            )
            continue
        if case_id in by_id:
            errors.append(
                _err(
                    "plan_case_implementation_incomplete",
                    f"duplicate case_id {case_id}",
                )
            )
        by_id[case_id] = row
        if lane not in VALID_LANES:
            errors.append(
                _err(
                    "plan_case_implementation_incomplete",
                    f"{prefix}.lane invalid",
                )
            )
        if status not in VALID_CASE_STATUS:
            errors.append(
                _err(
                    "plan_case_implementation_incomplete",
                    f"{prefix}.status invalid",
                )
            )
        if status == "missing":
            errors.append(
                _err(
                    "plan_case_implementation_gap",
                    f"{case_id}: status=missing (authored Plan case not implemented)",
                )
            )

    for source in source_cases:
        case_id = source["case_id"]
        lane = source["lane"]
        row = by_id.get(case_id)
        if row is None:
            errors.append(
                _err(
                    "plan_case_implementation_gap",
                    f"{case_id}: authored in Plan but absent from implementation ledger",
                )
            )
            continue
        row_lane = str(row.get("lane") or "").strip().lower()
        if row_lane and row_lane != lane:
            errors.append(
                _err(
                    "plan_case_implementation_incomplete",
                    f"{case_id}: ledger lane {row_lane} != source lane {lane}",
                )
            )
        status = row.get("status")
        test_ref = str(row.get("test_ref") or "").strip()
        campaign_ref = str(row.get("campaign_ref") or "").strip()
        evidence = str(row.get("evidence") or "").strip()

        if lane == "manual":
            if status not in {"implemented", "blocked_by_dependency", "executed"}:
                errors.append(
                    _err(
                        "plan_case_implementation_gap",
                        f"{case_id}: manual case must be implemented, executed, "
                        "or blocked_by_dependency",
                    )
                )
            if status in {"implemented", "executed"} and not evidence:
                errors.append(
                    _err(
                        "plan_case_implementation_incomplete",
                        f"{case_id}: manual case requires evidence",
                    )
                )
            continue

        if lane in AUTOMATED_LAYER_A and gate in {
            "layer_a",
            "layer_b",
            "e2e_campaign",
        }:
            if status not in {"implemented", "executed"}:
                errors.append(
                    _err(
                        "plan_case_implementation_gap",
                        f"{case_id}: {lane} case must be implemented before "
                        f"{gate} (got {status})",
                    )
                )
            if status in {"implemented", "executed"}:
                if not test_ref:
                    errors.append(
                        _err(
                            "plan_case_implementation_gap",
                            f"{case_id}: test_ref required when implemented",
                        )
                    )
                elif workspace is not None:
                    resolved = _resolve_test_ref(test_ref, workspace)
                    if resolved is None or not resolved.is_file():
                        errors.append(
                            _err(
                                "plan_case_test_ref_missing",
                                f"{case_id}: test_ref file missing ({test_ref})",
                            )
                        )
                    elif resolved.stat().st_size <= 0:
                        errors.append(
                            _err(
                                "plan_case_test_ref_missing",
                                f"{case_id}: test_ref file empty ({test_ref})",
                            )
                        )
                    else:
                        content = resolved.read_text(encoding="utf-8", errors="replace")
                        if case_id not in content and case_id not in evidence:
                            errors.append(
                                _err(
                                    "plan_case_test_ref_unbound",
                                    f"{case_id}: test_ref/evidence must mention "
                                    "the Case ID so Delivery cannot tick blindly",
                                )
                            )
                if not evidence:
                    errors.append(
                        _err(
                            "plan_case_implementation_incomplete",
                            f"{case_id}: evidence required (command or result note)",
                        )
                    )

        if lane in CAMPAIGN_LANES:
            if gate == "layer_a":
                if status not in {
                    "scheduled_campaign",
                    "executed",
                    "blocked_by_dependency",
                }:
                    errors.append(
                        _err(
                            "plan_case_implementation_gap",
                            f"{case_id}: {lane} must be scheduled_campaign|"
                            f"executed|blocked_by_dependency at layer_a (got {status})",
                        )
                    )
                if status == "scheduled_campaign" and not campaign_ref:
                    errors.append(
                        _err(
                            "plan_case_implementation_incomplete",
                            f"{case_id}: campaign_ref required when scheduled_campaign",
                        )
                    )
            if gate == "layer_b" and lane == "integration":
                if status not in {"executed", "blocked_by_dependency"}:
                    errors.append(
                        _err(
                            "plan_case_implementation_gap",
                            f"{case_id}: integration must be executed at layer_b "
                            f"(got {status})",
                        )
                    )
                if status == "executed" and not evidence:
                    errors.append(
                        _err(
                            "plan_case_implementation_incomplete",
                            f"{case_id}: executed integration requires evidence",
                        )
                    )
            if (
                gate == "layer_b"
                and lane == "e2e"
                and status
                not in {
                    "scheduled_campaign",
                    "executed",
                    "blocked_by_dependency",
                }
            ):
                errors.append(
                    _err(
                        "plan_case_implementation_gap",
                        f"{case_id}: e2e must remain scheduled_campaign or "
                        f"executed at layer_b (got {status})",
                    )
                )
            if gate == "e2e_campaign" and lane == "e2e":
                if status not in {"executed", "blocked_by_dependency"}:
                    errors.append(
                        _err(
                            "plan_case_implementation_gap",
                            f"{case_id}: e2e must be executed at e2e_campaign " f"(got {status})",
                        )
                    )
                if status == "executed" and not evidence:
                    errors.append(
                        _err(
                            "plan_case_implementation_incomplete",
                            f"{case_id}: executed e2e requires evidence",
                        )
                    )

    # Extra ledger rows not in source are allowed (notes) but warn via error? skip.

    if top_status == "complete" and errors:
        # keep errors; complete claim is invalid when gaps exist
        pass
    if top_status == "complete":
        gap_codes = {
            "plan_case_implementation_gap",
            "plan_case_test_ref_missing",
            "plan_case_test_ref_unbound",
        }
        if any(e["code"] in gap_codes for e in errors):
            errors.append(
                _err(
                    "plan_case_implementation_incomplete",
                    "status=complete is forbidden while implementation gaps remain",
                )
            )

    if gate in {"layer_a", "layer_b", "e2e_campaign"} and top_status != "complete":
        errors.append(
            _err(
                "plan_case_implementation_incomplete",
                f"status must be complete for {gate}",
            )
        )

    ok = not errors
    code = "ok"
    if not ok:
        priority = [
            "plan_case_source_missing",
            "plan_case_implementation_missing",
            "plan_case_implementation_unread",
            "plan_case_implementation_gap",
            "plan_case_test_ref_missing",
            "plan_case_test_ref_unbound",
            "plan_case_implementation_incomplete",
            "plan_case_implementation_lint_failed",
        ]
        present = {e["code"] for e in errors}
        code = next((c for c in priority if c in present), errors[0]["code"])
    return {
        "ok": ok,
        "code": code,
        "errors": errors,
        "source_case_count": len(source_cases),
        "ledger_case_count": len(by_id),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        type=Path,
        required=True,
        help="YAML/JSON with plan_case_implementation",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        required=True,
        help="YAML/JSON/Markdown source of Plan verification cases",
    )
    parser.add_argument(
        "--gate",
        choices=sorted(VALID_GATES),
        default="layer_a",
        help="Acceptance layer gate",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Repo root to verify test_ref files exist and bind Case IDs",
    )
    args = parser.parse_args(argv)
    ledger_data = _load(args.ledger)
    source_data = _load(args.cases)
    result = lint_plan_case_implementation(
        ledger_data,
        source_data,
        gate=args.gate,
        workspace=args.workspace.resolve() if args.workspace else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
