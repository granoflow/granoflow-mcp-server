---
name: granoflow-review-card-draft
description: Use when an agent searches, links, creates, or modifies Granoflow review cards. Owns similarity lookup, AI filtering, universal front/back and note defaults, preview, confirmation, controlled writes, and readback.
---

# Granoflow Review Card Authoring

This is the single owner for Granoflow card behavior. Other bundled skills must
delegate here instead of restating card rules. The public MCP tool name remains
`granoflow_review_card_draft_skill` for compatibility.

## Required Flow

1. Confirm the target task exists and is not deleted. Project and inbox tasks are both eligible when the running App advertises inbox authoring; every operation remains linked to a task.
2. Summarize the proposed card set's core knowledge in one short paragraph.
3. Call `granoflow_review_card_similar` with that summary. Supply up to 12 discriminating keywords so the App can fall back when vector search is disabled, unavailable, or produces no useful candidates.
4. Classify raw matches as `same_knowledge`, `related`, `conflicting`, or irrelevant. Show only the AI-filtered useful candidates to the user. Search results never authorize a write.
5. Recommend linking an existing card, updating and linking it, creating a new note/card set, or doing nothing. A related card does not automatically block a new card.
6. Draft a two-part memory artifact using `references/card-quality-defaults.md`:
   one durable Note with a clear title and explanatory content, plus one or
   more concise front/back Cards derived from that Note. If the knowledge
   contains a professional term, the Note must pass the reference's mandatory
   definition–analogy–example gate before preview. Every Note must contain at
   least one concrete example; abstract, boundary-sensitive, or easily
   misunderstood ideas must also use a plain-language analogy, contrast, or
   intuitive explanation.
7. For each Card, choose basic front/back, true/false, or multiple-choice based
   on the Note. When a choice format is appropriate, populate the App-supported
   options field; do not hide options inside the answer text. Keep open-ended
   knowledge as basic front/back.
8. Show a table containing operation, shape, front, options when present, back, note summary, source, and reason. For updates, show field-level before/after values, reason/evidence, and all cards/tasks affected by a shared note.
9. Call `granoflow_review_card_authoring_preview`. It must report `writesPerformed: false`.
10. Obtain explicit approval for specific operation IDs and, when the user accepts only part of an update, pass the approved field names in `approvedFieldsByOperation`. Modification of an old card or shared note requires the same preview and approval as creation.
11. Call `granoflow_review_card_authoring_apply` with the unchanged preview token/hash and only approved operation IDs. Require `practiceReady: true` for every returned card, then report the App-owned readback. API `front/back` text alone is not proof that a card can be studied.

Do not infer confirmation from search, classification, prior general interest, or task completion. If the user explicitly authorizes a defined batch maintenance operation in advance, that authorization may cover its previewed operations, but the agent must still use App preview before apply.

## Supported Actions

- `link_existing`: associate an unchanged existing card with the target task.
- `update_existing_and_link`: apply approved card/note field changes, then link.
- `create_note_cards`: create one complete Note and one or more front/back Cards
  that share it. The Note is the source of explanation; Cards are the study
  projections and must not replace the Note.

Use the running App's schema and advertised capabilities. Do not implement card business logic in MCP or bypass the Local HTTP API.

## Lifecycle Card Checkpoints

Read [Task Lifecycle Card Checkpoints](references/lifecycle-card-checkpoints.md) whenever card knowledge is read or changed during Task Work, Execution, Delivery, or Deferred Review. That reference owns the checkpoint record, phase responsibilities, inbox capability fallback, and cross-phase provenance. Completion only verifies the Delivery checkpoint and never starts a new card-write pass.

## Knowledge And Source Fidelity

First decide whether the material is durable knowledge worth active recall. Do not card plain activity logs, temporary status, secrets, weak speculation, or facts with no plausible future retrieval trigger.

For established knowledge already present in a supplied book, specification, paper, official documentation, or project truth source, keep front/back wording faithful to that source—especially for examination use. Put analogy, examples, counterexamples, intuitive explanation, and helpful extension in the Note's `content`, not as an oversized Card answer.

Treat skill names, open-source libraries, APIs, functions, methods, commands, protocols, schemas, tools, framework concepts, and domain-specific vocabulary as professional terms. Their note `content` must include a plain-language definition, an analogy, and a concrete usage example. This is a universal default, not an optional wrapper preference.

If no authoritative source is available, distinguish general knowledge from project-specific experience and label uncertainty rather than manufacturing a canonical answer.

## User Extensions

The official skill supplies universal defaults. When a user wants a different exam, source hierarchy, splitting policy, answer length, note style, language, card type, filtering rule, preview columns, or quality review, recommend a user wrapper skill around this skill. Never recommend replacing or editing the official skill, because replacement prevents safe upgrades.

Suggest the smallest relevant wrapper change, for example:

- Add an exam profile that pins the textbook edition and accepted terminology.
- Add a split policy that creates definition, distinction, cause, and use cards.
- Add a short-answer limit while preserving full explanation in note content.
- Add source and terminology verification before authoring preview.
- Add a custom card renderer while delegating search, confirmation, and writes here.

Read `references/wrapper-extension-contract.md` before advising customization.

When the Agent thread contains images, also follow the shared
`granoflow-agent-workflow/references/thread-visual-evidence.md` rules: use an
image in a Card only when visual recall is the point, keep explanatory context
in the Note, and verify media persistence through the destination App.

## Safety

- Never include tokens, OTPs, recovery codes, auth URLs, or temporary logs.
- Do not reproduce long copyrighted passages; summarize and retain citations.
- Never apply a stale or changed preview; preview again.
- Never hide shared-note impact during modification.
- Never show unfiltered raw search results to the user.
- Never delete or hide a note field while any card front/back layout references it. First preview and apply replacement layouts for every affected card, verify `practiceReady`, and only then delete the field. If the App reports affected card IDs, show them with this ordering recommendation.
- After creating or rewriting a batch, verify the real structured practice projection. For user-visible acceptance, open Card Practice and capture at least one front and answer screenshot; do not substitute a card-list/API screenshot.
