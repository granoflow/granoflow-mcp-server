---
name: granoflow-milestone-workflow
description: After Project Work (and frontend Design Baseline plus App Shell) are ready, plan and create Granoflow milestones singly or in batch. Stops when milestone entities exist; does not charter, author tasks, or execute. Prefer granoflow-portfolio-orchestrator for full portfolio-plus-tasks setup.
---

# Granoflow Milestone Workflow

Use this Skill to **plan and create** project milestones after Project Definition
prerequisites pass. It supports **single create** and **batch create**. It does
**not** draft Milestone Work charters, create child tasks, run Analysis, or
close milestones.

For creating high-quality child tasks, use `granoflow-task-authoring`.  
For create-all-milestones then create-all-tasks, use
`granoflow-portfolio-orchestrator`.  
For charter → coordinate → integrate → close, use
`granoflow-milestone-coordination`.

## When To Use

- Create one milestone, or create the full planned milestone set.
- Amend the portfolio when Project Work coverage has a real gap.
- Called by `granoflow-portfolio-orchestrator` as the milestone-creation step.

Do not use this Skill to invent milestones when Project Work / frontend baseline
gates fail. Do not use it to author task titles/descriptions or execute work.

## Entry Prerequisites (Hard Gate)

Before any milestone planning or entity creation, verify all of the following.
On failure, stop, return `project_milestone_prerequisites_incomplete`, and hand
back to `granoflow-project-definition`. Do not create App milestones.

1. **Project Work** is complete, current, and App-confirmed.
2. If the project **includes frontend**, the confirmed Design Baseline must
   exist with exact `prototypeId` / `versionId` / `packageSha256` readback,
   landscape and portrait **App Shell**, and successful `visual_confirmation`.

### Frontend Detection

Treat the project as including frontend when any of these hold:

- `product` / `platforms` / supported surfaces indicate app, web, desktop, or
  other user-facing UI;
- Project Work already has a non-empty `design_profile` or
  `prototype_template` reference;
- the user explicitly states the project has frontend/UI.

Backend-only / CLI-only / library-only projects without UI skip the Design
Baseline + App Shell requirement but still require complete Project Work.

## Modes

### `single_create`

Create exactly one milestone entity (preview → confirm → write → readback) when
the user names one outcome or when amending a coverage gap with one addition.

### `batch_create`

Plan and create the milestone portfolio:

1. Read live App milestones and Project Work `milestone_strategy`,
   `acceptance_coverage`, and `requirement_coverage`.
2. **Empty portfolio:** plan the **entire** ordered milestone set in one pass;
   persist into Project Work; create **all** planned milestone entities; mark
   First Ship when applicable (see
   `references/milestone-portfolio-creation.md`).
3. **Existing portfolio:** do **not** rebuild; amend only for real coverage or
   sequencing gaps.
4. Respect `active_milestone_limit` (default `1`): create inactive later
   milestones; activate the first sequenced (prefer First Ship).

## Workflow

1. Pass the hard gate.
2. Call `granoflow_agent_preferences_get(projectId)` once when project-bound.
   Preferences never weaken readiness, quality, authorization, or acceptance
   gates.
3. Choose `single_create` or `batch_create`.
4. Read `references/milestone-portfolio-creation.md`.
5. Preview creations; on confirm, write through App/API and read back every
   created milestone id.
6. Emit Done: milestone ids created/amended, sequencing, First Ship id if any,
   and handoff to `granoflow-task-authoring` or
   `granoflow-portfolio-orchestrator` (if tasks are still missing).

## Hard Rules

- Fail closed at entry when prerequisites are incomplete.
- Empty project → plan and create the full milestone set; existing → amend only.
- Never create child tasks or Milestone Work charters in this Skill.
- Never resolve "current" or "latest" for Design Baseline packages.
- Preserve preview, confirmation, write, and App/API readback.

## References

- Read [milestone-portfolio-creation.md](references/milestone-portfolio-creation.md)
  before planning or creating milestones.

## Success Criteria

- Prerequisites enforced; frontend projects require Baseline + App Shell.
- Single and batch create both end with App readback of milestone ids.
- This Skill stops at milestone entities; task authoring and coordination are
  other Skills.
