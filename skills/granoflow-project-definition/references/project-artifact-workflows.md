# Project Artifact Workflows

## UI Prototype

When primary screens, navigation/menu, key states, and theme direction are
clear enough to visualize, suggest an effect preview once. Enter this branch
immediately when the user asks for one.

1. Summarize the UI facts and remaining visual assumptions.
2. Use host authoring tools to create a self-contained `index.html` plus local
   CSS/static assets. Do not claim that Granoflow MCP renders HTML.
3. Give the user a clickable host-local preview for a sidebar or browser.
4. Ask for visual confirmation against layout, theme, navigation, critical
   states, empty/error states, accessibility, and responsive behavior.
5. Visual confirmation authorizes only packaging that exact source hash. It is
   not implementation acceptance or execution authorization.
6. Build a deterministic ZIP: root `index.html`, relative paths only, sorted
   entries, normalized timestamps, no symlinks, no path traversal, and all
   required static resources included. Use
   `scripts/package_prototype.py SOURCE OUTPUT` (or `--dry-run` before writing)
   unless the host already provides an equivalent deterministic packager.
7. Call `granoflow_logical_attachment_replace` with `visualConfirmed=true` to
   replace the target entity's `ui_prototype` logical slot and retain App-owned
   SHA/manifest evidence.

## Project Design Baseline Prototype

The project baseline is not the mutable `ui_prototype` logical slot. It is a
versioned App-owned Prototype linked to the project and referenced exactly from
Project Work.

1. Generate a realistic `index.html` from the proposed design profile, primary
   user journeys, navigation, shared components, critical states, empty/error
   states, accessibility, and responsive behavior.
2. Use real project/domain copy. A generic landing page, lorem ipsum, or a
   uniform AI-style feature grid fails the baseline quality gate.
3. Package deterministically with `scripts/package_prototype.py SOURCE OUTPUT`.
4. Call `granoflow_project_design_baseline_import`; then call
   `granoflow_project_design_baseline_read` with the returned exact
   `prototypeId`, `versionId`, and `packageSha256`.
5. Preview the App-linked artifact with the complete design proposal. Ask one
   visual-direction confirmation covering that exact package hash.
6. Store the exact ids/hash/manifest fields under
   `engineering.theme_and_design_system.prototype_template`; store the same
   hash under `visual_confirmation.template_package_sha256`.
7. A later revision imports a new immutable version and reopens visual
   confirmation. Never resolve "current" or "latest" in the host.

## Data Model

- Owner: project only.
- Slot: `data_model`.
- Filename: `data-model.md`.
- Every table uses a two-dimensional Markdown table covering field, type,
  nullability, default, keys/indexes/constraints, relations, ownership,
  retention, migration/backfill, sync/conflict, and notes.
- Include detailed prose for invariants, write owners, lifecycle, privacy,
  deletion/archive, compatibility, rollback, and unresolved decisions.
- Any later project/milestone/task discussion that changes data updates this
  same project slot. Never create a second current data model attachment.

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
- referenced screen/menu/state ids exist in the prototype or are marked
  planned;
- data entities used by workflows exist in `data-model.md`;
- workflow acceptance and failure paths map to Project Work acceptance ids;
- implementation evidence does not claim completion beyond confirmed artifacts;
- stale, conflicting, missing, or unconfirmed artifacts fail closed with all
  findings returned together.
