# Universal Card Quality Defaults

These defaults should work across subjects. User wrapper skills may narrow them.

## Note And Card Composition

Every memory artifact has two explicit components:

1. **Note:** one durable explanation with a meaningful title and complete
   `content`; and
2. **Cards:** one or more concise front/back study prompts derived from that
   Note.

The Note is the canonical explanation and may support multiple Cards. A Card is
not a shortened replacement for the Note, and a Note should not be duplicated
once per Card. Write the Note title as a stable topic or claim, not as a Todo
action or a filename. Write the Note body so it can be understood without
seeing the Cards: summary, context, evidence/source, explanation, **at least
one concrete example**, boundaries, and useful links or follow-up when relevant.
The example should show a realistic situation in which the knowledge changes an
understanding, decision, or action. For an abstract rule, unfamiliar concept,
trade-off, or easy-to-misread boundary, also add a plain-language analogy,
contrast, or other intuitive explanation. Put these explanations in the Note,
not in an oversized Card answer. Do not invent an example when the source is
insufficient; label the uncertainty and defer authoring if the example is
essential to understanding.

Create one Note with one Card when one recall unit is enough; split into
multiple Cards when the Note contains multiple independent recall units.

## Choosing A Card Shape

After writing the Note, decide whether each recall unit is best tested as a
basic front/back, true/false, or multiple-choice Card:

- Use **true/false** when the Note contains a crisp rule, boundary, common
  misconception, or factual claim whose truth can be judged without hidden
  context.
- Use **multiple-choice** when the Note contains a meaningful distinction,
  classification, trade-off, sequence, or decision among two or more plausible
  alternatives.
- Use **basic front/back** when the answer is a definition, explanation,
  command, short principle, or open recall that would be distorted by options.

When true/false or multiple-choice is appropriate, use the Card's supported
options field rather than encoding the options into an improvised answer string.
Options must be mutually distinguishable, the correct answer must be supported
by the Note, and distractors must be plausible without being ambiguous or
trick-based. Do not force a choice format merely to make a Note look like a
quiz.

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

For professional terms, absence of any one of the three parts is a quality
failure: rewrite the note before authoring preview. For non-professional terms,
the concrete-example requirement still applies; the analogy is required when
the idea is abstract, boundary-sensitive, or likely to be misunderstood. Keep
these explanations in note `content`; do not inflate the card back.

## Front And Back Cards

Each Card tests one recall unit from its shared Note. Make the front unambiguous
without leaking the answer. Make the back the smallest answer that remains
correct. Do not copy the entire Note content onto the back. Split overloaded
Cards, but keep the explanation in the shared Note.

Default to basic front/back cards. A user wrapper can add cloze, multiple-choice, true/false, image, pronunciation, or other formats, but extensions must preserve the official search and controlled-write flow.

Front/back are structured-layout fields, not merely duplicate strings on the card row. Every created or rewritten card must retain materialized field values referenced by non-empty front and back layout keys. Completion requires the App readback to report `practiceReady: true` and a real Card Practice front/answer check.

When removing a note field, first find every front/back layout that references its base field key. Rewrite those card layouts and verify them before requesting field deletion. A still-referenced field is protected and deletion must fail closed.

## Source

Prefer, in order: user-specified truth source; supplied primary material; official specification or documentation; peer-reviewed or authoritative reference; well-established general knowledge; clearly labeled local experience. Preserve title, edition/version, URL, or local artifact path when available.

For exam-like material, use the source's terminology and answer boundary on the card. Explanatory extensions belong in note content and must not contradict it.

## Worthiness

Create a card only when there is a plausible future situation in which recalling it changes understanding, an answer, a decision, or an action. Prefer fewer, stronger cards. If the future retrieval trigger is unclear, leave the material in task review instead.
