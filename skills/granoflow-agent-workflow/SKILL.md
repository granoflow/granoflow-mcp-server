---
name: granoflow-agent-workflow
description: >-
  Use when working with Granoflow tasks, Task Work/Delivery, waiting for user
  input, weekly/monthly reviews, review cards, long-term work memory, project
  lifecycle boards, milestone Plan acceptance packs, project E2E SoT,
  long-task run continuity, workflow-jargon glosses, Local HTTP API setup, or
  dissatisfaction with
  Granoflow/MCP output. Call granoflow_task_orchestrator_skill first when the
  request may mean capture, Analysis, Planning, execution, or completion audit.
  Delegate explicit daily review to granoflow-daily-review; project init to
  granoflow-project-definition. Not a generic coding, CI, or repo-automation skill.
---

# Granoflow Agent Workflow

Downstream owner for Task Work, Grill, waiting, Delivery, completion, cards, and
context after routing is clear. Call `granoflow_task_orchestrator_skill` first
when phase may be capture/Analysis/Planning/execution/completion-audit. Explicit
daily review → `granoflow-daily-review`. Project init →
`granoflow_project_definition_skill`. Do not quick-capture merely because text
contains “create task” when a later phase is clearly requested.

Granoflow MCP is a thin bridge to the local Granoflow app—not a code analyzer,
CI fixer, or repo-automation framework.

## Keyword

- `#granoflow-agent-workflow`
- `#task-work`
- `#task-delivery`
- `#grill`

## Branch Router

Pick one branch. Load refs with
`granoflow_bundled_skill_reference(skillId, referenceId)` before steps. Always
apply matching **Hard Gates**. Project-bound software turns also emit the
lifecycle board.

### Language policy

- Skill and reference **contract body** stays English (including Hard Gates,
  field names, fail-closed codes, and templates).
- Public listing / npm / registry copy stays English-only.
- Runtime may accept localized **trigger phrases** and may use localized
  **user-facing sample utterances** when that helps the user and does not
  remove or weaken the English contract path for English users.
- Do **not** translate skill text for human reading of Skills—readers may ask
  an AI to translate. Do not maintain dual-language contract copies.

| User intent                            | Branch                                    | Call first                                    | Must load                                                                    | Stop if                                     |
| -------------------------------------- | ----------------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------- |
| API/MCP connect fail                   | Connection First                          | `granoflow_setup_status`                      | `connection-first`                                                           | config write without dry-run                |
| Milestone create / task into milestone | Milestone And Task Deadlines              | —                                             | `milestone-and-task-deadlines`                                               | deadline-less milestone                     |
| Capture from discussion                | Discussed Requirement Task Capture        | Orchestrator → `capture`                      | `discussed-requirement-task-capture`                                         | multi-sentence success / invented placement |
| Today/dated/unfinished batch           | Due Task Processing And Execution         | Orchestrator if needed                        | `daily-pending-task-triage`, `task-work-document-workflow`                   | execute without ledger/Grill                |
| History / similar past work            | Long-Term Work Memory                     | —                                             | `long-term-work-memory`                                                      | guessing missing records                    |
| Context YAML / living Project Work     | Project And Milestone Context Stewardship | `granoflow_project_definition_skill` for init | `project-context-attachments`                                                | software edit without context Hard Gate     |
| Finish/complete task                   | Completing Tasks                          | —                                             | `task-delivery-workflow`, `implementation-learning-ledger`                   | complete without verified Work Document     |
| Auth/decision/login/2FA block          | Waiting For User Input                    | delegated-auth if envelope                    | `waiting-for-user-input`                                                     | chat-only ask                               |
| Analyze/start/execute one task         | Task Work And Execution                   | Orchestrator if unclear                       | `task-work-document-workflow` (+ template), `implementation-learning-ledger` | execute before separate instruction         |
| Weekly/monthly review                  | Review Drafting                           | —                                             | `review-drafting`                                                            | write without confirm                       |
| After-16:30 nudge                      | Daily Review Nudge                        | —                                             | —                                                                            | start review from nudge                     |
| Unhappy with Granoflow/MCP output      | User Dissatisfaction                      | —                                             | —                                                                            | treat as publish/commit auth                |
| Explicit daily journal/mood            | _(delegate)_                              | `granoflow_daily_review_skill`                | daily-review skill                                                           | draft daily review here                     |

