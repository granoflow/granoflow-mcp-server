#!/usr/bin/env python3
"""Lint Project SoT: schema, stages, 3.1→3.2 pin, thin gates."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DOC_TYPE = "project_sot"
SCHEMA = "granoflow_project_sot_v1"
LEGACY_DOC_TYPE = "project_e2e_sot"
LEGACY_SCHEMA = "granoflow_project_e2e_sot_v1"
STAGE_IDS = (
    "project_init",
    "milestones_created",
    "milestone_analysis",
    "milestone_plan",
    "milestone_implement",
    "integration_campaign",
    "e2e_campaign",
    "project_complete",
)
VALID_STATUS = frozenset({"active", "paused", "completed", "superseded"})
VALID_MODE = frozenset({"interactive", "unattended"})
VALID_STAGE_STATUS = frozenset({"not_started", "in_progress", "done", "blocked", "waived"})
VALID_ITEM_STATUS = frozenset({"pending", "in_progress", "done", "blocked", "paused", "cancelled"})
VALID_CROSS_M = frozenset({"pending", "planned", "not_applicable"})
VALID_IT_PATH = frozenset({"full_unit_and_it", "waived_e2e_direct", "not_started"})
VALID_CHECK = frozenset({"not_applicable", "covered", "gap"})
VALID_PARALLEL_BATCH_STATUS = frozenset(
    {
        "draft",
        "pending_acceptance",
        "accepted",
        "rejected",
        "superseded",
        "parked",
    }
)
LEGACY_NAME_RE = re.compile(r"project-e2e-sot", re.IGNORECASE)


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load_sot(path: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Load whole-file YAML/JSON, or legacy Markdown frontmatter."""
    warnings: list[dict[str, str]] = []
    text = path.read_text(encoding="utf-8")
    if LEGACY_NAME_RE.search(path.name):
        warnings.append(
            _err(
                "project_sot_legacy_path",
                "migrate to temp/project-sot.yaml; legacy e2e-named path is read-only",
            )
        )

    data: Any
    if text.startswith("---"):
        warnings.append(
            _err(
                "project_sot_legacy_path",
                "Markdown frontmatter SoT is deprecated; write whole-file YAML",
            )
        )
        end = text.find("\n---", 3)
        if end < 0:
            raise ValueError("YAML frontmatter closing --- missing")
        fm_text = text[3:end].strip("\n")
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(fm_text) or {}
        except ImportError:
            data = json.loads(fm_text)
    else:
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(text) or {}
        except ImportError:
            data = json.loads(text)
        except Exception:
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError("SoT must be whole-file YAML/JSON or legacy frontmatter") from exc

    if not isinstance(data, dict):
        raise ValueError("SoT root must be a mapping/object")
    return data, warnings


