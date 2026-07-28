# Hard Constraints (thread-confirmed)

Read this when verifying fail-closed rules before Project Work confirm, Baseline
visual confirmation, initialization Done, or task `visualConfirmed=true`.

Detail and procedures live in `project-definition-interaction.md` and
`project-artifact-workflows.md`. This file is the non-drop checklist for polish
and review.

## Mode Gate

- Default `executionMode: interactive`. Never infer unattended from activation
  phrases alone.
- Interactive: **ask → recommend → wait**. Drafting is allowed; confirm /
  Baseline accept is not automatic.
- Never auto-accept Baseline+Shell in interactive mode.
- Unattended only after explicit user declaration; then adopt recommendations
  except real blockers from `unattended-interaction-contract`.
- Entering / switching into unattended: run **External Capability Inventory**
  (secrets, payment, push/publish/deploy, destructive Git, human/device gates)
  and batch grant / exclude / `interaction_required` **early**. Mid-run
  discoveries go to `deferred_external_work` and are scheduled **late** without
  blocking other solvable work (see unattended contract).

## Design-first (do not invert)

- Previews express user-visible demand; tech follows. Undeliverable commitment →
  revise design/product, do not fake capability.
- Not a global “tech/data model before any preview” rule.

## Product truth on prototypes

- Before Preview Gate wait / `visualConfirmed=true`, prototypes must not show
  capabilities or states forbidden or unauthorized by confirmed product docs /
  Project Work → `prototype_product_truth_violation`.

## High-risk feasibility

- Platform-coupled / easy-to-overpromise screens: Tech Note may follow preview
  in parallel; **Readiness** requires a written conclusion (as drawn /
  degraded / revise design) → else `high_risk_feasibility_unresolved`.
- Ordinary Baseline chrome/IA screens: no Tech Note required.

## Prototype Preview Gate

- Every previewable HTML unit (or interactive option batch) gets a **clickable**
  link.
- Interactive: stop and wait (option batches: all links, one wait).
- Unattended: non-blocking notice + ledger; closing **Prototype Link Digest**
  required (`prototype_link_digest_required`).
- Skipping interactive wait → `prototype_preview_review_required`.
- Persist `granoflow_prototype_link_ledger_v1` and lint with
  `lint_prototype_link_ledger.py --require-complete` before UI Analysis
  confirmation. Missing/empty HTML files, non-absolute `file://` links, or
  digest without Markdown links → `prototype_link_file_missing` /
  `prototype_link_not_absolute` / `prototype_link_digest_required` /
  `prototype_link_ledger_incomplete`. SHA/id-only confirmation is not enough.

## Plan soft-merge + living acceptance pack

- `gf析` stops at Analysis; `gf规` / `run` auto-continue into per-task Plan after
  Analysis deliverables are complete (no courtesy “开始 Plan” pause).
- Keep task-level Plan Design Gate; milestone Plan acceptance pack is a **living
  draft** refreshed after each task Gate, with HTML basename + `file://` links
  and `prototype_alignment` vs confirmed prototypes.
- Software UI pack closeout requires Markdown test lanes `unit` + `integration`
  - `e2e` (author only; suites still run in Layer B / final-delivery campaigns).
- Lint: `lint_milestone_plan_acceptance_pack.py --require-links`.

## Plan cases must be implemented (no silent drop)

- Every authored Plan / pack Case ID Must appear in
  `plan_case_implementation` before the matching gate:
  - Layer A: `unit`/`widget` → on-disk `test_ref` bound to Case ID;
    `integration`/`e2e` → `scheduled_campaign` + `campaign_ref`.
  - Layer B: `integration` → `executed`.
  - Final-delivery e2e_campaign: `e2e` → `executed`.
- Lint: `lint_plan_case_implementation.py --gate … --workspace …`.
  Gaps → `plan_case_implementation_gap` / `plan_case_test_ref_missing` /
  `plan_case_test_ref_unbound`.

## Prototype → Contract operation coverage

- Confirmed HTML Must not carry `action:` / `navigation:` `data-contract-ref`
  values absent from the Screen Content Contract
  (`prototype_contract_orphan_ref`).
- Interactive controls Must use `data-contract-ref` or
  `data-contract-ignore` (`prototype_interactive_unmarked`).
- Lint: `lint_contract_prototype_semantics.py` with `--html` (Analysis /
  rematch / product-truth writeback). Contract → prototype coverage remains
  required as before.

## Plan Entry — prototype acceptance

