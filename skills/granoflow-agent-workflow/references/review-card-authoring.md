# Review Card Authoring Delegation

The bundled `granoflow-review-card-draft` skill is the sole owner of review-card search, quality defaults, preview, confirmation, writes, and readback. Load and follow it before any card operation. The remainder of this legacy reference is background only; if it conflicts with the core card skill, the core skill wins.

Read this reference before creating `reviewCardDrafts` while finishing a
Granoflow task, writing review content, or turning durable lessons into study
cards.

Before drafting cards, call `granoflow_review_card_draft_schema` and inspect
`single_task_ai` capabilities from `granoflow_ai_agent_tools`. Use the app-owned
schema for card types, note fields, layouts, and unsupported-pattern fallbacks.

Review cards are for future action, not for logging that something happened.
When a point is useful but not worth spaced practice, keep it in `taskReview`
instead.

## Worthiness Gate

Create cards for durable knowledge, not only language learning. First decide
whether the item is worth retaining, then classify it as the nearest knowledge
shape:

- `language_learning`
- `knowledge`
- `person`
- `organization`
- `place`
- `engineering_convention`
- `security_principle`

People, places, organizations, and professional terms introduced during a task
can become knowledge cards when they matter to future work.

Use source quality as the first filter. A book citation, documentation page,
paper, webpage, screenshot, or explicit local artifact is strong evidence that a
point may be worth retaining. Still create a card only when the point is useful
for future execution, understanding, risk checking, design, conversation, or
decision-making.

When no source is present, create a card only for reusable decisions, repeated
failure modes, project rules, concepts that affect future execution, or ideas
the user explicitly wants to retain.

## Card Tone

Treat each card as a compact note, not a quiz scrap. Card wording should be:

- plain;
- specific;
- easy to revisit later;
- grounded in the user's actual work;
- short enough to study.

Use analogies, concrete examples, and simple language only when they make the
idea easier to remember. Preserve source title, URL, screenshot path, or local
reference path in `sourceSummary` or a visible note field when available.

## Experience Cards

Experience cards are separate from general knowledge cards. They capture
situated facts that books or general model knowledge may not contain:

- a customer preference;
- a project-specific recurring failure mode;
- a vendor habit;
- a local workflow constraint;
- a team-specific decision boundary.

Do not create an experience card merely because something happened. Create it
only when the experience is likely to change a future action, conversation,
estimate, design choice, risk check, or relationship decision.

Keep useful experience cards dense. A good private preference card can be:

```text
front: Customer A likes what food?
back: Roasted lamb leg.
```

Add only the smallest useful qualifier when ambiguity or safety requires it:

```text
front: When choosing food for Customer A, what preference matters?
back: Roasted lamb leg; still confirm dietary constraints and context.
```

## Internal Self-Grill

Before creating cards, run this short internal self-review. This is not a user
questionnaire. If the answers are weak, rewrite the card, create fewer cards, or
keep the point in `taskReview`.

1. What future situation should make this card useful?
2. What is the smallest memorable payload?
3. Is this knowledge, project rule, or situated experience?
4. Would a future action change because of this card?
5. Which shape fits best: front/back, multiple-choice, true/false,
   image-assisted, language-learning, or no card?
6. Is the current draft suitable for that shape, or should it be shorter, split,
   merged, or left in `taskReview`?
7. Is any detail private, stale, speculative, or better kept out of a card?

If the future action would not change, omit the card.

## Study Shape

Choose the card shape that fits the material:

- Use normal front/back for definitions, principles, commands, boundaries, and
  "when should I do this?" knowledge.
- Use multiple-choice style fronts for choosing between plausible alternatives.
  Put the options on the front and explain why the right answer wins on the
  back.
- Use true/false style fronts for common misconceptions, risky assumptions, or
  sharp rules.
- Use image-assisted cards when a screenshot, diagram, UI state, or visual
  artifact is worth remembering. If the current tool contract cannot attach
  media directly, preserve the screenshot path, URL, or visual description in
  `sourceSummary` or a note field.

## Language-Learning Cards

For English words or phrases, create a separate language-learning card when the
term is worth learning. The 500 most frequent everyday English words are usually
not worth carding.

Create a card when the word, abbreviation, or phrase is:

- professionally relevant;
- domain-specific;
- ambiguous or easy to misuse;
- dictionary-listed but outside everyday high-frequency vocabulary;
- important for execution or comprehension.

Put the translation on the front. Put the English word or phrase on the back.
Add pronunciation support when available.

## Note Fields And Preview Gate

When a card benefits from phonetic spelling, translation, or click-to-speak
pronunciation:

1. Call `granoflow_ai_agent_tools` and inspect the `single_task_ai`
   `reviewCardDraftNoteFields` capability.
2. If it advertises `review_card_draft_note_fields_v1`, use `noteFields` for
   auxiliary fields such as `title`, `description`, `phonetic`, `translation`,
   and `pronunciation`.
3. Use `type: "text_to_speech"` plus `ttsLanguageCode` for speakable fields.
4. Include `frontLayout` and `backLayout` so fields appear in study.
5. Keep `front` and `back` complete even when structured fields are present;
   older clients and exports must still make sense.

If the capability is missing, unknown, or unreachable, omit `noteFields`,
`frontLayout`, and `backLayout`. Put phonetic, translation, and pronunciation
hints directly in `front` and `back`.

If `granoflow_task_finish` returns
`review_card_draft_note_fields_unsupported`, remove the unsupported fields,
rewrite the cards in the fallback shape, and retry only after the payload no
longer contains enhanced fields.

## Safety Rules

- Do not create cards that expose API tokens, secrets, private identifiers,
  recovery codes, OTPs, auth URLs, or temporary log content.
- If the durable point is about avoiding exposure, write a
  `security_principle` card.
- Do not copy long copyrighted text into cards. Summarize and preserve source
  references instead.
- Do not create duplicate cards when an existing similar card already captures
  the same durable point.

## Success Criteria

- Each card contains exactly one durable knowledge point.
- The card is short enough to study.
- Source context is preserved when available.
- The chosen study shape matches the knowledge.
- Enhanced fields are used only when the running app advertises support.
- No secret, credential, private identifier, or temporary log content is
  included.
