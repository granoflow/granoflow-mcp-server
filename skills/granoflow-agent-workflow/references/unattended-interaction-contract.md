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
2. **Agent-selectable defaults are solvable.** Packaging / source / tooling
   choices the Agent can recommend without inventing product behavior (for
   example App icon source under `app-icon-source-gate`, local stack picks
   already covered by Project Work recommendation rows, Design Baseline
   `auto_accept_recommendation`) must be **recommend → auto-adopt → record
   provenance** with `decision_authority: unattended_grant`. Do **not**
   consume `interaction_budget`, park an interaction wait, or stall the
   queue solely to ask which of the Agent's enumerated options the user
   prefers. Prefer documented defaults (App icon missing → `ai_generated`).
3. **Externally impossible work is deferred—not a whole-run stop.** If evidence
   shows the item cannot be executed for an external reason (missing user-only
   credential/OTP, no device/simulator, App Store / payment human approval,
   offline third party, capability absent and not installable in-scope), park
   it in `deferred_external_work` and **continue every other ready task**.
4. **Never block the queue.** One deferred item must not freeze sibling tasks,
   later milestones, or the rest of a campaign round.
5. **End with an explicit residual list.** When no more solvable ready work
   remains, emit a user-visible **Unattended Residual Report** naming every
   deferred or incomplete item, why it was external, and the resume condition.
   Do not silently omit residuals.

Still fail closed (not agent-selectable): inventing product journeys as
`user_stated`, thin-doc decision-changing gaps that change Outcome/behavior
(`thin_product_doc_gap_requires_user`), secrets, payment, push/publish/deploy,
destructive Git, or impersonation.

Inventing credentials, impersonating the user, or marking external work done
without evidence remains forbidden.

## Card-Truth Readiness Gate (RB / UIT)

Reality Boundary and Route UI Truth writes use Knowledge materialization. They
are **anti-drift obligations** — unattended **Must** apply them in the same wave
as Plan `gap` / Delivery `will_change`, or truth drifts while code moves.

Before whole-project / milestone-wide / final-delivery unattended when the
project keeps `reality_boundary_index` and/or `route_ui_truth_index`:

1. Verify App/capability readiness (Local HTTP, `field-media.upload` when UIT
   screenshots are required).
2. **Auto-apply** seed gaps and pending `will_change` via assessment preview→
   apply and materialization preview→apply (`decision_authority:
unattended_grant` — no mid-run user pause).
3. Upsert index rows from readback; run `lint_unattended_card_truth_ready.py`
   (see `unattended-card-truth-batch-gate.md`).
4. Continue solvable engineering, E2E, and freshness-gated vision.

Do **not** claim “unattended Delivery closed UIT/RB truth” without App readback
apply in that wave (`card_truth_delivery_claim_without_apply`). External-only
blockers (App unreachable, missing field-media) may set
`card_truth_batch_gate.status: blocked` — not “defer because unattended.”

Task **retrospective review cards** (learning/taste) remain
`subjective_acceptance`; RB/UIT archived-reference cards do **not**.

## External Capability Inventory (ask early)

Before treating an unattended run as fully scheduled—and again immediately when
the user **switches into** unattended—run a one-time **External Capability
Inventory** against product docs + Project Work + planned milestones. Cover at
least:

| Class                     | Examples                                                            |
| ------------------------- | ------------------------------------------------------------------- |
| Secrets / login           | API tokens, OTP, vendor console login, recovery codes               |
| Payment                   | IAP, billing, bank / merchant human approval                        |
| Push / publish / deploy   | store submit, production deploy, remote push, public messaging      |
| Destructive Git / history | force-push, hard reset, rewrite published history                   |
| Human / device gates      | App Store review, physical device, government / offline third party |
| E2E visible window (UI)   | OS/app display for `e2e_campaign` (`window_capability`)             |

