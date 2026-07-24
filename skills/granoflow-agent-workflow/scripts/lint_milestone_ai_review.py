#!/usr/bin/env python3
"""Validate Milestone AI review and final acceptance records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def _parse_text(text: str, source: Path) -> dict[str, Any]:
    if source.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        if source.suffix.lower() == ".md":
            match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.DOTALL)
            if not match:
                raise ValueError("Markdown input must contain YAML frontmatter")
            text = match.group(1)
        try:
            import yaml
        except ImportError as error:
            raise RuntimeError("PyYAML is required for YAML input") from error
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("input root must be an object")
    return value


def load_record(path: Path) -> dict[str, Any]:
    return _parse_text(path.read_text(encoding="utf-8"), path)


def canonical_plan_sha256(task_plan: dict[str, Any]) -> str:
    reviewed = {key: value for key, value in task_plan.items() if key != "review"}
    canonical = json.dumps(
        reviewed,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _provider_errors(providers: Any) -> list[str]:
    if not isinstance(providers, list) or not providers:
        return ["milestone_ai_review_required: providers must be non-empty"]
    errors: list[str] = []
    for index, provider in enumerate(providers):
        if not isinstance(provider, dict):
            errors.append(f"milestone_ai_review_required: provider[{index}] invalid")
            continue
        disposition = provider.get("disposition")
        result = provider.get("result")
        evidence_ref = provider.get("evidence_ref")
        valid = (
            disposition == "selected"
            and result == "used"
            or disposition == "native_fallback"
            and result == "model_fallback"
            or disposition == "not_required"
            and result == "not_required"
        )
        if not valid:
            errors.append(f"milestone_ai_review_required: provider[{index}] incomplete")
        if disposition != "not_required" and not evidence_ref:
            errors.append(f"milestone_ai_review_required: provider[{index}] evidence missing")
    return errors


def validate_decomposition(
    record: dict[str, Any],
    *,
    allow_legacy_v1: bool = False,
) -> tuple[list[str], dict[str, Any]]:
    schema_version = record.get("schema_version")
    if schema_version == 1 and allow_legacy_v1:
        return [], {"status": "legacy_v1_read_only"}
    if schema_version != 2:
        return ["milestone_ai_review_required: schema_version must be 2"], {}

    task_plan = record.get("task_plan")
    if not isinstance(task_plan, dict):
        return ["milestone_ai_review_required: task_plan missing"], {}

    errors: list[str] = []
    if task_plan.get("status") != "passed":
        errors.append("milestone_ai_review_required: task_plan.status must be passed")

    review = task_plan.get("review")
    if not isinstance(review, dict):
        return [*errors, "milestone_ai_review_required: task_plan.review missing"], {}
    if review.get("mode") != "ai_auto":
        errors.append("milestone_ai_review_required: review.mode must be ai_auto")

    roles = review.get("roles")
    if not isinstance(roles, dict):
        errors.append("milestone_ai_review_required: review roles missing")
    else:
        author = roles.get("author")
        reviewers = roles.get("reviewers")
        verifier = roles.get("final_verifier")
        reviewer_set = set(reviewers) if isinstance(reviewers, list) else set()
        if (
            not author
            or not verifier
            or not reviewer_set
            or author == verifier
            or author in reviewer_set
            or verifier in reviewer_set
        ):
            errors.append(
                "milestone_ai_review_required: author, reviewers, and verifier "
                "must be logically isolated"
            )

    errors.extend(_provider_errors(review.get("providers")))
    grill = review.get("grill")
    if not isinstance(grill, dict):
        errors.append("milestone_ai_review_required: grill ledger missing")
    else:
        generated = grill.get("generated_question_count")
        closed = grill.get("closed_question_count")
        blockers = grill.get("open_blocking_count")
        if not isinstance(generated, int) or generated < 1 or generated != closed:
            errors.append("milestone_ai_review_blocking_findings: grill questions remain open")
        if blockers != 0:
            errors.append("milestone_ai_review_blocking_findings: open blockers must be zero")

    if review.get("final_verifier_status") != "passed":
        errors.append("milestone_ai_review_verifier_failed")
    if review.get("ai_review_status") != "passed":
        errors.append("milestone_ai_review_required: ai_review_status must be passed")

    actual_digest = canonical_plan_sha256(task_plan)
    recorded_digest = review.get("reviewed_plan_sha256")
    if recorded_digest != actual_digest:
        errors.append("milestone_ai_review_plan_digest_mismatch")
    return errors, {"reviewed_plan_sha256": actual_digest}


def validate_execution_ready(
    record: dict[str, Any],
    acceptance_pack: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    errors, details = validate_decomposition(record)
    if errors:
        return errors, details

    reviewed_digest = details["reviewed_plan_sha256"]
    if acceptance_pack.get("status") != "accepted":
        errors.append("milestone_final_acceptance_required")
    if not acceptance_pack.get("ai_decomposition_review_ref"):
        errors.append("milestone_ai_review_required: acceptance review ref missing")
    if acceptance_pack.get("grill_finalizer_status") != "passed":
        errors.append("milestone_final_acceptance_required: finalizer not passed")

    grill_status = acceptance_pack.get("grill_me_status")
    final_status = acceptance_pack.get("final_acceptance_status")
    accepted_by = acceptance_pack.get("accepted_by")
    interactive = (
        grill_status == "shared_understanding_confirmed"
        and final_status == "user_accepted"
        and accepted_by == "user"
    )
    unattended = (
        grill_status == "recommendations_auto_adopted"
        and final_status == "unattended_auto_adopted"
        and accepted_by == "unattended_grant"
    )
    if not interactive and not unattended:
        if not grill_status:
            errors.append("milestone_final_grill_me_required")
        else:
            errors.append("milestone_final_acceptance_required")

    if acceptance_pack.get("authorization_effect") != "none":
        errors.append("milestone_final_acceptance_required: authorization_effect must be none")
    if (
        acceptance_pack.get("ai_decomposition_plan_sha256") != reviewed_digest
        or acceptance_pack.get("accepted_plan_sha256") != reviewed_digest
    ):
        errors.append("milestone_final_acceptance_digest_mismatch")
    return errors, details


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-plan", required=True, type=Path)
    parser.add_argument(
        "--phase",
        required=True,
        choices=("decomposition_passed", "execution_ready"),
    )
    parser.add_argument("--acceptance-pack", type=Path)
    parser.add_argument("--allow-legacy-v1", action="store_true")
    args = parser.parse_args(argv)

    try:
        record = load_record(args.task_plan)
        if args.phase == "decomposition_passed":
            errors, details = validate_decomposition(
                record,
                allow_legacy_v1=args.allow_legacy_v1,
            )
        else:
            if args.acceptance_pack is None:
                parser.error("--acceptance-pack is required for execution_ready")
            acceptance_pack = load_record(args.acceptance_pack)
            errors, details = validate_execution_ready(record, acceptance_pack)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        errors, details = [f"invalid_input: {error}"], {}

    payload = {
        "ok": not errors,
        "phase": args.phase,
        "errors": errors,
        **details,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
