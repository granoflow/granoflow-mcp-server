#!/usr/bin/env python3
"""Validate semantic evidence from Screen Content Contract to HTML prototypes."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from lint_requirement_contract_traceability import contract_element_refs

HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class ContractMarkerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name == "data-contract-ref" and isinstance(value, str):
                self.refs.add(value)


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        try:
            value = importlib.import_module("yaml").safe_load(text)
        except ImportError:
            value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("root must be an object")
    return value


def _extract(data: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = data.get(key, data)
    return value if isinstance(value, dict) else None


def canonical_semantic_review_sha256(review: dict[str, Any]) -> str:
    excluded = {
        "semantic_review_sha256",
        "status",
        "ai_semantic_review",
        "visual_quality_review",
        "final_verifier",
    }
    payload = {key: value for key, value in review.items() if key not in excluded}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _required_layouts(bundle: dict[str, Any] | None) -> set[str]:
    if bundle is None:
        return set()
    variants = bundle.get("variants")
    if not isinstance(variants, list):
        return set()
    return {
        row["layout_family_id"]
        for row in variants
        if isinstance(row, dict)
        if isinstance(row.get("layout_family_id"), str)
    }


def _load_html_markers(html_paths: dict[str, Path]) -> dict[str, set[str]]:
    markers: dict[str, set[str]] = {}
    for layout_id, path in html_paths.items():
        parser = ContractMarkerParser()
        parser.feed(path.read_text(encoding="utf-8"))
        markers[layout_id] = parser.refs
    return markers


def validate_contract_prototype_semantics(
    data: dict[str, Any],
    content_data: dict[str, Any] | None = None,
    traceability_data: dict[str, Any] | None = None,
    bundle_data: dict[str, Any] | None = None,
    html_paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    semantic = _extract(data, "contract_prototype_semantic_review")
    contract = (
        _extract(content_data, "screen_content_contract") if content_data is not None else None
    )
    traceability = (
        _extract(traceability_data, "requirement_contract_traceability")
        if traceability_data is not None
        else None
    )
    bundle = (
        _extract(bundle_data, "responsive_prototype_bundle") if bundle_data is not None else None
    )
    errors: list[dict[str, str]] = []
    if semantic is None:
        return {
            "ok": False,
            "code": "contract_prototype_semantic_review_required",
            "errors": [
                {
                    "code": "contract_prototype_semantic_review_required",
                    "detail": "semantic review missing",
                }
            ],
        }
    if semantic.get("schema") != "granoflow_contract_prototype_semantic_review_v1":
        errors.append(
            {
                "code": "contract_prototype_semantic_review_required",
                "detail": "semantic review schema invalid",
            }
        )
    expected_hashes = (
        ("content_contract_sha256", contract, "content_contract_sha256"),
        ("traceability_sha256", traceability, "traceability_sha256"),
        ("prototype_bundle_sha256", bundle, "bundle_sha256"),
    )
    for field, source, source_field in expected_hashes:
        if not isinstance(semantic.get(field), str) or not HASH_RE.fullmatch(semantic[field]):
            errors.append(
                {
                    "code": "contract_prototype_semantic_review_required",
                    "detail": f"{field} must be a lowercase SHA-256",
                }
            )
        if source is not None and semantic.get(field) != source.get(source_field):
            errors.append(
                {
                    "code": "contract_prototype_semantic_digest_mismatch",
                    "detail": f"{field} differs from current source",
                }
            )

    expected_elements = contract_element_refs(contract) if contract is not None else set()
    expected_layouts = _required_layouts(bundle)
    declared_layouts = semantic.get("required_layout_family_ids")
    if not isinstance(declared_layouts, list) or set(declared_layouts) != expected_layouts:
        errors.append(
            {
                "code": "contract_prototype_layout_coverage_missing",
                "detail": "required layout families differ from the Prototype Bundle",
            }
        )
    rows = semantic.get("rows")
    if not isinstance(rows, list) or not rows:
        rows = []
        errors.append(
            {
                "code": "contract_prototype_semantic_review_required",
                "detail": "semantic coverage rows required",
            }
        )
    covered_pairs: set[tuple[str, str]] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        element_ref = row.get("contract_element_ref")
        layout_id = row.get("layout_family_id")
        if not _nonempty(element_ref) or not _nonempty(layout_id):
            errors.append(
                {
                    "code": "contract_element_unrendered",
                    "detail": f"rows[{index}] element/layout required",
                }
            )
            continue
        assert isinstance(element_ref, str)
        assert isinstance(layout_id, str)
        covered_pairs.add((element_ref, layout_id))
        status = row.get("status")
        if status == "not_applicable":
            if not _nonempty(row.get("platform_exception_ref")) or not _nonempty(
                row.get("rationale")
            ):
                errors.append(
                    {
                        "code": "contract_element_unrendered",
                        "detail": f"rows[{index}] N/A needs platform exception evidence",
                    }
                )
            continue
        if status != "verified":
            errors.append(
                {
                    "code": "contract_element_unrendered",
                    "detail": f"rows[{index}] status must be verified|not_applicable",
                }
            )
            continue
        for field in ("dom_ref", "html_ref", "screenshot_ref"):
            if not _nonempty(row.get(field)):
                errors.append(
                    {
                        "code": "contract_element_unrendered",
                        "detail": f"rows[{index}].{field} required",
                    }
                )
        for field in ("html_sha256", "screenshot_sha256"):
            if not isinstance(row.get(field), str) or not HASH_RE.fullmatch(row[field]):
                errors.append(
                    {
                        "code": "contract_element_unrendered",
                        "detail": f"rows[{index}].{field} invalid",
                    }
                )
        if element_ref.startswith(("action:", "navigation:")) and not _nonempty(
            row.get("interaction_evidence_ref")
        ):
            errors.append(
                {
                    "code": "prototype_interaction_unverified",
                    "detail": f"rows[{index}] interaction evidence required",
                }
            )
        if element_ref.startswith(("state:", "permission:")) and not _nonempty(
            row.get("state_capture_ref")
        ):
            errors.append(
                {
                    "code": "contract_state_uncaptured",
                    "detail": f"rows[{index}] state capture required",
                }
            )
    expected_pairs = {
        (element_ref, layout_id)
        for element_ref in expected_elements
        for layout_id in expected_layouts
    }
    missing_pairs = sorted(expected_pairs - covered_pairs)
    if missing_pairs:
        errors.append(
            {
                "code": "contract_prototype_layout_coverage_missing",
                "detail": f"contract/layout pairs missing: {missing_pairs}",
            }
        )
    unknown_pairs = sorted(
        pair
        for pair in covered_pairs
        if pair[0] not in expected_elements or pair[1] not in expected_layouts
    )
    if unknown_pairs:
        errors.append(
            {
                "code": "contract_element_unrendered",
                "detail": f"unknown contract/layout pairs: {unknown_pairs}",
            }
        )

    markers = _load_html_markers(html_paths or {})
    for element_ref, layout_id in expected_pairs:
        if layout_id in markers and element_ref not in markers[layout_id]:
            errors.append(
                {
                    "code": "contract_element_unrendered",
                    "detail": f"{element_ref} marker missing from {layout_id} HTML",
                }
            )
    browser = semantic.get("deterministic_browser")
    if (
        not isinstance(browser, dict)
        or browser.get("status") != "passed"
        or not _nonempty_list(browser.get("evidence_refs"))
    ):
        errors.append(
            {
                "code": "prototype_interaction_unverified",
                "detail": "deterministic browser evidence must pass",
            }
        )
    blockers = semantic.get("open_blockers")
    if not isinstance(blockers, list) or blockers:
        errors.append(
            {
                "code": "contract_prototype_semantic_mismatch",
                "detail": "open semantic blockers remain",
            }
        )
    if semantic.get("authorization_effect") != "none":
        errors.append(
            {
                "code": "contract_prototype_semantic_review_required",
                "detail": "authorization_effect must be none",
            }
        )

    actual_digest = canonical_semantic_review_sha256(semantic)
    if semantic.get("semantic_review_sha256") != actual_digest:
        errors.append(
            {
                "code": "contract_prototype_semantic_digest_mismatch",
                "detail": "semantic review digest is stale",
            }
        )
    ai_review = semantic.get("ai_semantic_review")
    ai_valid = (
        isinstance(ai_review, dict)
        and _nonempty(ai_review.get("reviewer_id"))
        and ai_review.get("status") == "passed"
        and _nonempty_list(ai_review.get("evidence_refs"))
        and ai_review.get("reviewed_semantic_sha256") == actual_digest
    )
    if not ai_valid:
        errors.append(
            {
                "code": "semantic_reviewer_failed",
                "detail": "AI semantic reviewer must pass the current digest",
            }
        )
    visual = semantic.get("visual_quality_review")
    visual_valid = (
        isinstance(visual, dict)
        and visual.get("status") == "passed"
        and visual.get("mode") == "review_only"
        and visual.get("mutation_authorization") == "none"
        and _nonempty(visual.get("provider"))
        and _nonempty_list(visual.get("evidence_refs"))
    )
    if not visual_valid:
        errors.append(
            {
                "code": "visual_quality_reviewer_failed",
                "detail": "non-mutating visual quality review must pass",
            }
        )
    verifier = semantic.get("final_verifier")
    verifier_valid = (
        isinstance(verifier, dict)
        and isinstance(ai_review, dict)
        and _nonempty(verifier.get("verifier_id"))
        and verifier.get("verifier_id") != ai_review.get("reviewer_id")
        and verifier.get("status") == "passed"
        and _nonempty_list(verifier.get("evidence_refs"))
        and verifier.get("verified_semantic_sha256") == actual_digest
    )
    if not verifier_valid:
        errors.append(
            {
                "code": "semantic_verifier_failed",
                "detail": "independent semantic verifier must pass current digest",
            }
        )
    if semantic.get("status") != "passed":
        errors.append(
            {
                "code": "contract_prototype_semantic_review_required",
                "detail": "status must be passed",
            }
        )
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "semantic_review_sha256": actual_digest,
        "required_pair_count": len(expected_pairs),
    }


def _parse_html(value: str) -> tuple[str, Path]:
    layout_id, separator, raw_path = value.partition("=")
    if not separator or not layout_id or not raw_path:
        raise argparse.ArgumentTypeError("--html must be layout_family_id=/path/file.html")
    return layout_id, Path(raw_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("review", type=Path)
    parser.add_argument("--content-contract", type=Path)
    parser.add_argument("--traceability", type=Path)
    parser.add_argument("--prototype-bundle", type=Path)
    parser.add_argument("--html", action="append", type=_parse_html, default=[])
    args = parser.parse_args(argv)
    try:
        result = validate_contract_prototype_semantics(
            _load(args.review),
            _load(args.content_contract) if args.content_contract else None,
            _load(args.traceability) if args.traceability else None,
            _load(args.prototype_bundle) if args.prototype_bundle else None,
            dict(args.html),
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "contract_prototype_semantic_review_required",
            "errors": [
                {
                    "code": "contract_prototype_semantic_review_required",
                    "detail": str(error),
                }
            ],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