For **software UI** whole-project unattended runs, also record in the inventory
(and optionally SoT risks) that final-delivery E2E **requires**
`window_capability: available`. This is an early demo/ops preflight hint—not a
new mid-run confirmation. Missing display still fails closed later as
`e2e_campaign_window_required` (see `granoflow-e2e-test-campaign`).

For each class, record one disposition in Project Work / run ledger (and in a
milestone authorization manifest when that runner path is used):

- `granted` — user authorized the class for this run; credential **reference**
  only (never persist secret values);
- `excluded` / `not_required` — evidence shows the product/run does not need it;
  later work must not reopen an interaction wait for that class without new
  evidence;
- `interaction_required` — needed but not yet authorizable; batch **all** such
  classes in **one** early ask before deep milestone execution when possible.

**Do not** discover these classes for the first time mid-implement when a
document scan at unattended entry would have shown them. Early inventory is a
hard scheduling gate for unattended portfolio runs; skipping it fails closed as
`external_capability_inventory_skipped` when a later residual proves the class
was knowable from docs/Project Work at entry.

Ordinary Agent-selectable defaults (App icon, stack recommendations already in
Project Work, Baseline `auto_accept_recommendation`) are **not** inventory
classes—handle them under § Explicit Unattended Declaration item 2.

## Late discovery: park at the end, never block the queue

If an external / forbidden class is discovered **after** unattended entry
despite inventory (or truly emerges only from implementation evidence):

1. Immediately append `deferred_external_work` with `id`, `title`,
   `blocker_class`, `evidence`, and `resume_condition`.
2. **Do not** freeze sibling tasks, later milestones, IT/E2E campaigns, or
   other solvable work.
3. **Schedule late:** prefer completing all remaining solvable milestone work
   (Scheme 1: all Analysis→Plan + pack accept → Implement) and then
   `integration_campaign` / `e2e_campaign` before spending interaction budget
   on the deferred class.
   Surface it in the closing **Unattended Residual Report** (and any end-of-run
   dry-run prep) rather than interrupting the middle of the queue.
4. **Local hard dependency only:** when a single task's Outcome is impossible
   without that class, mark **that task** (or its dependent node) deferred /
   interaction_required and continue every independent task. Never escalate to a
   portfolio-wide stop.
5. Still fail closed on impersonation, inventing credentials, or claiming
   external work done without evidence.

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

## Task / milestone acceptance = checkbox (hard)

Universal closeout lives in `task-and-milestone-acceptance-layers`. In
unattended mode, AI self-recommend on the task artifact **is** confirmation
(`unattended_auto_adopted`)—the **same wave** **Must** complete the App task
(`status=done`). For milestone Layer B, run
`lint_milestone_child_done.py --claim-passed` in the same wave. Do not treat
suite green, Delivery upload, or a Closing Summary alone as closeout while a
task or in-scope sibling stays `pending`.

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

### Schedule under unattended

Unattended **implies** `schedule_policy.kind: unattended_milestone_loop`
(see `project-lifecycle-progress-board` **Schedule Policy**). Do **not** ask
the user to choose `breadth_first` / `depth_first` / `unset` (retired).

When the user (or an approved grant) **enters or switches into** unattended:

1. Set `interaction_mode: unattended` and
   `schedule_policy.kind: unattended_milestone_loop` for remaining work.
2. Do not redo completed Analysis/Plan/Implement evidence.
3. Run the **Unattended Entry Continuity Checklist** in
   `long-task-run-continuity` **in the same wave**: load continuity +
   `project-e2e-sot`; create/update `temp/project-e2e-sot-v*.md` with concrete
   `next_step`; probe Layer B (activate if available); **Must probe** Layer C
   and **arm** when available with the canonical wake payload bound to the SoT,
   or emit `host_wake_unavailable_notice` with the canonical resume prompt when
   unavailable/unknown. Expand the SoT after portfolio ready
   (`project-e2e-sot.md`).
4. Asking solely to enable host Plan mode fails closed as
   `collaborative_planning_surface_confirm_in_unattended`. Wake without a bound
   `next_step` is not a valid unattended schedule
   (`host_wake_prompt_missing_next_step` /
   `host_wake_unbound_from_run_plan`).

