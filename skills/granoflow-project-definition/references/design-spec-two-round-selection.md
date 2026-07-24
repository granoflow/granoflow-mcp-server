# Design Spec Two-Round HTML Selection

Use this contract when `visual_baseline.applicability: required`.

## Goal

Interactive Project Definition converges on one complete Design Spec through
two polished HTML review rounds:

1. a product-fitted direction chooser;
2. a comparison of two or three complete Design Spec candidates.

The selected Spec remains the token authority for the later App Shell round.
Neither round is an image-generation task.

## Product-fit envelope

Before drawing or authoring choices, derive a `product_fit_envelope` from the
highest-authority available sources:

1. user-confirmed decisions;
2. product documents;
3. user stories;
4. recorded inference.

Record source refs, an input SHA-256, audience, product tasks, platforms,
brand constraints, accessibility requirements, allowed directions, excluded
directions, and a concise rationale. Every offered choice Must have
`fit_status: passed`. Do not add an unsuitable option to fill a quota.

If four materially distinct, suitable choices cannot be produced for any
first-round dimension, stop with `design_direction_candidate_insufficient`.

## Round 1: visual direction chooser

Author one self-contained, responsive HTML page. It Must look like a finished
design artifact, not a default form or developer settings panel.

The six dimensions and user-visible numbering are fixed:

| Number | Dimension  | Required visual comparison                                       |
| ------ | ---------- | ---------------------------------------------------------------- |
| `1`    | Color      | Palette, surface distribution, foreground contrast, sample UI    |
| `2`    | Density    | The same content at visibly different spacing/control densities  |
| `3`    | Shape      | The same buttons, fields, and cards with different shape systems |
| `4`    | Typography | The same real product copy with different type systems           |
| `5`    | Layering   | The same cards using border, tint, and elevation strategies      |
| `6`    | Layout     | The same product content using different composition systems     |

Each dimension Must offer exactly four suitable values labeled `a` through
`d`. Abstract adjectives may support the preview but may not replace it.

The HTML Must:

- use real product copy and the same content across comparable values;
- expose semantic radio groups and full keyboard operation;
- generate the selection code live, for example `1a2b3d4c5a6b`;
- accept partial selection; omitted dimensions use their recorded recommended
  value;
- show the completed code before the user confirms;
- use HTML/CSS/JS and inline SVG only by default;
- avoid generated raster images; existing product-owned assets may be used
  only with a local source and a graceful fallback;
- be usable on narrow and wide viewports;
- keep seed ids, internal recipe ids, and fail codes out of visible copy.

Selection-code grammar is one or more unique dimension/value pairs:
`[1-6][a-d]`. Store both the user's input and the canonical completed code in
numeric dimension order.

## Round 2: complete Design Spec comparison

After Round 1 confirmation, author one polished responsive HTML comparison
page containing complete Design Spec candidates.

- Default to three candidates.
- Reduce to two only when a suitable, materially distinct third candidate
  cannot be produced. Record
  `reduction_reason_code: insufficient_distinct_third`.
- Never produce one candidate in interactive mode.
- Every candidate Must honor the completed Round 1 direction code.
- Every candidate Must cover the same token roles, component roles, product
  facts, and accessibility requirements.
- Every pair Must differ materially on at least three unlocked secondary axes.

Complete coverage includes:

- color ramps, semantic colors, surfaces, foregrounds, and contrast;
- typography roles, responsive type scale, weights, line heights, and tracking;
- spacing, density, control size, touch targets, and icon size;
- shape, borders, radius, opacity, elevation, and overlays;
- grid, content widths, breakpoints, and responsive behavior;
- interaction and semantic component states;
- light/dark/high-contrast policy when applicable;
- motion duration, easing, reduced-motion behavior, and transition roles;
- project-relevant components inferred from product documents.

The comparison page Must render real tokens through CSS custom properties and
real DOM components. It may include one controlled product-component
composition per candidate so the user can judge the system in context. It
Must not become a full journey walkthrough or a gallery of every product
screen.

## Randomness and exact reproduction

The initial batch uses a true-random `master_seed` and records it in the
machine-local visual-lot ledger. The seed is agent-only.

Derived seeds use HMAC-SHA256 over the algorithm version, product-fit SHA-256,
canonical selection code, and round/dimension/option identity. The same inputs
Must derive the same structured candidate seeds.

Exact visual reproduction uses the persisted HTML/token artifact and its
SHA-256 as the authority; do not depend on a later model call reproducing
identical markup.

`换新批` draws and records a new master seed with ledger dedupe. `在某套上改`
keeps the existing master and derived seed unless the user explicitly requests
a new direction.

## Records and gates

Write `granoflow_design_spec_selection_v2` under
`engineering.theme_and_design_system.design_spec_selection`. Validate it with:

```text
python skills/granoflow-project-definition/scripts/lint_design_spec_selection.py <record.json>
```

Fail closed with:

- `design_fit_envelope_required`
- `design_direction_round_required`
- `design_direction_candidate_insufficient`
- `design_selection_code_invalid`
- `design_round_html_quality_failed`
- `design_spec_candidate_count_invalid`
- `design_spec_candidate_difference_insufficient`
- `design_generation_reproducibility_missing`

User-facing pages and Preview Gate copy use only numbers, letters, plain
labels, visual previews, and selection summaries.

## Unattended mode

Explicit unattended mode remains single-option:

1. build and record the product-fit envelope;
2. auto-complete all six dimensions from their recommended values;
3. draw one master seed;
4. author one complete product-fitted Design Spec HTML;
5. record an `unattended_single` v2 selection and continue without waiting.

Do not emit an interactive Round 1 chooser or challengers.

## Widget evolution after Baseline

The selected Spec defines token roles; `widgets.yaml` defines reusable project
components.

After Baseline confirmation:

1. extract the initial reusable widgets into `widgets.yaml`;
2. publish a browseable Design System HTML catalog from the same catalog data;
3. on every later confirmed Task UI prototype, reuse an existing widget when
   the role already exists;
4. promote a new widget only when it is reusable beyond that Task and record
   exact `derived_from` prototype/version/SHA evidence;
5. refresh both `widgets.yaml` and the Design System HTML catalog after a
   promotion;
6. keep task-local components in Task Work;
7. reopen Baseline when a proposed widget changes locked color, typography,
   spacing, shape, elevation, motion, or component-state contracts.

The HTML catalog is a display projection of `widgets.yaml`, not a second
source of truth and not a new Design Spec vote.

App Shell top-bar and bottom-navigation roles enter this same lifecycle under
[shell-orientation-widget-contract.md](shell-orientation-widget-contract.md).
