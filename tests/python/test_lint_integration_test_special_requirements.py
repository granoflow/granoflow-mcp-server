#!/usr/bin/env python3
"""Tests for lint_integration_test_special_requirements.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "skills"
    / "granoflow-agent-workflow"
    / "scripts"
    / "lint_integration_test_special_requirements.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "lint_integration_test_special_requirements", SCRIPT
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_module()


class LintSpecialRequirementsTests(unittest.TestCase):
    def test_empty_list_ok(self) -> None:
        result = MOD.lint_special_requirements(
            {"engineering": {"quality_gates": {"integration_test_special_requirements": []}}}
        )
        self.assertTrue(result["ok"], result)

    def test_missing_field_ok(self) -> None:
        result = MOD.lint_special_requirements({"engineering": {"quality_gates": {}}})
        self.assertTrue(result["ok"], result)

    def test_seed_corpus_ok(self) -> None:
        result = MOD.lint_special_requirements(
            {
                "engineering": {
                    "quality_gates": {
                        "integration_test_special_requirements": [
                            {
                                "id": "ITR-001",
                                "kind": "seed_corpus",
                                "statement": "five Standard Ebooks for multi-book IT",
                                "corpus_paths": [
                                    "docs/mary-shelley_frankenstein.epub",
                                    "docs/jane-austen_pride-and-prejudice.epub",
                                ],
                                "not_app_seed": True,
                                "app_seed_paths": ["assets/sample/welcome.epub"],
                                "forbidden_substitutes": [
                                    "randomly_generated_fake_epub_as_primary_corpus"
                                ],
                                "applies_when": [
                                    "multi_book_library_it",
                                    "folder_import_it",
                                    "campaign_suite",
                                ],
                                "product_doc_refs": ["docs/11-product-V02.md §9.7"],
                                "provenance": "user_stated",
                                "enforcement": "fail_closed",
                            }
                        ]
                    }
                }
            }
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["count"], 1)

    def test_seed_corpus_missing_paths_fails(self) -> None:
        result = MOD.lint_special_requirements(
            {
                "engineering": {
                    "quality_gates": {
                        "integration_test_special_requirements": [
                            {
                                "id": "ITR-001",
                                "kind": "seed_corpus",
                                "statement": "missing corpus",
                                "corpus_paths": [],
                                "applies_when": ["campaign_suite"],
                                "enforcement": "fail_closed",
                            }
                        ]
                    }
                }
            }
        )
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
