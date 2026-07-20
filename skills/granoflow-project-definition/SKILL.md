---
name: granoflow-project-definition
description: Initialize or refine a Granoflow software project through three steps—Project Work, Design Baseline with tokens, and App Shell—lock stack-capable visuals under contract fidelity, and hand off to milestone/task skills. Activate with "Initialize this project" / "Define this project" / "初始化这个项目"; not "Initialize Granoflow".
---

# Granoflow Project Definition

Use this Skill when a user wants to start, define, refine, or initialize a
software project in Granoflow—including Project Work, Design Baseline, and App
Shell. It supports both technical users who edit one field at a time and users
who provide only a vague outcome or mixed-format product documents.

**Activation phrases (examples):** `Initialize this project`,
`Define this project`, `Start project definition`, `初始化这个项目`,
`定义这个项目`, `根据这些产品文档初始化项目并锁定设计基线`.

**Not this Skill:** `Initialize Granoflow` / `初始化 Granoflow` activates
`granoflow-first-run-import` (connection, capability packs, optional agent-data
import). Never route project definition through first-run import.

Granoflow App owns Project Work content, logical attachment identity,
confirmation, readiness, hashes, design-baseline versions, and action
admission. MCP is a thin protocol surface. The host Agent owns the
conversation, recommendations, HTML authoring, packaging, and execution tools.

## Authority Of Initialization Outputs

The confirmed Project Work YAML plus the App-linked Design Baseline (including
Design Tokens and landscape/portrait App Shell) are the authoritative visual
and information-architecture reference for:

- every later milestone;
- every task-level prototype;
- code implementation and acceptance.

Later work must not invent a parallel visual authority. Changing navigation IA,
Shell mode, or locked tokens requires a new Design Baseline version and a fresh
visual confirmation. Subsequent prototypes should declare
`derivedFrom` the exact baseline `prototypeId` / `versionId` /
`packageSha256` (document-level gate in this release; App hard reject is a
later iteration).

**Acceptance bar is contract fidelity (契约级一致), not pixel parity:**

- **Must:** primary navigation IA; landscape/portrait Shell modes and stated
  breakpoints; locked Design Tokens (roles for color, type scale, key spacing);
  main-journey layout regions; no new global primary entry absent from the
  baseline.
- **Should:** secondary visual closeness.
- **Won't:** pixel-perfect screenshots; spring-feel video match; native control
  chrome.

**Enhanced implementation:** when Flutter (or another stack) can look better
with mature third-party widgets, HTML may convey intent only, but each such
case must carry an `【增强实现】` / `implementation_notes` note naming the
intended component and the Must invariants that remain unchanged.

## Required References

1. Read the public
   `granoflow-agent-workflow/project-work-document-template` reference for the
   canonical YAML shape.
2. Read the public
   `granoflow-agent-workflow/requirement-intake-and-traceability` reference
   before extracting product documents, user stories, notes, chat, screenshots,
   or mixed-format source material.
3. Read `references/project-definition-interaction.md` before interviewing or
   recommending values.
4. Read `references/project-artifact-workflows.md` when UI prototypes, Design
   Baseline, App Shell, tokens, data models, or workflows are discussed.
5. Read the public
   `granoflow-agent-workflow/unattended-interaction-contract` when
   `executionMode` is unattended.
6. Call `granoflow_agent_preferences_get(projectId)` when preferences already
   exist. During initialization, recommend and write the `agent_preferences`
   project-rule section so later workflows can reuse explanation, execution,
   and Git choices without asking again. Preferences never weaken readiness,
   quality, authorization, acceptance, or external-action gates.

## Entry Modes

- `guided_step_by_step`: the user chooses a section or answers the next smallest
  decision-changing batch.
- `guided_from_vague_request`: extract facts, label assumptions, propose
  defaults, and guide the user to the same canonical document.

The modes share one `project_work` logical slot. Switching modes never creates
a second current Project Work attachment.

## Three-Step Initialization Outcome

Project initialization is opinionated and ends after three steps. Do not ask
the user to select Skills, fonts, colors, layout systems, or prototype engines
one item at a time. Style Skills (for example `apple-design`) are locked in
`skill_routing` during Step 1 and invoked only in Steps 2–3 for matching
`phase` values (`baseline`, `shell`, `later_ui`).

