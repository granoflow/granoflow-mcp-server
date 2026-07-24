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
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

VALID_CONCLUSIONS = frozenset({"split", "keep_cohesive", "needs_user_decision"})
SOURCE_FACT_LEDGER_SCHEMA = "granoflow_source_fact_ledger_v1"
JOURNEY_STEP_TRACEABILITY_SCHEMA = "granoflow_journey_step_traceability_v1"
BACKGROUND_ACTIVITY_CONTROL_SCHEMA = "granoflow_background_activity_control_v1"
VALID_SOURCE_KINDS = frozenset(
    {
        "user_stated",
        "necessary_implication",
        "domain_baseline",
        "product_expansion",
    }
)
VALID_FACT_DISPOSITIONS = frozenset({"adopted", "out_of_scope", "conflict"})
VALID_STEP_TYPES = frozenset({"entry", "action", "system_response", "outcome", "failure"})
VALID_INTERACTION_SURFACES = frozenset({"in_app_ui", "os_chrome", "mixed", "service_path"})
VALID_PLATFORM_BOUNDARIES = frozenset({"none", "plugin", "os"})
VALID_TEST_LAYERS = frozenset({"unit", "integration", "e2e"})
VALID_BACKGROUND_ACTIVITY_ROLES = frozenset(
    {
        "none",
        "starts_activity",
        "background_update",
        "protected_control",
        "exit_action",
    }
)
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


def _canonical_sha256(value: dict[str, Any], excluded: set[str]) -> str:
    payload = {key: item for key, item in value.items() if key not in excluded}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def canonical_source_fact_ledger_sha256(ledger: dict[str, Any]) -> str:
    return _canonical_sha256(ledger, {"ledger_sha256", "status", "review"})


def canonical_journey_step_traceability_sha256(traceability: dict[str, Any]) -> str:
    return _canonical_sha256(
        traceability,
        {"traceability_sha256", "status", "review"},
    )


def canonical_background_activity_control_sha256(control: dict[str, Any]) -> str:
    return _canonical_sha256(
        control,
        {"control_sha256", "status", "review"},
    )


def _independent_review_valid(
    value: dict[str, Any],
    *,
    digest: str,
    digest_field: str,
) -> bool:
    review = value.get("review")
    return (
        isinstance(review, dict)
        and _nonempty_str(review.get("author_id"))
        and _nonempty_str(review.get("reviewer_id"))
        and review.get("author_id") != review.get("reviewer_id")
        and review.get("status") == "passed"
        and bool(_nonempty_items(review.get("evidence_refs")))
        and review.get(digest_field) == digest
    )


