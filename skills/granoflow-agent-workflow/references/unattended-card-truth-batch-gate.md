# Unattended Card-Truth Batch Gate（交互批卡闸）

Owner for splitting **interactive Knowledge/card writes** from **unattended
engineering campaigns** after Reality Boundary (`RB-*`) and Route UI Truth
(`UIT-*`) anti-drift.

Parent contracts: `unattended-interaction-contract.md`,
`lifecycle-card-checkpoints.md`, `reality-boundary-cards.md`,
`route-ui-truth-cards.md`, `long-task-run-continuity.md`.

## Problem

Unattended **Must not** apply Note/Card / Knowledge materialization
(`subjective_acceptance`). Delivery anti-drift **Must** update the same
`fact_id` when Plan marks `will_change`. Claiming both “full unattended” and
“RB/UIT truth closed” without a prior interactive batch is fail-closed
dishonesty.

## Split claim (hard)

| Claim                                                      | Allowed when                                                                                                                                                 |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Unattended engineering campaign → E2E → `project_complete` | Card writes are either already applied, or deferred as Residual (`subjective_acceptance`) — **not** silently skipped while status says `updated_on_delivery` |
| RB/UIT anti-drift Delivery closed                          | Interactive (or explicit batch grant) completed preview→apply for every `will_change` / seed fact_id in the same wave                                        |

Do **not** tell the user “SoT guarantees unattended through Delivery including
UIT/RB truth” unless the batch gate below is green.

## Interactive Card-Truth Batch Gate

Run **before** entering or continuing whole-project / milestone-wide /
final-delivery **unattended** when the project uses RB and/or UIT indices.

### Gate steps

1. **External Capability Inventory** (unattended contract): include
   `window_capability` for E2E.
2. **App capability**: Local HTTP advertises `review-note: field-media.upload`
   when UIT screenshots must land on card backs. Missing → rebuild/restart App
   or defer UIT media with resume condition (do not fake upload).
3. **Seed / gap batch (interactive)**: For every first-wave or `gap` fact_id
   without index `note_id`:
   - Knowledge assessment preview → **user/batch approve** → apply
   - Materialization preview → **user/batch approve** → apply
   - Upsert `reality_boundary_index` / `route_ui_truth_index` from readback
4. **Pending `will_change` batch (interactive)**: If any open task Plan already
   lists `will_change` that is not yet `updated_on_delivery`, finish those card
   updates interactively (or park them — do not start unattended claiming they
   are done).
5. **Readiness lint** (same wave):

   ```text
   python3 skills/granoflow-agent-workflow/scripts/lint_unattended_card_truth_ready.py \
     --snapshot path/to/project_snapshot.yaml \
     [--capabilities path/to/capabilities.json] \
     [--require-uit-index] \
     [--require-field-media]
   ```

6. **Then** enter unattended for solvable engineering + E2E + vision→fix.
   Card apply remains forbidden until another interactive batch.

### Machine fields (Task Work / SoT / campaign)

```yaml
card_truth_batch_gate:
  status: pending | passed | not_applicable | deferred
  interactive_batch_completed_at: <ISO-8601|null>
  uit_index_count: <int>
  rb_index_count: <int>
  field_media_capability: available | missing | not_required
  deferred_fact_ids: [] # residual subjective_acceptance
  summary: <one line shown to user>
```

Fail codes:

- `card_truth_batch_gate_missing` — unattended whole-project/final-delivery
  entered without gate status
- `card_truth_batch_gate_blocked` — require-uit / field-media / empty index when
  product claims UIT/RB truth
- `card_truth_delivery_claim_without_apply` — Delivery claimed
  `updated_on_delivery` / `cards_updated: true` without App readback apply in
  this or a prior interactive batch

## Unattended behavior after gate

| Work                                         | Unattended                                                                                                                       |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Code, IT, E2E, vision (freshness), fix loops | Auto                                                                                                                             |
| Plan/Delivery `card_change_*_notice` display | Auto (notice, not approval)                                                                                                      |
| New Note/Card / Knowledge apply              | **Forbidden** — preview → Residual                                                                                               |
| Stale UIT vision fail                        | Enter fix (code/E2E); if fix needs new card text, park card update for next interactive batch                                    |
| Final wording                                | `project_complete` with Residual for cards/`user_final_acceptance` **or** stop for interactive final acceptance — never conflate |

## GranoReader first-wave UIT

Seed package: product repo `temp/uit-pilot/seed-notes.yaml` + `apply-seed.md`.
Empty `route_ui_truth_index: []` means gate **not** passed for UIT truth claims
until materialization readback fills rows.