### Step 1 — Project Work (intake + stack + routing)

1. Resolve exactly one Granoflow project or ask the user to choose.
2. Register and read every supplied source (requirement intake). Preserve
   unexpected requirements, label inference, and surface conflicts instead of
   choosing silently.
3. Fill Project Work from the canonical template. Preserve unknowns as
   null/empty plus provenance; never invent values to look complete.
4. Lock `engineering.stack` and a `stack_capability_profile`
   (`allowed` / `high_cost` / `forbidden`) before any HTML baseline work.
   Prototypes must not include `forbidden` patterns.
5. Complete **capability-critical third-party library selection** under
   `engineering.dependencies` before Project Work confirm (same Step 1 pass as
   stack—do not defer to the first coding task):
   - From requirements, list each primary product capability that needs a
     third-party library (examples: EPUB parse/render, encryption, media
     codecs, maps, payments SDK, embedded DB driver).
   - For each capability, recommend one concrete package (`name`), record
     `capability`, `capability_critical: true`, `purpose`,
     `alternatives_considered` (at least one real alternative or an explicit
     "no viable alternative" note), `selection_rationale`, and
     version/license/cost fields when known.
   - Write chosen packages into `dependencies.approved`. Framework-only answers
     (e.g. "use Flutter") without capability libraries fail closed as
     `capability_dependency_unselected` when the product clearly needs them.
   - If the product truly needs no such libraries beyond the stack, set
     `approved: []` and an explicit `no_capability_dependency_declaration`.
   - Interactive: present recommended + alternatives in one batch; unattended:
     adopt recommendations immediately.
6. Lock data surface declaration under `engineering.data_and_migrations`:
   - Set `data_persistence` (`none` | `local_files` | `embedded_db` |
     `server_db` | `mixed`).
   - If `none`: set `no_database_declaration` to an explicit statement that the
     project has no business database and needs no table schema; do **not**
     invent `data-model.md`.
   - If the project has a business database: create/update project
     `data_model` attachment (`data-model.md`), set
     `data_model_attachment`, and register it.
   - If the project defines JSON / structured files: create a separate
     `json_contracts` attachment (default `data-contracts.yaml` with YAML
     shapes), set `json_contracts_attachment`, and register it—never embed
     full shapes in Project Work body YAML.
   - If the project defines shared constants: create a separate
     `constants_catalog` attachment (default `constants-catalog.yaml`), set
     `constants_catalog_attachment`, and register it.
   - Mark unused attachment fields `not_applicable` rather than leaving them
     silently empty when the surface was considered.
7. Recommend one `design_profile` and `skill_routing` (capabilities with
   `phase`). Never present a menu of design Skills.
8. When required fields remain empty and the Agent lacks a safe recommendation,
   use `grill-me` (or an equivalent user_only question batch). Every question
   includes a recommended option.
9. Confirm Project Work (`granoflow_project_work_confirm`) only after App
   content/hash readback. Confirmation does not authorize code execution,
   commit, push, publish, or deploy.

### Step 2 — Design Baseline + Design Tokens

1. Require host evidence that `granoflow_product_builder_v1` is ready. If it is
   declined, missing, or partially available, return `capability_pack_not_ready`
   for automatic initialization. Manual Project Work editing remains available.
2. Invoke only `model_allowed` Skills listed in `skill_routing` whose `phase`
   includes `baseline`.
3. Generate one realistic high-fidelity HTML Design Baseline from real product
   journeys and critical states, constrained by `stack_capability_profile`.
   Do not use lorem ipsum, generic three-card AI layouts, or a marketing
   landing page when the product is an application.
4. Emit companion Design Tokens in DTCG-oriented JSON (or an equivalent
   mappable form). Reference them from `token_sources`; do not embed the full
   token graph in Project Work YAML.
5. Record `【增强实现】` / `implementation_notes` where HTML only conveys
   intent and the stack will use richer widgets.

### Step 3 — App Shell (landscape + portrait)

1. Invoke only Skills whose `phase` includes `shell`.
2. Deliver landscape and portrait App Shell (primary navigation, chrome,
   breakpoints) inside the **same** Design Baseline package. Missing Shell
   blocks Done and blocks `visual_confirmation` success.
