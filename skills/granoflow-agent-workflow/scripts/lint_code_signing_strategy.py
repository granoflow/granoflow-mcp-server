#!/usr/bin/env python3
"""Lint code_signing_strategy declarations and Project Work default_signing_goal."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_code_signing_strategy_v1"
VALID_GOALS = frozenset(
    {
        "local_dev_run",
        "device_debug",
        "distribute_store",
        "distribute_direct",
    }
)
LOCAL_GOALS = frozenset({"local_dev_run", "device_debug"})
DISTRIBUTE_GOALS = frozenset({"distribute_store", "distribute_direct"})

LOCAL_SELECTED_IDS = frozenset(
    {
        "apple_adhoc_local",
        "free_apple_id_device",
        "android_debug_keystore",
        "windows_unsigned_local",
        "linux_unsigned_local",
    }
)
DISTRIBUTE_SELECTED_IDS = frozenset(
    {
        "apple_development_team",
        "apple_developer_id",
        "distribute_store",
        "distribute_notarized",
        "android_release_keystore",
        "windows_authenticode",
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


def _is_local_selected(selected_id: str) -> bool:
    return selected_id in LOCAL_SELECTED_IDS or selected_id.startswith("other_local_")


def _is_distribute_selected(selected_id: str) -> bool:
    return selected_id in DISTRIBUTE_SELECTED_IDS or selected_id.startswith("other_distribute_")


def _default_signing_goal(project_work: Any | None) -> str | None:
    if not isinstance(project_work, dict):
        return None
    engineering = project_work.get("engineering")
    if not isinstance(engineering, dict):
        return None
    quality_gates = engineering.get("quality_gates")
    if not isinstance(quality_gates, dict):
        return None
    goal = quality_gates.get("default_signing_goal")
    if goal is None:
        return None
    if not isinstance(goal, str):
        return "__invalid_type__"
    return goal


def lint_default_signing_goal(project_work: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(project_work, dict):
        return {
            "ok": False,
            "code": "code_signing_default_goal_invalid",
            "errors": [
                _err(
                    "code_signing_default_goal_invalid",
                    "project_work must be an object",
                )
            ],
            "effective_goal": None,
        }

    raw = _default_signing_goal(project_work)
    if raw is None:
        return {
            "ok": True,
            "code": "ok",
            "errors": [],
            "effective_goal": "local_dev_run",
        }
    if raw == "__invalid_type__" or raw not in VALID_GOALS:
        errors.append(
            _err(
                "code_signing_default_goal_invalid",
                "engineering.quality_gates.default_signing_goal must be one of "
                + ", ".join(sorted(VALID_GOALS)),
            )
        )
        return {
            "ok": False,
            "code": "code_signing_default_goal_invalid",
            "errors": errors,
            "effective_goal": None,
        }
    return {
        "ok": True,
        "code": "ok",
        "errors": [],
        "effective_goal": raw,
    }


def lint_code_signing_strategy(
    strategy: Any | None,
    *,
    project_work: Any | None = None,
    require_strategy: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    if project_work is not None:
        pw_result = lint_default_signing_goal(project_work)
        if not pw_result["ok"]:
            return {
                "ok": False,
                "code": pw_result["code"],
                "errors": pw_result["errors"],
            }

    if strategy is None:
        if require_strategy:
            return {
                "ok": False,
                "code": "code_signing_strategy_missing",
                "errors": [
                    _err(
                        "code_signing_strategy_missing",
                        "signing-related change requires code_signing_strategy",
                    )
                ],
            }
        return {"ok": True, "code": "ok", "errors": []}

    if not isinstance(strategy, dict):
        return {
            "ok": False,
            "code": "code_signing_strategy_incomplete",
            "errors": [
                _err(
                    "code_signing_strategy_incomplete",
                    "code_signing_strategy must be an object",
                )
            ],
        }

    for field in ("schema", "goal", "selected", "user_confirmation"):
        if field not in strategy or strategy.get(field) in (None, ""):
            errors.append(
                _err(
                    "code_signing_strategy_incomplete",
                    f"code_signing_strategy.{field} is required",
                )
            )

    if "schema" in strategy and strategy.get("schema") not in (None, "", SCHEMA):
        errors.append(
            _err(
                "code_signing_strategy_incomplete",
                f"schema must be {SCHEMA}",
            )
        )

    goal = strategy.get("goal")
    if goal is not None and goal not in VALID_GOALS:
        errors.append(
            _err(
                "code_signing_strategy_incomplete",
                "goal must be one of " + ", ".join(sorted(VALID_GOALS)),
            )
        )

    user_confirmation = strategy.get("user_confirmation")
    if user_confirmation is not None and user_confirmation != "not_required":
        errors.append(
            _err(
                "code_signing_user_confirmation_forbidden",
                "user_confirmation must be not_required (never ask the user)",
            )
        )

    selected = strategy.get("selected")
    selected_id: str | None = None
    if selected is not None:
        if not isinstance(selected, dict):
            errors.append(
                _err(
                    "code_signing_strategy_incomplete",
                    "selected must be an object with id and label",
                )
            )
        else:
            selected_id = selected.get("id")
            label = selected.get("label")
            if not isinstance(selected_id, str) or not selected_id.strip():
                errors.append(
                    _err(
                        "code_signing_strategy_incomplete",
                        "selected.id is required",
                    )
                )
                selected_id = None
            if not isinstance(label, str) or not label.strip():
                errors.append(
                    _err(
                        "code_signing_strategy_incomplete",
                        "selected.label is required",
                    )
                )
            if selected_id is not None and not (
                _is_local_selected(selected_id) or _is_distribute_selected(selected_id)
            ):
                errors.append(
                    _err(
                        "code_signing_strategy_incomplete",
                        f"selected.id {selected_id!r} is not a known local/distribute id",
                    )
                )

    alts = strategy.get("alternatives_rejected")
    if alts is not None:
        if not isinstance(alts, list):
            errors.append(
                _err(
                    "code_signing_strategy_incomplete",
                    "alternatives_rejected must be a list when present",
                )
            )
        else:
            for index, row in enumerate(alts):
                if not isinstance(row, dict):
                    errors.append(
                        _err(
                            "code_signing_strategy_incomplete",
                            f"alternatives_rejected[{index}] must be an object",
                        )
                    )
                    continue
                if not isinstance(row.get("id"), str) or not row["id"].strip():
                    errors.append(
                        _err(
                            "code_signing_strategy_incomplete",
                            f"alternatives_rejected[{index}].id is required",
                        )
                    )
                if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                    errors.append(
                        _err(
                            "code_signing_strategy_incomplete",
                            f"alternatives_rejected[{index}].reason is required",
                        )
                    )

    evidence = strategy.get("evidence")
    if evidence is not None and not isinstance(evidence, dict):
        errors.append(
            _err(
                "code_signing_strategy_incomplete",
                "evidence must be an object when present",
            )
        )

    pw_goal = _default_signing_goal(project_work)
    effective_pw_goal = "local_dev_run" if pw_goal is None else pw_goal
    distribution_declared = effective_pw_goal in DISTRIBUTE_GOALS

    if (
        isinstance(goal, str)
        and goal in LOCAL_GOALS
        and isinstance(selected_id, str)
        and _is_distribute_selected(selected_id)
        and not distribution_declared
    ):
        errors.append(
            _err(
                "code_signing_goal_distribution_mismatch",
                "local_dev_run/device_debug cannot select a distribute signing "
                "id unless Project Work default_signing_goal is distribute_*",
            )
        )

    ok = not errors
    primary = "ok"
    if not ok:
        codes = [err["code"] for err in errors]
        if "code_signing_user_confirmation_forbidden" in codes:
            primary = "code_signing_user_confirmation_forbidden"
        elif "code_signing_goal_distribution_mismatch" in codes:
            primary = "code_signing_goal_distribution_mismatch"
        else:
            primary = "code_signing_strategy_incomplete"

    return {"ok": ok, "code": primary, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        help="strategy YAML/JSON, or Project Work when --kind project_work",
    )
    parser.add_argument(
        "--kind",
        choices=("strategy", "project_work"),
        default="strategy",
    )
    parser.add_argument(
        "--project-work",
        type=Path,
        help="optional Project Work for goal/distribution checks",
    )
    parser.add_argument(
        "--require-strategy",
        action="store_true",
        help="fail when strategy document is missing/empty",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    project_work: Any | None = None
    if args.project_work is not None:
        if not args.project_work.is_file():
            result: dict[str, Any] = {
                "ok": False,
                "code": "missing_file",
                "errors": [_err("missing_file", str(args.project_work))],
            }
            _emit(result, args.json)
            return 1
        project_work = _load(args.project_work)

    if args.kind == "project_work":
        if args.path is None or not args.path.is_file():
            result = {
                "ok": False,
                "code": "missing_file",
                "errors": [_err("missing_file", str(args.path))],
            }
        else:
            result = lint_default_signing_goal(_load(args.path))
            result["path"] = str(args.path)
        _emit(result, args.json)
        return 0 if result["ok"] else 1

    strategy: Any | None = None
    if args.path is None:
        if args.require_strategy:
            result = lint_code_signing_strategy(
                None,
                project_work=project_work,
                require_strategy=True,
            )
        else:
            result = {
                "ok": False,
                "code": "missing_file",
                "errors": [_err("missing_file", "strategy path required")],
            }
        _emit(result, args.json)
        return 0 if result["ok"] else 1

    if not args.path.is_file():
        if args.require_strategy:
            result = lint_code_signing_strategy(
                None,
                project_work=project_work,
                require_strategy=True,
            )
        else:
            result = {
                "ok": False,
                "code": "missing_file",
                "errors": [_err("missing_file", str(args.path))],
            }
        _emit(result, args.json)
        return 0 if result["ok"] else 1

    strategy = _load(args.path)
    result = lint_code_signing_strategy(
        strategy,
        project_work=project_work,
        require_strategy=args.require_strategy,
    )
    result["path"] = str(args.path)
    _emit(result, args.json)
    return 0 if result["ok"] else 1


def _emit(result: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["ok"]:
        print("ok")
    else:
        print(result["code"], file=sys.stderr)
        for err in result.get("errors", []):
            print(f"{err['code']}: {err['detail']}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
