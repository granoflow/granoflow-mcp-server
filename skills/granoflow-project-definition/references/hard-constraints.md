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

## Design Spec / Shell

| Mode        | Design Spec                                                                             | Shell                                                                                   |
| ----------- | --------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Interactive | Mainstream-first ≥5→**promote 3**, then triad via **true-random** `draw_visual_lots.py` | Mainstream-first ≥5→**promote 3**, then triad chrome cards; all **embed selected Spec** |
| Unattended  | Mainstream-first→one `spec_match` via true-random draw                                  | Mainstream-first→one `shell_match` embedding Spec (no palette seed)                     |

- **Candidate protocol (hard):** load
  `granoflow-agent-workflow/prototype-expression-brainstorm` before Spec/Shell
  HTML. Build **mainstream product references** first (`scope_mode`
  `same_category`|`capability_match`; default capability when unsure);
  brainstorm backfill **only** when mainstream `<5`. Spec/Shell promote count
  is **3** (not task AB=2). Offering Spec/Shell as dual-only →
  `prototype_option_promote_count_mismatch`. Candidate analysis does **not**
  replace lot draw. Lint with
  `lint_prototype_expression_brainstorm.py`.
- Design Spec artifact = **Style Guide / Design Tokens board** (Colors,
  Typescale, Spacing, Grid/Breakpoints, Component states, Shadows&Radius)—**not**
  a full journey-screen gallery. Wrong shape → `design_spec_wrong_artifact_type`.
- App Shell artifact = **product-near chrome + primary surface** that already
  **loads selected Spec tokens** and aims for final-product effect under
  contract fidelity—**not** grey wireframes. Fail closed
  `shell_spec_tokens_missing` / `shell_wireframe_only`.
- **Lot draw (hard):** Spec seeds and Shell chrome ids Must come from
  `scripts/draw_visual_lots.py` (**true random** only—no classroom salt /
  `--from`). Hand-invented `seed-*` / chrome ids → `design_spec_seed_not_drawn`.
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
- Unattended with a missing icon: residual / fail closed
  `app_icon_source_unresolved` (do not invent a source).
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
- Post-Baseline task/milestone pages Must **embed locked Spec tokens**
  (`data-baseline-tokens="locked"`) and **reuse Shell chrome language** /
  `widgets.yaml` roles. Generic parallel phone frames →
  `prototype_generic_phone_frame` / `prototype_shell_chrome_mismatch` /
  `prototype_spec_tokens_not_loaded` / `prototype_spec_tokens_drift`.
- After a chrome-family sibling is `visualConfirmed`, later pages Must reuse
  that confirmed control vocabulary (title-ico / tbtn / chip selected tint /
  pref-ico)—not invent a parallel dialect that only shares Baseline tokens →
  `prototype_confirmed_chrome_lock_*`.
- Interactive: **mainstream-reference-first** candidates (≥5; brainstorm
  backfill only when mainstream `<5`) then promote **two page expressions**
  (`expr_a` + `expr_b`) with **functional parity** (same capabilities, same
  data fields, same required states; only presentation differs)—see
  `granoflow-agent-workflow/prototype-expression-brainstorm`. Share the locked
  Design System; mix-and-match per task/page; ≥2 whitelist contrast axes;
  **side-by-side Contrast Gallery** with Baseline-fit + candidate digests +
  per-axis visible-diff captions; conditional **third** `industry_peer_c`
  only for documented industry-peer deadlock (still inside locked Design
  System). Lint `lint_prototype_expression_brainstorm.py`.
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
  `prototype_option_function_split`,
  `prototype_option_data_divergence`,
  `prototype_option_contrast_insufficient`,
  `prototype_option_near_duplicate`,
  `prototype_option_contrast_gallery_required`,
  `prototype_option_diff_unlabeled`, `prototype_option_third_unjustified`.
- Unattended: mainstream-first protocol then **one** `expr_a` only (still
  Baseline-fitted).
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
  - unattended must not auto-accept decision-changing thin-doc gaps
    (`thin_product_doc_gap_requires_user`).
    Detail: `product-spec-flow-decomposition.md`.
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
- When `visual_baseline.applicability: required`, Missing Shell fails Done.
  When `not_applicable`, Spec / Shell / widgets are not required for Done.
- Stack capability before HTML (UI path); capability-critical libraries
  selected or explicit `no_capability_dependency_declaration`.
- Never resolve Baseline `"current"` or `"latest"`.
