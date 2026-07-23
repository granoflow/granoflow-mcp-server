from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-agent-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_analysis_logic_draft import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_logic_draft_sha256,
    validate_analysis_logic_draft,
)
from lint_analysis_technical_package import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_technical_package_sha256,
    validate_analysis_technical_package,
)
from lint_responsive_prototype_bundle import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_bundle_sha256,
    validate_responsive_prototype_bundle,
)
from lint_screen_content_contract import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_content_contract_sha256,
    validate_screen_content_contract,
)


def _sha(character: str) -> str:
    return character * 64


def make_logic(*, greenfield: bool = False, no_data: bool = False) -> dict[str, Any]:
    draft: dict[str, Any] = {
        "schema": "granoflow_analysis_logic_draft_v1",
        "task_id": "task-ui-1",
        "system_type": "greenfield" if greenfield else "existing",
        "source_refs": ["project-work://requirements/R-1"],
        "existing_system_evidence": (
            [] if greenfield else ["repo://schema", "repo://api", "repo://ui"]
        ),
        "greenfield_basis": "Confirmed new product slice." if greenfield else None,
        "domain_entities": [] if no_data else [{"id": "item", "relationships": []}],
        "data_disposition": "not_applicable" if no_data else "unchanged",
        "data_disposition_basis": (
            "Static local content." if no_data else "Reads the existing item model."
        ),
        "workflows": [
            {
                "id": "open-item",
                "steps": ["open", "load", "display"],
                "failure_paths": ["load_error"],
            }
        ],
        "state_model": ["default", "loading", "empty", "error"],
        "permissions": ["signed_in_user"],
        "platform_constraints": ["mobile and desktop layouts"],
        "feasibility_findings": [],
        "open_blockers": [],
    }
    digest = canonical_logic_draft_sha256(draft)
    draft["review"] = {
        "author_id": "analysis-author",
        "reviewer_id": "engineering-reviewer",
        "status": "passed",
        "evidence_refs": ["review://logic-1"],
        "reviewed_draft_sha256": digest,
    }
    draft["status"] = "prototype_ready"
    draft["draft_sha256"] = digest
    return draft


def _states() -> list[dict[str, Any]]:
    return [
        {
            "id": state,
            "disposition": "covered",
            "behavior": f"Render the {state} presentation.",
        }
        for state in (
            "default",
            "loading",
            "empty",
            "error",
            "offline",
            "permission_denied",
        )
    ]


def make_content(
    logic: dict[str, Any],
    *,
    unattended: bool = False,
) -> dict[str, Any]:
    contract: dict[str, Any] = {
        "schema": "granoflow_screen_content_contract_v1",
        "task_id": "task-ui-1",
        "logic_draft_sha256": logic["draft_sha256"],
        "requirement_refs": ["project-work://requirements/R-1"],
        "acceptance_refs": ["project-work://acceptance/A-1"],
        "screens": [
            {
                "screen_id": "item-detail",
                "purpose": "Show an item and its primary action.",
                "user_roles": ["signed_in_user"],
                "entry_conditions": ["item id is available"],
                "interaction_mode": "interactive",
                "content_sections": [
                    {
                        "section_id": "summary",
                        "role": "primary_content",
                        "display_order": 1,
                        "data_fields": [
                            {
                                "field_id": "item.title",
                                "label": "Title",
                                "source_ref": "domain://item/title",
                                "format": "plain_text",
                                "required": True,
                                "visibility_rules": [],
                            }
                        ],
                    }
                ],
                "actions": [
                    {
                        "action_id": "save",
                        "label": "Save",
                        "preconditions": ["content is valid"],
                        "result": "Persist and show success.",
                        "failure_behavior": "Keep edits and show an error.",
                    }
                ],
                "states": _states(),
                "entry_routes": ["/items/:id"],
                "exit_routes": ["/items"],
                "back_behavior": "Return to the item list.",
                "permissions": ["signed_in_user can view and save"],
                "platform_exceptions": [],
            }
        ],
        "cross_screen_checks": {
            "data": True,
            "states": True,
            "navigation": True,
            "permissions": True,
        },
        "out_of_scope": ["item deletion"],
        "page_definition_brief_ref": "task-work://page-definition-brief",
        "page_definition_brief_sha256": _sha("b"),
        "confirmation_status": ("unattended_auto_adopted" if unattended else "user_confirmed"),
        "accepted_by": "unattended_grant" if unattended else "user",
        "authorization_effect": "none",
    }
    contract["content_contract_sha256"] = canonical_content_contract_sha256(contract)
    return contract


