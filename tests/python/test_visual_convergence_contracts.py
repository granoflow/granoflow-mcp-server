from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).parents[2] / "skills" / "granoflow-agent-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_rendered_prototype_fidelity import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    validate_rendered_fidelity,
)
from lint_visual_lot_receipt import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    validate_visual_lot_receipt,
)
from lint_widget_promotion import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    validate_widget_promotion,
)


def _sha(character: str) -> str:
    return character * 64


def make_bundle() -> dict[str, Any]:
    return {
        "responsive_prototype_bundle": {
            "bundle_sha256": _sha("a"),
            "widget_catalog_input_sha256": _sha("b"),
            "variants": [
                {"layout_family_id": "mobile_portrait"},
                {"layout_family_id": "desktop_landscape"},
            ],
        }
    }


def make_widget_ledger(
    *,
    disposition: str = "reused",
    rationale: str = "",
) -> dict[str, Any]:
    before = _sha("b")
    after = _sha("c") if disposition == "promoted" else before
    return {
        "widget_promotion": {
            "schema": "granoflow_widget_promotion_v1",
            "source_prototype_bundle_sha256": _sha("a"),
            "catalog_before_sha256": before,
            "decisions": [
                {
                    "widget_id": "project.primary-action",
                    "role": "primary_action",
                    "disposition": disposition,
                    "rationale": rationale,
                    "changes_locked_contract": False,
                }
            ],
            "catalog_after_sha256": after,
            "app_readback_sha256": after,
            "status": "passed",
        }
    }


def make_fidelity_ledger() -> dict[str, Any]:
    rows = []
    for index, layout_id in enumerate(("mobile_portrait", "desktop_landscape"), start=1):
        rows.append(
            {
                "layout_family_id": layout_id,
                "prototype_screenshot_ref": f"prototype://{layout_id}.png",
                "prototype_screenshot_sha256": _sha(str(index)),
                "implementation_screenshot_ref": f"build://{layout_id}.png",
                "implementation_screenshot_sha256": _sha(str(index + 2)),
                "numeric_metric": {
                    "name": "pixel_diff_ratio",
                    "value": 0.01,
                    "threshold": 0.02,
                    "passed": True,
                },
                "ai_visual_status": "passed",
                "region_diffs": [{"region": "body", "disposition": "matched"}],
                "recapture_complete": True,
            }
        )
    return {
        "rendered_prototype_fidelity": {
            "schema": "granoflow_rendered_prototype_fidelity_v1",
            "prototype_bundle_sha256": _sha("a"),
            "rows": rows,
            "status": "passed",
            "authorization_effect": "none",
        }
    }


def make_receipt(*, request_type: str = "initial") -> dict[str, Any]:
    ids = ["seed-a", "seed-b"]
    prior_ids: list[str] = []
    if request_type == "revise":
        prior_ids = list(ids)
    return {
        "schema": "granoflow_visual_lot_receipt_v1",
        "batch_id": "batch-1",
        "request_type": request_type,
        "kind": "spec",
        "entropy": "true_random",
        "dedupe": "ledger" if request_type == "refresh" else "off",
        "ids": ids,
        "prior_ids": prior_ids,
        "prior_ledger_sha256": _sha("a"),
        "ledger_after_sha256": _sha("b"),
        "recorded": True,
        "redrawn": request_type != "revise",
        "artifact_sha256s": [_sha("c"), _sha("d")],
        "materially_distinct_status": "passed",
    }


