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

## Keyword

- `#initialize-this-project`
- `#project-definition`
- `#design-baseline`

## When to use

- User asks to initialize or define **this** software project (not Granoflow
  itself).
- Need Project Work + Design Baseline (tokens + landscape/portrait App Shell)
  locked under contract fidelity before milestone/task automation.

## Authority Of Initialization Outputs

The confirmed Project Work YAML plus the App-linked Design Baseline (including
Design Tokens and landscape/portrait App Shell) are the authoritative visual
and information-architecture reference for every later milestone, task-level
prototype, and code acceptance.

Later work must not invent a parallel visual authority. Changing navigation IA,
Shell mode, or locked tokens requires a new Design Baseline version and a fresh
visual confirmation. Subsequent prototypes Must declare `derivedFrom` the exact
baseline `prototypeId` / `versionId` / `packageSha256` (document-level gate in
this release).

**Acceptance bar is contract fidelity (契约级一致), not pixel parity:**

- **Must:** primary navigation IA; landscape/portrait Shell modes and stated
  breakpoints; locked Design Tokens; main-journey layout regions; no new global
  primary entry absent from the baseline; locked widgets when catalog exists.
- **Should:** secondary visual closeness.
- **Won't:** pixel-perfect screenshots; spring-feel video match; native control
  chrome.

**Enhanced implementation:** when the target stack can look better with mature
third-party widgets, HTML may convey intent only, but each such case must carry
an `【增强实现】` / `implementation_notes` note naming the intended component and
the Must invariants that remain unchanged.

## Required References

1. Read `granoflow-agent-workflow/project-work-document-template` for the
   canonical YAML shape.
2. Read `granoflow-agent-workflow/requirement-intake-and-traceability` before
   extracting mixed-format product sources.
3. Read [project-definition-interaction.md](references/project-definition-interaction.md)
   before interviewing or recommending values (Mode Gate, batches).
4. Read [project-artifact-workflows.md](references/project-artifact-workflows.md)
   for Design Spec/Shell, Preview Gate, widgets, and task Craft Gate / option
   sets.
5. Read [hard-constraints.md](references/hard-constraints.md) before Done or
   any `visualConfirmed=true` to verify thread-confirmed fail-closed rules.
6. Apply Mode Gate: default `executionMode: interactive` unless the user
   **explicitly** declares unattended. Read
   `granoflow-agent-workflow/unattended-interaction-contract` only when
   unattended.
7. Call `granoflow_agent_preferences_get(projectId)` when preferences exist;
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
design routing → Project Work confirm. Detail:
[project-definition-interaction.md](references/project-definition-interaction.md).

Actions:

1. Resolve one project; emit Mode Gate notice.
2. Requirement intake + **Product Spec Completeness Hard Gate**
   (`product_spec_coverage`; no confirm while status is not `ready`).
3. Fill Project Work from the canonical template; preserve unknowns; no fake
   completeness. Initialization blockers must not stay `deferred_unknown`.
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
7. Recommend one `design_profile` + `skill_routing` (never a Skills menu).
8. Use `grill-me` for remaining decision-changing gaps (interactive wait;
   unattended explicit-only auto-adopt).
9. `granoflow_project_work_confirm` only after App content/hash readback **and**
   interactive user confirm (or unattended Mode Gate adopt). Confirmation does
   not authorize execute/commit/push/publish/deploy.

Success criteria:

- `product_spec_coverage.status` is `ready`.
- `stack_capability_profile` locked; capability libraries or explicit none.
- Project Work App-confirmed with hash readback.

Checkpoints:

- Interactive batches wait; unattended never inferred.
- No HTML baseline before stack capability lock.

### Step 2 — Design Baseline + Design Tokens

Design Spec round first (Mode split in
[project-artifact-workflows.md](references/project-artifact-workflows.md)), then
tokens for the chosen Spec.

Actions:

1. Require `granoflow_product_builder_v1` ready or return
   `capability_pack_not_ready` (manual Project Work still allowed).
2. Require `product_spec_coverage.status: ready`.
3. Invoke `skill_routing` Skills with `phase: baseline` (include `impeccable`
   when available for **random seeds**).
4. Design Spec Mode split:
   - **Interactive:** triad—**three different random seeds**—`spec_match` + two
     `ai_challenger_*`. Option-set Preview Gate; wait. Fail closed
     `design_spec_triad_required` / `design_spec_seed_collision`.
   - **Unattended (explicit only):** one `spec_match` + **random seed**. Link
     notice + ledger.
5. Emit Design Tokens → `token_sources`; record `【增强实现】` /
   `implementation_notes` where schematic; record `design_spec_selection`.

Success criteria:

- `design_spec_selection` recorded (option id if any, seed, provenance).
- `token_sources` set for the chosen Spec.

Checkpoints:

- Preview Gate links shown before pick/confirm.
- Spec triad seeds are distinct in interactive mode.

### Step 3 — App Shell

**From Shell onward, design style converges.** Shell Must perfectly fit the
selected Spec. Then merge, import, confirm Baseline, extract widgets.

Actions:

1. Invoke Skills with `phase: shell`.
2. Shell Mode split:
   - **Interactive:** triad fitted to selected Spec—`shell_match` + two
     chrome/structure challengers (distinct chrome-variant ids; **not**
     independent palette seeds). Fail closed `shell_triad_required` /
     `shell_seed_collision` / `shell_spec_mismatch`.
   - **Unattended (explicit only):** one `shell_match` fitted to Spec. Link
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

