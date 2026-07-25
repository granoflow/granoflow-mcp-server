#!/usr/bin/env python3
"""Lint prototype_link_ledger: absolute file:// links, on-disk HTML, digest."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

SCHEMA = "granoflow_prototype_link_ledger_v1"
VALID_STATUS = frozenset({"not_applicable", "pending", "complete"})
HTML_COVERAGE_SCHEMA = "granoflow_prototype_html_coverage_v1"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((file://[^)\s]+)\)")


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def _extract_ledger(data: Any) -> Any:
    if isinstance(data, list):
        # Bare list is a rejected transitional shape; return a marker object.
        return {"_bare_list": True, "entries": data}
    if not isinstance(data, dict):
        return None
    if "prototype_link_ledger" in data:
        value = data.get("prototype_link_ledger")
        if isinstance(value, list):
            return {"_bare_list": True, "entries": value}
        return value
    if data.get("schema") == SCHEMA:
        return data
    return None


def _extract_html_coverage(data: Any) -> Any:
    if not isinstance(data, dict):
        return None
    if "prototype_html_coverage" in data:
        return data.get("prototype_html_coverage")
    if data.get("schema") == HTML_COVERAGE_SCHEMA:
        return data
    return None


def path_to_file_url(path: Path) -> str:
    return path.expanduser().resolve().as_uri()


def file_url_to_path(file_url: str) -> Path | None:
    parsed = urlparse(file_url)
    if parsed.scheme != "file":
        return None
    # file:///abs/path → /abs/path; keep platform Path behavior.
    path = unquote(parsed.path)
    if path == "":
        return None
    return Path(path)


def _markdown_file_urls(digest: str) -> set[str]:
    return {match.group(1).strip() for match in MARKDOWN_LINK_RE.finditer(digest)}


def lint_prototype_link_ledger(
    data: Any,
    *,
    require_complete: bool = False,
    html_coverage: Any | None = None,
    prototype_root: Path | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    block = _extract_ledger(data)
    if block is None:
        return {
            "ok": False,
            "code": "prototype_link_ledger_unread",
            "errors": [
                _err(
                    "prototype_link_ledger_unread",
                    "prototype_link_ledger object required",
                )
            ],
        }
    if not isinstance(block, dict):
        return {
            "ok": False,
            "code": "prototype_link_ledger_lint_failed",
            "errors": [
                _err(
                    "prototype_link_ledger_lint_failed",
                    "prototype_link_ledger must be an object",
                )
            ],
        }

    if block.get("_bare_list") is True:
        return {
            "ok": False,
            "code": "prototype_link_ledger_lint_failed",
            "errors": [
                _err(
                    "prototype_link_ledger_lint_failed",
                    "prototype_link_ledger must use schema "
                    f"{SCHEMA} with entries[]; bare lists are not accepted",
                )
            ],
        }

    if block.get("contract_loaded") is not True:
        errors.append(
            _err(
                "prototype_link_ledger_unread",
                "contract_loaded must be true",
            )
        )

    if block.get("schema") != SCHEMA:
        errors.append(
            _err(
                "prototype_link_ledger_lint_failed",
                f"schema must be {SCHEMA}",
            )
        )

    status = block.get("status")
    if status not in VALID_STATUS:
        errors.append(
            _err(
                "prototype_link_ledger_lint_failed",
                "status must be not_applicable|pending|complete",
            )
        )
        return {
            "ok": False,
            "code": "prototype_link_ledger_lint_failed",
            "errors": errors,
        }

    if status == "not_applicable":
        if require_complete:
            # not_applicable is a valid complete state for non-UI tasks.
            return {
                "ok": not errors,
                "code": "ok" if not errors else errors[0]["code"],
                "errors": errors,
            }
        return {
            "ok": not errors,
            "code": "ok" if not errors else errors[0]["code"],
            "errors": errors,
        }

    if require_complete and status != "complete":
        errors.append(
            _err(
                "prototype_link_ledger_incomplete",
                "status must be complete before Analysis confirmation "
                "(or not_applicable when no UI prototype)",
            )
        )

    entries = block.get("entries")
    if not isinstance(entries, list):
        errors.append(
            _err(
                "prototype_link_ledger_lint_failed",
                "entries must be a list",
            )
        )
        return {
            "ok": False,
            "code": "prototype_link_ledger_lint_failed",
            "errors": errors,
        }

    if status == "complete" and len(entries) == 0:
        errors.append(
            _err(
                "prototype_link_ledger_incomplete",
                "status=complete requires at least one ledger entry",
            )
        )

    resolved_paths: dict[str, Path] = {}
    for index, entry in enumerate(entries):
        prefix = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(
                _err(
                    "prototype_link_incomplete",
                    f"{prefix} must be an object",
                )
            )
            continue

        title = entry.get("title")
        absolute_path = entry.get("absolute_path")
        file_url = entry.get("file_url")
        entity = entry.get("entity")
        sha = entry.get("sha_or_pending")

        if not _nonempty_str(title):
            errors.append(_err("prototype_link_incomplete", f"{prefix}.title required"))
        if not _nonempty_str(entity):
            errors.append(_err("prototype_link_incomplete", f"{prefix}.entity required"))
        if not _nonempty_str(sha):
            errors.append(
                _err(
                    "prototype_link_incomplete",
                    f"{prefix}.sha_or_pending required",
                )
            )

        if not _nonempty_str(absolute_path):
            errors.append(
                _err(
                    "prototype_link_incomplete",
                    f"{prefix}.absolute_path required",
                )
            )
            continue

        path = Path(str(absolute_path).strip())
        if not path.is_absolute():
            errors.append(
                _err(
                    "prototype_link_not_absolute",
                    f"{prefix}.absolute_path must be absolute, got {absolute_path!r}",
                )
            )
            continue

        if not _nonempty_str(file_url):
            errors.append(
                _err(
                    "prototype_link_incomplete",
                    f"{prefix}.file_url required",
                )
            )
            continue

        file_url_s = str(file_url).strip()
        if not file_url_s.startswith("file://"):
            errors.append(
                _err(
                    "prototype_link_not_absolute",
                    f"{prefix}.file_url must be an absolute file:// URL",
                )
            )
            continue

        expected_url = path_to_file_url(path)
        url_path = file_url_to_path(file_url_s)
        if url_path is None:
            errors.append(
                _err(
                    "prototype_link_not_absolute",
                    f"{prefix}.file_url is not a usable file:// URL",
                )
            )
            continue

        # Accept either exact as_uri match or same resolved filesystem path.
        if file_url_s != expected_url and url_path.resolve() != path.resolve():
            errors.append(
                _err(
                    "prototype_link_not_absolute",
                    f"{prefix}.file_url must match absolute_path " f"(expected {expected_url})",
                )
            )

        if not path.is_file():
            errors.append(
                _err(
                    "prototype_link_file_missing",
                    f"{prefix}: HTML file missing at {path}",
                )
            )
            continue

        if path.stat().st_size <= 0:
            errors.append(
                _err(
                    "prototype_link_file_missing",
                    f"{prefix}: HTML file is empty at {path}",
                )
            )
            continue

        if path.suffix.lower() not in {".html", ".htm"}:
            errors.append(
                _err(
                    "prototype_link_incomplete",
                    f"{prefix}: absolute_path must be an .html file",
                )
            )
            continue

        resolved_paths[str(path.resolve())] = path.resolve()

    if status == "complete":
        if block.get("chat_digest_emitted") is not True:
            errors.append(
                _err(
                    "prototype_link_digest_required",
                    "chat_digest_emitted must be true when status=complete "
                    "(Analysis turn must show clickable Prototype Link 小结/Digest)",
                )
            )
        digest = block.get("markdown_digest")
        if not _nonempty_str(digest):
            errors.append(
                _err(
                    "prototype_link_digest_required",
                    "markdown_digest required when status=complete",
                )
            )
        else:
            linked = _markdown_file_urls(str(digest))
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                file_url = entry.get("file_url")
                if not _nonempty_str(file_url):
                    continue
                if str(file_url).strip() not in linked:
                    errors.append(
                        _err(
                            "prototype_link_digest_required",
                            "markdown_digest must include a Markdown link "
                            f"[{entry.get('title', 'prototype')}]({file_url})",
                        )
                    )

    if html_coverage is not None and status != "not_applicable":
        coverage = _extract_html_coverage(html_coverage)
        if not isinstance(coverage, dict):
            errors.append(
                _err(
                    "prototype_link_ledger_lint_failed",
                    "html_coverage input must contain prototype_html_coverage",
                )
            )
        else:
            surfaces = coverage.get("surfaces")
            if not isinstance(surfaces, list):
                errors.append(
                    _err(
                        "prototype_link_ledger_lint_failed",
                        "prototype_html_coverage.surfaces must be a list",
                    )
                )
            else:
                root = prototype_root.resolve() if prototype_root else None
                for surface in surfaces:
                    if not isinstance(surface, dict):
                        continue
                    if surface.get("coverage") != "covered":
                        continue
                    ref = surface.get("html_prototype_ref")
                    surface_id = surface.get("surface_id", "?")
                    if not _nonempty_str(ref):
                        errors.append(
                            _err(
                                "prototype_link_incomplete",
                                f"html_coverage surface {surface_id} has empty "
                                "html_prototype_ref",
                            )
                        )
                        continue
                    ref_s = str(ref).strip()
                    # Allow ledger file_url or absolute path as html_prototype_ref.
                    if ref_s.startswith("file://"):
                        candidate = file_url_to_path(ref_s)
                    else:
                        candidate = Path(ref_s)
                        if not candidate.is_absolute():
                            if root is None:
                                errors.append(
                                    _err(
                                        "prototype_link_ledger_lint_failed",
                                        "--prototype-root required to resolve "
                                        f"relative html_prototype_ref for {surface_id}",
                                    )
                                )
                                continue
                            candidate = root / candidate
                    if candidate is None:
                        errors.append(
                            _err(
                                "prototype_link_incomplete",
                                f"surface {surface_id} html_prototype_ref unusable",
                            )
                        )
                        continue
                    key = str(candidate.resolve())
                    if key not in resolved_paths:
                        errors.append(
                            _err(
                                "prototype_link_ledger_incomplete",
                                f"covered surface {surface_id} HTML is not in "
                                f"prototype_link_ledger ({candidate})",
                            )
                        )

    ok = not errors
    code = "ok"
    if not ok:
        # Prefer the most actionable fail-closed code.
        priority = [
            "prototype_link_ledger_unread",
            "prototype_link_file_missing",
            "prototype_link_not_absolute",
            "prototype_link_digest_required",
            "prototype_link_incomplete",
            "prototype_link_ledger_incomplete",
            "prototype_link_ledger_lint_failed",
        ]
        present = {e["code"] for e in errors}
        code = next((c for c in priority if c in present), errors[0]["code"])
    return {"ok": ok, "code": code, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="YAML/JSON ledger path")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Fail unless status is complete (or not_applicable)",
    )
    parser.add_argument(
        "--html-coverage",
        type=Path,
        default=None,
        help="Optional prototype_html_coverage YAML/JSON to cross-check",
    )
    parser.add_argument(
        "--prototype-root",
        type=Path,
        default=None,
        help="Root for resolving relative html_prototype_ref values",
    )
    args = parser.parse_args(argv)
    data = _load(args.path)
    html_coverage = _load(args.html_coverage) if args.html_coverage else None
    result = lint_prototype_link_ledger(
        data,
        require_complete=args.require_complete,
        html_coverage=html_coverage,
        prototype_root=args.prototype_root,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
