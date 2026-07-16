# Knowledge Distillation Workflow

Read this reference whenever task analysis retrieves prior work, a task or periodic review proposes Experience, an Experience may become Knowledge, Knowledge may produce Cards or controls, or a Task Work reference changes.

## Domain Layers

- `Evidence` is a concrete statement owned by one Task and its specific Task Review revision. It does not exist independently of that task.
- `Experience` is an independent, reusable lesson with conclusion, rationale, context, boundary, and next action. It may summarize several Evidence or Review sources and may later assist many tasks.
- `Knowledge Assessment` decides whether a source is reusable Knowledge and routes it to `reference_only`, `system_managed`, `active_learning`, `defer_active_learning`, or `use_existing_knowledge`.
- `Knowledge` content is one existing Review Note plus at least one Card when materialized. There is no parallel Knowledge正文 object.
- `Task Work Reference` records a source actually adopted by the current task. `Knowledge Usage` separately records referenced, applied, validated, or contradicted use history.

Task, Meeting, Reading, and Decision are not separate persisted task types. When one matters to work, create or retrospectively add a normal Task and place its specific statements in the Task Review and Evidence flow.

## Evidence Authoring

Evidence can be proposed only after the Task Review exists. Call `granoflow_evidence_authoring_preview`, show every proposed operation, and apply only explicitly approved operations with `granoflow_evidence_authoring_apply`. Partial approval is valid. The running App owns the review revision/hash check, idempotency, source snapshot, and readback.

Current product behavior does not offer manual Evidence creation. Existing Evidence may be edited or deleted explicitly. Sync, backup, restore, and replay never require a Task Review and never trigger authoring.

Daily review journal prose should naturally cover the day's current Evidence without dumping a machine list into the diary. Evidence remains owned by its Tasks; daily coverage is a read-only/confirmed coverage relation, not a second Evidence copy.

## Experience Authoring And Presentation

Task Review, daily review, weekly review, and monthly review are all valid Experience proposal entrypoints. A single task may already justify an Experience; never wait for a weekly review merely because it is periodic. Weekly and monthly review can compare the current period's Experience with historical vector results to find repeated or conflicting patterns.

Call `granoflow_experience_authoring_preview`, show all candidates, and let the user approve all or a subset before `granoflow_experience_authoring_apply`. Direct Experience creation is forbidden. Existing Experience may be edited, merged, usage-linked, unlinked, or permanently deleted through its dedicated preview/confirmation path.

Experience is independent. Its detail shows source Tasks, Evidence/Review provenance, related Tasks, merge redirect, and Knowledge link when promoted. Project and milestone pages derive read-only Experience lists from their Tasks. Daily, weekly, and monthly pages display Experience only; Knowledge promotion is indicated on Experience detail/list status and is not duplicated as a separate periodic-review Knowledge section or count.

Deleting Experience detail requires impact preview and two confirmations, has no recycle bin, and removes all relations. Removing it from a Task removes only that Task usage; when that is the last task relation, disclose and separately confirm permanent Experience deletion. Other aggregate pages expose links only.

## Knowledge Eligibility And Routing

Do not ask only whether content is important. For every candidate, decide:

1. Would it still guide future work if the source Task disappeared?
2. Does it transfer to another comparable project?
3. Would forgetting it plausibly cause a wrong decision, rework, safety failure, or policy breach?
4. Must a person actively recall it at the moment of action rather than search for it later?
5. Can it stand alone with a clear boundary, and is it stable enough for its intended lifetime?

The first three memory-card signals are reusable, decision-impacting, and active-recall. Standalone expression and relative stability are additional gates. Route the result as follows:

- `active_learning`: create one explanatory Note and one or more concise learning Cards when the user should actively remember it and learning budget exists.
- `defer_active_learning`: create the Note plus an archived-reference Card when it deserves a durable Knowledge artifact but not current study load.
- `system_managed`: prefer Checklist, Skill, Linter, Test, App Guard, or another enforceable control. Create the Note plus an archived-reference Card; never claim the rule is verified until approved control evidence reads back.
- `reference_only`: keep searchable source material and create no Card for volatile APIs, version syntax, field catalogs, full policy text, commands, paths, or details best looked up.
- `use_existing_knowledge`: link the existing Note/Card rather than duplicate it.

An archived-reference Card may be manually activated by the user. Ordinary association never activates it. Association to an already active learning Card preserves the App's existing review-strengthening behavior because recent usage is a review signal; it does not mean that archived material must enter study.

Assessment and materialization are separate confirmation gates. Call
`granoflow_knowledge_assessment_preview` and
`granoflow_knowledge_assessment_apply` first; only an approved assessment may
pass through `granoflow_knowledge_materialization_preview` and
`granoflow_knowledge_materialization_apply`. Experience is not deleted or
hidden after promotion. Its list entry receives a low-emphasis promoted marker
and its detail links to the Knowledge Note.

Knowledge may originate from Experience, Evidence, Task, Artifact, or an external reference. Project work may directly cite third-party-library concepts or other external Knowledge without first inventing an Experience.

## Task Analysis Knowledge Pack

At the start of Task Analysis, call `granoflow_task_knowledge_pack` with a task-specific query. Keep Evidence, Experience, and Knowledge as three independent lanes. Report each lane's match mode, degraded reason, source health, and lineage; never mix them into one score or pretend keyword fallback is vector retrieval. `empty_ready` is a valid result and does not authorize invented candidates.

Search is zero-write. Classify each useful result as `adopted`, `considered`, `rejected`, or a gap. Explain how every adopted item changes scope, decision, risk, execution, or verification. Only adopted items may pass through adoption preview/apply and become structured Task Work references. Considered and rejected results remain zero-write.

In the reader-facing Task Work, render one optional `Granoflow References` section containing only still-adopted internal links. A link must open the corresponding Evidence, Experience, or Knowledge page. Do not expose preview tokens, hashes, scores, or rejected candidates in the document.

Every full Task Work rewrite and Delivery must call
`granoflow_task_knowledge_audit_preview` and, after approval,
`granoflow_task_knowledge_audit_apply` against App state. Remove a reference
when the final document no longer uses it, such as dropping a red-background
Evidence after choosing white. For Knowledge that is only `referenced`, removing
the reference may remove its current Usage and ordinary Task–Note association.
Once usage is `applied`, `validated`, or `contradicted`, document cleanup must
preserve that historical event.

Advance Knowledge Usage only through preview/apply with concrete evidence. `referenced` means the plan cites it; `applied` means execution used it; `validated` means outcome evidence supports it; `contradicted` means outcome evidence challenges it. Project and milestone Knowledge lists are read-only deduplicated projections of adopted Task usages, not owners of Knowledge.

## Grill And Full Rewrite

Grill findings are invisible authoring input. Integrate every accepted finding into the relevant Analysis, Scope, Risk, Decision, Plan, Verification, or Stop Condition. Never add `## Grill Review`, reviewer transcripts, findings ledgers, or patch notes.

After a Grill phase resolves, reconstruct the complete document as a new coherent version, validate it, then delete the prior local file. Upload only the new document. During that rewrite, regenerate `Granoflow References` from still-adopted sources and run reference audit before Delivery.

## Success Criteria

- No Evidence or Experience write occurs before preview and explicit approval.
- Raw task records and source documents are not mislabeled as Knowledge.
- Cards contain only knowledge worth timely human recall; enforceable or searchable material uses a better carrier.
- Task analysis reports three independent retrieval lanes and records only adopted references.
- Rewrites remove stale references without erasing applied Knowledge history.
- MCP forwards App contracts and fails closed on missing capability; it never recreates these decisions locally.
