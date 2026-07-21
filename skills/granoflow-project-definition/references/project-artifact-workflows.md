# Project Artifact Workflows

## Prototype Preview Gate (every HTML prototype)

Applies to **every** discrete HTML prototype the host authors in this workflow:

- each Design Baseline journey/critical-state screen (or self-contained preview
  unit) as it becomes previewable;
- landscape and portrait App Shell previews when authored as distinct preview
  units;
- every task/milestone `ui_prototype` package.

MCP does not render HTML. The host must expose a **clickable** preview link
(file URL, local static server, or host sidebar/browser open path).

### Mode Gate

Default `executionMode: interactive` unless the user explicitly declared
unattended. Never infer unattended from prototype authoring alone.

### Interactive (default)

When each prototype becomes previewable:

1. Emit the clickable preview link (and a one-line what-to-review hint).
2. **Stop** and wait for the user's visual review decision (accept / revise /
   reject) before packaging with `visualConfirmed=true`, importing Baseline,
   starting the next prototype, or continuing UI implementation.
3. Do not batch several unfinished prototypes into one confirmation when each
   already has its own previewable link—review them one by one.

Skipping the wait fails closed as `prototype_preview_review_required`.

### Unattended (explicit only)

When each prototype becomes previewable:

1. Emit the same clickable preview link as a **non-blocking notice** (does not
   consume the unattended interaction budget; do not wait).
2. Auto-continue solvable packaging/import/next work per
   `unattended-interaction-contract` (Baseline may still use
   `auto_accept_recommendation` only under explicit unattended).
3. Append `{ title, path_or_url, entity, sha_or_pending }` to the run's
   `prototype_link_ledger`.

At **run close** (Project Definition Done, milestone/task batch complete, or
`complete_with_residuals`):

1. Emit a mandatory **Prototype Link Digest** listing every ledger entry with
   clickable links in one place for human audit.
2. Do not omit links that were already shown mid-run.
3. The digest is the unattended closing review surface; it does not reopen
   mid-run waits. Park outstanding visual taste follow-ups in the Residual
   Report when the user must still judge aesthetics offline.
4. Omitting the digest fails closed as `prototype_link_digest_required`.

### Option-set exception (interactive Design Spec / Shell triads only)

When Project Definition is **interactive** and presents a **choice set of
three** Design Spec or Shell prototypes:

1. Design Spec triad: author all three with **three different random visual
   seeds** before asking (never reuse a seed inside the Spec triad).
2. Shell triad: author all three **fitted to the selected Spec**; use distinct
   chrome-variant ids only—**no** independent palette seeds
   (`shell_spec_mismatch` if Spec is broken).
3. Emit **all three** clickable links in one batch (plus a one-line contrast
   note per option).
4. **One wait** for select / revise / request-more—do not force a separate wait
   after each of the three mid-set.
5. After the user picks one, further single-screen refinements of that winner
   again follow the per-prototype rules above.

Unattended mode **does not** use this triad exception (see Design Spec / Shell
rounds below).

## UI Prototype (Task / Milestone Slot)

When a **task changes UI**, a high-fidelity HTML prototype is **mandatory**
(see `granoflow-agent-workflow/task-work-document-workflow` UI Change Prototype
Mandate). Do not treat prototypes as optional suggestions. Enter this branch as
soon as UI change is detected—not only when the user asks.

1. Read the confirmed project Design Baseline first
   (`granoflow_project_design_baseline_read` with exact ids/SHA). Accept against
   contract fidelity (契约级一致): Shell IA, tokens, main-path regions, and
   locked widgets Must match; pixel/motion 1:1 is not required.
2. Declare `derivedFrom` the baseline `prototypeId`, `versionId`, and
   `packageSha256` in Task Work / attachment metadata (document-level gate in
   this release). Missing `derivedFrom` on a UI-changing task fails closed.
3. **Do not** apply a new random visual seed. Task prototypes inherit the
   locked Spec + Shell. Fail closed `task_prototype_seed_forbidden`.
