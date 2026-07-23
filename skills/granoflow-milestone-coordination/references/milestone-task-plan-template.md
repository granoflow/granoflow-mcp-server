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

1. UI/software milestones with user-visible pages: `task_plan.status: passed`
   before App `create_one` (aligns with `decomposition_status: passed`).
2. Every `refined_screens[]` row needs completed `split_probe` and ≥1
   `tasks[].screen_ids` entry.
3. Refined screens `traces_to_key_screen` or `provenance: milestone_discovered`.
4. Changing ownership/split → `status: reopened` / `draft`; Task Analysis Must
   not silently reopen (`reopen_policy`).
5. Lint: `granoflow-agent-workflow/scripts/lint_task_screen_portfolio.py`.

## Shape

```yaml
document_type: milestone_task_plan
schema_version: 1
project_id: null
milestone_id: null
work_version: 1
updated_at: null

# Align with Milestone Work decomposition_status when status: passed.
task_plan:
  status: draft # draft | passed | reopened | not_applicable
  fail_closed_code: milestone_task_plan_incomplete
  # Project Work key screen_ids this milestone traces (may be empty for non-UI).
  key_screen_refs: []
  refined_screens:
    - screen_id: S-example
      title: null
      # Trace to a PW key page, or mark milestone_discovered.
      traces_to_key_screen: null # S-* | null
      provenance: traces_to_key_screen # traces_to_key_screen | milestone_discovered
      acceptance_ids: []
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
```
