#!/usr/bin/env python3
"""Lint Milestone Work task_plan composition coverage + split probes.

Composition SoT is Milestone task_plan (not Project Work). Validates refined
screens have split_probe and task rows; plan_passed requires status=passed;
portfolio_ready also requires App task_ids on every task row.

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


def lint_screen_task_portfolio(
    doc: Any,
    *,
    skeleton_doc: Any | None = None,
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

    if not refined and status == "passed":
        # Passed with zero refined screens is OK for non-UI; treat as ok.
        pass

    for row in refined:
        sid = str(row.get("screen_id") or row.get("id") or "?").strip()
        provenance = row.get("provenance")
        traces = row.get("traces_to_key_screen")
        if provenance not in VALID_PROVENANCE:
            # Allow omitting provenance when traces_to_key_screen is set.
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

    primary_fail = hits[0]["failCode"] if hits else None
    return {
        "ok": len(hits) == 0,
        "failCode": primary_fail,
        "hits": hits,
        "hitCount": len(hits),
        "refinedScreenCount": len(refined),
        "phase": phase,
    }


def lint_path(
    path: Path,
    *,
    skeleton_path: Path | None = None,
    phase: str = "plan_passed",
) -> dict[str, Any]:
    doc = _load(path)
    skeleton_doc = _load(skeleton_path) if skeleton_path is not None else None
    result = lint_screen_task_portfolio(
        doc,
        skeleton_doc=skeleton_doc,
        phase=phase,
    )
    result["path"] = str(path)
    if skeleton_path is not None:
        result["skeletonPath"] = str(skeleton_path)
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
        phase=args.phase,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
