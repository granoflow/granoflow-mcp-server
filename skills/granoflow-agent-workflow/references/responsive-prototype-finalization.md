# Responsive Prototype Finalization

This reference owns the Project platform contract, layout-family coverage,
task prototype option selection, final Prototype Bundle, Widget Catalog
promotion, and rendered implementation fidelity.

Load it during Project Definition for every UI software project, before
authoring or reopening a task `ui_prototype`, before Analysis confirmation, and
before UI Task Delivery.

For task-level content and behavior authority, also load
`task-analysis-finalization` before authoring HTML. This reference owns visual
and responsive finalization; it does not own screen content or logical
technical reconciliation.

Historical completed records remain readable. A new UI task, reopened task, or
continued prototype modification must use the contracts below.

## Authority And Invalidation

- Project Work `platform_support_matrix` is the product source of truth for
  supported platforms, exact versions, device classes, orientations, window
  constraints, layout families, and reference viewports.
- The confirmed Design Baseline owns global Spec, Shell, tokens, and initial
  widgets.
- The accepted Screen Content Contract owns task screen fields, actions,
  states, permissions, navigation, and data sources.
- The task Prototype Bundle owns the finalized HTML and interaction truth for
  every task-owned surface and required layout family.
- Project `widgets.yaml` owns reusable widget contracts. Visual truth remains
  in confirmed prototypes.
- Any platform-matrix digest, Baseline SHA, required layout family, variant
  HTML, screenshot, screen responsibility, or Widget Catalog input change
  invalidates the old Prototype Bundle.
- A platform-matrix change fans out to affected Baseline, Milestone AI review,
  task prototypes, Planning, and Milestone Plan Acceptance Packs.
- None of these confirmations grants implementation, commit, push, publish, or
  deploy authorization.

## Project Platform Support Matrix

Every UI software project records `ios`, `android`, `macos`, and `windows`,
including explicit `not_supported` rows. Web, Linux, and other platforms may be
added.

Supported rows must identify:

- minimum OS/runtime version and applicable target SDK/API;
- required validation versions;
- device classes and architectures;
- layout-family ids and orientation support;
- desktop window constraints when applicable;
- product-document, user-decision, or official-source evidence.

Each layout family defines a stable id, orientation, reference viewport width,
height, and DPR. `primary_layout_family` is used for option selection.

When product sources are incomplete, Project Definition recommends exact
values. Interactive mode waits for the user. Explicit unattended mode records
`unattended_auto_adopted` and `accepted_by: unattended_grant`; it never claims
user confirmation.

The canonical matrix digest is SHA-256 over compact, recursively key-sorted
JSON after removing only `matrix_sha256`.

## Project Definition Selection

Design Spec follows the product-fitted two-round HTML contract: a
six-dimension chooser, then three complete candidates by default or justified
two. App Shell selection presents its triad in the primary layout family.
After selection, expand only the winner to every required layout family and
obtain final Baseline confirmation for the complete package.

Single-layout selection may also be final confirmation only when the selected
artifact is already complete and its hash does not change. Multi-layout
projects and any post-selection refinement require a second final package
confirmation.

Visual lot draws use `draw_visual_lots.py`. Initial batches require distinct
recorded ids. A request for a new batch requires `--dedupe ledger --record` and
must be disjoint from machine-local history. Revising an option keeps its
existing lot id. A finalized lot receipt must also contain unique artifact
hashes and `materially_distinct_status: passed`.

## Task Analysis Option Selection

Task prototypes inherit the exact platform matrix, Baseline SHA, current
Widget Catalog SHA, and confirmed sibling chrome vocabulary. They never draw a
new visual seed or reopen the Design System.

Before option HTML, they also require a passed
`ui_component_effect_matrix_v1` and `task_ui_skill_pipeline_v1`. Their canonical
SHA values become Prototype Bundle inputs; any matrix, provider-output,
Baseline, Catalog, or platform input change invalidates the old Bundle.

They also inherit the passed Logic Draft and accepted Screen Content Contract
digests. User feedback that changes content or behavior must update those
contracts before regenerating HTML.

Before HTML, use the existing mainstream-first candidate protocol. Default to
two complete, functionally equivalent page expressions. Three are allowed only
when all three are materially distinct, feasible, parity-safe local
expressions and `option_count_reason_code` is one of:

- `three_viable_patterns`
- `cross_form_factor_tradeoff`
- `high_risk_interaction_choice`

Every option has the same capabilities, data fields, required states, product
behavior, and locked design system. Options differ only on declared legal
presentation axes.

