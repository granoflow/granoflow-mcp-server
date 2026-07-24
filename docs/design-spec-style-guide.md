# Design Spec Two-Round HTML Selection

## Summary

Interactive Project Definition now locks Design Spec through two polished HTML
rounds: a product-fitted six-dimension direction chooser, then a comparison of
three complete Style Guide candidates by default (or two when a suitable,
materially distinct third cannot be produced).

This corrects an agent failure mode observed while initializing GranoReader:
treating Spec as “complete every product page” instead of locking colors,
typescale, spacing, grid, component states, and elevation.

## Artifact split

| Round            | Artifact                                                               | Must include                                                                                                             | Must not                                                         |
| ---------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Direction round  | One polished responsive HTML chooser                                   | Product-fit options `1`–`6`, values `a`–`d`, live selection code, real visual comparisons                                | Default form, abstract labels without visuals, generated images  |
| Spec round       | One polished HTML comparison + tokens JSON per candidate               | Colors, Typescale, Spacing, Grid/Breakpoints, states, Shadows&Radius, controlled product-component preview               | Full journey-screen walkthrough / phone gallery of all screens   |
| Shell            | Product-near chrome (portrait + landscape) **embedding selected Spec** | Spec tokens loaded; primary nav; at least one Spec-styled primary surface (real copy); chrome variants only across triad | Grey wireframes; new palette/type seed; ignoring `token_sources` |
| Baseline package | Spec + chosen Shell + remaining journey screens                        | Screens mapped to `screen_coverage` consuming locked tokens; evolve from Shell surfaces                                  | Re-rolling Spec seeds; redrawing from a disconnected wireframe   |

## Fail-closed codes

- `design_spec_wrong_artifact_type` — Spec is a journey gallery instead of a Style Guide
- `design_spec_user_facing_jargon` — Preview Gate shows `seed-*` or internal option enums to the user
- `design_spec_seed_not_drawn` — Spec/Shell lots not drawn via `draw_visual_lots.py`
- `design_fit_envelope_required` — choices were authored before product-fit analysis
- `design_direction_candidate_insufficient` — a first-round dimension lacks four suitable choices
- `design_selection_code_invalid` — the user code or completed code is malformed
- `design_round_html_quality_failed` — either HTML round misses the visual/interaction bar
- `design_spec_candidate_count_invalid` — interactive Round 2 is not 3 or justified 2
- `design_spec_candidate_difference_insufficient` — candidates are cosmetic near-duplicates
- `design_generation_reproducibility_missing` — seed derivation or artifact SHA is absent
- `shell_spec_tokens_missing` — Shell does not load/apply selected Spec tokens
- `shell_wireframe_only` — Shell is grey boxes only, not product-near
- `visual_lot_dedupe_required` — 换新批 without machine-local ledger dedupe
- `visual_lot_exhausted` — not enough unused lots remain after strong dedupe
- `visual_lot_classroom_salt_forbidden` — `--from` / classroom salt rejected (true random only)
- Existing: `design_spec_triad_required`, `design_spec_seed_collision`, `shell_triad_required`, `shell_seed_collision`, `shell_spec_mismatch`

## Lot draw

The Spec master seed and Shell chrome ids come from
`skills/granoflow-project-definition/scripts/draw_visual_lots.py`. Design Spec
candidate seeds are reproducibly derived from the recorded master seed,
product-fit SHA, and selection code. Exact reproduction reuses the recorded
HTML/token artifact SHA. 换新批 uses ledger dedupe; 在某套上改 preserves the
seed unless the user asks for a new direction.

## Living Widget Catalog

After Baseline confirmation, `widgets.yaml` is the component contract and a
browseable Design System HTML catalog is its display projection. Confirmed
later Task prototypes may promote reusable widgets into both. Task-local
widgets stay local; changes to locked Spec tokens reopen Baseline.

## Shell quality bar

Shell Must already look like the product frame the user will ship against:
consume Spec colors/type/spacing/radius, show real bookshelf (or equivalent)
content, and keep glass on nav only when appropriate. Triad options differ by
chrome structure—not by inventing a second visual system.

Shell coverage follows the confirmed platform orientations. Every required
portrait and landscape layout contains both a top bar and a bottom navigation
bar. The selected Shell publishes these as `app_shell.top_bar` and
`app_shell.bottom_navigation` Widget Catalog roles with orientation variants.

## References

- `skills/granoflow-project-definition/references/project-artifact-workflows.md`
- `skills/granoflow-project-definition/references/hard-constraints.md`
- GranoReader initialization session (2026-07-21)
