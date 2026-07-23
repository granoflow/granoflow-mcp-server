---
name: granoflow-project-definition
description: Initialize or refine a Granoflow software project—AI self-checks Project Work, user browse-confirms Engineering Acceptance Pack (folder structure required), user-selects Design Spec/Shell when UI applies—then hand off to milestone/task skills. Activate with "Initialize this project" / "Define this project" / "初始化这个项目"; not "Initialize Granoflow".
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

## Keyword

- `#initialize-this-project`
- `#project-definition`
- `#design-baseline`

## When to use

- User asks to initialize or define **this** software project (not Granoflow
  itself).
- Need Project Work + Design Baseline (tokens + required layout-family App Shell)
  locked under contract fidelity before milestone/task automation.

## Authority Of Initialization Outputs

The confirmed Project Work YAML plus the App-linked Design Baseline (including
Design Tokens and every required layout-family App Shell) are the authoritative visual
and information-architecture reference for every later milestone, task-level
prototype, and code acceptance.

Later work must not invent a parallel visual authority. Changing navigation IA,
Shell mode, or locked tokens requires a new Design Baseline version and a fresh
visual confirmation. Subsequent prototypes Must declare `derivedFrom` the exact
baseline `prototypeId` / `versionId` / `packageSha256` (document-level gate in
this release).

**Acceptance bar combines contract fidelity with reference-viewport
pixel-level high-fidelity:**

- **Must:** primary navigation IA; landscape/portrait Shell modes and stated
  breakpoints; locked Design Tokens; main-journey layout regions; no new global
  primary entry absent from the baseline; locked widgets when catalog exists.
- **Must at reference viewports:** meet the Project fidelity policy's numeric
  threshold and AI visual review.
- **Should elsewhere:** preserve responsive mapping and secondary visual
  closeness.
- **May differ:** platform-native chrome only with a declared, approved
  exception.

**Enhanced implementation:** when the target stack can look better with mature
third-party widgets, HTML may convey intent only, but each such case must carry
an `【增强实现】` / `implementation_notes` note naming the intended component and
the Must invariants that remain unchanged.

**Design-first (hard):** prototypes stay ahead of engineering as the user-demand
surface. Before Preview Gate, check **product truth** (no unauthorized
states/capabilities). High-risk platform-coupled screens still preview first,
then take a short Tech Note in parallel; Readiness needs a feasibility
conclusion (as drawn / degraded / revise design). Details:
`references/project-artifact-workflows.md` § Design-first, product-truth, and
high-risk feasibility.

## Required References

1. Read `granoflow-agent-workflow/project-work-document-template` for the
   canonical YAML shape.
2. Read `granoflow-agent-workflow/requirement-intake-and-traceability` before
   extracting mixed-format product sources.
   Route Project Definition review through Project Work `review_routing`:
   `prd-review` by default, with office-hours or CEO review only when strategy,
   market, or product-risk conditions apply. Record native fallback evidence
   if a preferred reviewer is unavailable.
3. Read `granoflow-agent-workflow/responsive-prototype-finalization` for the
   platform matrix, required layout families, Prototype Bundle, Widget
   promotion, and rendered fidelity gates.
4. Read `granoflow-agent-workflow/discussion-writeback-contract` whenever the
   user accepts a mid-init adjustment (product coverage, Baseline/Shell, later
   task prototypes): App-slot writeback before the next gate. In the same
   batch, read `granoflow-agent-workflow/change-impact-fanout` and close the
   impact ledger (sibling tasks/docs/notes/cards) before claiming the decision
   done.
5. Read [project-definition-interaction.md](references/project-definition-interaction.md)
   before interviewing or recommending values (Mode Gate, batches).
6. Read [project-artifact-workflows.md](references/project-artifact-workflows.md)
   for Design Spec/Shell, Preview Gate, widgets, and task Craft Gate / option
   sets.
7. Read [hard-constraints.md](references/hard-constraints.md) before Done or
   any `visualConfirmed=true` to verify thread-confirmed fail-closed rules.
8. Read [product-spec-flow-decomposition.md](references/product-spec-flow-decomposition.md)
   during Step 1 product-spec coverage (operation flowchart → serial gates vs
   parallel ops → page-count conclusion + stress paths; not risk labels).
