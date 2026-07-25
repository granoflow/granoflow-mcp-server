# Product Truth SoT Layers（PW ↔ UIT/RB）

Owner for **where** product/screen/boundary truth lives after Route UI Truth
(`UIT-*`) and Reality Boundary (`RB-*`) cards exist. Prevents redundant conflict
between Project Work prose and card detail.

Related: `project-work-document-template.md`, `reality-boundary-cards.md`,
`route-ui-truth-cards.md`, `project-context-attachments.md`,
`unattended-card-truth-batch-gate.md`.

## Layers

| Content                                                 | Authority                                                             | Project Work                                                  |
| ------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------- |
| Screen / journey inventory                              | PW `screen_coverage` / journey rows                                   | Keep short rows (id, title, journeys)                         |
| Product-declared UI points (even if unimplemented)      | PW `ui_details` (declared)                                            | Keep short bullets + `source`; forbid screenshot-level essays |
| Route “what it looks like now” + checklist + screenshot | UIT Note/cards + `route_ui_truth_index`                               | **No body prose**; optional `uit_fact_id: UIT-*` pointer      |
| Status quo / boundary detail                            | RB Note/cards + `reality_boundary_index`                              | **No body prose**; optional `rb_fact_id: RB-*` pointer        |
| Hard Gate “may we change code?”                         | `project_rules.yaml` / `project_snapshot.yaml` **one-line** summaries | Do not pile boundary essays into PW                           |

```text
Product docs (evidence)
  → Project Work (requirements + inventory + pointers)
  → UIT/RB Notes & cards (retrievable reality detail)
  → snapshot/rules (Hard Gate short lines only)
```

## Forbidden dual-write

- Maintaining the **same** visual/boundary detail in both Project Work and
  cards, then treating both as truth.
- Updating only one side after a material UI/boundary change.
- Putting screen essays or boundary treatises into `project_snapshot.yaml` /
  `project_rules.yaml` (beyond one-line Hard Gate constraints).
- Opening a third long copy in Project Work on Delivery when cards/`will_change`
  already carry the update.

Fail-closed semantic (document gate): `product_truth_dual_write_forbidden`.

## Delivery discipline

When Plan marks UIT/RB `will_change`:

1. Verify, then update the **same** `fact_id` Note/cards + index.
2. Refresh Hard Gate **short** lines in snapshot/rules only if they still state
   the old constraint.
3. Do **not** paste the new detail into Project Work body. Pointers
   (`uit_fact_id` / `rb_fact_id`) may be added or corrected.

## Unattended

Card apply remains interactive (see `unattended-card-truth-batch-gate.md`).
SoT layering does not authorize unattended Knowledge/card writes.

## Migration note

Existing Project Work files may still contain long screen/boundary prose.
When next editing that Project Work attachment, migrate detail onto UIT/RB
cards (or index pointers) and leave only inventory + short declared
`ui_details` + `fact_id` pointers in PW. Do not invent a second parallel
ledger “for safety.”