**Scheme 1 schedule:** Under `pipeline_continue` / long-run / 「继续」 /
host-wake tick, for the current milestone: complete **all** in-scope
Analysis→Plan (定稿 Analysis opens Plan; `gf析` may stop only before 定稿) →
accept the milestone Plan acceptance pack → **then** milestone Implement
(Layer A + Layer B). **Forbidden** to Implement any child before the pack is
`accepted`. Then open the next milestone’s Analysis. After all feature
milestones finish that pattern, run `integration_campaign` then
`e2e_campaign`.

### Prototype links under unattended

Whenever HTML prototypes are authored (Design Baseline screens/Shell units or
task `ui_prototype`):

1. After **each** prototype becomes previewable, emit a **clickable** preview
   link as a non-blocking notice and append it to `prototype_link_ledger`.
   Each ledger entry **Must** include:
   - `title` (plain-language label);
   - `absolute_path` (resolved filesystem path);
   - `file_url` (`file://…` via absolute path, same bar as Plan Acceptance
     HTML links — e.g. `Path.resolve(...).as_uri()`);
   - `entity` / `sha_or_pending` as applicable.
     Relative paths, bare filenames, or prose-only location hints fail closed as
     `prototype_link_not_absolute` / `prototype_link_incomplete`. Chat notices
     and digests Must use Markdown links of the form
     `[title](file:///absolute/path/...)`.
2. Do not wait mid-run for visual taste confirmation.
3. Project Definition Design Spec / Shell under unattended: author **one**
   faithful `spec_match` **Style Guide / Design Tokens board** (not a
   journey-screen gallery) via `draw_visual_lots.py` **true-random** draw, then
   **one** `shell_match` that **embeds that Spec’s tokens** and is product-near
   (not wireframe-only; no independent palette seed)—do **not** run interactive
   triads or AI challengers. Journey/critical screens beyond the Shell’s primary
   surface belong in the Baseline package after Spec+Shell. After Baseline
   confirm, write `widgets.yaml` from that confirmed Baseline prototype.
4. At **every Analysis turn end** that authored or updated prototypes, emit a
   short Prototype Link 小结 listing those absolute `file://` links (in
   addition to mid-run notices). Persist the ledger on Milestone Work, run
   continuity, or `temp/` so links survive chat truncation.
5. At run close, emit a mandatory **Prototype Link Digest** that lists every
   ledger entry with clickable absolute `file://` links so the user can audit
   all prototypes in one place. Omitting the digest fails closed as
   `prototype_link_digest_required`. Persist
   `granoflow_prototype_link_ledger_v1` and run
   `lint_prototype_link_ledger.py --require-complete` before UI Analysis
   confirmation; missing/empty HTML → `prototype_link_file_missing`.
6. **Plan Entry:** before soft-merge / `plan` / `run` enters Planning on a UI
   task, run `lint_plan_entry_prototype_acceptance.py`. Non-UI
   (`prototype_requirement: not_required` / N/A) skips. UI Must have the
   auditable digest first; under unattended, record
   `prototype_plan_entry_acceptance` with
   `acceptance_source: unattended_auto_accept` **only after** that digest is
   green—never auto-accept without parent-chat-auditable `file://` links.
   Fail closed `plan_entry_prototype_acceptance_required` /
   `plan_entry_prototype_unconfirmed`.
7. Interactive mode (default when unattended was not declared) uses the
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
   option enums). Absolute `file://` links remain mandatory in interactive mode
   too.
