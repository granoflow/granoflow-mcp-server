# Project E2E SoT

Single owner for the **mutable, project-local end-to-end orchestration SoT**
stored under the target repo `temp/`. It is the coarse main path from project
init through delivery. Skill-internal Grill, lint, and suite-merge details are
black boxes—this file records gates, next step, and evidence pointers only.

## Mandatory Load

Load before long / unattended project runs, when creating or refreshing the
SoT, and when host-wake ticks resume work:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-agent-workflow",
  referenceId: "project-e2e-sot"
)
```

Skipping the load on a long or unattended project run fails closed as
`project_e2e_sot_unread`. Missing instance when required →
`project_e2e_sot_missing`. Stale digests / next step after cutoff →
`project_e2e_sot_stale`.

Also load `long-task-run-continuity` (Layer A = this SoT) and
`project-lifecycle-progress-board` (stage ids align).

## Location

```text
temp/project-e2e-sot-v<n>.md
```

YAML frontmatter + short body. Bump `v<n>` only on material replans. Legacy
`temp/run-plan-*` paths are compatibility aliases; prefer this file. Host wake
binds `bound_sot_path` to the active SoT.

Lint:

```text
python3 skills/granoflow-agent-workflow/scripts/lint_project_e2e_sot.py \
  path/to/project-e2e-sot-v1.md
```

## Lifecycle (when to write)

| When                                       | Action                                                                                                |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `project_init` done                        | **Create** skeleton: eight stages + meta; `work_items` may be empty                                   |
| `milestones_created` done                  | **Expand** per in-scope task `*.3.1_analysis` / `*.3.2_plan`; set early `cross_milestone_integration` |
| Task Analysis confirmed / 定稿             | Mark `3.1` done; same wave set `3.2` in_progress; pin `next_step` to that `3.2`                       |
| All milestone `3.2` done + pack `accepted` | Stage `milestone_plan` done; open `{M}.implement` only then                                           |
| `{M}.implement` close                      | Re-list pack `file://` with **fulfillment** wording (not plan-baseline); no per-task implement rows   |
| Stages 6 / 7                               | Project-level rows + thin-gate conclusions; system accept + notify                                    |
| Lost / stale                               | Regenerate from Granoflow Project Work / Milestone Work / Task Work + digests                         |

Do **not** create a full task-level SoT before `project_init` is done.

## Granularity (hard)

| On SoT                                          | Not on SoT                                  |
| ----------------------------------------------- | ------------------------------------------- |
| Board stages 1–8                                | Grill axes, prototype lint steps            |
| Per-task `3.1` / `3.2` only                     | Per-task Implement rows                     |
| Milestone `{M}.implement` black box             | Delivery / unit / learning ledger internals |
| Project `integration_campaign` / `e2e_campaign` | Suite merge algorithms                      |
| Thin gate enums + `evidence_ref`                | How edges were derived                      |

## Analysis → Plan pin (hard)

For any task pair `T`:

1. While `T.3.1` is not done, do not start `T.3.2` or Implement.
2. When `T.3.1` becomes done, `next_step` **Must** be `T.3.2` until that `3.2`
   is done (or explicit `user_override` / cancel).
3. User 「确认」/「定稿」 on Analysis **opens** Plan in the same wave.
4. Jumping `next_step` to another task while `T.3.2` is pending without
   `override` → `project_e2e_sot_next_step_unpinned`.

## Gate lint in `next_step` (hard at stage transitions)

When `next_step` enters or closes these transitions, its instruction text
**Must** name the gate lint (so host-wake ticks cannot skip the script):

| Transition                                            | Lint / gate to name in `next_step`                                                                 |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Milestone Plan pack accept / refresh before Implement | `lint_milestone_plan_acceptance_pack.py` (+ `--require-links` when HTML ready)                     |
| Pack ↔ task test-case sync (when cases present)       | `lint_milestone_plan_pack_case_sync.py`                                                            |
| Resume after cutoff / wake                            | `lint_project_e2e_sot.py --require-digest-match`                                                   |
| Layer B / milestone IT close                          | `lint_feature_completeness_matrix.py` and/or milestone IT preflight evidence                       |
| Delivery reconcile vs accepted pack                   | `lint_milestone_plan_pack_delivery_reconcile.py`                                                   |
| `e2e_campaign` round close / case execution gate      | `lint_plan_case_implementation.py --gate e2e_campaign` (+ e2e campaign artifact lint when written) |

Omitting the named lint at these transitions fails closed as
`project_e2e_sot_next_step_missing_gate_lint` when a wake tick or stage claim
proceeds without running it.

## Scheme 1 — Plan pack before Implement (hard)

Within a feature milestone: all in-scope `3.1→3.2` complete **and** milestone
Plan acceptance pack `status: accepted` (or valid unattended adopt) **before**
any `{M}.implement` / code Execution. Violations →
`implement_before_milestone_pack_accepted` /
`implement_before_all_ap_forbidden` (interactive portfolio rule unchanged).

