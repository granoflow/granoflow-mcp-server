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

from lint_implementation_contract_semantic_replay import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_implementation_replay_sha256,
    canonical_implementation_snapshot_sha256,
    validate_implementation_contract_semantic_replay,
)
from lint_platform_support_matrix import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_matrix_sha256,
)
from lint_requirement_contract_traceability import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    contract_element_refs,
)
from test_task_analysis_finalization_contracts import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    make_content,
    make_logic,
)


def _sha(character: str) -> str:
    return character * 64


def make_platform() -> dict[str, Any]:
    layouts = {
        "ios": ("mobile_portrait", "17", "phone"),
        "android": ("mobile_portrait", "14", "phone"),
        "macos": ("desktop_landscape", "14", "desktop"),
        "windows": ("desktop_landscape", "11", "desktop"),
    }
    matrix: dict[str, Any] = {
        "schema": "granoflow_platform_support_v1",
        "platforms": [
            {
                "id": platform_id,
                "support_status": "supported",
                "layout_family_ids": [layout],
                "required_test_versions": [version],
                "device_classes": [device],
            }
            for platform_id, (layout, version, device) in layouts.items()
        ],
    }
    matrix["matrix_sha256"] = canonical_matrix_sha256(matrix)
    return matrix


def make_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "schema": "granoflow_implementation_snapshot_v1",
        "files": [
            {"path": "lib/features/detail/model.dart", "sha256": _sha("1")},
            {"path": "lib/features/detail/view.dart", "sha256": _sha("2")},
        ],
        "build_ref": "build://app/semantic-replay",
        "build_sha256": _sha("3"),
    }
    snapshot["snapshot_sha256"] = canonical_implementation_snapshot_sha256(snapshot)
    return snapshot


def make_sources() -> tuple[dict[str, Any], ...]:
    return (
        make_platform(),
        make_content(make_logic()),
        {"bundle_sha256": _sha("a")},
        {"semantic_review_sha256": _sha("b")},
        {"technical_package_sha256": _sha("c")},
        make_snapshot(),
    )


