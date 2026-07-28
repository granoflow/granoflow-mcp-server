#!/usr/bin/env python3
"""Copy canonical device shell assets into a prototype source directory."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ASSETS_ROOT = Path(__file__).resolve().parents[1] / "assets" / "device-shells"
REGISTRY = ASSETS_ROOT / "device-shell-registry.json"


def _resolve_profiles(
    *,
    profile_ids: list[str] | None,
    layout_family_ids: list[str] | None,
    layout_bindings: dict[str, str] | None,
    registry_path: Path | None,
) -> list[str]:
    import importlib.util

    lint_script = Path(__file__).resolve().parent / "lint_device_shell.py"
    spec = importlib.util.spec_from_file_location("lint_device_shell", lint_script)
    if spec is None or spec.loader is None:
        raise ValueError("unable to load lint_device_shell")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    resolved = mod.resolve_required_profiles(
        profile_ids=profile_ids,
        layout_family_ids=layout_family_ids,
        layout_bindings=layout_bindings,
        registry_path=registry_path,
    )
    return sorted(resolved)


def load_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or REGISTRY
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "granoflow.device_shell_registry":
        raise ValueError("invalid device shell registry schema")
    return data


def profile_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in registry.get("profiles", []):
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            result[row["id"]] = row
    return result


def copy_profiles(
    dest: Path,
    profile_ids: list[str],
    *,
    registry_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    registry = load_registry(registry_path)
    profiles = profile_map(registry)
    dest = dest.resolve()
    copied: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    for profile_id in profile_ids:
        profile = profiles.get(profile_id)
        if profile is None:
            errors.append(
                {
                    "code": "device_shell_profile_unknown",
                    "detail": f"unknown profile {profile_id!r}",
                }
            )
            continue
        assets = profile.get("assets")
        if not isinstance(assets, dict):
            errors.append(
                {
                    "code": "device_shell_assets_missing",
                    "detail": f"{profile_id} has no assets block",
                }
            )
            continue
        for key in ("css", "frame_fragment"):
            rel = assets.get(key)
            if not isinstance(rel, str) or not rel.strip():
                errors.append(
                    {
                        "code": "device_shell_assets_missing",
                        "detail": f"{profile_id} missing asset {key}",
                    }
                )
                continue
            src = ASSETS_ROOT / rel
            if not src.is_file():
                errors.append(
                    {
                        "code": "device_shell_assets_missing",
                        "detail": f"asset not found: {src}",
                    }
                )
                continue
            target = dest / "device-shells" / profile_id / src.name
            copied.append(
                {
                    "profile_id": profile_id,
                    "asset": key,
                    "source": str(src),
                    "target": str(target),
                }
            )
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)

    registry_target = dest / "device-shells" / "device-shell-registry.json"
    copied.append(
        {
            "profile_id": "*",
            "asset": "registry",
            "source": str(registry_path or REGISTRY),
            "target": str(registry_target),
        }
    )
    if not dry_run:
        registry_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registry_path or REGISTRY, registry_target)

    ok = not errors
    return {
        "ok": ok,
        "dry_run": dry_run,
        "dest": str(dest),
        "copied": copied,
        "errors": errors,
        "code": "ok" if ok else errors[0]["code"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True, help="Prototype source directory")
    parser.add_argument(
        "--profiles",
        help="Comma-separated profile ids to copy",
    )
    parser.add_argument(
        "--layout-families",
        help="Comma-separated layout family ids; copies default profiles from registry",
    )
    parser.add_argument(
        "--layout-bindings",
        help="JSON map layout_family_id→profile_id for user-specified overrides",
    )
    parser.add_argument("--registry", type=Path, default=None, help="Override registry path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    profile_ids = [part.strip() for part in (args.profiles or "").split(",") if part.strip()]
    layout_ids = [part.strip() for part in (args.layout_families or "").split(",") if part.strip()]
    if bool(profile_ids) == bool(layout_ids):
        result = {
            "ok": False,
            "code": "device_shell_requirements_missing",
            "errors": [
                {
                    "code": "device_shell_requirements_missing",
                    "detail": "pass exactly one of --profiles or --layout-families",
                }
            ],
        }
    else:
        try:
            bindings: dict[str, str] | None = None
            if args.layout_bindings:
                parsed = json.loads(args.layout_bindings)
                if not isinstance(parsed, dict):
                    raise ValueError("--layout-bindings must be a JSON object")
                bindings = {str(key): str(value) for key, value in parsed.items()}
            resolved = _resolve_profiles(
                profile_ids=profile_ids or None,
                layout_family_ids=layout_ids or None,
                layout_bindings=bindings,
                registry_path=args.registry,
            )
            result = copy_profiles(
                args.dest,
                resolved,
                registry_path=args.registry,
                dry_run=args.dry_run,
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            result = {
                "ok": False,
                "code": "device_shell_assets_missing",
                "errors": [{"code": "device_shell_assets_missing", "detail": str(error)}],
            }

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
