# Unattended Interaction Contract

This document is the single owner for deciding whether an unattended Granoflow
run may ask the user a question, what counts as authorized work, and how
externally impossible items are deferred. Read it whenever a user requests
unattended, hands-off, automatic, or no-interruption completion.

## Explicit Unattended Declaration

When the user **explicitly declares** unattended mode for a bounded scope
(task, milestone, integration campaign, or whole-project completion), that
declaration is the authorization boundary for the run:

1. **Solvable work is authorized.** Any step the Agent and current environment
   can complete without a human-held secret, physical presence, third-party
   human approval, or out-of-band channel is treated as granted. Execute it
   directly (phase confirms, local tools, recommended defaults, local gates,
   Delivery, campaign suite runs on the selected device, project-context
   `revise_code` / `revise_context_yaml` decisions, etc.). Do not invent a
   mid-run confirmation for solvable work.
2. **Externally impossible work is deferred—not a whole-run stop.** If evidence
   shows the item cannot be executed for an external reason (missing user-only
   credential/OTP, no device/simulator, App Store / payment human approval,
   offline third party, capability absent and not installable in-scope), park
   it in `deferred_external_work` and **continue every other ready task**.
3. **Never block the queue.** One deferred item must not freeze sibling tasks,
   later milestones, or the rest of a campaign round.
4. **End with an explicit residual list.** When no more solvable ready work
   remains, emit a user-visible **Unattended Residual Report** naming every
   deferred or incomplete item, why it was external, and the resume condition.
   Do not silently omit residuals.

Inventing credentials, impersonating the user, or marking external work done
without evidence remains forbidden.

### Device capability is not unattended test scope

Inventory the current platform, official simulators/emulators, and already
installed third-party VMs with a proven E2E path. This is a capability list,
not a mandatory matrix. In unattended mode:

1. if the project supports the current development platform, select only that
   platform for integration/E2E execution;
2. if it does not, select exactly one already-available supported host,
   preferring the project primary platform, then an official virtual device,
   then an installed E2E-capable third-party VM;
3. never install a third-party VM stack or image;
4. keep all non-selected supported platforms development-only and record an
   external-device handoff with `tested: false`.

The final Residual Report may ask the user to test those platforms. A later
reply equivalent to “知道了 / 了解 / 我会测试” acknowledges and completes that
handoff, but does not change `tested: false` or authorize a green platform
claim.

## Observable Invariant

After a valid unattended request starts one bounded run, use:

```yaml
interaction_budget: 0
interaction_decision: continue | defer_item | complete_with_residuals
blocker_class: none | direction_change | scope_drift | external_impossible | subjective_acceptance
completed_independent_work: []
deferred_external_work: []
# each deferred row: id, title, blocker_class, evidence, resume_condition
question_batch_size: 0
```

## Milestone Final Grill

For Milestone final acceptance, unattended mode does not skip `grill-me`.
Process one question at a time: state the question, the AI recommendation, and
the reason, then auto-adopt that recommendation without waiting. Record
`grill_me_status: recommendations_auto_adopted`,
`final_acceptance_status: unattended_auto_adopted`, and
`accepted_by: unattended_grant`. Never label the result user-accepted. The
accepted digest must equal the reviewed plan digest, and
`authorization_effect` remains `none`.

`interaction_budget: 0` counts every user-facing request for confirmation,
choice, permission, information, or approval. Status notices, evidence reports,
a Structural Change Forecast, an explicit `project_context_resolution`
decision notice, defer notices, and the final Residual Report do not consume
the budget—they must still be emitted so the user can see progress and gaps.
Do not consume the budget for non-confirming notices and residual reporting.

Do not repair one observed phrase such as a particular Analysis prompt. Apply
the invariant to the whole run. When the unattended scope remains clear,
solvable work covers Analysis confirmation, Planning permission, Plan
confirmation, Execution authorization, implementation choices, local tool
selection, test repair, deterministic verification, Delivery, attachment
readback, completion, and campaign suite execution.