class WidgetPromotionTest(unittest.TestCase):
    def test_reuse_and_promotion_pass_with_app_readback(self) -> None:
        bundle = make_bundle()
        self.assertTrue(validate_widget_promotion(make_widget_ledger(), bundle)["ok"])
        promoted = make_widget_ledger(
            disposition="promoted", rationale="Reusable empty-state action."
        )
        self.assertTrue(validate_widget_promotion(promoted, bundle)["ok"])

    def test_task_local_requires_rationale(self) -> None:
        result = validate_widget_promotion(
            make_widget_ledger(disposition="task_local"),
            make_bundle(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "widget_promotion_required")

    def test_near_duplicate_role_fails(self) -> None:
        ledger = make_widget_ledger()
        ledger["widget_promotion"]["decisions"].append(
            {
                "widget_id": "task.alternate-primary",
                "role": "primary_action",
                "disposition": "promoted",
                "rationale": "Looks similar but was incorrectly duplicated.",
            }
        )
        ledger["widget_promotion"]["catalog_after_sha256"] = _sha("c")
        ledger["widget_promotion"]["app_readback_sha256"] = _sha("c")
        result = validate_widget_promotion(ledger, make_bundle())
        self.assertFalse(result["ok"])

    def test_stale_catalog_and_missing_readback_fail(self) -> None:
        ledger = make_widget_ledger()
        ledger["widget_promotion"]["catalog_before_sha256"] = _sha("d")
        ledger["widget_promotion"]["app_readback_sha256"] = ""
        result = validate_widget_promotion(ledger, make_bundle())
        self.assertFalse(result["ok"])
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("widget_catalog_stale", codes)
        self.assertIn("widget_promotion_readback_mismatch", codes)

    def test_locked_widget_change_reopens_baseline(self) -> None:
        ledger = make_widget_ledger()
        ledger["widget_promotion"]["decisions"][0]["changes_locked_contract"] = True
        result = validate_widget_promotion(ledger, make_bundle())
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "widget_locked_contract_baseline_reopen_required"
                for error in result["errors"]
            )
        )
        ledger["widget_promotion"]["baseline_reopened"] = True
        self.assertTrue(validate_widget_promotion(ledger, make_bundle())["ok"])


class RenderedFidelityTest(unittest.TestCase):
    def test_all_required_viewports_pass(self) -> None:
        result = validate_rendered_fidelity(make_fidelity_ledger(), make_bundle())
        self.assertTrue(result["ok"])

    def test_missing_viewport_blocks(self) -> None:
        ledger = make_fidelity_ledger()
        ledger["rendered_prototype_fidelity"]["rows"].pop()
        result = validate_rendered_fidelity(ledger, make_bundle())
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "rendered_fidelity_layout_missing" for error in result["errors"])
        )

    def test_numeric_and_ai_failures_block(self) -> None:
        ledger = make_fidelity_ledger()
        row = ledger["rendered_prototype_fidelity"]["rows"][0]
        row["numeric_metric"]["value"] = 0.05
        row["numeric_metric"]["passed"] = False
        row["ai_visual_status"] = "failed"
        result = validate_rendered_fidelity(ledger, make_bundle())
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("rendered_fidelity_numeric_failed", codes)
        self.assertIn("rendered_fidelity_ai_failed", codes)

    def test_native_difference_requires_contract_and_approval(self) -> None:
        ledger = make_fidelity_ledger()
        diff = ledger["rendered_prototype_fidelity"]["rows"][0]["region_diffs"][0]
        diff["disposition"] = "approved_native_exception"
        result = validate_rendered_fidelity(ledger, make_bundle())
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                error["code"] == "rendered_fidelity_exception_unapproved"
                for error in result["errors"]
            )
        )
        diff["approved"] = True
        diff["platform_contract_ref"] = "project-work://platform-support-matrix"
        self.assertTrue(validate_rendered_fidelity(ledger, make_bundle())["ok"])

    def test_stale_bundle_digest_blocks(self) -> None:
        ledger = make_fidelity_ledger()
        ledger["rendered_prototype_fidelity"]["prototype_bundle_sha256"] = _sha("f")
        result = validate_rendered_fidelity(ledger, make_bundle())
        self.assertFalse(result["ok"])


class VisualLotReceiptTest(unittest.TestCase):
    def test_initial_refresh_and_revise_receipts_pass(self) -> None:
        for request_type in ("initial", "refresh", "revise"):
            with self.subTest(request_type=request_type):
                self.assertTrue(
                    validate_visual_lot_receipt(make_receipt(request_type=request_type))["ok"]
                )

    def test_refresh_overlap_fails(self) -> None:
        receipt = make_receipt(request_type="refresh")
        receipt["prior_ids"] = ["seed-a"]
        result = validate_visual_lot_receipt(receipt)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(error["code"] == "visual_lot_refresh_overlap" for error in result["errors"])
        )

    def test_artifact_hashes_must_be_distinct_and_reviewed(self) -> None:
        receipt = make_receipt()
        receipt["artifact_sha256s"] = [_sha("c"), _sha("c")]
        receipt["materially_distinct_status"] = "pending"
        result = validate_visual_lot_receipt(receipt)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "visual_lot_artifacts_not_distinct")

    def test_revise_cannot_change_lot_ids(self) -> None:
        receipt = make_receipt(request_type="revise")
        receipt["prior_ids"] = ["seed-a", "seed-c"]
        result = validate_visual_lot_receipt(receipt)
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
