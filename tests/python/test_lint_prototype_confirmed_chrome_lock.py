#!/usr/bin/env python3
"""Tests for lint_prototype_confirmed_chrome_lock.py."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_prototype_confirmed_chrome_lock.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_confirmed_chrome_lock", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()

AUTHORITY = """<!DOCTYPE html><html data-baseline-tokens="locked"><body>
<div class="phone" data-product-ui="true">
  <div class="sheet on">
    <div class="sheet-title-ico"><svg></svg></div>
    <button class="tbtn play" type="button" aria-label="发布"></button>
    <button class="pref-ico" type="button" aria-label="添加书签"></button>
  </div>
</div>
</body></html>
"""

FITTED = """<!DOCTYPE html><html data-baseline-tokens="locked"><body>
<div class="phone" data-product-ui="true">
  <div class="sheet on">
    <div class="sheet-title-ico"><svg></svg></div>
    <button class="tbtn" type="button" aria-label="取消"></button>
    <button class="tbtn play" type="button" aria-label="发布"></button>
  </div>
</div>
</body></html>
"""

DRIFT_LEGACY = """<!DOCTYPE html><html data-baseline-tokens="locked"><body>
<div class="phone" data-product-ui="true">
  <div class="sheet on">
    <h2>快速评论</h2>
    <button class="btn bp" type="button">发布</button>
    <button class="btn bs" type="button">取消</button>
  </div>
</div>
</body></html>
"""

DRIFT_MISSING_TITLE = """<!DOCTYPE html><html data-baseline-tokens="locked"><body>
<div class="phone" data-product-ui="true">
  <div class="sheet on">
    <button class="tbtn play" type="button" aria-label="发布"></button>
  </div>
</div>
</body></html>
"""


class LintConfirmedChromeLockTests(unittest.TestCase):
    def test_no_authority_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(FITTED, encoding="utf-8")
            result = MOD.lint_candidate(path, [])
            self.assertTrue(result["ok"])
            self.assertTrue(result.get("notApplicable"))

    def test_fitted_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth.html"
            cand = Path(tmp) / "cand.html"
            auth.write_text(AUTHORITY, encoding="utf-8")
            cand.write_text(FITTED, encoding="utf-8")
            result = MOD.lint_candidate(cand, [auth])
            self.assertTrue(result["ok"], result)

    def test_legacy_btn_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth.html"
            cand = Path(tmp) / "cand.html"
            auth.write_text(AUTHORITY, encoding="utf-8")
            cand.write_text(DRIFT_LEGACY, encoding="utf-8")
            result = MOD.lint_candidate(cand, [auth])
            self.assertFalse(result["ok"])
            codes = {e["code"] for e in result["errors"]}
            self.assertIn("prototype_confirmed_chrome_lock_drift", codes)

    def test_missing_title_ico_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth.html"
            cand = Path(tmp) / "cand.html"
            auth.write_text(AUTHORITY, encoding="utf-8")
            cand.write_text(DRIFT_MISSING_TITLE, encoding="utf-8")
            result = MOD.lint_candidate(cand, [auth])
            self.assertFalse(result["ok"])
            codes = {e["code"] for e in result["errors"]}
            self.assertIn("prototype_confirmed_chrome_lock_drift", codes)


if __name__ == "__main__":
    unittest.main()