For periodic reviews, milestone escalation and archival: emit a notice, then
continue when solvable under the declaration. If archive capability is missing,
**defer** that archival item and continue other work—do not PATCH status to fake
closure.

During Project Definition, every decision carries a recommendation. **Only when
the user explicitly declared unattended for that initialization** may the host
adopt recommendations immediately and default Design Baseline + App Shell visual
confirmation to `auto_accept_recommendation` after exact App import/readback—
**except** the Product Spec Completeness / flow-decomposition rules below. If
unattended was not explicitly declared, Project Definition stays interactive:
ask → recommend → wait for the user to decide. Soft aesthetic preference is not
a wait-for-user loop under explicit unattended; it never authorizes skipping
interactive confirmation.

### Discussion writeback under unattended

Material discussion decisions (prototype rematch, page split, Plan/Scope edit,
product-spec coverage) still require App-slot writeback + hash/id readback
**and** a closed Change Impact Fan-out ledger in the same batch.
`interaction_budget: 0` never excuses leaving truth only in chat or `temp/`,
nor skipping sibling-task/doc/card dispositions →
`discussion_writeback_pending` / `temp_only_artifact_forbidden` /
`change_impact_*` / `prototype_product_doc_writeback_required`. See
`discussion-writeback-contract`, `change-impact-fanout`, and
`prototype-product-truth-writeback`.

### Product Spec under unattended (thin docs ≠ silent ready)

When filling `product_spec_coverage` under explicit unattended:

1. **Always** draw the operation flowchart, list serial gates vs parallel ops,
   and record `split` / `keep_cohesive` (with required summaries) or park
   `needs_user_decision` as residual /
   `thin_product_doc_gap_requires_user` — never skip the pass. Do **not** use
   risk labels to force multi-screen.
2. Auto-adopt only **non-decision-changing** gap fills with
   `agent_recommendation_adopted`. Decision-changing thin-doc gaps must **not**
   be silent-auto-accepted → fail closed or residual
   `thin_product_doc_gap_requires_user`.
3. Never invent whole journeys as `user_stated`. Never mark
   `product_spec_coverage.status: ready` while decomposition, stress paths, or
   decision-changing thin gaps remain open.
4. Unattended Baseline visual `auto_accept_recommendation` never waives these
   gates.

### Prototype links under unattended

Whenever HTML prototypes are authored (Design Baseline screens/Shell units or
task `ui_prototype`):

1. After **each** prototype becomes previewable, emit a clickable preview link
   as a non-blocking notice and append it to `prototype_link_ledger`.
2. Do not wait mid-run for visual taste confirmation.
3. Project Definition Design Spec / Shell under unattended: author **one**
   faithful `spec_match` **Style Guide / Design Tokens board** (not a
   journey-screen gallery) via `draw_visual_lots.py` **true-random** draw, then
   **one** `shell_match` that **embeds that Spec’s tokens** and is product-near
   (not wireframe-only; no independent palette seed)—do **not** run interactive
   triads or AI challengers. Journey/critical screens beyond the Shell’s primary
   surface belong in the Baseline package after Spec+Shell. After Baseline
   confirm, write `widgets.yaml` from that confirmed Baseline prototype.
4. At run close, emit a mandatory **Prototype Link Digest** that lists every
   ledger entry with clickable links so the user can audit all prototypes in
   one place. Omitting the digest fails closed as
   `prototype_link_digest_required`.
5. Interactive mode (default when unattended was not declared) uses the
   product-fitted two-round Design Spec HTML contract: six-dimension chooser,
   user selection code, then three complete Style Guide candidates by default
   or justified two. After the selected Spec is locked, run the Shell triad of
   Spec-embedded product-near chrome variants (tokens missing / wireframe-only
   → `shell_spec_tokens_missing` / `shell_wireframe_only`), stop after each
   review batch for pick / **换新批** (`--dedupe ledger`) / **在某套上改**
   (`prototype_preview_review_required` /
   `shell_triad_required` / `shell_spec_mismatch` / seed-collision /
   `design_spec_seed_not_drawn` / `visual_lot_dedupe_required` /
   `design_spec_user_facing_jargon` codes if skipped or rules violated).
   User-facing Preview Gate copy stays plain language (no `seed-*` / internal
   option enums).
