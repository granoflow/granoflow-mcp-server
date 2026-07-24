# UI Component And Effect Matrix

Load this contract before Task UI HTML authoring. It chooses the best
implementable Widget, control, and effect candidates inside the user's
selection, locked Design Baseline, Widget Catalog, platform matrix, stack
capability profile, and approved dependencies.

## Hard eligibility

- Reuse an eligible Catalog Widget when the same role exists.
- Preserve a compatible user-selected candidate.
- An incompatible user selection may map automatically to a same-role,
  functionally equivalent variant only when the mapping is visible in the
  review HTML and does not change behavior.
- A behavior-changing replacement remains `pending_user_decision`.
- `forbidden` candidates never enter a selected option.
- Accessibility, functional equivalence, platform coverage, and performance
  are hard gates.
- Every required platform/orientation/layout family needs an implementation
  and fallback.

## High-cost effects

A selected `high_cost` effect requires all of:

- a material core-experience benefit;
- passed performance budget;
- a passed reduced-motion alternative;
- a complete lower-capability fallback.

## Ranking

After hard gates, rank eligible candidates per role:

```text
product_fit * 30
+ usability * 25
+ aesthetic * 25
+ performance * 10
+ maintainability * 10
```

Each score is an integer from `0` to `5`. Existing eligible Catalog Widgets
win before ranking. For equal scores, prefer no new dependency, then stable
candidate id order.

The Contrast Gallery shows selected Widgets, platform adaptations, effects,
fallbacks, and visible differences. It does not show internal provider or
skill bookkeeping.

Validate the record with:

```text
python skills/granoflow-project-definition/scripts/lint_ui_component_effect_matrix.py <record.json>
```

Fail closed with:

- `ui_component_effect_matrix_required`
- `ui_component_effect_incompatible`
- `ui_component_effect_user_decision_required`
- `ui_component_effect_high_cost_unjustified`
- `ui_component_effect_fallback_missing`
- `ui_component_effect_ranking_invalid`
- `ui_widget_reuse_bypassed`

After confirmation, promote reusable new roles or variants to `widgets.yaml`
and its Design System HTML projection. Keep Task-local decoration local.