9. Apply Mode Gate: default `executionMode: interactive` unless the user
   **explicitly** declares unattended. Read
   `granoflow-agent-workflow/unattended-interaction-contract` only when
   unattended.
   8b. When the product is a mobile or desktop App, load
   `granoflow-agent-workflow/app-icon-source-gate` during Step 1, persist
   `product.app_icon`, and lint with `lint_app_icon_source_gate.py` before
   confirm / Done (`app_icon_source_*` fail-closed codes in
   `hard-constraints.md`).
   8c. Before Engineering Acceptance Pack emit / `granoflow_project_work_confirm`,
   load `granoflow-agent-workflow/engineering-acceptance-pack` and
   `granoflow-agent-workflow/markdown-html-acceptance-render`. YAML is AI
   self-checked; the pack is user browse-confirm.
10. Call `granoflow_agent_preferences_get(projectId)` when preferences exist;
    recommend `agent_preferences` during init (interactive: wait before write).
    Preferences never weaken readiness, quality, authorization, acceptance, or
    external-action gates.

## Entry Modes

Entry modes pace the conversation; they are **not** unattended authorization.

- `guided_step_by_step`: user picks a section or the next smallest
  decision-changing batch.
- `guided_from_vague_request`: extract facts, label assumptions, propose
  defaults, same canonical document.

Both default to `executionMode: interactive` (**ask → recommend → wait**).
Unattended apply/adopt requires an explicit user declaration. The modes share
one `project_work` logical slot. Switching modes never creates a second current
Project Work attachment.

## Three-Step Initialization Outcome

Project initialization is opinionated and ends after three steps. Do not ask
the user to select Skills, fonts, colors, layout systems, or prototype engines
one item at a time. Recommend one `skill_routing` package in Step 1
(interactive: wait; unattended explicit only: adopt) and invoke listed Skills
only in Steps 2–3 for matching `phase` (`baseline`, `shell`, `later_ui`).

Unless the user explicitly declared unattended, every Step 1–3 decision batch
follows **ask → recommend → wait for the user to decide**. Drafting YAML/HTML
is allowed; treating values as confirmed, confirming Project Work, or
auto-accepting Baseline+Shell is not.

### Step 1 — Project Work

Intake → stack capability → capability-critical libraries → data persistence →
directory/module locks → design routing → **AI self-check** → **Engineering
Acceptance Pack (user browse-confirm)** → Project Work App confirm. Detail:
[project-definition-interaction.md](references/project-definition-interaction.md).
Pack contract: `granoflow-agent-workflow/engineering-acceptance-pack`.

**Acceptance division (hard):** Project Work YAML is **AI self-checked** (never
the user-facing acceptance page). Engineering Acceptance Pack is **user
browse-and-confirm**. Design Spec / Shell remain **user selection** in Steps
2–3 when `visual_baseline.applicability: required`.

Actions:

1. Resolve one project; emit Mode Gate notice.
2. Requirement intake + **Product Spec Completeness Hard Gate**
   (`product_spec_coverage`; mandatory operation-flow / serial-gate page-count
   conclusion + stress paths + **screen detail registration** /
   `ui_details` when sources state them; no confirm while status is not
   `ready`).
3. Fill Project Work from the canonical template; preserve unknowns; no fake
   completeness. Initialization blockers must not stay `deferred_unknown`.
   When product docs name durable IT fixture/corpus rules, fill
   `engineering.quality_gates.integration_test_special_requirements` (see
   `integration-test-special-requirements`); otherwise leave `[]`.
4. Lock `engineering.stack` and `stack_capability_profile` before any HTML baseline
   work. Interactive: wait; unattended: adopt.
5. Complete **capability-critical third-party library selection** under
   `engineering.dependencies` before Project Work confirm (same Step 1 pass as
   stack—do not defer to the first coding task): write
   `dependencies.approved` (or explicit `no_capability_dependency_declaration`).
   Framework-only answers fail closed as `capability_dependency_unselected`
   when capabilities clearly need packages. Record `alternatives_considered`.
6. Recommend `data_persistence`; if `none`, set `no_database_declaration`.
   Create `data_model` / `json_contracts` (`data-contracts.yaml`) /
   `constants_catalog` (`constants-catalog.yaml`) attachments when required.
