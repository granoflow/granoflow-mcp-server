# Reality Boundary Cards

Use this reference when a project’s **status quo（现状）** and **boundaries（边界）**
should become durable, searchable Knowledge for agents—not active study load.

This is a **theme contract + location key + index** layer. Card quality,
similarity search, and preview/apply confirmation still follow the parent
`granoflow-review-card-draft` skill. Do not invent a second authoring path.

## Goal

- One theme = **one Note** (body states status quo and the boundary group together)
- Each boundary = **one front/back archived card** (`archived_reference`)
- Stable location key = `fact_id` + project snapshot index (not a deck path)

## Defaults (phase 1)

- **Do not change the App.** Reuse Knowledge materialization:
  assessment disposition `defer_active_learning` → Note + `archived_reference` cards.
- **Do not rely on milestone subdecks.** Materialization often lands in「未归类」;
  the canonical place is `fact_id` + `reality_boundary_index`.
- **Do not use** `review_card_authoring` `create_note_cards` as the primary write
  path for these themes: that path does not set `memory_disposition` and creates
  practice-ready learning cards.

## Identity: `fact_id`

Format: `RB-<stable-slug>` (ASCII kebab-case).

Examples:

- `RB-library-encryption`
- `RB-sample-book`
- `RB-platform-scope`
- `RB-e2e-residuals`

Rules:

- Stable across edits; rename only with an explicit migration that updates the
  Note title/content, all boundary cards’ `sourceSummary`, and the index.
- Never create a second Note for an existing `fact_id`.

## Note shape

**Title:** `[RB-<slug>] <short Chinese theme>`

Example: `[RB-library-encryption] 书库加密`

**Content** (fixed skeleton):

```markdown
fact_id: RB-library-encryption
kind: reality_boundary
project_id: <uuid>
last_changed_in_milestone: <id or null>
---

## 现状

...

## 边界

- B1: ...
- B2: ...
```

Keep Hard Gate **one-line** summaries in `project_rules.yaml` /
`project_snapshot.yaml`; detail migrates into these Notes/cards over time.
Project Work must **not** keep a parallel boundary treatise—only optional
`rb_fact_id` pointers (`product-truth-sot-layers.md`). Dual-write →
`product_truth_dual_write_forbidden`.

## Card shape

For each boundary line:

| Field           | Rule                                                                                                        |
| --------------- | ----------------------------------------------------------------------------------------------------------- |
| `front`         | Short boundary title (human-readable cue)                                                                   |
| `back`          | Boundary points / consequences                                                                              |
| `sourceSummary` | Must include the **full** `fact_id` (retrieval primary key). Prefer `fact_id` alone or `fact_id \| <theme>` |

Optional: put `fact_id` and the Chinese theme in Note title and content so
keyword fallback can hit without the index.

## Project index

Write/update `reality_boundary_index` on `project_snapshot.yaml`
(see `granoflow-agent-workflow/references/project-context-attachments.md`):

```yaml
reality_boundary_index:
  - fact_id: RB-library-encryption
    note_id: ...
    card_ids: [...]
    title: 书库加密
    updated_at: ...
```

Update rules:

1. After successful materialization readback, upsert the row for that `fact_id`.
2. On boundary add/remove, refresh `card_ids`, Note content, and `updated_at`.
3. On theme merge/retire, remove or redirect the index row in the same write.
4. Index is the fast path; App Note/Card rows remain the content SoT.

## Add / update flow

```text
1. Read project_snapshot reality_boundary_index for fact_id
2. If missing, granoflow_review_card_similar with fact_id + theme keywords
3. AI-filter: same_knowledge if fact_id matches title/sourceSummary/content
4. Hit → update_existing_and_link / update Note + cards; refresh index
   Miss → Knowledge assessment (defer_active_learning) → materialization → index
5. Forbid creating a second Note for the same fact_id
```

### Assessment signals (to get `defer_active_learning`)

App gate (do not invent local logic): eligible + `activeRecall: true` +
`budgetAvailable: false` → `defer_active_learning`.

Typical candidate signals for reality/boundary themes:

- `reusable`, `decisionImpact`, `standalone`, `stable`, `activeRecall`: true
- `budgetAvailable`: false (archive reference, not study queue)
- Do **not** set `projectSpecific: true` (App marks that ineligible →
  `reference_only` → zero cards)
- Prefer `scopeType: project` with an `external_reference` (or task/experience)
  source that carries `sourceIdentity` + `sourceHash`

Then:

1. `granoflow_knowledge_assessment_preview` → user/batch approval → `apply`
2. `granoflow_knowledge_materialization_preview` with `assessmentId`, Note
   `title`/`content`, and boundary `cards` (each with `sourceSummary` containing
   `fact_id`) → approval → `apply`
3. Readback `noteId` / `cardIds` → write `reality_boundary_index`

## Retrieve flow

