# Unattended Interaction Contract

This document is the single owner for deciding whether an unattended Granoflow
run may ask the user a question. Read it whenever a user requests unattended,
hands-off, automatic, or no-interruption completion.

## Observable Invariant

After a valid unattended request starts one bounded run, use:

```yaml
interaction_budget: 0
interaction_decision: continue | wait
blocker_class: none | direction_change | scope_drift | forbidden_action | missing_user_only_input | subjective_acceptance
completed_independent_work: []
question_batch_size: 0 | 1
```

`interaction_budget: 0` counts every user-facing request for confirmation,
choice, permission, information, or approval. Status notices, evidence reports,
and a Structural Change Forecast do not consume the budget because they do not
ask the user to act.

Do not repair one observed phrase such as a particular Analysis prompt. Apply
the invariant to the whole run. When target and local-safe scope remain clear,
the unattended decision policy covers Analysis confirmation, Planning
permission, Plan confirmation, Execution authorization, implementation choices,
local tool selection, test repair, deterministic verification, Delivery,
attachment readback, and completion.

For periodic reviews, milestone escalation and archival follow the same
zero-interruption rule but require a notice before action. The notice names the
milestone, deadline classification, title/description signals, linked-task
evidence, recommendation, and next action. A notice is not a question and does
not consume the interaction budget. Continue only when authorization covers the
exact action and milestone, the App exposes the safe capability, and
evidence/readback gates pass. Missing archive capability is a blocker, not
permission to PATCH status or overwrite the final description.

## Current Run Versus Durable Delegation

A user-origin instruction that explicitly asks to run or complete one exact or
unambiguous target unattended is a direct instruction for the same active run.
The host reports the resolved target, repositories, allowed local action
classes, forbidden actions, and stop conditions as a non-confirming notice,
then continues. The same active run does not require an envelope round trip.

Record `authorization_source: same_run_direct` and the source message. At every
phase, consume the direct instruction only when the recommended result remains
inside the original Outcome, Evidence, Scope, Risk, target, repositories, and
local-safe action classes. A Grill pass is evidence for that decision, not
authorization by itself.

When authorization must survive an unattended interval, process restart, or
later host turn, use `authorization_source: durable_envelope`. That path still
requires the confirmed envelope, App-owned attachment receipt, expiry, phase
grants, Plan hash, and deterministic gate validation. Never silently convert a
same-run instruction into durable delegation.

Neither path authorizes publish, deploy, commit, push, deletion, login, payment,
secret or 2FA access, external messages, approved-asset overwrite, irreversible
actions, or scope expansion unless the user separately and explicitly grants
the exact action and the owning workflow allows it.

## Continue Without Asking

Set `interaction_decision: continue` when the Agent can choose a recommended
path without changing what the user will receive or the boundaries they set.
This includes:

- consuming ordinary phase gates through the current unattended authorization;
- choosing implementation details, files, symbols, local tools, and test order
  from repository evidence and the confirmed scope;
- repairing lint, format, type, build, unit-test, and deterministic integration
  failures until the required gate is green;
- starting or checking an allowed local development service or App;
- revising Analysis or Plan wording after a Grill when the revision does not
  change direction, acceptance, scope, risk, or authorization;
- producing and reading back Task Work, Delivery, acceptance evidence, nodes,
  attachments, and final task state;
- applying a newly discovered touchpoint that is already implied by the
  approved outcome and remains inside the declared minimum-change budget.

Silence is not required. Report material progress and changes, but phrase every
ordinary phase transition as a notice followed by continued work, never as a
question disguised as courtesy.

## Real Blockers

Set `interaction_decision: wait` only when at least one class below is proven
from current evidence:

- `direction_change`: alternatives would materially change Outcome, Evidence,
  product behavior, acceptance criteria, architecture, data semantics, or risk,
  and current evidence cannot choose safely;
- `scope_drift`: the required target, repository, module, public contract, data
  model, or action lies outside the bounded instruction;
- `forbidden_action`: progress requires a separately authorized external,
  destructive, secret-bearing, irreversible, publish, deploy, commit, push, or
  communication action;
- `missing_user_only_input`: required credentials, source material, business
  facts, physical access, or another input exists only with the user;
- `subjective_acceptance`: the active acceptance contract genuinely requires a
  human taste, visual, legal, or product judgment that automation cannot prove.

A failed test, incomplete draft, unfamiliar code, ordinary implementation
choice, available local fallback, or preference for reassurance is not a real
blocker. Retry, diagnose, replan, or use the best evidence-backed local option.

## Waiting Behavior

Before waiting, complete all independent safe work. Persist the blocker class,
evidence, affected actions, and resume condition in the existing waiting
workflow. Combine every remaining decision-changing issue into one batched
question with one recommendation and its consequence. Set
`question_batch_size: 1`; never start a sequence of phase-by-phase questions.

If no real blocker remains, `blocker_class` must be `none`,
`question_batch_size` must be `0`, and the run continues through verified
completion.
