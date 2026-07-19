---
name: granoflow-project-definition
description: Define or refine a Granoflow software project, automatically propose and lock one coherent design system plus high-fidelity prototype baseline, persist one partial-to-confirmed Project Work YAML, and gate automation on App-owned completeness and readback.
---

# Granoflow Project Definition

Use this Skill when a user wants to start, define, refine, automate, or continue
a software project in Granoflow. It supports both technical users who want to
edit one field at a time and users who provide only a vague outcome.

Granoflow App owns Project Work content, logical attachment identity,
confirmation, readiness, hashes, and action admission. MCP is a thin protocol
surface. The host Agent owns the conversation, recommendations, HTML authoring,
packaging, and execution tools.

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
4. Read `references/project-artifact-workflows.md` when UI prototypes, data
   models, workflows, or cross-artifact consistency are discussed.
5. Call `granoflow_agent_preferences_get(projectId)` when preferences already
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

## Fixed Initialization Outcome

Project initialization is opinionated. Do not ask the user to select Skills,
fonts, colors, layout systems, or prototype engines one item at a time.

1. Require host evidence that `granoflow_product_builder_v1` is ready. If it is
   declined, missing, or partially available, return `capability_pack_not_ready`
   for automatic project initialization. Manual Project Work editing remains
   available.
2. Inspect the repository, product type, target users/platforms, existing
   `DESIGN.md`, theme tokens, shared components, and real UI evidence.
3. Produce one coherent design proposal covering aesthetic, decoration,
   layout, color, typography, spacing, shape/elevation, and motion. Include
   category-safe choices and at least two deliberate product-specific risks.
4. Generate one realistic high-fidelity HTML baseline from real product
   journeys and critical states. Do not use lorem ipsum, generic three-card AI
   layouts, or a marketing landing page when the product is an application.
5. Import it with `granoflow_project_design_baseline_import`, then read the exact
   prototype/version/package SHA with `granoflow_project_design_baseline_read`.
6. Show the complete proposal and exact baseline preview as one visual decision.
   The user may confirm it or request changes, but does not choose the router or
   individual Skills.
7. On confirmation, lock `design_profile`, `skill_routing`,
   `prototype_template`, and `visual_confirmation` in Project Work. Confirm the
   exact current Project Work SHA only after App readback.

## Workflow

1. Resolve exactly one Granoflow project or ask the user to choose. Read its
   current project description, active milestone context, and current
   `project_work` logical attachment.
2. If no Project Work exists, start from the canonical YAML template. Preserve
   unknowns as null/empty plus provenance; never invent values to make the
   document look complete.
   Register and read every supplied source before mapping it. Preserve
   unexpected requirements, label inference, and report product-document/user-
   story omissions or conflicts instead of choosing silently.
3. Choose the entry mode from the user's request. A vague request defaults to
   `guided_from_vague_request`; an explicit section/field request defaults to
   `guided_step_by_step`.
4. Present one recommendation batch. Every recommended value includes reason,
   source, alternatives, and whether custom input is allowed. Let the user
   accept one, accept all eligible low-risk recommendations, or customize.
5. Update the full YAML locally, replace the current `project_work` slot with
   optimistic revision and expected SHA-256, then read App-owned content/hash
   back. Report partial coverage honestly.
6. When the user asks to create/modify a milestone or task manually, call
   `granoflow_project_work_evaluate` with that action and the exact dependent
   paths. If any are missing, stop that action and ask for the returned batch.
   Before creating a task, also apply
   `granoflow-agent-workflow/task-authoring-quality-contract`.
7. When the user asks for automatic creation, execution, continuation,
   publishing, deployment, task/project completion, or end-to-end project work,
   call the matching Project Work action. `project_document_incomplete` always
   returns to definition; never bypass it or reimplement the gate in the host.
   Project admission never weakens the shared title, plain-language, analogy,
   example, or change-evidence requirements for tasks created afterward.
8. When all fields are complete, show a concise final decision summary. Only an
   explicit confirmation may call `granoflow_project_work_confirm` against the
   exact current SHA. Project Work confirmation does not authorize execution or
   any separately gated external action.
9. After confirmation, rerun the requested action evaluation. Continue only
   when the App returns `admission=allowed` and all ordinary Task Work,
   readiness, authorization, and repository rules also pass.
10. Later visual work reads the confirmed design and routing lock. Invoke a
    relevant available `model_allowed` Skill without asking again, and record
    its output/evidence in Task Work. `user_only`, unknown, installation,
    network/cost, data egress, publish, deploy, and destructive actions keep
    their ordinary gates.

## Automation Boundary

The Project Work gate answers whether the project definition is sufficient for
an action. It does not execute code, create images, run a browser, commit, push,
publish, deploy, delete, pay, message, or infer subjective approval. Those
actions remain with host tools and their own authorization gates.

## Success Criteria

- A partial discussion can produce a useful, hash-read-back Project Work YAML.
- Manual milestone/task definition checks only its real dependencies.
- Every automatic action requires complete, current, App-confirmed Project
  Work and returns all relevant missing paths at once.
- Step-by-step and vague-request modes converge on the same schema and source
  discipline.
- Project artifacts use one current logical slot each and are read back after
  every replacement.
- Every automatically initialized project has one App-linked, immutable-version
  design baseline and one confirmed project-level routing profile.
