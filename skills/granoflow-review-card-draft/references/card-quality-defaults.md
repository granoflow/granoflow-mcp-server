# Universal Card Quality Defaults

These defaults should work across subjects. User wrapper skills may narrow them.

## Note

Every new card set has a meaningful note title and a complete `content` explanation. Explain the knowledge in plain language. The note is the durable explanation and may support multiple cards.

## Mandatory Professional-Term Explanation

Treat an item as a professional term whenever understanding it depends on specialized technical, professional, academic, or project vocabulary. This explicitly includes:

- skill names and tool names;
- open-source libraries, packages, frameworks, and models;
- APIs, protocols, schemas, data structures, and architectural patterns;
- functions, methods, classes, hooks, commands, flags, and configuration keys;
- domain-specific business, scientific, legal, medical, design, media, or engineering terms.

For every professional term, note `content` must contain all three parts:

1. **Plain-language definition:** say what it is and what job it performs without relying on more unexplained jargon.
2. **Analogy:** compare it to a familiar everyday object, role, or situation and state where the analogy stops being exact when that boundary matters.
3. **Concrete example:** show the term being used in a realistic call, command, code fragment, workflow, or scenario. For a function or method, include representative input/action and observable result when available.

Example for `skill-polish`:

- Definition: a skill that tightens an already scaffolded skill into a maintainable final form.
- Analogy: like an editor revising an existing manuscript; it improves structure and clarity but does not write the first draft from nothing.
- Example: after `skill-scaffold` creates `SKILL.md`, call `skill-polish` to move detail into references and preserve preview gates.

An analogy or example may be omitted only when the item is not a professional term. For professional terms, absence of any one of the three parts is a quality failure: rewrite the note before authoring preview. Keep these explanations in note `content`; do not inflate the card back.

## Front And Back

Each card tests one recall unit. Make the front unambiguous without leaking the answer. Make the back the smallest answer that remains correct. Do not copy the entire note content onto the back. Split overloaded cards.

Default to basic front/back cards. A user wrapper can add cloze, multiple-choice, true/false, image, pronunciation, or other formats, but extensions must preserve the official search and controlled-write flow.

Front/back are structured-layout fields, not merely duplicate strings on the card row. Every created or rewritten card must retain materialized field values referenced by non-empty front and back layout keys. Completion requires the App readback to report `practiceReady: true` and a real Card Practice front/answer check.

When removing a note field, first find every front/back layout that references its base field key. Rewrite those card layouts and verify them before requesting field deletion. A still-referenced field is protected and deletion must fail closed.

## Source

Prefer, in order: user-specified truth source; supplied primary material; official specification or documentation; peer-reviewed or authoritative reference; well-established general knowledge; clearly labeled local experience. Preserve title, edition/version, URL, or local artifact path when available.

For exam-like material, use the source's terminology and answer boundary on the card. Explanatory extensions belong in note content and must not contradict it.

## Worthiness

Create a card only when there is a plausible future situation in which recalling it changes understanding, an answer, a decision, or an action. Prefer fewer, stronger cards. If the future retrieval trigger is unclear, leave the material in task review instead.