Success criteria:

- Baseline SHA readback; landscape and portrait App Shell present.
- `widgets.yaml` + `widgets_attachment` + registry SHA
  (`widget_catalog_required` if missing).
- `design_spec_selection` and `shell_selection` recorded.

Checkpoints:

- Spec-fitted Shell only; Preview Gate honored.
- Missing Shell fails Done.

### Done And Handoff

Initialization is Done only when all hold:

- Project Work complete, current, App-confirmed;
- `product_spec_coverage.status` is `ready`—else
  `product_spec_coverage_incomplete`;
- Design Baseline current with exact SHA after mode-appropriate Spec + Shell
  rounds—else `design_spec_triad_required` / `shell_triad_required` /
  `shell_spec_mismatch` / seed-collision codes when interactive rules were
  violated;
- every Baseline journey/critical screen maps to
  `product_spec_coverage.screen_coverage`;
- Baseline includes landscape and portrait App Shell; **Missing Shell fails
  Done**;
- `widgets.yaml` written from confirmed Baseline—else `widget_catalog_required`;
- `design_spec_selection` and `shell_selection` recorded;
- `skill_routing` and `stack_capability_profile` locked;
- contract-fidelity and enhanced-implementation rules recorded;
- `data_persistence` is set (`none` ⇒ explicit `no_database_declaration`);
  required data attachments registered with SHA readback;
- capability-critical third-party libraries are selected in
  `dependencies.approved` (each with `capability`, recommended package,
  alternatives considered, and rationale), or
  `no_capability_dependency_declaration` is explicit when none apply.

Emit a short **handoff card** naming `granoflow-portfolio-orchestrator` as the
primary next owner. Component Skills: `granoflow-milestone-workflow`,
`granoflow-task-authoring`, then `granoflow-milestone-coordination` /
`granoflow-task-orchestrator`. This Skill does **not** create the full
milestone/task tree, run task Analysis/Plan Grill, or implement product code.

## Workflow

1. Resolve the project and current `project_work` attachment.
2. Apply the Mode Gate: default `interactive` unless the user explicitly
   declared unattended. Choose entry mode (`guided_step_by_step` vs
   `guided_from_vague_request`). Vague requests default to
   `guided_from_vague_request`.
3. Run Step 1 (intake → stack capability → capability-critical libraries →
   data persistence → design routing → Project Work confirm). Every
   communication states `recommended_value`, reason, and source. In
   interactive mode, **ask → recommend → wait** for the user to decide before
   locking or confirming. In unattended (explicit only), adopt recommendations immediately
   except real blockers from `unattended-interaction-contract`
   (`direction_change`, `missing_user_only_input`, `forbidden_action`, etc.).
4. Check `granoflow_product_builder_v1`, then run Steps 2 and 3 (interactive:
   Design Spec triad with distinct random seeds, then Shell triad fitted to
   the selected Spec; unattended explicit only: one random-seed `spec_match` +
   one Spec-fitted `shell_match`, then `auto_accept_recommendation`). After
   Baseline confirm, write `widgets.yaml`.
5. When the user asks to create/modify a milestone or task manually, call
   `granoflow_project_work_evaluate` with that action. Missing paths return in
   one batch. Before creating a task, apply
   `granoflow-agent-workflow/task-authoring-quality-contract`.
6. Automatic create/execute/publish/deploy/complete actions require complete
   confirmed Project Work; `project_document_incomplete` returns to definition.
   Never bypass App admission.
7. After initialization Done, later visual work reads the confirmed baseline,
   `skill_routing`, and `widgets.yaml`. Task/milestone prototypes Must
   `derivedFrom` the exact baseline package SHA, **must not** re-roll random
   visual seeds, reuse catalog widgets when the same role exists, pass **Task
   Prototype Craft Gate And Option Set** (interactive 2–3 options; unattended
   one `delta_match`), and accept against contract fidelity.

## Rules

Hard constraints (non-exhaustive; full list in
[hard-constraints.md](references/hard-constraints.md)):

- Mode Gate + Preview Gate always apply.
- Interactive Spec: three different random seeds; Shell: Spec-fitted only.
- From Shell onward, design style converges (`shell_spec_mismatch`).
- `widgets.yaml` after Baseline confirm; task reuse + no task random seed.
- Task interactive: dual (+ conditional industry third) + Craft Gate; unattended
  single `delta_match`.
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
  for the user to decide before confirm / Baseline accept.
- Thin product docs still require `product_spec_coverage.status: ready` before
  Done; interactive fills by ask→recommend→wait; unattended fills by
  recommend+adopt with honest provenance (`product_spec_coverage_incomplete`
  otherwise).
- A partial discussion can produce a useful, hash-read-back Project Work YAML.
- Every recommendation is explicit; unattended (explicit only) adopts
  recommendations without re-asking, except real blockers.
- Stack capability is locked before Design Baseline HTML is authored.
- Every automatic project initialization yields one App-linked Design Baseline
  that includes Design Tokens references, landscape App Shell, and portrait
  App Shell, plus one confirmed `skill_routing` profile and `widgets.yaml`.
- Contract fidelity (not pixel 1:1) is the stated acceptance bar; enhanced
  implementation notes are present where HTML is schematic.
- Confirmed baseline is declared the reference for later milestones, task
  prototypes, and code acceptance.
- Initialization hands off to milestone/task Skills without pretending those
  phases already ran.
- Manual milestone/task definition checks only real dependencies; automatic
  actions require complete, current, App-confirmed Project Work.
