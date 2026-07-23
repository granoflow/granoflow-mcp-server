#!/usr/bin/env python3
"""Lint Project Work product_spec_coverage for flow-decomposition gates.

Validates operation-flow / serial-gate page-count conclusions + stress paths,
plus screen_detail_registration / ui_details provenance when status=ready.
Does not treat risk labels as a reason to force multi-screen.

Accepts JSON (preferred) or YAML when PyYAML is available. Input may be a full
Project Work document or a bare product_spec_coverage object.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_CONCLUSIONS = frozenset({"split", "keep_cohesive", "needs_user_decision"})
VALID_UI_DETAIL_SOURCES = frozenset(
    {
        "user_confirmed",
        "from_product_doc",
        "from_user_story",
        "inferred",
    }
)
REQUIRED_DESIGN_TRUTH_PRIORITY = (
    "user_confirmed",
    "from_product_doc",
    "from_user_story",
    "inferred",
    "ai_live_inference",
)


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover
            raise SystemExit("PyYAML is required to lint .yaml/.yml; pass JSON instead.") from exc
        return yaml.safe_load(text)
    return json.loads(text)


def _coverage(doc: Any) -> dict[str, Any]:
    if not isinstance(doc, dict):
        raise ValueError("document must be an object")
    if "product_spec_coverage" in doc:
        cov = doc["product_spec_coverage"]
    elif "journey_coverage" in doc:
        cov = doc
    else:
        raise ValueError(
            "expected product_spec_coverage or a bare coverage object with journey_coverage"
        )
    if not isinstance(cov, dict):
        raise ValueError("product_spec_coverage must be an object")
    return cov


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _nonempty_items(value: Any) -> list[Any]:
    out: list[Any] = []
    for item in _list(value):
        if _nonempty_str(item):
            out.append(str(item).strip())
        elif isinstance(item, dict) and (
            _nonempty_str(item.get("id"))
            or _nonempty_str(item.get("title"))
            or _nonempty_str(item.get("name"))
        ):
            out.append(item)
    return out


def _operation_flow_present(decomp: dict[str, Any]) -> bool:
    flow = decomp.get("operation_flow")
    if not isinstance(flow, dict):
        return False
    if _nonempty_items(flow.get("user_operations")):
        return True
    return _nonempty_str(flow.get("summary"))


def lint_coverage(cov: dict[str, Any]) -> dict[str, Any]:
    hits: list[dict[str, str]] = []

    def hit(code: str, journey_id: str, detail: str) -> None:
        hits.append(
            {
                "code": code,
                "journeyId": journey_id,
                "detail": detail,
                "failCode": code
                if code.startswith(("flow_", "journey_", "thin_", "screen_"))
                else "product_spec_coverage_incomplete",
            }
        )

    journeys = _list(cov.get("journey_coverage"))
    for row in journeys:
        if not isinstance(row, dict):
            continue
        if row.get("disposition") != "adopted":
            continue
        jid = str(row.get("journey_id") or row.get("id") or "?")
        decomp = row.get("decomposition")
        if not isinstance(decomp, dict):
            hit(
                "flow_decomposition_pass_missing",
                jid,
                "adopted journey missing decomposition object",
            )
            continue
        if decomp.get("pass_completed") is not True:
            hit(
                "flow_decomposition_pass_missing",
                jid,
                "pass_completed must be true",
            )
        if not _operation_flow_present(decomp):
            hit(
                "flow_decomposition_operation_flow_missing",
                jid,
                "operation_flow needs user_operations or non-empty summary",
            )

        serial_gates = _nonempty_items(decomp.get("serial_gates"))
        conclusion = decomp.get("conclusion")
        if conclusion not in VALID_CONCLUSIONS:
            hit(
                "flow_decomposition_conclusion_missing",
                jid,
                "conclusion must be split | keep_cohesive | needs_user_decision",
            )
        elif conclusion == "split":
            concluded = [s for s in _list(decomp.get("concluded_screen_ids")) if _nonempty_str(s)]
            if len(concluded) < 2:
                hit(
                    "flow_decomposition_split_without_screens",
                    jid,
                    "split requires at least two concluded_screen_ids",
                )
            if not serial_gates:
                hit(
                    "flow_decomposition_split_without_serial_gate",
                    jid,
                    "split requires at least one serial_gate",
                )
            if not _nonempty_str(decomp.get("accepted_split_summary")):
                hit(
                    "flow_decomposition_conclusion_missing",
                    jid,
                    "split requires accepted_split_summary",
                )
        elif conclusion == "keep_cohesive":
            if serial_gates:
                hit(
                    "flow_decomposition_keep_with_serial_gates",
                    jid,
                    "keep_cohesive forbids non-empty serial_gates",
                )
            if not _nonempty_str(decomp.get("rejected_split_summary")):
                hit(
                    "flow_decomposition_keep_without_rejected_split",
                    jid,
                    "keep_cohesive requires rejected_split_summary",
                )

        acceptance_ids = [a for a in _list(row.get("acceptance_ids")) if _nonempty_str(a)]
        stress_paths = _list(row.get("stress_paths"))
        by_acceptance: dict[str, dict[str, Any]] = {}
        for path in stress_paths:
            if not isinstance(path, dict):
                continue
            aid = path.get("acceptance_id")
            if _nonempty_str(aid):
                by_acceptance[str(aid)] = path
        for aid in acceptance_ids:
            path = by_acceptance.get(aid)
            if path is None:
                hit(
                    "journey_stress_path_incomplete",
                    jid,
                    f"missing stress_path for acceptance_id={aid}",
                )
                continue
            if not _nonempty_str(path.get("entry")):
                hit(
                    "journey_stress_path_incomplete",
                    jid,
                    f"stress_path entry missing for {aid}",
                )
            if not _nonempty_str(path.get("success_exit")):
                hit(
                    "journey_stress_path_incomplete",
                    jid,
                    f"stress_path success_exit missing for {aid}",
                )
            fail_exit = path.get("failure_exit")
            if fail_exit is not None and not _nonempty_str(fail_exit):
                hit(
                    "journey_stress_path_incomplete",
                    jid,
                    f"stress_path failure_exit empty for {aid}",
                )

    for gap in _list(cov.get("gap_fills")):
        if not isinstance(gap, dict):
            continue
        if (
            gap.get("decision_changing") is True
            and gap.get("mode") == "unattended"
            and gap.get("provenance") == "agent_recommendation_adopted"
        ):
            hit(
                "thin_product_doc_gap_requires_user",
                str(gap.get("gap_id") or "?"),
                "unattended must not auto-adopt decision-changing thin-doc gaps",
            )

    for row in _list(cov.get("screen_coverage")):
        if not isinstance(row, dict):
            continue
        sid = str(row.get("screen_id") or row.get("id") or "?")
        for detail in _list(row.get("ui_details")):
            if not isinstance(detail, dict):
                hit(
                    "screen_ui_details_source_invalid",
                    sid,
                    "ui_details entry must be an object",
                )
                continue
            source = detail.get("source")
            if source not in VALID_UI_DETAIL_SOURCES:
                hit(
                    "screen_ui_details_source_invalid",
                    sid,
                    "ui_details.source must be user_confirmed | from_product_doc | "
                    "from_user_story | inferred",
                )
            if not _nonempty_str(detail.get("detail_id")) and not _nonempty_str(detail.get("id")):
                hit(
                    "screen_ui_details_source_invalid",
                    sid,
                    "ui_details entry needs detail_id",
                )
            if not _nonempty_str(detail.get("statement")):
                hit(
                    "screen_ui_details_source_invalid",
                    sid,
                    "ui_details entry needs statement",
                )

    if cov.get("status") == "ready":
        registration = cov.get("screen_detail_registration")
        if not isinstance(registration, dict):
            hit(
                "screen_detail_registration_missing",
                "_screen_detail_registration",
                "status=ready requires screen_detail_registration object",
            )
        else:
            if registration.get("status") != "adopted":
                hit(
                    "screen_detail_registration_missing",
                    "_screen_detail_registration",
                    "screen_detail_registration.status must be adopted",
                )
            priority = [
                str(item).strip()
                for item in _list(registration.get("design_truth_priority"))
                if _nonempty_str(item)
            ]
            if tuple(priority) != REQUIRED_DESIGN_TRUTH_PRIORITY:
                hit(
                    "screen_detail_registration_missing",
                    "_screen_detail_registration",
                    "design_truth_priority must be " + " > ".join(REQUIRED_DESIGN_TRUTH_PRIORITY),
                )
            if registration.get("init_html_policy") != "design_spec_and_shell_only":
                hit(
                    "screen_detail_registration_missing",
                    "_screen_detail_registration",
                    "init_html_policy must be design_spec_and_shell_only",
                )

    checklist = cov.get("checklist")
    if isinstance(checklist, dict) and cov.get("status") == "ready":
        required_flags = [
            "every_adopted_journey_decomposition_pass_completed",
            "every_adopted_journey_has_decomposition_conclusion",
            "every_adopted_acceptance_has_stress_path",
            "no_unattended_decision_changing_thin_gap_auto_accept",
            "screen_detail_registration_adopted",
        ]
        for flag in required_flags:
            if checklist.get(flag) is not True:
                hit(
                    "product_spec_coverage_incomplete",
                    "_checklist",
                    f"status=ready but checklist.{flag} is not true",
                )

    primary_fail = hits[0]["failCode"] if hits else None
    return {
        "ok": len(hits) == 0,
        "failCode": primary_fail,
        "hits": hits,
        "hitCount": len(hits),
    }


def lint_document(doc: Any, *, path: str | None = None) -> dict[str, Any]:
    result = lint_coverage(_coverage(doc))
    result["path"] = path
    return result


def lint_path(path: Path) -> dict[str, Any]:
    return lint_document(_load(path), path=str(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint product_spec_coverage flow-decomposition gates"
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Project Work JSON/YAML or bare coverage JSON/YAML",
    )
    args = parser.parse_args(argv)
    results = [lint_path(p) for p in args.paths]
    payload = {
        "ok": all(r["ok"] for r in results),
        "failCode": next((r["failCode"] for r in results if not r["ok"]), None),
        "files": results,
        "hitCount": sum(int(r["hitCount"]) for r in results),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
