#!/usr/bin/env python3
"""Lint candidate prototype HTML against confirmed sibling chrome authorities.

Fail closed when a new page invents a parallel control dialect after siblings
in the same chrome family were visually confirmed (see
prototype-confirmed-chrome-lock.md).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Core chrome markers: if an authority uses them, a candidate .sheet Must reuse.
CORE_MARKERS = (
    "sheet-title-ico",
    "tbtn",
)

# Modern vocabulary signals (authority-side) that ban legacy action dialect.
MODERN_MARKERS = (
    "sheet-title-ico",
    "tbtn",
    "pref-ico",
)

# Legacy dialect markers forbidden when any authority uses the modern vocab.
LEGACY_ACTION_RE = re.compile(
    r"""class\s*=\s*["'][^"']*\bbtn\b[^"']*\bbp\b""",
    re.I,
)
LEGACY_SECONDARY_RE = re.compile(
    r"""class\s*=\s*["'][^"']*\bbtn\b[^"']*\bbs\b""",
    re.I,
)
SHEET_RE = re.compile(r"""class\s*=\s*["'][^"']*\bsheet\b""", re.I)
CLASS_TOKEN_RE = re.compile(r"""class\s*=\s*["']([^"']+)["']""", re.I)


def class_tokens(text: str) -> set[str]:
    found: set[str] = set()
    for block in CLASS_TOKEN_RE.findall(text):
        for token in block.split():
            found.add(token)
    return found


def lint_candidate(candidate: Path, authorities: list[Path]) -> dict:
    cand_text = candidate.read_text(encoding="utf-8")
    errors: list[dict[str, str]] = []

    if not authorities:
        return {
            "ok": True,
            "path": str(candidate),
            "errors": [],
            "notApplicable": True,
            "reason": "no_authority_html",
        }

    auth_tokens: set[str] = set()
    for path in authorities:
        auth_tokens |= class_tokens(path.read_text(encoding="utf-8"))

    cand_tokens = class_tokens(cand_text)
    has_sheet = bool(SHEET_RE.search(cand_text))

    # Same-role reuse: core markers present in authority Must appear on
    # candidate sheets. Role-specific markers (e.g. pref-ico) are not forced
    # onto every sheet—only core dialect + legacy ban.
    required = [m for m in CORE_MARKERS if m in auth_tokens]
    if has_sheet:
        for marker in required:
            if marker not in cand_tokens:
                errors.append(
                    {
                        "code": "prototype_confirmed_chrome_lock_drift",
                        "detail": (
                            f"authority uses .{marker} but candidate .sheet "
                            f"frame is missing it"
                        ),
                    }
                )

    modern = any(m in auth_tokens for m in MODERN_MARKERS)
    if modern and has_sheet:
        if LEGACY_ACTION_RE.search(cand_text) or LEGACY_SECONDARY_RE.search(cand_text):
            errors.append(
                {
                    "code": "prototype_confirmed_chrome_lock_drift",
                    "detail": (
                        "candidate uses legacy .btn.bp/.btn.bs while authority "
                        "chrome uses tbtn/sheet-title-ico/pref-ico vocabulary"
                    ),
                }
            )

    return {
        "ok": not errors,
        "path": str(candidate),
        "errors": errors,
        "requiredMarkers": required,
        "authorityCount": len(authorities),
        "failCode": errors[0]["code"] if errors else None,
    }


def lint_many(candidates: list[Path], authorities: list[Path]) -> dict:
    files = [lint_candidate(path, authorities) for path in candidates]
    ok = all(item.get("ok") for item in files)
    fail = next((item.get("failCode") for item in files if item.get("failCode")), None)
    return {
        "ok": ok,
        "failCode": None if ok else (fail or "prototype_confirmed_chrome_lock_lint_failed"),
        "files": files,
        "authorityCount": len(authorities),
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument(
        "candidates",
        nargs="+",
        type=Path,
        help="Candidate option HTML files",
    )
    value.add_argument(
        "--authority",
        action="append",
        default=[],
        type=Path,
        help="Confirmed sibling authority HTML (repeatable)",
    )
    return value


def main() -> int:
    args = parser().parse_args()
    authorities = [path for path in args.authority if path.is_file()]
    missing_auth = [str(path) for path in args.authority if not path.is_file()]
    if missing_auth:
        print(
            json.dumps(
                {
                    "ok": False,
                    "failCode": "prototype_confirmed_chrome_lock_authority_missing",
                    "error": f"authority file(s) not found: {missing_auth}",
                },
                ensure_ascii=False,
            )
        )
        return 2
    result = lint_many(args.candidates, authorities)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