- Non-UI (`prototype_requirement: not_required` / N/A): no prototype gate.
- UI: before Plan / soft-merge into Plan, auditable Prototype Link Digest
  (`file://`) **then** acceptance (`verbal` | `app_visual_confirmed` |
  `unattended_auto_accept`). Unattended auto-accept only after digest.
- Lint: `lint_plan_entry_prototype_acceptance.py`. Fail closed
  `plan_entry_prototype_acceptance_required` /
  `plan_entry_prototype_unconfirmed`.

## Unit tests: behavior per operation — not copy

- **Forbid** unit tests whose purpose is asserting user-visible copy/text
  presence (`find.text` / `getByText` / `asserts: copy_presence`).
- **Require** ≥1 `unit` Plan case per in-scope operation/action
  (`operation_id` ← Screen Content Contract `actions[].action_id`).
- Lint: `lint_plan_unit_policy.py` (+ `--scan-tests` at Delivery).
  Fail closed `unit_copy_assertion_forbidden` /
  `unit_operation_coverage_incomplete`.
- Reality Boundary Plan half: `lint_plan_reality_boundary.py` (+ `--snapshot`
  when available). Fail closed `reality_boundary_check_missing` /
  `reality_boundary_will_change_without_verification` /
  `card_change_plan_notice_missing`.
- Card change Delivery notice (any review card write):
  `lint_delivery_card_change_notice.py`. Fail closed
  `card_change_delivery_notice_missing` /
  `reality_boundary_delivery_stale`.
- Product truth dual-write: Project Work must not host screen visual / status
  quo / boundary **detail** that also lives on UIT/RB cards (PW keeps
  inventory + short declared `ui_details` + `uit_fact_id`/`rb_fact_id`
  pointers). Fail closed `product_truth_dual_write_forbidden` (document gate;
  see `granoflow-agent-workflow/product-truth-sot-layers`).

## Design Spec / Shell

| Mode        | Design Spec                                                                                                                                                             | Shell                                                                                   |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Interactive | Product-fit envelope → six-dimension HTML chooser → three complete HTML Specs by default, or justified two; one true-random master seed with reproducible derived seeds | Mainstream-first ≥5→**promote 3**, then triad chrome cards; all **embed selected Spec** |
| Unattended  | Mainstream-first→one `spec_match` via true-random draw                                                                                                                  | Mainstream-first→one `shell_match` embedding Spec (no palette seed)                     |

- **Candidate protocol (hard):** load
  `granoflow-agent-workflow/prototype-expression-brainstorm` before Spec/Shell
  HTML. Build **mainstream product references** first (`scope_mode`
  `same_category`|`capability_match`; default capability when unsure);
  brainstorm backfill **only** when mainstream `<5`. Spec/Shell promote count
  is **3** (not task AB=2). Offering Spec/Shell as dual-only →
  `prototype_option_promote_count_mismatch`. Candidate analysis does **not**
  replace lot draw. Lint with
  `lint_prototype_expression_brainstorm.py`.
- Complete Design Spec candidate = **Style Guide / Design Tokens board** (Colors,
  Typescale, Spacing, Grid/Breakpoints, Component states, Shadows&Radius)—**not**
  a full journey-screen gallery. One controlled product-component composition
  is required. Wrong shape → `design_spec_wrong_artifact_type`.
- App Shell artifact = **product-near chrome + primary surface** that already
  **loads selected Spec tokens** and aims for final-product effect under
  contract fidelity—**not** grey wireframes. Fail closed
  `shell_spec_tokens_missing` / `shell_wireframe_only`.
- Shell renders only the orientations required by `platform_support_matrix`.
  Every required portrait and landscape layout includes both a top bar and a
  bottom navigation bar. The selected variants become
  `app_shell.top_bar` / `app_shell.bottom_navigation` Widget Catalog entries.
- **Init HTML budget (hard):** Design Baseline package at Project Definition =
  Spec Style Guide + App Shell only. Do **not** ship every
  `screen_coverage` page as init HTML. Per-screen hi-fi → task/milestone
  `ui_prototype`. Fail closed when Spec is used as a walkthrough gallery →
  `design_spec_wrong_artifact_type`.
- **Screen detail registration (hard):** before
  `product_spec_coverage.status: ready`, adopt
  `screen_detail_registration` and register durable `ui_details` when product
  docs / user stories state them. Design-truth priority (high→low):
  `user_confirmed` → `from_product_doc` → `from_user_story` → `inferred` →
  `ai_live_inference`. Lower Must not override higher without user confirm.
  Fail closed `screen_detail_registration_missing` /
  `screen_ui_details_source_invalid`.
