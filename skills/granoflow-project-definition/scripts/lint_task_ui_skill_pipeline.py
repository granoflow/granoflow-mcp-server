#!/usr/bin/env python3
"""Validate evidenced, host-owned Task UI design capability routing."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "task_ui_skill_pipeline_v1"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
ALWAYS_REQUIRED = {
    "ui_expression_exploration",
    "high_fidelity_html_authoring",
    "visual_quality_audit",
    "platform_design_guidance",
    "final_design_review",
}
CONDITIONAL = {"advanced_motion_authoring"}
ALL_CAPABILITIES = ALWAYS_REQUIRED | CONDITIONAL
APPLE_PLATFORMS = {"ios", "macos", "tvos", "watchos", "visionos"}


def _hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.fullmatch(value) is not None


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_task_ui_skill_pipeline(data: dict[str, Any]) -> dict[str, Any]:
    record = data.get("task_ui_skill_pipeline", data)
    errors: list[dict[str, str]] = []

    def hit(code: str, detail: str) -> None:
        errors.append({"code": code, "detail": detail})

    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        return {
            "ok": False,
            "code": "task_ui_skill_pipeline_required",
            "errors": [
                {
                    "code": "task_ui_skill_pipeline_required",
                    "detail": f"record schema must be {SCHEMA}",
                }
            ],
        }

    platforms = record.get("platform_ids")
    stack_kinds = record.get("stack_kinds")
    if not isinstance(platforms, list) or not platforms:
        hit("task_ui_skill_pipeline_required", "platform_ids required")
        platforms = []
    if not isinstance(stack_kinds, list) or not stack_kinds:
        hit("task_ui_skill_pipeline_required", "stack_kinds required")
        stack_kinds = []
    input_shas = record.get("input_shas")
    required_inputs = {
        "baseline",
        "widget_catalog",
        "platform_matrix",
        "component_effect_matrix",
    }
    if not isinstance(input_shas, dict) or any(
        not _hash(input_shas.get(field)) for field in required_inputs
    ):
        hit("task_ui_skill_evidence_missing", "all input SHA values are required")

    rows = record.get("capabilities")
    if not isinstance(rows, list):
        rows = []
    by_id = {
        row.get("capability_id"): row
        for row in rows
        if isinstance(row, dict) and _text(row.get("capability_id"))
    }
    if len(by_id) != len(rows) or set(by_id) != ALL_CAPABILITIES:
        hit(
            "task_ui_skill_pipeline_required",
            "each defined capability must appear exactly once",
        )

    advanced_required = record.get("advanced_motion_required") is True
    for capability_id in ALL_CAPABILITIES:
        row = by_id.get(capability_id)
        if not isinstance(row, dict):
            continue
        applicable = row.get("condition_status") == "applicable"
        if capability_id in ALWAYS_REQUIRED and not applicable:
            hit("task_ui_skill_capability_missing", f"{capability_id} must apply")
        if capability_id == "advanced_motion_authoring":
            expected = "applicable" if advanced_required else "not_applicable"
            if row.get("condition_status") != expected:
                hit(
                    "task_ui_skill_pipeline_required",
                    "advanced motion condition does not match matrix",
                )
        if not applicable:
            continue

        provider = row.get("selected_provider")
        if not isinstance(provider, dict):
            hit("task_ui_skill_capability_missing", f"{capability_id} provider missing")
            continue
        provider_id = provider.get("provider_id")
        provider_kind = provider.get("kind")
        if provider_kind not in {"external_skill", "native"} or not _text(provider_id):
            hit("task_ui_skill_capability_missing", f"{capability_id} provider invalid")
        if provider.get("availability") != "available":
            hit("task_ui_skill_capability_missing", f"{capability_id} unavailable")
        if provider.get("result") not in {"used", "model_fallback"}:
            hit("task_ui_skill_capability_missing", f"{capability_id} result invalid")
        if not _text(provider.get("discovery_evidence")):
            hit("task_ui_skill_evidence_missing", f"{capability_id} discovery missing")
        if not _hash(provider.get("input_sha256")) or not _hash(
            provider.get("output_artifact_sha256")
        ):
            hit("task_ui_skill_evidence_missing", f"{capability_id} artifact evidence missing")
        if provider.get("authorization_effect") != "none":
            hit("task_ui_skill_invocation_unsafe", f"{capability_id} changes authority")

        expected_policy = (
            "artifact_only"
            if capability_id in {"ui_expression_exploration", "high_fidelity_html_authoring"}
            else "review_only"
        )
        if provider.get("mutation_policy") != expected_policy:
            hit("task_ui_skill_invocation_unsafe", f"{capability_id} mutation policy invalid")
        if (
            capability_id == "final_design_review"
            and provider.get("mutation_authorization") != "none"
        ):
            hit("task_ui_skill_invocation_unsafe", "final review must be mutation-free")

        normalized_id = str(provider_id).lower()
        if "gsap" in normalized_id and not set(stack_kinds) & {"web", "html", "javascript"}:
            hit("task_ui_skill_invocation_unsafe", "GSAP selected for a non-Web stack")
        if "apple-design" in normalized_id and not set(platforms) & APPLE_PLATFORMS:
            hit("task_ui_skill_invocation_unsafe", "Apple Design selected without Apple platform")

    if record.get("status") != "passed":
        hit("task_ui_skill_pipeline_required", "pipeline status must be passed")

    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("root must be an object")
        result = validate_task_ui_skill_pipeline(value)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "task_ui_skill_pipeline_required",
            "errors": [{"code": "task_ui_skill_pipeline_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
