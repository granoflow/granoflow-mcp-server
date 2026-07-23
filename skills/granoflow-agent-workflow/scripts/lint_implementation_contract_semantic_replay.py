#!/usr/bin/env python3
"""Validate runtime semantic coverage from accepted UI contracts to an implementation."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any

from lint_requirement_contract_traceability import contract_element_refs

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
REPLAY_SCHEMA = "granoflow_implementation_contract_semantic_replay_v1"
SNAPSHOT_SCHEMA = "granoflow_implementation_snapshot_v1"
BINDING_KINDS = frozenset({"dom", "accessibility", "test_id", "native_semantics"})
NON_UI_TYPES = frozenset({"backend", "documentation", "non_ui_software"})


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


def _extract(data: dict[str, Any] | None, key: str) -> dict[str, Any] | None:
    if data is None:
        return None
    value = data.get(key, data)
    return value if isinstance(value, dict) else None


def _canonical_sha256(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def canonical_implementation_snapshot_sha256(snapshot: dict[str, Any]) -> str:
    payload = {key: value for key, value in snapshot.items() if key != "snapshot_sha256"}
    return _canonical_sha256(payload)


def canonical_implementation_replay_sha256(replay: dict[str, Any]) -> str:
    excluded = {"replay_sha256", "status", "ai_semantic_review", "final_verifier"}
    return _canonical_sha256({key: value for key, value in replay.items() if key not in excluded})


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _hash(value: Any) -> bool:
    return isinstance(value, str) and bool(HASH_RE.fullmatch(value))


def _error(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _valid_relative_path(value: Any) -> bool:
    if not _nonempty(value) or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and str(path) == value


def _validate_snapshot(
    snapshot: dict[str, Any] | None,
    expected_sha256: Any,
) -> list[dict[str, str]]:
    code = "implementation_contract_source_digest_mismatch"
    if snapshot is None or snapshot.get("schema") != SNAPSHOT_SCHEMA:
        return [_error(code, "implementation snapshot schema missing")]
    errors: list[dict[str, str]] = []
    files = snapshot.get("files")
    if not isinstance(files, list) or not files:
        errors.append(_error(code, "snapshot files required"))
        files = []
    paths: list[str] = []
    for index, row in enumerate(files):
        if (
            not isinstance(row, dict)
            or not _valid_relative_path(row.get("path"))
            or not _hash(row.get("sha256"))
        ):
            errors.append(_error(code, f"snapshot files[{index}] path/hash invalid"))
        else:
            paths.append(row["path"])
    if paths != sorted(set(paths)):
        errors.append(_error(code, "snapshot paths must be unique and sorted"))
    if not _nonempty(snapshot.get("build_ref")) or not _hash(snapshot.get("build_sha256")):
        errors.append(_error(code, "snapshot build reference/hash required"))
    actual = canonical_implementation_snapshot_sha256(snapshot)
    if snapshot.get("snapshot_sha256") != actual or expected_sha256 != actual:
        errors.append(_error(code, "snapshot digest differs from current snapshot"))
    return errors


def _validate_sources(
    replay: dict[str, Any],
    sources: tuple[tuple[str, dict[str, Any] | None, str], ...],
    snapshot: dict[str, Any] | None,
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for field, source, source_field in sources:
        if (
            not _hash(replay.get(field))
            or source is None
            or replay.get(field) != source.get(source_field)
        ):
            errors.append(
                _error(
                    "implementation_contract_source_digest_mismatch",
                    f"{field} differs from current source",
                )
            )
    errors.extend(_validate_snapshot(snapshot, replay.get("implementation_snapshot_sha256")))
    return errors


def _validate_preconditions(replay: dict[str, Any]) -> list[dict[str, str]]:
    preconditions = replay.get("preconditions")
    if not isinstance(preconditions, dict):
        return [_error("implementation_contract_runtime_failed", "preconditions required")]
    expected = {
        "app_readback_status": "verified",
        "execution_authorization_status": "valid",
        "run_status": "valid",
        "implementation_design_fidelity_status": "complete",
        "runnable_build_status": "passed",
    }
    errors: list[dict[str, str]] = []
    for field, value in expected.items():
        if preconditions.get(field) != value:
            code = (
                "implementation_contract_authorization_invalid"
                if field in {"execution_authorization_status", "run_status"}
                else "implementation_contract_runtime_failed"
            )
            errors.append(_error(code, f"preconditions.{field} must be {value}"))
    return errors


def _platform_requirements(
    matrix: dict[str, Any] | None,
) -> tuple[
    dict[str, dict[str, set[str]]],
    set[tuple[str, str]],
    set[tuple[str, str]],
]:
    supported: dict[str, dict[str, set[str]]] = {}
    layout_pairs: set[tuple[str, str]] = set()
    version_pairs: set[tuple[str, str]] = set()
    if matrix is None:
        return supported, layout_pairs, version_pairs
    for row in matrix.get("platforms", []):
        if not isinstance(row, dict) or row.get("support_status") != "supported":
            continue
        platform_id = row.get("id")
        if not isinstance(platform_id, str):
            continue
        values = {
            "layouts": {
                value for value in row.get("layout_family_ids", []) if isinstance(value, str)
            },
            "versions": {
                value for value in row.get("required_test_versions", []) if isinstance(value, str)
            },
            "devices": {value for value in row.get("device_classes", []) if isinstance(value, str)},
        }
        supported[platform_id] = values
        layout_pairs.update((platform_id, value) for value in values["layouts"])
        version_pairs.update((platform_id, value) for value in values["versions"])
    return supported, layout_pairs, version_pairs


def _validate_targets(
    replay: dict[str, Any],
    matrix: dict[str, Any] | None,
) -> tuple[set[str], list[dict[str, str]]]:
    supported, required_layouts, required_versions = _platform_requirements(matrix)
    targets = replay.get("runtime_targets")
    errors: list[dict[str, str]] = []
    if not isinstance(targets, list) or not targets:
        return set(), [
            _error(
                "implementation_contract_target_coverage_missing",
                "runtime_targets required",
            )
        ]
    target_ids: set[str] = set()
    observed_layouts: set[tuple[str, str]] = set()
    observed_versions: set[tuple[str, str]] = set()
    for index, target in enumerate(targets):
        if not isinstance(target, dict) or not _nonempty(target.get("id")):
            errors.append(
                _error(
                    "implementation_contract_target_coverage_missing",
                    f"runtime_targets[{index}] id required",
                )
            )
            continue
        target_id = target["id"]
        platform_id = target.get("platform_id")
        layout_id = target.get("layout_family_id")
        version = target.get("test_version")
        device = target.get("device_class")
        if target_id in target_ids:
            errors.append(
                _error(
                    "implementation_contract_target_coverage_missing",
                    f"duplicate runtime target {target_id}",
                )
            )
        target_ids.add(target_id)
        allowed = supported.get(platform_id, {}) if isinstance(platform_id, str) else {}
        valid = (
            layout_id in allowed.get("layouts", set())
            and version in allowed.get("versions", set())
            and device in allowed.get("devices", set())
            and _nonempty(target.get("runtime_artifact_ref"))
            and _hash(target.get("runtime_artifact_sha256"))
        )
        if not valid:
            errors.append(
                _error(
                    "implementation_contract_target_coverage_missing",
                    f"runtime target {target_id} is outside the platform matrix",
                )
            )
        if isinstance(platform_id, str) and isinstance(layout_id, str):
            observed_layouts.add((platform_id, layout_id))
        if isinstance(platform_id, str) and isinstance(version, str):
            observed_versions.add((platform_id, version))
    if not required_layouts.issubset(observed_layouts) or not required_versions.issubset(
        observed_versions
    ):
        errors.append(
            _error(
                "implementation_contract_target_coverage_missing",
                "supported layouts or required test versions are uncovered",
            )
        )
    return target_ids, errors


def _evidence_error(
    row: dict[str, Any],
    ref_field: str,
    hash_field: str,
    code: str,
    index: int,
) -> dict[str, str] | None:
    if _nonempty(row.get(ref_field)) and _hash(row.get(hash_field)):
        return None
    return _error(code, f"rows[{index}] {ref_field}/{hash_field} required")


def _validate_verified_row(
    row: dict[str, Any],
    element_ref: str,
    target_id: str,
    index: int,
) -> tuple[list[dict[str, str]], tuple[str, str, int] | None]:
    errors: list[dict[str, str]] = []
    binding = row.get("runtime_binding")
    dom_row = None
    if (
        not isinstance(binding, dict)
        or binding.get("kind") not in BINDING_KINDS
        or not _nonempty(binding.get("ref"))
    ):
        errors.append(
            _error(
                "implementation_contract_element_missing",
                f"rows[{index}] runtime binding invalid",
            )
        )
    elif binding.get("kind") == "dom":
        dom_row = (target_id, element_ref, index)
    required = [("capture_ref", "capture_sha256", "implementation_contract_element_missing")]
    if element_ref.startswith(("action:", "navigation:")):
        required.append(
            (
                "interaction_evidence_ref",
                "interaction_evidence_sha256",
                "implementation_contract_interaction_failed",
            )
        )
    if element_ref.startswith(("state:", "permission:")):
        required.append(
            (
                "state_capture_ref",
                "state_capture_sha256",
                "implementation_contract_state_unverified",
            )
        )
    if element_ref.startswith(("field:", "data_source:")):
        required.append(
            (
                "data_evidence_ref",
                "data_evidence_sha256",
                "implementation_contract_data_binding_unverified",
            )
        )
    for ref_field, hash_field, code in required:
        error = _evidence_error(row, ref_field, hash_field, code, index)
        if error:
            errors.append(error)
    return errors, dom_row


def _validate_rows(
    replay: dict[str, Any],
    content: dict[str, Any] | None,
    target_ids: set[str],
) -> tuple[list[tuple[str, str, int]], int, list[dict[str, str]]]:
    expected_elements = contract_element_refs(content) if content is not None else set()
    expected_pairs = {
        (element_ref, target_id) for element_ref in expected_elements for target_id in target_ids
    }
    rows = replay.get("rows")
    errors: list[dict[str, str]] = []
    if not isinstance(rows, list) or not rows:
        return (
            [],
            len(expected_pairs),
            [_error("implementation_contract_element_missing", "semantic rows required")],
        )
    covered_pairs: set[tuple[str, str]] = set()
    dom_rows: list[tuple[str, str, int]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(
                _error("implementation_contract_element_missing", f"rows[{index}] invalid")
            )
            continue
        element_ref = row.get("contract_element_ref")
        target_id = row.get("runtime_target_id")
        if not isinstance(element_ref, str) or not isinstance(target_id, str):
            errors.append(
                _error(
                    "implementation_contract_element_missing",
                    f"rows[{index}] element/target required",
                )
            )
            continue
        covered_pairs.add((element_ref, target_id))
        if row.get("status") == "approved_platform_exception":
            fields = (
                "platform_exception_ref",
                "approved_exception_evidence_ref",
                "rationale",
            )
            if not all(_nonempty(row.get(field)) for field in fields):
                errors.append(
                    _error(
                        "implementation_contract_element_missing",
                        f"rows[{index}] platform exception is not approved",
                    )
                )
        elif row.get("status") == "verified":
            row_errors, dom_row = _validate_verified_row(row, element_ref, target_id, index)
            errors.extend(row_errors)
            if dom_row:
                dom_rows.append(dom_row)
        else:
            errors.append(
                _error(
                    "implementation_contract_element_missing",
                    f"rows[{index}] status invalid",
                )
            )
    if covered_pairs != expected_pairs:
        errors.append(
            _error(
                "implementation_contract_element_missing",
                "element/runtime coverage differs from the required set",
            )
        )
    return dom_rows, len(expected_pairs), errors


def _validate_html(
    dom_rows: list[tuple[str, str, int]],
    html_paths: dict[str, Path] | None,
) -> list[dict[str, str]]:
    if not html_paths:
        return []
    marker_sets: dict[str, set[str]] = {}
    for target_id, path in html_paths.items():
        parser = ContractMarkerParser()
        parser.feed(path.read_text(encoding="utf-8"))
        marker_sets[target_id] = parser.refs
    return [
        _error(
            "implementation_contract_element_missing",
            f"rows[{index}] runtime HTML lacks data-contract-ref",
        )
        for target_id, element_ref, index in dom_rows
        if target_id in marker_sets and element_ref not in marker_sets[target_id]
    ]


def _validate_final_gates(
    replay: dict[str, Any],
    target_ids: set[str],
    digest: str,
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    deterministic = replay.get("deterministic_runtime")
    if (
        not isinstance(deterministic, dict)
        or deterministic.get("status") != "passed"
        or set(deterministic.get("runtime_target_ids", [])) != target_ids
        or not _nonempty_list(deterministic.get("evidence_refs"))
    ):
        errors.append(
            _error(
                "implementation_contract_runtime_failed",
                "deterministic runtime must pass every target",
            )
        )
    if replay.get("open_blockers") != []:
        errors.append(_error("implementation_contract_open_blockers", "open blockers remain"))
    if replay.get("authorization_effect") != "none":
        errors.append(
            _error(
                "implementation_contract_authorization_invalid",
                "Replay cannot grant authority",
            )
        )
    if replay.get("replay_sha256") != digest:
        errors.append(
            _error(
                "implementation_contract_replay_digest_mismatch",
                "recorded Replay digest is stale",
            )
        )
    author_id = replay.get("implementation_author_id")
    ai_review = replay.get("ai_semantic_review")
    ai_valid = (
        _nonempty(author_id)
        and isinstance(ai_review, dict)
        and _nonempty(ai_review.get("reviewer_id"))
        and ai_review.get("reviewer_id") != author_id
        and ai_review.get("status") == "passed"
        and _nonempty_list(ai_review.get("evidence_refs"))
        and ai_review.get("reviewed_replay_sha256") == digest
    )
    if not ai_valid:
        errors.append(
            _error(
                "implementation_contract_ai_failed",
                "independent AI reviewer must pass the current digest",
            )
        )
    verifier = replay.get("final_verifier")
    verifier_valid = (
        isinstance(verifier, dict)
        and isinstance(ai_review, dict)
        and _nonempty(verifier.get("verifier_id"))
        and verifier.get("verifier_id") not in {author_id, ai_review.get("reviewer_id")}
        and verifier.get("status") == "passed"
        and _nonempty_list(verifier.get("evidence_refs"))
        and verifier.get("verified_replay_sha256") == digest
    )
    if not verifier_valid:
        errors.append(
            _error(
                "implementation_contract_verifier_failed",
                "independent verifier must pass the current digest",
            )
        )
    if replay.get("status") != "passed":
        errors.append(_error("implementation_contract_replay_required", "status must be passed"))
    return errors


def validate_implementation_contract_semantic_replay(
    replay_data: dict[str, Any],
    platform_data: dict[str, Any] | None = None,
    content_data: dict[str, Any] | None = None,
    bundle_data: dict[str, Any] | None = None,
    semantic_data: dict[str, Any] | None = None,
    technical_data: dict[str, Any] | None = None,
    snapshot_data: dict[str, Any] | None = None,
    html_paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    replay = _extract(replay_data, "implementation_contract_semantic_replay")
    if replay is None or replay.get("schema") != REPLAY_SCHEMA:
        errors = [_error("implementation_contract_replay_required", "schema missing")]
        return {"ok": False, "code": errors[0]["code"], "errors": errors}
    digest = canonical_implementation_replay_sha256(replay)
    if replay.get("applicability") == "not_applicable":
        valid = (
            replay.get("task_type") in NON_UI_TYPES
            and _nonempty(replay.get("rationale"))
            and replay.get("authorization_effect") == "none"
            and replay.get("status") == "not_applicable"
            and replay.get("replay_sha256") == digest
        )
        errors = (
            []
            if valid
            else [
                _error(
                    "implementation_contract_replay_required",
                    "invalid not_applicable declaration",
                )
            ]
        )
        return {
            "ok": valid,
            "code": "ok" if valid else errors[0]["code"],
            "errors": errors,
            "replay_sha256": digest,
        }
    errors: list[dict[str, str]] = []
    if replay.get("applicability") != "required":
        errors.append(_error("implementation_contract_replay_required", "applicability invalid"))
    platform = _extract(platform_data, "platform_support_matrix")
    content = _extract(content_data, "screen_content_contract")
    sources = (
        ("platform_matrix_sha256", platform, "matrix_sha256"),
        ("content_contract_sha256", content, "content_contract_sha256"),
        (
            "prototype_bundle_sha256",
            _extract(bundle_data, "responsive_prototype_bundle"),
            "bundle_sha256",
        ),
        (
            "prototype_semantic_review_sha256",
            _extract(semantic_data, "contract_prototype_semantic_review"),
            "semantic_review_sha256",
        ),
        (
            "technical_package_sha256",
            _extract(technical_data, "analysis_technical_package"),
            "technical_package_sha256",
        ),
    )
    errors.extend(
        _validate_sources(
            replay,
            sources,
            _extract(snapshot_data, "implementation_snapshot"),
        )
    )
    errors.extend(_validate_preconditions(replay))
    target_ids, target_errors = _validate_targets(replay, platform)
    errors.extend(target_errors)
    dom_rows, pair_count, row_errors = _validate_rows(replay, content, target_ids)
    errors.extend(row_errors)
    errors.extend(_validate_html(dom_rows, html_paths))
    errors.extend(_validate_final_gates(replay, target_ids, digest))
    return {
        "ok": not errors,
        "code": "ok" if not errors else errors[0]["code"],
        "errors": errors,
        "replay_sha256": digest,
        "runtime_target_count": len(target_ids),
        "required_pair_count": pair_count,
    }


def _parse_html(value: str) -> tuple[str, Path]:
    target_id, separator, raw_path = value.partition("=")
    if not separator or not target_id or not raw_path:
        raise argparse.ArgumentTypeError("--html must be runtime_target_id=/path/file.html")
    return target_id, Path(raw_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path)
    parser.add_argument("--platform-matrix", type=Path, required=True)
    parser.add_argument("--content-contract", type=Path, required=True)
    parser.add_argument("--prototype-bundle", type=Path, required=True)
    parser.add_argument("--prototype-semantic-review", type=Path, required=True)
    parser.add_argument("--technical-package", type=Path, required=True)
    parser.add_argument("--implementation-snapshot", type=Path, required=True)
    parser.add_argument("--html", action="append", type=_parse_html, default=[])
    args = parser.parse_args(argv)
    try:
        result = validate_implementation_contract_semantic_replay(
            _load(args.replay),
            _load(args.platform_matrix),
            _load(args.content_contract),
            _load(args.prototype_bundle),
            _load(args.prototype_semantic_review),
            _load(args.technical_package),
            _load(args.implementation_snapshot),
            dict(args.html),
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {
            "ok": False,
            "code": "implementation_contract_replay_required",
            "errors": [_error("implementation_contract_replay_required", str(error))],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