4. Load project `widgets.yaml`; reuse widgets with the same role before
   inventing new chrome/controls (`widget_reuse_required` if skipped).
5. Use host authoring tools to create a self-contained `index.html` plus local
   CSS/static assets. Do not claim that Granoflow MCP renders HTML.
6. Apply the **Prototype Preview Gate**: give a clickable host-local preview
   link; interactive waits for visual review; unattended records the link and
   continues, then includes it in the closing digest.
7. Visual confirmation (interactive user accept, or unattended auto-accept when
   explicitly authorized) authorizes only packaging that exact source hash. It
   is not implementation acceptance or execution authorization. After
   confirmation, extract any new/changed reusable widgets into the same
   project `widgets` slot.
8. Build a deterministic ZIP: root `index.html`, relative paths only, sorted
   entries, normalized timestamps, no symlinks, no path traversal, and all
   required static resources included. Use
   `scripts/package_prototype.py SOURCE OUTPUT` (or `--dry-run` before writing)
   unless the host already provides an equivalent deterministic packager.
9. Call `granoflow_logical_attachment_replace` with `visualConfirmed=true` to
   replace the target entity's `ui_prototype` logical slot and retain App-owned
   SHA/manifest evidence.
10. Record `【增强实现】` / `implementation_notes` where the HTML is schematic
    and the target stack will use richer third-party widgets, listing Must
    invariants that remain unchanged.

## Project Design Baseline Package

The project Design Baseline is not the mutable `ui_prototype` logical slot. It
is a versioned App-owned Prototype linked to the project and referenced exactly
from Project Work. It is the authoritative visual/IA reference for later
milestones, task prototypes, and code acceptance.

A complete initialization package **must** include:

1. High-fidelity HTML screens for primary journeys and critical states;
2. Companion Design Tokens (DTCG-oriented JSON or equivalent), referenced from
   Project Work `token_sources`—do not dump the full token graph into YAML;
3. Landscape App Shell (primary navigation + chrome + breakpoints);
4. Portrait App Shell (or an explicit responsive Shell that covers both modes
   with documented breakpoints).

Missing App Shell fails Done and fails visual confirmation for initialization.

### Design Spec then Shell (mode-split rounds)

Project Definition **must not** jump to an unlabeled locked Baseline+Shell.
Run Design Spec first, then Shell. **Design Spec** may explore with random
visual seeds (`impeccable` / matching `skill_routing` Skills).
**From Shell onward, design style converges**: every Shell candidate Must
perfectly fit the **already selected** Design Spec (tokens, typography, color
roles, IA Musts). Do not invent a second visual system at Shell time.

#### Mode split (hard)

| Mode                           | Design Spec                                                                                                                                                                                                                                                                                                                             | Shell                                                                                                                                                                                                                                    |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Interactive (default)**      | **Triad**: exactly three options, **three different random seeds**—one `spec_match` (faithful to user requirements) + two `ai_challenger_*` (AI judges better or at least as good, with rationale). User picks one, revises, or requests more (each new batch again: distinct random seeds, same 1+2 shape unless user says otherwise). | After Spec selection: **Triad** of three Shells that all **reuse the selected Spec**—one `shell_match` + two chrome/structure challengers. Distinct **Shell chrome-variant ids** (not new palette seeds). Same pick / more-options gate. |
| **Unattended (explicit only)** | **Single** Design Spec: faithful `spec_match` only, with **one random seed**. No challengers, no triad wait. Emit link notice + ledger.                                                                                                                                                                                                 | **Single** Shell: faithful `shell_match` only, derived from that Spec—**no independent palette seed**. Emit link notice + ledger. Auto-accept package when explicitly unattended.                                                        |

Contract-fidelity Musts (journeys, IA, acceptance behavior, primary nav, Shell
modes) stay intact on every option. Spec-round challengers may vary craft
presentation within those Musts. Shell-round challengers may only vary chrome
density, nav structure, and breakpoint expression **inside** the selected Spec.

