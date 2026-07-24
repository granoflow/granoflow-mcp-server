# Task Authoring Quality Contract

Read this reference before an AI agent or automation creates a Granoflow task,
whether the task is created directly, while defining a project, while
decomposing a milestone, during first-run import, or as a waiting/notification
task. This is the single semantic owner of task title, description, and change
evidence quality. Other workflows should reference it instead of copying a
second version of these rules.

Human title-only quick capture in the App remains unchanged. This contract
governs tasks authored by AI agents and automation through Granoflow tools.
Existing-task mutations are owned by `task-description-update-contract`; do
not copy update classification or completion-freeze rules into this file.

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

When the task is **copy-only** / 文字验证, do not add unit, integration, or
other automated tests—use visual/copy review only
(`copy_change_tests_forbidden`). See `user-visible-copy-boundary.md`.

When the task changes user-facing copy, list every changed string with:

- the old complete text;
- the new complete text; and
- why the wording changed.

When the task changes UI, treat the project Design Baseline (when present) and
the current UI as authority, and prototype **only** the authorized delta.
Unlisted layout, hierarchy, copy, interaction, and visual treatment are
protected surfaces.

**Mandatory prototype:** any UI change requires a high-fidelity HTML prototype.
Set Task Work `prototype_requirement: required`. Apply **Task Prototype Craft
Gate And Option Set**: interactive **mainstream-reference-first** candidate
pool (≥5; brainstorm backfill only when mainstream `<5`; AI chooses
`same_category` vs `capability_match`, defaulting to capability when unsure)
then dual **page expressions** (`expr_a` + `expr_b`) with **functional
parity** (same capabilities + same data; see
`prototype-expression-brainstorm.md`) inside the locked Design System, with ≥2
contrast axes and a **side-by-side Contrast Gallery** with candidate digest +
per-axis visible-diff captions (mix-and-match per task/page; never reopen
Design Spec as task options; conditional industry third only when documented);
unattended same protocol then single `expr_a`; Craft Gate before
`visualConfirmed` (`task_prototype_craft_incomplete` otherwise), including
**Baseline fit** (`prototype-baseline-fit.md`;
`prototype_baseline_fit_*` / `prototype_generic_phone_frame` /
`prototype_shell_chrome_mismatch`; require
`craft_checklist.baseline_fit_ok` after `lint_prototype_baseline_fit.py`),
**product truth** (`prototype_product_truth_violation`), **expression
candidates** (`prototype_option_brainstorm_*` /
`prototype_option_mainstream_skip` / `prototype_option_scope_mode_invalid` /
`prototype_option_function_split` / `prototype_option_data_divergence`;
require `craft_checklist.expression_brainstorm_ok` after
`lint_prototype_expression_brainstorm.py`), and **user-visible copy boundary**
(`user_visible_copy_boundary_unread` /
`user_visible_copy_boundary_violation`; require
`craft_checklist.user_visible_copy_boundary_ok` after
`lint_prototype_user_copy.py`).
Keep **design-first**:
previews express demand; if undeliverable, revise design—do not fake
capability. High-risk platform-coupled UI needs a Tech Note conclusion before
Readiness (`high_risk_feasibility_unresolved`). Declare `derivedFrom` the
confirmed Design Baseline package when the project has one, accept against
contract fidelity (契约级一致), **no** random visual seed, reuse
`widgets.yaml` when the same role exists, upload the **chosen** option to the
task's `ui_prototype` logical slot with visual confirmation, and read it back.
Later discussion changes Must re-import and rewrite Task Work refs per
`discussion-writeback-contract` + `change-impact-fanout` (never leave the new
truth only in chat/`temp`; close sibling impact ledger in the same batch)
**before Analysis confirmation**. Confirmed `ui_prototype` is an Analysis
deliverable; Planning Must not start while it is missing.
Fail closed on Design System reopen
(`prototype_option_design_system_reopened`), prose-only near-duplicates
(`prototype_option_near_duplicate`), missing gallery
(`prototype_option_contrast_gallery_required`), or unlabeled diffs
(`prototype_option_diff_unlabeled`).
Do not mark `not_required` for a UI change.
A whole-page redesign is valid only when the task explicitly authorizes that
whole-page surface.

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

**Also update the project data attachments named in Project Work**
(`data_model_attachment`, `json_contracts_attachment`,
`constants_catalog_attachment`):

- DB / schema change → update the project `data_model` attachment
  (`data-model.md` or the registered name) and registry SHA.
- JSON / structured file shape or semantics change → update the project
  `json_contracts` attachment (YAML shapes; default `data-contracts.yaml`).
- Shared constant name, value, type, or ownership change → update the project
  `constants_catalog` attachment (default `constants-catalog.yaml`).

Code and these attachments must stay consistent. Shipping code without the
matching attachment update fails closed as `data_artifact_stale`. Do not embed
full JSON shapes or constant catalogs into Project Work body YAML.

During Task **Analysis**, if the current project table schema, JSON contract, or
constant catalog is unreasonable for the Outcome, raise the issue and propose a
revision before Analysis confirmation—do not wait for Delivery to discover that
the model cannot work.

During Task **Analysis**, if a capability-critical library in Project Work
`dependencies.approved` is unreasonable for the Outcome (or a required
capability library was never selected), raise it and update
`dependencies.approved` before confirming Analysis—do not silently pick a
different EPUB/crypto/… package only in code.

For software tasks, Plan/Delivery must record unit-test sufficiency. Prefer no
new integration tests; if unit tests cannot cover the Outcome boundary, add at
most two task-local integration tests and leave them for **manual** execution—
the Agent must not run them. Recommend the user's **local machine** as the
integration device; the user confirms or chooses another target.

Before software edits, check `project_snapshot.yaml` and `project_rules.yaml`
for conflicts with the planned change. Interactive conflicts need user
confirmation; unattended conflicts need an explicit emitted decision
(`revise_code` or `revise_context_yaml`).

If a task has no copy, UI, database, JSON-contract, or shared-constant change,
say so explicitly in Task Work and Delivery instead of fabricating an artifact.

For software Plans that will edit code, also satisfy `plan-design-gate.md`
(Markdown verification test cases traced to Analysis; explicit
`data_disposition` even when `unchanged`; task-local libraries only; no hollow
Execution Plan). Schema change artifacts in this file remain required when
disposition is `extend` or `breaking`.

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
- When software Planning edits code, the Plan Design Gate minimal set is
  present or explicitly `not_applicable` with basis.
- The selected project, milestone, import, or waiting workflow has not weakened
  this contract.
