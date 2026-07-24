#!/usr/bin/env python3
"""Render / validate a project lifecycle progress board YAML/JSON snapshot.

Exit 0 and print JSON ``{"ok": true, "markdown": "...", "next_action": {...}}``
when the board is complete. Exit 1 with ``ok: false`` and ``failCode`` otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

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

STAGE_LABELS = {
    "project_init": "1. 项目初始化 (Project Definition)",
    "milestones_created": "2. 里程碑与任务组合创建",
    "milestone_analysis": "3. 分里程碑 Analysis",
    "milestone_plan": "4. 分里程碑 Plan / Design Gate",
    "milestone_implement": "5. 实施（Layer A + 里程碑 Layer B IT）",
    "integration_campaign": "6. 最终交付 · 项目级 IT（单里程碑可跳过）",
    "e2e_campaign": "7. 最终交付 · 全面 E2E（界面路径 + 截图）",
    "project_complete": "8. 项目完成",
}

STATUS_OK = frozenset({"not_started", "in_progress", "done", "blocked"})
SESSION_DELIVERY_STATUSES = frozenset(
    {
        "offer_or_ask",
        "in_progress",
        "complete",
        "not_applicable",
    }
)
PRE_E2E_PATHS = frozenset({"e2e_direct", "full_unit_and_it", "not_selected"})


def _validate_session_delivery(sd: dict[str, Any]) -> str | None:
    status = sd.get("status")
    if status not in SESSION_DELIVERY_STATUSES:
        return f"session_delivery.status invalid: {status!r}"
    touched = sd.get("milestones_touched_count")
    if not isinstance(touched, int) or touched < 0:
        return "session_delivery.milestones_touched_count must be int ≥ 0"
    project_count = sd.get("project_feature_milestone_count")
    if not isinstance(project_count, int) or project_count < 1:
        return "session_delivery.project_feature_milestone_count must be int ≥ 1"
    path = sd.get("pre_e2e_path")
    if path not in PRE_E2E_PATHS:
        return f"session_delivery.pre_e2e_path invalid: {path!r}"
    prompt = sd.get("prompt_full_delivery")
    if prompt not in {True, False}:
        return "session_delivery.prompt_full_delivery must be bool"
    if path == "e2e_direct" and project_count != 1:
        return "e2e_direct requires project_feature_milestone_count == 1"
    if path == "full_unit_and_it" and project_count < 2:
        return "full_unit_and_it requires project_feature_milestone_count ≥ 2"
    if status == "offer_or_ask" and not str(sd.get("recommendation") or "").strip():
        return "offer_or_ask requires recommendation"
    return None


def _session_override_allows_next_action(
    sd: dict[str, Any] | None,
    earliest_incomplete: str | None,
    na_stage: str,
) -> bool:
    """Single feature-milestone project: skip stage 6, jump to full-project E2E."""
    if not isinstance(sd, dict):
        return False
    if sd.get("pre_e2e_path") != "e2e_direct":
        return False
    if sd.get("project_feature_milestone_count") != 1:
        return False
    if earliest_incomplete != "integration_campaign":
        return False
    return na_stage == "e2e_campaign"


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise SystemExit("PyYAML required for YAML input")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("root must be object")
    board = data.get("project_lifecycle_board", data)
    if not isinstance(board, dict):
        raise ValueError("project_lifecycle_board must be object")
    return board


def _fail(code: str, detail: str) -> dict[str, Any]:
    return {"ok": False, "failCode": code, "detail": detail, "markdown": None}


def validate_and_render(board: dict[str, Any]) -> dict[str, Any]:
    if board.get("contract_loaded") is not True:
        return _fail(
            "project_lifecycle_board_unread",
            "contract_loaded must be true (load reference via MCP first)",
        )

    mode = board.get("interaction_mode")
    if mode not in {"interactive", "unattended"}:
        return _fail(
            "project_lifecycle_board_render_failed",
            "interaction_mode must be interactive|unattended",
        )

    board_confirmation = board.get("board_confirmation")
    expected_confirm = "display_only" if mode == "unattended" else "required"
    if board_confirmation != expected_confirm:
        return _fail(
            "project_lifecycle_board_render_failed",
            f"board_confirmation must be {expected_confirm} for {mode}",
        )

    stages = board.get("stages")
    if not isinstance(stages, list) or not stages:
        return _fail(
            "project_lifecycle_board_incomplete_stages",
            "stages must be a non-empty list",
        )

    by_id: dict[str, dict[str, Any]] = {}
    for row in stages:
        if not isinstance(row, dict):
            return _fail(
                "project_lifecycle_board_render_failed",
                "each stage must be an object",
            )
        sid = row.get("id")
        if sid not in STAGE_IDS:
            return _fail(
                "project_lifecycle_board_incomplete_stages",
                f"unknown or missing stage id: {sid!r}",
            )
        status = row.get("status")
        if status not in STATUS_OK:
            return _fail(
                "project_lifecycle_board_render_failed",
                f"stage {sid} has invalid status {status!r}",
            )
        if not str(row.get("evidence") or "").strip():
            return _fail(
                "project_lifecycle_board_render_failed",
                f"stage {sid} missing evidence",
            )
        by_id[str(sid)] = row

    missing = [s for s in STAGE_IDS if s not in by_id]
    if missing:
        return _fail(
            "project_lifecycle_board_incomplete_stages",
            f"missing stages: {', '.join(missing)}",
        )

    # Detect illegal skip: a later stage done while an earlier is not done/blocked
    earliest_incomplete: str | None = None
    for sid in STAGE_IDS:
        st = by_id[sid]["status"]
        if st != "done":
            earliest_incomplete = sid
            break
    for i, sid in enumerate(STAGE_IDS):
        if by_id[sid]["status"] != "done":
            continue
        for earlier in STAGE_IDS[:i]:
            if by_id[earlier]["status"] not in {"done", "blocked"}:
                return _fail(
                    "project_lifecycle_stage_skip",
                    f"{sid}=done but earlier {earlier}={by_id[earlier]['status']}",
                )

    session_delivery = board.get("session_delivery")
    if session_delivery is not None:
        if not isinstance(session_delivery, dict):
            return _fail(
                "project_lifecycle_board_render_failed",
                "session_delivery must be an object when present",
            )
        sd_err = _validate_session_delivery(session_delivery)
        if sd_err:
            return _fail("full_delivery_session_fields_missing", sd_err)

    next_action = board.get("next_action")
    if not isinstance(next_action, dict):
        return _fail(
            "project_lifecycle_board_render_failed",
            "next_action object required",
        )
    na_stage = next_action.get("stage_id")
    summary = str(next_action.get("summary") or "").strip()
    if na_stage not in STAGE_IDS or not summary:
        return _fail(
            "project_lifecycle_board_render_failed",
            "next_action.stage_id and summary required",
        )
    session_override = _session_override_allows_next_action(
        session_delivery if isinstance(session_delivery, dict) else None,
        earliest_incomplete,
        str(na_stage),
    )
    if earliest_incomplete is None:
        if na_stage != "project_complete":
            return _fail(
                "project_lifecycle_board_render_failed",
                "all stages done; next_action.stage_id must be project_complete",
            )
    elif (
        na_stage != earliest_incomplete
        and by_id[earliest_incomplete]["status"] != "blocked"
        and not session_override
    ):
        return _fail(
            "project_lifecycle_board_render_failed",
            f"next_action.stage_id={na_stage} but first incomplete is {earliest_incomplete}",
        )
    if (
        isinstance(session_delivery, dict)
        and session_delivery.get("pre_e2e_path") == "e2e_direct"
        and session_delivery.get("project_feature_milestone_count") != 1
    ):
        return _fail(
            "full_delivery_pre_e2e_skip_invalid",
            "e2e_direct requires exactly one project feature milestone",
        )

    needs_confirm = next_action.get("needs_user_confirmation")
    if mode == "unattended":
        if needs_confirm is not False:
            return _fail(
                "project_lifecycle_board_confirm_in_unattended",
                "unattended next_action.needs_user_confirmation must be false",
            )
    elif needs_confirm not in {True, False}:
        return _fail(
            "project_lifecycle_board_render_failed",
            "interactive next_action.needs_user_confirmation must be bool",
        )

    entry_kind = str(board.get("entry_kind") or "").strip()
    reentry = board.get("reentry")
    if reentry is not None and not isinstance(reentry, dict):
        return _fail(
            "project_lifecycle_board_render_failed",
            "reentry must be an object when present",
        )

    title = str(board.get("project_title") or board.get("project_id") or "Project")
    lines: list[str] = [
        "## 项目进度板",
        "",
        f"- 项目：{title}",
        f"- 模式：{mode}"
        + ("（进度板仅展示，不要求确认）" if mode == "unattended" else "（阶段门禁需确认）"),
        f"- 更新：{board.get('updated_at') or '—'}",
    ]
    if entry_kind:
        lines.append(f"- 入口：`{entry_kind}`")
    pipeline_order = board.get("pipeline_order")
    if isinstance(pipeline_order, dict) and pipeline_order.get("mode"):
        po_mode = pipeline_order.get("mode")
        po_label = {
            "unset": "未选择（进 Plan 前需确认）",
            "breadth_first": "先全部分析",
            "depth_first": "做一个完整闭环再做下一个",
        }.get(str(po_mode), str(po_mode))
        lines.append(f"- 多里程碑顺序：{po_label} (`{po_mode}`)")
    lines.extend(
        [
            "",
            "### 流水线",
            "",
            "| 阶段 | 状态 | 证据 |",
            "| --- | --- | --- |",
        ]
    )
    for sid in STAGE_IDS:
        row = by_id[sid]
        lines.append(f"| {STAGE_LABELS[sid]} | `{row['status']}` | {row.get('evidence')} |")

    milestones = board.get("milestones") or []
    if isinstance(milestones, list) and milestones:
        lines.extend(["", "### 里程碑（Analysis / Plan / Implement）", ""])
        lines.append("| 里程碑 | Analysis | Plan | Implement | 备注 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for m in milestones:
            if not isinstance(m, dict):
                continue
            key = m.get("key") or m.get("milestone_id") or "?"
            name = m.get("title") or ""
            lines.append(
                f"| {key} {name} | `{m.get('analysis', '—')}` | "
                f"`{m.get('plan', '—')}` | `{m.get('implement', '—')}` | "
                f"{m.get('note') or '—'} |"
            )

    blockers = board.get("blockers") or []
    if isinstance(blockers, list) and blockers:
        lines.extend(["", "### 阻塞", ""])
        for b in blockers:
            if isinstance(b, dict):
                lines.append(
                    f"- {b.get('summary') or b.get('id')} "
                    f"(`{b.get('blocker_class') or 'other'}`)"
                )

    if isinstance(session_delivery, dict):
        lines.extend(["", "### 最终交付（本会话）", ""])
        lines.append(f"- 状态：`{session_delivery.get('status')}`")
        lines.append(
            f"- 项目功能里程碑数：{session_delivery.get('project_feature_milestone_count')}"
        )
        lines.append(f"- 预 E2E 路径：`{session_delivery.get('pre_e2e_path')}`")
        lines.append(f"- 本会话触及里程碑数：{session_delivery.get('milestones_touched_count')}")
        touched = session_delivery.get("milestones_touched") or []
        if isinstance(touched, list) and touched:
            lines.append(f"- 触及：{', '.join(str(x) for x in touched)}")
        lines.append(
            f"- 提示最终交付：{'是' if session_delivery.get('prompt_full_delivery') else '否'}"
        )
        rec = str(session_delivery.get("recommendation") or "").strip()
        if rec:
            lines.append(f"- 建议：{rec}")

    if isinstance(reentry, dict):
        lines.extend(["", "### 回轨", ""])
        from_stage = reentry.get("from_stage")
        if from_stage:
            lines.append(f"- 从阶段：`{from_stage}`")
        change_class = reentry.get("change_class")
        if change_class:
            lines.append(f"- 变更类：`{change_class}`")
        writeback_status = reentry.get("writeback_status")
        if writeback_status:
            lines.append(f"- 写回：`{writeback_status}`")
        reason = str(reentry.get("reason") or "").strip()
        if reason:
            lines.append(f"- 原因：{reason}")

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- 阶段：`{na_stage}`",
            f"- 动作：{summary}",
            f"- Owner：`{next_action.get('owner_skill') or '—'}`",
            f"- 需要用户确认：{'是' if needs_confirm else '否（展示即可）'}",
            "",
        ]
    )

    return {
        "ok": True,
        "failCode": None,
        "markdown": "\n".join(lines),
        "next_action": next_action,
        "earliest_incomplete": earliest_incomplete,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Board YAML/JSON path")
    args = parser.parse_args(argv)
    try:
        board = _load(args.path)
        result = validate_and_render(board)
    except Exception as exc:  # noqa: BLE001
        result = _fail("project_lifecycle_board_render_failed", str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
