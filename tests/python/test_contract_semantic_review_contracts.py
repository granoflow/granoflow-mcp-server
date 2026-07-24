from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

AGENT_SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-agent-workflow" / "scripts"
sys.path.insert(0, str(AGENT_SCRIPTS))
sys.path.insert(0, str(Path(__file__).parent))

from lint_analysis_technical_package import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    validate_analysis_technical_package,
)
from lint_contract_grill import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    REQUIRED_AXES,
    canonical_contract_grill_sha256,
    validate_contract_grill,
)
from lint_contract_prototype_semantics import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_semantic_review_sha256,
    validate_contract_prototype_semantics,
)
from lint_requirement_contract_traceability import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_traceability_sha256,
    contract_element_refs,
    validate_requirement_contract_traceability,
)
from test_task_analysis_finalization_contracts import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    make_bundle,
    make_content,
    make_logic,
    make_platform,
    make_technical_package,
)


def _sha(character: str) -> str:
    return character * 64


def make_traceability(content: dict[str, Any]) -> dict[str, Any]:
    elements = sorted(contract_element_refs(content))
    ledger: dict[str, Any] = {
        "schema": "granoflow_requirement_contract_traceability_v1",
        "content_contract_sha256": content["content_contract_sha256"],
        "rows": [
            {
                "source_kind": "requirement",
                "source_ref": content["requirement_refs"][0],
                "contract_element_refs": elements,
                "status": "covered",
            },
            {
                "source_kind": "acceptance",
                "source_ref": content["acceptance_refs"][0],
                "contract_element_refs": [elements[0]],
                "status": "covered",
            },
        ],
    }
    digest = canonical_traceability_sha256(ledger)
    ledger["review"] = {
        "author_id": "analysis-author",
        "reviewer_id": "product-reviewer",
        "status": "passed",
        "evidence_refs": ["review://requirement-coverage"],
        "reviewed_traceability_sha256": digest,
    }
    ledger["status"] = "passed"
    ledger["traceability_sha256"] = digest
    return ledger


def make_grill(
    content: dict[str, Any],
    traceability: dict[str, Any],
    *,
    unattended: bool = False,
) -> dict[str, Any]:
    mode = "unattended" if unattended else "interactive"
    grill: dict[str, Any] = {
        "schema": "granoflow_contract_grill_v1",
        "content_contract_sha256": content["content_contract_sha256"],
        "traceability_sha256": traceability["traceability_sha256"],
        "mode": mode,
        "questions": [
            {
                "id": f"grill-{axis}",
                "axis": axis,
                "question": f"Is {axis} complete and evidence-backed?",
                "recommendation": "Keep the current contract mapping.",
                "rationale": "The traceability evidence closes this axis.",
                "disposition": "accepted",
                "answer_source": "unattended_grant" if unattended else "user",
                "evidence_refs": [f"grill://{axis}"],
                "blocking": False,
            }
            for axis in sorted(REQUIRED_AXES)
        ],
        "coverage_axes": {axis: True for axis in REQUIRED_AXES},
        "open_blockers": [],
        "authorization_effect": "none",
    }
    grill["grill_sha256"] = canonical_contract_grill_sha256(grill)
    grill["status"] = "passed"
    return grill


def make_semantic_review(
    content: dict[str, Any],
    traceability: dict[str, Any],
    bundle: dict[str, Any],
) -> dict[str, Any]:
    elements = sorted(contract_element_refs(content))
    layouts = sorted(
        {
            row["layout_family_id"]
            for row in bundle["variants"]
            if isinstance(row.get("layout_family_id"), str)
        }
    )
    rows = []
    for element in elements:
        for layout in layouts:
            row: dict[str, Any] = {
                "contract_element_ref": element,
                "layout_family_id": layout,
                "dom_ref": f'[data-contract-ref="{element}"]',
                "html_ref": f"prototype://{layout}.html",
                "html_sha256": _sha("a"),
                "screenshot_ref": f"prototype://{layout}/{element}.png",
                "screenshot_sha256": _sha("b"),
                "interaction_evidence_ref": None,
                "state_capture_ref": None,
                "status": "verified",
            }
            if element.startswith(("action:", "navigation:")):
                row["interaction_evidence_ref"] = f"browser://{layout}/interaction/{element}"
            if element.startswith(("state:", "permission:")):
                row["state_capture_ref"] = f"browser://{layout}/state/{element}"
            rows.append(row)
    semantic: dict[str, Any] = {
        "schema": "granoflow_contract_prototype_semantic_review_v1",
        "content_contract_sha256": content["content_contract_sha256"],
        "traceability_sha256": traceability["traceability_sha256"],
        "prototype_bundle_sha256": bundle["bundle_sha256"],
        "required_layout_family_ids": layouts,
        "rows": rows,
        "deterministic_browser": {
            "status": "passed",
            "evidence_refs": ["browser://run/semantic-review"],
        },
        "open_blockers": [],
        "authorization_effect": "none",
    }
    digest = canonical_semantic_review_sha256(semantic)
    semantic["ai_semantic_review"] = {
        "reviewer_id": "semantic-reviewer",
        "status": "passed",
        "evidence_refs": ["review://semantic"],
        "reviewed_semantic_sha256": digest,
    }
    semantic["visual_quality_review"] = {
        "provider": "native_visual_review",
        "mode": "review_only",
        "mutation_authorization": "none",
        "status": "passed",
        "evidence_refs": ["review://visual-quality"],
    }
    semantic["final_verifier"] = {
        "verifier_id": "semantic-final-verifier",
        "status": "passed",
        "evidence_refs": ["verify://semantic"],
        "verified_semantic_sha256": digest,
    }
    semantic["status"] = "passed"
    semantic["semantic_review_sha256"] = digest
    return semantic


class RequirementTraceabilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.logic = make_logic()
        self.content = make_content(self.logic)
        self.ledger = make_traceability(self.content)

    def test_bidirectional_traceability_passes(self) -> None:
        result = validate_requirement_contract_traceability(self.ledger, self.content)
        self.assertTrue(result["ok"])
        self.assertGreater(len(result["contract_element_refs"]), 10)

    def test_unmapped_requirement_and_contract_element_block(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["rows"] = ledger["rows"][1:]
        ledger["rows"][0]["contract_element_refs"] = [ledger["rows"][0]["contract_element_refs"][0]]
        digest = canonical_traceability_sha256(ledger)
        ledger["traceability_sha256"] = digest
        ledger["review"]["reviewed_traceability_sha256"] = digest
        result = validate_requirement_contract_traceability(ledger, self.content)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("requirement_contract_unmapped", codes)
        self.assertIn("contract_element_without_product_basis", codes)

    def test_stale_digest_or_non_independent_review_blocks(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["review"]["reviewer_id"] = ledger["review"]["author_id"]
        ledger["rows"][0]["source_ref"] = "requirement://changed"
        result = validate_requirement_contract_traceability(ledger, self.content)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("requirement_contract_review_failed", codes)
        self.assertIn("requirement_contract_traceability_digest_mismatch", codes)


class ContractGrillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.logic = make_logic()
        self.content = make_content(self.logic)
        self.traceability = make_traceability(self.content)

    def test_interactive_and_unattended_grills_pass(self) -> None:
        for unattended in (False, True):
            with self.subTest(unattended=unattended):
                grill = make_grill(self.content, self.traceability, unattended=unattended)
                self.assertTrue(
                    validate_contract_grill(grill, self.content, self.traceability)["ok"]
                )
                self.assertEqual(grill["authorization_effect"], "none")

    def test_missing_axis_and_open_blocker_fail(self) -> None:
        grill = make_grill(self.content, self.traceability)
        grill["questions"].pop()
        grill["coverage_axes"]["states"] = False
        grill["open_blockers"] = ["Empty state behavior is unresolved."]
        grill["grill_sha256"] = canonical_contract_grill_sha256(grill)
        result = validate_contract_grill(grill, self.content, self.traceability)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("contract_grill_coverage_incomplete", codes)
        self.assertIn("contract_grill_open_questions", codes)

    def test_background_control_gaps_have_specific_plain_failures(self) -> None:
        grill = make_grill(self.content, self.traceability)
        grill["questions"] = [
            row
            for row in grill["questions"]
            if row["axis"] not in {"background_activity_control", "post_update_user_control"}
        ]
        grill["coverage_axes"]["background_activity_control"] = False
        grill["coverage_axes"]["post_update_user_control"] = False
        grill["grill_sha256"] = canonical_contract_grill_sha256(grill)
        result = validate_contract_grill(grill, self.content, self.traceability)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("background_state_write_scope_missing", codes)
        self.assertIn("post_update_interaction_test_missing", codes)

    def test_human_path_gaps_have_specific_plain_failures(self) -> None:
        grill = make_grill(self.content, self.traceability)
        grill["questions"] = [
            row
            for row in grill["questions"]
            if row["axis"] not in {"human_path_continuity", "shortcut_non_interference"}
        ]
        grill["coverage_axes"]["human_path_continuity"] = False
        grill["coverage_axes"]["shortcut_non_interference"] = False
        grill["grill_sha256"] = canonical_contract_grill_sha256(grill)
        result = validate_contract_grill(grill, self.content, self.traceability)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("e2e_campaign_human_interaction_evidence_missing", codes)
        self.assertIn("e2e_campaign_shortcut_overclaim", codes)

    def test_wrong_answer_source_and_authorization_fail(self) -> None:
        grill = make_grill(self.content, self.traceability, unattended=True)
        grill["questions"][0]["answer_source"] = "user"
        grill["authorization_effect"] = "execution_authorization"
        grill["grill_sha256"] = canonical_contract_grill_sha256(grill)
        self.assertFalse(validate_contract_grill(grill, self.content, self.traceability)["ok"])


class ContractPrototypeSemanticReviewTest(unittest.TestCase):
    def setUp(self) -> None:
        self.logic = make_logic()
        self.content = make_content(self.logic)
        self.platform = make_platform()
        self.bundle = make_bundle(self.logic, self.content, self.platform)
        self.traceability = make_traceability(self.content)
        self.semantic = make_semantic_review(self.content, self.traceability, self.bundle)

    def test_all_contract_layout_pairs_pass(self) -> None:
        result = validate_contract_prototype_semantics(
            self.semantic,
            self.content,
            self.traceability,
            self.bundle,
        )
        self.assertTrue(result["ok"])
        self.assertGreater(result["required_pair_count"], 20)

    def test_real_html_markers_are_checked_per_layout(self) -> None:
        elements = sorted(contract_element_refs(self.content))
        html = "".join(f'<div data-contract-ref="{element}"></div>' for element in elements)
        with tempfile.TemporaryDirectory() as directory:
            paths: dict[str, Path] = {}
            for layout in self.semantic["required_layout_family_ids"]:
                path = Path(directory) / f"{layout}.html"
                path.write_text(html, encoding="utf-8")
                paths[layout] = path
            self.assertTrue(
                validate_contract_prototype_semantics(
                    self.semantic,
                    self.content,
                    self.traceability,
                    self.bundle,
                    paths,
                )["ok"]
            )
            paths["mobile_portrait"].write_text(
                '<div data-contract-ref="screen:item-detail"></div>',
                encoding="utf-8",
            )
            result = validate_contract_prototype_semantics(
                self.semantic,
                self.content,
                self.traceability,
                self.bundle,
                paths,
            )
            self.assertFalse(result["ok"])
            self.assertTrue(
                any(error["code"] == "contract_element_unrendered" for error in result["errors"])
            )

    def test_missing_pair_interaction_and_state_evidence_block(self) -> None:
        semantic = copy.deepcopy(self.semantic)
        semantic["rows"].pop()
        action = next(
            row for row in semantic["rows"] if row["contract_element_ref"].startswith("action:")
        )
        state = next(
            row for row in semantic["rows"] if row["contract_element_ref"].startswith("state:")
        )
        action["interaction_evidence_ref"] = None
        state["state_capture_ref"] = None
        digest = canonical_semantic_review_sha256(semantic)
        semantic["semantic_review_sha256"] = digest
        semantic["ai_semantic_review"]["reviewed_semantic_sha256"] = digest
        semantic["final_verifier"]["verified_semantic_sha256"] = digest
        result = validate_contract_prototype_semantics(
            semantic, self.content, self.traceability, self.bundle
        )
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("contract_prototype_layout_coverage_missing", codes)
        self.assertIn("prototype_interaction_unverified", codes)
        self.assertIn("contract_state_uncaptured", codes)

    def test_browser_ai_visual_and_verifier_fail_closed(self) -> None:
        semantic = copy.deepcopy(self.semantic)
        semantic["deterministic_browser"]["status"] = "failed"
        semantic["ai_semantic_review"]["status"] = "failed"
        semantic["visual_quality_review"]["mode"] = "fix_and_commit"
        semantic["visual_quality_review"]["mutation_authorization"] = "granted"
        semantic["final_verifier"]["verifier_id"] = semantic["ai_semantic_review"]["reviewer_id"]
        result = validate_contract_prototype_semantics(
            semantic, self.content, self.traceability, self.bundle
        )
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("prototype_interaction_unverified", codes)
        self.assertIn("semantic_reviewer_failed", codes)
        self.assertIn("visual_quality_reviewer_failed", codes)
        self.assertIn("semantic_verifier_failed", codes)

    def test_content_or_bundle_change_invalidates_semantic_review(self) -> None:
        changed_content = copy.deepcopy(self.content)
        changed_content["content_contract_sha256"] = _sha("c")
        changed_bundle = copy.deepcopy(self.bundle)
        changed_bundle["bundle_sha256"] = _sha("d")
        result = validate_contract_prototype_semantics(
            self.semantic,
            changed_content,
            self.traceability,
            changed_bundle,
        )
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "contract_prototype_semantic_digest_mismatch"
                for error in result["errors"]
            )
        )

    def test_technical_package_binds_semantic_review_digest(self) -> None:
        package = make_technical_package(
            self.logic,
            self.content,
            self.platform,
            self.bundle,
            self.semantic,
        )
        self.assertTrue(
            validate_analysis_technical_package(
                package,
                self.logic,
                self.content,
                self.platform,
                self.bundle,
                self.semantic,
            )["ok"]
        )
        changed = copy.deepcopy(self.semantic)
        changed["semantic_review_sha256"] = _sha("e")
        self.assertFalse(
            validate_analysis_technical_package(
                package,
                self.logic,
                self.content,
                self.platform,
                self.bundle,
                changed,
            )["ok"]
        )


if __name__ == "__main__":
    unittest.main()
