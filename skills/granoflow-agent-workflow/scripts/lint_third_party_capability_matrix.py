#!/usr/bin/env python3
"""Lint granoflow_third_party_capabilities_v1 declarations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_third_party_capabilities_v1"
VALID_STATUS = frozenset({"not_started", "incomplete", "complete", "not_applicable"})
VALID_PROBE_METHODS = frozenset({"host_api", "runtime_call", "entitlement_check", "manual"})
VALID_PROBE = frozenset({"unprobed", "available", "unavailable"})


def _err(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _extract_block(data: dict[str, Any]) -> dict[str, Any] | None:
    if "third_party_capabilities" in data and isinstance(data["third_party_capabilities"], dict):
        return data["third_party_capabilities"]
    engineering = data.get("engineering")
    if isinstance(engineering, dict):
        block = engineering.get("third_party_capabilities")
        if isinstance(block, dict):
            return block
    return None


def lint_third_party_capability_matrix(
    data: dict[str, Any],
    *,
    require_complete: bool = False,
    claim_full_platform: bool = False,
) -> dict[str, Any]:
    """Return {ok, errors} for a third-party capability matrix artifact."""
    errors: list[dict[str, str]] = []
    block = _extract_block(data)
    if block is None:
        errors.append(
            _err(
                "third_party_capability_matrix_unloaded",
                "third_party_capabilities block missing",
            )
        )
        return {"ok": False, "errors": errors}

    if block.get("contract_loaded") is not True:
        errors.append(
            _err(
                "third_party_capability_matrix_unloaded",
                "contract_loaded must be true",
            )
        )
    if block.get("schema") != SCHEMA:
        errors.append(
            _err(
                "third_party_capability_matrix_unloaded",
                f"schema must be {SCHEMA}",
            )
        )

    status = block.get("status")
    if status not in VALID_STATUS:
        errors.append(
            _err(
                "third_party_capability_matrix_incomplete",
                "status must be not_started|incomplete|complete|not_applicable",
            )
        )

    if status == "not_applicable":
        decl = block.get("no_user_visible_third_party_declaration")
        if not _nonempty_str(decl):
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    "not_applicable requires no_user_visible_third_party_declaration",
                )
            )
        rows = block.get("rows")
        if isinstance(rows, list) and len(rows) > 0:
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    "not_applicable must not include capability rows",
                )
            )
        return {"ok": len(errors) == 0, "errors": errors}

    rows = block.get("rows")
    if not isinstance(rows, list) or len(rows) == 0:
        errors.append(
            _err(
                "third_party_capability_matrix_incomplete",
                "rows must be a non-empty list unless status=not_applicable",
            )
        )
        return {"ok": False, "errors": errors}

    if require_complete and status != "complete":
        errors.append(
            _err(
                "third_party_capability_matrix_incomplete",
                "status must be complete when require_complete is set",
            )
        )

    for index, row in enumerate(rows):
        prefix = f"rows[{index}]"
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix} must be object",
                )
            )
            continue

        capability = row.get("capability")
        if not _nonempty_str(capability):
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix}.capability required",
                )
            )

        user_visible = row.get("user_visible")
        if not isinstance(user_visible, bool):
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix}.user_visible must be bool",
                )
            )
            user_visible = False

        fallback = row.get("fallback")
        if user_visible and not _nonempty_str(fallback):
            errors.append(
                _err(
                    "third_party_capability_fallback_missing",
                    f"{prefix}.fallback required when user_visible is true",
                )
            )

        platforms = row.get("required_platforms")
        if not isinstance(platforms, list) or not platforms:
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix}.required_platforms must be non-empty list",
                )
            )
            platforms = []
        elif any(not _nonempty_str(p) for p in platforms):
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix}.required_platforms entries must be non-empty strings",
                )
            )

        method = row.get("probe_method")
        if method not in VALID_PROBE_METHODS:
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix}.probe_method must be "
                    "host_api|runtime_call|entitlement_check|manual",
                )
            )

        in_ship_bar = row.get("in_ship_bar")
        if not isinstance(in_ship_bar, bool):
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix}.in_ship_bar must be bool",
                )
            )

        probes = row.get("probe_by_platform")
        if probes is None:
            probes = {}
        if not isinstance(probes, dict):
            errors.append(
                _err(
                    "third_party_capability_matrix_incomplete",
                    f"{prefix}.probe_by_platform must be object when present",
                )
            )
            probes = {}

        probing_started = bool(probes) or status == "complete" or require_complete
        if probing_started:
            for platform in platforms:
                if not isinstance(platform, str):
                    continue
                if platform not in probes:
                    errors.append(
                        _err(
                            "third_party_capability_platform_missing",
                            f"{prefix}.probe_by_platform missing key {platform!r}",
                        )
                    )
                    continue
                value = probes.get(platform)
                if value not in VALID_PROBE:
                    errors.append(
                        _err(
                            "third_party_capability_matrix_incomplete",
                            f"{prefix}.probe_by_platform[{platform!r}] "
                            "must be unprobed|available|unavailable",
                        )
                    )
                elif value == "unprobed":
                    if claim_full_platform or (in_ship_bar is True and require_complete):
                        errors.append(
                            _err(
                                "third_party_capability_unprobed",
                                f"{prefix} platform {platform!r} still unprobed "
                                "under ship/complete claim",
                            )
                        )
                    if claim_full_platform:
                        errors.append(
                            _err(
                                "third_party_capability_overclaim",
                                f"{prefix} cannot claim full platform support "
                                f"while {platform!r} is unprobed",
                            )
                        )
                elif value == "unavailable" and claim_full_platform:
                    errors.append(
                        _err(
                            "third_party_capability_overclaim",
                            f"{prefix} cannot claim full platform support while "
                            f"{platform!r} is unavailable",
                        )
                    )

        if in_ship_bar is False and user_visible and require_complete:
            leftover = row.get("residual_code")
            if not _nonempty_str(leftover) and not _nonempty_str(row.get("ship_bar_leftover")):
                errors.append(
                    _err(
                        "third_party_capability_ship_bar_excluded",
                        f"{prefix} excluded from ship bar without residual_code "
                        "or ship_bar_leftover",
                    )
                )

    return {"ok": len(errors) == 0, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint third-party capability matrix artifacts")
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Require status=complete and probed ship-bar platforms",
    )
    parser.add_argument(
        "--claim-full-platform",
        action="store_true",
        help="Fail if any required platform is unprobed or unavailable",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "dry_run",
                    "mutates_state": False,
                    "planned_actions": ["Lint third_party_capabilities JSON"],
                    "artifacts": [str(args.file)],
                    "warnings": [],
                },
                ensure_ascii=False,
            )
        )
        return 0

    data = json.loads(args.file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print(
            json.dumps(
                {
                    "ok": False,
                    "errors": [
                        {
                            "code": "third_party_capability_matrix_unloaded",
                            "message": "root must be object",
                        }
                    ],
                },
                ensure_ascii=False,
            )
        )
        return 1

    result = lint_third_party_capability_matrix(
        data,
        require_complete=args.require_complete,
        claim_full_platform=args.claim_full_platform,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
