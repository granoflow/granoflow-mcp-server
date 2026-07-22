# Design Spec = Style Guide / Design Tokens（0.1.22）

## Summary

Project Definition **Round A (Design Spec)** must author **Style Guide /
Design Tokens boards**, not full-page galleries of every
`product_spec_coverage` journey screen.

This corrects an agent failure mode observed while initializing GranoReader:
treating Spec as “complete every product page” instead of locking colors,
typescale, spacing, grid, component states, and elevation.

## Artifact split

| Round            | Artifact                                                               | Must include                                                                                                             | Must not                                                         |
| ---------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Spec             | Style Guide HTML + tokens JSON                                         | Colors, Typescale, Spacing, Grid/Breakpoints, Button/Input states, Shadows&Radius                                        | Full journey-screen walkthrough / phone gallery of all screens   |
| Shell            | Product-near chrome (portrait + landscape) **embedding selected Spec** | Spec tokens loaded; primary nav; at least one Spec-styled primary surface (real copy); chrome variants only across triad | Grey wireframes; new palette/type seed; ignoring `token_sources` |
| Baseline package | Spec + chosen Shell + remaining journey screens                        | Screens mapped to `screen_coverage` consuming locked tokens; evolve from Shell surfaces                                  | Re-rolling Spec seeds; redrawing from a disconnected wireframe   |

## Fail-closed codes

- `design_spec_wrong_artifact_type` — Spec is a journey gallery instead of a Style Guide
- `design_spec_user_facing_jargon` — Preview Gate shows `seed-*` or internal option enums to the user
- `design_spec_seed_not_drawn` — Spec/Shell lots not drawn via `draw_visual_lots.py`
- `shell_spec_tokens_missing` — Shell does not load/apply selected Spec tokens
- `shell_wireframe_only` — Shell is grey boxes only, not product-near
- `visual_lot_dedupe_required` — 换新批 without machine-local ledger dedupe
- `visual_lot_exhausted` — not enough unused lots remain after strong dedupe
- `visual_lot_classroom_salt_forbidden` — `--from` / classroom salt rejected (true random only)
- Existing: `design_spec_triad_required`, `design_spec_seed_collision`, `shell_triad_required`, `shell_seed_collision`, `shell_spec_mismatch`

## Lot draw

Spec seeds and Shell chrome ids Must come from
`skills/granoflow-project-definition/scripts/draw_visual_lots.py` (true random;
`--record` to `~/.granoflow/visual-lot-ledger.json`). 换新批 uses
`--dedupe ledger`. 在某套上改 does not re-draw unless the user asks for a
structural change.

## Shell quality bar

Shell Must already look like the product frame the user will ship against:
consume Spec colors/type/spacing/radius, show real bookshelf (or equivalent)
content, and keep glass on nav only when appropriate. Triad options differ by
chrome structure—not by inventing a second visual system.

## References

- `skills/granoflow-project-definition/references/project-artifact-workflows.md`
- `skills/granoflow-project-definition/references/hard-constraints.md`
- GranoReader initialization session (2026-07-21)