8. Task / milestone `ui_prototype`: inherit locked Spec + Shell; **no** random
   visual seed (`task_prototype_seed_forbidden`); reuse `widgets.yaml` when the
   same role exists (`widget_reuse_required`); pass Craft Gate before confirm
   else `task_prototype_craft_incomplete` (including Baseline fit →
   `prototype_baseline_fit_*` / `prototype_generic_phone_frame`, product truth →
   `prototype_product_truth_violation` and user-visible copy boundary →
   `user_visible_copy_boundary_unread` /
   `user_visible_copy_boundary_violation`); keep design-first; high-risk UI needs
   feasibility conclusion before Readiness
   (`high_risk_feasibility_unresolved`).
   - **Unattended:** load `prototype-baseline-fit`,
     `prototype-expression-brainstorm`, and `prototype-serial-revision`.
     Mainstream-first → promote **one** Baseline-fitted `expr_a` thesis; run
     review-only gstack/preferred reviewers + grill **self-QA** (no user
     interview); serial multi-draft up to 5; auto-adopt final green; residual
     blocking at cap → `prototype_revision_blocking_residual`. Lint
     `lint_prototype_expression_brainstorm.py` and
     `lint_prototype_revision_ledger.py`. No Design System reopen.
   - **Interactive (default when not unattended):** same serial pipeline with
     strict Spec/Shell fit + confirmed sibling chrome vocabulary; selection
     surface = last ≤3 drafts with **推荐**; single draft =
     `confirm_or_revise` (detail revise notes open the next draft inside the
     5-cap). Never re-offer Design Spec labels as task options; never ship
     generic parallel phones or invent a parallel chrome dialect after
     siblings are confirmed
     (`prototype_option_design_system_reopened` /
     `prototype_baseline_fit_*` /
     `prototype_generic_phone_frame` /
     `prototype_shell_chrome_mismatch` /
     `prototype_confirmed_chrome_lock_*` /
     `prototype_option_brainstorm_*` /
     `prototype_option_mainstream_skip` /
     `prototype_option_scope_mode_invalid` /
     `prototype_option_promote_count_mismatch` /
     `prototype_revision_*`).

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
- destructive Git / history rewrites not pre-granted in the early inventory;
- Note/Card creation/link/modify that still needs human study-judgment over the
  latest preview—prepare dry-run at the end, then list as residual rather than
  blocking engineering tasks mid-run.
  Review Note/Card authoring is also excluded from unattended authorization.
- any action whose success cannot be evidenced without an external human step.

Do not use “forbidden_action” as a mid-run freeze of the whole portfolio when
sibling solvable work remains. Prefer the **Late discovery** scheduling rule:
keep the deferred class at the end of the solvable queue unless a single task
has a hard local dependency.

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

### Long-task run continuity (required on implement / unattended entry)

Unattended full-pipeline completion needs **three** portable layers (see
`long-task-run-continuity.md`). This contract owns **Auth** only:

| Layer | Portable name                             | Owner                                          |
| ----- | ----------------------------------------- | ---------------------------------------------- |
| Auth  | ask-budget / continue / defer / residual  | **this file**                                  |
| A     | Project E2E SoT / durable run plan        | `project-e2e-sot` + `long-task-run-continuity` |
| B     | Collaborative planning surface (optional) | `long-task-run-continuity`                     |
| C     | Host wake surface (when to re-enter)      | `long-task-run-continuity`                     |

**Host wake alone is not enough.** A robust recurring tick that only says
「继续」 without reading SoT `next_step` is not a successful unattended
delivery path—it fails closed under
`host_wake_prompt_missing_next_step` /
`host_wake_unbound_from_run_plan` in `long-task-run-continuity`.

When **entering unattended** (grant or mid-run switch), and again before
unattended **implement** / campaign work that is long (milestone-wide or
multi-task), execute the **Unattended Entry Continuity Checklist** in
`long-task-run-continuity.md` (load + SoT + Layer B/C probe/arm or
`host_wake_unavailable_notice`). That SoT file is the portable continuity
surface. Do not treat chat wake as proof that `granoflow-gfmcp-runner` or
another external worker is running.