#### Round A — Design Spec

**Interactive**

1. Produce exactly three high-fidelity Design Spec options sharing the same
   product IA and `product_spec_coverage` screens.
2. Assign **three different random seeds** (palette/typography/material—e.g.
   impeccable `palette.mjs` or equivalent). Reusing a seed inside the triad
   fails closed as `design_spec_seed_collision`.
3. Label: `spec_match` | `ai_challenger_a` | `ai_challenger_b` with contrast
   rationale on challengers.
4. Option-set Preview Gate: three links; wait for pick / revise / more options.
5. Record selection under
   `engineering.theme_and_design_system.design_spec_selection` (option id,
   seed, provenance: `user_selected`).

Fail closed `design_spec_triad_required` if fewer than three distinct-seed
options were offered before selection.

**Unattended (explicit only)**

1. Produce **one** Design Spec: `spec_match` only (faithful to user
   requirements), with a **random seed**.
2. Preview Gate: link notice + ledger (no wait, no triad).
3. Record `design_spec_selection` with provenance
   `unattended_spec_match_random_seed`.

#### Round B — App Shell (after Spec selection)

**Convergence rule (hard):** every Shell option Must perfectly fit the selected
Design Spec. Reusing Spec tokens/IA is mandatory. Introducing a new palette /
typography / material seed that breaks Spec → fail closed `shell_spec_mismatch`.

**Interactive**

1. Produce exactly three Shell options (landscape + portrait) derived from the
   **selected** Design Spec tokens/IA only.
2. Assign **three different chrome-variant ids** (structure/density/nav
   expression). Do **not** assign independent palette seeds. Duplicate
   chrome-variant ids → `shell_seed_collision`.
3. Label: `shell_match` | two `ai_challenger_*` with rationale (chrome only).
4. Option-set Preview Gate; wait for pick / more options.
5. Record `shell_selection` with `user_selected` and the Spec selection id/SHA
   it was fitted to.

Fail closed `shell_triad_required` if the interactive Shell triad is skipped.

**Unattended (explicit only)**

1. Produce **one** Shell: `shell_match` only, fitted to the unattended Spec
   (no independent palette seed).
2. Link notice + ledger; record `shell_selection` with
   `unattended_shell_match_fitted_to_spec`.

#### After Spec + Shell are chosen

Merge the **selected** (or sole unattended) Design Spec + Shell into one
deterministic Baseline package, import/readback exact ids/SHA, and lock
`prototype_template` / `visual_confirmation` / `token_sources`. Do not import a
non-selected interactive triad candidate as the project authority. After the
Baseline package is visually confirmed, run the **first mandatory Widget
Catalog extract** (see below) from that confirmed Baseline prototype.

### Authoring Steps

1. Lock `stack_capability_profile` first. Do not draw `forbidden` patterns.
2. Require `product_spec_coverage.status: ready` before Spec/Shell HTML.
3. Run **Round A** under the Mode split above. Invoke `skill_routing` Skills
   with `phase: baseline` (include `impeccable` when available for random
   seeds).
4. Use real project/domain copy. A generic landing page, lorem ipsum, or a
   uniform AI-style feature grid fails the baseline quality gate. Every
   authored journey/critical screen Must map to an adopted
   `product_spec_coverage.screen_coverage` row (`baseline_required: true`);
   unmapped screens fail closed as `product_spec_coverage_incomplete`.
5. After Design Spec selection (or sole unattended Spec), emit/refine Design
   Tokens for that Spec (`tokens/*.json`) under
   `engineering.theme_and_design_system.token_sources`.
6. Run **Round B** under the Mode split above (`phase: shell`). Every Shell
   option Must fit the selected Spec (`shell_spec_mismatch` if not).