def lint_coverage(cov: dict[str, Any]) -> dict[str, Any]:
    hits: list[dict[str, str]] = []

    def hit(code: str, journey_id: str, detail: str) -> None:
        hits.append(
            {
                "code": code,
                "journeyId": journey_id,
                "detail": detail,
                "failCode": code
                if code.startswith(
                    ("flow_", "journey_", "source_", "thin_", "screen_", "background_")
                )
                else "product_spec_coverage_incomplete",
            }
        )

    journeys = _list(cov.get("journey_coverage"))
    adopted_journey_ids: set[str] = set()
    for row in journeys:
        if not isinstance(row, dict):
            continue
        if row.get("disposition") != "adopted":
            continue
        jid = str(row.get("journey_id") or row.get("id") or "?")
        adopted_journey_ids.add(jid)
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

    fact_ledger = cov.get("source_fact_ledger")
    traceability = cov.get("journey_step_traceability")
    background_control = cov.get("background_activity_control")
    require_integrity_contracts = cov.get("status") == "ready"
    fact_by_id: dict[str, dict[str, Any]] = {}
    adopted_fact_ids: set[str] = set()
    facts_with_failure_outcomes: set[str] = set()
    mapped_fact_ids: set[str] = set()
    fact_digest: str | None = None
    trace_digest: str | None = None
    seen_step_ids: set[str] = set()

    if not isinstance(fact_ledger, dict):
        if require_integrity_contracts:
            hit(
                "source_fact_ledger_missing",
                "_source_fact_ledger",
                f"status=ready requires {SOURCE_FACT_LEDGER_SCHEMA}",
            )
    else:
        if fact_ledger.get("schema") != SOURCE_FACT_LEDGER_SCHEMA:
            hit(
                "source_fact_ledger_invalid",
                "_source_fact_ledger",
                f"schema must be {SOURCE_FACT_LEDGER_SCHEMA}",
            )
        facts = _list(fact_ledger.get("facts"))
        if not facts:
            hit(
                "source_fact_ledger_invalid",
                "_source_fact_ledger",
                "facts must be a non-empty list",
            )
        for index, fact in enumerate(facts):
            fid = str(fact.get("fact_id") or "?") if isinstance(fact, dict) else "?"
            if not isinstance(fact, dict):
                hit(
                    "source_fact_ledger_invalid",
                    fid,
                    f"facts[{index}] must be an object",
                )
                continue
            if not _nonempty_str(fact.get("fact_id")) or fid in fact_by_id:
                hit(
                    "source_fact_ledger_invalid",
                    fid,
                    f"facts[{index}].fact_id required and unique",
                )
                continue
            fact_by_id[fid] = fact
            source_kind = fact.get("source_kind")
            disposition = fact.get("disposition")
            required_text_fields = (
                "statement",
                "source_ref",
                "source_locator",
                "subject",
                "action",
            )
            if source_kind not in VALID_SOURCE_KINDS or disposition not in VALID_FACT_DISPOSITIONS:
                hit(
                    "source_fact_ledger_invalid",
                    fid,
                    "source_kind or disposition is invalid",
                )
            if any(not _nonempty_str(fact.get(field)) for field in required_text_fields):
                hit(
                    "source_fact_ledger_invalid",
                    fid,
                    "statement/source_ref/source_locator/subject/action are required",
                )
            if not _nonempty_str(fact.get("object")):
                hit("source_fact_ledger_invalid", fid, "object is required")
            for field in ("conditions", "expected_outcomes", "failure_outcomes", "platforms"):
                if not isinstance(fact.get(field), list):
                    hit(
                        "source_fact_ledger_invalid",
                        fid,
                        f"{field} must be a list",
                    )
            if not _nonempty_items(fact.get("expected_outcomes")):
                hit(
                    "source_fact_ledger_invalid",
                    fid,
                    "expected_outcomes must contain an observable result",
                )
            if _nonempty_items(fact.get("failure_outcomes")):
                facts_with_failure_outcomes.add(fid)
            if disposition == "adopted":
                adopted_fact_ids.add(fid)
            elif not _nonempty_str(fact.get("explicit_non_goal_ref")):
                hit(
                    "source_fact_unmapped",
                    fid,
                    "out_of_scope/conflict fact requires explicit_non_goal_ref",
                )
            if source_kind in {"necessary_implication", "domain_baseline"} and (
                not _nonempty_str(fact.get("rationale"))
                or not _nonempty_items(fact.get("evidence_refs"))
            ):
                hit(
                    "source_fact_ledger_invalid",
                    fid,
                    f"{source_kind} requires rationale and evidence_refs",
                )
            if (
                source_kind == "product_expansion"
                and disposition == "adopted"
                and not _nonempty_str(fact.get("confirmation_ref"))
            ):
                hit(
                    "product_expansion_requires_user",
                    fid,
                    "adopted product_expansion requires confirmation_ref",
                )

        fact_digest = canonical_source_fact_ledger_sha256(fact_ledger)
        if fact_ledger.get("ledger_sha256") != fact_digest:
            hit(
                "source_fact_ledger_digest_mismatch",
                "_source_fact_ledger",
                "ledger_sha256 is stale",
            )
        if not _independent_review_valid(
            fact_ledger,
            digest=fact_digest,
            digest_field="reviewed_ledger_sha256",
        ):
            hit(
                "source_fact_ledger_review_failed",
                "_source_fact_ledger",
                "independent review must pass the current ledger digest",
            )
        if fact_ledger.get("status") != "passed":
            hit(
                "source_fact_ledger_invalid",
                "_source_fact_ledger",
                "status must be passed",
            )

    if not isinstance(traceability, dict):
        if require_integrity_contracts:
            hit(
                "journey_step_traceability_missing",
                "_journey_step_traceability",
                f"status=ready requires {JOURNEY_STEP_TRACEABILITY_SCHEMA}",
            )
    else:
        if traceability.get("schema") != JOURNEY_STEP_TRACEABILITY_SCHEMA:
            hit(
                "journey_step_traceability_invalid",
                "_journey_step_traceability",
                f"schema must be {JOURNEY_STEP_TRACEABILITY_SCHEMA}",
            )
        if fact_digest is not None and traceability.get("source_fact_ledger_sha256") != fact_digest:
            hit(
                "journey_step_traceability_digest_mismatch",
                "_journey_step_traceability",
                "source_fact_ledger_sha256 is stale",
            )
        traced_journey_ids: set[str] = set()
        for index, journey in enumerate(_list(traceability.get("journeys"))):
            if not isinstance(journey, dict):
                hit(
                    "journey_step_traceability_invalid",
                    "?",
                    f"journeys[{index}] must be an object",
                )
                continue
            jid = str(journey.get("journey_id") or "?")
            if not _nonempty_str(journey.get("journey_id")) or jid in traced_journey_ids:
                hit(
                    "journey_step_traceability_invalid",
                    jid,
                    "journey_id is required and unique",
                )
                continue
            traced_journey_ids.add(jid)
            steps = _list(journey.get("steps"))
            step_types: set[str] = set()
            journey_fact_ids: set[str] = set()
            has_boundary = False
            has_failure = False
            sequences: list[int] = []
            for step_index, step in enumerate(steps):
                sid = str(step.get("step_id") or "?") if isinstance(step, dict) else "?"
                if not isinstance(step, dict):
                    hit(
                        "journey_step_traceability_invalid",
                        jid,
                        f"steps[{step_index}] must be an object",
                    )
                    continue
                if not _nonempty_str(step.get("step_id")) or sid in seen_step_ids:
                    hit(
                        "journey_step_traceability_invalid",
                        jid,
                        f"steps[{step_index}].step_id required and globally unique",
                    )
                else:
                    seen_step_ids.add(sid)
                sequence = step.get("sequence")
                if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
                    hit(
                        "journey_step_traceability_invalid",
                        jid,
                        f"{sid}.sequence must be a positive integer",
                    )
                else:
                    sequences.append(sequence)
                step_type = step.get("step_type")
                surface = step.get("interaction_surface")
                boundary = step.get("platform_boundary")
                layers = set(_nonempty_items(step.get("required_test_layers")))
                refs = set(_nonempty_items(step.get("source_fact_ids")))
                step_types.add(str(step_type))
                journey_fact_ids.update(str(ref) for ref in refs)
                mapped_fact_ids.update(str(ref) for ref in refs)
                if step_type not in VALID_STEP_TYPES:
                    hit(
                        "journey_step_traceability_invalid",
                        jid,
                        f"{sid}.step_type invalid",
                    )
                if surface not in VALID_INTERACTION_SURFACES:
                    hit(
                        "journey_step_traceability_invalid",
                        jid,
                        f"{sid}.interaction_surface invalid",
                    )
                if boundary not in VALID_PLATFORM_BOUNDARIES:
                    hit(
                        "journey_step_traceability_invalid",
                        jid,
                        f"{sid}.platform_boundary invalid",
                    )
                if not refs or refs - set(fact_by_id):
                    hit(
                        "journey_step_source_missing",
                        jid,
                        f"{sid} requires known source_fact_ids",
                    )
                if not layers or layers - VALID_TEST_LAYERS:
                    hit(
                        "journey_step_test_layers_invalid",
                        jid,
                        f"{sid}.required_test_layers invalid",
                    )
                if not _nonempty_str(step.get("actor")) or not _nonempty_str(step.get("action")):
                    hit(
                        "journey_step_traceability_invalid",
                        jid,
                        f"{sid}.actor and action are required",
                    )
                if not _nonempty_str(step.get("expected_observation")):
                    hit(
                        "journey_step_observation_missing",
                        jid,
                        f"{sid}.expected_observation required",
                    )
                if step_type == "entry" and not _nonempty_str(step.get("entry_ref")):
                    hit(
                        "journey_entry_missing",
                        jid,
                        f"{sid}.entry_ref required for entry step",
                    )
                if (
                    step_type == "action"
                    and surface in {"in_app_ui", "os_chrome", "mixed"}
                    and not _nonempty_str(step.get("control"))
                ):
                    hit(
                        "interactive_control_action_missing",
                        jid,
                        f"{sid}.control required for user-visible action",
                    )
                if boundary in {"plugin", "os"}:
                    has_boundary = True
                    required_boundary_layers = (
                        {"unit", "e2e"}
                        if surface in {"os_chrome", "mixed"}
                        else {"unit", "integration"}
                    )
                    if not required_boundary_layers.issubset(layers):
                        hit(
                            "platform_boundary_test_missing",
                            jid,
                            f"{sid} requires {sorted(required_boundary_layers)}",
                        )
                    if not _nonempty_items(step.get("failure_modes")):
                        hit(
                            "platform_boundary_failure_modes_missing",
                            jid,
                            f"{sid}.failure_modes required for platform boundary",
                        )
                if step_type == "failure":
                    has_failure = True
            if not steps:
                hit(
                    "journey_step_traceability_invalid",
                    jid,
                    "steps must be a non-empty list",
                )
            if sequences and sequences != list(range(1, len(sequences) + 1)):
                hit(
                    "journey_step_sequence_invalid",
                    jid,
                    "step sequence must be contiguous and ordered from 1",
                )
            for required_type in ("entry", "action", "outcome"):
                if required_type not in step_types:
                    hit(
                        "journey_entry_missing"
                        if required_type == "entry"
                        else "journey_step_traceability_invalid",
                        jid,
                        f"journey requires a {required_type} step",
                    )
            if (has_boundary or journey_fact_ids & facts_with_failure_outcomes) and not has_failure:
                hit(
                    "journey_failure_step_missing",
                    jid,
                    "platform boundary or source failure outcome requires a failure step",
                )

        missing_journeys = sorted(adopted_journey_ids - traced_journey_ids)
        if missing_journeys:
            hit(
                "journey_step_traceability_missing",
                "_journey_step_traceability",
                f"adopted journeys missing: {missing_journeys}",
            )
        unknown_journeys = sorted(traced_journey_ids - adopted_journey_ids)
        if unknown_journeys:
            hit(
                "journey_step_traceability_invalid",
                "_journey_step_traceability",
                f"unknown/non-adopted journeys traced: {unknown_journeys}",
            )

        trace_digest = canonical_journey_step_traceability_sha256(traceability)
        if traceability.get("traceability_sha256") != trace_digest:
            hit(
                "journey_step_traceability_digest_mismatch",
                "_journey_step_traceability",
                "traceability_sha256 is stale",
            )
        if not _independent_review_valid(
            traceability,
            digest=trace_digest,
            digest_field="reviewed_traceability_sha256",
        ):
            hit(
                "journey_step_traceability_review_failed",
                "_journey_step_traceability",
                "independent review must pass the current traceability digest",
            )
        replay = traceability.get("semantic_replay")
        if not (
            isinstance(replay, dict)
            and replay.get("status") == "passed"
            and replay.get("missing_fact_ids") == []
            and replay.get("distorted_fact_ids") == []
            and _nonempty_items(replay.get("evidence_refs"))
        ):
            hit(
                "semantic_replay_failed",
                "_journey_step_traceability",
                "semantic_replay must pass with no missing or distorted facts",
            )
        if traceability.get("status") != "passed":
            hit(
                "journey_step_traceability_invalid",
                "_journey_step_traceability",
                "status must be passed",
            )

    if not isinstance(background_control, dict):
        if require_integrity_contracts:
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                f"status=ready requires {BACKGROUND_ACTIVITY_CONTROL_SCHEMA}",
            )
    else:
        if background_control.get("schema") != BACKGROUND_ACTIVITY_CONTROL_SCHEMA:
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                f"schema must be {BACKGROUND_ACTIVITY_CONTROL_SCHEMA}",
            )
        if (
            fact_digest is not None
            and background_control.get("source_fact_ledger_sha256") != fact_digest
        ):
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                "source_fact_ledger_sha256 is stale",
            )
        if (
            trace_digest is not None
            and background_control.get("journey_step_traceability_sha256") != trace_digest
        ):
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                "journey_step_traceability_sha256 is stale",
            )

        classifications = _list(background_control.get("fact_classifications"))
        classified_fact_ids: set[str] = set()
        active_fact_ids: set[str] = set()
        for index, classification in enumerate(classifications):
            if not isinstance(classification, dict):
                hit(
                    "background_activity_fact_unclassified",
                    "_background_activity_control",
                    f"fact_classifications[{index}] must be an object",
                )
                continue
            fid = str(classification.get("fact_id") or "?")
            role = classification.get("role")
            if (
                not _nonempty_str(classification.get("fact_id"))
                or fid in classified_fact_ids
                or fid not in adopted_fact_ids
            ):
                hit(
                    "background_activity_fact_unclassified",
                    fid,
                    "each adopted fact must be classified exactly once",
                )
                continue
            classified_fact_ids.add(fid)
            if role not in VALID_BACKGROUND_ACTIVITY_ROLES:
                hit(
                    "background_activity_fact_unclassified",
                    fid,
                    f"role must be one of {sorted(VALID_BACKGROUND_ACTIVITY_ROLES)}",
                )
            elif role != "none":
                active_fact_ids.add(fid)

        missing_classifications = sorted(adopted_fact_ids - classified_fact_ids)
        if missing_classifications:
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                f"adopted facts missing classification: {missing_classifications}",
            )

        activity_fact_ids: set[str] = set()
        activity_ids: set[str] = set()
        activities = _list(background_control.get("activities"))
        for index, activity in enumerate(activities):
            prefix = f"activities[{index}]"
            if not isinstance(activity, dict):
                hit(
                    "background_activity_fact_unclassified",
                    "_background_activity_control",
                    f"{prefix} must be an object",
                )
                continue
            activity_id = str(activity.get("activity_id") or "?")
            if not _nonempty_str(activity.get("activity_id")) or activity_id in activity_ids:
                hit(
                    "background_activity_fact_unclassified",
                    activity_id,
                    f"{prefix}.activity_id is required and unique",
                )
                continue
            activity_ids.add(activity_id)
            source_fact_ids = set(_nonempty_items(activity.get("source_fact_ids")))
            journey_step_ids = set(_nonempty_items(activity.get("journey_step_ids")))
            activity_fact_ids.update(str(item) for item in source_fact_ids)
            if (
                not source_fact_ids
                or not source_fact_ids.issubset(active_fact_ids)
                or not journey_step_ids
                or not journey_step_ids.issubset(seen_step_ids)
            ):
                hit(
                    "background_activity_fact_unclassified",
                    activity_id,
                    "activity requires classified source_fact_ids and known journey_step_ids",
                )
            if activity.get("continues_after_user_action") is not True:
                hit(
                    "background_activity_fact_unclassified",
                    activity_id,
                    "continues_after_user_action must be true",
                )
            background_events = set(_nonempty_items(activity.get("background_events")))
            allowed_changes = set(_nonempty_items(activity.get("allowed_background_changes")))
            protected_state = set(_nonempty_items(activity.get("must_not_change")))
            controls = set(_nonempty_items(activity.get("controls_that_must_keep_working")))
            exit_actions = set(_nonempty_items(activity.get("ways_to_exit")))
            layers = set(_nonempty_items(activity.get("required_test_layers")))
            if not background_events:
                hit(
                    "background_activity_fact_unclassified",
                    activity_id,
                    "background_events must name observable updates",
                )
            if not allowed_changes or not protected_state or allowed_changes & protected_state:
                hit(
                    "background_state_write_scope_missing",
                    activity_id,
                    "declare disjoint allowed_background_changes and must_not_change",
                )
            if not controls:
                hit(
                    "background_event_overwrites_user_state",
                    activity_id,
                    "controls_that_must_keep_working must name protected control classes",
                )
            if not exit_actions:
                hit(
                    "background_activity_exit_missing",
                    activity_id,
                    "ways_to_exit must name how the user ends or leaves the activity",
                )
            if not layers or layers - VALID_TEST_LAYERS:
                hit(
                    "background_activity_fact_unclassified",
                    activity_id,
                    "required_test_layers contains an invalid layer",
                )
            if activity.get("user_visible") is True and not {
                "integration",
                "e2e",
            }.issubset(layers):
                hit(
                    "component_path_required",
                    activity_id,
                    "user-visible background activity requires integration and e2e",
                )

        missing_activity_facts = sorted(active_fact_ids - activity_fact_ids)
        if missing_activity_facts:
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                f"background-activity facts missing activity mapping: {missing_activity_facts}",
            )
        if not active_fact_ids and activities:
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                "activities must be empty when every adopted fact is classified none",
            )

        control_digest = canonical_background_activity_control_sha256(background_control)
        if background_control.get("control_sha256") != control_digest:
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                "control_sha256 is stale",
            )
        if not _independent_review_valid(
            background_control,
            digest=control_digest,
            digest_field="reviewed_control_sha256",
        ):
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                "independent review must pass the current background activity digest",
            )
        replay = background_control.get("semantic_replay")
        if not (
            isinstance(replay, dict)
            and replay.get("status") == "passed"
            and replay.get("missing_fact_ids") == []
            and replay.get("unknown_fact_ids") == []
            and _nonempty_items(replay.get("evidence_refs"))
        ):
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                "semantic_replay must classify every adopted fact with no unknowns",
            )
        if background_control.get("status") != "passed":
            hit(
                "background_activity_fact_unclassified",
                "_background_activity_control",
                "status must be passed",
            )

    for fid in adopted_fact_ids - mapped_fact_ids:
        fact = fact_by_id[fid]
        if not _nonempty_items(fact.get("mapped_acceptance_ids")):
            hit(
                "source_fact_unmapped",
                fid,
                "adopted fact must map to a journey step or acceptance id",
            )

    checklist = cov.get("checklist")
    if isinstance(checklist, dict) and cov.get("status") == "ready":
        required_flags = [
            "every_adopted_journey_decomposition_pass_completed",
            "every_adopted_journey_has_decomposition_conclusion",
            "every_adopted_acceptance_has_stress_path",
            "no_unattended_decision_changing_thin_gap_auto_accept",
            "screen_detail_registration_adopted",
            "source_fact_ledger_reviewed",
            "every_adopted_fact_mapped",
            "every_adopted_journey_step_traced",
            "semantic_replay_passed",
            "every_adopted_fact_background_activity_classified",
            "background_activity_control_reviewed",
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