6. Task / milestone `ui_prototype`: inherit locked Spec + Shell; **no** random
   visual seed (`task_prototype_seed_forbidden`); reuse `widgets.yaml` when the
   same role exists (`widget_reuse_required`); pass Craft Gate before confirm
   else `task_prototype_craft_incomplete` (including Baseline fit →
   `prototype_baseline_fit_*` / `prototype_generic_phone_frame`, product truth →
   `prototype_product_truth_violation` and user-visible copy boundary →
   `user_visible_copy_boundary_unread` /
   `user_visible_copy_boundary_violation`); keep design-first; high-risk UI needs
   feasibility conclusion before Readiness
   (`high_risk_feasibility_unresolved`).
   - **Unattended:** mainstream-first candidate protocol then **one**
     Baseline-fitted `expr_a` only (no dual/triple; no Design System reopen).
     Load `prototype-baseline-fit` and `prototype-expression-brainstorm` when
     authoring task page expressions; run
     `lint_prototype_expression_brainstorm.py`.
   - **Interactive (default when not unattended):** load
     `prototype-baseline-fit` (and `prototype-confirmed-chrome-lock` when
     chrome-family siblings are already confirmed), run
     **mainstream-reference-first** candidates (≥5; brainstorm backfill only
     when mainstream `<5`), then **two page expressions** (`expr_a` +
     `expr_b`) with **functional parity** and **strict Spec/Shell fit** inside
     the locked Design System **plus confirmed sibling chrome vocabulary**,
     with ≥2 contrast axes; mix-and-match per task/page;
     **side-by-side Contrast Gallery** with Baseline-fit + chrome-lock +
     candidate digests
     - per-axis visible-diff captions; optional third only for documented
       industry-peer deadlock; never re-offer Design Spec labels as task
       options; never feature-split, data-diverge, ship generic parallel
       phones, or invent a parallel chrome dialect after siblings are
       confirmed
       (`prototype_option_design_system_reopened` /
       `prototype_baseline_fit_*` /
       `prototype_generic_phone_frame` /
       `prototype_shell_chrome_mismatch` /
       `prototype_confirmed_chrome_lock_*` /
       `prototype_option_brainstorm_*` /
       `prototype_option_mainstream_skip` /
       `prototype_option_scope_mode_invalid` /
       `prototype_option_function_split` /
       `prototype_option_data_divergence` /
       `prototype_option_third_unjustified` /
       `prototype_option_contrast_insufficient` /
       `prototype_option_near_duplicate` /
       `prototype_option_contrast_gallery_required` /
       `prototype_option_diff_unlabeled`).

## Current Run Versus Durable Delegation

A user-origin instruction that explicitly asks to run or complete one exact or
unambiguous target unattended is a direct instruction for the same active run.
The host reports the resolved target, repositories, solvable action classes,
deferred-external policy, and stop conditions as a non-confirming notice, then
continues. The same active run does not require an envelope round trip.

Record `authorization_source: same_run_direct` and the source message. At every
phase, consume the direct instruction while work remains inside the declared
Outcome, Evidence, Scope, Risk, target, and repositories. A Grill pass is
evidence for that decision, not a separate authorization ritual.

When authorization must survive an unattended interval, process restart, or
later host turn, use `authorization_source: durable_envelope`. That path still
records the confirmed envelope, App-owned attachment receipt, expiry, and
scope—but under an **explicit unattended declaration**, solvable actions inside
that scope execute without re-asking. Externally impossible actions are deferred.

### What “solvable” includes under explicit unattended

Treat as authorized and execute when the environment can do it now:

- ordinary phase gates and document upload/readback;
- local code, tests (unit/lint/type/build), builds, and Structural Forecast /
  project-context hard gates;
- local Git checkpoint/commit when the project/git preference and grant allow
  local history writes;
