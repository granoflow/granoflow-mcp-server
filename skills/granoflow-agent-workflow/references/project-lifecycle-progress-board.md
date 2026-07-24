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

Also load `pipeline-attachment-and-reentry` on project-bound turns to classify
`entry_kind` and apply stage rewind after confirmed midstream changes.

## Pipeline Stages (hard order)

Hosts **Must** treat the following stages as the canonical project path.
Do not invent parallel “shortcut” completions that skip earlier stages.

| #   | Stage id               | Meaning                                                                                                                                                                           | Primary owners                                                                                 |
| --- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | `project_init`         | Project Definition Done (Project Work + Engineering pack; Design Baseline when `visual_baseline` required)                                                                        | `granoflow-project-definition`                                                                 |
| 2   | `milestones_created`   | Planned milestones exist; portfolio tasks authored                                                                                                                                | `granoflow-portfolio-orchestrator`, `granoflow-milestone-workflow`, `granoflow-task-authoring` |
| 3   | `milestone_analysis`   | **Per active milestone**: every in-scope child has confirmed Analysis                                                                                                             | `granoflow-task-orchestrator` + agent-workflow Analysis                                        |
| 4   | `milestone_plan`       | **Per active milestone**: every in-scope child has Plan Design Gate / execution-ready Plan **and** one milestone Plan acceptance pack shown (interactive: user-accepted)          | Plan Design Gate + `milestone-plan-acceptance-pack` + Readiness                                |
| 5   | `milestone_implement`  | **IT preflight** then **Layer A** per child; per-milestone **Layer B** = milestone-scoped IT suite (user-invisible) + Experience + 任务回顾 (`milestone-integration-acceptance`). | task-orchestrator + `milestone-integration-acceptance`                                         |
| 6   | `integration_campaign` | **最终交付 · 项目级 IT**（多里程碑路径：全量单测后编排全部不可见 IT）。单功能里程碑项目可 **waive** 本阶段，直进全面 E2E。不替代 Layer B。见 `full-delivery-acceptance`。         | `full-delivery-acceptance` + `granoflow-integration-test-campaign`                             |
| 7   | `e2e_campaign`         | **最终交付 · 全面 E2E**（始终全项目覆盖，防改一处坏别处）：覆盖矩阵、可见窗、截图、Closing Summary。                                                                              | `full-delivery-acceptance` + `granoflow-e2e-test-campaign`                                     |
| 8   | `project_complete`     | Required milestones accepted; **最终交付** green (or explicit residual); residuals closed or deferred                                                                             | milestone-coordination accept + project closeout                                               |

Rules:

1. Stages 3–5 follow Project Work `pipeline_order` (see **Pipeline Order Gate**
   below). Until the user chooses, do **not** assume milestone-by-milestone Plan
   entry when peer milestones have not started Analysis.
2. Stages 6–7 are **最终交付测试** (`full-delivery-acceptance`). Milestone
   delivery stops at Layer B (no E2E). Final delivery **May** start after any
   Layer B green (including a single milestone finished today). Path:
   - project has **1** feature milestone → waive stage 6 / skip portfolio unit+IT
     → **full-project** E2E
   - project has **≥2** → full unit → stage 6 IT → **full-project** E2E
     Inside campaigns, `campaign_drive: agent_auto`; board display-only.
3. Stage 7 requires stage 6 `done` **or** valid single-milestone waiver
   (`pre_e2e_path: e2e_direct` / `integration_gate: waived_single_milestone`).
   Claiming `project_complete` while skipping最终交付 without residual fails
   closed as `project_lifecycle_stage_skip`.
4. Ordinary feature tasks still obey task-local IT policy. Per-milestone IT =
   Layer B in stage 5; project-wide IT/E2E only in最终交付 (with the 1-milestone
   waiver above).

## Pipeline Order Gate

Persist on Project Work (and mirror on the board snapshot):

```yaml
pipeline_order:
  mode: unset | breadth_first | depth_first
  decided_at: null # ISO-8601 when set
  decided_by: null # user | unattended_grant
```

