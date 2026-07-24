# Pipeline Attachment And Re-entry

Unified entry classification and re-entry algorithm so **new projects**, **new
milestones**, **scattered tasks**, and **mid-pipeline digressions** all attach
to the same lifecycle pipeline. Open Q&A is allowed; confirmed decisions must
write back and, when early requirements change late, **rewind stages** before
continuing.

Does **not** replace: `discussion-writeback-contract`, `change-impact-fanout`,
`project-lifecycle-progress-board`, or task-orchestrator route owners. It
**orders** them.

## Mandatory Load

Load on every **project-bound** software turn (and when classifying how a turn
attaches to the pipeline):

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "pipeline-attachment-and-reentry"
)
```

Skipping on a project-bound turn fails closed as `pipeline_entry_unclassified`
when `entry_kind` is also omitted from the board / turn record.

Also load `project-lifecycle-progress-board`. For confirmed material decisions,
load `discussion-writeback-contract` + `change-impact-fanout`.

## A. Entry Kind (exactly one per turn)

Classify before choosing the primary owner. Prefer the **most specific** match
when signals overlap (`midstream_change` beats `pipeline_continue`).

| `entry_kind`        | Signals                                                                 | Attach action                                                                    | Primary owners                                  |
| ------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------- |
| `new_project`       | Initialize / define this project                                        | Project Definition; board from stage `project_init`                              | `granoflow-project-definition`                  |
| `new_milestones`    | Create or amend one or more milestones                                  | Milestone create/amend → task authoring → board stages 2–5                       | portfolio + milestone-workflow + task-authoring |
| `scattered_task`    | Incidental / one-line requirement                                       | Strong-bind active milestone else inbox; never skip Analysis when later executed | orchestrator `capture` + discussed-requirement  |
| `pipeline_continue` | 「进度」「下一步」「继续」「回到流水线」                                | Emit board; execute `next_action` only                                           | lifecycle board                                 |
| `midstream_change`  | Already in Plan / Implement / delivery, user changes early requirements | Open Q&A → writeback + fan-out → **stage rewind** → recompute board              | writeback + fan-out + this reference            |

Record `entry_kind` on the lifecycle board snapshot when project-bound.

## B. Open Q&A Without Leaving The Pipeline

1. Agents **May** answer digressions and explore options freely.
2. When the user **accepts / confirms / locks** a material adjustment, run
   writeback + change-impact fan-out (existing contracts)—chat/`temp/` alone is
   forbidden.
3. Every project-bound turn **still** ends with the lifecycle board
   (`project_lifecycle_board_missing` if omitted), including after
   `midstream_change`.
4. `next_action.summary` **Must** be plain language. After a confirmed
   midstream change, prefer:
   「已把刚才确认的改动写回真源；下一步回到 …（Analysis/Plan/…）」。

## C. Stage Rewind (hard)

When a confirmed change lands while the project is already at Plan, Implement,
Layer B, or final delivery, **rewind** before more product code or campaign
claims. Do not “orally patch and keep coding.”

| Change class                                  | Rewind                                                                                                                                                                                         |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `task_local`                                  | Re-open Analysis and/or Plan for that task; milestone `implement` → `in_progress`; do **not** claim Layer B / final delivery still green for that scope                                        |
| `portfolio_change`                            | Author missing tasks/coverage; affected tasks return to Analysis; recompute board stages 3–5 for the active milestone                                                                          |
| `charter_change` / product-truth              | Follow Project Work `charter_change_policy` (default `reopen_project_work`); may return stages toward `project_init` / Analysis; stale Plan/Delivery refs → `stale_reference_after_discussion` |
| Layer B / final-delivery coverage invalidated | Set `integration_campaign` / `e2e_campaign` (as applicable) back to `not_started` or `in_progress`; add a blocker row with reason                                                              |

After rewind, `next_action.stage_id` **Must** equal the first incomplete stage
(or the session override rules in `full-delivery-acceptance` when applicable).
Keeping later stages `done` after a confirmed early change fails closed as
`pipeline_stage_not_rewound`.

## D. Multiple Milestones And Scattered Tasks

1. Default `active_milestone_limit: 1` (Project Work): many milestones **May**
   be created in one turn (`new_milestones`), but Analysis→Implement prefers the
   **earliest incomplete** sequenced milestone. Board `milestones[]` lists each
   row.
2. `scattered_task` in inbox: board **not** required until the task binds a
   `projectId` or the user asks to attach it to the project—then emit board +
   `next_action` immediately.
3. `follow_up` work outside the current acceptance boundary → new task and/or
   new milestone (`new_milestones` / `scattered_task`), not silent scope creep
   inside Implement.

## E. Board Fields (optional but recommended)

```yaml
entry_kind: new_project | new_milestones | scattered_task | pipeline_continue | midstream_change
reentry:
  from_stage: milestone_implement # stage where digression was noticed
  reason: "<plain language>"
  change_class: task_local | portfolio_change | charter_change | follow_up
  writeback_status: written_and_read_back | pending | not_applicable
```

Render scripts **Must** tolerate absence; when present, show a short 「回轨」
section.

## F. Fail-Closed Codes

| Code                          | When                                                                 |
| ----------------------------- | -------------------------------------------------------------------- |
| `pipeline_entry_unclassified` | Project-related turn without `entry_kind` / contract unread          |
| `pipeline_reentry_skipped`    | Confirmed `midstream_change` without writeback, rewind, or board     |
| `pipeline_stage_not_rewound`  | Early change confirmed but later pipeline stages left falsely `done` |

## Relationship

| Concern                     | Owner                                                  |
| --------------------------- | ------------------------------------------------------ |
| Stage labels / next_action  | `project-lifecycle-progress-board`                     |
| Confirmed decision bytes    | `discussion-writeback-contract` + fan-out              |
| Capture vs analyze/plan/run | `granoflow-task-orchestrator`                          |
| Final delivery path         | `full-delivery-acceptance` / acceptance-delivery skill |
| This file                   | Classify entry + order re-entry                        |

## Must Not

- Skip the board on project-bound turns because the user “only asked a question.”
- Continue Implement/campaign after confirmed early-requirement changes without rewind.
- Classify every digression as `pipeline_continue` to avoid writeback.
- Force a board on pure unbound inbox mood/capture with no project binding.