## Hard Gates (must)

| When                                   | Gate                                     | Load                                                                                                                                                                                                                                                                | Fail closed                                                                                                                                                                                                                                                                        |
| -------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Project-bound software turn end        | Lifecycle board + attach                 | `project-lifecycle-progress-board` (+ render) + `pipeline-attachment-and-reentry`                                                                                                                                                                                   | `project_lifecycle_board_missing`, `pipeline_entry_unclassified`, `pipeline_reentry_skipped`, `pipeline_stage_not_rewound`                                                                                                                                                         |
| User-facing workflow jargon            | Plain-language gloss                     | `project-interaction-style`, `workflow-jargon-plain-language`                                                                                                                                                                                                       | `workflow_jargon_unexplained`                                                                                                                                                                                                                                                      |
| Mobile/desktop App PD                  | App icon                                 | `app-icon-source-gate`                                                                                                                                                                                                                                              | `app_icon_source_*`                                                                                                                                                                                                                                                                |
| Milestone/task portfolio (UI)          | Milestone task_plan SoT                  | `screen-task-portfolio-coverage` + `milestone-task-plan-template` (+ `lint_task_screen_portfolio.py`)                                                                                                                                                               | `milestone_task_plan_incomplete`, `task_portfolio_screen_coverage_incomplete`, `screen_split_probe_incomplete`, `screen_task_portfolio_coverage_unread`                                                                                                                            |
| Milestone decomposition/final accept   | AI review + final Grill                  | `milestone-ai-review` (+ `lint_milestone_ai_review.py`)                                                                                                                                                                                                             | `milestone_ai_review_*`, `milestone_final_grill_me_required`, `milestone_final_acceptance_*`                                                                                                                                                                                       |
| Analysis close (UI tasks)              | Analysis deliverables                    | `task-work-document-workflow` § Analysis Deliverables (+ `prototype-serial-revision` + `prototype-doc-coverage` + `lint_prototype_stack.py` on prototype source + `lint_prototype_link_ledger.py --require-complete` + `lint_prototype_revision_ledger.py` when UI) | `analysis_deliverables_incomplete`, `ui_prototype_required`, `prototype_stack_forbidden_*`, `prototype_link_*`, `prototype_revision_*`, `milestone_task_plan_incomplete`                                                                                                           |
| Multi-milestone schedule               | Schedule Policy                          | `project-lifecycle-progress-board` Schedule Policy (+ `schedule_policy` derived from `interaction_mode`)                                                                                                                                                            | `implement_before_all_ap_forbidden` under interactive; unattended entry activates host Plan + bound host wake when available (`long-task-run-continuity`)                                                                                                                          |
| UI prototype lock/rematch              | HTML/widget/doc coverage + stack lock    | `prototype-doc-coverage` (+ `lint_prototype_stack.py`) + `prototype-serial-revision`                                                                                                                                                                                | `prototype_html_coverage_*`, `prototype_stack_forbidden_*`, `widget_reuse_required`, `prototype_plan_truth_*`, `prototype_revision_*`                                                                                                                                              |
| UI platform/Analysis finalization      | Responsive Bundle                        | `responsive-prototype-finalization` (+ platform, bundle, widget promotion linters)                                                                                                                                                                                  | `platform_support_matrix_*`, `responsive_prototype_*`, `widget_promotion_*`                                                                                                                                                                                                        |
| UI product/technical Analysis closure  | Analysis finalization                    | `task-analysis-finalization` (+ logic, traceability, Grill, semantic incl. Prototype→Contract reverse, technical package linters)                                                                                                                                   | `analysis_logic_draft_*`, `screen_content_contract_*`, `requirement_contract_*`, `contract_grill_*`, `contract_prototype_*`, `prototype_contract_orphan_ref`, `prototype_interactive_unmarked`, `analysis_technical_package_*`                                                     |
| Runnable UI before Task Delivery       | Runtime semantics + rendered fidelity    | `implementation-contract-semantic-replay`, `responsive-prototype-finalization`, `prototype-implementation-fidelity`                                                                                                                                                 | `implementation_contract_*`, `rendered_fidelity_*`                                                                                                                                                                                                                                 |
| UI implement before unit tests         | Prototype Phase A                        | `prototype-implementation-fidelity`                                                                                                                                                                                                                                 | Phase A / undeclared codes                                                                                                                                                                                                                                                         |
| Software Delivery (non-UI design)      | Impl design fidelity                     | `implementation-design-fidelity`                                                                                                                                                                                                                                    | `impl_design_fidelity_*` (keep⇒rationale+design writeback)                                                                                                                                                                                                                         |
| Task vs milestone closeout             | Acceptance layers                        | `task-and-milestone-acceptance-layers`                                                                                                                                                                                                                              | `acceptance_layers_fused` if Layer A/B merged into one unlabeled “all done”                                                                                                                                                                                                        |
| Delivery / Layer A–B / E2E close       | Plan case implementation                 | `lint_plan_case_implementation.py` (`layer_a` / `layer_b` / `e2e_campaign`) + Delivery profile                                                                                                                                                                      | `plan_case_implementation_*`, `plan_case_test_ref_missing`, `plan_case_test_ref_unbound`                                                                                                                                                                                           |
| Plan/Delivery unit policy              | Ops coverage; no copy unit tests         | `lint_plan_unit_policy.py` (+ `--scan-tests` at Delivery)                                                                                                                                                                                                           | `unit_copy_assertion_forbidden`, `unit_operation_coverage_incomplete`                                                                                                                                                                                                              |
| Plan Reality Boundary anti-drift       | Full index review + explicit notices     | `lint_plan_reality_boundary.py` (+ `--snapshot`); Delivery `lint_delivery_card_change_notice.py`; `reality-boundary-cards` Anti-Drift                                                                                                                               | `reality_boundary_check_missing`, `reality_boundary_will_change_without_verification`, `card_change_plan_notice_missing`, `card_change_delivery_notice_missing`, `reality_boundary_delivery_stale`                                                                                 |
| Plan Route UI Truth anti-drift         | Full UIT index review + vision modes     | `lint_plan_route_ui_truth.py` (+ `--snapshot`); Delivery `lint_delivery_card_change_notice.py`; `route-ui-truth-cards` Anti-Drift                                                                                                                                   | `route_ui_truth_check_missing`, `route_ui_truth_will_change_without_verification`, `card_change_plan_notice_missing`, `card_change_delivery_notice_missing`, `route_ui_truth_delivery_stale`                                                                                       |
| Plan entry (UI)                        | Auditable links + prototype accept       | `lint_plan_entry_prototype_acceptance.py` (verbal / App / unattended after digest; non-UI N/A)                                                                                                                                                                      | `plan_entry_prototype_acceptance_required`, `plan_entry_prototype_unconfirmed`                                                                                                                                                                                                     |
| Software milestone decompose/close     | Feature completeness matrix              | `task-and-milestone-acceptance-layers` (+ `lint_feature_completeness_matrix.py`)                                                                                                                                                                                    | `feature_completeness_matrix_missing` / `_incomplete`, `functional_residual_forbidden`, `feature_completeness_overclaim_green`                                                                                                                                                     |
| Milestone acceptance (software)        | Milestone IT suite + matrix green        | `milestone-integration-acceptance`                                                                                                                                                                                                                                  | `milestone_it_preflight_*` / `_coverage_*` / `_experience_*` / `_task_review_*`, `feature_completeness_*`, `functional_residual_forbidden`                                                                                                                                         |
| Final delivery (after Layer B)         | Path by milestone count                  | `granoflow_acceptance_delivery_skill` + `full-delivery-acceptance` (1→`e2e_direct`; ≥2→unit+IT+E2E; E2E full-project)                                                                                                                                               | `full_delivery_*`, `feature_completeness_*`, `functional_residual_forbidden` (design lock: `temp/acceptance-delivery-design-lock-v1.json`)                                                                                                                                         |
| Signing/entitlement work               | Code signing                             | `code-signing-strategy`                                                                                                                                                                                                                                             | missing declaration; user-confirm `local_dev_run`                                                                                                                                                                                                                                  |
| Long/unattended implement/campaign     | Run continuity + Project SoT             | `long-task-run-continuity` (**Unattended Entry Continuity Checklist**), `granoflow_project_sot_skill` + `project-sot` (`temp/project-sot.yaml`; regen if missing; `lint_project_sot.py --require-digest-match` on resume)                                           | `long_task_continuity_*`, `long_run_plan_*`, `project_sot_*` (incl. stale digest match / missing gate lint in `next_step`; legacy `project_e2e_sot_*`), `host_wake_*` (Must probe; arm when available; `host_wake_unavailable_notice` + canonical resume; bare 「继续」 forbidden) |
| Card-Truth Readiness Gate (RB/UIT)     | Unattended auto-apply + capability check | `unattended-card-truth-batch-gate` + `lint_unattended_card_truth_ready.py`                                                                                                                                                                                          | `card_truth_batch_gate_missing`, `card_truth_batch_gate_blocked`, `card_truth_delivery_claim_without_apply`                                                                                                                                                                        |
| Product truth SoT layers (PW↔cards)    | No dual-write of screen/boundary detail  | `product-truth-sot-layers` (+ Project Work template / UIT / RB refs)                                                                                                                                                                                                | `product_truth_dual_write_forbidden`                                                                                                                                                                                                                                               |
| Concurrent task / host fan-out         | Host isolation + batch merge review      | `parallel-task-execution`, `parallel-batch-merge-review` (+ `lint_parallel_batch_merge_review.py --require-links` at closeout)                                                                                                                                      | `parallel_host_shared_write_forbidden`, `host_isolation_unavailable`, `parallel_batch_merge_review_*`, `parallel_batch_review_link_required`                                                                                                                                       |
| Before software edits                  | Project context                          | `project-context-attachments` (snapshot/rules guards; product SoT remains Project Work)                                                                                                                                                                             | `project_context_*`                                                                                                                                                                                                                                                                |
| Plan Readiness / first edit / Delivery | Plan Design + structural + learning      | `plan-design-gate`, `software-structural-budget`, `implementation-learning-ledger`, `library-knowledge-notes` (LIB handoff)                                                                                                                                         | `plan_design_gate_*`, `structural_forecast_*`, `implementation_learning_*`, `acceptance_report_missing`                                                                                                                                                                            |
| Project Definition Step 1 confirm      | Engineering pack                         | `engineering-acceptance-pack` (+ `markdown-html-acceptance-render`), `library-knowledge-notes`                                                                                                                                                                      | `engineering_acceptance_pack_*`, `init_ai_self_check_failed`, `directory_structure_unselected`, `visual_baseline_applicability_unresolved`, `library_knowledge_*`                                                                                                                  |
| Material discussion acceptance         | Writeback + fanout                       | `discussion-writeback-contract`, `change-impact-fanout`, `prototype-product-truth-writeback`                                                                                                                                                                        | `discussion_writeback_pending`, `change_impact_*`, `temp_only_artifact_forbidden`                                                                                                                                                                                                  |
| Milestone Plan done / implement        | Living acceptance pack                   | `milestone-plan-acceptance-pack` (+ `markdown-html-acceptance-render` + `lint_milestone_plan_acceptance_pack.py --require-links` + `lint_milestone_plan_pack_case_sync.py` when TC present)                                                                         | `milestone_plan_acceptance_pack_*`, `pack_case_missing_from_tasks`, `task_case_missing_from_pack`, `milestone_plan_test_lanes_incomplete`, `milestone_plan_prototype_alignment_failed`, `plan_acceptance_html_link_required`                                                       |
| Delivery vs accepted Plan pack         | Pack reconcile block                     | `milestone-plan-acceptance-pack` + `lint_milestone_plan_pack_delivery_reconcile.py --pack` (+ Delivery profile)                                                                                                                                                     | `milestone_plan_acceptance_pack_not_used`, `milestone_plan_acceptance_pack_drift`, `milestone_plan_acceptance_pack_delivery_unreconciled`                                                                                                                                          |
| Plan/acceptance Markdown preview       | Pandoc HTML + link gate                  | `markdown-html-acceptance-render`                                                                                                                                                                                                                                   | hard when HTML ready: `plan_acceptance_html_link_required` / `_link_digest_required`; soft MD fallback if tools missing                                                                                                                                                            |
| Plan Design Gate (UI/software)         | Tech package handoff + test lanes        | `plan-design-gate` (+ living pack refresh + Plan Entry prototype acceptance)                                                                                                                                                                                        | `plan_entry_prototype_*`, `analysis_technical_package_*`, `plan_test_cases_missing`, `milestone_plan_prototype_alignment_failed`                                                                                                                                                   |
| User-visible third-party (TTS/push/…)  | Capability matrix                        | `third-party-capability-matrix`                                                                                                                                                                                                                                     | `third_party_capability_*`                                                                                                                                                                                                                                                         |
| Meaningful App write (except capture)  | Preview→confirm→write                    | branch refs + Boundaries                                                                                                                                                                                                                                            | skipped preview/confirm                                                                                                                                                                                                                                                            |