3. Package deterministically; import with
   `granoflow_project_design_baseline_import`; read back exact
   `prototypeId`, `versionId`, and `packageSha256` via
   `granoflow_project_design_baseline_read`. Never resolve "current" or
   "latest".
4. Confirm Baseline+Shell as one visual package decision (interactive: user
   confirm; unattended: `auto_accept_recommendation` by default).
5. Lock `prototype_template`, `visual_confirmation`, and `token_sources` in
   Project Work after App readback.

### Done And Handoff

Initialization is Done only when all of the following hold:

- Project Work is complete, current, and App-confirmed;
- Design Baseline is current with exact SHA readback;
- Baseline package includes landscape and portrait App Shell;
- `skill_routing` and `stack_capability_profile` are locked;
- contract-fidelity and enhanced-implementation rules are recorded;
- `data_persistence` is set; `none` includes explicit
  `no_database_declaration`; required data attachments (tables / JSON
  contracts / constants catalog) exist with file names recorded in Project
  Work and registry SHA readback;
- capability-critical third-party libraries are selected in
  `dependencies.approved` (each with `capability`, recommended package,
  alternatives considered, and rationale), or
  `no_capability_dependency_declaration` is explicit when none apply.

Emit a short handoff card naming `granoflow-portfolio-orchestrator` as the
primary next owner (creates all milestones, then quality-authors tasks).
Component Skills: `granoflow-milestone-workflow` (milestone create),
`granoflow-task-authoring` (task create), then
`granoflow-milestone-coordination` / `granoflow-task-orchestrator` for
charter/Analysis/execution. This Skill does **not** create the full
milestone/task tree, run task Analysis/Plan Grill, or implement product code.

## Workflow

1. Resolve the project and current `project_work` attachment.
2. Choose entry mode. Vague requests default to `guided_from_vague_request`.
3. Run Step 1 (intake → stack capability → capability-critical libraries →
   data persistence → design routing → Project Work confirm). Every
   communication states `recommended_value`, reason, and source. In
   interactive mode, wait for confirm/customize. In unattended mode, adopt
   recommendations immediately except real blockers from
   `unattended-interaction-contract` (`direction_change`,
   `missing_user_only_input`, `forbidden_action`, etc.).
4. Check `granoflow_product_builder_v1`, then run Steps 2 and 3.
5. When the user asks to create/modify a milestone or task manually, call
   `granoflow_project_work_evaluate` with that action. Missing paths return in
   one batch. Before creating a task, apply
   `granoflow-agent-workflow/task-authoring-quality-contract`.
6. Automatic create/execute/publish/deploy/complete actions require
   complete confirmed Project Work; `project_document_incomplete` returns to
   definition. Never bypass App admission.
7. After initialization Done, later visual work reads the confirmed baseline
   and `skill_routing`. Invoke listed Skills without re-selecting a style
   menu. Task/milestone prototypes should `derivedFrom` the exact baseline
   package SHA and accept against contract fidelity.

## Automation Boundary

The Project Work gate answers whether the project definition is sufficient for
an action. It does not execute product code, create images outside the baseline
workflow, run a browser as acceptance, commit, push, publish, deploy, delete,
pay, message, or invent subjective approval. Those actions remain with host
tools and their own authorization gates.

## Success Criteria

- Activation phrases route here; `Initialize Granoflow` does not.
- A partial discussion can produce a useful, hash-read-back Project Work YAML.
- Every recommendation is explicit; unattended adopts recommendations without
  re-asking, except real blockers.
- Stack capability is locked before Design Baseline HTML is authored.
- Every automatic project initialization yields one App-linked Design Baseline
  that includes Design Tokens references, landscape App Shell, and portrait
  App Shell, plus one confirmed `skill_routing` profile.
- Contract fidelity (not pixel 1:1) is the stated acceptance bar; enhanced
  implementation notes are present where HTML is schematic.
- Confirmed baseline is declared the reference for later milestones, task
  prototypes, and code acceptance.
- Initialization hands off to milestone/task Skills without pretending those
  phases already ran.
- Manual milestone/task definition checks only real dependencies; automatic
  actions require complete, current, App-confirmed Project Work.
