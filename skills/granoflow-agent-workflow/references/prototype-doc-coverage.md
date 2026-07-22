# Prototype → Document Coverage

Hard gate so a **finalized / rematched** task-level `ui_prototype` is fully
reflected in **Task Work** and **Project Work** with no silent conflicts or
omissions, **every task-owned user-visible UI surface has high-fidelity HTML
prototype coverage**, and **widgets.yaml roles are reused—not near-duplicated**.
Complements `prototype-product-truth-writeback` (product-truth class +
product_doc) and `discussion-writeback-contract` (slot writes).

MCP stays thin: agents update App/repo docs via existing tools; this Skill owns
the coverage ledgers and fail-closed codes.

## Mandatory Load

When a task `ui_prototype` is **finalized, confirmed, rematched, or the user
asks to change the prototype**, load via MCP before closing Analysis (or the
discussion batch that locks the prototype):

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "prototype-doc-coverage"
)
```

Also load `prototype-product-truth-writeback`, `change-impact-fanout`, and
`discussion-writeback-contract` in the same batch.

Skipping this load when the gate applies fails closed as
`prototype_doc_coverage_unread`.

## When It Applies

| Trigger                                             | Gate                                       |
| --------------------------------------------------- | ------------------------------------------ |
| Prototype finalized / `visualConfirmed` / rematch   | Required                                   |
| User asks to modify the prototype                   | Required                                   |
| `prototype_requirement: not_required` / no UI proto | All three ledgers `status: not_applicable` |

## Hard Rule — HTML Prototype Surface Ledger

Before Analysis confirmation, inventory **every material user-visible UI
surface owned by this task**—pages, dialogs/modals, sheets, popovers, toasts
(when user-visible and task-owned), and other overlays—and map each to a
**high-fidelity HTML prototype file** in the task `ui_prototype` package (or
linked option batch). No omissions.

Persist on Task Work:

```yaml
prototype_html_coverage:
  schema: granoflow_prototype_html_coverage_v1
  contract_loaded: true
  prototype_id: <id>
  version_id: <id> | null
  status: not_applicable | pending | complete
  surfaces:
    - surface_id: S-settings
      kind: page | dialog | modal | sheet | popover | toast | panel | other
      label: <plain-language>
      html_prototype_ref: <package-relative path or clickable link>
      coverage: covered | missing
      note: <optional>
```

Rules:

1. Build the inventory from Task Work Scope/Outcome, UI acceptance, and any
   surface the task adds or materially changes—not only pages already in the
   prototype package.
2. Each surface **Must** have `coverage: covered` and a non-empty
   `html_prototype_ref` before Analysis close. Partial HTML wireframes,
   prose-only descriptions, or “same as baseline” without a task HTML file do
   **not** count.
3. `coverage: missing` while claiming `status: complete` fails closed as
   `prototype_html_coverage_gap` with **every gap surface_id listed**.
4. Analysis **Must not** close while `status: pending` with any required surface
   still missing HTML.
5. `status: complete` only when every inventoried surface is `covered` (or
   `not_applicable` when the task truly has no UI surfaces).

Lint:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_prototype_doc_coverage.py \
  --kind html_coverage path/to/html-coverage.yaml
```

## Hard Rule — Widget Reuse Ledger

When project `widgets.yaml` exists, load it (App readback) before authoring or
confirming task HTML prototypes. **Same role ⇒ Must reuse the catalog widget
id** (`reuse_policy: must_reuse_when_same_role`). Do not invent near-duplicate
chrome/controls for an existing role.

Persist on Task Work:

```yaml
prototype_widget_reuse:
  schema: granoflow_prototype_widget_reuse_v1
  contract_loaded: true
  catalog_sha256: <widgets.yaml sha256> | null
  status: not_applicable | pending | complete
  declarations:
    - role: shell.primary_nav
      widget_id: shell.primary_nav # Must match catalog when role exists
      action: reused | new_role
      html_surfaces: [S-home, S-library]
      rationale: null | <required when action=new_role and role exists in catalog>
```

Rules:

1. For every chrome/control/pattern role used in task HTML prototypes, declare a
   row. `action: reused` when an existing catalog widget applies.
2. When `widgets.yaml` contains a widget for the same `role` (by `id` or
   documented role alias), the declaration **Must** use that `widget_id` with
   `action: reused`. Skipping without accepted rationale →
   `widget_reuse_required`.
3. Two declarations with the same `role` but different `widget_id` values fail
   closed as `widget_reuse_required` (near-duplicate).
4. `action: new_role` is allowed **only** when no catalog widget covers that
   role; after visual confirmation, extract the new widget into project
   `widgets.yaml`.
5. Analysis **Must not** close while `status: pending` or while lint reports
   reuse violations.

Lint (pass project catalog for cross-check):

```text
python3 skills/granoflow-agent-workflow/scripts/lint_prototype_doc_coverage.py \
  --kind widget_reuse path/to/widget-reuse.yaml --widgets path/to/widgets.yaml
```

## Hard Rule — Document Coverage Ledger

Build a row for every material prototype page, control, state, user-visible
copy block, and primary flow that the prototype shows. Map each row to Task
Work and Project Work loci. Persist on Task Work (and attach/readback as
needed):

```yaml
prototype_doc_coverage:
  schema: granoflow_prototype_doc_coverage_v1
  contract_loaded: true
  prototype_id: <id>
  version_id: <id> | null
  status: not_applicable | pending | complete
  rows:
    - page_id: S-welcome
      element_id: primary_cta # or page / state / copy id
      kind: page | control | state | copy | flow
      task_work_locus: <section/field path or quote>
      project_work_locus: <section/field path or not_applicable+reason>
      coverage: covered | missing | conflict
      note: <plain-language>
```