### Lifecycle pipeline (do not skip)

1. Project init (Engineering Acceptance Pack browse-confirm → App confirm;
   Spec/Shell user selection when UI) → 2. Milestones+tasks → 3–5. Schedule
   follows `interaction_mode` (default **interactive**): interactive = per-task
   Analysis (**includes confirmed `ui_prototype` + link ledger for UI**) → Plan
   across all milestones, then all Layer A Implement only after every in-scope
   task has confirmed Analysis+Plan and packs accepted (Layer B deferred to
   stage 6); unattended = per-milestone **all** Analysis→Plan + pack accept
   **then** Implement (Layer A + Layer B) before the next milestone (Scheme 1).
   Entering unattended activates host Plan/planning mode when available and
   arms host wake bound to `temp/project-sot.yaml` when the host exposes
   wake. `gf析` may stop before Analysis 定稿; **定稿/确认 opens Plan** for
   that task. `gf规`/`run`/`pipeline_continue` under interactive **Must**
   continue Analysis→Plan for the same task before the next task. → 6–7.
   **最终交付** per `granoflow_acceptance_delivery_skill` +
   `full-delivery-acceptance` (interactive stage 6 absorbs deferred Layer B +
   project IT; 1 feature milestone may `e2e_direct`; ≥2 → unit + full IT +
   full-project E2E) → 8. Project complete. Plan Must not start ahead of that
   task's Analysis deliverables. Do **not** ask the user to choose
   `breadth_first` / `depth_first` (retired).