- **Lot draw (hard):** the Spec master seed and Shell chrome ids Must come from
  `scripts/draw_visual_lots.py` (**true random** only—no classroom salt /
  `--from`). Design Spec candidate seeds derive from the recorded master seed.
  Hand-invented `seed-*` / chrome ids → `design_spec_seed_not_drawn`.
- **Request-more / 换新批:** re-draw with `--dedupe ledger` against the
  machine-local visual-lot ledger (`~/.granoflow/visual-lot-ledger.json` by
  default)—stronger than same-run-only. Skipping dedupe →
  `visual_lot_dedupe_required`. Pool exhausted → `visual_lot_exhausted`.
- **Revise-on-option / 在某套上改:** edit that option in place; do **not**
  re-draw Spec seed or change Shell chrome primary axis unless the user
  explicitly asks for a structural change.
- Fail closed: `design_spec_triad_required`, `design_spec_seed_collision`,
  `design_spec_seed_not_drawn`, `design_spec_wrong_artifact_type`,
  `shell_triad_required`, `shell_seed_collision`, `shell_spec_mismatch`,
  `shell_spec_tokens_missing`, `shell_wireframe_only`,
  `prototype_option_brainstorm_*`, `prototype_option_mainstream_skip`,
  `prototype_option_scope_mode_invalid`, `prototype_option_backfill_unjustified`,
  `prototype_option_promote_count_mismatch`,
  `prototype_option_function_split`,
  `visual_lot_dedupe_required`, `visual_lot_exhausted`,
  `visual_lot_classroom_salt_forbidden`.
- **From Shell onward, design style converges.**
- **User-facing Preview Gate copy:** never show `seed-*` ids, internal option
  enums (`spec_match` / `ai_challenger_*`), or other agent-only jargon. Present
  plain-language choice labels + clickable links only. Seeds and option ids
  remain in Project Work / run ledger only (`design_spec_user_facing_jargon`).

## App Icon Source Gate

- When the product is a **mobile or desktop App**, load
  `granoflow-agent-workflow/app-icon-source-gate` during Step 1 and persist
  `product.app_icon` before Project Work confirm / initialization Done.
- Scan user-submitted docs for an icon. If missing in interactive mode: ask
  the user to choose `user_provided` / `ai_generated` /
  `downloaded_license_clear` and wait—never silently finalize an icon.
- Unattended with a missing icon: **recommend and auto-adopt** a source
  (default `ai_generated`; see gate), set
  `user_decision_recorded: true` + `decision_authority: unattended_grant`,
  finalize the asset, and continue. Do **not** park an interaction wait just
  to ask which source. Residual only when generation/download is externally
  impossible.
- Pure Web/CLI/library → `applicability: not_applicable` with basis.
- Lint: `lint_app_icon_source_gate.py`. Fail closed:
  `app_icon_source_gate_unread`, `app_icon_applicability_unresolved`,
  `app_icon_document_scan_missing`, `app_icon_source_unresolved`,
  `app_icon_source_lint_failed`.

## Widgets

- After Baseline visual confirmation **when**
  `visual_baseline.applicability: required`: first mandatory `widgets.yaml`
  extract (`widget_catalog_required` if missing).
- When `not_applicable`, widgets are not required for initialization Done.
- YAML = contract (identity, props, tokens, states, reuse); visuals stay in
  confirmed prototypes.
- Incremental extract after later confirmed prototypes; one current project
  slot.
- Every incremental extract records a Widget Promotion Ledger with source
  Bundle SHA, catalog-before/catalog-after SHA, and matching App readback.
- New reusable roles are promoted; `task_local` requires rationale. Changing a
  locked visual/Shell/token contract requires Baseline reopen.

## Platform And Responsive Prototype

- UI projects record explicit iOS, Android, macOS, and Windows support rows,
  exact versions, required validation versions, devices, orientations, layout
  families, and source refs.
- Shell selection uses the primary layout. Only the selected Shell expands to
  all required layout families before final Baseline confirmation.
- Task Analysis defaults to one serial page thesis refined across up to five
  drafts (`prototype-serial-revision`), not a parallel dual pick.
- Analysis cannot pass without a current responsive Prototype Bundle digest,
  every required layout family, final acceptance, and Widget promotion
  readback.
- Runnable UI cannot reach Task Delivery until every Bundle layout passes the
  numeric and AI rendered fidelity gates.

## Milestone / task authoring (task_plan)