7. Lock **directory structure + modules** (`engineering.directory_structure`
   with non-empty `roots`; at least one `architecture.modules` row with `id` +
   `responsibility`). Interactive: recommend → wait; unattended: adopt. Empty
   roots → `directory_structure_unselected`.
8. Recommend one `design_profile` + design `skill_routing` (never a Skills
   menu), separately from Project Work `review_routing`. Set
   `visual_baseline.applicability` to `required` or `not_applicable` with
   basis (CLI/library/no UI chrome). Unresolved →
   `visual_baseline_applicability_unresolved`.
9. Use `grill-me` for remaining decision-changing gaps (interactive wait;
   unattended explicit-only auto-adopt).
10. **AI self-check** Project Work + companions (`init_ai_self_check`); record
    `passed` or fail closed `init_ai_self_check_failed`. Do **not** present
    raw YAML as the user acceptance page.
11. Emit **Engineering Acceptance Pack** (project from YAML; MD→HTML via
    `markdown-html-acceptance-render`). Interactive: Preview Gate links →
    **wait** for browse accept/revise. Unattended: link digest + Mode Gate
    adopt. Confirm without pack accept →
    `engineering_acceptance_pack_unconfirmed`.
12. `granoflow_project_work_confirm` only after pack accepted/adopted **and**
    App content/hash readback. Confirmation does not authorize
    execute/commit/push/publish/deploy.

Success criteria:

- `product_spec_coverage.status` is `ready`.
- `stack_capability_profile` locked; capability libraries or explicit none.
- `directory_structure.roots` non-empty; modules valid.
- `init_ai_self_check.status: passed`; Engineering Pack `status: accepted`
  (or valid unattended adopt).
- Project Work App-confirmed with hash readback.

Checkpoints:

- Interactive batches wait; unattended never inferred.
- No HTML baseline before stack capability lock.
- No `granoflow_project_work_confirm` before Engineering Pack accept.

### Step 2 — Design Baseline + Design Tokens

**Skip** when `visual_baseline.applicability: not_applicable` (record basis;
Steps 2–3 and `widgets.yaml` are not required for Done).

Before entering Step 2 for a UI project, complete and lint
`platform_support_matrix`. iOS, Android, macOS, and Windows each need an
explicit support disposition. Supported rows require exact versions, devices,
architectures, orientations, required test versions, layout-family mappings,
and source refs. Product documents win; otherwise recommend values from
authoritative platform evidence. Interactive mode waits, while explicitly
unattended mode records `unattended_auto_adopted`.

When `required`: Design Spec round first (Mode split in
[project-artifact-workflows.md](references/project-artifact-workflows.md)), then
tokens for the chosen Spec. **User selects** Spec options (interactive triad
Preview Gate).

Actions:

1. Require `granoflow_product_builder_v1` ready or return
   `capability_pack_not_ready` (manual Project Work still allowed).
2. Require `product_spec_coverage.status: ready`.
3. Invoke `skill_routing` Skills with `phase: baseline` (include `impeccable`
   when available to **compose** palettes from drawn seeds).
4. Design Spec Mode split:
   - **Interactive:** triad from `draw_visual_lots.py --kind spec --count 3
--record` (**true random**; never hand-invent seeds; no classroom salt)—
     `spec_match` + two `ai_challenger_*`. Each option is a **Style Guide /
     Design Tokens board** (Colors, Typescale, Spacing, Grid/Breakpoints,
     Component states, Shadows&Radius)—**not** a gallery of every product
     screen. Preview Gate: pick / **换新批** (`--dedupe ledger`) / **在某套上改**.
     User-facing copy uses plain-language labels only—**no seed ids or internal
     option enums**. Fail closed `design_spec_triad_required` /
     `design_spec_seed_collision` / `design_spec_seed_not_drawn` /
     `design_spec_wrong_artifact_type` / `design_spec_user_facing_jargon` /
     `visual_lot_dedupe_required` / `visual_lot_exhausted`.
   - **Unattended (explicit only):** one `spec_match` via true-random draw.
     Link notice + ledger (plain-language title).
5. Emit Design Tokens → `token_sources`; record `【增强实现】` /
   `implementation_notes` where schematic; record `design_spec_selection`.

Success criteria:

- `design_spec_selection` recorded (option id if any, seed, provenance).
- `token_sources` set for the chosen Spec.
- Spec previews are Style Guides; journey-screen HTML deferred to task/milestone
  `ui_prototype` (init Baseline = Spec + Shell only).

