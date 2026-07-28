#!/usr/bin/env python3
"""Lint LIB-pub-* knowledge_ref pointers on dependencies.approved rows."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REF_PATTERN = re.compile(r"^LIB-pub-[a-z0-9-]+$")
VALID_LINK_STATUS = frozenset({"linked", "skeleton", "gap", "superseded"})


def _err(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalize_package_slug(name: str) -> str:
    """Normalize approved[].name to LIB-pub slug segment."""
    slug = name.strip().lower().replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def expected_knowledge_ref(name: str) -> str:
    return f"LIB-pub-{normalize_package_slug(name)}"


def _extract_approved(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    deps = data.get("dependencies")
    if isinstance(deps, dict):
        approved = deps.get("approved")
        if isinstance(approved, list):
            return [row for row in approved if isinstance(row, dict)]
    engineering = data.get("engineering")
    if isinstance(engineering, dict):
        deps = engineering.get("dependencies")
        if isinstance(deps, dict):
            approved = deps.get("approved")
            if isinstance(approved, list):
                return [row for row in approved if isinstance(row, dict)]
    return None


def _load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyYAML required") from exc
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ValueError("root must be mapping")
    return loaded


def lint_library_knowledge_refs(
    data: dict[str, Any],
    *,
    require_init_ready: bool = False,
) -> dict[str, Any]:
    """Return {ok, errors} for dependencies.approved knowledge pointers."""
    errors: list[dict[str, str]] = []
    approved = _extract_approved(data)
    if approved is None:
        errors.append(
            _err(
                "library_knowledge_link_incomplete",
                "engineering.dependencies.approved block missing",
            )
        )
        return {"ok": False, "errors": errors}

    for index, row in enumerate(approved):
        name = row.get("name")
        if not _nonempty_str(name):
            continue
        package_name = str(name).strip()
        prefix = f"approved[{index}] ({package_name})"

        knowledge_ref = row.get("knowledge_ref")
        link_status = row.get("knowledge_link_status")
        superseded_by = row.get("superseded_by")
        gap_reason = row.get("knowledge_gap_reason")
        capability_critical = row.get("capability_critical") is True

        if knowledge_ref is not None and knowledge_ref != "":
            if not isinstance(knowledge_ref, str) or not REF_PATTERN.match(knowledge_ref):
                errors.append(
                    _err(
                        "library_knowledge_ref_invalid",
                        f"{prefix}: knowledge_ref must match LIB-pub-<slug>",
                    )
                )
            else:
                expected = expected_knowledge_ref(package_name)
                if link_status == "linked" and knowledge_ref != expected:
                    errors.append(
                        _err(
                            "library_knowledge_slug_mismatch",
                            (
                                f"{prefix}: linked knowledge_ref {knowledge_ref} "
                                f"!= expected {expected}"
                            ),
                        )
                    )

        if link_status is not None and link_status != "":
            if link_status not in VALID_LINK_STATUS:
                errors.append(
                    _err(
                        "library_knowledge_link_incomplete",
                        f"{prefix}: invalid knowledge_link_status {link_status!r}",
                    )
                )
            if link_status == "linked" and (
                not _nonempty_str(knowledge_ref)
                or (isinstance(knowledge_ref, str) and not REF_PATTERN.match(knowledge_ref))
            ):
                errors.append(
                    _err(
                        "library_knowledge_link_incomplete",
                        f"{prefix}: linked status requires valid knowledge_ref",
                    )
                )
            if link_status == "gap" and not _nonempty_str(gap_reason):
                errors.append(
                    _err(
                        "library_knowledge_link_incomplete",
                        f"{prefix}: gap status requires knowledge_gap_reason",
                    )
                )
            if link_status == "superseded" and not _nonempty_str(superseded_by):
                errors.append(
                    _err(
                        "library_knowledge_link_incomplete",
                        f"{prefix}: superseded status requires superseded_by",
                    )
                )

        if (
            superseded_by is not None
            and superseded_by != ""
            and (not isinstance(superseded_by, str) or not REF_PATTERN.match(superseded_by))
        ):
            errors.append(
                _err(
                    "library_knowledge_ref_invalid",
                    f"{prefix}: superseded_by must match LIB-pub-<slug>",
                )
            )

        if require_init_ready and capability_critical and link_status not in VALID_LINK_STATUS:
            errors.append(
                _err(
                    "library_knowledge_link_incomplete",
                    f"{prefix}: capability_critical row missing knowledge_link_status",
                )
            )

    return {"ok": not errors, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-work",
        type=Path,
        required=True,
        help="Project Work YAML path",
    )
    parser.add_argument(
        "--require-init-ready",
        action="store_true",
        help="Require knowledge_link_status on capability_critical rows",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "dry_run",
                    "mutates_state": False,
                    "planned_actions": ["Lint library knowledge_ref pointers"],
                    "artifacts": [str(args.project_work)],
                    "warnings": [],
                },
                ensure_ascii=False,
            )
        )
        return 0

    data = _load_yaml(args.project_work)
    result = lint_library_knowledge_refs(
        data,
        require_init_ready=args.require_init_ready,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
