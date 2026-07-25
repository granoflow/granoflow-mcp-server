# Project E2E SoT Template

Copy to `temp/project-e2e-sot-v<n>.md`. See `project-e2e-sot.md`.

```yaml
---
doc_type: project_e2e_sot
schema: granoflow_project_e2e_sot_v1
project_id: ""
project_title: ""
status: active # active | paused | completed | superseded
interaction_mode: interactive # interactive | unattended
collaborative_planning_surface: unknown
host_wake_surface: unknown
host_wake_bound: false
bound_sot_path: temp/project-e2e-sot-v1.md
updated_at: ""
source_digests:
  project_work: ""
  milestone_work: "" # optional
  portfolio: ""
# Required for long/unattended resume (--require-digest-match): host fills from App readback
source_digest_verification:
  project_work:
    recorded: "" # must equal source_digests.project_work
    app_readback: "" # App content SHA / digest
    matched: false
cross_milestone_integration: not_applicable # pending | planned | not_applicable
stages:
  - id: project_init
    status: not_started # not_started | in_progress | done | blocked
    evidence: ""
  - id: milestones_created
    status: not_started
    evidence: ""
  - id: milestone_analysis
    status: not_started
    evidence: ""
  - id: milestone_plan
    status: not_started
    evidence: ""
  - id: milestone_implement
    status: not_started
    evidence: ""
  - id: integration_campaign
    status: not_started
    evidence: ""
  - id: e2e_campaign
    status: not_started
    evidence: ""
  - id: project_complete
    status: not_started
    evidence: ""
work_items: []
# Example after portfolio ready:
# - id: M1.T1.3.1_analysis
#   pair: M1.T1
#   seq: "3.1"
#   stage_id: milestone_analysis
#   skill: granoflow-task-orchestrator
#   status: pending # pending | in_progress | done | blocked | paused | cancelled
#   confirmation: none # none | user_confirmed | unattended_auto_adopted
#   evidence_ref: null
# - id: M1.T1.3.2_plan
#   pair: M1.T1
#   seq: "3.2"
#   stage_id: milestone_plan
#   skill: granoflow-task-orchestrator
#   status: pending
#   confirmation: none
#   evidence_ref: null
# - id: M1.implement
#   stage_id: milestone_implement
#   skill: granoflow-task-orchestrator
#   status: pending
#   pack_path: temp/milestone-plan-acceptance-M1-v1.md
#   confirmation: none
#   evidence_ref: null
next_step:
  work_item_id: "" # required when status=active and work remains
  # At pack/Layer B/E2E/resume transitions, summary Must name gate lint (see project-e2e-sot.md)
  summary: ""
  pinned_by: null # analysis_context_affinity | schedule | null
  override: null # null | user_explicit
integration_campaign:
  path: not_started # full_unit_and_it | waived_e2e_direct | not_started
  cross_milestone_journey_check: not_applicable # not_applicable | covered | gap
  evidence_ref: []
e2e_campaign:
  coverage_matrix_check: not_applicable # not_applicable | covered | gap
  evidence_ref: []
# Optional; omit or [] when no concurrent batches this run:
parallel_batches: [] # [{ batch_id, review_ref, status: draft|pending_acceptance|accepted|rejected|superseded|parked }]
---
```

# Project E2E SoT — `<project_title>`

## Goal

## Next step

## Notes
