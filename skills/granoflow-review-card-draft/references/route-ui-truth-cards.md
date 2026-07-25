# Route UI Truth Cards（界面真相）

Use this reference when a project's **route screens（路由主界面）** and
**operation overlays（操作界面）** should become durable, searchable Knowledge
for agents—so UI truth does not drift relative to code / E2E.

Mirror the Reality Boundary pattern (`reality-boundary-cards.md`): theme
contract + location key + index. Card quality and preview/apply still follow
the parent `granoflow-review-card-draft` skill.

## Goal

- One **route screen** = **one Note** + ≥1 `archived_reference` card
- Each **operation overlay** on that route = **one** archived card (same Note),
  front describes differences vs the host route
- Stable key = `fact_id` + `route_ui_truth_index` (not a deck path)

## Relationship to Project Work

See `granoflow-agent-workflow/references/product-truth-sot-layers.md`.

| Layer | Owner |
| --- | --- |
| Screen inventory + short declared `ui_details` | Project Work |
| “Looks like now”, checklist, card-back WebP | **These UIT cards** |
| Hard Gate one-liners | `project_rules` / snapshot |

Do **not** copy UIT detail back into Project Work body. PW may store
`uit_fact_id` only. Dual-write → `product_truth_dual_write_forbidden`.

## Defaults

- Reuse Knowledge materialization: `defer_active_learning` → Note +
  `archived_reference` cards.
- Do **not** use `create_note_cards` as the primary write path.
- Screenshots: E2E capture → App WebP ≤300KB → note image field → place on
  card **back** via `granoflow_review_note_field_media_upload`
  (`fieldKey` default `custom_uit_screenshot`, `layoutSide: back`).

## Identity: `fact_id`

Format: `UIT-<stable-slug>` (ASCII kebab-case).

Examples:

- `UIT-welcome`
- `UIT-bookshelf`
- `UIT-reader`
- `UIT-settings`

Rules:

- Stable across edits; never create a second Note for an existing `fact_id`.
- Prefer slug aligned with `screen_id` / route id (`S-bookshelf` → `UIT-bookshelf`).

## Note shape

**Title:** `[UIT-<slug>] <short Chinese screen name>`

**Content** skeleton:

```markdown
fact_id: UIT-bookshelf
kind: route_ui_truth
route_id: S-bookshelf
project_id: <uuid>
last_changed_in_milestone: <id or null>
---

## 路由职责

...

## Checklist（识图硬点）

- C1: ...
- C2: ...

## 操作界面（相对主屏差异）

- OP-<id>: trigger=...; delta=...
```

## Card shape

| Card              | Front                                      | Back                                                         |
| ----------------- | ------------------------------------------ | ------------------------------------------------------------ |
| Route main        | Screen name / one-line duty                | WebP screenshot field + short state notes                    |
| Operation overlay | Trigger + relative delta vs host route     | Optional overlay WebP (only when op vision is opted in)      |

`sourceSummary` **Must** include the full `fact_id`.

## Project index

```yaml
route_ui_truth_index:
  - fact_id: UIT-bookshelf
    note_id: ...
    card_ids: [...]
    title: 书架
    route_id: S-bookshelf
    updated_at: ...
```

Pointer only—App Note/Card remain content SoT.

## Vision + freshness（省流）

Track per `fact_id` / `op_id`:

| Field | Meaning |
| --- | --- |
| `screenshot_at` | Last successful card-back upload / capture time (App readback preferred) |
| `ui_changed_at` | Last Delivery update for that UIT theme (`will_change` → `updated_on_delivery` / index `updated_at`) |

Rule:

- `screenshot_at >= ui_changed_at` → **skip** recapture, re-upload, and vision (`skipped_fresh`)
- otherwise (stale, missing image, or missing timestamps) → **must** screenshot → upload → vision

Do **not** warn users that vision is “expensive” or ask permission to skip for
cost: with freshness skip, automatic vision is the default and is worth running
when stale.

### Route main screens

- Checklist vision against the card-back WebP when stale.
- Failure:
  - **interactive**: alert + human review images (do not auto-edit code)
  - **unattended**: enter fix flow directly

### Operation overlays

- Text deltas remain SoT; widget/semantic E2E asserts remain.
- Vision runs **automatically in both interactive and unattended** when stale
  (same freshness rule). No cost ask / no unattended default skip.
- Never treat pixel-diff ≈ prose as a hard assert.

## Anti-Drift Lifecycle

Same four steps as Reality Boundary, with `route_ui_truth_*` fields:

1. **Find** — Full `route_ui_truth_index` enumeration (`related` per row).
   Forbid vector top-k as relatedness SoT.
2. **Classify** — `unrelated` | `unchanged` | `will_change` | `gap`.
3. **Verify** — `will_change` needs `verification_refs` (E2E step / screenshot /
   checklist id).
4. **Announce + Update** — Shared `card_change_*_notice` with
   `kind: route_ui_truth`; Delivery updates the **same** `fact_id`.

### Lint

```text
python3 skills/granoflow-agent-workflow/scripts/lint_plan_route_ui_truth.py \
  path/to/task-work.yaml \
  [--snapshot path/to/project_snapshot.yaml]

python3 skills/granoflow-agent-workflow/scripts/lint_delivery_card_change_notice.py \
  path/to/task-work.yaml
```

Fail-closed codes: `route_ui_truth_check_missing`,
`route_ui_truth_will_change_without_verification`,
`route_ui_truth_delivery_stale`, plus shared
`card_change_*_notice_missing`.

### Machine fields

```yaml
route_ui_truth_check_status: not_applicable | missing | checked_unchanged | checked_will_change | updated_on_delivery
route_ui_truth_fact_ids: [UIT-...]
route_ui_truth_will_change: [UIT-...]
route_ui_truth_index_review:
  - fact_id: UIT-bookshelf
    related: true
    disposition: unchanged
    note_id: ...
    card_ids: [...]
    verification_refs: []
route_ui_truth_not_applicable_reason: null
# Prefer on route_ui_truth_index rows (and op entries):
#   screenshot_at: <ISO-8601>
#   ui_changed_at: <ISO-8601>
```

## First-wave GranoReader routes

`S-welcome`, `S-create_library`, `S-bookshelf`, `S-import_preview`,
`S-reader`, `S-reader_search`, `S-book_detail`, `S-settings`.

## Unattended

Follow `granoflow-agent-workflow/references/unattended-card-truth-batch-gate.md`:

1. Interactive batch: seed / `will_change` Knowledge apply + index upsert
2. `lint_unattended_card_truth_ready.py --require-uit-index --require-field-media`
   (when card-back screenshots are in scope)
3. Then unattended engineering + E2E + freshness vision

Unattended **Must not** apply UIT Notes/cards. Vision→fix may change code;
new card prose still needs a later interactive batch.

## Forbidden

- Second Note for an existing `UIT-*`
- Skipping stale vision for cost / “ask the user if vision is worth it”
- Claiming unattended Delivery closed UIT truth without the Card-Truth Batch Gate
- Using embedding similarity instead of full index enumeration
- Treating operational pixel-diff as the sole green light
