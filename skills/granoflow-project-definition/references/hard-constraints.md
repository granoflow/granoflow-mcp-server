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

| Mode        | Design Spec                                     | Shell                                                     |
| ----------- | ----------------------------------------------- | --------------------------------------------------------- |
| Interactive | Triad via **true-random** `draw_visual_lots.py` | Triad chrome cards from deck; all **embed selected Spec** |
| Unattended  | One `spec_match` via true-random draw           | One `shell_match` embedding Spec (no palette seed)        |

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
  `visual_lot_dedupe_required`, `visual_lot_exhausted`,
  `visual_lot_classroom_salt_forbidden`.
- **From Shell onward, design style converges.**
- **User-facing Preview Gate copy:** never show `seed-*` ids, internal option
  enums (`spec_match` / `ai_challenger_*`), or other agent-only jargon. Present
  plain-language choice labels + clickable links only. Seeds and option ids
  remain in Project Work / run ledger only (`design_spec_user_facing_jargon`).

## Widgets

- After Baseline visual confirmation: first mandatory `widgets.yaml` extract
  (`widget_catalog_required` if missing).
- YAML = contract (identity, props, tokens, states, reuse); visuals stay in
  confirmed prototypes.
- Incremental extract after later confirmed prototypes; one current project
  slot.

## Task / milestone `ui_prototype`

- `derivedFrom` exact Baseline; **no** random visual seed
  (`task_prototype_seed_forbidden`).
- Reuse `widgets.yaml` same role (`widget_reuse_required`).
- **Craft Gate** before `visualConfirmed` (`task_prototype_craft_incomplete`),
  including **product truth** (`prototype_product_truth_violation`) and
  **user-visible copy boundary**
  (`user_visible_copy_boundary_unread` /
  `user_visible_copy_boundary_violation`; checklist field
  `user_visible_copy_boundary_ok` +
  `lint_prototype_user_copy.py`).
- Interactive: default **two page expressions** (`expr_a` + `expr_b`) that
  share the locked Design System; mix-and-match per task/page; ≥2 whitelist
  contrast axes; **side-by-side Contrast Gallery** with per-axis visible-diff
  captions; conditional **third** `industry_peer_c` only for documented
  industry-peer deadlock (still inside locked Design System).
- Never re-offer Design Spec labels (`delta_match` / `ai_challenger` /
  `spec_match`) as task options after Baseline lock
  (`prototype_option_design_system_reopened`).
- Fail closed: `prototype_option_design_system_reopened`,
  `prototype_option_contrast_insufficient`,
  `prototype_option_near_duplicate`,
  `prototype_option_contrast_gallery_required`,
  `prototype_option_diff_unlabeled`, `prototype_option_third_unjustified`.
- Unattended: **one** `expr_a` only.
- High-risk UI tasks: feasibility conclusion before Readiness
  (`high_risk_feasibility_unresolved`).

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
- Missing Shell fails Done.
- Stack capability before HTML; capability-critical libraries selected or
  explicit `no_capability_dependency_declaration`.
- Never resolve Baseline `"current"` or `"latest"`.
