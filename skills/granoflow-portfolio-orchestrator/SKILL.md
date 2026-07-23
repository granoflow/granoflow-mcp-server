---
name: granoflow-portfolio-orchestrator
description: After Project Definition Done, create the full milestone portfolio then quality-author every milestone's tasks via skeleton coverage and create_one loops. Hands off to milestone-coordination or task-orchestrator for Analysis and execution.
---

# Granoflow Portfolio Orchestrator

Use this Skill as the **main entry** after Project Definition when the user
wants a complete milestone set and complete child tasks for those milestones—
especially First Ship then refine—without collapsing quality into one huge
model dump.

This Skill **orchestrates** other bundled Skills. It does not replace their
contracts.

## Keyword

- `#portfolio-orchestrator`
- `#portfolio-ready`
- `#first-ship-portfolio`

## When To Use

- Project Definition is Done (or prerequisites already pass).
- The user asks to plan the project milestones and create their tasks.
- Resume an interrupted portfolio setup (`Portfolio Ready` not yet reached).

Do not use this Skill to run Analysis, implement code, or close milestones.
After **Portfolio Ready**, hand off to `granoflow-milestone-coordination`
and/or `granoflow-task-orchestrator`.

## Delegates To

| Step                              | Skill                                          |
| --------------------------------- | ---------------------------------------------- |
| Prerequisites + create milestones | `granoflow-milestone-workflow`                 |
| Skeleton + create_one tasks       | `granoflow-task-authoring`                     |
| Later charter/execute/integrate   | `granoflow-milestone-coordination`             |
| Later single-task lifecycle       | `granoflow-task-orchestrator` / agent-workflow |

## Workflow

Read `references/portfolio-orchestration-contract.md` and keep resumable state
updated after every successful step.

1. **Gate** — Same hard gate as milestone-workflow (complete Project Work;
   frontend → Design Baseline + App Shell). On failure →
   `granoflow-project-definition`.

   Checkpoints:

   - Stop and hand back to `granoflow-project-definition` when prerequisites fail.
   - Frontend projects require Design Baseline + App Shell before any milestone work.

2. **Milestones** — Invoke `granoflow-milestone-workflow` `batch_create` (or
   amend). Require App readback of all planned milestone ids.

   Checkpoints:

   - Require App readback of every planned milestone id before proceeding.
   - Amend only for real coverage gaps; do not rebuild an existing portfolio.

3. **Order** — Process milestones in sequencing order; prefer
   `role: first_ship` first when present.

   Checkpoints:

   - Prefer `role: first_ship` first when present; otherwise follow sequencing order.

4. **Per milestone tasks** —
   - for requirement-driven/software work: load `milestone-ai-review`, ensure
     schema v2 AI review passed with current digest; when UI applies, ensure
     Milestone Work `task_plan` exists and
     `status: passed` (refined screens, page journeys, split probes, task
     summaries) per `screen-task-portfolio-coverage` +
     `milestone-task-plan-template`;
   - `granoflow-task-authoring` `batch_skeleton` aligned to `task_plan.tasks`
     - acceptance / task_plan lint (`lint_task_screen_portfolio.py`);
   - then `create_one` for each pending row (description batch size **1**);
   - quality contract on every create; fail only that row;
   - write back App `task_id` onto Milestone `task_plan.tasks[]` (not Project
     Work).

   Checkpoints:

   - Requirement-driven/software: schema v2 AI review and
     `task_plan.status: passed` before any `create_one` loop.
   - Run skeleton coverage check before create (acceptance + task_plan).
   - Full description batch size is **1**; never merge multiple descriptions in one turn.
   - Quality failure fails only that row; rewrite and retry the same row.
   - Do not declare a milestone's tasks done while refined screens are
     orphaned or `task_id` writeback is missing.

5. **Portfolio Ready** — when every planned milestone exists and every
   milestone's skeleton rows are created with quality-passed descriptions.

   Checkpoints:

   - Do not declare Portfolio Ready until every planned milestone exists and every skeleton row is created with quality-passed descriptions.

6. **Handoff** — name `granoflow-milestone-coordination` (active First Ship /
   active milestone) and `granoflow-task-orchestrator` for Analysis onward.

   Checkpoints:

   - Do not start child execution inside this Skill; hand off for Analysis onward.

7. **Progress board** — end the turn with
   `granoflow-agent-workflow/project-lifecycle-progress-board` showing stage
   `milestones_created` status and next action = per-milestone Analysis.
   Interactive: confirm only the real next gate. Unattended: display-only.

   Checkpoints:

   - End every project-bound turn with the progress board; interactive confirms only the real next gate; unattended is display-only.

## Hard Rules

- Never merge multiple full task descriptions into one authoring turn.
- Never skip coverage check before create loops.
- Never weaken `task-authoring-quality-contract`.
- Do not start child execution inside this Skill.
- Resume from recorded `milestones_created` / `tasks_created N/M` /
  `current_milestone_id` instead of restarting from scratch.

## Success Criteria

- `planned_milestones == created_milestones` (after amend rules).
- Each milestone has acceptance coverage via created tasks (or explicit
  controller-owned acceptances).
- Every created task passed authoring quality.
- State is **Portfolio Ready**, not "assistant summarized a plan".

## References

- Read `references/portfolio-orchestration-contract.md` before orchestration and after every successful step to keep resumable state updated.
