#!/usr/bin/env python3
"""Lint Milestone Work task_plan composition + PW detail carry-forward.

Composition SoT is Milestone task_plan (not Project Work). Validates refined
screens have split_probe and task rows; plan_passed requires status=passed;
portfolio_ready also requires App task_ids. With --project-work, every in-scope
PW ui_detail and key page must be dispositioned in detail_carryforward.

Accepts JSON (preferred) or YAML when PyYAML is available.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_CONCLUSIONS = frozenset({"keep_cohesive", "split", "needs_user_decision"})
VALID_PHASES = frozenset({"plan_passed", "portfolio_ready"})
VALID_PROVENANCE = frozenset({"traces_to_key_screen", "milestone_discovered"})
VALID_DETAIL_DISPOSITION = frozenset({"carried", "deferred_out_of_milestone", "out_of_scope"})


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover
            raise SystemExit("PyYAML is required to lint .yaml/.yml; pass JSON instead.") from exc
        return yaml.safe_load(text)
    return json.loads(text)


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _task_plan(doc: Any) -> dict[str, Any] | None:
    if not isinstance(doc, dict):
        raise ValueError("document must be an object")
    if "task_plan" in doc:
        plan = doc["task_plan"]
    elif "refined_screens" in doc or "tasks" in doc:
        plan = doc
    else:
        return None
    if plan is None:
        return None
    if not isinstance(plan, dict):
        raise ValueError("task_plan must be an object")
    return plan


def _pw_screen_rows(project_work: Any) -> list[dict[str, Any]]:
    if not isinstance(project_work, dict):
        return []
    cov = project_work.get("product_spec_coverage")
    if isinstance(cov, dict):
        rows = cov.get("screen_coverage")
    else:
        rows = project_work.get("screen_coverage")
    return [r for r in _list(rows) if isinstance(r, dict)]


def _detail_id(detail: dict[str, Any]) -> str | None:
    for key in ("detail_id", "id"):
        if _nonempty_str(detail.get(key)):
            return str(detail.get(key)).strip()
    return None


def _in_scope_key_screens(
    pw_rows: list[dict[str, Any]],
    *,
    key_screen_refs: set[str],
    milestone_acceptance_ids: set[str] | None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in pw_rows:
        if row.get("disposition") != "adopted":
            continue
        sid = str(row.get("screen_id") or row.get("id") or "").strip()
        if not sid:
            continue
        if sid in key_screen_refs:
            out.append(row)
            continue
        if milestone_acceptance_ids is not None:
            row_acc = {str(a).strip() for a in _list(row.get("acceptance_ids")) if _nonempty_str(a)}
            if row_acc and not row_acc.isdisjoint(milestone_acceptance_ids):
                out.append(row)
    return out


def _skeleton_rows(doc: Any, skeleton_doc: Any | None) -> list[dict[str, Any]]:
    candidates: list[Any] = []
    for source in (skeleton_doc, doc):
        if not isinstance(source, dict):
            continue
        for key in ("task_skeleton", "skeleton", "skeleton_rows"):
            if key in source:
                candidates = _list(source.get(key))
                break
        if candidates:
            break
    return [row for row in candidates if isinstance(row, dict)]


def _screen_ids_from_tasks(tasks: list[dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    for row in tasks:
        for sid in _list(row.get("screen_ids")):
            if _nonempty_str(sid):
                found.add(str(sid).strip())
    return found


def _screen_ids_from_skeleton(rows: list[dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    for row in rows:
        for sid in _list(row.get("screen_ids")):
            if _nonempty_str(sid):
                found.add(str(sid).strip())
    return found


def _lint_detail_carryforward(
    plan: dict[str, Any],
    *,
    project_work: Any,
    hit: Any,
) -> None:
    pw_rows = _pw_screen_rows(project_work)
    key_refs = {str(s).strip() for s in _list(plan.get("key_screen_refs")) if _nonempty_str(s)}
    task_acceptances: set[str] = set()
    for task in _list(plan.get("tasks")):
        if not isinstance(task, dict):
            continue
        for aid in _list(task.get("acceptance_ids")):
            if _nonempty_str(aid):
                task_acceptances.add(str(aid).strip())
    milestone_acceptance = task_acceptances or None
    in_scope = _in_scope_key_screens(
        pw_rows,
        key_screen_refs=key_refs,
        milestone_acceptance_ids=milestone_acceptance,
    )
    if not in_scope and not key_refs:
        return

    for row in in_scope:
        sid = str(row.get("screen_id") or row.get("id") or "?").strip()
        if sid not in key_refs:
            hit(
                "milestone_detail_carryforward_incomplete",
                sid,
                "in-scope Project Work key page missing from key_screen_refs",
            )

    traces = set()
    for refined in _list(plan.get("refined_screens")):
        if not isinstance(refined, dict):
            continue
        if _nonempty_str(refined.get("traces_to_key_screen")):
            traces.add(str(refined.get("traces_to_key_screen")).strip())
    carry = plan.get("detail_carryforward")
    if not isinstance(carry, dict):
        # If any in-scope screen has ui_details, require the block.
        has_details = any(_list(r.get("ui_details")) for r in in_scope)
        if has_details or in_scope:
            hit(
                "milestone_detail_carryforward_incomplete",
                "_detail_carryforward",
                "task_plan.detail_carryforward object required when Project Work is provided",
            )
        return

    if carry.get("status") == "not_applicable":
        has_details = any(
            isinstance(d, dict) and _detail_id(d)
            for r in in_scope
            for d in _list(r.get("ui_details"))
        )
        if has_details:
            hit(
                "milestone_detail_carryforward_incomplete",
                "_detail_carryforward",
                "detail_carryforward.status not_applicable but PW ui_details exist",
            )
        return

    if plan.get("status") == "passed" and carry.get("status") != "complete":
        hit(
            "milestone_detail_carryforward_incomplete",
            "_detail_carryforward",
            "detail_carryforward.status must be complete when task_plan.status=passed",
        )

    rows = [r for r in _list(carry.get("rows")) if isinstance(r, dict)]
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for crow in rows:
        ks = str(crow.get("key_screen_id") or "").strip()
        did = str(crow.get("detail_id") or "").strip()
        if ks and did:
            indexed[(ks, did)] = crow

    task_keys = {
        str(t.get("local_key")).strip()
        for t in _list(plan.get("tasks"))
        if isinstance(t, dict) and _nonempty_str(t.get("local_key"))
    }
    refined_ids = {
        str(r.get("screen_id") or r.get("id") or "").strip()
        for r in _list(plan.get("refined_screens"))
        if isinstance(r, dict) and _nonempty_str(r.get("screen_id") or r.get("id"))
    }

    for row in in_scope:
        sid = str(row.get("screen_id") or row.get("id") or "?").strip()
        details = [d for d in _list(row.get("ui_details")) if isinstance(d, dict)]
        if not details and sid not in traces:
            # Key page with no details: still must be traced by a refined screen
            # or explicitly deferred via detail_id=__key_screen__.
            marker = indexed.get((sid, "__key_screen__"))
            if marker is None:
                hit(
                    "milestone_detail_carryforward_incomplete",
                    sid,
                    "key page needs refined traces_to_key_screen or "
                    "detail_carryforward row detail_id=__key_screen__",
                )
            continue
        if not details:
            continue
        for detail in details:
            did = _detail_id(detail)
            if did is None:
                hit(
                    "milestone_detail_carryforward_incomplete",
                    sid,
                    "Project Work ui_details entry missing detail_id",
                )
                continue
            crow = indexed.get((sid, did))
            if crow is None:
                hit(
                    "milestone_detail_carryforward_incomplete",
                    f"{sid}/{did}",
                    "PW ui_detail not dispositioned in detail_carryforward.rows",
                )
                continue
            disposition = crow.get("disposition")
            if disposition not in VALID_DETAIL_DISPOSITION:
                hit(
                    "milestone_detail_carryforward_incomplete",
                    f"{sid}/{did}",
                    "disposition must be carried | deferred_out_of_milestone | out_of_scope",
                )
                continue
            if disposition == "carried":
                rs = str(crow.get("carried_to_refined_screen") or "").strip()
                tk = str(crow.get("carried_to_task_local_key") or "").strip()
                if rs not in refined_ids:
                    hit(
                        "milestone_detail_carryforward_incomplete",
                        f"{sid}/{did}",
                        "carried_to_refined_screen must reference a refined_screens id",
                    )
                if tk not in task_keys:
                    hit(
                        "milestone_detail_carryforward_incomplete",
                        f"{sid}/{did}",
                        "carried_to_task_local_key must reference a tasks[].local_key",
                    )
            elif not _nonempty_str(crow.get("rationale")):
                hit(
                    "milestone_detail_carryforward_incomplete",
                    f"{sid}/{did}",
                    f"{disposition} requires rationale",
                )


def lint_screen_task_portfolio(
    doc: Any,
    *,
    skeleton_doc: Any | None = None,
    project_work: Any | None = None,
    phase: str = "plan_passed",
) -> dict[str, Any]:
    if phase not in VALID_PHASES:
        raise ValueError(f"phase must be one of {sorted(VALID_PHASES)}")

    hits: list[dict[str, str]] = []

    def hit(code: str, screen_id: str, detail: str) -> None:
        hits.append({"code": code, "screenId": screen_id, "detail": detail, "failCode": code})

    plan = _task_plan(doc)
    if plan is None:
        hit(
            "milestone_task_plan_incomplete",
            "_task_plan",
            "document must contain task_plan (or bare plan with refined_screens/tasks)",
        )
        return {
            "ok": False,
            "failCode": hits[0]["failCode"],
            "hits": hits,
            "hitCount": len(hits),
            "refinedScreenCount": 0,
            "phase": phase,
        }

    status = plan.get("status")
    if status == "not_applicable":
        return {
            "ok": True,
            "failCode": None,
            "hits": [],
            "hitCount": 0,
            "refinedScreenCount": 0,
            "phase": phase,
            "note": "task_plan_not_applicable",
        }

    if phase in VALID_PHASES and status != "passed":
        hit(
            "milestone_task_plan_incomplete",
            "_task_plan",
            f"task_plan.status must be passed for phase={phase} (got {status!r})",
        )

    refined = [r for r in _list(plan.get("refined_screens")) if isinstance(r, dict)]
    tasks = [t for t in _list(plan.get("tasks")) if isinstance(t, dict)]
    task_screen_ids = _screen_ids_from_tasks(tasks)
    skeleton_rows = _skeleton_rows(doc, skeleton_doc)
    skeleton_screen_ids = _screen_ids_from_skeleton(skeleton_rows)

    for row in refined:
        sid = str(row.get("screen_id") or row.get("id") or "?").strip()
        provenance = row.get("provenance")
        traces = row.get("traces_to_key_screen")
        if provenance not in VALID_PROVENANCE:
            if not _nonempty_str(traces):
                hit(
                    "milestone_task_plan_incomplete",
                    sid,
                    "refined screen needs traces_to_key_screen or provenance=milestone_discovered",
                )
        elif provenance == "traces_to_key_screen" and not _nonempty_str(traces):
            hit(
                "milestone_task_plan_incomplete",
                sid,
                "provenance=traces_to_key_screen requires traces_to_key_screen",
            )

        probe = row.get("split_probe")
        if not isinstance(probe, dict) or probe.get("pass_completed") is not True:
            hit(
                "screen_split_probe_incomplete",
                sid,
                "split_probe.pass_completed must be true",
            )
        else:
            conclusion = probe.get("conclusion")
            if conclusion not in VALID_CONCLUSIONS:
                hit(
                    "screen_split_probe_incomplete",
                    sid,
                    "split_probe.conclusion must be keep_cohesive | split | needs_user_decision",
                )
            elif conclusion == "keep_cohesive":
                if not _nonempty_str(probe.get("rejected_split_summary")):
                    hit(
                        "screen_split_probe_incomplete",
                        sid,
                        "keep_cohesive requires rejected_split_summary",
                    )
            elif conclusion == "split":
                resulting = [
                    str(s).strip()
                    for s in _list(probe.get("resulting_screen_ids"))
                    if _nonempty_str(s)
                ]
                if len(resulting) < 2 and not _nonempty_str(probe.get("accepted_split_summary")):
                    hit(
                        "screen_split_probe_incomplete",
                        sid,
                        "split requires resulting_screen_ids (>=2) or accepted_split_summary",
                    )

        if sid not in task_screen_ids:
            hit(
                "task_portfolio_screen_coverage_incomplete",
                sid,
                "refined screen_id missing from task_plan.tasks[].screen_ids",
            )
        if skeleton_rows and sid not in skeleton_screen_ids:
            hit(
                "task_portfolio_screen_coverage_incomplete",
                sid,
                "refined screen_id missing from skeleton screen_ids",
            )

    for task in tasks:
        local_key = str(task.get("local_key") or task.get("id") or "?").strip()
        if not _nonempty_str(task.get("responsibility")):
            hit(
                "milestone_task_plan_incomplete",
                local_key,
                "task_plan.tasks[].responsibility must be non-empty",
            )
        if phase == "portfolio_ready" and not _nonempty_str(task.get("task_id")):
            hit(
                "task_portfolio_screen_coverage_incomplete",
                local_key,
                "task_plan.tasks[].task_id must be set for portfolio_ready",
            )

    if project_work is not None:
        _lint_detail_carryforward(plan, project_work=project_work, hit=hit)

    primary_fail = hits[0]["failCode"] if hits else None
    return {
        "ok": len(hits) == 0,
        "failCode": primary_fail,
        "hits": hits,
        "hitCount": len(hits),
        "refinedScreenCount": len(refined),
        "phase": phase,
        "projectWorkChecked": project_work is not None,
    }


def lint_path(
    path: Path,
    *,
    skeleton_path: Path | None = None,
    project_work_path: Path | None = None,
    phase: str = "plan_passed",
) -> dict[str, Any]:
    doc = _load(path)
    skeleton_doc = _load(skeleton_path) if skeleton_path is not None else None
    project_work = _load(project_work_path) if project_work_path is not None else None
    result = lint_screen_task_portfolio(
        doc,
        skeleton_doc=skeleton_doc,
        project_work=project_work,
        phase=phase,
    )
    result["path"] = str(path)
    if skeleton_path is not None:
        result["skeletonPath"] = str(skeleton_path)
    if project_work_path is not None:
        result["projectWorkPath"] = str(project_work_path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint Milestone task_plan screen → task coverage and split probes"
    )
    parser.add_argument("path", type=Path, help="Milestone Work JSON/YAML with task_plan")
    parser.add_argument(
        "--skeleton",
        type=Path,
        default=None,
        help="Skeleton JSON/YAML (task_skeleton / skeleton list)",
    )
    parser.add_argument(
        "--project-work",
        type=Path,
        default=None,
        help="Project Work JSON/YAML for key-page / ui_details carry-forward checks",
    )
    parser.add_argument(
        "--phase",
        choices=sorted(VALID_PHASES),
        default="plan_passed",
        help="plan_passed: status=passed + probes + task rows; "
        "portfolio_ready: also require task_ids",
    )
    args = parser.parse_args(argv)
    result = lint_path(
        args.path,
        skeleton_path=args.skeleton,
        project_work_path=args.project_work,
        phase=args.phase,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
