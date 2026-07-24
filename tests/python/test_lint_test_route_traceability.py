from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-agent-workflow" / "scripts"
GRANOREADER_FIXTURE = (
    Path(__file__).parents[2] / "tests/python/fixtures/granoreader_requirement_integrity.json"
)
sys.path.insert(0, str(SCRIPTS))

from lint_test_route_traceability import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_test_route_traceability_sha256,
    validate_test_route_traceability,
)


def project_work(
    *,
    boundary: bool = True,
    background_activity: bool = False,
) -> dict[str, Any]:
    step: dict[str, Any] = {
        "step_id": "J-import-picker",
        "sequence": 1,
        "step_type": "action",
        "control": "bookshelf plus button",
        "actor": "user",
        "action": "opens the native folder picker",
        "interaction_surface": "os_chrome" if boundary else "in_app_ui",
        "platform_boundary": "plugin" if boundary else "none",
        "expected_observation": "folder picker is visible",
        "source_fact_ids": ["F-plus-picker"],
        "required_test_layers": ["unit", "e2e"] if boundary else ["e2e"],
    }
    if boundary:
        step["failure_modes"] = ["missing_plugin", "cancel"]
    work = {
        "product_spec_coverage": {
            "source_fact_ledger": {
                "schema": "granoflow_source_fact_ledger_v1",
                "ledger_sha256": "b" * 64,
            },
            "journey_step_traceability": {
                "schema": "granoflow_journey_step_traceability_v1",
                "traceability_sha256": "a" * 64,
                "journeys": [{"journey_id": "J-import", "steps": [step]}],
            },
        }
    }
    if background_activity:
        step["required_test_layers"] = ["integration", "e2e"]
        work["product_spec_coverage"]["background_activity_control"] = {
            "schema": "granoflow_background_activity_control_v1",
            "control_sha256": "c" * 64,
            "activities": [
                {
                    "activity_id": "BA-refresh",
                    "source_fact_ids": ["F-plus-picker"],
                    "journey_step_ids": ["J-import-picker"],
                    "continues_after_user_action": True,
                    "user_visible": True,
                    "background_events": ["progress update"],
                    "allowed_background_changes": ["progress"],
                    "must_not_change": ["active panel"],
                    "controls_that_must_keep_working": ["settings panel"],
                    "ways_to_exit": ["cancel"],
                    "required_test_layers": ["integration", "e2e"],
                }
            ],
        }
    return work


def _post_update_sequence() -> dict[str, Any]:
    return {
        "activity_started": "state://activity-running",
        "first_background_event": {
            "signal": "progress changed to 10",
            "evidence_kind": "state_change",
            "evidence_ref": "state://progress-10",
        },
        "protected_user_action": {
            "control_ref": "settings panel",
            "evidence_ref": "ui://settings-opened",
        },
        "second_background_event": {
            "signal": "progress changed to 20",
            "evidence_kind": "state_change",
            "evidence_ref": "state://progress-20",
        },
        "user_action_preserved": "ui://settings-still-open",
        "exit_action": "cancel",
        "activity_ended": "state://activity-stopped",
    }


def _human_interactions(*, boundary: bool) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "J-import-picker",
            "navigation_method": "os_control" if boundary else "visible_control",
            "control_ref": "bookshelf plus button",
            "action": "system_interaction" if boundary else "click",
            "before_observation": "bookshelf is visible",
            "after_observation": "folder picker is visible",
            "evidence_kind": "host_event" if boundary else "driver_event",
            "evidence_ref": "host://picker-open" if boundary else "driver://plus-click",
        }
    ]