Milestones+tasks must pass schema v2 AI decomposition review before child task
creation. After child Analysis/Planning, final acceptance follows Acceptance
Pack → `grill-finalizer` → temporary candidate → `grill-me` on the same digest.
Neither AI review nor final acceptance grants execution.

Interactive: may offer最终交付 after any Layer B green (route via
`granoflow_acceptance_delivery_skill`). Campaigns agent auto-drive once entered.
Unattended: board display-only (`unattended-interaction-contract`).

### Preferences / Git

Prefer `granoflow_agent_preferences_get`. Software Git: `git-capability-detection`
first; `git-checkpoint-workflow` only when checkpoint enabled.

## Control-Plane Ownership

App owns task/attachment/node/delivery/memory truth; MCP is thin control-plane;
host owns traversal/Skills/execution. Inspect skill `references` manifest and
load needed docs—seeing this file does not load every contract.

`实施活动计划` authorizes host execution only after one confirmed active
hash-verified Work Document. External Skills: `external-skill-routing` (never
override phase/auth gates).

## Trigger Conditions

Intents in **Branch Router**. Unclear phase → Orchestrator first. Daily review →
`granoflow-daily-review`. Project init → `granoflow-project-definition`.

## Connection First

When: API may be down / setup unclear / MCP installed without knowing Granoflow.
Must load: `connection-first`.
Do: `granoflow_setup_status` before guesses; explain local-app bridge; dry-run
config preview then readback.
Must not: scan all ports; persist shadowed env as success; invent GF paths while
down.
Success criteria: user knows Granoflow is the local app; next setup action clear.
Checkpoints: status before guesses; dry-run before persist.