- After Project Definition, UI portfolio authoring Must apply
  `granoflow-agent-workflow/screen-task-portfolio-coverage`: write Milestone
  Work `task_plan` (refined screens + page journeys + task summaries) with
  per-screen `split_probe`, ≥1 task per refined screen, and
  `detail_carryforward` that dispositions every in-scope Project Work
  `ui_details` row (`carried` / `deferred_out_of_milestone` / `out_of_scope`)
  before App task create. Acceptance-only skeleton coverage is not enough.
  Composition SoT is Milestone Work—not Project Work. Fail closed
  `milestone_task_plan_incomplete` /
  `milestone_detail_carryforward_incomplete` /
  `task_portfolio_screen_coverage_incomplete` /
  `screen_split_probe_incomplete`. Analysis Must not reopen ownership/split
  without reopening milestone `task_plan`. Users are not the acceptors of
  detail tables at this phase—AI self-audit + lint are.

## Task / milestone `ui_prototype`

- `derivedFrom` exact Baseline; **no** random visual seed
  (`task_prototype_seed_forbidden`).
- Reuse `widgets.yaml` same role (`widget_reuse_required`).
- **Craft Gate** before `visualConfirmed` (`task_prototype_craft_incomplete`),
  including **Baseline fit** (strict Spec tokens + Shell chrome language;
  `granoflow-agent-workflow/prototype-baseline-fit`;
  `baseline_fit_ok` + `lint_prototype_baseline_fit.py`),
  **confirmed chrome lock** (reuse vocabulary from visually confirmed sibling
  pages in the same chrome family;
  `granoflow-agent-workflow/prototype-confirmed-chrome-lock`;
  `confirmed_chrome_lock_ok` + `lint_prototype_confirmed_chrome_lock.py` when
  authorities exist),
  **product truth** (`prototype_product_truth_violation`), and
  **user-visible copy boundary**
  (`user_visible_copy_boundary_unread` /
  `user_visible_copy_boundary_violation`; checklist field
  `user_visible_copy_boundary_ok` +
  `lint_prototype_user_copy.py`).
- When iOS and/or macOS layout families use `device_shell_profile_id`, Must
  copy bundled frames and pass `lint_device_shell.py` (`device_shell_ok`;
  `granoflow-project-definition/device-shell-templates`). Hand-drawn bezels →
  `device_shell_profile_missing` / `device_shell_layout_mismatch`.
- Post-Baseline task/milestone pages Must **embed locked Spec tokens**
  (`data-baseline-tokens="locked"`) and **reuse Shell chrome language** /
  `widgets.yaml` roles. Generic parallel phone frames →
  `prototype_generic_phone_frame` / `prototype_shell_chrome_mismatch` /
  `prototype_spec_tokens_not_loaded` / `prototype_spec_tokens_drift`.
- After a chrome-family sibling is `visualConfirmed`, later pages Must reuse
  that confirmed control vocabulary (title-ico / tbtn / chip selected tint /
  pref-ico)—not invent a parallel dialect that only shares Baseline tokens →
  `prototype_confirmed_chrome_lock_*`.
- Interactive and unattended: **mainstream-reference-first** candidates (≥5;
  brainstorm backfill only when mainstream `<5`) then promote **one** serial
  thesis (`expr_a`)—see
  `granoflow-agent-workflow/prototype-expression-brainstorm`. Load
  `granoflow-agent-workflow/prototype-serial-revision`: temp brief → contract
  update → green `ui_component_effect_matrix` + `stack-realization-notes`
  (stack deliverable surface; no default Web-only showcase) → review-only
  gstack/preferred reviewers + grill self-QA → draft → post-review → revise
  for blocking only; max **5** drafts; early stop on 0 blocking; drafts 4–5
  blocking-only; each draft binds matrix + notes SHA. Interactive selection
  surface = last **≤3** drafts with **推荐** marker; single draft =
  confirm_or_revise (no forced multi-pick). Unattended auto-adopts final
  green. Lint `lint_prototype_expression_brainstorm.py`,
  `lint_stack_realization_notes.py`, and `lint_prototype_revision_ledger.py`.
- Never re-offer Design Spec labels (`delta_match` / `ai_challenger` /
  `spec_match`) as task options after Baseline lock
  (`prototype_option_design_system_reopened`).