Checkpoints:

- Preview Gate links shown before pick/confirm.
- Spec lots drawn via script; triad seeds distinct in interactive mode.

### Step 3 — App Shell

**Skip** when `visual_baseline.applicability: not_applicable`.

When `required`: **From Shell onward, design style converges.** Shell Must
**embed the selected Design Spec** (tokens + type/spacing roles). Present the
choice triad in `platform_support_matrix.primary_layout_family`; after
selection, expand only the winner to every required layout family, then show
and confirm the complete product-near Baseline package. Finally extract
widgets.
**User selects** Shell options (interactive triad Preview Gate).

Actions:

1. Invoke Skills with `phase: shell`.
2. Shell Mode split:
   - **Interactive:** triad from `draw_visual_lots.py --kind shell --count 3
--record` (chrome deck); each loads selected Spec tokens—`shell_match` +
     two chrome challengers (**not** independent palette seeds). Preview Gate:
     pick / **换新批** (`--dedupe ledger`) / **在某套上改**. Fail closed
     `shell_triad_required` / `shell_seed_collision` / `shell_spec_mismatch` /
     `shell_spec_tokens_missing` / `shell_wireframe_only` /
     `visual_lot_dedupe_required`.
   - **Unattended (explicit only):** one `shell_match` embedding Spec. Link
     notice + ledger.
3. Package chosen Spec+Shell; `granoflow_project_design_baseline_import` then
   `granoflow_project_design_baseline_read` with exact `prototypeId`,
   `versionId`, `packageSha256`. Never resolve "current" or "latest". Never
   import a non-selected interactive triad candidate.
4. Confirm Baseline+Shell (interactive: after picks/confirm; unattended
   explicit only: `auto_accept_recommendation` + digest). **Never auto-accept
   Baseline+Shell in interactive mode.**
5. Lock `prototype_template`, `visual_confirmation`, `token_sources`,
   `design_spec_selection`, `shell_selection`.
6. After Baseline visual confirmation: first mandatory `widgets.yaml` extract
   (`derived_from` = that confirmed Baseline prototype).

Success criteria (when `visual_baseline.applicability: required`):

- Baseline SHA readback; every required layout-family App Shell present.
- Shell options consumed selected Spec tokens and were product-near (not
  wireframe-only).
- `widgets.yaml` + `widgets_attachment` + registry SHA
  (`widget_catalog_required` if missing).
- `design_spec_selection` and `shell_selection` recorded.

Checkpoints:

- Spec-embedded Shell only; Preview Gate honored.
- When applicability is `required`, Missing Shell fails Done.

### Done And Handoff

Initialization is Done only when all hold:

- Project Work complete, current, App-confirmed;
- `product_spec_coverage.status` is `ready`—else
  `product_spec_coverage_incomplete`;
- `init_ai_self_check.status: passed`; Engineering Acceptance Pack accepted
  (or valid unattended adopt)—else `engineering_acceptance_pack_*` /
  `init_ai_self_check_failed`;
- `directory_structure.roots` non-empty with valid modules—else
  `directory_structure_unselected`;
- `visual_baseline.applicability` resolved—else
  `visual_baseline_applicability_unresolved`;
- When `visual_baseline.applicability: required`:
  - Design Baseline current with exact SHA after mode-appropriate Spec + Shell
    rounds—else `design_spec_triad_required` / `shell_triad_required` /
    `shell_spec_mismatch` / seed-collision codes when interactive rules were
    violated;
  - init Baseline package is Spec Style Guide + App Shell only (not every key
    page as HTML); any packaged HTML page maps to key-page
    `product_spec_coverage.screen_coverage` (or Spec/Shell roles);
  - `screen_inventory` marks key pages as `not_portfolio_complete` (not tasks);
  - `screen_detail_registration` adopted with durable `ui_details` registered
    when product docs / stories state them;
  - Baseline includes every required layout-family App Shell; **Missing
    required layout fails Done**;
  - `widgets.yaml` written from confirmed Baseline—else `widget_catalog_required`;
  - `design_spec_selection` and `shell_selection` recorded;
- When `visual_baseline.applicability: not_applicable`: Spec / Shell /
  `widgets.yaml` are not required for Done;
