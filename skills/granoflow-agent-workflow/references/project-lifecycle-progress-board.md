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

| #   | Stage id               | Meaning                                                                                                                                                                                                             | Primary owners                                                                                             |
| --- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | `project_init`         | Project Definition Done (Project Work + Engineering pack; Design Baseline when `visual_baseline` required)                                                                                                          | `granoflow-project-definition`                                                                             |
| 2   | `milestones_created`   | Planned milestones exist; portfolio tasks authored                                                                                                                                                                  | `granoflow-portfolio-orchestrator`, `granoflow-milestone-workflow`, `granoflow-task-authoring`             |
| 3   | `milestone_analysis`   | **Per active milestone**: every in-scope child has confirmed Analysis (**UI includes confirmed prototype + link ledger**). `gf析` may stop here; `gf规`/`run` soft-merge into Plan.                                 | `granoflow-task-orchestrator` + agent-workflow Analysis                                                    |
| 4   | `milestone_plan`       | **Per-task** Plan Design Gate + living milestone Plan acceptance pack (draft→HTML links→`prototype_alignment`→accept). Soft-merge: no courtesy pause after Analysis for `gf规`/`run`.                               | Plan Design Gate + `milestone-plan-acceptance-pack` + `lint_milestone_plan_acceptance_pack.py` + Readiness |
| 5   | `milestone_implement`  | **Only after** milestone Plan acceptance pack is `accepted`. Milestone-level implement black box (per-task code inside). Unattended: include Layer B here. Interactive: Layer A here; Layer B may defer to stage 6. | task-orchestrator + (`milestone-integration-acceptance` when Layer B runs here)                            |
| 6   | `integration_campaign` | **最终交付 · 项目级 IT**：编排并跑全量不可见 IT。交互调度在此吸收原各里程碑 Layer B + 项目级 IT。单功能里程碑项目可 **waive** 本阶段，直进全面 E2E。见 `full-delivery-acceptance`。                                 | `full-delivery-acceptance` + `granoflow-integration-test-campaign`                                         |
| 7   | `e2e_campaign`         | **最终交付 · 全面 E2E**（始终全项目覆盖，防改一处坏别处）：覆盖矩阵、可见窗、截图、Closing Summary。                                                                                                                | `full-delivery-acceptance` + `granoflow-e2e-test-campaign`                                                 |
| 8   | `project_complete`     | Required milestones accepted; **最终交付** green (or explicit residual); residuals closed or deferred                                                                                                               | milestone-coordination accept + project closeout                                                           |

Rules:

1. Stages 3–5 follow **Schedule Policy** derived from `interaction_mode`
   (see below). **Do not** ask the user to choose traversal names
   (`breadth_first` / `depth_first` / `unset` are retired).
2. Stages 6–7 are **最终交付测试** (`full-delivery-acceptance`). Path:
   - project has **1** feature milestone → waive stage 6 / skip portfolio unit+IT
     → **full-project** E2E (milestone Layer B already covered under unattended
     schedule, or ran inside the single-milestone design+implement path)
   - project has **≥2** → full unit → stage 6 IT → **full-project** E2E
     Inside campaigns, `campaign_drive: agent_auto`; board display-only.
3. Stage 7 requires stage 6 `done` **or** valid single-milestone waiver
   (`pre_e2e_path: e2e_direct` / `integration_gate: waived_single_milestone`).
   Claiming `project_complete` while skipping最终交付 without residual fails
   closed as `project_lifecycle_stage_skip`.
4. Ordinary feature tasks still obey task-local IT policy. Layer B timing:
   unattended → stage 5 per milestone; interactive → stage 6 with project IT.
   E2E only in最终交付.

## Schedule Policy (derived from interaction mode)

**Default is interactive.** Users never pick `breadth_first` /
`depth_first` / `unset`. Scheduling is implied by
`interaction_mode` (preferences, grant, or an explicit mid-run switch).

Persist optionally on Project Work / board (mirror only; not a user chooser):

```yaml
schedule_policy:
  schema: granoflow_schedule_policy_v1
  # Always derived — do not ask the user to set this enum
  kind: interactive_all_ap_then_implement | unattended_milestone_loop
  derived_from: interactive | unattended
  switched_at: null # ISO-8601 when user switches into unattended mid-run
  switched_by: null # user | unattended_grant
```

