#!/usr/bin/env python3
"""Lint Project Work product.app_icon for the App Icon Source Gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_APPLICABILITY = frozenset({"required", "not_applicable"})
VALID_SCAN = frozenset({"found", "missing", "not_scanned"})
VALID_SOURCE = frozenset(
    {
        "user_provided",
        "ai_generated",
        "downloaded_license_clear",
        "unresolved",
        "not_applicable",
    }
)


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _app_icon(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    if "app_icon" in data and isinstance(data.get("app_icon"), dict):
        return data["app_icon"]
    product = data.get("product")
    if isinstance(product, dict) and isinstance(product.get("app_icon"), dict):
        return product["app_icon"]
    return None


def lint_app_icon(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    icon = _app_icon(data)
    if icon is None:
        return {
            "ok": False,
            "code": "app_icon_source_lint_failed",
            "errors": [
                _err(
                    "app_icon_source_lint_failed",
                    "product.app_icon object required for lint input",
                )
            ],
        }

    applicability = icon.get("applicability")
    if applicability not in VALID_APPLICABILITY:
        errors.append(
            _err(
                "app_icon_applicability_unresolved",
                "applicability must be required|not_applicable",
            )
        )
        return {
            "ok": False,
            "code": "app_icon_source_lint_failed",
            "errors": errors,
        }

    basis = icon.get("applicability_basis")
    if not isinstance(basis, str) or not basis.strip():
        errors.append(
            _err(
                "app_icon_source_lint_failed",
                "applicability_basis required",
            )
        )

    if applicability == "not_applicable":
        source = icon.get("source_choice")
        if source not in {None, "not_applicable"} and source not in VALID_SOURCE:
            errors.append(
                _err(
                    "app_icon_source_lint_failed",
                    "source_choice invalid for not_applicable",
                )
            )
        ok = not errors
        return {
            "ok": ok,
            "code": "ok" if ok else "app_icon_source_lint_failed",
            "errors": errors,
        }

    scan = icon.get("document_scan_status")
    if scan not in VALID_SCAN:
        errors.append(
            _err(
                "app_icon_document_scan_missing",
                "document_scan_status must be found|missing|not_scanned",
            )
        )
    elif scan == "not_scanned":
        errors.append(
            _err(
                "app_icon_document_scan_missing",
                "document_scan_status must not remain not_scanned when required",
            )
        )

    source = icon.get("source_choice")
    if source not in VALID_SOURCE:
        errors.append(
            _err(
                "app_icon_source_lint_failed",
                "source_choice must be a valid enum value",
            )
        )
    elif scan == "missing" and source == "unresolved":
        errors.append(
            _err(
                "app_icon_source_unresolved",
                "required + missing docs requires a resolved source_choice",
            )
        )
    elif (
        scan == "missing"
        and source
        in {
            "user_provided",
            "ai_generated",
            "downloaded_license_clear",
        }
        and icon.get("user_decision_recorded") is not True
    ):
        errors.append(
            _err(
                "app_icon_source_unresolved",
                "user_decision_recorded must be true after a source choice",
            )
        )

    if source in {"user_provided", "ai_generated", "downloaded_license_clear"}:
        path = icon.get("asset_path")
        if path is not None and not (isinstance(path, str) and path.strip()):
            errors.append(
                _err(
                    "app_icon_source_lint_failed",
                    "asset_path must be null or a non-empty string",
                )
            )

    if source == "downloaded_license_clear":
        note = icon.get("license_note")
        if not isinstance(note, str) or not note.strip():
            errors.append(
                _err(
                    "app_icon_source_lint_failed",
                    "license_note required for downloaded_license_clear",
                )
            )

    ok = not errors
    return {
        "ok": ok,
        "code": "ok" if ok else "app_icon_source_lint_failed",
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Project Work YAML/JSON path")
    args = parser.parse_args(argv)
    result = lint_app_icon(_load(args.path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