def route_ledger(
    *,
    boundary: bool = True,
    background_activity: bool = False,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if boundary:
        rows.append(
            {
                "route_id": "TR-import-unit",
                "journey_id": "J-import",
                "step_ids": ["J-import-picker"],
                "source_fact_ids": ["F-plus-picker"],
                "requirement_refs": ["R-import"],
                "acceptance_refs": ["A-import"],
                "test_layer": "unit",
                "path_kind": "service_path",
                "test_path": "test/import_source_picker_test.dart",
                "assertions": ["missing plugin falls back", "cancel leaves shelf unchanged"],
                "evidence_refs": ["test://import-source-picker"],
                "doubles_policy": "allowed",
                "covered_failure_modes": ["missing_plugin", "cancel"],
                "status": "covered",
            }
        )
    if background_activity:
        rows.append(
            {
                "route_id": "TR-refresh-integration",
                "journey_id": "J-import",
                "step_ids": ["J-import-picker"],
                "source_fact_ids": ["F-plus-picker"],
                "requirement_refs": ["R-import"],
                "acceptance_refs": ["A-import"],
                "test_layer": "integration",
                "path_kind": "component_path",
                "test_path": "test/refreshing_view_test.dart",
                "assertions": ["settings remains open across updates"],
                "evidence_refs": ["test://refreshing-view"],
                "doubles_policy": "allowed",
                "background_activity_id": "BA-refresh",
                "post_update_sequence": _post_update_sequence(),
                "status": "covered",
            }
        )
    rows.append(
        {
            "route_id": "TR-import-e2e",
            "journey_id": "J-import",
            "step_ids": ["J-import-picker"],
            "source_fact_ids": ["F-plus-picker"],
            "requirement_refs": ["R-import"],
            "acceptance_refs": ["A-import"],
            "test_layer": "e2e",
            "path_kind": "os_capability" if boundary else "human_path",
            "test_path": "integration_test/bookshelf_import_test.dart",
            "assertions": ["plus button opens picker", "selected folder reaches shelf"],
            "evidence_refs": ["e2e://macos/bookshelf-import"],
            "doubles_policy": "real_only" if boundary else "none",
            "entry_ref": "bookshelf plus button",
            "observable_result": "imported book appears on the shelf",
            "host_ids": ["macos-current"],
            "e2e_scope": "full_project_e2e",
            "navigation_method": "os_control" if boundary else "visible_control",
            "bypassed_step_ids": [],
            "human_interactions": _human_interactions(boundary=boundary),
            "status": "covered",
            **(
                {
                    "background_activity_id": "BA-refresh",
                    "post_update_sequence": _post_update_sequence(),
                }
                if background_activity
                else {}
            ),
        }
    )
    ledger: dict[str, Any] = {
        "schema": "granoflow_test_route_traceability_v1",
        "source_fact_ledger_sha256": "b" * 64,
        "journey_step_traceability_sha256": "a" * 64,
        **({"background_activity_control_sha256": "c" * 64} if background_activity else {}),
        "rows": rows,
    }
    digest = canonical_test_route_traceability_sha256(ledger)
    ledger["review"] = {
        "author_id": "task-author",
        "reviewer_id": "test-reviewer",
        "status": "passed",
        "evidence_refs": ["review://test-routes"],
        "reviewed_traceability_sha256": digest,
    }
    ledger["traceability_sha256"] = digest
    ledger["status"] = "passed"
    return ledger


def refresh_digest(ledger: dict[str, Any]) -> None:
    digest = canonical_test_route_traceability_sha256(ledger)
    ledger["traceability_sha256"] = digest
    ledger["review"]["reviewed_traceability_sha256"] = digest


class TestRouteTraceabilityTests(unittest.TestCase):
    def test_native_picker_unit_and_real_e2e_pass(self) -> None:
        result = validate_test_route_traceability(route_ledger(), project_work())
        self.assertTrue(result["ok"], result)

    def test_service_path_cannot_replace_human_e2e(self) -> None:
        fixture = json.loads(GRANOREADER_FIXTURE.read_text(encoding="utf-8"))
        ledger = route_ledger()
        ledger["rows"][1]["path_kind"] = "service_path"
        ledger["rows"][1]["doubles_policy"] = "allowed"
        refresh_digest(ledger)
        result = validate_test_route_traceability(ledger, project_work())
        codes = {error["code"] for error in result["errors"]}
        self.assertIn(fixture["expected_fail_codes"][2], codes)
        self.assertIn("test_route_os_capability_overclaim", codes)

    def test_test_double_cannot_close_os_capability(self) -> None:
        ledger = route_ledger()
        ledger["rows"][1]["doubles_policy"] = "allowed"
        refresh_digest(ledger)
        result = validate_test_route_traceability(ledger, project_work())
        self.assertIn(
            "test_route_test_double_overclaim",
            {error["code"] for error in result["errors"]},
        )

    def test_missing_missing_plugin_and_cancel_unit_coverage_fails(self) -> None:
        ledger = route_ledger()
        ledger["rows"][0]["covered_failure_modes"] = ["cancel"]
        refresh_digest(ledger)
        result = validate_test_route_traceability(ledger, project_work())
        self.assertIn(
            "test_route_boundary_failure_missing",
            {error["code"] for error in result["errors"]},
        )

    def test_ordinary_ui_step_does_not_require_all_three_layers(self) -> None:
        result = validate_test_route_traceability(
            route_ledger(boundary=False),
            project_work(boundary=False),
        )
        self.assertTrue(result["ok"], result)

    def test_full_project_rejects_direct_url(self) -> None:
        ledger = route_ledger(boundary=False)
        row = ledger["rows"][0]
        row["navigation_method"] = "direct_url"
        row["human_interactions"][0]["navigation_method"] = "direct_url"
        row["bypassed_step_ids"] = ["J-before-import"]
        refresh_digest(ledger)
        result = validate_test_route_traceability(
            ledger,
            project_work(boundary=False),
        )
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("e2e_campaign_forbidden_navigation_method", codes)
        self.assertIn("e2e_campaign_visible_step_bypassed", codes)

    def test_screenshot_is_not_human_interaction_evidence(self) -> None:
        ledger = route_ledger(boundary=False)
        ledger["rows"][0]["human_interactions"][0]["evidence_kind"] = "screenshot"
        refresh_digest(ledger)
        result = validate_test_route_traceability(
            ledger,
            project_work(boundary=False),
        )
        self.assertIn(
            "e2e_campaign_human_interaction_evidence_missing",
            {error["code"] for error in result["errors"]},
        )

    def test_feature_shortcut_declares_bypassed_steps(self) -> None:
        ledger = route_ledger(boundary=False)
        row = ledger["rows"][0]
        row["e2e_scope"] = "feature_e2e"
        row["navigation_method"] = "deep_link"
        row["bypassed_step_ids"] = ["J-import-entry"]
        row["human_interactions"][0]["navigation_method"] = "visible_control"
        refresh_digest(ledger)
        result = validate_test_route_traceability(
            ledger,
            project_work(boundary=False),
        )
        self.assertTrue(result["ok"], result)

    def test_stale_project_digest_and_non_independent_review_fail(self) -> None:
        ledger = copy.deepcopy(route_ledger())
        ledger["journey_step_traceability_sha256"] = "c" * 64
        ledger["review"]["reviewer_id"] = ledger["review"]["author_id"]
        refresh_digest(ledger)
        result = validate_test_route_traceability(ledger, project_work())
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("test_route_traceability_digest_mismatch", codes)
        self.assertIn("test_route_review_failed", codes)

    def test_background_activity_component_and_human_paths_pass(self) -> None:
        result = validate_test_route_traceability(
            route_ledger(boundary=False, background_activity=True),
            project_work(boundary=False, background_activity=True),
        )
        self.assertTrue(result["ok"], result)

    def test_service_path_cannot_replace_background_component_path(self) -> None:
        ledger = route_ledger(boundary=False, background_activity=True)
        ledger["rows"][0]["path_kind"] = "service_path"
        refresh_digest(ledger)
        result = validate_test_route_traceability(
            ledger,
            project_work(boundary=False, background_activity=True),
        )
        self.assertIn(
            "component_path_required",
            {error["code"] for error in result["errors"]},
        )

    def test_background_activity_cannot_end_after_start_only(self) -> None:
        ledger = route_ledger(boundary=False, background_activity=True)
        del ledger["rows"][0]["post_update_sequence"]["second_background_event"]
        refresh_digest(ledger)
        result = validate_test_route_traceability(
            ledger,
            project_work(boundary=False, background_activity=True),
        )
        self.assertIn(
            "post_update_interaction_test_missing",
            {error["code"] for error in result["errors"]},
        )

    def test_exit_callback_without_ended_evidence_fails(self) -> None:
        ledger = route_ledger(boundary=False, background_activity=True)
        del ledger["rows"][1]["post_update_sequence"]["activity_ended"]
        refresh_digest(ledger)
        result = validate_test_route_traceability(
            ledger,
            project_work(boundary=False, background_activity=True),
        )
        self.assertIn(
            "post_update_interaction_test_missing",
            {error["code"] for error in result["errors"]},
        )


if __name__ == "__main__":
    unittest.main()