- `skill_routing` and `stack_capability_profile` locked;
- contract-fidelity and enhanced-implementation rules recorded when UI path
  applies;
- `data_persistence` is set (`none` ⇒ explicit `no_database_declaration`);
  required data attachments registered with SHA readback;
- capability-critical third-party libraries are selected in
  `dependencies.approved` (each with `capability`, recommended package,
  alternatives considered, and rationale), or
  `no_capability_dependency_declaration` is explicit when none apply.

Emit the Project Lifecycle Progress Board
(`granoflow-agent-workflow/project-lifecycle-progress-board`) with
`project_init=done` and next action = create milestone portfolio. Interactive
mode keeps confirmation for the next gate; unattended is display-only.

Emit a short **handoff card** naming `granoflow-portfolio-orchestrator` as the
primary next owner. Component Skills: `granoflow-milestone-workflow`,
`granoflow-task-authoring`, then `granoflow-milestone-coordination` /
`granoflow-task-orchestrator`. This Skill does **not** create the full
milestone/task tree, run task Analysis/Plan Grill, or implement product code.

## Workflow

1. Resolve the project and current `project_work` attachment.
   Checkpoints:
   - Route `Initialize Granoflow` to first-run import, not this Skill.
   - One current `project_work` logical slot; no duplicate attachments.
2. Apply the Mode Gate: default `interactive` unless the user explicitly
   declared unattended. Choose entry mode (`guided_step_by_step` vs
   `guided_from_vague_request`). Vague requests default to
   `guided_from_vague_request`.
   Checkpoints:
   - Unattended never inferred from activation phrases alone.
   - Entry modes pace conversation; they are not authorization grants.
3. Run Step 1 (intake → stack → libraries → data → directory/modules →
   design routing → `visual_baseline.applicability` → AI self-check →
   Engineering Acceptance Pack browse-confirm → `granoflow_project_work_confirm`).
   Every communication states `recommended_value`, reason, and source. In
   interactive mode, **ask → recommend → wait** for decision batches; pack
   confirm is **browse accept/revise**, not a YAML read-through. In
   unattended (explicit only), adopt recommendations immediately except real
   blockers from `unattended-interaction-contract`
   (`direction_change`, `missing_user_only_input`, `forbidden_action`, etc.).
   Checkpoints:
   - No HTML baseline before stack capability lock.
   - `product_spec_coverage.status: ready` before confirm.
   - Pack accepted/adopted before App confirm; YAML AI-self-checked only.
4. When `visual_baseline.applicability: required`, check
   `granoflow_product_builder_v1`, then run Steps 2 and 3 (interactive:
   Design Spec triad with distinct random seeds, then Shell triad fitted to
   the selected Spec; unattended explicit only: one random-seed `spec_match` +
   one Spec-fitted `shell_match`, then `auto_accept_recommendation`). After
   Baseline confirm, write `widgets.yaml`. When `not_applicable`, skip Steps
   2–3 and widgets for Done.
   Checkpoints:
   - Spec/Shell lots via `draw_visual_lots.py`; Preview Gate before pick.
   - Never auto-accept Baseline+Shell in interactive mode.
5. When the user asks to create/modify a milestone or task manually, call
   `granoflow_project_work_evaluate` with that action. Missing paths return in
   one batch. Before creating a task, apply
   `granoflow-agent-workflow/task-authoring-quality-contract`.
   Checkpoints:
   - Missing evaluate paths returned in one batch, not piecemeal.
   - Task authoring quality contract before any task create.
6. Automatic create/execute/publish/deploy/complete actions require complete
   confirmed Project Work; `project_document_incomplete` returns to definition.
   Never bypass App admission.
   Checkpoints:
   - App admission gates never bypassed for automation.
   - Incomplete Project Work → `project_document_incomplete`.
7. After initialization Done, later visual work reads
   `responsive-prototype-finalization`, the confirmed platform matrix,
   baseline, `skill_routing`, and `widgets.yaml`. Task/milestone prototypes Must
   `derivedFrom` the exact baseline package SHA, **must not** re-roll random
   visual seeds, reuse catalog widgets when the same role exists, pass **Task
   Prototype Craft Gate And Option Set** (interactive: mainstream-reference-
   first candidates ≥5, brainstorm backfill only when mainstream `<5`, then
   AI-selected two or three **page expressions** with functional parity inside
   locked Design System **and confirmed sibling chrome vocabulary when
   applicable**, **side-by-side Contrast Gallery** + Baseline-fit /
   chrome-lock / candidate digests, mix-and-match per task/page, conditional
   industry third; unattended same protocol then one `expr_a`; never reopen
   Design Spec as task options; never feature-split A/B; never invent a
   parallel chrome dialect after siblings are confirmed), and accept against
   contract fidelity.
   Checkpoints:
   - Task prototypes `derivedFrom` exact baseline SHA; no task-level re-roll.
   - Hand off to portfolio orchestrator; do not create full milestone tree here.

