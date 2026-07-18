# Task Authoring Quality Contract

Read this reference before an AI agent or automation creates a Granoflow task,
whether the task is created directly, while defining a project, while
decomposing a milestone, during first-run import, or as a waiting/notification
task. This is the single semantic owner of task title, description, and change
evidence quality. Other workflows should reference it instead of copying a
second version of these rules.

Human title-only quick capture in the App remains unchanged. This contract
governs tasks authored by AI agents and automation through Granoflow tools.

## Required Title And Description

Every created task must satisfy all four requirements:

1. The title names an action or observable outcome, not only a document,
   filename, component, or technical mechanism.
2. The description uses plain language that a non-programmer can understand.
   Necessary technical terms must be explained where they first appear.
3. The description contains one real analogy that makes the problem or intended
   result intuitive.
4. The description contains one concrete example showing what a person or
   system will encounter before and after the task succeeds.

Think of the description as a museum label: it should help a new visitor
understand what they are looking at without finding the original conversation.
For example, instead of writing only `Add mutation admission validation`, write
that the change is like a ticket inspector who checks every entrance, then give
a concrete case such as a milestone-generated task being rejected when its
description has no analogy or example.

An analogy and an example do different jobs. The analogy builds intuition; the
example proves the rule against a specific situation. One sentence cannot be
declared as both pieces of evidence.

## MCP Authoring Evidence

Calls to `granoflow_task_create`, `granoflow_task_create_structured`, and every
`create` operation in `granoflow_task_history_mutate` must provide:

```json
{
  "authoringEvidence": {
    "titleIntent": "action_or_outcome",
    "plainLanguageReviewed": true,
    "analogyExcerpt": "an exact non-placeholder excerpt from description",
    "exampleExcerpt": "a different exact non-placeholder excerpt from description"
  }
}
```

For generic creation, place `authoringEvidence` inside `input`. For historical
creation, place it beside `fields` on that mutation. This evidence is checked by
the MCP server and removed before the Local HTTP API request. It does not become
part of the App's task data model.

The deterministic check proves that the declared excerpts exist and are not
obvious placeholders. The authoring agent remains responsible for deciding
whether the wording is genuinely clear, analogous, and concrete. Missing or
invalid evidence returns `task_authoring_quality_failed` with all detected
issues and performs no task write.

## Change Evidence In The Description Or Task Work

For every software-development task, record a semantic minimum-change budget
before Planning or execution. The budget must distinguish:

- **required changes**: the smallest observable behavior that must become true;
- **allowed touchpoints**: UI regions, modules, APIs, data, dependencies, or
  adjacent structure that may change only when needed to deliver that behavior;
  and
- **protected surfaces**: visible behavior and internal boundaries that must
  remain unchanged unless the user explicitly expands scope.

Minimum change means the smallest complete semantic change, not the fewest
files or lines. A tightly bounded supporting refactor is allowed only when its
necessity maps directly to the confirmed Outcome or Evidence and its protected
surfaces remain explicit. Drive-by refactors, design-system or state-management
replacement, dependency upgrades, public API or schema changes, broad renames,
and unrelated cleanup are outside a local task unless separately justified and
authorized. If execution discovers one of those needs, stop before performing
it and either obtain scope confirmation or create a separate follow-up task.

When the task changes user-facing copy, list every changed string with:

- the old complete text;
- the new complete text; and
- why the wording changed.

When the task changes UI, treat the current UI as the baseline and prototype
only the authorized delta. Unlisted layout, hierarchy, copy, interaction, and
visual treatment are protected surfaces. Create and show an HTML prototype,
upload it to the task's `ui_prototype` logical slot, and read it back before
claiming the UI change is accepted. A whole-page redesign is valid only when
the task explicitly authorizes that whole-page surface.

When the task changes database tables or fields, keep one Markdown data-model
artifact for that task in the `data_model` logical slot. The same file must
contain:

- a two-dimensional Markdown table for every changed database table;
- bold formatting on every changed field;
- a Mermaid flowchart explaining why the schema must change; and
- the reason and compatibility effect of the change.

Use at most one such Markdown file per task. If discussion or implementation
changes the design, replace or revise that same logical artifact; do not upload
parallel `v2`, `v3`, or alternative data-model files.

If a task has no copy, UI, or database change, say so explicitly in Task Work
and Delivery instead of fabricating an artifact.

## Pre-Write Checklist

- The title still makes sense when shown alone.
- A non-programmer can explain the description back in their own words.
- The analogy is real and appears verbatim in the description.
- The concrete example is different from the analogy and appears verbatim in
  the description.
- Copy, UI, and database evidence requirements are either satisfied or
  explicitly marked not applicable.
- The minimum-change budget names required changes, allowed touchpoints, and
  protected surfaces; every supporting structural change maps to the confirmed
  Outcome or Evidence.
- The selected project, milestone, import, or waiting workflow has not weakened
  this contract.