- Fail closed: `prototype_option_design_system_reopened`,
  `prototype_baseline_fit_unread`,
  `prototype_baseline_fit_digest_required`,
  `prototype_baseline_fit_lint_failed`,
  `prototype_spec_tokens_not_loaded`,
  `prototype_spec_tokens_drift`,
  `prototype_shell_chrome_mismatch`,
  `prototype_generic_phone_frame`,
  `prototype_confirmed_chrome_lock_unread`,
  `prototype_confirmed_chrome_lock_authority_missing`,
  `prototype_confirmed_chrome_lock_drift`,
  `prototype_confirmed_chrome_lock_digest_required`,
  `prototype_confirmed_chrome_lock_lint_failed`,
  `prototype_option_brainstorm_unread`,
  `prototype_option_brainstorm_missing`,
  `prototype_option_brainstorm_incomplete`,
  `prototype_option_brainstorm_digest_required`,
  `prototype_option_mainstream_skip`,
  `prototype_option_scope_mode_invalid`,
  `prototype_option_backfill_unjustified`,
  `prototype_option_promote_count_mismatch`,
  `prototype_serial_revision_unread`,
  `prototype_revision_ledger_required`,
  `prototype_revision_max_drafts`,
  `prototype_revision_late_draft_without_blocking`,
  `prototype_revision_blocking_residual`,
  `prototype_revision_selection_invalid`,
  `prototype_revision_stack_gates_incomplete`,
  `prototype_revision_lint_failed`,
  `stack_realization_notes_unread`,
  `stack_realization_notes_required`,
  `stack_realization_notes_incomplete`,
  `stack_realization_notes_matrix_mismatch`,
  `stack_realization_notes_coverage_incomplete`,
  `stack_realization_notes_disposition_invalid`,
  `stack_realization_notes_lint_failed`.
- High-risk UI tasks: feasibility conclusion before Readiness
  (`high_risk_feasibility_unresolved`).

## Discussion writeback

- Material discussion accepts (prototypes, page splits, product coverage, Plan
  fields) Must write App authoritative slots + readback before the next phase
  gate — never leave truth only in chat/`temp`
  (`discussion_writeback_pending` / `temp_only_artifact_forbidden` /
  `stale_reference_after_discussion`).
  Detail: `granoflow-agent-workflow/discussion-writeback-contract`.
- Same batch Must load `granoflow-agent-workflow/change-impact-fanout`, scan
  required scopes (product docs, project/milestone/task work, prototypes,
  notes/cards, experience), disposition every hit, and lint a closed ledger
  (`change_impact_unread` / `change_impact_ledger_incomplete` /
  `change_impact_open_targets` / `change_impact_false_none` /
  `change_impact_deferred_unapproved` /
  `change_impact_updated_missing_evidence` / `change_impact_lint_failed`).
  Soft “remember to update siblings” is not enough.
- When any `ui_prototype` is updated, same batch Must load
  `granoflow-agent-workflow/prototype-product-truth-writeback`, set
  `decision_class` (`product_truth_changing` when unsure), and for
  product-truth changes update product docs + Task Work locked contracts while
  dispositioning user stories (`prototype_product_doc_writeback_required` /
  `prototype_user_story_disposition_required` /
  `prototype_product_truth_class_required` /
  `prototype_product_truth_writeback_unread`).

## Other initialization gates

- `product_spec_coverage.status: ready` before Done
  (`product_spec_coverage_incomplete`), including:
  - every adopted journey: mandatory **operation-flow** pass (serial gates vs
    parallel ops + final confirm) + conclusion (`flow_decomposition_*`; not
    risk→multi-screen);
  - every adopted acceptance: stress path
    (`journey_stress_path_incomplete`);
  - `screen_detail_registration.status: adopted` + checklist
    `screen_detail_registration_adopted`
    (`screen_detail_registration_missing` /
    `screen_ui_details_source_invalid`);
  - unattended must not auto-accept decision-changing thin-doc gaps
    (`thin_product_doc_gap_requires_user`).
    Detail: `product-spec-flow-decomposition.md` and
    `granoflow-agent-workflow/requirement-intake-and-traceability`.
- **Engineering Acceptance Pack** (software Step 1): AI self-check YAML → pack
  MD→HTML browse-confirm → then `granoflow_project_work_confirm`. Fail closed
  `engineering_acceptance_pack_unread` /
  `engineering_acceptance_pack_missing` /
  `engineering_acceptance_pack_incomplete` /
  `engineering_acceptance_pack_unconfirmed` /
  `engineering_acceptance_pack_drift` /
  `engineering_acceptance_link_digest_required` /
  `init_ai_self_check_failed` /
  `directory_structure_unselected` /
  `visual_baseline_applicability_unresolved`. Detail:
  `granoflow-agent-workflow/engineering-acceptance-pack`.
- When `visual_baseline.applicability: required`, Missing Shell fails Done;
  init Baseline = Spec + Shell only (not a full S-* HTML gallery).
  When `not_applicable`, Spec / Shell / widgets are not required for Done.
- Stack capability before HTML (UI path); capability-critical libraries
  selected or explicit `no_capability_dependency_declaration`.
- Never resolve Baseline `"current"` or `"latest"`.
