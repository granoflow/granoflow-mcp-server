---
name: granoflow-review-card-draft
description: Use when an AI agent needs to create Granoflow review cards with the correct fields, card types, note fields, layouts, and fallbacks. Fetch the app-owned schema first, preview cards for the user, then write through granoflow_task_finish or single_task_ai import after confirmation.
---

# Granoflow Review Card Draft

Use this skill when the user asks to create review cards, word cards, multiple-choice cards,
image-assisted cards, or study cards from a task, book, conversation, or lesson.

Public prompt:

```text
Create review cards from this material
```

Also accept equivalent requests in the user's language.

## Required First Steps

1. Call `granoflow_review_card_draft_schema` (or `GET /v1/ai-agent/review-card-drafts/schema`).
2. Call `granoflow_ai_agent_tools` and inspect `single_task_ai.capabilities`.
3. Read the bundled `granoflow-agent-workflow` reference
   `references/review-card-authoring.md` for worthiness and safety rules.

Do not guess card fields from memory when the running app exposes a schema.

## Workflow

1. Decide whether each candidate point deserves a card or should stay in `taskReview`.
2. Pick the nearest supported `cardType` or documented `patternId` from the schema.
3. Build a preview for the user: title, card shape, front/back, note fields, layout, fallback notes.
4. Wait for explicit user confirmation before writing.
5. Write through:
   - `granoflow_task_finish` with `reviewCardDrafts` when finishing a task, or
   - `granoflow_task_import` / validated `single_task_ai` JSON when importing task results.
6. Use `dryRun=true` first when the tool supports it.

## Schema Rules

- Only use import-supported `cardType` values from the schema (`basic_qa`, `reverse_qa`, `keyword_cloze`).
- For `language_word`, follow the schema example: translation on front, target word on back,
  optional `note_fields` for pronunciation.
- For `multiple_choice`, `image_assisted`, and `image_multiple_choice`, use the schema fallback
  strategy. Do not invent unsupported structured fields.
- Keep `front` and `back` complete even when `note_fields` and layouts are present.
- Preserve source context in `sourceSummary`; never store secret values in cards.

## Confirmation

Do not write cards silently. Show the preview first unless the user already explicitly asked to
import the exact preview you just showed.

## Non-Goals

- Do not implement card business logic in MCP.
- Do not attach image binaries through import JSON when the schema says fallback only.
- Do not create cards for plain activity logs or secret-bearing content.
