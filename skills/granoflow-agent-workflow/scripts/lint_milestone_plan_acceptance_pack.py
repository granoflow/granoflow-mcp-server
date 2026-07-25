#!/usr/bin/env python3
"""Lint milestone Plan acceptance packs: sections, links, lanes, alignment."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

DOC_TYPE = "milestone_plan_acceptance_pack"
ALIGNMENT_SCHEMA = "granoflow_milestone_plan_prototype_alignment_v1"
SECTION_KEYS = (
    "user_copy",
    "data_structures",
    "flowcharts",
    "uml_diagrams",
    "test_cases",
)
VALID_STATUS = frozenset(
    {"draft", "pending_acceptance", "accepted", "superseded", "not_applicable"}
)
VALID_ALIGN_STATUS = frozenset({"pending", "aligned", "conflict"})
LANE_RE = re.compile(
    r"^\|\s*[^|]+\s*\|\s*(unit|integration|e2e)\s*\|",
    re.IGNORECASE | re.MULTILINE,
)
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        # JSON whole-file fallback for tests
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("pack must start with YAML frontmatter or be JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("JSON pack root must be an object")
        body = ""
        if _nonempty_str(data.get("body_markdown")):
            body = str(data["body_markdown"])
        elif _nonempty_str(data.get("_body")):
            body = str(data["_body"])
        return data, body
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("YAML frontmatter closing --- missing")
    fm_text = text[3:end].strip("\n")
    body = text[end + 4 :]
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(fm_text) or {}
    except ImportError:
        data = json.loads(fm_text)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, body


def _file_url_to_path(file_url: str) -> Path | None:
    parsed = urlparse(file_url)
    if parsed.scheme != "file":
        return None
    path = unquote(parsed.path)
    return Path(path) if path else None


def _lanes_in_body(body: str) -> set[str]:
    return {match.group(1).lower() for match in LANE_RE.finditer(body)}


def lint_milestone_plan_acceptance_pack(
    path: Path,
    *,
    require_links: bool = False,
    require_closeout: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    try:
        data, body = _load_frontmatter(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "code": "milestone_plan_acceptance_pack_incomplete",
            "errors": [
                _err(
                    "milestone_plan_acceptance_pack_incomplete",
                    str(exc),
                )
            ],
        }

    if data.get("doc_type") != DOC_TYPE and data.get("schema") != DOC_TYPE:
        # Allow nested under key
        if isinstance(data.get("milestone_plan_acceptance_pack"), dict):
            data = data["milestone_plan_acceptance_pack"]
            body = body if body else ""
        elif data.get("doc_type") != DOC_TYPE:
            errors.append(
                _err(
                    "milestone_plan_acceptance_pack_incomplete",
                    f"doc_type must be {DOC_TYPE}",
                )
            )

    status = data.get("status")
    if status not in VALID_STATUS:
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_incomplete",
                "status must be draft|pending_acceptance|accepted|superseded|" "not_applicable",
            )
        )

    if status == "not_applicable":
        return {
            "ok": not errors,
            "code": "ok" if not errors else errors[0]["code"],
            "errors": errors,
        }

    sections = data.get("sections")
    if not isinstance(sections, dict):
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_incomplete",
                "sections object required",
            )
        )
        sections = {}

    for key in SECTION_KEYS:
        block = sections.get(key)
        if not isinstance(block, dict):
            errors.append(
                _err(
                    "milestone_plan_acceptance_pack_incomplete",
                    f"sections.{key} required",
                )
            )
            continue
        present = block.get("present")
        if present is not True and present is not False:
            errors.append(
                _err(
                    "milestone_plan_acceptance_pack_incomplete",
                    f"sections.{key}.present must be true|false",
                )
            )
        if present is True:
            # Heading cues (English or Chinese)
            cues = {
                "user_copy": ("user copy", "用户文案"),
                "data_structures": ("data structure", "表结构", "数据结构"),
                "flowcharts": ("flowchart", "流程图"),
                "uml_diagrams": ("uml", "UML"),
                "test_cases": ("test case", "测试用例"),
            }
            body_l = body.lower()
            if not any(cue.lower() in body_l or cue in body for cue in cues[key]):
                errors.append(
                    _err(
                        "milestone_plan_acceptance_pack_incomplete",
                        f"sections.{key}.present=true but body heading missing",
                    )
                )

    software_ui = data.get("software_ui_milestone")
    if software_ui is None:
        # Infer: any UI-ish signals
        software_ui = bool(data.get("responsive_prototype_bundles")) or bool(
            (data.get("prototype_alignment") or {}).get("tasks")
        )

    closeout = status in {"pending_acceptance", "accepted"} or require_closeout
    if software_ui and closeout:
        tc = sections.get("test_cases") if isinstance(sections, dict) else None
        if not isinstance(tc, dict) or tc.get("present") is not True:
            errors.append(
                _err(
                    "milestone_plan_test_lanes_incomplete",
                    "software UI milestone requires sections.test_cases.present=true "
                    "before closeout/accepted",
                )
            )
        else:
            lanes = _lanes_in_body(body)
            for lane in ("unit", "integration", "e2e"):
                if lane not in lanes:
                    errors.append(
                        _err(
                            "milestone_plan_test_lanes_incomplete",
                            f"test_cases body missing Markdown lane column '{lane}'",
                        )
                    )

    html_render = data.get("html_render")
    if not isinstance(html_render, dict):
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_incomplete",
                "html_render object required",
            )
        )
        html_render = {}

    html_status = html_render.get("status")
    link_emitted = html_render.get("link_emitted")
    md_url = html_render.get("markdown_file_url")
    html_url = html_render.get("html_file_url")

    if require_links or closeout:
        if link_emitted is not True:
            errors.append(
                _err(
                    "plan_acceptance_html_link_required",
                    "html_render.link_emitted must be true when links required",
                )
            )
        if not _nonempty_str(md_url) or not str(md_url).startswith("file://"):
            errors.append(
                _err(
                    "plan_acceptance_html_link_required",
                    "html_render.markdown_file_url must be absolute file://",
                )
            )
        if html_status == "ready":
            if not _nonempty_str(html_url) or not str(html_url).startswith("file://"):
                errors.append(
                    _err(
                        "plan_acceptance_html_link_required",
                        "html_render.html_file_url required when status=ready",
                    )
                )
            else:
                html_path = _file_url_to_path(str(html_url))
                if html_path is None or not html_path.is_file():
                    errors.append(
                        _err(
                            "plan_acceptance_html_link_required",
                            f"HTML file missing for {html_url}",
                        )
                    )
                elif html_path.stat().st_size <= 0:
                    errors.append(
                        _err(
                            "plan_acceptance_html_link_required",
                            f"HTML file empty for {html_url}",
                        )
                    )

    # Alignment
    alignment = data.get("prototype_alignment")
    if software_ui:
        if not isinstance(alignment, dict):
            errors.append(
                _err(
                    "milestone_plan_prototype_alignment_failed",
                    "prototype_alignment required for software UI milestones",
                )
            )
        else:
            if alignment.get("schema") != ALIGNMENT_SCHEMA:
                errors.append(
                    _err(
                        "milestone_plan_prototype_alignment_failed",
                        f"prototype_alignment.schema must be {ALIGNMENT_SCHEMA}",
                    )
                )
            a_status = alignment.get("status")
            if a_status not in VALID_ALIGN_STATUS:
                errors.append(
                    _err(
                        "milestone_plan_prototype_alignment_failed",
                        "prototype_alignment.status must be pending|aligned|conflict",
                    )
                )
            tasks = alignment.get("tasks")
            if not isinstance(tasks, list) or not tasks:
                errors.append(
                    _err(
                        "milestone_plan_prototype_alignment_failed",
                        "prototype_alignment.tasks must be a non-empty list for UI",
                    )
                )
            else:
                for index, task in enumerate(tasks):
                    prefix = f"prototype_alignment.tasks[{index}]"
                    if not isinstance(task, dict):
                        errors.append(
                            _err(
                                "milestone_plan_prototype_alignment_failed",
                                f"{prefix} must be an object",
                            )
                        )
                        continue
                    if not _nonempty_str(task.get("task_id")):
                        errors.append(
                            _err(
                                "milestone_plan_prototype_alignment_failed",
                                f"{prefix}.task_id required",
                            )
                        )
                    sha = task.get("prototype_package_sha256")
                    if not _nonempty_str(sha) or not HASH_RE.fullmatch(str(sha)):
                        errors.append(
                            _err(
                                "milestone_plan_prototype_alignment_failed",
                                f"{prefix}.prototype_package_sha256 must be 64 hex",
                            )
                        )
                    if task.get("aligned") is not True:
                        errors.append(
                            _err(
                                "milestone_plan_prototype_alignment_failed",
                                f"{prefix}.aligned must be true before Gate/pack accept",
                            )
                        )
                    if not _nonempty_str(task.get("evidence")):
                        errors.append(
                            _err(
                                "milestone_plan_prototype_alignment_failed",
                                f"{prefix}.evidence required",
                            )
                        )
            if closeout and a_status != "aligned":
                errors.append(
                    _err(
                        "milestone_plan_prototype_alignment_failed",
                        "prototype_alignment.status must be aligned at closeout",
                    )
                )
            if a_status == "conflict":
                errors.append(
                    _err(
                        "milestone_plan_prototype_alignment_failed",
                        "prototype_alignment.status=conflict blocks acceptance",
                    )
                )

    in_scope = data.get("in_scope_task_ids")
    if closeout and (not isinstance(in_scope, list) or not in_scope):
        errors.append(
            _err(
                "milestone_plan_acceptance_pack_incomplete",
                "in_scope_task_ids required at closeout",
            )
        )

    ok = not errors
    code = "ok"
    if not ok:
        priority = [
            "milestone_plan_prototype_alignment_failed",
            "milestone_plan_test_lanes_incomplete",
            "plan_acceptance_html_link_required",
            "milestone_plan_acceptance_pack_incomplete",
        ]
        present = {e["code"] for e in errors}
        code = next((c for c in priority if c in present), errors[0]["code"])
    return {"ok": ok, "code": code, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Pack Markdown/JSON path")
    parser.add_argument(
        "--require-links",
        action="store_true",
        help="Require link_emitted and absolute file:// URLs",
    )
    parser.add_argument(
        "--require-closeout",
        action="store_true",
        help="Apply closeout rules even when status is still draft",
    )
    args = parser.parse_args(argv)
    result = lint_milestone_plan_acceptance_pack(
        args.path,
        require_links=args.require_links,
        require_closeout=args.require_closeout,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
