# Project Artifact Workflows

## UI Prototype (Task / Milestone Slot)

When a **task changes UI**, a high-fidelity HTML prototype is **mandatory**
(see `granoflow-agent-workflow/task-work-document-workflow` UI Change Prototype
Mandate). Do not treat prototypes as optional suggestions. Enter this branch as
soon as UI change is detected—not only when the user asks.

1. Read the confirmed project Design Baseline first
   (`granoflow_project_design_baseline_read` with exact ids/SHA). Accept against
   contract fidelity (契约级一致): Shell IA, tokens, main-path regions Must
   match; pixel/motion 1:1 is not required.
2. Declare `derivedFrom` the baseline `prototypeId`, `versionId`, and
   `packageSha256` in Task Work / attachment metadata (document-level gate in
   this release). Missing `derivedFrom` on a UI-changing task fails closed.
3. Use host authoring tools to create a self-contained `index.html` plus local
   CSS/static assets. Do not claim that Granoflow MCP renders HTML.
4. Give the user a clickable host-local preview for a sidebar or browser.
5. Ask for visual confirmation against layout, theme, navigation, critical
   states, empty/error states, accessibility, and responsive behavior.
6. Visual confirmation authorizes only packaging that exact source hash. It is
   not implementation acceptance or execution authorization.
7. Build a deterministic ZIP: root `index.html`, relative paths only, sorted
   entries, normalized timestamps, no symlinks, no path traversal, and all
   required static resources included. Use
   `scripts/package_prototype.py SOURCE OUTPUT` (or `--dry-run` before writing)
   unless the host already provides an equivalent deterministic packager.
8. Call `granoflow_logical_attachment_replace` with `visualConfirmed=true` to
   replace the target entity's `ui_prototype` logical slot and retain App-owned
   SHA/manifest evidence.
9. Record `【增强实现】` / `implementation_notes` where the HTML is schematic
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

### Authoring Steps

1. Lock `stack_capability_profile` first. Do not draw `forbidden` patterns.
2. Generate realistic HTML from the proposed design profile, primary journeys,
   shared components, critical states, empty/error states, accessibility, and
   responsive/Shell behavior. Invoke `skill_routing` Skills with
   `phase: baseline` then `phase: shell`.
3. Use real project/domain copy. A generic landing page, lorem ipsum, or a
   uniform AI-style feature grid fails the baseline quality gate.
4. Emit Design Tokens beside the HTML (for example `tokens/*.json`) and list
   them under `engineering.theme_and_design_system.token_sources`.
5. Add `implementation_notes` / `【增强实现】` for schematic HTML that the
   stack will implement with richer controls.
6. Package deterministically with `scripts/package_prototype.py SOURCE OUTPUT`.
7. Call `granoflow_project_design_baseline_import`; then call
   `granoflow_project_design_baseline_read` with the returned exact
   `prototypeId`, `versionId`, and `packageSha256`.
8. Preview the App-linked artifact with the complete design proposal. Confirm
   Baseline+Shell as one package decision covering that exact package hash
   (interactive confirm, or unattended `auto_accept_recommendation`).
9. Store the exact ids/hash/manifest fields under
   `engineering.theme_and_design_system.prototype_template`; store the same
   hash under `visual_confirmation.template_package_sha256`; store token file
   references under `token_sources`.
10. A later revision imports a new immutable version and reopens visual
    confirmation. Never resolve "current" or "latest" in the host.

### Contract Fidelity For Downstream Work

Downstream prototypes and code Must preserve Shell mode, primary navigation IA,
token roles, and main-journey layout regions. They Should stay visually close.
They Won't be judged on pixel or spring-feel parity. Material Shell/token
changes require a new baseline version—not silent drift in a task prototype.

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
- data entities used by workflows exist in `data-model.md`;
- workflow acceptance and failure paths map to Project Work acceptance ids;
- implementation evidence does not claim completion beyond confirmed artifacts;
- stale, conflicting, missing, or unconfirmed artifacts fail closed with all
  findings returned together.
