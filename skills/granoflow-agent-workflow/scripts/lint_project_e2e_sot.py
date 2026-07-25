#!/usr/bin/env python3
"""Deprecated wrapper: delegates to granoflow-project-sot lint_project_sot.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    new_lint = (
        Path(__file__).resolve().parents[2]
        / "granoflow-project-sot"
        / "scripts"
        / "lint_project_sot.py"
    )
    tip = {
        "ok": False,
        "code": "project_sot_legacy_path",
        "detail": (
            "lint_project_e2e_sot.py is deprecated; "
            "use skills/granoflow-project-sot/scripts/lint_project_sot.py "
            "and temp/project-sot.yaml"
        ),
    }
    # Always print migration tip on stderr so JSON stdout stays machine-clean.
    print(json.dumps(tip, ensure_ascii=False), file=sys.stderr)
    if not new_lint.is_file():
        print(
            json.dumps(
                {
                    "ok": False,
                    "code": "project_sot_lint_failed",
                    "errors": [
                        {
                            "code": "project_sot_lint_failed",
                            "detail": f"missing delegate {new_lint}",
                        }
                    ],
                },
                ensure_ascii=False,
            )
        )
        return 1
    completed = subprocess.run(
        [sys.executable, str(new_lint), *args],
        check=False,
    )
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
