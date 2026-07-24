# Milestone Task Plan Template

Machine-readable **composition SoT** for one milestone's refined screens, page
journeys, and task summaries. Load via MCP
(`referenceId: milestone-task-plan-template`). Persist as YAML on Milestone Work
during `decompose_required`.

- **Not** a second product `R-*` ledger (Project Work remains product SoT).
- Project Work keeps **key-page inventory** only (`key_pages_from_sources`).
- Hi-fi HTML stays in task Analysis `ui_prototype`.
- Sibling file `milestone-task-plan-template.yaml` mirrors this shape for
  host-side copy.

## Rules

1. New and reopened requirement-driven/software milestones use schema v2 and
   pass `milestone-ai-review` before App `create_one`; completed v1 records are
   read-only until changed or continued.
2. Every `refined_screens[]` row needs completed `split_probe` and ≥1
   `tasks[].screen_ids` entry.
3. Refined screens `traces_to_key_screen` or `provenance: milestone_discovered`.
4. **Detail carry-forward (hard):** every Project Work
   `screen_coverage[].ui_details[]` on in-scope key pages Must appear in
   `detail_carryforward.rows` as `carried` | `deferred_out_of_milestone` |
   `out_of_scope` (with rationale). Silent drop →
   `milestone_detail_carryforward_incomplete`.
5. In-scope key pages (sharing this milestone's acceptance ids, or listed in
   `key_screen_refs`) Must be referenced; do not leave PW key pages orphaned.
6. Changing ownership/split/detail disposition → `status: reopened` / `draft`;
   Task Analysis Must not silently reopen (`reopen_policy`).
7. Lint decomposition review with
   `granoflow-agent-workflow/scripts/lint_milestone_ai_review.py --phase decomposition_passed`.
8. Lint screen carry-forward with
   `granoflow-agent-workflow/scripts/lint_task_screen_portfolio.py --project-work`.

## Shape

```yaml
document_type: milestone_task_plan
schema_version: 2
project_id: null
milestone_id: null
work_version: 1
updated_at: null

# Align with Milestone Work decomposition_status when status: passed.
task_plan:
  status: draft # draft | passed | reopened | not_applicable
  fail_closed_code: milestone_task_plan_incomplete
  review:
    mode: ai_auto
    roles:
      author: null
      reviewers: []
      final_verifier: null
    providers:
      - capability: prd-review
        disposition: selected # selected | native_fallback | not_required
        result: used # used | model_fallback | not_required
        evidence_ref: null
    grill:
      generated_question_count: 0
      closed_question_count: 0
      open_blocking_count: 0
    ai_review_status: pending # pending | passed | failed
    final_verifier_status: pending # pending | passed | failed
    reviewed_plan_sha256: null
  # Project Work key screen_ids this milestone traces (may be empty for non-UI).
  key_screen_refs: []
  # Every PW ui_detail on in-scope key pages must appear here (no silent drop).
  detail_carryforward:
    status: incomplete # incomplete | complete | not_applicable
    fail_closed_code: milestone_detail_carryforward_incomplete
    rows:
      - key_screen_id: S-example
        detail_id: example_detail
        # carried | deferred_out_of_milestone | out_of_scope
        disposition: carried
        carried_to_refined_screen: S-example # required when carried
        carried_to_task_local_key: T1 # required when carried
        rationale: null # required when deferred_* or out_of_scope
  refined_screens:
    - screen_id: S-example
      title: null
      # Trace to a PW key page, or mark milestone_discovered.
      traces_to_key_screen: null # S-* | null
      provenance: traces_to_key_screen # traces_to_key_screen | milestone_discovered
      acceptance_ids: []
      carried_ui_detail_ids: [] # detail_ids carried onto this refined screen
      split_probe:
        pass_completed: false
        # keep_cohesive | split | needs_user_decision
        conclusion: null
        rejected_split_summary: null
        accepted_split_summary: null
        resulting_screen_ids: []
        rationale: null
  page_journeys:
    - journey_id: MJ-001
      title: null
      screen_ids: []
      summary: null
      acceptance_ids: []
  tasks:
    - local_key: T1
      task_id: null # App id after create_one
      responsibility: null # frozen one-line duty
      screen_ids: []
      acceptance_ids: []
      depends_on: []
      reopen_policy: forbidden_without_milestone_task_plan_reopen
  checklist:
    every_refined_screen_has_split_probe: false
    every_refined_screen_has_task: false
    every_task_has_responsibility: false
    traces_or_discovered_set: false
    every_in_scope_key_page_referenced: false
    every_pw_ui_detail_dispositioned: false
```