Show options in `primary_layout_family`. After selecting one, expand that
option to all required layout families. Do not present portrait and landscape
as different products or different feature sets.

## Final Prototype Bundle

Use schema `granoflow_responsive_prototype_bundle_v2` for active UI work. It
records:

- Logic Draft and Screen Content Contract digests;
- platform matrix, Baseline, and Widget Catalog input digests;
- option-count decision, primary-layout options, and selected option;
- one finalized variant for every required layout family;
- exact viewport, HTML, screenshot, and SHA references;
- functional, data, state, navigation, and widget cross-layout checks;
- Widget Promotion Ledger reference;
- Task UI skill pipeline and component/effect matrix digests;
- final acceptance state and canonical bundle digest.

The canonical bundle digest excludes `bundle_sha256`,
`final_acceptance_status`, `accepted_by`, and `authorization_effect`. Every
other bundle change invalidates acceptance.

Interactive multi-layout confirmation shows every final variant and waits.
Explicit unattended mode states each recommendation and reason, then records
`unattended_auto_adopted` with `accepted_by: unattended_grant`.
`authorization_effect` is always `none`.

Analysis cannot pass while a required layout family is missing, a cross-layout
check is incomplete, the Bundle digest is stale, or final acceptance is
missing.

Historical completed v1 Bundles remain readable under
`historical_read_only`. Reopening or continuing prototype work requires v2 and
fails closed as `responsive_prototype_bundle_upgrade_required`.

## Widget Promotion

Before task prototype authoring, read current project `widgets.yaml` and record
its App readback SHA. The same role must reuse the catalog widget.

After final prototype confirmation:

1. Record every used widget as `reused`, `promoted`, or `task_local`.
2. Promote every new reusable role into the same project `widgets` slot.
3. Give every `task_local` decision a non-empty rationale.
4. Read back the updated catalog and require `catalog_after_sha256` to equal
   `app_readback_sha256`.
5. A change to a locked widget's visual system, Shell role, or token contract
   requires a new Design Baseline version. Adding a new role does not.

Widget variants identify `layout_family_id` and `platform_ids`; platform
adapters remain variants of one project role rather than parallel design
systems.

Analysis closes only after the Widget Promotion Ledger passes or is honestly
not applicable. The next task must load the resulting catalog SHA.

## Rendered Fidelity

Reference viewports target pixel-level high-fidelity reproduction. Other sizes
follow the confirmed responsive mapping. Platform-native differences require
evidence and an approved exception.

Phase A remains a code-reading comparison before unit tests. After the UI is
runnable and before Task Delivery, run the rendered fidelity loop for every
Prototype Bundle variant:

1. Capture the implementation at the exact viewport and DPR.
2. Record prototype and implementation screenshot refs and SHA values.
3. Record the configured numeric difference metric, value, and project
   threshold.
4. Require the numeric result and AI visual reviewer to pass.
5. Disposition every material region difference.
6. Require platform-native exceptions to cite the platform contract and be
   explicitly approved.
7. Revise and recapture until every required layout family passes.

This task-level loop does not replace Milestone/E2E Phase B.

## Fail-Closed Codes

- `platform_support_matrix_required`
- `platform_support_matrix_incomplete`
- `platform_support_matrix_digest_mismatch`
- `visual_lot_receipt_required`
- `visual_lot_refresh_overlap`
- `visual_lot_artifacts_not_distinct`
- `responsive_prototype_bundle_required`
- `responsive_prototype_bundle_upgrade_required`
- `responsive_prototype_content_mismatch`
- `responsive_prototype_layout_missing`
- `responsive_prototype_option_count_invalid`
- `responsive_prototype_cross_layout_failed`
- `responsive_prototype_digest_mismatch`
- `responsive_prototype_final_acceptance_required`
- `widget_promotion_required`
- `widget_catalog_stale`
- `widget_promotion_readback_mismatch`
- `widget_locked_contract_baseline_reopen_required`
- `task_ui_skill_pipeline_required`
- `task_ui_skill_capability_missing`
- `task_ui_skill_invocation_unsafe`
- `task_ui_skill_evidence_missing`
- `ui_component_effect_matrix_required`
- `ui_component_effect_incompatible`
- `ui_component_effect_user_decision_required`
- `ui_component_effect_high_cost_unjustified`
- `ui_component_effect_fallback_missing`
- `ui_component_effect_ranking_invalid`
- `ui_widget_reuse_bypassed`
- `rendered_fidelity_required`
- `rendered_fidelity_layout_missing`
- `rendered_fidelity_numeric_failed`
- `rendered_fidelity_ai_failed`
- `rendered_fidelity_exception_unapproved`