- integration-test and E2E **campaign** suite runs on the campaign device when
  **最终交付** was entered (`full-delivery-acceptance`; stages
  `integration_campaign` and `e2e_campaign` use `campaign_drive: agent_auto` in
  interactive and unattended alike—orchestrate, run, triage, fix, re-test
  without ordinary confirm questions; E2E also captures/shows screenshots under
  `temp/` when the host can). Single feature-milestone projects may waive
  portfolio IT and run full-project E2E directly;
- adopting recommendations and `revise_code` / `revise_context_yaml` decisions
  with emitted notices.

### What must be deferred (external impossible)

Park in `deferred_external_work` and continue other work:

- secrets, 2FA, OTPs, or credentials that exist only with the user;
- physical device / human App Store / payment / bank / government approval;
- publish/deploy/push/external messaging that the current host literally cannot
  perform (missing token, offline store, policy wall);
- Note/Card creation/link/modify that still needs human study-judgment over the
  latest preview—prepare dry-run at the end, then list as residual rather than
  blocking engineering tasks mid-run.
  Review Note/Card authoring is also excluded from unattended authorization.
- any action whose success cannot be evidenced without an external human step.

Do not use “forbidden_action” as a mid-run freeze of the whole portfolio when
sibling solvable work remains.

## Continue Without Asking

Set `interaction_decision: continue` when the Agent can execute solvable work
inside the declared unattended scope. This includes:

- consuming ordinary phase gates under the explicit unattended authorization;
- choosing implementation details, files, symbols, local tools, and test order
  from repository evidence and the confirmed scope;
- repairing lint, format, type, build, and unit-test failures until the
  required gate is green (task-local integration tests remain **not executed
  inside the feature task**; stage `integration_campaign` /
  `granoflow-integration-test-campaign` owns integration runs;
  `e2e_campaign` / `granoflow-e2e-test-campaign` owns UI E2E + screenshots
  under `agent_auto`);
  do **not** run task-local integration or E2E suites inside ordinary
  feature-task flows—defer execution to the matching campaign stage.
- starting or checking an allowed local development service or App;
- revising Analysis or Plan wording after a Grill when the revision stays
  inside declared Outcome/Scope;
- producing and reading back Task Work, Delivery, acceptance evidence, nodes,
  attachments, and final task state;
- applying a newly discovered touchpoint already implied by the approved
  outcome and minimum-change budget.

Silence is not required. Report material progress as notices, never as
questions disguised as courtesy.

### Project Lifecycle Progress Board (display-only)

When the run is **project-bound**, every material turn (and the run end)
**Must** emit the Project Lifecycle Progress Board from
`project-lifecycle-progress-board.md` with:

- `interaction_mode: unattended`
- `board_confirmation: display_only`
- `next_action.needs_user_confirmation: false`

Do **not** ask the user to acknowledge or confirm the board. Unattended still
walks the same pipeline stages as interactive mode; it only skips asking.
Asking solely because the board was shown fails closed as
`project_lifecycle_board_confirm_in_unattended`.

### Milestone Plan Acceptance Pack (display-only)

When closing a milestone Plan phase under unattended, emit the
`milestone-plan-acceptance-pack` Markdown as a **display-only** notice. Do not
ask the user to acknowledge the pack. Auto-adopt only under a valid unattended
Planning grant; still fail closed on `plan_copy_*` /
`milestone_plan_acceptance_pack_incomplete`. Asking solely for pack
acknowledgement fails closed as
`milestone_plan_acceptance_pack_confirm_in_unattended`.

During unattended **implement**, still load the adopted pack and use it as the
primary milestone alignment reference; skip only acknowledgement questions, not
pack reconciliation at Delivery.

### Long-task run continuity (required on implement)

Before unattended **implement** / campaign work that is long (milestone-wide or
multi-task), load `long-task-run-continuity.md` and create/update a **durable
run plan** on disk. That file is the portable continuity surface.

If the host exposes a **collaborative planning surface**
(`availability: available`), activate it without asking. If it is unavailable
or unknown, **do not block**—continue with the durable run plan alone.

Asking the user solely to enable a host-local planning UI fails closed as
`collaborative_planning_surface_confirm_in_unattended`. Missing or stale
durable run plans fail as `long_run_plan_missing` / `long_run_plan_stale`.

