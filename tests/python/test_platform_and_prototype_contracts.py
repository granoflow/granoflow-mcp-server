from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-agent-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_platform_support_matrix import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_matrix_sha256,
    validate_platform_support_matrix,
)
from lint_responsive_prototype_bundle import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    canonical_bundle_sha256,
    validate_responsive_prototype_bundle,
)


def _sha(character: str) -> str:
    return character * 64


def _supported_platform(
    platform_id: str,
    layouts: list[str],
    *,
    device_classes: list[str],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": platform_id,
        "support_status": "supported",
        "min_os_version": "17.0",
        "target_sdk_version": "18",
        "required_test_versions": ["17.0", "18.0"],
        "device_classes": device_classes,
        "architectures": ["arm64"],
        "layout_family_ids": layouts,
        "orientations": ["portrait", "landscape"],
        "source_refs": ["product://platform-decision"],
    }
    if platform_id == "android":
        row["min_api_level"] = 28
        row["target_sdk_version"] = "35"
    if platform_id in {"macos", "windows"}:
        row["window_constraints"] = {
            "minimum_size": {"width": 900, "height": 640},
            "default_size": {"width": 1440, "height": 900},
            "resizable": True,
            "fullscreen": True,
        }
    return row


def make_matrix(*, desktop: bool = False) -> dict[str, Any]:
    layouts: list[dict[str, Any]] = [
        {
            "id": "mobile_portrait",
            "orientation": "portrait",
            "reference_viewport": {"width": 390, "height": 844, "dpr": 3},
        }
    ]
    platforms = [
        _supported_platform("ios", ["mobile_portrait"], device_classes=["phone"]),
        _supported_platform("android", ["mobile_portrait"], device_classes=["phone"]),
        {
            "id": "macos",
            "support_status": "not_supported",
            "rationale": "Mobile-only initial release.",
        },
        {
            "id": "windows",
            "support_status": "not_supported",
            "rationale": "Mobile-only initial release.",
        },
    ]
    if desktop:
        layouts.append(
            {
                "id": "desktop_landscape",
                "orientation": "landscape",
                "reference_viewport": {"width": 1440, "height": 900, "dpr": 2},
            }
        )
        platforms[2] = _supported_platform(
            "macos", ["desktop_landscape"], device_classes=["desktop"]
        )
    matrix: dict[str, Any] = {
        "schema": "granoflow_platform_support_v1",
        "layout_families": layouts,
        "primary_layout_family": "mobile_portrait",
        "platforms": platforms,
        "confirmation_status": "user_confirmed",
        "accepted_by": "user",
    }
    matrix["matrix_sha256"] = canonical_matrix_sha256(matrix)
    return matrix


def make_bundle(
    matrix: dict[str, Any],
    *,
    option_count: str = "two",
    unattended: bool = False,
) -> dict[str, Any]:
    count = 3 if option_count == "three" else 2
    options = [
        {
            "id": f"option-{index + 1}",
            "html_sha256": _sha(str(index + 1)),
            "contrast_axes": ["information density", "navigation emphasis"],
            "parity": {
                "capabilities": True,
                "data": True,
                "states": True,
                "behavior": True,
            },
        }
        for index in range(count)
    ]
    required_layouts = {
        layout_id
        for row in matrix["platforms"]
        if row["support_status"] == "supported"
        for layout_id in row["layout_family_ids"]
    }
    platform_ids_by_layout = {
        layout_id: [
            row["id"]
            for row in matrix["platforms"]
            if row["support_status"] == "supported" and layout_id in row["layout_family_ids"]
        ]
        for layout_id in required_layouts
    }
    viewport_by_layout = {row["id"]: row["reference_viewport"] for row in matrix["layout_families"]}
    variants = [
        {
            "layout_family_id": layout_id,
            "platform_ids": platform_ids_by_layout[layout_id],
            "viewport": viewport_by_layout[layout_id],
            "html_ref": f"prototype://{layout_id}.html",
            "html_sha256": _sha("a"),
            "screenshot_ref": f"prototype://{layout_id}.png",
            "screenshot_sha256": _sha("b"),
        }
        for layout_id in sorted(required_layouts)
    ]
    bundle: dict[str, Any] = {
        "schema": "granoflow_responsive_prototype_bundle_v2",
        "analysis_logic_draft_sha256": _sha("e"),
        "screen_content_contract_sha256": _sha("f"),
        "platform_matrix_sha256": matrix["matrix_sha256"],
        "baseline_package_sha256": _sha("c"),
        "widget_catalog_input_sha256": _sha("d"),
        "primary_layout_family": matrix["primary_layout_family"],
        "option_count_decision": option_count,
        "option_count_reason_code": ("three_viable_patterns" if option_count == "three" else None),
        "selection_round": {
            "layout_family_id": matrix["primary_layout_family"],
            "options": options,
        },
        "selected_option_id": "option-1",
        "variants": variants,
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
    bundle["bundle_sha256"] = canonical_bundle_sha256(bundle)
    return bundle


class PlatformSupportMatrixTest(unittest.TestCase):
    def test_mobile_matrix_passes_with_all_four_platform_rows(self) -> None:
        result = validate_platform_support_matrix(make_matrix())
        self.assertTrue(result["ok"])
        self.assertEqual(result["required_layout_family_ids"], ["mobile_portrait"])

    def test_unattended_acceptance_is_explicit(self) -> None:
        matrix = make_matrix()
        matrix["confirmation_status"] = "unattended_auto_adopted"
        matrix["accepted_by"] = "unattended_grant"
        matrix["matrix_sha256"] = canonical_matrix_sha256(matrix)
        self.assertTrue(validate_platform_support_matrix(matrix)["ok"])

    def test_missing_required_platform_fails(self) -> None:
        matrix = make_matrix()
        matrix["platforms"].pop()
        matrix["matrix_sha256"] = canonical_matrix_sha256(matrix)
        result = validate_platform_support_matrix(matrix)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "platform_support_matrix_incomplete")

    def test_supported_platform_requires_versions(self) -> None:
        matrix = make_matrix()
        del matrix["platforms"][0]["min_os_version"]
        matrix["platforms"][0]["required_test_versions"] = []
        matrix["matrix_sha256"] = canonical_matrix_sha256(matrix)
        self.assertFalse(validate_platform_support_matrix(matrix)["ok"])

    def test_unknown_layout_and_missing_desktop_window_fail(self) -> None:
        matrix = make_matrix(desktop=True)
        matrix["platforms"][2]["layout_family_ids"] = ["unknown"]
        del matrix["platforms"][2]["window_constraints"]
        matrix["matrix_sha256"] = canonical_matrix_sha256(matrix)
        result = validate_platform_support_matrix(matrix)
        self.assertFalse(result["ok"])
        details = " ".join(error["detail"] for error in result["errors"])
        self.assertIn("unknown layout", details)
        self.assertIn("window_constraints", details)

    def test_digest_drift_fails_closed(self) -> None:
        matrix = make_matrix()
        matrix["platforms"][0]["min_os_version"] = "18.0"
        result = validate_platform_support_matrix(matrix)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "platform_support_matrix_digest_mismatch"
                for error in result["errors"]
            )
        )


