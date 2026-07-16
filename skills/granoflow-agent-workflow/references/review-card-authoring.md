# Review Card Authoring Delegation

The bundled `granoflow-review-card-draft` skill is the sole owner of review-card search, quality defaults, preview, confirmation, writes, and readback. Load and follow it before any card operation. The remainder of this legacy reference is background only; if it conflicts with the core card skill, the core skill wins.

Read this reference before creating `reviewCardDrafts` while finishing a
Granoflow task, writing review content, or turning durable lessons into study
cards.

Before drafting cards, call `granoflow_review_card_draft_schema` and inspect
`single_task_ai` capabilities from `granoflow_ai_agent_tools`. Use the app-owned
schema for card types, note fields, layouts, and unsupported-pattern fallbacks.

Every card operation produces or reuses a two-part artifact: one Note with a
stable title and complete explanation, plus one or more Cards derived from that
Note. Review cards are for future action, not for logging that something happened.
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

## Note And Card Tone

Write the Note like a durable knowledge note: a stable title, plain-language
summary, context, explanation, evidence or source, and examples or boundaries
when useful. Then write each Card as one compact recall prompt from that Note.
Do not put the entire Note into a Card back, and do not create a separate Note
for every Card unless the knowledge is genuinely independent.

Treat each card as a compact note, not a quiz scrap. Card wording should be:

- plain;
- specific;
- easy to revisit later;
- grounded in the user's actual work;
- short enough to study.

Use analogies, concrete examples, and simple language only when they make the
idea easier to remember. Preserve source title, URL, screenshot path, or local
reference path in `sourceSummary` or a visible note field when available.

## Experience Is Not A Card Type

An Experience is an independent reusable lesson, not a study Card. Keep it
searchable and available to future task analysis even when it never becomes
Knowledge. Only after the App-owned Knowledge assessment approves the source may
materialization create or reuse a Note and Card.

Situated facts such as one customer's preference, one project's temporary
constraint, or one vendor's current habit usually remain Evidence, Experience,
or searchable reference. Card them only when the Knowledge gate shows that a
person must actively recall a stable, reusable boundary at the moment of action.
If a system, checklist, Skill, Linter, Test, or App Guard can enforce the rule,
prefer that carrier over memory practice.

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
- Use multiple-choice style cards when the Note requires choosing between
  plausible alternatives, classifications, trade-offs, or sequences. Put the
  alternatives in the Card's options field and explain why the right answer
  wins on the back.
- Use true/false style cards when the Note contains a crisp rule, boundary,
  common misconception, or factual claim that can be judged without hidden
  context. Represent the two choices through the Card's options field.
- Do not force a choice format when options would distort an explanation or
  make the answer depend on trick wording; use normal front/back instead.
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