| `interaction_mode`      | `schedule_policy.kind`              | Meaning                                                                                                                                                                                                                                                                                                             |
| ----------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interactive` (default) | `interactive_all_ap_then_implement` | **Per task** across all feature milestones: Analysis (incl. prototypes) → Plan → next task. **Forbidden** to start any Implement while any in-scope task still lacks confirmed Analysis+Plan. Then all Layer A → stage 6 full IT (absorbs Layer B) → stage 7 E2E. Purpose: finish human-reviewed design work first. |
| `unattended`            | `unattended_milestone_loop`         | **Per milestone (Scheme 1)**: all in-scope children Analysis→Plan (3.1→3.2; 定稿 opens Plan) → milestone Plan acceptance pack `accepted` → then milestone Implement (+ Layer B) → next milestone. **Forbidden** to Implement any task before the pack is accepted.                                                  |

### Mid-run switch to unattended

Whenever the user (or an approved grant) switches into unattended:

1. Set `interaction_mode: unattended` and
   `schedule_policy.kind: unattended_milestone_loop` for **remaining** work.
2. Do **not** redo completed Analysis/Plan/Implement evidence.
3. Continue from the earliest incomplete work under the unattended milestone
   loop (finish current milestone’s P→I before opening the next milestone’s
   Analysis when that reduces context drift).
4. If the host Agent exposes a built-in **Plan / planning mode** (or equivalent
   collaborative planning surface) and it is available, **enter it when
   switching into unattended** without asking the user to enable it. If the
   surface is unavailable or unknown, continue with the Project E2E SoT alone
   (`project-e2e-sot` / `long-task-run-continuity`) — never block on a vendor
   mode name. Asking solely to enable host Plan mode fails closed as
   `collaborative_planning_surface_confirm_in_unattended`.
5. If the host exposes a **host wake surface** and it is available, arm wake
   **bound to `temp/project-e2e-sot-v*.md`** (Host Wake Tick Protocol in
   `long-task-run-continuity`). Do not arm a bare 「继续」 wake.

### Interactive continue rules

Under interactive `pipeline_continue` / 「继续」: after a task’s Analysis
**定稿/确认**, proceed to that same task’s Plan before the next task’s
Analysis. Explicit `analyze` / `gf析` may stop before 定稿. Do **not** start
Implement until every feature milestone’s in-scope tasks have confirmed
Analysis+Plan **and** each milestone Plan acceptance pack is `accepted`.

### Unattended continue rules

Do **not** chat-ask for schedule choice. Unattended already implies
`unattended_milestone_loop` (Scheme 1). Under `pipeline_continue` / long-run /
「继续」 / host-wake tick: finish all remaining Analysis→Plan for the current
milestone and accept the Plan pack before any Implement; do not Implement one
child while sibling Plans are open. Orchestration truth is
`temp/project-e2e-sot-v*.md` (`project-e2e-sot.md`).

## Interaction Modes

| Mode          | Same pipeline?             | Progress board                                  | Stage / phase confirmations                                                                                                                                   |
| ------------- | -------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interactive` | Yes (interactive schedule) | **Required** at end of every project-bound turn | Existing confirm gates remain (`[confirm]`, Plan Gate, visual pick, etc.)                                                                                     |
| `unattended`  | Yes (unattended schedule)  | **Required** as **display-only notice**         | Do **not** ask the user to confirm the board or ordinary phase questions; follow `unattended-interaction-contract` (defer external blockers; residual report) |

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
  schedule_policy: # derived from interaction_mode; never a user chooser
    schema: granoflow_schedule_policy_v1
    kind: interactive_all_ap_then_implement | unattended_milestone_loop
    derived_from: interactive | unattended
    switched_at: null
    switched_by: null # user | unattended_grant
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
3. Else if design work (Analysis/Plan) incomplete under the active schedule:
   - interactive (`interactive_all_ap_then_implement`) → for the earliest
     sequenced task that lacks confirmed Analysis or Plan: finish that task’s
     Analysis (incl. prototype), then that task’s Plan, then the next task;
     traverse all feature milestones before any Implement. Living milestone
     Plan acceptance pack updates as each task enters Plan.
   - unattended (`unattended_milestone_loop`) → on the earliest sequenced
     milestone: finish **all** in-scope Analysis→Plan (3.1→3.2; 定稿 opens
     Plan), accept the milestone Plan pack, **then** milestone Implement
     (+ Layer B). Never Implement before pack `accepted` (Scheme 1).