| `mode`          | Meaning                                                                                                  |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| `breadth_first` | Finish Analysis (including prototypes) for **all** feature milestones, then Plan batches, then Implement |
| `depth_first`   | For one milestone: Analysis → Plan → Implement (incl. Layer B), then start the next milestone's Analysis |
| `unset`         | Not yet chosen; Plan entry may be blocked by the ask gate below                                          |

### Ask gate (interactive)

Before starting Plan for any feature milestone (Plan Design Gate drafts, Plan
batch, or claiming `milestone_plan` in progress), if **all** of:

1. Project has **≥2** feature milestones;
2. `pipeline_order.mode` is `unset` (or missing);
3. At least one **other** feature milestone still has Analysis `not_started`
   (no child Analysis started);

then **stop**. Do not enter Plan. Ask the user in plain language exactly:

> 多里程碑时，先全部分析，还是做一个完整闭环再做下一个？

Map answers:

- 先全部分析 → write `pipeline_order.mode: breadth_first`, `decided_by: user`
- 做一个完整闭环再做下一个 → write `pipeline_order.mode: depth_first`,
  `decided_by: user`

Then continue per the chosen mode. Skipping the ask and entering Plan fails
closed as `pipeline_order_unresolved`.

Skip the ask when: only one feature milestone; or every other feature milestone
already has Analysis `in_progress` / `done`; or `mode` is already set.

### Unattended

Do **not** chat-ask mid-run. `pipeline_order.mode` Must already be
`breadth_first` or `depth_first` in Project Work or the unattended grant
(`decided_by: unattended_grant`). Missing choice → fail closed
`pipeline_order_unresolved`, list it in the Residual Report, and refuse Plan
entry. Never silently default to `depth_first`.

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
  pipeline_order: # mirror Project Work; optional on legacy boards
    mode: unset | breadth_first | depth_first
    decided_at: null
    decided_by: null # user | unattended_grant
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
  session_delivery: # see full-delivery-acceptance
    schema: granoflow_session_delivery_v1
    milestones_touched_count: <int>
    milestones_touched: [<key-or-id>]
    project_feature_milestone_count: <int>
    pre_e2e_path: e2e_direct | full_unit_and_it | not_selected
    status: offer_or_ask | in_progress | complete | not_applicable
    prompt_full_delivery: true | false
    other_milestones: []
    recommendation: <plain language>
  entry_kind: new_project | new_milestones | scattered_task | pipeline_continue | midstream_change # optional; recommended
  reentry: # optional; when entry_kind is midstream_change or after rewind
    from_stage: <stage id>
    reason: <plain language>
    change_class: task_local | portfolio_change | charter_change | follow_up
    writeback_status: written_and_read_back | pending | not_applicable
  next_action:
    stage_id: <stage id>
    summary: <one imperative sentence>
    owner_skill: <skill id>
    needs_user_confirmation: true | false
  blockers: [] # {id, summary, blocker_class}
  loaded_reference_sha256: <sha from granoflow_bundled_skill_reference>