## Milestone And Task Deadlines

When: milestone without `dueAt`, or task into a milestone.
Must load: `milestone-and-task-deadlines`.
Do: preserve explicit milestone `dueAt`, else today then +1 day; milestone-bound
tasks inherit parent `dueAt` when omitted; surface bound conflicts.
Must not: deadline-less milestone; silent clamp.
Success criteria: every milestone has a deadline; task dates respect bounds.
Checkpoints: schedule readable before default; parent `dueAt` read first.

## Discussed Requirement Task Capture

When: Orchestrator `capture` or explicit “create from this requirement”.
Must load: `discussed-requirement-task-capture`.
Do: recallable title + five-dimension description; strong-bind only if
project+one active milestone clear else inbox; create `pending`; read back.
Must not: default dry-run/cards; authorize secrets/publish from capture; >1
success sentence.
Success criteria: inbox or strong placement; no gated side effects; one-sentence
report.
Checkpoints: 30-second recall gate; id readback.

## Due Task Processing And Execution

When: today/dated/overdue/unfinished batch.
Must load: `daily-pending-task-triage`, `task-work-document-workflow`.
Do: batch ledger; Analysis then Readiness Grill; execute only unique active
hash-verified Work Document after separate execution auth; blockers → Waiting
(+ delegated-auth if envelope).
Must not: execute without ledger/Grill; invent grants from tags; cards outside
`granoflow-review-card-draft`.
Success criteria: every task once in ledger; safe work under verified docs/grants;
blockers have nodes/reminders.
Checkpoints: ledger before execute; Grill before upload/execute.