4. Under interactive schedule, when every feature milestone’s in-scope tasks
   have confirmed Analysis+Plan **and** each milestone pack is accepted, and
   Implement is incomplete → stage `milestone_implement`: Layer A only
   (implement + unit tests) for each task in order; **do not** run Layer B
   mid-wave. Use accepted packs as the primary alignment reference; keep
   `temp/project-e2e-sot-v*.md` per `project-e2e-sot.md` /
   `long-task-run-continuity.md` when long/unattended.
5. Under unattended schedule, after a milestone’s pack is accepted, implement
   that milestone (Layer A + Layer B) before starting the next milestone’s
   Analysis. When switching into unattended, activate the host collaborative
   planning surface if available and bind host wake to the Project E2E SoT.
6. After the Implement wave is ready for最终交付:
   - interactive + count ≥ 2 → stage 6 runs **full** IT (orchestrate then
     execute; absorbs deferred Layer B suites + project IT), then stage 7 E2E
   - unattended: after any milestone Layer B green, **May** offer最终交付;
     count == 1 → `e2e_direct` (waive stage 6); count ≥ 2 → `full_unit_and_it`
   - interactive + count == 1 → after Layer A (and any single-milestone IT
     policy) green, `e2e_direct` may waive stage 6 → full-project E2E
7. Final delivery green (or residuals) → `project_complete` / accept residuals

Within stages 3–5: interactive prefers **per-task Analysis→Plan across all
milestones**, then all Implements; unattended prefers the **earliest
sequenced** milestone not done through Implement (including that milestone’s
Layer B).

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

| Code                                                   | When                                                                                         |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `project_lifecycle_board_unread`                       | Reference not loaded via MCP                                                                 |
| `project_lifecycle_board_missing`                      | Project-bound turn without board                                                             |
| `project_lifecycle_board_render_failed`                | Script/render not ok                                                                         |
| `project_lifecycle_board_confirm_in_unattended`        | Unattended asked user to confirm the board                                                   |
| `project_lifecycle_stage_skip`                         | Later stage claimed without earlier evidence                                                 |
| `project_lifecycle_board_incomplete_stages`            | Board omits one of the eight stage ids                                                       |
| `implement_before_all_ap_forbidden`                    | Interactive schedule started Implement while any in-scope task lacks confirmed Analysis+Plan |
| `project_e2e_sot_implement_before_pack_accepted`       | Implement started before milestone Plan acceptance pack accepted (Scheme 1)                  |
| `collaborative_planning_surface_confirm_in_unattended` | Asked solely to enable host Plan/planning UI under unattended                                |
| `full_delivery_*`                                      | See `full-delivery-acceptance`                                                               |
| `pipeline_entry_unclassified`                          | See `pipeline-attachment-and-reentry`                                                        |
| `pipeline_reentry_skipped`                             | See `pipeline-attachment-and-reentry`                                                        |
| `pipeline_stage_not_rewound`                           | See `pipeline-attachment-and-reentry`                                                        |

## Admission Test

1. Did we load this reference via MCP?
2. Are all eight stage ids present with status + evidence?
3. Is `next_action.summary` a single concrete imperative in **plain language**
   (per `workflow-jargon-plain-language.md`)? Do not leave bare
   `execution_authorization` / `run` without a gloss and a suggested user
   phrase (e.g. 「可以说『开始实施』」).
4. If unattended: is the board display-only with no confirm prompt?
5. Does the next stage match the first incomplete pipeline step under the
   schedule derived from `interaction_mode`?
6. Under interactive: was Implement refused while any in-scope task still
   lacks confirmed Analysis+Plan (`implement_before_all_ap_forbidden`)?
7. When switching into unattended: if host Plan/planning mode is available,
   was it entered without asking; if unavailable, did work continue with the
   Project E2E SoT alone? If host wake is available, was it armed bound to
   that SoT (not a bare 「继续」)?
8. Under unattended: was Implement withheld until the milestone Plan acceptance
   pack was accepted (Scheme 1)?
9. If midstream change was confirmed: were writeback + stage rewind applied
   (`pipeline_reentry_skipped` / `pipeline_stage_not_rewound` otherwise)?
