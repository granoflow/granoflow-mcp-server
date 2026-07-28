#!/usr/bin/env python3
"""Validate prototype HTML uses canonical Granoflow device shell markers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REGISTRY = (
    Path(__file__).resolve().parents[1] / "assets" / "device-shells" / "device-shell-registry.json"
)
ATTR_RE = re.compile(
    r'data-device-shell\s*=\s*["\']([^"\']+)["\']',
    re.I,
)
LAYOUT_RE = re.compile(
    r'data-layout-family\s*=\s*["\']([^"\']+)["\']',
    re.I,
)
PRODUCT_UI_RE = re.compile(
    r'data-product-ui\s*=\s*["\']true["\']',
    re.I,
)


def load_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or REGISTRY
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "granoflow.device_shell_registry":
        raise ValueError("invalid device shell registry schema")
    profiles = data.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("device shell registry has no profiles")
    return data


def profile_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in registry.get("profiles", []):
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            result[row["id"]] = row
    return result


def lint_html(
    text: str,
    *,
    required_profile_ids: set[str],
    profiles: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def hit(code: str, detail: str) -> None:
        errors.append({"code": code, "detail": detail})

    found_shell_ids = set(ATTR_RE.findall(text))
    found_layout_ids = set(LAYOUT_RE.findall(text))

    if not required_profile_ids:
        hit("device_shell_requirements_missing", "no required profile ids supplied")
        return errors

    missing = required_profile_ids - found_shell_ids
    if missing:
        hit(
            "device_shell_profile_missing",
            f"missing data-device-shell for: {', '.join(sorted(missing))}",
        )

    for profile_id in found_shell_ids:
        profile = profiles.get(profile_id)
        if profile is None:
            hit("device_shell_profile_unknown", f"unknown profile {profile_id!r}")
            continue
        expected_layout = profile.get("layout_family_id")
        attrs = profile.get("required_attributes", {})
        if isinstance(attrs, dict):
            expected_layout = attrs.get("data-layout-family", expected_layout)
        if expected_layout and expected_layout not in found_layout_ids:
            hit(
                "device_shell_layout_mismatch",
                f"{profile_id} requires data-layout-family={expected_layout!r}",
            )
        if not PRODUCT_UI_RE.search(text):
            hit(
                "device_shell_product_ui_missing",
                f'{profile_id} page must mark product UI with data-product-ui="true"',
            )

    extra = found_shell_ids - required_profile_ids
    if extra:
        hit(
            "device_shell_profile_unexpected",
            f"unexpected data-device-shell values: {', '.join(sorted(extra))}",
        )

    return errors


def lint_paths(
    paths: list[Path],
    *,
    required_profile_ids: set[str],
    registry_path: Path | None = None,
) -> dict[str, Any]:
    registry = load_registry(registry_path)
    profiles = profile_by_id(registry)
    all_errors: list[dict[str, str]] = []

    for path in paths:
        if not path.is_file():
            all_errors.append({"code": "device_shell_lint_failed", "detail": f"not a file: {path}"})
            continue
        text = path.read_text(encoding="utf-8")
        for err in lint_html(text, required_profile_ids=required_profile_ids, profiles=profiles):
            all_errors.append({**err, "detail": f"{path.name}: {err['detail']}"})

    ok = not all_errors
    return {
        "ok": ok,
        "code": "ok" if ok else all_errors[0]["code"],
        "required_profile_ids": sorted(required_profile_ids),
        "errors": all_errors,
    }


def default_profile_for_layout_family(
    layout_family_id: str,
    registry: dict[str, Any],
    profiles: dict[str, dict[str, Any]],
) -> str | None:
    defaults = registry.get("defaults_by_layout_family", {})
    if isinstance(defaults, dict):
        candidate = defaults.get(layout_family_id)
        if isinstance(candidate, str) and candidate in profiles:
            return candidate
    for profile_id, profile in profiles.items():
        if (
            profile.get("layout_family_id") == layout_family_id
            and profile.get("is_default_for_layout_family") is True
        ):
            return profile_id
    matches = [
        profile_id
        for profile_id, profile in profiles.items()
        if profile.get("layout_family_id") == layout_family_id
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def resolve_required_profiles(
    *,
    profile_ids: list[str] | None,
    layout_family_ids: list[str] | None,
    layout_bindings: dict[str, str] | None = None,
    registry_path: Path | None = None,
) -> set[str]:
    registry = load_registry(registry_path)
    profiles = profile_by_id(registry)
    if profile_ids:
        return set(profile_ids)
    if layout_family_ids:
        result: set[str] = set()
        for layout_id in layout_family_ids:
            bound = (layout_bindings or {}).get(layout_id)
            if bound:
                if bound not in profiles:
                    raise ValueError(f"unknown device_shell_profile_id {bound!r}")
                result.add(bound)
                continue
            chosen = default_profile_for_layout_family(layout_id, registry, profiles)
            if chosen is None:
                raise ValueError(
                    f"no default device shell for layout family {layout_id!r}; "
                    "set device_shell_profile_id or pass --profiles"
                )
            result.add(chosen)
        return result
    raise ValueError("pass --profiles or --layout-families")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", nargs="+", type=Path, help="HTML file(s) to lint")
    parser.add_argument(
        "--profiles",
        help=(
            "Comma-separated required profile ids "
            "(e.g. iphone_17_pro_portrait_v1,macos_tahoe_window_v1)"
        ),
    )
    parser.add_argument(
        "--layout-families",
        help="Comma-separated layout family ids; resolves default profiles from registry",
    )
    parser.add_argument(
        "--layout-bindings",
        help=(
            "JSON map layout_family_id→profile_id, "
            'e.g. {"mobile_portrait":"android_phone_portrait_v1"}'
        ),
    )
    parser.add_argument("--registry", type=Path, default=None, help="Override registry path")
    args = parser.parse_args(argv)

    try:
        profile_ids = [part.strip() for part in (args.profiles or "").split(",") if part.strip()]
        layout_ids = [
            part.strip() for part in (args.layout_families or "").split(",") if part.strip()
        ]
        bindings: dict[str, str] | None = None
        if args.layout_bindings:
            parsed = json.loads(args.layout_bindings)
            if not isinstance(parsed, dict):
                raise ValueError("--layout-bindings must be a JSON object")
            bindings = {str(key): str(value) for key, value in parsed.items()}
        required = resolve_required_profiles(
            profile_ids=profile_ids or None,
            layout_family_ids=layout_ids or None,
            layout_bindings=bindings,
            registry_path=args.registry,
        )
        result = lint_paths(args.html, required_profile_ids=required, registry_path=args.registry)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "device_shell_lint_failed",
            "errors": [{"code": "device_shell_lint_failed", "detail": str(error)}],
        }

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
