# Card-Truth Readiness Gate（RB / UIT · 无人值守可落卡）

Owner for **Reality Boundary (`RB-*`)** and **Route UI Truth (`UIT-*`)**
Knowledge/card writes during **unattended** engineering. These writes are
**anti-drift obligations**, not taste gates — if code or UI changes while
Notes/cards stay empty, truth drifts.

Parent contracts: `unattended-interaction-contract.md`,
`lifecycle-card-checkpoints.md`, `reality-boundary-cards.md`,
`route-ui-truth-cards.md`, `long-task-run-continuity.md`.

## Problem (old rule — revoked)

Previously this gate split “interactive card apply” from unattended engineering.
That caused **truth drift**: unattended Delivery changed code/UI but deferred
RB/UIT apply, leaving Granoflow with zero cards while Task Work claimed
`updated_on_delivery`.

**New rule:** unattended **Must** create and update RB/UIT Notes/cards in the
same wave as the Plan/Delivery that changes the underlying truth.

## What is still subjective (not RB/UIT)

Task **retrospective review cards** (learning load, taste, legal nuance) remain
`subjective_acceptance` under `granoflow-review-card-draft` § Unattended Review
Boundary. Do not conflate those with RB/UIT archived-reference anti-drift
cards.

## Unattended apply obligation (hard)

When `executionMode: unattended` (or explicit unattended declaration) and any
of the following is true, **Must** run Knowledge assessment preview → apply and
materialization preview → apply **without** waiting for a mid-run user pause:

| Trigger         | When                                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| `gap`           | Plan/Delivery `*_index_review` marks a new `fact_id` with no index row                                        |
| `will_change`   | Plan listed `will_change`; Delivery has verification evidence                                                 |
| Greenfield seed | Project uses RB/UIT but index is empty — seed from product docs + Project Work pointers before deep Implement |

Use `decision_authority: unattended_grant` on the apply path. App preview→apply
readback is still required; skipping readback remains
`card_truth_delivery_claim_without_apply`.

**Must not** mark `updated_on_delivery`, `cards_updated: true`, or
`card_truth_batch_gate.status: passed` without App readback note_id/card_ids.

## Card-Truth Readiness Gate (capability + index integrity)

Run at unattended entry and again before claiming RB/UIT Delivery closed. This
gate checks **readiness**, not user batch approval.

### Gate steps

1. **External Capability Inventory** (unattended contract): include
   `window_capability` for E2E when UIT vision is in scope.
2. **App capability**: Local HTTP reachable; when UIT card-back screenshots are
   required, advertise `review-note: field-media.upload`. Missing →
   `card_truth_batch_gate.status: blocked` with resume condition (rebuild/restart
   App) — **not** silent defer while code keeps changing.
3. **Auto seed / apply (unattended)**: For every `gap` / empty index row /
   pending `will_change` without readback apply in this wave:
   - Knowledge assessment preview → apply
   - Materialization preview → apply
   - Upsert `reality_boundary_index` / `route_ui_truth_index` from readback
4. **Readiness lint**:

   ```text
   python3 skills/granoflow-agent-workflow/scripts/lint_unattended_card_truth_ready.py \
     --snapshot path/to/project_snapshot.yaml \
     [--capabilities path/to/capabilities.json] \
     [--require-uit-index] \
     [--require-rb-index] \
     [--require-field-media]
   ```

5. **Then** continue solvable engineering + E2E + freshness-gated vision.
   Further RB/UIT `will_change` in later tasks **Must** apply in those tasks'
   Delivery waves — not parked for a separate interactive session.

### Machine fields (Task Work / SoT / campaign)

```yaml
card_truth_batch_gate:
  status: pending | passed | not_applicable | blocked
  unattended_apply_enabled: true
  last_apply_at: <ISO-8601|null>
  uit_index_count: <int>
  rb_index_count: <int>
  field_media_capability: available | missing | not_required
  blocked_fact_ids: [] # external/capability blockers only
  summary: <one line shown to user>
```

Status meanings:

- `passed` — indices + readback consistent with claimed Delivery; capabilities OK
- `not_applicable` — project does not use RB/UIT indices
- `blocked` — App/capability/external blocker; engineering may continue but
  **Must not** claim RB/UIT Delivery closed
- `pending` — apply not yet attempted for known gaps/changes in this wave

Fail codes:

- `card_truth_batch_gate_missing` — unattended whole-project/final-delivery
  entered without gate status when RB/UIT is in scope
- `card_truth_batch_gate_blocked` — require-uit / field-media / placeholder index
  when product claims UIT/RB truth
- `card_truth_delivery_claim_without_apply` — Delivery claimed
  `updated_on_delivery` / `cards_updated: true` without App readback apply in
  the same wave

## Unattended behavior (after readiness)

| Work                                                | Unattended                                                                 |
| --------------------------------------------------- | -------------------------------------------------------------------------- |
| Code, IT, E2E, vision (freshness), fix loops        | Auto                                                                       |
| RB/UIT seed (`gap`) / `will_change` apply           | **Auto** (preview→apply→index upsert)                                      |
| Plan/Delivery `card_change_*_notice` display        | Auto (notice, not approval)                                                |
| Task retrospective review cards                     | Defer (`subjective_acceptance`)                                            |
| Stale UIT vision fail                               | Fix code/E2E **and** refresh UIT card text in same wave when `will_change` |
| External-only block (App down, field-media missing) | `blocked` + Residual; do not fake apply                                    |

## GranoReader first-wave UIT

Seed package: product repo `temp/uit-pilot/seed-notes.yaml` + `apply-seed.md`.
Empty `route_ui_truth_index: []` means unattended **Must** run seed apply
before claiming UIT truth closed — not defer to a later interactive batch.
