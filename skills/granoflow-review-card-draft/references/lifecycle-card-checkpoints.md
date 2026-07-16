# Task Lifecycle Card Checkpoints

This is the canonical phase contract for review cards used by Granoflow task workflows. The parent `granoflow-review-card-draft` skill remains the sole owner of similarity search, classification, card quality, preview, approval, apply, and practice-ready readback. Task Work, Execution, Delivery, Completion, and Deferred Review must link here instead of copying that algorithm. Historical Analysis and Plan checkpoints remain valid legacy provenance.

## Phase Model

Card Checkpoints exist at `task_work | execution | delivery | deferred_review`. Completion does not run a new checkpoint; it reads and summarizes the Delivery checkpoint. Read legacy `analysis | plan` values without rewriting them.

At each checkpoint:

1. Re-read the latest task and linked cards, then search for similar cards when relevant.
2. Use reliable existing cards as input to the current phase.
3. Classify any material knowledge delta as link, update, create, unchanged, deferred, or conflict.
4. Route every proposed write through the parent skill's preview and operation-level approval flow.
5. Apply only approved operations and require App-owned `practiceReady: true` readback.
6. Persist the checkpoint result in the phase document or node evidence.

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

- Task Work establishes the knowledge baseline during Analysis and reconciles decision boundaries, terminology, rules, and risks when Planning is triggered. A later Work Document version does not recreate unchanged knowledge.
- Execution runs a checkpoint only on a material knowledge/card delta such as a correction, verified fact, confirmed rule change, or reusable experience.
- Delivery reconciles cards with the actual result and records accepted, overturned, or deferred Work Document assumptions. Legacy Delivery may refer to Analysis/Plan assumptions.
- Deferred Review performs final deduplication, quality audit, and evidence-backed experience capture; it is not the first bulk-card pass.

An unattended runner may read cards and record candidates, but it cannot infer operation approval. It records proposed writes as `deferred` and continues safe work when the task contract permits.
