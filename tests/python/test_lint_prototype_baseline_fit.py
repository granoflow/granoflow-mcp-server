#!/usr/bin/env python3
"""Tests for lint_prototype_baseline_fit.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_prototype_baseline_fit.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_baseline_fit", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()

FITTED = """<!DOCTYPE html><html><head><style>
:root[data-baseline-tokens="locked"] {
  --font-display: "Literata", Georgia, serif;
  --font-ui: "Source Sans 3", system-ui, sans-serif;
  --primary: oklch(0.48 0.09 180);
  --radius: 14px;
}
</style></head><body>
<div class="phone" data-product-ui="true"><p>正文</p></div>
</body></html>
"""

MISSING = """<!DOCTYPE html><html><body>
<div class="phone"><p>正文</p></div>
</body></html>
"""

DRIFT = """<!DOCTYPE html><html><head><style>
:root[data-baseline-tokens="locked"] {
  --font-display: "Literata", Georgia, serif;
  --font-ui: "Source Sans 3", system-ui, sans-serif;
  --primary: oklch(0.99 0.20 300);
  --radius: 14px;
}
</style></head><body><div class="phone">x</div></body></html>
"""


class LintPrototypeBaselineFitTests(unittest.TestCase):
    def test_fitted_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(FITTED, encoding="utf-8")
            result = MOD.lint_html(path, None)
            self.assertTrue(result["ok"], result)

    def test_missing_tokens_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(MISSING, encoding="utf-8")
            result = MOD.lint_html(path, None)
            self.assertFalse(result["ok"])
            codes = {e["code"] for e in result["errors"]}
            self.assertIn("prototype_spec_tokens_not_loaded", codes)

    def test_drift_vs_baseline_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "index.html"
            tokens = Path(tmp) / "tokens.css"
            html.write_text(DRIFT, encoding="utf-8")
            tokens.write_text(
                ':root{--font-display:"Literata", Georgia, serif;'
                '--font-ui:"Source Sans 3", system-ui, sans-serif;'
                "--primary: oklch(0.48 0.09 180);--radius: 14px;}",
                encoding="utf-8",
            )
            result = MOD.lint_html(html, tokens)
            self.assertFalse(result["ok"])
            codes = {e["code"] for e in result["errors"]}
            self.assertIn("prototype_spec_tokens_drift", codes)

    def test_cli_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(MISSING, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
