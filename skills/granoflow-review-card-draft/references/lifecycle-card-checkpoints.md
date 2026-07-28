# Task Lifecycle Card Checkpoints

This is the canonical phase contract for review cards used by Granoflow task workflows. The parent `granoflow-review-card-draft` skill remains the sole owner of similarity search, classification, card quality, preview, approval, apply, and practice-ready readback. Task Work, Execution, Delivery, Completion, and Deferred Review must link here instead of copying that algorithm. Historical Analysis and Plan checkpoints remain valid legacy provenance.

## Phase Model

Card Checkpoints exist at `task_work | execution | delivery | deferred_review`. Completion does not run a new checkpoint; it reads and summarizes the Delivery checkpoint. Read legacy `analysis | plan` values without rewriting them.

At each checkpoint:

1. Re-read the latest task and linked cards, then search for similar cards when relevant.
2. Use reliable existing cards as input to the current phase.
3. Classify any material knowledge delta as link, update, create, unchanged, deferred, or conflict.
4. **Allowlist:** create/update Cards only for `RB-*` / `UIT-*` / Card-worthy
   `LIB-pub-*` (see parent skill Card Allowlist). Generic Card ideas without an
   explicit user request → `deferred` (or Experience / ledger), never create.
5. Route every proposed **allowlisted** write through the parent skill's
   preview and operation-level approval flow.
6. Apply only approved operations and require App-owned `practiceReady: true` readback.
7. Persist the checkpoint result in the phase document or node evidence.
8. **Explicit change notice (hard):** The Agent **Must** show a user-visible
   notice and record `card_change_plan_notice` (Plan / Task Work) or
   `card_change_delivery_notice` (Execution apply / Delivery) with
   `shown_to_user: true`. If any card create/update/archive is planned or
   applied (Reality Boundary, Route UI Truth, Library Knowledge, or an
   explicitly requested generic card), list every item; Delivery applied
   writes **Must** set `cards_updated: true`. If zero cards change, show
   **only** one confirmation line (`none: true`, e.g. 「本次迭代无卡片变更」/
   「本次实施无卡片变更」)—no item list. Missing notices fail closed as
   `card_change_plan_notice_missing` or `card_change_delivery_notice_missing`.
   Reality Boundary details: `reality-boundary-cards.md` Anti-Drift. Route UI
   Truth details: `route-ui-truth-cards.md` Anti-Drift (freshness + auto
   vision). Unattended whole-project runs that claim RB/UIT Delivery closed
   must pass `unattended-card-truth-batch-gate` first.

Before preview, validate every proposed Note: its body must contain at least
one concrete example of the knowledge in use. If the knowledge is abstract,
defines a boundary, contains a trade-off, or is easy to misunderstand, the Note
must also contain a plain-language analogy, contrast, or intuitive explanation.
This explanatory material belongs in the Note; Card fronts and backs remain
concise recall prompts and answers.

Search and read operations are safe before confirmation. Search results, a prior phase approval, task completion, or general interest never authorize a card write. Approval of an Analysis draft and approval of card `approvedOperationIds` are separate decisions, even if one natural-language reply explicitly grants both.

## Canonical Record

```yaml
card_checkpoint:
  phase: task_work | execution | delivery | deferred_review
  checked_at: <timestamp>
  based_on_task_updated_at: <timestamp>
  based_on_card_updated_at_by_id: {}
  based_on_note_updated_at_by_id: {}
  preview_hash: null | <hash>
  input_card_ids: []
  operations:
    linked: []
    created: []
    updated: []
  applied_operation_ids: []
  deferred_operation_ids: []
  failed_operation_ids: []
  unchanged_card_ids: []
  candidates: []
  status: completed | partial | deferred | conflict | verification_failed | not_applicable
  change_summary: changed | unchanged
  evidence: []
  deferred_reason: null | <reason>
  readback: completed | not_required | failed
```

`status` describes execution of the checkpoint; `change_summary` describes whether knowledge or card associations changed. `completed + unchanged` is a successful check, not a skipped one. Fill linked/created/updated only after successful apply and practice-ready readback. A mixed batch uses `partial`, with applied, deferred, and failed operation IDs kept separately.

Candidates contain only a minimal summary, `origin_phase`, evidence still needed, and `revisit_phase`. When knowledge appears in one phase and is validated or applied later, record `origin_phase`, `validated_phase`, and `applied_phase` in phase evidence; these are document provenance, not database fields.

Use `conflict` for stale previews or an unsafe shared-note merge. Use `verification_failed` when apply may have succeeded but readback did not prove the result; re-read before any retry. Phase documents may persist `preview_hash` for audit but must not persist `previewToken`.

## Capability And Task Eligibility

Discover capabilities from the running App before authoring. The current contract is `taskRequired=true`, `projectTaskRequired=false`, `inboxTaskAuthoring=true`, and `uncategorizedDeckFallback=true`. Any existing, non-deleted task is eligible; cards created for inbox tasks use the App-owned uncategorized deck. A missing or deleted task returns `task_not_found`.

For an older App that advertises `projectTaskRequired=true`, project tasks may use its legacy path, while inbox-task writes are `deferred` with a capability reason. If these capability fields are absent, do not assume inbox authoring support. Never move an inbox task into a project merely to create a card.

## Phase Responsibilities

- Task Work establishes the knowledge baseline during Analysis and reconciles decision boundaries, terminology, rules, and risks when Planning is triggered. A later Work Document version does not recreate unchanged knowledge. Prefer linking allowlisted themes; do not open a generic Card batch.
- Execution runs a checkpoint only on a material knowledge/card delta such as a correction, verified fact, confirmed rule change, or reusable experience. **Must not** create generic Cards unless the user explicitly asked; allowlisted RB/UIT/LIB updates follow their theme contracts.
- Delivery reconciles allowlisted cards with the actual result and records accepted, overturned, or deferred Work Document assumptions. Legacy Delivery may refer to Analysis/Plan assumptions.
- Deferred Review performs final deduplication, quality audit, and evidence-backed experience capture; it is not a bulk generic-card pass. Card session only for allowlisted candidates or explicit user request.

An unattended runner may read cards and record **allowlisted** candidates, but it cannot infer operation approval. It **must not** invent generic Card write plans. During a review, carry allowlisted candidates into the parent skill's Review-Ending Authoring Session (when the allowlist/session gate permits), run the App-owned dry-run preview, display the complete Note/Card set, and stop for genuine user editing and approval. Record proposed writes as `deferred` and continue safe work before that final stop when the task contract permits. A general unattended instruction never authorizes Note/Card creation, linking, or modification.