class ResponsivePrototypeBundleTest(unittest.TestCase):
    def test_single_layout_two_option_bundle_passes(self) -> None:
        matrix = make_matrix()
        result = validate_responsive_prototype_bundle(make_bundle(matrix), matrix)
        self.assertTrue(result["ok"])

    def test_mobile_and_desktop_bundle_passes(self) -> None:
        matrix = make_matrix(desktop=True)
        result = validate_responsive_prototype_bundle(make_bundle(matrix), matrix)
        self.assertTrue(result["ok"])
        self.assertEqual(
            result["required_layout_family_ids"],
            ["desktop_landscape", "mobile_portrait"],
        )

    def test_three_options_require_allowed_reason(self) -> None:
        matrix = make_matrix()
        bundle = make_bundle(matrix, option_count="three")
        bundle["option_count_reason_code"] = None
        bundle["bundle_sha256"] = canonical_bundle_sha256(bundle)
        result = validate_responsive_prototype_bundle(bundle, matrix)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "responsive_prototype_option_count_invalid")

    def test_three_distinct_options_and_unattended_acceptance_pass(self) -> None:
        matrix = make_matrix()
        bundle = make_bundle(matrix, option_count="three", unattended=True)
        result = validate_responsive_prototype_bundle(bundle, matrix)
        self.assertTrue(result["ok"])
        self.assertEqual(bundle["authorization_effect"], "none")

    def test_function_or_data_parity_failure_blocks(self) -> None:
        matrix = make_matrix()
        bundle = make_bundle(matrix)
        bundle["selection_round"]["options"][0]["parity"]["data"] = False
        bundle["bundle_sha256"] = canonical_bundle_sha256(bundle)
        result = validate_responsive_prototype_bundle(bundle, matrix)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "responsive_prototype_cross_layout_failed"
                for error in result["errors"]
            )
        )

    def test_required_layout_missing_blocks(self) -> None:
        matrix = make_matrix(desktop=True)
        bundle = make_bundle(matrix)
        bundle["variants"] = [
            row for row in bundle["variants"] if row["layout_family_id"] != "desktop_landscape"
        ]
        bundle["bundle_sha256"] = canonical_bundle_sha256(bundle)
        result = validate_responsive_prototype_bundle(bundle, matrix)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "responsive_prototype_layout_missing" for error in result["errors"]
            )
        )

    def test_bundle_and_platform_digest_drift_block(self) -> None:
        matrix = make_matrix()
        bundle = make_bundle(matrix)
        stale_bundle = copy.deepcopy(bundle)
        stale_bundle["variants"][0]["viewport"]["width"] = 430
        result = validate_responsive_prototype_bundle(stale_bundle, matrix)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "responsive_prototype_digest_mismatch"
                for error in result["errors"]
            )
        )

        changed_matrix = copy.deepcopy(matrix)
        changed_matrix["platforms"][0]["required_test_versions"] = ["18.0"]
        changed_matrix["matrix_sha256"] = canonical_matrix_sha256(changed_matrix)
        result = validate_responsive_prototype_bundle(bundle, changed_matrix)
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
