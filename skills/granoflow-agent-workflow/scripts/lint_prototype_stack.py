#!/usr/bin/env python3
"""Lint prototype packages for Vanilla JS stack lock (v1).

Fails closed when TypeScript, JSX/Vue SFCs, npm/bundler toolchains, or
React/Preact/Vue/Svelte framework markers appear in a prototype source
directory (or extracted zip root).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FORBIDDEN_EXTENSIONS = frozenset({".ts", ".tsx", ".jsx", ".vue"})
FORBIDDEN_BASENAMES = frozenset(
    {
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lock",
        "bun.lockb",
    }
)
TSCONFIG_PREFIX = "tsconfig"
CONTENT_SCAN_SUFFIXES = frozenset({".html", ".htm", ".js", ".css", ".mjs", ".cjs"})

FRAMEWORK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "react_import",
        re.compile(
            r"""(?:from\s+['"]react(?:-dom)?['"]|require\s*\(\s*['"]react(?:-dom)?['"]\s*\))""",
            re.I,
        ),
    ),
    (
        "preact_import",
        re.compile(
            r"""(?:from\s+['"]preact(?:/[\w.-]+)?['"]|require\s*\(\s*['"]preact(?:/[\w.-]+)?['"]\s*\))""",
            re.I,
        ),
    ),
    (
        "vue_import",
        re.compile(
            r"""(?:from\s+['"]vue['"]|require\s*\(\s*['"]vue['"]\s*\))""",
            re.I,
        ),
    ),
    (
        "svelte_import",
        re.compile(
            r"""(?:from\s+['"]svelte(?:/[\w.-]+)?['"]|require\s*\(\s*['"]svelte(?:/[\w.-]+)?['"]\s*\))""",
            re.I,
        ),
    ),
    (
        "framework_cdn",
        re.compile(
            r"""(?:unpkg\.com|jsdelivr\.net|cdnjs\.cloudflare\.com)/[^"'\\\s>]*(?:react|preact|vue|svelte)""",
            re.I,
        ),
    ),
    (
        "react_global",
        re.compile(r"""\bReactDOM\b|\bReact\.createElement\b"""),
    ),
    (
        "vue_global",
        re.compile(r"""\bVue\.createApp\b|\bvue\.global(?:\.prod)?\.js\b""", re.I),
    ),
]


def _err(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _is_tsconfig(name: str) -> bool:
    lower = name.lower()
    return lower == "tsconfig.json" or (
        lower.startswith(TSCONFIG_PREFIX) and lower.endswith(".json")
    )


def lint_prototype_stack(root: Path) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    root = root.resolve()
    if not root.is_dir():
        return {
            "ok": False,
            "code": "prototype_stack_lint_failed",
            "errors": [_err("prototype_stack_lint_failed", f"not a directory: {root}")],
        }

    node_modules_reported = False
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        parts = path.relative_to(root).parts
        if "node_modules" in parts:
            if not node_modules_reported:
                nm = "/".join(parts[: parts.index("node_modules") + 1])
                errors.append(
                    _err(
                        "prototype_stack_forbidden_toolchain",
                        f"node_modules not allowed: {nm}",
                    )
                )
                node_modules_reported = True
            continue
        if not path.is_file():
            continue
        name = path.name
        suffix = path.suffix.lower()
        if suffix in FORBIDDEN_EXTENSIONS:
            errors.append(
                _err(
                    "prototype_stack_forbidden_language",
                    f"forbidden extension {suffix}: {rel}",
                )
            )
            continue
        if name.lower() in FORBIDDEN_BASENAMES or _is_tsconfig(name):
            errors.append(
                _err(
                    "prototype_stack_forbidden_toolchain",
                    f"forbidden toolchain file: {rel}",
                )
            )
            continue
        if suffix not in CONTENT_SCAN_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                errors.append(
                    _err(
                        "prototype_stack_lint_failed",
                        f"unreadable {rel}: {exc}",
                    )
                )
                continue
        for label, pattern in FRAMEWORK_PATTERNS:
            if pattern.search(text):
                errors.append(
                    _err(
                        "prototype_stack_forbidden_framework",
                        f"{label} in {rel}",
                    )
                )
                break

    # Deduplicate while preserving order
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, str]] = []
    for item in errors:
        key = (item["code"], item["detail"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    ok = not unique
    primary = "ok"
    if not ok:
        codes = {e["code"] for e in unique}
        for candidate in (
            "prototype_stack_forbidden_language",
            "prototype_stack_forbidden_framework",
            "prototype_stack_forbidden_toolchain",
            "prototype_stack_lint_failed",
        ):
            if candidate in codes:
                primary = candidate
                break
    return {"ok": ok, "code": primary, "errors": unique}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        type=Path,
        help="Prototype source directory or extracted zip root",
    )
    args = parser.parse_args()
    result = lint_prototype_stack(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
