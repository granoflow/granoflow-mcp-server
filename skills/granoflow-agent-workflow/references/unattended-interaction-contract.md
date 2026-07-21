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
   Delivery, campaign suite runs on the declared device, project-context
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
confirmation to `auto_accept_recommendation` after exact App import/readback.
If unattended was not explicitly declared, Project Definition stays interactive:
ask → recommend → wait for the user to decide. Soft aesthetic preference is not
a wait-for-user loop under explicit unattended; it never authorizes skipping
interactive confirmation.

### Prototype links under unattended

Whenever HTML prototypes are authored (Design Baseline screens/Shell units or
task `ui_prototype`):

1. After **each** prototype becomes previewable, emit a clickable preview link
   as a non-blocking notice and append it to `prototype_link_ledger`.
2. Do not wait mid-run for visual taste confirmation.
3. Project Definition Design Spec / Shell under unattended: author **one**
   faithful `spec_match` with a **random seed**, then **one** `shell_match`
   **fitted to that Spec** (no independent palette seed)—do **not** run
   interactive triads or AI challengers. After Baseline confirm, write
   `widgets.yaml` from that confirmed Baseline prototype.
4. At run close, emit a mandatory **Prototype Link Digest** that lists every
   ledger entry with clickable links so the user can audit all prototypes in
   one place. Omitting the digest fails closed as
   `prototype_link_digest_required`.
5. Interactive mode (default when unattended was not declared) remains: Design
   Spec triad (each option a **different random seed**) then Shell triad
   (Spec-fitted chrome variants only), stop after each triad batch for pick /
   more options (`prototype_preview_review_required` /
   `design_spec_triad_required` / `shell_triad_required` /
   `shell_spec_mismatch` / seed-collision codes if skipped or rules violated).
6. Task / milestone `ui_prototype`: inherit locked Spec + Shell; **no** random
   visual seed (`task_prototype_seed_forbidden`); reuse `widgets.yaml` when the
   same role exists (`widget_reuse_required`); pass Craft Gate before confirm
   (`task_prototype_craft_incomplete` if not).
   - **Unattended:** **one** `delta_match` only (no dual/triple).
   - **Interactive (default when not unattended):** default **two** options
     (`delta_match` + `ai_challenger`) with ≥2 contrast axes; optional third
     only for documented industry-peer deadlock
     (`prototype_option_third_unjustified` /
     `prototype_option_contrast_insufficient` /
     `prototype_option_near_duplicate`).

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
- integration-test **campaign** suite runs on the campaign device;
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
  required gate is green (task-local integration tests remain manual-only
  outside an integration-test **campaign**);
  do **not** run task-local integration tests in unattended flows; humans run
  them.
- starting or checking an allowed local development service or App;
- revising Analysis or Plan wording after a Grill when the revision stays
  inside declared Outcome/Scope;
- producing and reading back Task Work, Delivery, acceptance evidence, nodes,
  attachments, and final task state;
- applying a newly discovered touchpoint already implied by the approved
  outcome and minimum-change budget.

Silence is not required. Report material progress as notices, never as
questions disguised as courtesy.

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
