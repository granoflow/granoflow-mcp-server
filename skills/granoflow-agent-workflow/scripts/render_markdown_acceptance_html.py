#!/usr/bin/env python3
"""Probe Pandoc+Mermaid toolchain and render Markdown acceptance packs to HTML.

Exit codes:
  0 — probe ready and/or HTML written
  2 — required tools missing (Markdown-only fallback)
  3 — render/probe error
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_markdown_html_render_v1"
VENDOR_LUA = Path(__file__).resolve().parent / "vendor" / "pandoc-ext-diagram" / "diagram.lua"


def _which(name: str) -> str | None:
    return shutil.which(name)


def path_to_file_url(path: Path) -> str:
    """Return a clickable file:// URL for absolute local paths."""
    resolved = path.expanduser().resolve()
    return resolved.as_uri()


def resolve_diagram_lua(explicit: str | None) -> Path | None:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        return path if path.is_file() else None
    env = os.environ.get("GRANOFLOW_DIAGRAM_LUA")
    if env:
        path = Path(env).expanduser().resolve()
        return path if path.is_file() else None
    if VENDOR_LUA.is_file():
        return VENDOR_LUA
    return None


def probe_toolchain(diagram_lua: Path | None = None) -> dict[str, Any]:
    lua = resolve_diagram_lua(str(diagram_lua) if diagram_lua else None)
    pandoc = _which("pandoc")
    mmdc = _which("mmdc")
    plantuml = _which("plantuml")
    tools = {
        "pandoc": pandoc is not None,
        "mmdc": mmdc is not None,
        "diagram_lua": lua is not None,
        "plantuml": plantuml is not None,
    }
    missing = [name for name, ok in tools.items() if name != "plantuml" and not ok]
    status = "ready" if not missing else "missing"
    return {
        "schema": SCHEMA,
        "status": status,
        "tools": tools,
        "paths": {
            "pandoc": pandoc,
            "mmdc": mmdc,
            "diagram_lua": str(lua) if lua else None,
            "plantuml": plantuml,
        },
        "missing": missing,
        "optional_missing": [] if plantuml else ["plantuml"],
        "token_note": (
            "Markdown→HTML conversion is a local CLI step and does not consume LLM tokens."
        ),
        "install_hint": {
            "macos_homebrew": [
                "brew install pandoc",
                "npm install -g @mermaid-js/mermaid-cli",
                "brew install plantuml  # optional UML",
            ],
        },
    }


def render_html(
    markdown_path: Path,
    output_path: Path | None = None,
    *,
    diagram_lua: Path | None = None,
) -> dict[str, Any]:
    md = markdown_path.expanduser().resolve()
    probe = probe_toolchain(diagram_lua)
    if probe["status"] != "ready":
        return {
            **probe,
            "code": "markdown_html_toolchain_missing",
            "html_path": None,
            "html_file_url": None,
            "markdown_path": str(md) if md.is_file() else str(markdown_path),
            "markdown_file_url": path_to_file_url(md) if md.is_file() else None,
            "ok": False,
        }

    if not md.is_file():
        return {
            "schema": SCHEMA,
            "status": "error",
            "code": "markdown_html_render_failed",
            "ok": False,
            "detail": f"markdown not found: {md}",
            "html_path": None,
            "html_file_url": None,
            "markdown_path": str(md),
            "markdown_file_url": None,
            "tool_probe": probe,
        }

    out = output_path.expanduser().resolve() if output_path else md.with_suffix(".html")
    lua = Path(probe["paths"]["diagram_lua"])
    cmd = [
        "pandoc",
        str(md),
        "--from",
        "gfm",
        "--lua-filter",
        str(lua),
        "--embed-resources",
        "--standalone",
        "-o",
        str(out),
    ]
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "schema": SCHEMA,
            "status": "error",
            "code": "markdown_html_render_failed",
            "ok": False,
            "detail": str(exc),
            "html_path": None,
            "tool_probe": probe,
        }

    if completed.returncode != 0 or not out.is_file():
        return {
            "schema": SCHEMA,
            "status": "error",
            "code": "markdown_html_render_failed",
            "ok": False,
            "detail": (completed.stderr or completed.stdout or "pandoc failed").strip(),
            "html_path": None,
            "tool_probe": probe,
            "cmd": cmd,
        }

    return {
        "schema": SCHEMA,
        "status": "ready",
        "code": "ok",
        "ok": True,
        "html_path": str(out),
        "html_file_url": path_to_file_url(out),
        "markdown_path": str(md),
        "markdown_file_url": path_to_file_url(md),
        "link_block_hint": {
            "primary": path_to_file_url(out),
            "secondary": path_to_file_url(md),
            "note": probe["token_note"],
        },
        "tool_probe": probe,
        "token_note": probe["token_note"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true", help="Only probe toolchain")
    parser.add_argument("--input", type=Path, help="Markdown pack path")
    parser.add_argument("--output", type=Path, help="HTML output path")
    parser.add_argument("--diagram-lua", type=Path, help="Override diagram.lua path")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine JSON (default)",
        default=True,
    )
    args = parser.parse_args(argv)

    if args.probe or args.input is None:
        result = probe_toolchain(args.diagram_lua)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "ready" else 2

    result = render_html(args.input, args.output, diagram_lua=args.diagram_lua)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("ok"):
        return 0
    if result.get("code") == "markdown_html_toolchain_missing":
        return 2
    return 3


if __name__ == "__main__":
    sys.exit(main())