## Rules

Hard constraints (non-exhaustive; full list in
[hard-constraints.md](references/hard-constraints.md)):

- Mode Gate + Preview Gate always apply.
- Step 1: AI self-check YAML; user browse-confirms Engineering Acceptance Pack;
  then App confirm. Spec/Shell are user selection when visual baseline required.
- Interactive Spec/Shell: mainstream-first ≥5→**promote 3**, then true-random
  lots via `draw_visual_lots.py` (Shell: Spec-fitted chrome deck only).
- From Shell onward, design style converges (`shell_spec_mismatch`).
- `widgets.yaml` after Baseline confirm when visual baseline required; task
  reuse + no task random seed.
- Task interactive: **strict Baseline fit** (locked Spec tokens + Shell chrome
  language) + **confirmed chrome lock** when chrome-family siblings are already
  `visualConfirmed` + mainstream-first candidates → dual page expressions
  (`expr_a`/`expr_b`) with functional parity + Craft Gate + **Contrast
  Gallery** (Baseline-fit + chrome-lock + candidate digests + visible-diff
  captions); mix-and-match per task/page; unattended same protocol → single
  `expr_a`; never reopen Design Spec at task level; never feature-split A/B;
  never ship generic parallel phone frames; never invent a parallel chrome
  dialect after siblings are confirmed.
- Never auto-accept Baseline+Shell in interactive mode.

## Automation Boundary

The Project Work gate answers whether the project definition is sufficient for
an action. It does not execute product code, create images outside the baseline
workflow, run a browser as acceptance, commit, push, publish, deploy, delete,
pay, message, or invent subjective approval. Those actions remain with host
tools and their own authorization gates.

## Success Criteria

- Activation phrases route here; `Initialize Granoflow` does not.
- `executionMode` defaults to interactive; unattended requires an explicit
  user declaration and is never inferred from activation phrases alone.
- Interactive runs ask each decision batch, include a recommendation, and wait
  for the user to decide before Engineering Pack accept / Baseline accept.
  Project Work YAML is AI-self-checked; users browse-confirm the Engineering
  Acceptance Pack (not a YAML dump).
- Thin product docs still require `product_spec_coverage.status: ready` before
  Done, including an operation-flow / serial-gate page-count conclusion per
  adopted journey and stress paths per acceptance. Interactive fills by
  ask→recommend→wait; unattended may auto-adopt **non-decision-changing** fills
  only and must still run the operation-flow pass — decision-changing thin-doc
  gaps fail closed `thin_product_doc_gap_requires_user`
  (`product_spec_coverage_incomplete` / nested codes otherwise).
- A partial discussion can produce a useful, hash-read-back Project Work YAML.
- Every recommendation is explicit; unattended (explicit only) adopts
  recommendations without re-asking, except real blockers.
- Stack capability is locked before Design Baseline HTML is authored (when
  visual baseline is required).
- Directory structure + modules are locked and projected into the Engineering
  Acceptance Pack before App confirm.
- When `visual_baseline.applicability: required`, automatic project
  initialization yields one App-linked Design Baseline that includes Design
  Tokens references and all required layout-family Shell variants, plus one
  confirmed `skill_routing` profile and `widgets.yaml`. When `not_applicable`,
  Spec/Shell/widgets are skipped for Done.
- Contract fidelity plus reference-viewport pixel-level high-fidelity is the
  acceptance bar; enhanced implementation notes are present where HTML is
  schematic.
- Confirmed baseline (when required) is declared the reference for later
  milestones, task prototypes, and code acceptance.
- Initialization hands off to milestone/task Skills without pretending those
  phases already ran.
- Manual milestone/task definition checks only real dependencies; automatic
  actions require complete, current, App-confirmed Project Work.
