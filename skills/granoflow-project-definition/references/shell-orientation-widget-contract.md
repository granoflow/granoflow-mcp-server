# App Shell Orientation And Widget Contract

Use this contract after the Design Spec is selected.

## Required orientations

Derive Shell coverage from the confirmed `platform_support_matrix`.

- A platform requiring portrait receives portrait Shell HTML.
- A platform requiring landscape receives landscape Shell HTML.
- A platform requiring both receives both in every Shell candidate.
- Do not invent an unsupported orientation.
- Do not omit a required orientation to create candidate contrast.

Each rendered orientation Must use selected Design Spec tokens and real product
copy.

## Mandatory Shell widgets

Every required portrait and landscape layout Must include both:

1. a top bar;
2. a bottom navigation bar.

These are project Widget Catalog roles:

- `app_shell.top_bar`
- `app_shell.bottom_navigation`

Store platform/orientation differences as variants of those roles, not as
unrelated duplicate widgets. Variants may change geometry, density, safe-area
handling, item arrangement, overflow, and responsive behavior while preserving
the role contract.

Shell candidates may differ in the expression inside the two bars, content
hierarchy, grouping, spacing, and responsive composition. They may not differ
by removing either mandatory bar.

## Selection and Widget Catalog projection

Only the selected Shell contributes widgets to the project catalog.

After Baseline confirmation:

1. promote `app_shell.top_bar` and `app_shell.bottom_navigation` to
   `widgets.yaml`;
2. record the selected Shell artifact ref/version/SHA under `derived_from`;
3. include every required platform/orientation variant;
4. render both roles and their variants in the browseable Design System HTML
   catalog;
5. keep unselected Shell candidate widgets out of the catalog.

Later Task UI work must reuse these roles. A Task may extend a recorded variant
when a newly supported platform/orientation requires it. Removing either role
or changing locked token behavior reopens Baseline.

## Record and gate

Write `granoflow_shell_selection_v2` under
`engineering.theme_and_design_system.shell_selection` and validate it with:

```text
python skills/granoflow-project-definition/scripts/lint_shell_selection.py <record.json>
```

Fail closed with:

- `shell_orientation_requirements_missing`
- `shell_required_layout_missing`
- `shell_top_bar_missing`
- `shell_bottom_navigation_missing`
- `shell_widget_catalog_projection_invalid`
- existing `shell_spec_mismatch`, `shell_spec_tokens_missing`,
  `shell_wireframe_only`, and Shell candidate-count gates.
