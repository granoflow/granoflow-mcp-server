#!/usr/bin/env python3
"""Tests for lint_prototype_link_ledger.py."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_prototype_link_ledger.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_prototype_link_ledger", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _write_html(directory: Path, name: str = "index.html", body: str = "<html></html>") -> Path:
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path.resolve()


def ok_entry(html_path: Path, **overrides: Any) -> dict[str, Any]:
    file_url = MOD.path_to_file_url(html_path)
    entry: dict[str, Any] = {
        "title": "Open library · mobile",
        "absolute_path": str(html_path),
        "file_url": file_url,
        "entity": "task:T2",
        "sha_or_pending": "pending",
    }
    entry.update(overrides)
    return entry


def ok_ledger(html_path: Path, **overrides: Any) -> dict[str, Any]:
    entry = ok_entry(html_path)
    file_url = entry["file_url"]
    block: dict[str, Any] = {
        "schema": "granoflow_prototype_link_ledger_v1",
        "contract_loaded": True,
        "status": "complete",
        "chat_digest_emitted": True,
        "markdown_digest": ("## Prototype Link Digest\n\n" f"- [{entry['title']}]({file_url})\n"),
        "entries": [entry],
    }
    block.update(overrides)
    return {"prototype_link_ledger": block}


class LintPrototypeLinkLedgerTests(unittest.TestCase):
    def test_complete_ledger_with_existing_html_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = _write_html(Path(tmp))
            result = MOD.lint_prototype_link_ledger(ok_ledger(html), require_complete=True)
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["code"], "ok")

    def test_missing_file_fails(self) -> None:
        missing = Path("/tmp/granoflow-missing-prototype-link-ledger.html")
        if missing.exists():
            missing.unlink()
        result = MOD.lint_prototype_link_ledger(ok_ledger(missing))
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "prototype_link_file_missing")

    def test_relative_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = _write_html(Path(tmp))
            ledger = ok_ledger(
                html,
                entries=[
                    ok_entry(
                        html,
                        absolute_path="temp/m1-t2-prototype/index.html",
                        file_url="file://temp/m1-t2-prototype/index.html",
                    )
                ],
            )
            result = MOD.lint_prototype_link_ledger(ledger)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_link_not_absolute")

    def test_digest_missing_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = _write_html(Path(tmp))
            ledger = ok_ledger(
                html,
                markdown_digest="## Prototype Link Digest\n\n(no links)\n",
            )
            result = MOD.lint_prototype_link_ledger(ledger)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_link_digest_required")

    def test_chat_digest_not_emitted_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = _write_html(Path(tmp))
            ledger = ok_ledger(html, chat_digest_emitted=False)
            result = MOD.lint_prototype_link_ledger(ledger)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_link_digest_required")

    def test_require_complete_rejects_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html = _write_html(Path(tmp))
            ledger = ok_ledger(html, status="pending")
            result = MOD.lint_prototype_link_ledger(ledger, require_complete=True)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_link_ledger_incomplete")

    def test_not_applicable_passes_require_complete(self) -> None:
        data = {
            "prototype_link_ledger": {
                "schema": "granoflow_prototype_link_ledger_v1",
                "contract_loaded": True,
                "status": "not_applicable",
                "entries": [],
            }
        }
        result = MOD.lint_prototype_link_ledger(data, require_complete=True)
        self.assertTrue(result["ok"], result)

    def test_bare_list_rejected(self) -> None:
        result = MOD.lint_prototype_link_ledger({"prototype_link_ledger": [{"title": "x"}]})
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "prototype_link_ledger_lint_failed")

    def test_html_coverage_cross_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            html = _write_html(root, "mobile_portrait.html")
            _write_html(root, "desktop_landscape.html")
            ledger = ok_ledger(
                html,
                entries=[ok_entry(html, title="mobile")],
                markdown_digest=(
                    "## Prototype Link Digest\n\n" f"- [mobile]({MOD.path_to_file_url(html)})\n"
                ),
            )
            coverage = {
                "prototype_html_coverage": {
                    "schema": "granoflow_prototype_html_coverage_v1",
                    "contract_loaded": True,
                    "prototype_id": "p1",
                    "status": "complete",
                    "surfaces": [
                        {
                            "surface_id": "S-open",
                            "kind": "page",
                            "label": "Open",
                            "html_prototype_ref": "mobile_portrait.html",
                            "coverage": "covered",
                        },
                        {
                            "surface_id": "S-open-desktop",
                            "kind": "page",
                            "label": "Open desktop",
                            "html_prototype_ref": "desktop_landscape.html",
                            "coverage": "covered",
                        },
                    ],
                }
            }
            result = MOD.lint_prototype_link_ledger(
                ledger,
                require_complete=True,
                html_coverage=coverage,
                prototype_root=root,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "prototype_link_ledger_incomplete")
            codes = {e["code"] for e in result["errors"]}
            self.assertIn("prototype_link_ledger_incomplete", codes)

    def test_cli_ok_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            html = _write_html(root)
            ledger_path = root / "ledger.json"
            import json

            ledger_path.write_text(
                json.dumps(ok_ledger(html), ensure_ascii=False),
                encoding="utf-8",
            )
            code = MOD.main([str(ledger_path), "--require-complete"])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