```

Optional `entry_kind` / `reentry` are tolerated by the render script. When
`reentry` is present, render a short 「回轨」 section. After confirmed early
requirement changes, recompute stages per `pipeline-attachment-and-reentry`
before setting `next_action` (do not leave later stages falsely `done`).

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

If this turn is `midstream_change` (or rewind just applied), set `next_action`
from the **rewound** first incomplete stage and say in plain language that the
confirmed change was written back and work returns to Analysis/Plan/etc. See
`pipeline-attachment-and-reentry`.

Otherwise compute `next_action` from the **first** incomplete stage in order,
then apply **最终交付** rules from `full-delivery-acceptance`:

1. `project_init` incomplete → continue Project Definition
2. milestones missing → portfolio / milestone-workflow
3. If the **Pipeline Order Gate** ask applies (about to enter Plan; peers not
   started Analysis; mode unset):
   - interactive → `stage_id: milestone_plan`,
     `needs_user_confirmation: true`,
     `summary` = the exact ask sentence above; do not start Plan work
   - unattended → blocker `pipeline_order_unresolved`; refuse Plan; residual
4. Else if Analysis incomplete under the active order:
   - `depth_first` / single milestone / peers already analyzing → finish the
     earliest sequenced milestone's remaining Analysis
   - `breadth_first` → finish Analysis on any feature milestone still incomplete
     before any Plan
5. Analysis done for the Plan-eligible milestone(s), Plan incomplete → Plan
   Design Gate / plan batch; when Gate drafts are ready, emit
   `milestone-plan-acceptance-pack` for acceptance
6. Plan ready (pack accepted / unattended grant), implement incomplete → run /
   execute remaining tasks **using the accepted pack as the primary milestone
   alignment reference** (see `milestone-plan-acceptance-pack.md`); for long
   or unattended implement also keep an active durable run plan per
   `long-task-run-continuity.md` (optional collaborative planning surface when
   the host exposes one—never require a vendor mode name)
7. After Layer B green, **May** offer最终交付 even if only one milestone
   finished this run. When entering:
   - `project_feature_milestone_count == 1` → `pre_e2e_path: e2e_direct`;
     waive/skip stage 6; `next_action.stage_id: e2e_campaign` (full-project E2E)
   - count ≥ 2 → `full_unit_and_it`; next is stage 6 then stage 7
8. Final delivery green (or residuals) → `project_complete` / accept residuals

Within stages 3–5 after `pipeline_order` is set: `depth_first` prefers the
**earliest sequenced** milestone not done through Implement; `breadth_first`
prefers completing all Analyses, then all Plans, then all Implements.

## Relationship To Other Contracts

- Does **not** weaken Task Work, Grill, prototype, Plan Design Gate,
  milestone Plan acceptance pack, Delivery, Git checkpoint, or external-action
  gates.
- Unattended board display coexists with Unattended Residual Report at run end.
- Portfolio Ready is stage `milestones_created`, not project complete.
- Child task `done` alone does not set `integration_campaign`,
  `e2e_campaign`, or `project_complete` to `done`.
- Single-milestone `e2e_direct` waives portfolio IT only; it does **not** mark
  `e2e_campaign` or `project_complete` as `done`.

## Fail-Closed Codes

| Code                                            | When                                                                 |
| ----------------------------------------------- | -------------------------------------------------------------------- |
| `project_lifecycle_board_unread`                | Reference not loaded via MCP                                         |
| `project_lifecycle_board_missing`               | Project-bound turn without board                                     |
| `project_lifecycle_board_render_failed`         | Script/render not ok                                                 |
| `project_lifecycle_board_confirm_in_unattended` | Unattended asked user to confirm the board                           |
| `project_lifecycle_stage_skip`                  | Later stage claimed without earlier evidence                         |
| `project_lifecycle_board_incomplete_stages`     | Board omits one of the eight stage ids                               |
| `pipeline_order_unresolved`                     | Plan entry attempted while order unset and peer Analysis not started |
| `full_delivery_*`                               | See `full-delivery-acceptance`                                       |
| `pipeline_entry_unclassified`                   | See `pipeline-attachment-and-reentry`                                |
| `pipeline_reentry_skipped`                      | See `pipeline-attachment-and-reentry`                                |
| `pipeline_stage_not_rewound`                    | See `pipeline-attachment-and-reentry`                                |

## Admission Test

1. Did we load this reference via MCP?
2. Are all eight stage ids present with status + evidence?
3. Is `next_action.summary` a single concrete imperative in **plain language**
   (per `workflow-jargon-plain-language.md`)? Do not leave bare
   `execution_authorization` / `run` without a gloss and a suggested user
   phrase (e.g. 「可以说『开始实施』」).
4. If unattended: is the board display-only with no confirm prompt?
5. Does the next stage match the first incomplete pipeline step under the
   active `pipeline_order` (or the Pipeline Order ask / residual when unset)?
6. If about to enter Plan with peer Analysis `not_started` and mode unset: was
   Plan refused and the ask (interactive) or `pipeline_order_unresolved`
   (unattended) emitted?
7. If midstream change was confirmed: were writeback + stage rewind applied
   (`pipeline_reentry_skipped` / `pipeline_stage_not_rewound` otherwise)?
