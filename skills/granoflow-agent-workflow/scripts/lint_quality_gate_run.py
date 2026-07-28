#!/usr/bin/env python3
"""Lint static hygiene quality_gate_run evidence and Project Work lock."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_quality_gate_run_v1"
VALID_STAGES = frozenset({"layer_a", "layer_b", "final_delivery"})
VALID_SOURCES = frozenset({"full_gate", "composed"})
VALID_SCOPES = frozenset({"full", "task_owned"})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _as_cmd_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
            elif isinstance(item, dict):
                cmd = item.get("command") or item.get("cmd")
                if isinstance(cmd, str) and cmd.strip():
                    out.append(cmd.strip())
        return out
    return []


def _quality_gates(project_work: Any) -> dict[str, Any] | None:
    if not isinstance(project_work, dict):
        return None
    engineering = project_work.get("engineering")
    if not isinstance(engineering, dict):
        return None
    gates = engineering.get("quality_gates")
    return gates if isinstance(gates, dict) else None


def resolve_hygiene_commands(project_work: Any) -> dict[str, Any]:
    """Return {ok, commands, source, errors, layer_a_scope}."""
    errors: list[dict[str, str]] = []
    gates = _quality_gates(project_work)
    if gates is None:
        return {
            "ok": False,
            "commands": [],
            "source": None,
            "layer_a_scope": "full",
            "errors": [
                _err(
                    "quality_gates_unconfigured",
                    "engineering.quality_gates missing",
                )
            ],
        }

    full_gate = _as_cmd_list(gates.get("full_gate"))
    composed: list[str] = []
    for key in ("lint", "format_check", "type_or_static_check"):
        composed.extend(_as_cmd_list(gates.get(key)))
    # Deduplicate preserving order
    seen: set[str] = set()
    composed_uniq: list[str] = []
    for cmd in composed:
        if cmd not in seen:
            seen.add(cmd)
            composed_uniq.append(cmd)

    layer_a_scope = gates.get("layer_a_scope", "full")
    if layer_a_scope not in VALID_SCOPES:
        errors.append(
            _err(
                "static_quality_gate_scope_invalid",
                "quality_gates.layer_a_scope must be full|task_owned",
            )
        )
        layer_a_scope = "full"

    if full_gate:
        source = "full_gate"
        commands = full_gate
    elif composed_uniq:
        source = "composed"
        commands = composed_uniq
        if not _as_cmd_list(gates.get("type_or_static_check")) and not full_gate:
            # composed without any static slot is incomplete for software hygiene
            errors.append(
                _err(
                    "quality_gates_unconfigured",
                    "composed hygiene requires type_or_static_check "
                    "or a full_gate that owns static analysis",
                )
            )
    else:
        return {
            "ok": False,
            "commands": [],
            "source": None,
            "layer_a_scope": layer_a_scope,
            "errors": [
                _err(
                    "quality_gates_unconfigured",
                    "full_gate empty and lint/format/type_or_static_check empty",
                )
            ],
        }

    return {
        "ok": len(errors) == 0,
        "commands": commands,
        "source": source,
        "layer_a_scope": layer_a_scope,
        "errors": errors,
    }


def _extract_run(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    if isinstance(data.get("quality_gate_run"), dict):
        return data["quality_gate_run"]
    mia = data.get("milestone_it_acceptance")
    if isinstance(mia, dict) and isinstance(mia.get("quality_gate_run"), dict):
        return mia["quality_gate_run"]
    # Bare run object
    if data.get("schema") == SCHEMA:
        return data
    return None


def lint_quality_gate_run(
    data: Any,
    *,
    expect_stage: str | None = None,
    project_work: Any | None = None,
    require_configured: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    resolved: dict[str, Any] | None = None
    if project_work is not None or require_configured:
        resolved = resolve_hygiene_commands(project_work)
        assert resolved is not None
        if not resolved["ok"]:
            errors.extend(resolved["errors"])
            if require_configured and data is None:
                return {"ok": False, "errors": errors}
        elif require_configured and data is None:
            return {"ok": True, "errors": [], "resolved": resolved}

    run = _extract_run(data) if data is not None else None
    if run is None:
        if require_configured and data is None:
            return {"ok": len(errors) == 0, "errors": errors, "resolved": resolved}
        errors.append(
            _err(
                "static_quality_gate_skipped",
                "quality_gate_run block missing",
            )
        )
        return {"ok": False, "errors": errors}

    if run.get("contract_loaded") is not True:
        errors.append(
            _err(
                "static_quality_gate_unread",
                "contract_loaded must be true",
            )
        )
    if run.get("schema") != SCHEMA:
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                f"schema must be {SCHEMA}",
            )
        )

    stage = run.get("for_stage")
    if stage not in VALID_STAGES:
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                "for_stage must be layer_a|layer_b|final_delivery",
            )
        )
    if expect_stage is not None and stage != expect_stage:
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                f"for_stage must be {expect_stage}, got {stage!r}",
            )
        )

    source = run.get("source")
    if source not in VALID_SOURCES:
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                "source must be full_gate|composed",
            )
        )

    scope = run.get("scope")
    if scope not in VALID_SCOPES:
        errors.append(
            _err(
                "static_quality_gate_scope_invalid",
                "scope must be full|task_owned",
            )
        )
    elif stage in {"layer_b", "final_delivery"} and scope != "full":
        errors.append(
            _err(
                "static_quality_gate_scope_invalid",
                f"{stage} requires scope: full",
            )
        )
    elif stage == "layer_a" and scope == "task_owned":
        allowed = resolved is not None and resolved.get("layer_a_scope") == "task_owned"
        if not allowed:
            errors.append(
                _err(
                    "static_quality_gate_scope_invalid",
                    "layer_a task_owned requires Project Work "
                    "quality_gates.layer_a_scope: task_owned",
                )
            )

    commands = _as_cmd_list(run.get("commands"))
    if not commands:
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                "commands must be a non-empty list",
            )
        )

    if (
        resolved is not None
        and resolved.get("ok")
        and commands
        and commands != resolved["commands"]
    ):
        errors.append(
            _err(
                "static_quality_gate_commands_mismatch",
                "run commands must equal Project Work hygiene suite order",
            )
        )

    exit_code = run.get("exit_code")
    if not isinstance(exit_code, int):
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                "exit_code must be an integer",
            )
        )
    elif exit_code != 0:
        errors.append(
            _err(
                "static_quality_gate_failed",
                f"exit_code must be 0, got {exit_code}",
            )
        )

    issue_count = run.get("issue_count")
    if not isinstance(issue_count, int):
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                "issue_count must be an integer",
            )
        )
    elif issue_count != 0:
        errors.append(
            _err(
                "static_quality_gate_failed",
                f"issue_count must be 0 (warnings count as failure), got {issue_count}",
            )
        )

    residual = run.get("residual")
    if residual is not None:
        if not isinstance(residual, dict):
            errors.append(
                _err(
                    "static_quality_gate_lint_failed",
                    "residual must be an object when present",
                )
            )
        else:
            rclass = residual.get("class")
            if rclass != "blocked_external":
                errors.append(
                    _err(
                        "static_quality_gate_failed",
                        "only residual.class blocked_external is allowed; "
                        "analyzer debt is not an allowed residual",
                    )
                )
            if not _nonempty_str(residual.get("basis")):
                errors.append(
                    _err(
                        "static_quality_gate_lint_failed",
                        "residual.basis must be non-empty",
                    )
                )

    if not _nonempty_str(run.get("ran_at")):
        errors.append(
            _err(
                "static_quality_gate_lint_failed",
                "ran_at must be a non-empty string",
            )
        )

    # Deduplicate
    seen_e: set[tuple[str, str]] = set()
    uniq: list[dict[str, str]] = []
    for e in errors:
        key = (e["code"], e["detail"])
        if key in seen_e:
            continue
        seen_e.add(key)
        uniq.append(e)

    return {"ok": len(uniq) == 0, "errors": uniq}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        type=Path,
        default=None,
        help="YAML/JSON quality_gate_run or parent doc containing it",
    )
    parser.add_argument(
        "--gate",
        choices=sorted(VALID_STAGES),
        default=None,
        help="Expected for_stage",
    )
    parser.add_argument(
        "--project-work",
        type=Path,
        default=None,
        help="Project Work YAML/JSON for hygiene command lock",
    )
    parser.add_argument(
        "--require-configured",
        action="store_true",
        help="Only check Project Work hygiene suite is configured",
    )
    args = parser.parse_args(argv)

    if args.require_configured and args.run is None:
        if args.project_work is None:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "errors": [
                            _err(
                                "static_quality_gate_lint_failed",
                                "--project-work required with --require-configured",
                            )
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 2
        pw = _load(args.project_work)
        result = lint_quality_gate_run(
            None,
            project_work=pw,
            require_configured=True,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 2

    if args.run is None:
        print(
            json.dumps(
                {
                    "ok": False,
                    "errors": [
                        _err(
                            "static_quality_gate_lint_failed",
                            "--run is required unless --require-configured",
                        )
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    data = _load(args.run)
    pw = _load(args.project_work) if args.project_work else None
    result = lint_quality_gate_run(
        data,
        expect_stage=args.gate,
        project_work=pw,
        require_configured=bool(args.project_work),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