def make_platform() -> dict[str, Any]:
    return {
        "matrix_sha256": _sha("c"),
        "platforms": [
            {
                "id": "ios",
                "support_status": "supported",
                "layout_family_ids": ["mobile_portrait"],
            },
            {
                "id": "macos",
                "support_status": "supported",
                "layout_family_ids": ["desktop_landscape"],
            },
        ],
    }


def make_bundle(
    logic: dict[str, Any],
    content: dict[str, Any],
    platform: dict[str, Any],
    *,
    unattended: bool = False,
    schema: str = "granoflow_responsive_prototype_bundle_v2",
) -> dict[str, Any]:
    bundle: dict[str, Any] = {
        "schema": schema,
        "analysis_logic_draft_sha256": logic["draft_sha256"],
        "screen_content_contract_sha256": content["content_contract_sha256"],
        "platform_matrix_sha256": platform["matrix_sha256"],
        "baseline_package_sha256": _sha("d"),
        "widget_catalog_input_sha256": _sha("e"),
        "primary_layout_family": "mobile_portrait",
        "option_count_decision": "two",
        "option_count_reason_code": None,
        "selection_round": {
            "layout_family_id": "mobile_portrait",
            "options": [
                {
                    "id": "option-1",
                    "html_sha256": _sha("1"),
                    "contrast_axes": ["density", "navigation emphasis"],
                    "parity": {
                        "capabilities": True,
                        "data": True,
                        "states": True,
                        "behavior": True,
                    },
                },
                {
                    "id": "option-2",
                    "html_sha256": _sha("2"),
                    "contrast_axes": ["density", "navigation emphasis"],
                    "parity": {
                        "capabilities": True,
                        "data": True,
                        "states": True,
                        "behavior": True,
                    },
                },
            ],
        },
        "selected_option_id": "option-1",
        "variants": [
            {
                "layout_family_id": "mobile_portrait",
                "platform_ids": ["ios"],
                "viewport": {"width": 390, "height": 844, "dpr": 3},
                "html_ref": "prototype://mobile.html",
                "html_sha256": _sha("3"),
                "screenshot_ref": "prototype://mobile.png",
                "screenshot_sha256": _sha("4"),
            },
            {
                "layout_family_id": "desktop_landscape",
                "platform_ids": ["macos"],
                "viewport": {"width": 1440, "height": 900, "dpr": 2},
                "html_ref": "prototype://desktop.html",
                "html_sha256": _sha("5"),
                "screenshot_ref": "prototype://desktop.png",
                "screenshot_sha256": _sha("6"),
            },
        ],
        "cross_layout_checks": {
            "functional": True,
            "data": True,
            "states": True,
            "navigation": True,
            "widgets": True,
        },
        "cross_layout_consistency_status": "passed",
        "widget_promotion_ref": "task-work://widget-promotion",
        "final_acceptance_status": ("unattended_auto_adopted" if unattended else "user_confirmed"),
        "accepted_by": "unattended_grant" if unattended else "user",
        "authorization_effect": "none",
    }
    if schema.endswith("_v1"):
        bundle.pop("analysis_logic_draft_sha256")
        bundle.pop("screen_content_contract_sha256")
    bundle["bundle_sha256"] = canonical_bundle_sha256(bundle)
    return bundle


def make_technical_package(
    logic: dict[str, Any],
    content: dict[str, Any],
    platform: dict[str, Any],
    bundle: dict[str, Any],
    semantic: dict[str, Any] | None = None,
    *,
    unattended: bool = False,
    no_data: bool = False,
) -> dict[str, Any]:
    package: dict[str, Any] = {
        "schema": "granoflow_analysis_technical_package_v1",
        "logic_draft_sha256": logic["draft_sha256"],
        "content_contract_sha256": content["content_contract_sha256"],
        "platform_matrix_sha256": platform["matrix_sha256"],
        "prototype_bundle_sha256": bundle["bundle_sha256"],
        "contract_prototype_semantic_review_sha256": (
            semantic["semantic_review_sha256"] if semantic is not None else _sha("9")
        ),
        "logical_data_model": ([] if no_data else [{"entity": "item", "relationships": []}]),
        "schema_impact": {
            "disposition": "not_applicable" if no_data else "unchanged",
            "summary": "No persistent data." if no_data else "Use the existing model.",
            "existing_schema_refs": [] if no_data else ["repo://schema"],
        },
        "operation_flows": [{"id": "open-item", "ref": "task-work://flow/open-item"}],
        "state_model": [{"id": "item-view", "ref": "task-work://state/item"}],
        "permission_model": [{"role": "signed_in_user", "capabilities": ["view", "save"]}],
        "ui_data_bindings": [
            {
                "screen_id": "item-detail",
                "field_id": "item.title",
                "source_ref": "domain://item/title",
            }
        ],
        "platform_behavior": [
            {"layout_family_id": "mobile_portrait", "status": "matched"},
            {"layout_family_id": "desktop_landscape", "status": "matched"},
        ],
        "technical_risks": [],
        "reconciliation": {
            "status": "passed",
            "rows": [
                {
                    "axis": axis,
                    "status": "matched",
                    "evidence_refs": [f"reconcile://{axis}"],
                }
                for axis in (
                    "fields",
                    "actions",
                    "states",
                    "navigation",
                    "permissions",
                    "data_sources",
                )
            ],
        },
        "behavior_summary_ref": "task-work://behavior-summary",
        "behavior_summary_sha256": _sha("f"),
        "final_acceptance_status": ("unattended_auto_adopted" if unattended else "user_confirmed"),
        "accepted_by": "unattended_grant" if unattended else "user",
        "authorization_effect": "none",
    }
    digest = canonical_technical_package_sha256(package)
    package["review"] = {
        "author_id": "analysis-author",
        "reviewer_id": "engineering-reviewer",
        "status": "passed",
        "evidence_refs": ["review://technical"],
        "reviewed_technical_package_sha256": digest,
    }
    package["final_verifier"] = {
        "verifier_id": "final-verifier",
        "status": "passed",
        "evidence_refs": ["verify://technical"],
        "verified_technical_package_sha256": digest,
    }
    package["status"] = "passed"
    package["technical_package_sha256"] = digest
    return package