Asking the user solely to enable a host-local planning UI fails closed as
`collaborative_planning_surface_confirm_in_unattended`. Missing or stale SoT
fails as `long_run_plan_missing` / `project_e2e_sot_missing` /
`long_run_plan_stale` / `project_e2e_sot_stale`. Wake misuse codes
(`host_wake_*`, including `host_wake_unavailable_notice` as a non-blocking
notice) are owned by `long-task-run-continuity`.

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
- `subjective_acceptance`: task retrospective review cards, taste/legal gates —
  **not** RB/UIT anti-drift archived-reference apply (those Must auto-apply in
  unattended);

`blocker_class: subjective_acceptance`

- `direction_change` / `scope_drift`: only when the item itself cannot be
  safely auto-resolved—even then, prefer adopting the recorded recommendation
  for solvable siblings; park only the contested item when possible.

## Parallel Batch Merge Review (unattended)

When a concurrent task batch finishes under
`granoflow-agent-workflow/parallel-task-execution`:

1. Load `parallel-batch-merge-review` and write
   `temp/parallel-batch-<batch_id>-review-v<n>.md` (+ HTML links as notice).
2. Auto-adopt only when lint is green, `pairwise_recheck: parallel_safe`, every
   worker has Delivery readback evidence, and Host Concurrency Policy was
   obeyed. Record `decision_authority: unattended_grant` /
   `accepted_by: unattended_grant`. Never present this as user acceptance.
3. On lint failure, write conflict, `host_isolation_unavailable`, or
   `parallel_host_shared_write_forbidden`: **park that batch** (or the
   conflicting workers) in `deferred_external_work` / Residual with resume
   condition (serialize, isolate worktree, or replan). **Do not** freeze sibling
   independent `parallel_safe` batches or later milestones.
4. Single-writer merge + post-merge gates run only after auto-adopt
   `status: accepted`.

Same-tree `shared_write` fan-out remains forbidden even under unattended grant.

## Complete With Residuals

When no solvable ready work remains, set
`interaction_decision: complete_with_residuals` and emit the
**Unattended Residual Report**.

**Hard residual filter** (see `task-and-milestone-acceptance-layers.md`):

- Allowed leftovers: host/OS `blocked_external`, pixel/Baseline manual visual,
  external-device handoff (`tested: false`), true publish/device/card gates the
  grant cannot satisfy.
- **Forbidden** leftovers: unfinished SoT features, stub delivery surfaces,
  user-visible “后续版本提供” / “将在后续版本” deferral copy, matrix rows left
  `pending` while claiming task/milestone done. Those are **still solvable** —
  keep implementing and testing, or fail closed as
  `functional_residual_forbidden` / `feature_completeness_matrix_incomplete`.
  Do **not** use `complete_with_residuals` to declare the declared feature
  scope complete while they remain.

```markdown
## Unattended Residual Report

- Scope: <declared unattended scope>
- Completed: <count / summary refs>
- Feature completeness: <per-milestone matrix status; all in-scope green or
  only allowed blocked_external rows>
- Prototype Link Digest: <clickable absolute file:// links for every HTML
  prototype authored; required when any prototype was produced;
  relative-only paths are not enough>
- Plan Acceptance Link Digest: <clickable HTML/Markdown pack links authored this
  run; required when any Plan acceptance HTML was produced>
- Parallel Batch Review Digest: <clickable HTML/Markdown
  `temp/parallel-batch-*-review-v*.md` links; required when any concurrent batch
  ran; note auto-adopted vs parked batches>
- Acceptance layers (when any task/milestone closed this run):
  - Layer A 单任务完成: <per-task Delivery / acceptance_report refs>
  - Layer B 里程碑集成验收: <Suite Plan order / IT green|residual / matrix / Experience / 任务回顾>
  - Do not fuse into one unlabeled “all done” list (`acceptance_layers_fused`)
- Deferred / not executed (allowed classes only):
  1. <title> — <blocker_class> — <why external> — <resume_condition>
  2. ...
- Explicit statement: these items were **not** executed in this unattended run;
  no functional stubs were parked as residuals.
```

A run with residuals is a successful unattended completion of everything
solvable—not a fake all-green project. Never claim deferred publish/device/card
work as done. Never claim feature completeness while SoT behaviors remain
stubbed.

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
