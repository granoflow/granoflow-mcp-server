# Library Knowledge Notes

Use this reference when **cross-project third-party library knowledge** should
be durable, searchable, and linkable from Project Work—without duplicating API
manuals or project-specific selection prose.

This is a **theme contract + location key** layer. Card quality, similarity
search, Knowledge assessment, and preview/apply confirmation still follow
`granoflow-review-card-draft` and `knowledge-distillation-workflow`. Do not
invent a second authoring path.

Related: `project-work-document-template.md`, `knowledge-distillation-workflow.md`,
`implementation-learning-ledger.md`, `product-truth-sot-layers.md`,
`third-party-capability-matrix.md`, `stack-realization-notes.md`.

## Goal

- **One package = one Note** keyed by `LIB-pub-<slug>` (not one mega-note per
  framework such as “Flutter”).
- **API / manual material** lives in the Note **References** section with
  official links (`reference_only`); **do not** create Cards for volatile API
  syntax, field catalogs, or version-specific signatures.
- **Cross-project lessons** (pitfalls, abandoned approaches, platform traps,
  deprecation, license/security red lines) update the Note; **Cards are
  optional** and only when active recall is justified.
- **Project Work** keeps short `selection_rationale` plus `knowledge_ref`
  pointers—never a parallel library treatise.

## Defaults (phase 1)

- **Do not change the App.** Reuse Knowledge materialization:
  assessment disposition `defer_active_learning` → Note + optional
  `archived_reference` cards.
- **Do not use** `review_card_authoring` `create_note_cards` as the primary
  write path: that path does not set `memory_disposition` and creates
  practice-ready learning cards by default.
- **Init must not** batch-create pitfall Cards for every approved package.

## Identity: `fact_id`

Format: `LIB-pub-<slug>` where `<slug>` normalizes `engineering.dependencies.approved[].name`:

- lowercase ASCII
- `_` → `-`
- no spaces

Examples:

- package `drift` → `LIB-pub-drift`
- package `flutter_tts` → `LIB-pub-flutter-tts`
- npm package `@scope/pkg` → document the approved `name` field; slug uses the
  stored `name` after normalization (agents must not invent a second id).

Rules:

- Stable across projects; one Note per `fact_id` globally.
- Never create a second Note for an existing `fact_id`.
- Rename only with explicit migration: update Note title/content, card
  `sourceSummary`, and every Project Work `knowledge_ref` that points at it.

## Project Work pointer (not body prose)

Each `engineering.dependencies.approved[]` row may carry:

```yaml
knowledge_ref: LIB-pub-drift # null until linked
knowledge_link_status: linked # linked | skeleton | gap | superseded
superseded_by: null # LIB-pub-<slug> when this package was replaced
knowledge_gap_reason: null # required when knowledge_link_status: gap
```

Lint: `lint_library_knowledge_refs.py` (optional `--require-init-ready` at Step 1
confirm).

## Note shape

**Title:** `[LIB-pub-<slug>] <package display name>`

Example: `[LIB-pub-drift] drift (embedded DB)`

**Content** (fixed skeleton):

```markdown
fact_id: LIB-pub-drift
kind: library_knowledge
package_name: drift
ecosystem: pub.dev
last_changed_at: <iso8601 or null>
superseded_by: null
---

## 简介

One plain-language sentence: what this library is for in products like ours.

## References（reference_only）

- Official docs: <url>
- Package registry: <url>
- Version notes: <short pointer only; no API Card>

## Cross-project lessons

- L1: <pitfall / abandoned approach / platform trap + boundary>
- L2: ...

## Card index（optional）

- C1: <one-line recall cue → defers to archived card id when present>
```

Keep **project selection rationale** in Project Work `selection_rationale`
(one short paragraph). Do not paste the full lesson list into Project Work.
Dual-write → `product_truth_dual_write_forbidden` (library column in
`product-truth-sot-layers.md`).

## Card admission

**Note-first.** Default `knowledge_action: update_note`. When unsure whether a
lesson is a red-line → **no Card**.

Decision order for material implementation learning (including **AI self-discovered
fixes** the user never saw):

1. **Always** record a `material` ledger row when the materiality gate passes
   (`implementation-learning-ledger.md`).
2. **Default** promote through Experience → update the **LIB Note** lesson
   section (`knowledge_action: update_note`).
3. **Add a Card** (`knowledge_action: add_card`) only when **all** hold:
   - Knowledge Assessment approves active recall / `defer_active_learning`;
   - reusable on another comparable project;
   - forgetting plausibly causes wrong decision, rework, or platform failure;
   - lookup at action time is worse than remembering one crisp rule;
   - stable boundary exists.
     Otherwise keep `update_note` (AI self-fix still updates the Note when
     reusable, without a Card).
4. Route API catalogs, commands, paths, and volatile syntax as
   `reference_only` (Note link only, **no Card**).
5. Route enforceable rules to `system_managed` when a linter/test/guard is the
   better carrier; Card remains optional archived reference.

Card shape when created:

| Field           | Rule                                                                       |
| --------------- | -------------------------------------------------------------------------- |
| `front`         | Short red-line cue (human-readable)                                        |
| `back`          | Correct rule + boundary                                                    |
| `sourceSummary` | Must include full `fact_id` (primary retrieval key)                        |
| disposition     | `defer_active_learning` → `archived_reference` unless user activates study |

Prefer **one Card per independent recall unit**, not one Card per API symbol.

## Boundary table (do not merge)

| Topic                         | Owner                                                       |
| ----------------------------- | ----------------------------------------------------------- |
| Which package is chosen       | PW `dependencies.approved` + Engineering Acceptance Pack §1 |
| Runtime probe / fallback      | `engineering.third_party_capabilities`                      |
| HTML role → Widget mapping    | Task `stack_realization_notes` (task-local, not LIB)        |
| Product screen / journey      | PW inventory + UIT cards                                    |
| Status quo / product boundary | RB cards + `reality_boundary_index`                         |
| Cross-project library lessons | **LIB Note** (+ optional Cards)                             |
| Init selection why            | PW `selection_rationale` (short); long lessons → LIB Note   |

## Init handoff (Project Definition Step 1)

Immediately after writing `dependencies.approved` rows (same Step 1 pass):

1. For each approved package, compute expected `LIB-pub-<slug>`.
2. Search App Knowledge: `granoflow_task_knowledge_pack` and/or
   `granoflow_review_card_similar` with `fact_id` + package name keywords.
3. **Hit** → set `knowledge_ref`, `knowledge_link_status: linked`; Assessment
   may return `use_existing_knowledge` (link, do not duplicate Note).
4. **Miss** → create **skeleton Note** (简介 + registry/docs links only);
   set `knowledge_link_status: skeleton`. Do **not** create pitfall Cards at
   init.
5. **Search blocked / intentionally deferred** → `knowledge_link_status: gap`
   with `knowledge_gap_reason` (blocks `--require-init-ready` until resolved).

Interactive: present link/skeleton/gap summary in the library batch when
possible. Unattended: adopt search-first results under explicit Mode Gate.

## Implementation handoff

When a material ledger event involves an approved third-party package:

1. Set `target_library_ref` to the matching `LIB-pub-<slug>`.
2. Set `knowledge_action`:
   - `update_note` — default for new lesson text;
   - `add_card` — when Assessment approves active recall;
   - `contradict` — outcome challenges prior lesson (Usage + Note update);
   - `supersede` — package replaced; update Note + PW `superseded_by` fanout;
   - `none` — material but not library-scoped (leave null / omit ref).
3. Deferred Task Review → Experience authoring → Knowledge Assessment →
   materialization. **Do not** skip preview/apply gates.
4. Delivery reconciles ledger `ledger_sha256`; Card promotion remains
   independent of Delivery write.

Fail-closed when library-scoped material event lacks ref:
`implementation_learning_library_ref_missing`.

## Deprecation and package change

When abandoning package A for package B:

1. Update PW row: new `name`, `knowledge_ref: LIB-pub-B`, prior Note gets
   `superseded_by: LIB-pub-B` in content frontmatter.
2. Run change-impact fanout on dependent tasks and capability matrix rows.
3. Merge portable lessons from A’s Note into B’s Note; archive A’s Note or
   mark read-only with pointer—never two active Notes for the same capability
   without explicit migration.

## Override: `card-quality-defaults`

When `kind: library_knowledge`, the universal professional-term rule **does not**
require definition + analogy + Card for every API symbol. The Note **简介**
section satisfies the plain-language definition requirement. Cards remain
optional and lesson-scoped. See `granoflow-review-card-draft/references/card-quality-defaults.md`.

## Add / update flow

```text
1. Read PW approved[].knowledge_ref for package name
2. granoflow_review_card_similar / task_knowledge_pack with LIB-pub-<slug>
3. AI-filter: same_knowledge if fact_id matches title/sourceSummary/content
4. Hit → update_existing / use_existing_knowledge
   Miss → assessment (defer_active_learning or reference_only) → materialization
5. Refresh PW knowledge_link_status when first linked or superseded
6. Forbid second Note for same fact_id
```

## Stock migration checklist (manual, per project)

Execute outside init Hard Gates; use when cleaning legacy messy Notes/Cards:

1. Export `dependencies.approved` package list from Project Work.
2. For each package, search/create `LIB-pub-*` Note.
3. Merge scattered library-themed Review Cards into the matching LIB Note;
   keep at most red-line archived Cards.
4. Delete or archive API-quiz Cards; move links into Note References.
5. Shorten PW library prose; set `knowledge_ref` + `knowledge_link_status`.
6. Split any “Flutter mega-note” into per-package LIB Notes aligned with
   `approved`.
7. Leave `stack_realization_notes` in tasks; do not merge into LIB.
8. Re-run `lint_library_knowledge_refs.py --require-init-ready` before Step 1
   re-confirm if applicable.

## Fail-closed codes (document gate)

- `library_knowledge_ref_invalid` — malformed `knowledge_ref`
- `library_knowledge_link_incomplete` — init-ready missing status or linked ref
- `library_knowledge_slug_mismatch` — `linked` ref slug ≠ normalized `name`
- `implementation_learning_library_ref_missing` — material library event without ref
