#!/usr/bin/env python3
"""Validate App Shell orientation coverage and Widget Catalog projection."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_shell_selection_v2"
ORIENTATIONS = {"portrait", "landscape"}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_WIDGET_ROLES = {
    "app_shell.top_bar",
    "app_shell.bottom_navigation",
}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.fullmatch(value) is not None


def _layout_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("platform_id")), str(row.get("orientation"))


def validate_shell_selection(data: dict[str, Any]) -> dict[str, Any]:
    record = data.get("shell_selection", data)
    errors: list[dict[str, str]] = []

    def hit(code: str, detail: str) -> None:
        errors.append({"code": code, "detail": detail})

    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        return {
            "ok": False,
            "code": "shell_orientation_requirements_missing",
            "errors": [
                {
                    "code": "shell_orientation_requirements_missing",
                    "detail": f"record schema must be {SCHEMA}",
                }
            ],
        }

    mode = record.get("mode")
    if mode not in {"interactive_triad", "unattended_single"}:
        hit("shell_orientation_requirements_missing", "mode invalid")

    requirements = record.get("required_layout_families")
    required_keys: set[tuple[str, str]] = set()
    if not isinstance(requirements, list) or not requirements:
        hit("shell_orientation_requirements_missing", "required layouts missing")
    else:
        for row in requirements:
            if not isinstance(row, dict) or not _text(row.get("platform_id")):
                hit("shell_orientation_requirements_missing", "platform id missing")
                continue
            orientations = row.get("orientations")
            if (
                not isinstance(orientations, list)
                or not orientations
                or len(orientations) != len(set(orientations))
                or not set(orientations).issubset(ORIENTATIONS)
            ):
                hit(
                    "shell_orientation_requirements_missing",
                    f"{row.get('platform_id')} orientations invalid",
                )
                continue
            for orientation in orientations:
                required_keys.add((row["platform_id"], orientation))

    candidates = record.get("candidates")
    expected_count = 3 if mode == "interactive_triad" else 1
    if not isinstance(candidates, list) or len(candidates) != expected_count:
        hit("shell_required_layout_missing", "candidate count invalid")
        candidates = []

    candidate_ids: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or not _text(candidate.get("option_id")):
            hit("shell_required_layout_missing", "candidate id missing")
            continue
        option_id = candidate["option_id"]
        candidate_ids.append(option_id)
        if not _text(candidate.get("fitted_to_design_spec_option_id")):
            hit("shell_spec_mismatch", f"{option_id} has no fitted Spec")
        if not _text(candidate.get("artifact_ref")) or not _hash(candidate.get("artifact_sha256")):
            hit("shell_required_layout_missing", f"{option_id} artifact invalid")
        layouts = candidate.get("layouts")
        if not isinstance(layouts, list):
            hit("shell_required_layout_missing", f"{option_id} layouts missing")
            continue
        actual_keys = {_layout_key(layout) for layout in layouts if isinstance(layout, dict)}
        if actual_keys != required_keys:
            hit(
                "shell_required_layout_missing",
                f"{option_id} must cover exactly the required layouts",
            )
        for layout in layouts:
            if not isinstance(layout, dict):
                continue
            key = _layout_key(layout)
            if not _text(layout.get("top_bar_widget_id")):
                hit("shell_top_bar_missing", f"{option_id} {key} top bar missing")
            if not _text(layout.get("bottom_navigation_widget_id")):
                hit(
                    "shell_bottom_navigation_missing",
                    f"{option_id} {key} bottom navigation missing",
                )

    if len(candidate_ids) != len(set(candidate_ids)):
        hit("shell_required_layout_missing", "candidate ids must be unique")

    selected_id = record.get("selected_option_id")
    selected = next(
        (candidate for candidate in candidates if candidate.get("option_id") == selected_id),
        None,
    )
    if selected_id is not None and selected is None:
        hit("shell_required_layout_missing", "selected option invalid")

    projection = record.get("widget_catalog_projection")
    if selected is not None:
        if (
            not isinstance(projection, dict)
            or projection.get("status") != "passed"
            or projection.get("source_shell_artifact_sha256") != selected.get("artifact_sha256")
        ):
            hit(
                "shell_widget_catalog_projection_invalid",
                "projection must bind the selected Shell SHA",
            )
        else:
            widgets = projection.get("widgets")
            if not isinstance(widgets, list):
                widgets = []
            by_role = {widget.get("role"): widget for widget in widgets if isinstance(widget, dict)}
            if set(by_role) != REQUIRED_WIDGET_ROLES:
                hit(
                    "shell_widget_catalog_projection_invalid",
                    "projection needs both mandatory roles",
                )
            for role in REQUIRED_WIDGET_ROLES:
                widget = by_role.get(role)
                if not isinstance(widget, dict) or not _text(widget.get("widget_id")):
                    hit(
                        "shell_widget_catalog_projection_invalid",
                        f"{role} widget id missing",
                    )
                    continue
                variants = widget.get("variants")
                variant_rows = variants if isinstance(variants, list) else []
                variant_keys = {
                    _layout_key(variant) for variant in variant_rows if isinstance(variant, dict)
                }
                if variant_keys != required_keys:
                    hit(
                        "shell_widget_catalog_projection_invalid",
                        f"{role} variants do not cover required layouts",
                    )
                if widget.get("derived_from_sha256") != selected.get("artifact_sha256"):
                    hit(
                        "shell_widget_catalog_projection_invalid",
                        f"{role} derived_from SHA mismatch",
                    )

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
        result = validate_shell_selection(value)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "shell_orientation_requirements_missing",
            "errors": [
                {
                    "code": "shell_orientation_requirements_missing",
                    "detail": str(error),
                }
            ],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