Unattended schedule: per milestone **all A→P (+ pack accept) → then implement
(+ Layer B) → next milestone**. Do not A→P→I per task with code before siblings
finish Plan.

## Thin gates (main path)

```yaml
cross_milestone_integration: pending | planned | not_applicable
integration_campaign:
  path: full_unit_and_it | waived_e2e_direct | not_started
  cross_milestone_journey_check: not_applicable | covered | gap
  evidence_ref: [] # suite_plan, closing_summary, journey_derivation, …
e2e_campaign:
  coverage_matrix_check: not_applicable | covered | gap
  evidence_ref: []
# Optional coarse pointers (omit or [] when unused; details in review pack):
parallel_batches: [] # [{ batch_id, review_ref, status }]
```

`parallel_batches` is a **pointer only** to
`temp/parallel-batch-<batch_id>-review-v<n>.md` after concurrent implement
batches. Host concurrency rules and merge-review live in
`parallel-task-execution` / `parallel-batch-merge-review`—not on this SoT.

- `cross_milestone_journey_check: gap` ⇒ stage `integration_campaign` must not
  be `done` (`cross_milestone_journey_gap`).
- `coverage_matrix_check: gap` ⇒ stage `e2e_campaign` must not be `done`
  (`e2e_coverage_matrix_gap`).
- Derivation / merge rules stay in integration / e2e campaign references.

## Implement closeout (interaction)

SoT row is milestone-level `{M}.implement` only. At wave end:

- Re-emit the same milestone pack absolute `file://` links.
- Plan-phase listing = baseline plan; Implement listing = **fulfillment
  promise**. Copy must distinguish the two.
- Interactive: offer optional local deploy for manual pack contrast.
- Gaps vs pack → immediate rework; do not green-wash.

## Stages 6 / 7 (interaction)

Even in interactive mode: `agent_auto`, system acceptance, notify via Closing
Summary—do not ask the user to approve IT/E2E green. Board display-only.

## Minimum frontmatter

See `project-e2e-sot-template.md`. Required keys:

- `doc_type: project_e2e_sot`
- `project_id`, `status`, `interaction_mode`, `updated_at`
- `source_digests` (at least `project_work`)
- `source_digest_verification` — required when linting with
  `--require-digest-match` (long/unattended resume): for each non-empty
  `source_digests.*` key, `{ recorded, app_readback, matched: true }` with
  `recorded == source_digests[key] == app_readback`
- `stages` (all eight board ids)
- `work_items` (list; may be empty after init-only create)
- `next_step` with `work_item_id` when status is `active`
- `cross_milestone_integration`
- `integration_campaign` / `e2e_campaign` objects with check enums

## Regeneration

When missing or stale:

1. Resolve project; read Project Work / milestones / tasks / pack statuses /
   campaign evidence.
2. Rebuild stages + `work_items` from evidence (confirmed Analysis → 3.1 done,
   etc.).
3. Set `next_step` to the earliest legal unfinished item under Scheme 1 + pin
   rules.
4. Refresh `source_digests` and `updated_at`.
5. Lint before continuing.

## Fail-closed codes

| Code                                          | Meaning                                                               |
| --------------------------------------------- | --------------------------------------------------------------------- |
| `project_e2e_sot_unread`                      | Reference not loaded                                                  |
| `project_e2e_sot_missing`                     | Required run without active SoT file                                  |
| `project_e2e_sot_stale`                       | Digests / next_step not refreshed, or `--require-digest-match` failed |
| `project_e2e_sot_lint_failed`                 | Lint aggregate failure                                                |
| `project_e2e_sot_next_step_unpinned`          | 3.1 done but next skips pending 3.2                                   |
| `project_e2e_sot_next_step_missing_gate_lint` | Stage-transition `next_step` omitted required gate lint name          |
| `implement_before_milestone_pack_accepted`    | Execution before pack accepted                                        |
| `cross_milestone_journey_gap`                 | Stage 6 done while check is `gap`                                     |
| `e2e_coverage_matrix_gap`                     | Stage 7 done while check is `gap`                                     |

## Relationship

| Concern               | Owner                                               |
| --------------------- | --------------------------------------------------- |
| Board display         | `project-lifecycle-progress-board.md`               |
| Wake / continuity     | `long-task-run-continuity.md` (Layer A = this SoT)  |
| Ask budget            | `unattended-interaction-contract.md`                |
| Pack accept gate      | `milestone-plan-acceptance-pack.md`                 |
| Parallel batch review | `parallel-batch-merge-review.md` (+ host policy)    |
| IT journey derivation | `granoflow-integration-test-campaign` orchestration |
| E2E matrix            | `e2e-user-flow-coverage.md`                         |

## Admission Test

1. Was this reference loaded for a long / unattended project run?
2. Does an active SoT exist after `project_init`?
3. Are task rows only 3.1/3.2 (plus milestone/project black boxes)?
4. After Analysis 定稿, is next_step pinned to that task’s 3.2?
5. Is Implement blocked until pack accepted?
6. Are stage 6/7 thin gates not `gap` when those stages claim `done`?
