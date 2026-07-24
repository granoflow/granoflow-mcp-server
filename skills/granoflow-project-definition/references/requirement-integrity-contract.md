# Requirement Integrity Contract

Read this reference while producing or re-evaluating
`product_spec_coverage`. It prevents source requirements from being compressed
into a weaker journey summary and makes necessary product completion explicit.

## Source facts

Emit `granoflow_source_fact_ledger_v1`. One fact is one independently testable
statement, not a paragraph summary. Preserve the source's named entry point,
control, user action, object, conditions, visible success, visible failure, and
platform when stated.

Classify each fact:

- `user_stated`: explicitly present in the user's words or source documents.
- `necessary_implication`: required for an already accepted goal to work.
- `domain_baseline`: a baseline capability needed for this product category.
- `product_expansion`: changes product direction or scope.

Necessary implications and domain baselines may be adopted with rationale and
evidence when they do not change direction. Adopted product expansion requires
a user `confirmation_ref`. Never relabel an inference as user-stated.

Every adopted fact must map to a journey step or acceptance row. A rejected,
conflicting, or out-of-scope fact needs an explicit non-goal reference.

## Journey steps

Emit `granoflow_journey_step_traceability_v1`. Each adopted journey has ordered,
globally unique steps that preserve:

- entry surface or entry reference;
- visible control for user actions;
- actor, action, and expected observation;
- interaction surface (`in_app_ui`, `os_chrome`, `mixed`, `service_path`);
- platform boundary (`none`, `plugin`, `os`);
- source fact ids and applicable test layers.

Every user-visible journey needs entry, action, and outcome steps. Add a
failure step when source facts contain failure outcomes or the route crosses a
plugin/OS boundary.

Do not require unit, integration, and E2E for every step. Declare only the
applicable layers. Plugin/OS boundaries require unit coverage for adapter
errors and fallbacks; visible OS chrome additionally requires E2E, while a
non-visible platform service boundary requires integration.

## Background activities and user control

Emit `granoflow_background_activity_control_v1`. Classify every adopted fact as
`none`, `starts_activity`, `background_update`, `protected_control`, or
`exit_action`. An activity is anything that keeps running or automatically
updates the product after a user action: progress, streaming output, timed
refresh, synchronization, media position, and similar behavior.

For each activity record:

- whether it continues after a user action;
- the background events it emits;
- exactly which state those events may change;
- which page, panel, focus, input, selection, and navigation state they must
  not change;
- representative controls that must keep working;
- every way the user can stop, cancel, close, return, or otherwise exit;
- linked facts, journey steps, and required test layers.

Use direct behavior language: while a feature runs, a background update must
not close a panel, move focus, switch a user selection, navigate elsewhere, or
undo the user's latest action unless the accepted product contract explicitly
requires that change.

An unclassified fact, unknown write scope, missing exit, overlapping allowed
and forbidden state, or missing independent semantic replay blocks `ready`.
Visible activities require component-path Integration and human-path E2E.
Unit coverage is additional only when a separately testable controller,
reducer, adapter error, or fallback exists.

## Review and readiness

All integrity contracts use deterministic SHA-256 digests and an independent
reviewer whose id differs from the author. Semantic replay must report empty
`missing_fact_ids` and `distorted_fact_ids`.

Legacy documents remain readable. Once `product_spec_coverage.status` is
`ready` or the document is re-evaluated for readiness, missing ledgers are
returned as migration gaps and cannot silently pass.

Lint with:

```bash
python3 skills/granoflow-project-definition/scripts/lint_product_spec_coverage.py \
  project-work.yaml
```
