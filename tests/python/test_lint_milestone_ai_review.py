import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).parents[2]
    / "skills/granoflow-agent-workflow/scripts/lint_milestone_ai_review.py"
)
SPEC = importlib.util.spec_from_file_location("lint_milestone_ai_review", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def make_record(*, ui: bool = True, fallback: bool = False):
    providers = [
        {
            "capability": "prd-review",
            "disposition": "native_fallback" if fallback else "selected",
            "result": "model_fallback" if fallback else "used",
            "evidence_ref": "evidence://prd-review",
        },
        {
            "capability": "engineering-reviewer",
            "disposition": "selected",
            "result": "used",
            "evidence_ref": "evidence://engineering",
        },
    ]
    if ui:
        providers.append(
            {
                "capability": "design-reviewer",
                "disposition": "selected",
                "result": "used",
                "evidence_ref": "evidence://design",
            }
        )
    task_plan = {
        "status": "passed",
        "tasks": [
            {
                "id": "T1",
                "responsibility": "deliver one coherent slice",
                "dependencies": [],
                "acceptance": ["behavior is observable"],
                "screens": ["library"] if ui else [],
            }
        ],
        "review": {
            "mode": "ai_auto",
            "roles": {
                "author": "author",
                "reviewers": ["prd-review", "engineering-reviewer"],
                "final_verifier": "final-verifier",
            },
            "providers": providers,
            "grill": {
                "generated_question_count": 3,
                "closed_question_count": 3,
                "open_blocking_count": 0,
            },
            "ai_review_status": "passed",
            "final_verifier_status": "passed",
            "reviewed_plan_sha256": "",
        },
    }
    task_plan["review"]["reviewed_plan_sha256"] = MODULE.canonical_plan_sha256(task_plan)
    return {"schema_version": 2, "task_plan": task_plan}


def make_pack(record, *, unattended: bool = False):
    digest = record["task_plan"]["review"]["reviewed_plan_sha256"]
    if unattended:
        grill_status = "recommendations_auto_adopted"
        final_status = "unattended_auto_adopted"
        accepted_by = "unattended_grant"
    else:
        grill_status = "shared_understanding_confirmed"
        final_status = "user_accepted"
        accepted_by = "user"
    return {
        "status": "accepted",
        "accepted_by": accepted_by,
        "ai_decomposition_review_ref": "review://milestone/M1",
        "ai_decomposition_plan_sha256": digest,
        "grill_finalizer_status": "passed",
        "grill_me_status": grill_status,
        "final_acceptance_status": final_status,
        "accepted_plan_sha256": digest,
        "authorization_effect": "none",
    }


class MilestoneAiReviewTests(unittest.TestCase):
    def test_ui_and_non_ui_happy_paths(self):
        for ui in (True, False):
            with self.subTest(ui=ui):
                errors, _ = MODULE.validate_decomposition(make_record(ui=ui))
                self.assertEqual(errors, [])

    def test_native_fallback_with_evidence_passes(self):
        errors, _ = MODULE.validate_decomposition(make_record(fallback=True))
        self.assertEqual(errors, [])

    def test_open_blocking_finding_fails(self):
        record = make_record()
        record["task_plan"]["review"]["grill"]["open_blocking_count"] = 1
        errors, _ = MODULE.validate_decomposition(record)
        self.assertIn(
            "milestone_ai_review_blocking_findings: open blockers must be zero",
            errors,
        )

    def test_failed_verifier_fails(self):
        record = make_record()
        record["task_plan"]["review"]["final_verifier_status"] = "failed"
        errors, _ = MODULE.validate_decomposition(record)
        self.assertIn("milestone_ai_review_verifier_failed", errors)

    def test_reviewed_content_mutations_invalidate_digest(self):
        mutations = (
            ("responsibility", "different responsibility"),
            ("dependencies", ["T0"]),
            ("acceptance", ["different acceptance"]),
            ("screens", ["settings"]),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                record = make_record()
                record["task_plan"]["tasks"][0][field] = value
                errors, _ = MODULE.validate_decomposition(record)
                self.assertIn("milestone_ai_review_plan_digest_mismatch", errors)

    def test_interactive_user_acceptance_passes(self):
        record = make_record()
        errors, _ = MODULE.validate_execution_ready(record, make_pack(record))
        self.assertEqual(errors, [])

    def test_unattended_auto_adoption_passes(self):
        record = make_record()
        errors, _ = MODULE.validate_execution_ready(
            record,
            make_pack(record, unattended=True),
        )
        self.assertEqual(errors, [])

    def test_missing_grill_me_fails(self):
        record = make_record()
        pack = make_pack(record)
        pack["grill_me_status"] = ""
        errors, _ = MODULE.validate_execution_ready(record, pack)
        self.assertIn("milestone_final_grill_me_required", errors)

    def test_missing_final_acceptance_fails(self):
        record = make_record()
        pack = make_pack(record)
        pack["final_acceptance_status"] = ""
        errors, _ = MODULE.validate_execution_ready(record, pack)
        self.assertIn("milestone_final_acceptance_required", errors)

    def test_acceptance_digest_mismatch_fails(self):
        record = make_record()
        pack = make_pack(record)
        pack["accepted_plan_sha256"] = "0" * 64
        errors, _ = MODULE.validate_execution_ready(record, pack)
        self.assertIn("milestone_final_acceptance_digest_mismatch", errors)

    def test_legacy_v1_is_read_only_only_when_explicitly_allowed(self):
        errors, _ = MODULE.validate_decomposition({"schema_version": 1})
        self.assertTrue(errors)
        errors, details = MODULE.validate_decomposition(
            {"schema_version": 1},
            allow_legacy_v1=True,
        )
        self.assertEqual(errors, [])
        self.assertEqual(details, {"status": "legacy_v1_read_only"})

    def test_markdown_frontmatter_is_loadable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "pack.md"
            path.write_text("---\nstatus: accepted\n---\n# Pack\n", encoding="utf-8")
            self.assertEqual(MODULE.load_record(path), {"status": "accepted"})

    def test_cli_emits_structured_result(self):
        record = make_record()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "task-plan.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                result = MODULE.main(
                    [
                        "--task-plan",
                        str(path),
                        "--phase",
                        "decomposition_passed",
                    ]
                )
        self.assertEqual(result, 0)
        self.assertTrue(json.loads(output.getvalue())["ok"])


if __name__ == "__main__":
    unittest.main()
