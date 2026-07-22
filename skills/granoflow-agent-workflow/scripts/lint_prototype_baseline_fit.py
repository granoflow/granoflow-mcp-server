#!/usr/bin/env python3
"""Lint post-Baseline prototype HTML for Spec token + Shell fit markers.

Fail closed when option HTML looks like a generic parallel phone frame:
missing locked token root, missing required CSS custom properties, or
(optional) drifted token values vs a Baseline tokens file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_VARS = (
    "--font-display",
    "--font-ui",
    "--primary",
    "--radius",
)

TOKEN_ROOT_RE = re.compile(
    r'data-baseline-tokens\s*=\s*["\']locked["\']',
    re.I,
)
VAR_DECL_RE = re.compile(
    r"(--[a-zA-Z0-9-]+)\s*:\s*([^;]+);",
)


def parse_vars(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for name, value in VAR_DECL_RE.findall(text):
        found[name] = " ".join(value.split())
    return found


def load_baseline_vars(path: Path) -> dict[str, str]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
        # Accept flat {"--primary": "..."} or nested draft with css-ish strings
        flat: dict[str, str] = {}
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and key.startswith("--"):
                    flat[key] = " ".join(value.split())
                elif key in {"primary", "color.primary"} and isinstance(value, str):
                    flat["--primary"] = " ".join(value.split())
        return flat
    return parse_vars(raw)


def lint_html(html_path: Path, baseline_tokens: Path | None) -> dict:
    text = html_path.read_text(encoding="utf-8")
    errors: list[dict[str, str]] = []

    if not TOKEN_ROOT_RE.search(text):
        errors.append(
            {
                "code": "prototype_spec_tokens_not_loaded",
                "detail": 'missing data-baseline-tokens="locked"',
            }
        )

    vars_in_html = parse_vars(text)
    for name in REQUIRED_VARS:
        if name not in vars_in_html:
            errors.append(
                {
                    "code": "prototype_spec_tokens_not_loaded",
                    "detail": f"missing CSS custom property {name}",
                }
            )

    if baseline_tokens is not None:
        if not baseline_tokens.is_file():
            errors.append(
                {
                    "code": "prototype_baseline_fit_lint_failed",
                    "detail": f"baseline tokens file not found: {baseline_tokens}",
                }
            )
        else:
            base = load_baseline_vars(baseline_tokens)
            for name in REQUIRED_VARS:
                if name in base and name in vars_in_html:
                    if vars_in_html[name] != base[name]:
                        errors.append(
                            {
                                "code": "prototype_spec_tokens_drift",
                                "detail": (
                                    f"{name} drifted: html={vars_in_html[name]!r} "
                                    f"baseline={base[name]!r}"
                                ),
                            }
                        )

    # Soft structural smell: Inter/Roboto as only display stack while Literata
    # is common in GranoReader Baseline — warn as mismatch when present without
    # Literata/Source Sans.
    if re.search(r"font-family:\s*Inter\b|font-family:\s*Roboto\b", text, re.I):
        if "Literata" not in text and "Source Sans" not in text:
            errors.append(
                {
                    "code": "prototype_shell_chrome_mismatch",
                    "detail": "generic Inter/Roboto stack without Baseline typefaces",
                }
            )

    ok = not errors
    return {
        "ok": ok,
        "path": str(html_path),
        "errors": errors,
        "code": "ok" if ok else "prototype_baseline_fit_lint_failed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Path to option index.html")
    parser.add_argument(
        "--baseline-tokens",
        type=Path,
        default=None,
        help="Optional Baseline tokens CSS or flat JSON for drift check",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args(argv)

    if not args.html.is_file():
        result = {
            "ok": False,
            "code": "prototype_baseline_fit_lint_failed",
            "errors": [{"code": "missing_file", "detail": str(args.html)}],
        }
    else:
        result = lint_html(args.html, args.baseline_tokens)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["ok"]:
            print(f"ok: true  {args.html}")
        else:
            print(f"ok: false  {args.html}")
            for err in result.get("errors", []):
                print(f"  - {err['code']}: {err['detail']}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
