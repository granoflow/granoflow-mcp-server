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

## Prototype Preview Gate

- Every previewable HTML unit (or interactive option batch) gets a **clickable**
  link.
- Interactive: stop and wait (option batches: all links, one wait).
- Unattended: non-blocking notice + ledger; closing **Prototype Link Digest**
  required (`prototype_link_digest_required`).
- Skipping interactive wait → `prototype_preview_review_required`.

## Design Spec / Shell

| Mode        | Design Spec                             | Shell                                                         |
| ----------- | --------------------------------------- | ------------------------------------------------------------- |
| Interactive | Triad, **three different random seeds** | Triad, all **fitted to selected Spec** (chrome variants only) |
| Unattended  | One `spec_match` + random seed          | One `shell_match` fitted to Spec (no palette seed)            |

- Fail closed: `design_spec_triad_required`, `design_spec_seed_collision`,
  `shell_triad_required`, `shell_seed_collision`, `shell_spec_mismatch`.
- **From Shell onward, design style converges.**

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
- **Craft Gate** before `visualConfirmed` (`task_prototype_craft_incomplete`).
- Interactive: default **two** options (`delta_match` + `ai_challenger`) with
  ≥2 whitelist contrast axes; conditional **third** `industry_peer_c` only for
  documented industry-peer deadlock.
- Fail closed: `prototype_option_contrast_insufficient`,
  `prototype_option_near_duplicate`, `prototype_option_third_unjustified`.
- Unattended: **one** `delta_match` only.

## Other initialization gates

- `product_spec_coverage.status: ready` before Done
  (`product_spec_coverage_incomplete`).
- Missing Shell fails Done.
- Stack capability before HTML; capability-critical libraries selected or
  explicit `no_capability_dependency_declaration`.
- Never resolve Baseline `"current"` or `"latest"`.