Rules:

1. Prototype is the **source of truth** for UI/product surface description.
2. `coverage: missing` → Task Work and/or Project Work must be updated until
   covered (`prototype_doc_coverage_gap`).
3. `coverage: conflict` → docs disagree with the prototype; rewrite docs to
   match the prototype (`prototype_doc_conflict`). Do not “keep docs” by
   soft-passing Analysis.
4. Analysis / discussion batch **Must not** close while any row is
   `missing`/`conflict`, or while `status` is `pending` with a non-empty
   required inventory.
5. `status: complete` only when every row is `covered` (or inventory truly
   empty with explicit `not_applicable` justification).
6. Project Work updates are required when the prototype changes journeys,
   screens, acceptance, ship bar, or user-visible product copy that Project
   Work owns. Honest `project_work_locus: not_applicable` needs a reason.

Lint:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_prototype_doc_coverage.py \
  --kind coverage path/to/coverage.yaml
```

## Plan Stage — Truth Conflict Gate

During Planning, **re-read** the current App prototype against Task Work. If
they disagree:

1. Treat the **prototype as source of truth**.
2. Emit `prototype_plan_truth` with conflicts + recommended doc updates.
3. **Explicitly remind** the user (interactive) and list recommendation items.
4. After the user **agrees**, update Task Work **and** Project Work (when in
   scope), then re-lint.
5. Unattended: apply recommended doc updates under the current authorization,
   emit a non-question notice, and writeback + readback.

```yaml
prototype_plan_truth:
  schema: granoflow_prototype_plan_truth_v1
  contract_loaded: true
  prototype_is_source_of_truth: true # must be true
  status: not_applicable | aligned | conflict
  conflicts: [] # [{ page_id, field, prototype_says, task_work_says, recommendation }]
  user_notified: true | false
  user_resolution: not_applicable | pending | accepted_doc_update
  task_work_updated: true | false | not_applicable
  project_work_updated: true | false | not_applicable
```

Fail closed:

| Code                               | When                                                         |
| ---------------------------------- | ------------------------------------------------------------ |
| `prototype_plan_truth_conflict`    | `status: conflict` and resolution not `accepted_doc_update`  |
| `prototype_plan_truth_unnotified`  | Interactive conflict without `user_notified: true`           |
| `prototype_plan_truth_docs_stale`  | User accepted update but TW/PW flags not updated             |
| `prototype_plan_truth_sot_invalid` | `prototype_is_source_of_truth` is not true when gate applies |

`plan_design_gate_status` **Must not** be `passed` while
`prototype_plan_truth.status: conflict` and resolution is `pending`.

Lint:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_prototype_doc_coverage.py \
  --kind plan_truth path/to/plan-truth.yaml
```

## Relationship to Implementation (Phase A)

Document coverage does **not** replace implement-time
`prototype-implementation-fidelity` Phase A (`code_review_guess` — **code vs
prototype**, not screenshots). Coverage makes docs match the prototype;
Phase A makes code match the prototype.

## Fail-closed Codes (Analysis)

| Code                                 | When                                                                                                      |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `prototype_doc_coverage_unread`      | Gate applies; reference not loaded / `contract_loaded` false                                              |
| `prototype_html_coverage_unread`     | HTML ledger missing or `contract_loaded` false when UI applies                                            |
| `prototype_widget_reuse_unread`      | Widget ledger missing or `contract_loaded` false when catalog exists                                      |
| `prototype_doc_coverage_gap`         | Doc row `coverage: missing` while claiming complete                                                       |
| `prototype_html_coverage_gap`        | Surface `coverage: missing` or empty `html_prototype_ref` while complete; detail lists `surface_id` gaps  |
| `prototype_doc_conflict`             | Doc row `coverage: conflict` while claiming complete                                                      |
| `prototype_doc_coverage_incomplete`  | Doc `status: complete` but rows empty when prototype exists                                               |
| `prototype_html_coverage_incomplete` | HTML `status: complete` but `surfaces` empty when UI applies                                              |
| `widget_reuse_required`              | Same role not reused from `widgets.yaml`; near-duplicate widget ids; `new_role` when catalog entry exists |
| `prototype_doc_coverage_lint_failed` | Structural lint failure on any ledger kind                                                                |

Analysis confirmation (`analysis_status: confirmed`, Readiness pass) **Must
not** proceed while any Analysis ledger above reports `pending`, gap/conflict
rows, or lint `ok: false`.

## Agent Checklist

### Analysis / prototype lock

1. Load this reference + product-truth writeback + fan-out + discussion writeback?
2. Inventory **all task-owned UI surfaces** into `prototype_html_coverage.surfaces` with HTML refs?
3. Lint `--kind html_coverage` ok and `prototype_html_coverage.status: complete`?
4. Load `widgets.yaml`; declare `prototype_widget_reuse`; lint `--kind widget_reuse` ok?
5. Inventory prototype pages/controls/states/copy/flows into doc `rows`?
6. Update Task Work + Project Work until all doc rows `covered`?
7. Lint `--kind coverage` ok and `prototype_doc_coverage.status: complete`?

### Plan

1. Re-diff prototype vs Task Work?
2. If conflict: notify + recommendations; wait for agree (interactive)?
3. Writeback TW/PW; lint `--kind plan_truth` ok; then Plan Design Gate `passed`?