1. Known `fact_id`: read snapshot index → `note_id` / `card_ids` → App get
2. Unknown theme: `granoflow_review_card_similar` with candidate `RB-*` and
   Chinese theme words; AI-filter `same_knowledge`
3. Update boundaries on the **same** Note; refresh index and
   `last_changed_in_milestone`

## Unattended

RB card create/update uses the same Knowledge apply path as UIT. Unattended
**Must** apply preview→apply→index upsert for every Plan `gap` and Delivery
`will_change` in the same wave (`decision_authority: unattended_grant`).
Before claiming RB Delivery closed, run the Card-Truth Readiness Gate
(`granoflow-agent-workflow/references/unattended-card-truth-batch-gate.md`) —
**not** defer because the run is unattended. External-only blockers may set
`card_truth_batch_gate.status: blocked`; do not mark `updated_on_delivery`
without apply readback.

## Forbidden

- Second Note for an existing `fact_id`
- Primary create via practice authoring (`create_note_cards` without
  `archived_reference`)
- Treating deck path /「未归类」as the location SoT
- Carding journey steps or acceptance matrices as reality-boundary themes
- Claiming unattended RB anti-drift Delivery closed without App readback apply
  in the same wave

## Anti-Drift Lifecycle (Task Analysis / Plan / Delivery)

Use Reality Boundary cards to stop **truth drift**: code or observable product
behavior changes while recorded status quo / boundaries stay stale, so the next
Hard Gate or Plan “corrects” the implementation back to the old (wrong) truth.

Applies to: `software_development` tasks, and any project-bound task that will
change material facts in `project_snapshot.yaml` / `project_rules.yaml`.

Does **not** require empty card edits when every related theme is `unchanged`.

Stable key for every step is **`fact_id`** (plus index `note_id` / `card_ids`).
Do **not** use vector similarity scores to decide which themes a task relates
to—same-project RB cards are often too close in embedding space.

### Four steps (Plan → Delivery)

1. **Find** — Load the full `reality_boundary_index`. For **every** index row,
   record `related: true|false` in `reality_boundary_index_review`. Optionally
   run `granoflow_review_card_similar` only as a leak-net; AI-filter hits by
   full `fact_id` in `sourceSummary` / Note title, then merge into the review
   (never replace enumeration with top-k).
2. **Classify** — Each row: `unrelated` | `unchanged` | `will_change` | `gap`.
   `reality_boundary_fact_ids` = rows with `related: true`.
3. **Verify if changing** — Every `will_change` must name verification
   (`verification_refs`: case ids and/or evidence refs) and keep `fact_id` +
   `note_id` / `card_ids`. If `copy_change_only`, document or index readback
   refs are enough—do not invent automated tests.
4. **Announce if changing (hard)** — If `will_change` is non-empty, the Agent
   **Must** emit a user-visible Plan change notice listing every `fact_id`
   (see Explicit Change Notices). Silent `will_change` in YAML only is not
   enough.
5. **Update after pass + announce (hard)** — When verification passes, update
   the **same** `fact_id` Note + boundary cards + index (and Hard Gate short
   summaries if they still state the old truth). Set `updated_on_delivery`.
   Then emit a user-visible Delivery change notice listing every updated
   `fact_id` / `card_ids` and stating cards were updated.

Empty index and task truly has no RB themes: `status: not_applicable`,
`index_review: []`, one-line reason.

### Explicit Change Notices (hard)

Applies to Reality Boundary themes **and** any other review card create/update
in this task (see `lifecycle-card-checkpoints.md`). Rule:

- **Zero card changes planned or applied** → still **Must** show one short
  confirmation line only (no item list, no extra prose). Use `none: true`.
- **Any card will change or did change** → notice is **mandatory**, must be
  shown to the user (`shown_to_user: true`), and must list every item
  (`none` must be absent or false).

Plan notice (before Readiness) — when changes are planned:

```yaml
card_change_plan_notice:
  emitted: true
  shown_to_user: true # Must be true only after the Agent displayed the list
  none: false
  items:
    - kind: reality_boundary # or review_card | experience_card | …
      action: update # create | update | archive
      fact_id: RB-library-encryption # required for reality_boundary
      note_id: ...
      card_ids: [...]
      summary: <one line: what will change in this iteration>
```

Plan notice — when nothing will change (one line only):

```yaml
card_change_plan_notice:
  emitted: true
  shown_to_user: true
  none: true
  summary: 本次迭代无卡片变更
  items: []
```

Delivery / post-implementation — when cards were updated:

```yaml
card_change_delivery_notice:
  emitted: true
  shown_to_user: true
  none: false
  cards_updated: true # Must be true when any listed card/Note write applied
  items:
    - kind: reality_boundary
      action: update
      fact_id: RB-library-encryption
      note_id: ...
      card_ids: [...]
      summary: <one line: what was changed; cards updated>
```