## Defer Item (do not block peers)

Set `interaction_decision: defer_item` when the **current** work item is
externally impossible but other ready work exists:

1. Persist a defer record (id, title, `blocker_class`, evidence,
   `resume_condition`).
2. Emit a short defer notice (not a question).
3. Immediately schedule/continue the next ready solvable task, milestone work,
   or campaign step.
4. Do **not** open a waiting question batch that stalls the run.

`blocker_class` for deferred items:

- `external_impossible`: proven external/human-only dependency;
- `subjective_acceptance`: Note/Card or true taste/legal gate parked for the
  residual report;

`blocker_class: subjective_acceptance`

- `direction_change` / `scope_drift`: only when the item itself cannot be
  safely auto-resolved—even then, prefer adopting the recorded recommendation
  for solvable siblings; park only the contested item when possible.

## Complete With Residuals

When no solvable ready work remains, set
`interaction_decision: complete_with_residuals` and emit the
**Unattended Residual Report**:

```markdown
## Unattended Residual Report

- Scope: <declared unattended scope>
- Completed: <count / summary refs>
- Prototype Link Digest: <clickable links for every HTML prototype authored;
  required when any prototype was produced>
- Plan Acceptance Link Digest: <clickable HTML/Markdown pack links authored this
  run; required when any Plan acceptance HTML was produced>
- Acceptance layers (when any task/milestone closed this run):
  - Layer A 单任务完成: <per-task Delivery / acceptance_report refs>
  - Layer B 里程碑集成验收: <Suite Plan order / IT green|residual / Experience / 任务回顾>
  - Do not fuse into one unlabeled “all done” list (`acceptance_layers_fused`)
- Deferred / not executed:
  1. <title> — <blocker_class> — <why external> — <resume_condition>
  2. ...
- Explicit statement: these items were **not** executed in this unattended run.
```

A run with residuals is a successful unattended completion of everything
solvable—not a fake all-green project. Never claim deferred publish/device/card
work as done.

## Waiting Behavior (narrow)

Under explicit unattended mode, **do not** use mid-run
`interaction_decision: wait` + user questions to serialize the portfolio.
Prefer `defer_item` + continue peers, then `complete_with_residuals`.

Only if the host cannot even start (no project, no grant text, corrupt state)
may the run stop with a single blocker notice; still list what could not start.

A failed test, incomplete draft, unfamiliar code, ordinary implementation
choice, or preference for reassurance is not external-impossible—retry,
diagnose, replan, or use the best evidence-backed local option.

## Responsive Prototype Finalization

For UI Project Definition and Task Analysis, unattended mode does not skip the
platform, option-selection, layout-expansion, or final Bundle checkpoints.
State each recommendation and its evidence, then auto-adopt it without waiting.

- Record platform and Bundle acceptance as `unattended_auto_adopted`.
- Record `accepted_by: unattended_grant`; never write `user_confirmed`.
- Expand the selected primary-layout option to every required layout family.
- Complete Widget Catalog writeback and App SHA readback before Analysis closes.
- Preserve `authorization_effect: none`; prototype acceptance never authorizes
  implementation.

## Task Analysis Product And Technical Finalization

Unattended UI Analysis still runs the complete
`task-analysis-finalization` sequence:

- review the internal Logic Draft with a logically independent reviewer;
- state and auto-adopt the Page Definition Brief as
  `unattended_auto_adopted` / `unattended_grant`;
- run every Contract Grill axis question-by-question, stating the recommendation
  and reason before auto-adopting it;
- bind every option and layout to the same Content Contract digest;
- produce deterministic DOM, state, screenshot, and interaction evidence for
  the Contract-to-Prototype Semantic Review;
- independently review and verify the Analysis Technical Package;
- present the final layouts and behavior summary, then auto-adopt the
  recommendation without claiming user acceptance;
- complete Widget Catalog writeback and App SHA readback before Analysis
  closes.

Every acceptance record keeps `authorization_effect: none`.
