#!/usr/bin/env python3
"""Tests for lint_parallel_batch_merge_review.py (schema / I/O, not prose)."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT / "skills" / "granoflow-agent-workflow" / "scripts" / "lint_parallel_batch_merge_review.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("lint_parallel_batch_merge_review", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


def _base(**overrides: object) -> dict:
    data: dict = {
        "doc_type": "parallel_batch_merge_review",
        "schema": "granoflow_parallel_batch_merge_review_v1",
        "batch_id": "batch-1",
        "milestone_id": "M1",
        "project_id": "proj-1",
        "version": 1,
        "status": "draft",
        "interaction_mode": "interactive",
        "host_isolation": "same_tree_disjoint",
        "workers": [
            {
                "task_id": "t1",
                "write_surfaces": ["src/a.ts"],
                "delivery_ref": "",
                "exit_ok": False,
                "diff_ref": None,
            }
        ],
        "pairwise_recheck": "pending",
        "post_merge_gates": [],
        "decision_authority": None,
        "accepted_at": "",
        "html_render": {
            "status": "skipped_markdown_only",
            "html_path": None,
            "html_file_url": None,
            "markdown_path": "/tmp/pack.md",
            "markdown_file_url": "",
            "link_emitted": False,
        },
    }
    data.update(overrides)
    return data


def _write_json(data: dict) -> Path:
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    )
    json.dump(data, tmp)
    tmp.close()
    return Path(tmp.name)


class LintParallelBatchMergeReviewTests(unittest.TestCase):
    def test_draft_ok(self) -> None:
        path = _write_json(_base())
        try:
            result = MOD.lint_parallel_batch_merge_review(path)
            self.assertTrue(result["ok"], result)
        finally:
            path.unlink(missing_ok=True)

    def test_empty_workers_fails(self) -> None:
        path = _write_json(_base(workers=[]))
        try:
            result = MOD.lint_parallel_batch_merge_review(path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "parallel_batch_merge_review_incomplete")
        finally:
            path.unlink(missing_ok=True)

    def test_closeout_requires_delivery_and_recheck(self) -> None:
        path = _write_json(_base(status="pending_acceptance"))
        try:
            result = MOD.lint_parallel_batch_merge_review(path)
            self.assertFalse(result["ok"])
            details = " ".join(e["detail"] for e in result["errors"])
            self.assertIn("pairwise_recheck", details)
            self.assertIn("delivery_ref", details)
        finally:
            path.unlink(missing_ok=True)

    def test_accepted_interactive(self) -> None:
        path = _write_json(
            _base(
                status="accepted",
                pairwise_recheck="parallel_safe",
                decision_authority="user_explicit",
                workers=[
                    {
                        "task_id": "t1",
                        "write_surfaces": ["src/a.ts"],
                        "delivery_ref": "delivery-t1",
                        "exit_ok": True,
                        "diff_ref": None,
                    }
                ],
                html_render={
                    "status": "skipped_markdown_only",
                    "html_path": None,
                    "html_file_url": None,
                    "markdown_path": "/tmp/pack.md",
                    "markdown_file_url": "file:///tmp/pack.md",
                    "link_emitted": True,
                },
            )
        )
        try:
            result = MOD.lint_parallel_batch_merge_review(path)
            self.assertTrue(result["ok"], result)
        finally:
            path.unlink(missing_ok=True)

    def test_conflict_blocks_accepted(self) -> None:
        path = _write_json(
            _base(
                status="accepted",
                pairwise_recheck="conflict",
                decision_authority="user_explicit",
                workers=[
                    {
                        "task_id": "t1",
                        "write_surfaces": ["src/a.ts"],
                        "delivery_ref": "delivery-t1",
                        "exit_ok": True,
                        "diff_ref": None,
                    }
                ],
                html_render={
                    "status": "skipped_markdown_only",
                    "html_path": None,
                    "html_file_url": None,
                    "markdown_path": "/tmp/pack.md",
                    "markdown_file_url": "file:///tmp/pack.md",
                    "link_emitted": True,
                },
            )
        )
        try:
            result = MOD.lint_parallel_batch_merge_review(path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["code"], "parallel_batch_merge_review_unaccepted")
        finally:
            path.unlink(missing_ok=True)

    def test_cli_json(self) -> None:
        import subprocess

        path = _write_json(_base())
        try:
            proc = subprocess.run(
                ["python3", str(SCRIPT), str(path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