Delivery — when nothing was updated (one line only):

```yaml
card_change_delivery_notice:
  emitted: true
  shown_to_user: true
  none: true
  cards_updated: false
  summary: 本次实施无卡片变更
  items: []
```

For Reality Boundary, every `will_change` `fact_id` **Must** appear in
`card_change_plan_notice.items`, and after apply in
`card_change_delivery_notice.items` with `cards_updated: true`.

### Analysis / Plan

1. Enumerate the full index into `reality_boundary_index_review` (required when
   the Plan Design Gate applies).
2. In Task Work prose, summarize each **related** theme: `fact_id`, one-line
   status quo / boundary, disposition.
3. For every `gap`: record it; create only via Knowledge `defer_active_learning`
   (never a second Note for an existing `fact_id`).
4. **Display** either the Plan change list, or the single line
   「本次迭代无卡片变更」, then set `card_change_plan_notice`
   (`shown_to_user: true`; use `none: true` when unchanged).
5. Before Readiness / `plan_design_gate_status: passed`, run:

   ```text
   python3 skills/granoflow-agent-workflow/scripts/lint_plan_reality_boundary.py \
     path/to/task-work.yaml \
     [--snapshot path/to/project_snapshot.yaml]
   ```

### Delivery

1. After verification passes, every Plan `will_change` `fact_id` **must**
   update the same Note and boundary cards, refresh `reality_boundary_index`,
   and align Hard Gate short summaries in snapshot/rules with the new truth.
2. Readback: index `note_id` matches the Note; cards remain
   `archived_reference`.
3. **Display** either the Delivery change list (what changed + cards updated)
   or the single line 「本次实施无卡片变更」, then set
   `card_change_delivery_notice` (`shown_to_user: true`; `none: true` and
   `cards_updated: false` when unchanged). Run:

   ```text
   python3 skills/granoflow-agent-workflow/scripts/lint_delivery_card_change_notice.py \
     path/to/task-work.yaml
   ```

4. If all related items are `unchanged`, or none apply, record
   `checked_unchanged` or `not_applicable`. Do **not** edit cards only to
   satisfy process. Do **not** invent itemized change lists when `none: true`.
5. Claiming done while `will_change` cards/index still describe the old truth
   fails closed as `reality_boundary_delivery_stale`. Claiming done without the
   required Delivery notice (change list **or** the one-line none confirmation)
   fails as `card_change_delivery_notice_missing`.

### Machine fields (Task Work / Delivery)

```yaml
reality_boundary_check_status: not_applicable | missing | checked_unchanged | checked_will_change | updated_on_delivery
reality_boundary_fact_ids: [RB-...] # related:true subset
reality_boundary_will_change: [RB-...] # subset of fact_ids
reality_boundary_index_review:
  - fact_id: RB-library-encryption
    related: true
    disposition: unchanged # or will_change | gap | unrelated
    note_id: ...
    card_ids: [...]
    verification_refs: [] # required non-empty when disposition=will_change
reality_boundary_not_applicable_reason: null | <one line>
card_change_plan_notice: { emitted, shown_to_user, none, summary, items: [] }
card_change_delivery_notice: { emitted, shown_to_user, none, cards_updated, summary, items: [] }
```

### Fail-closed codes

- `reality_boundary_check_missing` — Gate-required Plan missing status /
  `index_review`, illegal disposition, incomplete index coverage (with
  `--snapshot`), or `will_change` not listed in `reality_boundary_fact_ids`
- `reality_boundary_will_change_without_verification` — `will_change` without
  non-empty `verification_refs` (Plan) or without verification evidence
  (Delivery)
- `card_change_plan_notice_missing` — missing user-visible Plan notice: either
  itemized changes, or `none: true` plus one-line `summary` when nothing changes
- `card_change_delivery_notice_missing` — missing user-visible Delivery notice:
  either itemized updates with `cards_updated: true`, or `none: true` plus
  one-line `summary` when nothing changed
- `reality_boundary_delivery_stale` — `will_change` verified but Note / cards /
  index (and needed Hard Gate short summaries) were not updated to the new truth

Plan Design Gate + `lint_plan_reality_boundary.py` enforce the Plan half
(including Plan notice). Delivery uses
`lint_delivery_card_change_notice.py` plus profile omit-checks. This reference
owns RB semantics; universal card notices are owned with
`lifecycle-card-checkpoints.md`.

## Success checks

- Add path always checks index + similar search before create
- Cards are `archived_reference` (not in the learning queue)
- Re-retrieve by `fact_id` returns the same `note_id`
- Software Plan enumerates full index in `index_review`; lint green before
  Readiness; `will_change` has verification refs **and** a user-visible Plan
  notice (or the one-line none confirmation); Delivery updates the same
  `fact_id` after pass **and** shows a Delivery notice with
  `cards_updated: true` (or the one-line none confirmation)