def lint_project_sot(
    data: dict[str, Any],
    *,
    require_digest_match: bool = False,
    path_warnings: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = list(path_warnings or [])

    doc_type = data.get("doc_type")
    if doc_type == LEGACY_DOC_TYPE:
        warnings.append(
            _err(
                "project_sot_legacy_path",
                f"doc_type {LEGACY_DOC_TYPE} deprecated; use {DOC_TYPE}",
            )
        )
    elif doc_type != DOC_TYPE:
        errors.append(_err("project_sot_lint_failed", f"doc_type must be {DOC_TYPE}"))

    schema = data.get("schema")
    if schema is not None:
        if doc_type == LEGACY_DOC_TYPE and schema == LEGACY_SCHEMA:
            warnings.append(
                _err(
                    "project_sot_legacy_path",
                    f"schema {LEGACY_SCHEMA} deprecated; use {SCHEMA}",
                )
            )
        elif schema != SCHEMA and not (doc_type == LEGACY_DOC_TYPE and schema == LEGACY_SCHEMA):
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    f"schema must be {SCHEMA} when present",
                )
            )

    if data.get("status") not in VALID_STATUS:
        errors.append(
            _err(
                "project_sot_lint_failed",
                "status must be active|paused|completed|superseded",
            )
        )
    if data.get("interaction_mode") not in VALID_MODE:
        errors.append(
            _err(
                "project_sot_lint_failed",
                "interaction_mode must be interactive|unattended",
            )
        )
    if not _nonempty_str(data.get("project_id")):
        errors.append(_err("project_sot_lint_failed", "project_id required"))
    if not _nonempty_str(data.get("updated_at")):
        errors.append(_err("project_sot_lint_failed", "updated_at required"))

    digests = data.get("source_digests")
    if not isinstance(digests, dict) or not _nonempty_str(digests.get("project_work")):
        errors.append(
            _err(
                "project_sot_lint_failed",
                "source_digests.project_work required",
            )
        )

    if data.get("cross_milestone_integration") not in VALID_CROSS_M:
        errors.append(
            _err(
                "project_sot_lint_failed",
                "cross_milestone_integration must be pending|planned|not_applicable",
            )
        )

    stages = data.get("stages")
    if not isinstance(stages, list):
        errors.append(_err("project_sot_lint_failed", "stages must be a list"))
        stages = []
    seen: set[str] = set()
    stage_by_id: dict[str, dict[str, Any]] = {}
    for row in stages:
        if not isinstance(row, dict):
            errors.append(_err("project_sot_lint_failed", "stage row must be object"))
            continue
        sid = row.get("id")
        if sid not in STAGE_IDS:
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    f"unknown stage id: {sid!r}",
                )
            )
            continue
        if sid in seen:
            errors.append(_err("project_sot_lint_failed", f"duplicate stage id: {sid}"))
        seen.add(str(sid))
        if row.get("status") not in VALID_STAGE_STATUS:
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    f"stage {sid} status invalid",
                )
            )
        stage_by_id[str(sid)] = row
    for sid in STAGE_IDS:
        if sid not in seen:
            errors.append(_err("project_sot_lint_failed", f"missing stage id: {sid}"))

    work_items = data.get("work_items")
    if not isinstance(work_items, list):
        errors.append(_err("project_sot_lint_failed", "work_items must be a list"))
        work_items = []

    items_by_id: dict[str, dict[str, Any]] = {}
    for item in work_items:
        if not isinstance(item, dict):
            errors.append(_err("project_sot_lint_failed", "work_item must be object"))
            continue
        wid = item.get("id")
        if not _nonempty_str(wid):
            errors.append(_err("project_sot_lint_failed", "work_item.id required"))
            continue
        wid_s = str(wid)
        if wid_s in items_by_id:
            errors.append(_err("project_sot_lint_failed", f"duplicate work_item id: {wid_s}"))
        items_by_id[wid_s] = item
        st = item.get("status")
        if st not in VALID_ITEM_STATUS:
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    f"work_item {wid_s} status invalid",
                )
            )
        parts = wid_s.split(".")
        if len(parts) >= 3 and parts[-1] == "implement":
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    f"per-task implement row forbidden: {wid_s}",
                )
            )

    next_step = data.get("next_step")
    if not isinstance(next_step, dict):
        next_step = {}
    next_id = next_step.get("work_item_id")
    override = next_step.get("override")

    pending_32_after_31: list[str] = []
    for wid, item in items_by_id.items():
        seq = str(item.get("seq") or "")
        if seq != "3.1" or item.get("status") != "done":
            continue
        pair = item.get("pair")
        if not _nonempty_str(pair):
            if ".3.1" in wid:
                pair = wid.split(".3.1")[0]
            else:
                continue
        sibling = None
        for cand_id, cand in items_by_id.items():
            if cand.get("seq") == "3.2" and (
                cand.get("pair") == pair or cand_id.startswith(f"{pair}.3.2")
            ):
                sibling = cand_id
                break
        if sibling is None:
            continue
        sib_status = items_by_id[sibling].get("status")
        if sib_status not in {"done", "cancelled"}:
            pending_32_after_31.append(sibling)

    if (
        data.get("status") == "active"
        and pending_32_after_31
        and override not in {"user_explicit"}
        and next_id not in pending_32_after_31
    ):
        errors.append(
            _err(
                "project_sot_next_step_unpinned",
                f"3.1 done requires next_step in {pending_32_after_31}, " f"got {next_id!r}",
            )
        )

    if data.get("status") == "active" and work_items:
        unfinished = [
            i
            for i in work_items
            if isinstance(i, dict) and i.get("status") not in {"done", "cancelled"}
        ]
        if unfinished and not _nonempty_str(next_id):
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    "next_step.work_item_id required while active work remains",
                )
            )

    itc = data.get("integration_campaign")
    if not isinstance(itc, dict):
        errors.append(_err("project_sot_lint_failed", "integration_campaign object required"))
        itc = {}
    else:
        if itc.get("path") not in VALID_IT_PATH:
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    "integration_campaign.path invalid",
                )
            )
        if itc.get("cross_milestone_journey_check") not in VALID_CHECK:
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    "integration_campaign.cross_milestone_journey_check invalid",
                )
            )
        if (
            stage_by_id.get("integration_campaign", {}).get("status") == "done"
            and itc.get("cross_milestone_journey_check") == "gap"
        ):
            errors.append(
                _err(
                    "cross_milestone_journey_gap",
                    "integration_campaign stage done while check is gap",
                )
            )

    e2e = data.get("e2e_campaign")
    if not isinstance(e2e, dict):
        errors.append(_err("project_sot_lint_failed", "e2e_campaign object required"))
        e2e = {}
    else:
        if e2e.get("coverage_matrix_check") not in VALID_CHECK:
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    "e2e_campaign.coverage_matrix_check invalid",
                )
            )
        if (
            stage_by_id.get("e2e_campaign", {}).get("status") == "done"
            and e2e.get("coverage_matrix_check") == "gap"
        ):
            errors.append(
                _err(
                    "e2e_coverage_matrix_gap",
                    "e2e_campaign stage done while coverage_matrix_check is gap",
                )
            )

    parallel_batches = data.get("parallel_batches")
    if parallel_batches is not None:
        if not isinstance(parallel_batches, list):
            errors.append(
                _err(
                    "project_sot_lint_failed",
                    "parallel_batches must be a list when present",
                )
            )
        else:
            for i, row in enumerate(parallel_batches):
                if not isinstance(row, dict):
                    errors.append(
                        _err(
                            "project_sot_lint_failed",
                            f"parallel_batches[{i}] must be an object",
                        )
                    )
                    continue
                if not _nonempty_str(row.get("batch_id")):
                    errors.append(
                        _err(
                            "project_sot_lint_failed",
                            f"parallel_batches[{i}].batch_id required",
                        )
                    )
                if not _nonempty_str(row.get("review_ref")):
                    errors.append(
                        _err(
                            "project_sot_lint_failed",
                            f"parallel_batches[{i}].review_ref required",
                        )
                    )
                if row.get("status") not in VALID_PARALLEL_BATCH_STATUS:
                    errors.append(
                        _err(
                            "project_sot_lint_failed",
                            f"parallel_batches[{i}].status invalid",
                        )
                    )

    if require_digest_match:
        digests_obj = data.get("source_digests")
        verification = data.get("source_digest_verification")
        if not isinstance(digests_obj, dict):
            errors.append(
                _err(
                    "project_sot_stale",
                    "source_digests required for --require-digest-match",
                )
            )
            digests_obj = {}
        if not isinstance(verification, dict):
            errors.append(
                _err(
                    "project_sot_stale",
                    "source_digest_verification required for --require-digest-match",
                )
            )
            verification = {}
        for key, recorded in digests_obj.items():
            if not _nonempty_str(recorded):
                continue
            row = verification.get(key)
            if not isinstance(row, dict):
                errors.append(
                    _err(
                        "project_sot_stale",
                        f"source_digest_verification.{key} missing",
                    )
                )
                continue
            row_recorded = row.get("recorded")
            app_readback = row.get("app_readback")
            matched = row.get("matched")
            if not _nonempty_str(row_recorded) or not _nonempty_str(app_readback):
                errors.append(
                    _err(
                        "project_sot_stale",
                        f"source_digest_verification.{key} needs recorded+app_readback",
                    )
                )
            if str(row_recorded).strip() != str(recorded).strip():
                errors.append(
                    _err(
                        "project_sot_stale",
                        f"source_digest_verification.{key}.recorded " f"!= source_digests.{key}",
                    )
                )
            if matched is not True:
                errors.append(
                    _err(
                        "project_sot_stale",
                        f"source_digest_verification.{key}.matched must be true",
                    )
                )
            elif (
                _nonempty_str(row_recorded)
                and _nonempty_str(app_readback)
                and str(row_recorded).strip() != str(app_readback).strip()
            ):
                errors.append(
                    _err(
                        "project_sot_stale",
                        f"source_digest_verification.{key} recorded!=app_readback "
                        "but matched=true",
                    )
                )

    if errors:
        primary = errors[0]["code"]
        return {
            "ok": False,
            "code": primary,
            "errors": errors,
            "warnings": warnings,
        }
    return {"ok": True, "code": "ok", "errors": [], "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to project-sot.yaml (or legacy SoT)")
    parser.add_argument(
        "--require-digest-match",
        action="store_true",
        help="Require source_digest_verification matched against App readback",
    )
    args = parser.parse_args(argv)
    try:
        data, path_warnings = _load_sot(args.path)
    except (OSError, ValueError) as exc:
        result = {
            "ok": False,
            "code": "project_sot_lint_failed",
            "errors": [_err("project_sot_lint_failed", str(exc))],
            "warnings": [],
        }
        print(json.dumps(result, ensure_ascii=False))
        return 1
    result = lint_project_sot(
        data,
        require_digest_match=args.require_digest_match,
        path_warnings=path_warnings,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