7. Add `implementation_notes` / `【增强实现】` where HTML is schematic.
8. Package the chosen Spec+Shell with `scripts/package_prototype.py`.
9. Call `granoflow_project_design_baseline_import`; then
   `granoflow_project_design_baseline_read` with exact
   `prototypeId`, `versionId`, and `packageSha256`.
10. Confirm the imported package hash (interactive: after triad picks / final
    confirm as needed; unattended explicit only:
    `auto_accept_recommendation`). Never auto-accept in interactive mode.
11. Store `prototype_template`, `visual_confirmation.template_package_sha256`,
    `token_sources`, `design_spec_selection`, and `shell_selection`.
12. After Baseline visual confirmation, extract chrome/shared widgets into the
    project `widgets` attachment (`widgets.yaml`)—first mandatory catalog
    write.
13. Later revisions reopen the mode-appropriate Spec/Shell rounds.
    Never resolve "current" or "latest".
14. Closing Prototype Link Digest lists every candidate offered (all triad
    links in interactive; the single Spec + single Shell in unattended).

### Contract Fidelity For Downstream Work

Downstream prototypes and code Must preserve Shell mode, primary navigation IA,
token roles, main-journey layout regions, and **locked widgets** from
`widgets.yaml`. They Should stay visually close. They Won't be judged on pixel
or spring-feel parity.

**Task / milestone `ui_prototype` (hard):**

- Must `derivedFrom` the exact Baseline `prototypeId` / `versionId` /
  `packageSha256`.
- Must **not** apply a new random visual seed (no impeccable palette re-roll,
  no Spec re-exploration). Fail closed `task_prototype_seed_forbidden`.
- Before inventing a new chrome/control/pattern, check `widgets.yaml` and
  reuse when the same role exists (`reuse_policy: must_reuse_when_same_role`).
  Skipping reuse without rationale → `widget_reuse_required`.
- Material Shell/token/widget catalog changes require a new Baseline version
  and catalog update—not silent drift in a task prototype.

## Widget Catalog (project `widgets.yaml`)

YAML expresses the **contract** of reusable UI modules—not full visual
geometry, motion, or platform chrome. Visual truth remains in confirmed HTML
prototypes; the catalog records identity, props, token bindings, states,
composition, reuse policy, and anchors into those prototypes.

### Slot and ownership

- Owner: project only. Logical slot: `widgets`. Default file: `widgets.yaml`.
- One current attachment. Any later extract updates this **same** slot.
- Record `widgets_attachment` (exact file name) and registry SHA/readback in
  Project Work. Missing catalog after confirmed Baseline Shell →
  `widget_catalog_required`. Stale SHA vs App readback →
  `widget_catalog_stale`.

### When to extract

1. **First mandatory extract:** after the Design Baseline package (selected
   Spec + Shell) is visually confirmed—example source is that confirmed
   Baseline prototype (`prototype_template` ids/SHA).
2. **Incremental extracts:** after every later confirmed Baseline revision or
   task/milestone `ui_prototype` that introduces or changes a reusable
   chrome/control/pattern.
3. Do not invent widgets from unconfirmed drafts.

### Example shape (Baseline prototype as source)

```yaml
# widgets.yaml — contract catalog; visuals live in confirmed prototypes
schema: granoflow.widgets
schema_version: 1
widgets:
  - id: shell.top_nav
    kind: chrome # chrome | control | pattern | page_region
    status: locked # proposed | locked | deprecated
    derived_from:
      # Example: the confirmed Design Baseline prototype (previous Spec+Shell)
      prototype_id: "<prototype_template.prototype_id>"
      version_id: "<prototype_template.version_id>"
      package_sha256: "<prototype_template.package_sha256>"
      region_id: top_nav
    tokens: [color.surface, type.body, space.s2]
    variants: [landscape, portrait]
    props:
      title: string
      selected_tab: enum
    states: [default, selected, disabled]
    composition: [shell.tab_item]
    reuse_policy: must_reuse_when_same_role
    implementation_notes: []
```

### Reuse gate

Hosts authoring any UI prototype after the first catalog write Must:

