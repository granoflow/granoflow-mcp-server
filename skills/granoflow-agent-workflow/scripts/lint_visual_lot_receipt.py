#!/usr/bin/env python3
"""Validate finalized visual-lot receipts and material option distinction."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_visual_lot_receipt(data: dict[str, Any]) -> dict[str, Any]:
    receipt = data.get("visual_lot_receipt", data)
    errors: list[dict[str, str]] = []
    if not isinstance(receipt, dict):
        return {
            "ok": False,
            "code": "visual_lot_receipt_required",
            "errors": [{"code": "visual_lot_receipt_required", "detail": "receipt missing"}],
        }
    if receipt.get("schema") != "granoflow_visual_lot_receipt_v1":
        errors.append({"code": "visual_lot_receipt_required", "detail": "receipt schema invalid"})
    request_type = receipt.get("request_type")
    ids = receipt.get("ids")
    prior_ids = receipt.get("prior_ids")
    artifacts = receipt.get("artifact_sha256s")
    if request_type not in {"initial", "refresh", "revise"}:
        errors.append({"code": "visual_lot_receipt_required", "detail": "request_type invalid"})
    if not isinstance(ids, list) or not ids or len(set(ids)) != len(ids):
        errors.append({"code": "visual_lot_receipt_required", "detail": "ids must be unique"})
        ids = []
    if not isinstance(prior_ids, list):
        prior_ids = []
    if request_type == "refresh":
        if receipt.get("dedupe") != "ledger" or receipt.get("recorded") is not True:
            errors.append(
                {
                    "code": "visual_lot_receipt_required",
                    "detail": "refresh requires ledger dedupe and record",
                }
            )
        if set(ids) & set(prior_ids):
            errors.append(
                {
                    "code": "visual_lot_refresh_overlap",
                    "detail": "refresh ids overlap historical ids",
                }
            )
    if request_type == "initial" and receipt.get("recorded") is not True:
        errors.append(
            {
                "code": "visual_lot_receipt_required",
                "detail": "initial draw must be recorded",
            }
        )
    if request_type == "revise" and (ids != prior_ids or receipt.get("redrawn") is not False):
        errors.append(
            {
                "code": "visual_lot_refresh_overlap",
                "detail": "revise must preserve prior ids without redraw",
            }
        )
    if (
        not isinstance(artifacts, list)
        or len(artifacts) != len(ids)
        or any(not isinstance(item, str) or not HASH_RE.fullmatch(item) for item in artifacts)
    ):
        errors.append(
            {
                "code": "visual_lot_artifacts_not_distinct",
                "detail": "one artifact SHA is required per lot",
            }
        )
    elif len(set(artifacts)) != len(artifacts):
        errors.append(
            {
                "code": "visual_lot_artifacts_not_distinct",
                "detail": "artifact SHA values must be distinct",
            }
        )
    if receipt.get("materially_distinct_status") != "passed":
        errors.append(
            {
                "code": "visual_lot_artifacts_not_distinct",
                "detail": "AI material distinction review must pass",
            }
        )
    for field in ("prior_ledger_sha256", "ledger_after_sha256"):
        if not isinstance(receipt.get(field), str) or not HASH_RE.fullmatch(receipt[field]):
            errors.append(
                {
                    "code": "visual_lot_receipt_required",
                    "detail": f"{field} invalid",
                }
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
        result = validate_visual_lot_receipt(value)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "visual_lot_receipt_required",
            "errors": [{"code": "visual_lot_receipt_required", "detail": str(error)}],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
