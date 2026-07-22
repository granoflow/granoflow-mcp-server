# Project Lifecycle Progress Board

Mandatory end-of-turn progress + next-step reporting for **project-bound**
Granoflow software work. Prevents agents from finishing a reply without telling
the user what stage the project is in and what to do next.

## Mandatory Load

Before authoring any user-visible progress summary for a project-bound turn,
load this reference via MCP:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "project-lifecycle-progress-board"
)
```

Skipping the load and claiming project progress fails closed as
`project_lifecycle_board_unread`.

Also load `unattended-interaction-contract.md` when
`interaction_mode: unattended`.

## Pipeline Stages (hard order)

Hosts **Must** treat the following stages as the canonical project path.
Do not invent parallel “shortcut” completions that skip earlier stages.

| #   | Stage id               | Meaning                                                                                                                                                                                                                                                                                                                                  | Primary owners                                                                                 |
| --- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | `project_init`         | Project Definition Done (Project Work + Design Baseline when required)                                                                                                                                                                                                                                                                   | `granoflow-project-definition`                                                                 |
| 2   | `milestones_created`   | Planned milestones exist; portfolio tasks authored                                                                                                                                                                                                                                                                                       | `granoflow-portfolio-orchestrator`, `granoflow-milestone-workflow`, `granoflow-task-authoring` |
| 3   | `milestone_analysis`   | **Per active milestone**: every in-scope child has confirmed Analysis                                                                                                                                                                                                                                                                    | `granoflow-task-orchestrator` + agent-workflow Analysis                                        |
| 4   | `milestone_plan`       | **Per active milestone**: every in-scope child has Plan Design Gate / execution-ready Plan **and** one milestone Plan acceptance pack shown (interactive: user-accepted)                                                                                                                                                                 | Plan Design Gate + `milestone-plan-acceptance-pack` + Readiness                                |
| 5   | `milestone_implement`  | Code + unit tests + **authored** integration tests (task-local: do not run IT here), aligned to the accepted `milestone-plan-acceptance-pack`                                                                                                                                                                                            | task-orchestrator `run` / agent-workflow execution + acceptance pack                           |
| 6   | `integration_campaign` | App compiles; **orchestrate** standard IT into a minimal **service_path** suite (cross-module real I/O; UI clicks not required); Acceptance Outcomes close `domain_io` only (platform/UI/session deferred); AI **auto-drives** until green; **plain-language Closing Summary**; change report if edits. Next stage is E2E, not closeout. | `granoflow-integration-test-campaign` + local build                                            |
| 7   | `e2e_campaign`         | After IT green: from Project Work (+ Design Baseline / user stories) build coverage matrix + Acceptance Outcomes for user-required real results; **author** missing UI journeys; host probes (window / secure storage); auto-fix bugs; screenshots under `temp/` shown to user; Closing Summary as final test deliverable                | `granoflow-e2e-test-campaign` + host capture                                                   |
| 8   | `project_complete`     | Required milestones accepted; residuals closed or explicitly deferred                                                                                                                                                                                                                                                                    | milestone-coordination accept + project closeout                                               |

Rules:

1. Stages advance **milestone-by-milestone** for 3–5 (First Ship before refine
   when Project Work sequencing says so).
2. Stage 6 is **not** implied by every child `done`. Require compile +
   **orchestrated** integration suite evidence (or an explicit campaign
   residual). Inside stage 6, `campaign_drive: agent_auto` applies for both
   `interactive` and `unattended`—do not pause for ordinary “run next / fix
   this?” confirms; the board stays display-only for the IT loop.
3. Stage 7 requires stage 6 complete (or green_with_external_residuals). Inside
   stage 7, same agent_auto / display-only board rules. Claiming
   `project_complete` while skipping E2E without an explicit E2E residual fails
   closed as `project_lifecycle_stage_skip`.
4. Ordinary feature tasks still obey task-local IT policy (add ≤2
   **service_path** integration tests, do not run them inside the feature task;
   recommend `requires`/`produces` metadata). Running integration belongs to
   stage 6; running E2E belongs to stage 7.

## Interaction Modes

| Mode          | Same pipeline? | Progress board                                  | Stage / phase confirmations                                                                                                                                   |
| ------------- | -------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interactive` | Yes            | **Required** at end of every project-bound turn | Existing confirm gates remain (`[confirm]`, Plan Gate, visual pick, etc.)                                                                                     |
| `unattended`  | Yes            | **Required** as **display-only notice**         | Do **not** ask the user to confirm the board or ordinary phase questions; follow `unattended-interaction-contract` (defer external blockers; residual report) |

Unattended **never** skips stages. It only skips **asking**. The board is still
emitted so the user can see progress and gaps.

Fail closed:

- `project_lifecycle_board_missing` — project-bound turn ended without a board
- `project_lifecycle_board_confirm_in_unattended` — unattended turn asked the
  user to confirm the board or next stage merely because the board was shown
- `project_lifecycle_stage_skip` — claimed a later stage without earlier stage
  evidence

## When The Board Is Required

Required when **any** of:

- Active work is bound to a `projectId` with Project Work / portfolio / milestone
  coordination / task Analysis|Plan|run on that project