def make_replay(
    platform: dict[str, Any],
    content: dict[str, Any],
    bundle: dict[str, Any],
    semantic: dict[str, Any],
    technical: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    binding_kinds = {
        "ios": "native_semantics",
        "android": "test_id",
        "macos": "accessibility",
        "windows": "dom",
    }
    targets = [
        {
            "id": f"{row['id']}-{row['layout_family_ids'][0]}",
            "platform_id": row["id"],
            "layout_family_id": row["layout_family_ids"][0],
            "test_version": row["required_test_versions"][0],
            "device_class": row["device_classes"][0],
            "runtime_artifact_ref": f"runtime://{row['id']}",
            "runtime_artifact_sha256": _sha("4"),
        }
        for row in platform["platforms"]
    ]
    rows: list[dict[str, Any]] = []
    for element in sorted(contract_element_refs(content)):
        for target in targets:
            row: dict[str, Any] = {
                "contract_element_ref": element,
                "runtime_target_id": target["id"],
                "runtime_binding": {
                    "kind": binding_kinds[target["platform_id"]],
                    "ref": f"runtime://{target['id']}/{element}",
                },
                "capture_ref": f"capture://{target['id']}/{element}",
                "capture_sha256": _sha("5"),
                "status": "verified",
            }
            if element.startswith(("action:", "navigation:")):
                row["interaction_evidence_ref"] = f"interaction://{target['id']}/{element}"
                row["interaction_evidence_sha256"] = _sha("6")
            if element.startswith(("state:", "permission:")):
                row["state_capture_ref"] = f"state://{target['id']}/{element}"
                row["state_capture_sha256"] = _sha("7")
            if element.startswith(("field:", "data_source:")):
                row["data_evidence_ref"] = f"data://{target['id']}/{element}"
                row["data_evidence_sha256"] = _sha("8")
            rows.append(row)
    replay: dict[str, Any] = {
        "schema": "granoflow_implementation_contract_semantic_replay_v1",
        "applicability": "required",
        "implementation_author_id": "implementation-author",
        "platform_matrix_sha256": platform["matrix_sha256"],
        "content_contract_sha256": content["content_contract_sha256"],
        "prototype_bundle_sha256": bundle["bundle_sha256"],
        "prototype_semantic_review_sha256": semantic["semantic_review_sha256"],
        "technical_package_sha256": technical["technical_package_sha256"],
        "implementation_snapshot_sha256": snapshot["snapshot_sha256"],
        "preconditions": {
            "app_readback_status": "verified",
            "execution_authorization_status": "valid",
            "run_status": "valid",
            "implementation_design_fidelity_status": "complete",
            "runnable_build_status": "passed",
        },
        "runtime_targets": targets,
        "rows": rows,
        "deterministic_runtime": {
            "status": "passed",
            "runtime_target_ids": [target["id"] for target in targets],
            "evidence_refs": ["runtime://semantic-suite"],
        },
        "open_blockers": [],
        "authorization_effect": "none",
    }
    digest = canonical_implementation_replay_sha256(replay)
    replay["ai_semantic_review"] = {
        "reviewer_id": "semantic-reviewer",
        "status": "passed",
        "evidence_refs": ["review://semantic"],
        "reviewed_replay_sha256": digest,
    }
    replay["final_verifier"] = {
        "verifier_id": "semantic-final-verifier",
        "status": "passed",
        "evidence_refs": ["verify://semantic"],
        "verified_replay_sha256": digest,
    }
    replay["status"] = "passed"
    replay["replay_sha256"] = digest
    return replay


class ImplementationContractSemanticReplayTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = make_sources()
        self.replay = make_replay(*self.sources)

    def validate(
        self,
        replay: dict[str, Any] | None = None,
        html_paths: dict[str, Path] | None = None,
    ) -> dict[str, Any]:
        return validate_implementation_contract_semantic_replay(
            replay or self.replay,
            *self.sources,
            html_paths,
        )

    def test_web_flutter_apple_android_bindings_pass(self) -> None:
        result = self.validate()
        self.assertTrue(result["ok"])
        self.assertEqual(result["runtime_target_count"], 4)
        self.assertGreater(result["required_pair_count"], 40)

    def test_runtime_html_markers_are_checked(self) -> None:
        elements = sorted(contract_element_refs(self.sources[1]))
        html = "".join(f'<div data-contract-ref="{element}"></div>' for element in elements)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "windows.html"
            path.write_text(html, encoding="utf-8")
            target_id = "windows-desktop_landscape"
            self.assertTrue(self.validate(html_paths={target_id: path})["ok"])
            path.write_text('<div data-contract-ref="screen:missing"></div>', encoding="utf-8")
            self.assertFalse(self.validate(html_paths={target_id: path})["ok"])

    def test_missing_target_and_element_block(self) -> None:
        replay = copy.deepcopy(self.replay)
        removed = replay["runtime_targets"].pop()
        replay["rows"] = [
            row for row in replay["rows"] if row["runtime_target_id"] != removed["id"]
        ]
        codes = {error["code"] for error in self.validate(replay)["errors"]}
        self.assertIn("implementation_contract_target_coverage_missing", codes)
        self.assertIn("implementation_contract_replay_digest_mismatch", codes)
        replay = copy.deepcopy(self.replay)
        replay["rows"].pop()
        self.assertIn(
            "implementation_contract_element_missing",
            {error["code"] for error in self.validate(replay)["errors"]},
        )

    def test_interaction_state_and_data_evidence_block(self) -> None:
        replay = copy.deepcopy(self.replay)
        rows = replay["rows"]
        next(row for row in rows if row["contract_element_ref"].startswith("action:")).pop(
            "interaction_evidence_ref"
        )
        next(row for row in rows if row["contract_element_ref"].startswith("state:")).pop(
            "state_capture_ref"
        )
        next(row for row in rows if row["contract_element_ref"].startswith("field:")).pop(
            "data_evidence_ref"
        )
        codes = {error["code"] for error in self.validate(replay)["errors"]}
        self.assertIn("implementation_contract_interaction_failed", codes)
        self.assertIn("implementation_contract_state_unverified", codes)
        self.assertIn("implementation_contract_data_binding_unverified", codes)

    def test_approved_platform_exception_requires_evidence(self) -> None:
        replay = copy.deepcopy(self.replay)
        row = replay["rows"][0]
        row["status"] = "approved_platform_exception"
        row["platform_exception_ref"] = "platform://ios/native-behavior"
        row["approved_exception_evidence_ref"] = "decision://native-exception"
        row["rationale"] = "The platform contract requires the native control."
        digest = canonical_implementation_replay_sha256(replay)
        replay["replay_sha256"] = digest
        replay["ai_semantic_review"]["reviewed_replay_sha256"] = digest
        replay["final_verifier"]["verified_replay_sha256"] = digest
        self.assertTrue(self.validate(replay)["ok"])
        del row["approved_exception_evidence_ref"]
        self.assertFalse(self.validate(replay)["ok"])

    def test_source_snapshot_and_structural_drift_block(self) -> None:
        replay = copy.deepcopy(self.replay)
        replay["content_contract_sha256"] = _sha("d")
        replay["preconditions"]["implementation_design_fidelity_status"] = "needs_split"
        snapshot = copy.deepcopy(self.sources[-1])
        snapshot["files"][0]["sha256"] = _sha("e")
        result = validate_implementation_contract_semantic_replay(
            replay, *self.sources[:-1], snapshot
        )
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("implementation_contract_source_digest_mismatch", codes)
        self.assertIn("implementation_contract_runtime_failed", codes)

    def test_reviews_blockers_and_authority_fail_closed(self) -> None:
        replay = copy.deepcopy(self.replay)
        replay["deterministic_runtime"]["status"] = "failed"
        replay["ai_semantic_review"]["reviewer_id"] = replay["implementation_author_id"]
        replay["final_verifier"]["verifier_id"] = replay["ai_semantic_review"]["reviewer_id"]
        replay["open_blockers"] = ["The submit action did not persist."]
        replay["authorization_effect"] = "execution_authorization"
        codes = {error["code"] for error in self.validate(replay)["errors"]}
        self.assertIn("implementation_contract_runtime_failed", codes)
        self.assertIn("implementation_contract_ai_failed", codes)
        self.assertIn("implementation_contract_verifier_failed", codes)
        self.assertIn("implementation_contract_open_blockers", codes)
        self.assertIn("implementation_contract_authorization_invalid", codes)

    def test_non_ui_task_can_be_not_applicable(self) -> None:
        replay: dict[str, Any] = {
            "schema": "granoflow_implementation_contract_semantic_replay_v1",
            "applicability": "not_applicable",
            "task_type": "backend",
            "rationale": "The task has no user interface.",
            "authorization_effect": "none",
            "status": "not_applicable",
        }
        replay["replay_sha256"] = canonical_implementation_replay_sha256(replay)
        self.assertTrue(validate_implementation_contract_semantic_replay(replay)["ok"])


if __name__ == "__main__":
    unittest.main()