1. Load current `widgets.yaml` (App readback).
2. Prefer existing widget ids for the same role.
3. Add new rows only for new roles; lock them after that prototype is
   confirmed.
4. Never replace a locked widget's visual system via task-local random seed.

## Capability-Critical Dependencies

Established in Project Definition **Step 1** immediately after stack lock.
Record chosen packages in Project Work `engineering.dependencies.approved`
(not a separate attachment). Each critical row needs `name`, `capability`,
`capability_critical: true`, `alternatives_considered`, and
`selection_rationale`. Framework-only selection without required capability
packages fails closed as `capability_dependency_unselected`. Later tasks may
challenge and revise the same Project Work list; they must not silently swap
critical libraries in code.

## Data Persistence And Structured Contracts

Established in Project Definition **Step 1**. Project Work records
`data_persistence`, attachment file names, and artifact registry rows. Full
shapes never live in the Project Work body YAML.

### No business database

When `data_persistence: none`, set `no_database_declaration` to an explicit
statement (for example: 本项目无业务数据库，无需设计表结构). Do not create a
table schema in `data-model.md`. Set `data_model_attachment: not_applicable`.

### Data Model (tables)

- Owner: project only. Slot: `data_model`. Default file: `data-model.md`.
- Required when `data_persistence` implies a business database
  (`embedded_db`, `server_db`, or `mixed` with DB). Record the exact file name
  in `data_and_migrations.data_model_attachment`.
- Every table uses a two-dimensional Markdown table covering field, type,
  nullability, default, keys/indexes/constraints, relations, ownership,
  retention, migration/backfill, sync/conflict, and notes.
- Include detailed prose for invariants, write owners, lifecycle, privacy,
  deletion/archive, compatibility, rollback, and unresolved decisions.
- Any later change updates this **same** project slot. Never create a second
  current data model attachment.

### JSON / structured file contracts

- Owner: project only. Slot: `json_contracts`. Default file:
  `data-contracts.yaml`.
- Required when the project defines JSON or other structured files as a
  contract. Use YAML (or Markdown embedding YAML) for shapes and field
  semantics. Record `json_contracts_attachment`.
- Do not dump full contract graphs into Project Work YAML.

### Constants catalog

- Owner: project only. Slot: `constants_catalog`. Default file:
  `constants-catalog.yaml`.
- Required when the project defines shared constants. List constant names,
  values or types, owners, and purpose in YAML. Record
  `constants_catalog_attachment`.

### Code must match attachments

Tasks that change database schema, JSON/structured file shapes, or shared
constants **must** update the corresponding project attachment and refresh
registry SHA/readback in the same task before Delivery. Code that drifts from
these attachments fails closed with `data_artifact_stale`.

## Workflows

- Owner: the entity whose scope the process describes.
- Slot: `workflows` on project, milestone, or task.
- Filename: `workflows.md`.
- One entity has one current workflows attachment. Multiple diagrams live in
  that same file.
- Every diagram has a stable id, Mermaid source, trigger, actors, preconditions,
  happy path, alternate/error paths, state/data changes, downstream handoff,
  observability, and detailed prose. A diagram without explanation is
  incomplete.

## Artifact Registry And Consistency

Project Work records the current entity, slot, attachment id, SHA, status,
source decision, and relations for every governed artifact. Before automation
or completion, verify:

- registry SHA matches App readback;
- Design Baseline package SHA matches `prototype_template` and
  `visual_confirmation`;
- referenced screen/menu/state ids exist in the baseline or are marked
  planned;
- App Shell landscape and portrait coverage is present for initialization Done;
- `widgets.yaml` exists after Baseline confirmation with registry SHA readback;
- data entities used by workflows exist in `data-model.md`;
- workflow acceptance and failure paths map to Project Work acceptance ids;
- implementation evidence does not claim completion beyond confirmed artifacts;
- stale, conflicting, missing, or unconfirmed artifacts fail closed with all
  findings returned together.