- User asks for status, “下一步”, remaining work, or project/milestone progress
- A phase stops at a gate (Analysis confirm, Plan Gate, visual pick, execution
  auth, IT campaign)

**Not** required for: pure inbox capture with no project binding; daily mood
notes; unrelated MCP setup troubleshooting with no project work.

## Board Artifact

Persist a machine-readable snapshot (repo `temp/` or Milestone/Project Work
appendix) and render Markdown for the user.

```yaml
project_lifecycle_board:
  schema_version: 1
  project_id: <uuid>
  project_title: <string>
  interaction_mode: interactive | unattended
  board_confirmation: required | display_only
  updated_at: <ISO-8601>
  contract_loaded: true
  stages:
    - id: project_init
      status: not_started | in_progress | done | blocked
      evidence: <short>
    - id: milestones_created
      status: ...
      evidence: ...
    # ... all eight stages ...
  milestones:
    - milestone_id: <uuid>
      key: M1
      title: <string>
      analysis: not_started | in_progress | done | blocked
      plan: not_started | in_progress | done | blocked
      implement: not_started | in_progress | done | blocked
      note: <optional>
  next_action:
    stage_id: <stage id>
    summary: <one imperative sentence>
    owner_skill: <skill id>
    needs_user_confirmation: true | false
  blockers: [] # {id, summary, blocker_class}
  loaded_reference_sha256: <sha from granoflow_bundled_skill_reference>
```

`board_confirmation`:

- `interactive` → `required` (showing the board does not replace phase confirms;
  `needs_user_confirmation` reflects the **next gate**, not the board itself)
- `unattended` → `display_only` and `needs_user_confirmation: false` on the
  board’s next_action row (external blockers go to Residual Report)

## Render Script

Prefer:

```text
python3 skills/granoflow-agent-workflow/scripts/render_project_lifecycle_board.py PATH.yaml
```

Require stdout JSON with `ok: true` and non-empty `markdown`. Lint/render
failure keeps the turn incomplete (`project_lifecycle_board_render_failed`).

## End-Of-Turn User Surface (hard)

Every project-bound assistant turn **Must** end with the rendered board
Markdown (or an equivalent table that includes all eight stages, per-milestone
A/P/I rows, **下一步**, and blockers).

Recommended heading:

```markdown
## 项目进度板

...

## 下一步

...
```

Interactive: after the board, ask only for the **actual next gate** (if any),
not “请确认进度板”.

Unattended: emit the board as a notice; continue solvable work; do not wait on
board acknowledgement.

## Recommended Next-Action Rules

Compute `next_action` from the **first** incomplete stage in order:

1. `project_init` incomplete → continue Project Definition
2. milestones missing → portfolio / milestone-workflow
3. current milestone Analysis incomplete → analyze batch / remaining tasks
4. Analysis done, Plan incomplete → Plan Design Gate / plan batch; when Gate
   drafts are ready, emit `milestone-plan-acceptance-pack` for acceptance
5. Plan ready (pack accepted / unattended grant), implement incomplete → run /
   execute remaining tasks **using the accepted pack as the primary milestone
   alignment reference** (see `milestone-plan-acceptance-pack.md`); for long
   or unattended implement also keep an active durable run plan per
   `long-task-run-continuity.md` (optional collaborative planning surface when
   the host exposes one—never require a vendor mode name)
6. implement done for required milestones, suite not green → integration
   campaign (orchestrate → auto-drive → triage/fix/re-test → change report)
7. else → project complete / accept residuals

Within stages 3–5, prefer the **earliest sequenced** milestone that is not done.

## Relationship To Other Contracts

- Does **not** weaken Task Work, Grill, prototype, Plan Design Gate,
  milestone Plan acceptance pack, Delivery, Git checkpoint, or external-action
  gates.
- Unattended board display coexists with Unattended Residual Report at run end.
- Portfolio Ready is stage `milestones_created`, not project complete.
- Child task `done` alone does not set `integration_campaign`,
  `e2e_campaign`, or `project_complete` to `done`.

## Fail-Closed Codes

| Code                                            | When                                         |
| ----------------------------------------------- | -------------------------------------------- |
| `project_lifecycle_board_unread`                | Reference not loaded via MCP                 |
| `project_lifecycle_board_missing`               | Project-bound turn without board             |
| `project_lifecycle_board_render_failed`         | Script/render not ok                         |
| `project_lifecycle_board_confirm_in_unattended` | Unattended asked user to confirm the board   |
| `project_lifecycle_stage_skip`                  | Later stage claimed without earlier evidence |
| `project_lifecycle_board_incomplete_stages`     | Board omits one of the eight stage ids       |

## Admission Test

1. Did we load this reference via MCP?
2. Are all eight stage ids present with status + evidence?
3. Is `next_action.summary` a single concrete imperative in **plain language**
   (per `workflow-jargon-plain-language.md`)? Do not leave bare
   `execution_authorization` / `run` without a gloss and a suggested user
   phrase (e.g. 「可以说『开始实施』」).
4. If unattended: is the board display-only with no confirm prompt?
5. Does the next stage match the first incomplete pipeline step?