class AnalysisLogicDraftTest(unittest.TestCase):
    def test_existing_and_greenfield_no_data_drafts_pass(self) -> None:
        for draft in (make_logic(), make_logic(greenfield=True, no_data=True)):
            with self.subTest(system_type=draft["system_type"]):
                self.assertTrue(validate_analysis_logic_draft(draft)["ok"])

    def test_existing_system_requires_current_evidence(self) -> None:
        draft = make_logic()
        draft["existing_system_evidence"] = []
        draft["draft_sha256"] = canonical_logic_draft_sha256(draft)
        draft["review"]["reviewed_draft_sha256"] = draft["draft_sha256"]
        self.assertFalse(validate_analysis_logic_draft(draft)["ok"])

    def test_open_blocker_and_failed_independence_block(self) -> None:
        draft = make_logic()
        draft["open_blockers"] = ["Permission source is unknown."]
        draft["draft_sha256"] = canonical_logic_draft_sha256(draft)
        draft["review"]["reviewed_draft_sha256"] = draft["draft_sha256"]
        draft["review"]["reviewer_id"] = draft["review"]["author_id"]
        result = validate_analysis_logic_draft(draft)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("analysis_logic_draft_blocking_findings", codes)
        self.assertIn("analysis_logic_draft_review_failed", codes)

    def test_logic_change_invalidates_digest_and_review(self) -> None:
        draft = make_logic()
        draft["permissions"].append("administrator")
        result = validate_analysis_logic_draft(draft)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "analysis_logic_draft_digest_mismatch"
                for error in result["errors"]
            )
        )


class ScreenContentContractTest(unittest.TestCase):
    def test_user_and_unattended_content_acceptance_pass(self) -> None:
        logic = make_logic()
        for unattended in (False, True):
            with self.subTest(unattended=unattended):
                contract = make_content(logic, unattended=unattended)
                result = validate_screen_content_contract(contract, logic)
                self.assertTrue(result["ok"])
                self.assertEqual(contract["authorization_effect"], "none")

    def test_missing_field_state_permission_and_navigation_block(self) -> None:
        logic = make_logic()
        contract = make_content(logic)
        screen = contract["screens"][0]
        screen["content_sections"][0]["data_fields"] = []
        screen["states"] = [row for row in screen["states"] if row["id"] != "permission_denied"]
        screen["permissions"] = []
        screen["entry_routes"] = []
        contract["content_contract_sha256"] = canonical_content_contract_sha256(contract)
        result = validate_screen_content_contract(contract, logic)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("screen_content_contract_incomplete", codes)
        self.assertIn("screen_content_contract_state_missing", codes)

    def test_content_change_invalidates_digest(self) -> None:
        logic = make_logic()
        contract = make_content(logic)
        contract["screens"][0]["actions"][0]["result"] = "Navigate to the list."
        result = validate_screen_content_contract(contract, logic)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "screen_content_contract_digest_mismatch"
                for error in result["errors"]
            )
        )


class AnalysisFinalizationIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.logic = make_logic()
        self.content = make_content(self.logic)
        self.platform = make_platform()
        self.bundle = make_bundle(self.logic, self.content, self.platform)

    def test_bundle_v2_binds_logic_and_content(self) -> None:
        result = validate_responsive_prototype_bundle(
            self.bundle,
            self.platform,
            self.content,
            self.logic,
        )
        self.assertTrue(result["ok"])

    def test_active_v1_requires_upgrade_but_historical_is_readable(self) -> None:
        legacy = make_bundle(
            self.logic,
            self.content,
            self.platform,
            schema="granoflow_responsive_prototype_bundle_v1",
        )
        active = validate_responsive_prototype_bundle(legacy, self.platform)
        historical = validate_responsive_prototype_bundle(
            legacy,
            self.platform,
            lifecycle="historical_read_only",
        )
        self.assertFalse(active["ok"])
        self.assertEqual(active["code"], "responsive_prototype_bundle_upgrade_required")
        self.assertTrue(historical["ok"])

    def test_content_change_invalidates_bundle_and_technical_package(self) -> None:
        package = make_technical_package(self.logic, self.content, self.platform, self.bundle)
        changed = copy.deepcopy(self.content)
        changed["screens"][0]["purpose"] = "Show and edit an item."
        changed["content_contract_sha256"] = canonical_content_contract_sha256(changed)
        bundle_result = validate_responsive_prototype_bundle(
            self.bundle,
            self.platform,
            changed,
            self.logic,
        )
        package_result = validate_analysis_technical_package(
            package,
            self.logic,
            changed,
            self.platform,
            self.bundle,
        )
        self.assertFalse(bundle_result["ok"])
        self.assertFalse(package_result["ok"])

    def test_technical_package_passes_for_user_unattended_and_no_data(self) -> None:
        package = make_technical_package(self.logic, self.content, self.platform, self.bundle)
        self.assertTrue(
            validate_analysis_technical_package(
                package,
                self.logic,
                self.content,
                self.platform,
                self.bundle,
            )["ok"]
        )

        logic = make_logic(greenfield=True, no_data=True)
        content = make_content(logic, unattended=True)
        bundle = make_bundle(logic, content, self.platform, unattended=True)
        package = make_technical_package(
            logic,
            content,
            self.platform,
            bundle,
            unattended=True,
            no_data=True,
        )
        result = validate_analysis_technical_package(package, logic, content, self.platform, bundle)
        self.assertTrue(result["ok"])
        self.assertEqual(package["authorization_effect"], "none")

    def test_physical_design_is_forbidden_in_analysis(self) -> None:
        package = make_technical_package(self.logic, self.content, self.platform, self.bundle)
        package["schema_impact"]["tables"] = [{"name": "items"}]
        digest = canonical_technical_package_sha256(package)
        package["technical_package_sha256"] = digest
        package["review"]["reviewed_technical_package_sha256"] = digest
        package["final_verifier"]["verified_technical_package_sha256"] = digest
        result = validate_analysis_technical_package(package)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "analysis_technical_package_physical_design_forbidden")

    def test_missing_reconciliation_review_or_verifier_blocks(self) -> None:
        package = make_technical_package(self.logic, self.content, self.platform, self.bundle)
        package["reconciliation"]["rows"].pop()
        digest = canonical_technical_package_sha256(package)
        package["technical_package_sha256"] = digest
        package["review"]["reviewed_technical_package_sha256"] = digest
        package["review"]["status"] = "failed"
        package["final_verifier"]["verified_technical_package_sha256"] = digest
        package["final_verifier"]["verifier_id"] = package["review"]["reviewer_id"]
        result = validate_analysis_technical_package(package)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("analysis_technical_package_reconciliation_failed", codes)
        self.assertIn("analysis_technical_package_review_failed", codes)
        self.assertIn("analysis_technical_package_verifier_failed", codes)

    def test_bundle_change_invalidates_technical_digest_binding(self) -> None:
        package = make_technical_package(self.logic, self.content, self.platform, self.bundle)
        changed_bundle = copy.deepcopy(self.bundle)
        changed_bundle["variants"][0]["viewport"]["width"] = 430
        changed_bundle["bundle_sha256"] = canonical_bundle_sha256(changed_bundle)
        result = validate_analysis_technical_package(
            package,
            self.logic,
            self.content,
            self.platform,
            changed_bundle,
        )
        self.assertFalse(result["ok"])

    def test_acceptance_must_match_bundle_and_grant_no_authority(self) -> None:
        package = make_technical_package(self.logic, self.content, self.platform, self.bundle)
        package["accepted_by"] = "unattended_grant"
        package["authorization_effect"] = "execution_authorization"
        result = validate_analysis_technical_package(
            package,
            self.logic,
            self.content,
            self.platform,
            self.bundle,
        )
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "analysis_behavior_acceptance_required"
                for error in result["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