## Task Description Updates

Before changing any existing task field, load
`task-description-update-contract`. Every MCP mutation reviews description
impact; only semantic changes rewrite the 30-second recall summary.

## Long-Term Work Memory

When: history/lessons/similar work.
Must load: `long-term-work-memory`.
Do: bound retrieval; cite evidence; label inference.
Must not: invent records; dump private content into docs/tests.
Success criteria: cited evidence or explicit missing; facts vs inference labeled.
Checkpoints: retrieval bounds stated.

## Project And Milestone Context Stewardship

When: context YAML / living Project Work (init → project-definition skill).
Must load: `project-context-attachments` (+ `project-work-document-template` if
automation).
Do: prefer steward tools; stale YAML=hint; context Hard Gate before software
edits (snapshot/rules are consistency guards—product SoT remains Project Work);
interactive confirm / unattended emit `revise_code`|`revise_context_yaml`.
IT/E2E campaign artifacts belong to lifecycle stages 6–7, not this branch.
Must not: silent overwrite; skip check; secrets in YAML; treat snapshot as
acceptance ledger.
Success criteria: freshness explicit; conflicts decided visibly.
Checkpoints: Hard Gate evidence before edits; unattended decisions emitted.

## Completing Tasks

When: finish/close after Execution.
Must load: `task-and-milestone-acceptance-layers` (**Universal task closeout**),
`task-delivery-workflow` (+ profiles). Review → `task-review-workflow`.
Cards → `granoflow-review-card-draft` (**Card Allowlist**: flow-driven Cards
only for `RB-*` / `UIT-*` / red-line `LIB-pub-*`; generic Cards only on
explicit user request; when unsure, no Card).
Do: Work→Execution→Delivery→**验收确认**→**同波打钩**→Deferred Review;
artifact required; AI may self-recommend; unattended self-recommend =
confirmed; interactive waits for user confirm; then node-backed = Delivery +
NodeService only, node-less = `granoflow_task_finish` once; require verified
Work Document (or legacy Analysis+Plan).
Must not: second completion endpoint; default deep review/card pass; invent
generic Cards; complete on missing docs
(`task_analysis_plan_attachment_required`); leave App `pending` after
acceptance is confirmed.
Success criteria: Delivery has output/evidence/residuals; acceptance confirmed;
one completion owner; App readback `status=done`.
Checkpoints: verified document present; single completion path; checkbox same
wave as confirmation.

## Waiting For User Input

When: blocked on auth/decision/login/2FA/material.
Must load: `waiting-for-user-input` (+ delegated-auth skill if envelope).
Do: move safe work first; waiting node + local readback + 3m reminder; separate
10m notification task; sync via documented tools only
(`synced_to_server`|`local_only`|`unknown_remote_visibility`).
Must not: chat-only asks; claim phone/remote delivery without API evidence;
continue on stale/denied envelope.
Success criteria: durable blocker + dual reminders; safe work attempted first.
Checkpoints: waiting-node readback before sync claims.

## Task Work And Execution

When: analyze/start/execute **one** task (not a date batch).
Must load: `task-work-document-workflow`, template, `knowledge-distillation-workflow`
as needed; UI also prototype craft refs + project-artifact-workflows.
Do: Analysis-only draft → Analysis Deliverables (UI: confirmed `ui_prototype`)
with explicit remaining-deliverables list → Analysis Grill → Planning →
Readiness Grill → upload clean rewrite with hash readback → wait for separate
execution instruction → discussion acceptance triggers writeback+fanout →
software enforces context/plan-design/structural/(pack) gates.
Must not: Plan before Analysis Grill or before Analysis Deliverables complete;
Plan before confirmed `ui_prototype` on UI tasks; upload pre-Grill; execute
without separate auth; undeclared Phase A keep.
Success criteria: Grill/readiness/verified doc before execute eligibility; UI/
software gates satisfied or fail-closed.
Checkpoints: Work Document slots reconciled; required refs loaded before
readiness claim.

