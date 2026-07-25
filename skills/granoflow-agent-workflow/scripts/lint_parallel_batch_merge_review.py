#!/usr/bin/env python3
"""Lint parallel batch merge-review packs: schema, workers, links."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

DOC_TYPE = "parallel_batch_merge_review"
SCHEMA = "granoflow_parallel_batch_merge_review_v1"
VALID_STATUS = frozenset({"draft", "pending_acceptance", "accepted", "rejected", "superseded"})
VALID_MODE = frozenset({"interactive", "unattended"})
VALID_ISOLATION = frozenset({"same_tree_disjoint", "worktree", "serialized"})
VALID_RECHECK = frozenset({"pending", "parallel_safe", "conflict"})
VALID_AUTHORITY = frozenset({None, "user_explicit", "unattended_grant"})


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("pack must start with YAML frontmatter or be JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("JSON pack root must be an object")
        return data
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("YAML frontmatter closing --- missing")
    fm_text = text[3:end].strip("\n")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(fm_text) or {}
    except ImportError:
        data = json.loads(fm_text)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data


def _file_url_to_path(file_url: str) -> Path | None:
    parsed = urlparse(file_url)
    if parsed.scheme != "file":
        return None
    path = unquote(parsed.path)
    return Path(path) if path else None


def lint_parallel_batch_merge_review(
    path: Path,
    *,
    require_links: bool = False,
    require_closeout: bool = False,
) -> dict[str, Any]:
    try:
        data = _load_frontmatter(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "code": "parallel_batch_merge_review_incomplete",
            "errors": [_err("parallel_batch_merge_review_incomplete", str(exc))],
        }

    errors: list[dict[str, str]] = []

    if data.get("doc_type") != DOC_TYPE:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                f"doc_type must be {DOC_TYPE}",
            )
        )
    schema = data.get("schema")
    if schema is not None and schema != SCHEMA:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                f"schema must be {SCHEMA} when present",
            )
        )
    if not _nonempty_str(data.get("batch_id")):
        errors.append(_err("parallel_batch_merge_review_incomplete", "batch_id required"))
    if data.get("status") not in VALID_STATUS:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                "status must be draft|pending_acceptance|accepted|rejected|superseded",
            )
        )
    if data.get("interaction_mode") not in VALID_MODE:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                "interaction_mode must be interactive|unattended",
            )
        )
    if data.get("host_isolation") not in VALID_ISOLATION:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                "host_isolation must be same_tree_disjoint|worktree|serialized",
            )
        )
    if data.get("pairwise_recheck") not in VALID_RECHECK:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                "pairwise_recheck must be pending|parallel_safe|conflict",
            )
        )

    authority = data.get("decision_authority")
    if authority not in VALID_AUTHORITY:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                "decision_authority must be null|user_explicit|unattended_grant",
            )
        )

    workers = data.get("workers")
    if not isinstance(workers, list) or not workers:
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                "workers must be a non-empty list",
            )
        )
        workers = []
    for i, row in enumerate(workers):
        if not isinstance(row, dict):
            errors.append(
                _err(
                    "parallel_batch_merge_review_incomplete",
                    f"workers[{i}] must be an object",
                )
            )
            continue
        if not _nonempty_str(row.get("task_id")):
            errors.append(
                _err(
                    "parallel_batch_merge_review_incomplete",
                    f"workers[{i}].task_id required",
                )
            )
        surfaces = row.get("write_surfaces")
        if not isinstance(surfaces, list):
            errors.append(
                _err(
                    "parallel_batch_merge_review_incomplete",
                    f"workers[{i}].write_surfaces must be a list",
                )
            )
        if not isinstance(row.get("exit_ok"), bool):
            errors.append(
                _err(
                    "parallel_batch_merge_review_incomplete",
                    f"workers[{i}].exit_ok must be a boolean",
                )
            )

    closeout = require_closeout or data.get("status") in {
        "pending_acceptance",
        "accepted",
    }
    if closeout:
        if data.get("pairwise_recheck") == "pending":
            errors.append(
                _err(
                    "parallel_batch_merge_review_incomplete",
                    "pairwise_recheck must not be pending at closeout",
                )
            )
        if data.get("pairwise_recheck") == "conflict" and data.get("status") == "accepted":
            errors.append(
                _err(
                    "parallel_batch_merge_review_unaccepted",
                    "pairwise_recheck=conflict blocks accepted",
                )
            )
        for i, row in enumerate(workers):
            if isinstance(row, dict) and not _nonempty_str(row.get("delivery_ref")):
                errors.append(
                    _err(
                        "parallel_batch_merge_review_incomplete",
                        f"workers[{i}].delivery_ref required at closeout",
                    )
                )
        if data.get("status") == "accepted":
            if data.get("interaction_mode") == "interactive":
                if authority != "user_explicit":
                    errors.append(
                        _err(
                            "parallel_batch_merge_review_unaccepted",
                            "interactive accepted requires decision_authority=user_explicit",
                        )
                    )
            elif authority != "unattended_grant":
                errors.append(
                    _err(
                        "parallel_batch_merge_review_unaccepted",
                        "unattended accepted requires decision_authority=unattended_grant",
                    )
                )

    html_render = data.get("html_render")
    if not isinstance(html_render, dict):
        errors.append(
            _err(
                "parallel_batch_merge_review_incomplete",
                "html_render object required",
            )
        )
        html_render = {}

    if require_links or closeout:
        link_emitted = html_render.get("link_emitted")
        md_url = html_render.get("markdown_file_url")
        html_url = html_render.get("html_file_url")
        html_status = html_render.get("status")
        if link_emitted is not True:
            errors.append(
                _err(
                    "parallel_batch_review_link_required",
                    "html_render.link_emitted must be true when links required",
                )
            )
        if not _nonempty_str(md_url) or not str(md_url).startswith("file://"):
            errors.append(
                _err(
                    "parallel_batch_review_link_required",
                    "html_render.markdown_file_url must be absolute file://",
                )
            )
        if html_status == "ready":
            if not _nonempty_str(html_url) or not str(html_url).startswith("file://"):
                errors.append(
                    _err(
                        "parallel_batch_review_link_required",
                        "html_render.html_file_url required when status=ready",
                    )
                )
            else:
                html_path = _file_url_to_path(str(html_url))
                if html_path is None or not html_path.is_file():
                    errors.append(
                        _err(
                            "parallel_batch_review_link_required",
                            "html_render.html_file_url must point to an existing file",
                        )
                    )

    ok = not errors
    code = "ok"
    if not ok:
        priority = [
            "parallel_batch_merge_review_unaccepted",
            "parallel_batch_review_link_required",
            "parallel_batch_merge_review_incomplete",
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
    result = lint_parallel_batch_merge_review(
        args.path,
        require_links=args.require_links,
        require_closeout=args.require_closeout,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
