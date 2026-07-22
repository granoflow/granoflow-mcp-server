# Prototype → Product Truth Writeback

Apply whenever the user **accepts, confirms, or locks** a material **prototype**
correction (craft rematch, chrome/control change, copy-in-frame, option pick
that changes behavior, or any mid-discussion UI fix that redefines how the
product works).

**Owner:** ensure prototype deltas that change product truth land in
**authoritative product docs + Task Work locked contracts** so Execution and
code implement the same truth — not a gallery-only preview.

Complements `discussion-writeback-contract` (slot writes) and
`change-impact-fanout` (cross-entity completeness). This contract owns the
**prototype → docs/contracts** semantic gate.

MCP stays thin: write through existing App/repo tools. Do not invent a second
store.

## Mandatory Load (fail closed if skipped)

Before closing a discussion batch that updates any task/milestone
`ui_prototype` (import, rematch, or confirmed craft fix), the host **Must**
load this reference via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "prototype-product-truth-writeback"
)
```

Skipping fails closed as `prototype_product_truth_writeback_unread`.

Seeing `discussion-writeback-contract`, `change-impact-fanout`, or SKILL prose
alone does **not** count.

Also load `change-impact-fanout`, `discussion-writeback-contract`, and
`prototype-doc-coverage` in the same batch. Coverage owns the page/control/
copy completeness ledger against Task Work **and** Project Work; this file
owns `decision_class` and product_doc / locked-contract writeback.

## Decision Class (hard)

Every material prototype decision batch Must set:

```yaml
decision_class: product_truth_changing | craft_only
```

| Class                    | Meaning                                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| `product_truth_changing` | Chrome, control presence, entry points, flows, toggles, product-visible labels, or behavior     |
| `craft_only`             | Same product truth; expression-only (spacing, color within Spec, icon metaphor with same label) |

**Default when unsure:** `product_truth_changing` (fail closed / safer). Do not
guess `craft_only` to skip docs.

Omitting `decision_class` while any `prototype` candidate is `updated` fails
closed as `prototype_product_truth_class_required`.

## Hard Rule — `product_truth_changing`

In the same batch as prototype writeback, the Change Impact Ledger Must:

1. Record `decision_class: product_truth_changing`.
2. Set `product_truth_writeback_loaded: true` (this reference loaded via MCP).
3. Disposition **and update** at least one `product_doc` (authoritative product
   spec / V0x doc path + section evidence).
4. Disposition **and update** at least one `task_work` with
   `locked_product_contracts` (or equivalent Musts) that code can implement.
5. Disposition **and update** Project Work when journeys / screens /
   acceptance / product copy change; otherwise explicit `not_applicable` with
   reason on the coverage ledger (`prototype-doc-coverage`).
6. Complete `prototype_doc_coverage` with every material prototype page /
   control / state / copy / flow mapped and `coverage: covered` (no
   `missing`/`conflict`) before Analysis close.
7. Scan and **disposition** every hit under user stories (`user_story` entity
   when present in the repo). Honest `not_applicable` is allowed when journeys
   / entries are unchanged — with an auditable reason. Silent skip is not.
8. Update related `prototype` packages + Task Work `ui_prototype_confirmed`
   refs per writeback.

Closing with only `prototype` `updated` (docs/contracts left stale) fails
closed as `prototype_product_doc_writeback_required`. Coverage gaps/conflicts
fail as `prototype_doc_coverage_gap` / `prototype_doc_conflict`.

## Hard Rule — `craft_only`

1. Record `decision_class: craft_only` and
   `product_truth_writeback_loaded: true`.
2. Prototype + Task Work prototype refs may `updated`.
3. `product_doc` / `user_story` May be `not_applicable` only with a reason that
   cites **existing sections already encoding** the unchanged product truth.
4. If the “craft” change actually moved chrome, toggles, labels, or behavior,
   reclassify to `product_truth_changing` — do not force `craft_only`.

## Ledger Fields (minimum)

Extend the Change Impact Ledger entry:

```yaml
change_impact:
  - at: null
    decision_summary: null
    decision_class: product_truth_changing # or craft_only; required when prototypes updated
    product_truth_writeback_loaded: false # must be true when prototypes updated
    contract_loaded: false # change-impact-fanout
    scan_terms: []
    scopes_checked: []
    candidates:
      - entity_type: product_doc | user_story | task_work | prototype | ...
        # ...
    status: open | closed | failed
```

Run `scripts/lint_change_impact_fanout.py` — require `ok: true` before closing.

## Authoritative Slot Map (additive)

| Adjustment kind                    | Must write                                                                 | Also                                                                 |
| ---------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Prototype product-truth correction | Repo `product_doc` + Task Work `locked_product_contracts` + `ui_prototype` | Disposition `user_story`; Project Work when journeys/coverage change |
| Prototype craft-only rematch       | `ui_prototype` + Task Work prototype refs                                  | `product_doc`/`user_story` N/A only with section-cite reason         |

## Timing

Same moments as writeback / fan-out: before Analysis/Plan confirm, Readiness
`passed`, and Execution. Unattended: same; never skip docs because
`interaction_budget` is 0.

## Fail-closed codes

| Code                                        | When                                                                   |
| ------------------------------------------- | ---------------------------------------------------------------------- |
| `prototype_product_truth_writeback_unread`  | This reference not loaded via MCP before prototype decision close      |
| `prototype_product_truth_class_required`    | Prototype `updated` but `decision_class` missing                       |
| `prototype_product_doc_writeback_required`  | `product_truth_changing` without `product_doc` + `task_work` `updated` |
| `prototype_user_story_disposition_required` | `product_truth_changing` with no `user_story` candidate dispositioned  |
| `change_impact_lint_failed`                 | Lint script ≠ ok (includes the above when encoded in the ledger)       |

## Agent Checklist

1. Load `prototype-product-truth-writeback` via MCP?
2. Load `prototype-doc-coverage` and complete coverage rows (TW + PW)?
3. `decision_class` set (`product_truth_changing` if unsure)?
4. If product-truth: product doc + Task Work contracts updated + user stories dispositioned?
5. Prototype imported / confirmed refs rewritten?
6. Fan-out ledger lint `ok` and `closed`?
7. If any check fails → do not close the discussion batch / phase gate.

## Relationship

- Does **not** replace fan-out or writeback; it **constrains** dispositions when
  prototypes change.
- Complements `prototype_product_truth_violation` (previews must not invent
  unauthorized behavior): this gate forces authorized behavior into docs so
  code can implement it.
- Complements `user-visible-copy-boundary` (what may appear in-frame): when a
  correction **requires** visible product text, that requirement Must land in
  product docs / locked contracts, not only in HTML.