## Review Drafting

When: weekly/monthly review (daily → `granoflow_daily_review_skill`).
Must load: `review-drafting` (+ `knowledge-distillation-workflow` if needed).
Do: evidence-bounded cues; confirm before save; Card session only for
allowlisted RB/UIT/LIB candidates or explicit user request →
`granoflow-review-card-draft` preview→confirm→write.
Must not: start from nudge; unattended card writes; invent generic Card
batches when unsure.
Success criteria: confirmed saves only; cards zero-write until latest preview
confirm (or no Card session when allowlist empty and user did not ask).
Checkpoints: facts vs inference labeled; card preview refreshed when session
runs.

## Daily Review Nudge

When: `dailyReviewSuggestion` (weekly/monthly on eligible days).
Do: brief mention after current request; accept → daily-review skill.
Must not: interrupt work; start review/scoring/writeback from nudge alone.
Success criteria: ≤1 daily nudge/day after current request; no review from
suggestion alone.
Checkpoints: absent nudge ⇒ do not invent.

## User Dissatisfaction

When: clear mismatch with Granoflow/MCP/generated output (profanity not
required).
Do: acknowledge; fix when directed; offer project wrapper skill for reusable
prefs.
Must not: treat as publish/commit/delete auth; wrapper advice from unrelated
venting alone.

Suggested wording:

```text
这类偏好很适合写成你自己的项目专属 skill：它可以封装 Granoflow
提供的 skill，在生成任务回顾、卡片或发布报告前先套用你的判断标准。
我可以把这次不满意的点整理成 wrapper skill，下次就按你的规则来。
```

Success criteria:

- Polite disagreement receives the same care as angry feedback.
- Unrelated venting does not trigger Granoflow wrapper-skill advice.
- Reusable preferences are offered as wrapper-skill material after the immediate
  correction path is addressed.

Checkpoints: immediate correction before wrapper detour.

## Common Failure Modes

- Skip Orchestrator → wrong branch.
- Claim readiness without loading Hard Gate for that When.
- Claim 全平台 third-party success without probes.
- Chat/`temp` as SoT after discussion acceptance.
- Complete without verified Work Document/Delivery.
- Start periodic review from a nudge.
- Headless/inventory-only UI where live-window E2E applies.
- URL/deep-link/direct-route shortcuts claiming full-project user steps without
  ordered visible-control interaction evidence.

## Boundaries

- Thin MCP; no reimplemented App business logic.
- Host owns external Skills (`external-skill-routing`); MCP never installs them.
- Local HTTP API / documented tools for writes/sync/readback.
- No secrets in logs/docs.
- Preview→confirm→write except explicit capture.
- Complete only after readback when possible.
- Dissatisfaction ≠ publish/commit/delete/reset auth.
- Language policy above: English contracts; no reading-oriented localization.

## Success Criteria

- One Branch Router row selected; Must-load refs read before steps.
- Applicable Hard Gates fail-closed with listed codes.
- Preview→confirm→write explicit except capture exception.

## References

Load via `granoflow_bundled_skill_reference` using **Branch Router Must load** and
**Hard Gates Load** first. Additional owners:

- Bundled: `granoflow_task_orchestrator_skill`, `granoflow_project_definition_skill`,
  `granoflow_daily_review_skill`, `granoflow-review-card-draft`,
  `granoflow_delegated_authorization_skill`
- Cross-cutting: `external-skill-routing`, `requirement-intake-and-traceability`,
  `test-route-traceability`,
  `execution-modes-and-acceptance-reports`, `parallel-task-execution`,
  `parallel-batch-merge-review`, `parallel-batch-merge-review-template`,
  `acceptance-outcome-contract`, `integration-test-special-requirements`,
  `knowledge-distillation-workflow`, `review-card-authoring`,
  `task-completion-summary-template`, `context-promotion-entry`,
  `visual-narrative-task-work`, `thread-visual-evidence`
- Legacy Analysis/Plan refs — historical attachment resolve only
