# Milestone AI Review

Use this contract for requirement-driven or software Milestones before task
creation, when reopening a Milestone for changes, and before final Milestone
plan acceptance.

Historical schema v1 task plans remain readable. Reopening one to change its
tasks, dependencies, acceptance, screens, or responsibilities, or continuing
child-task creation, requires upgrading it to schema v2 and completing this
review.

## Ownership

- This reference owns Milestone AI review, reviewer-provider orchestration,
  evidence accounting, deterministic plan digests, Final Verifier rules, and
  the final Grill Me acceptance sequence.
- Milestone coordination, portfolio orchestration, task authoring, requirement
  intake, Task Work, and delivery skills only route into this contract.
- A review report is evidence. It never replaces Project Work, requirement
  ledger, Task Work, or the Milestone Plan Acceptance Pack as a source of truth.
- No review, verifier, finalizer, Grill Me, or acceptance result grants
  implementation, commit, push, publish, or deploy authorization.
- For UI work, the reviewed plan binds the current platform matrix digest.
  Changing supported versions, required layout families, screen ownership, or
  Prototype Bundle responsibilities invalidates the Milestone review and
  downstream Acceptance Pack.

## Stage Review Routing

All external reviewers are `preferred_method`. When unavailable, use a native
reviewer with explicit evidence and record `native_fallback`; absence never
creates authorization.

| Stage                     | Default reviewers                                        | Conditional reviewers                                                        |
| ------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `project_definition`      | `prd-review`                                             | office-hours or CEO reviewer for strategy, market, or product-risk questions |
| `milestone_decomposition` | `prd-review` plus engineering reviewer                   | CEO for product bets, design reviewer for UI scope, CSO for high-risk scope  |
| `analysis`                | `prd-review` for product work; `investigate` for defects | CSO for high-risk work                                                       |
| `planning`                | engineering reviewer                                     | design reviewer for UI; CSO for high-risk work                               |
| `delivery` and `review`   | code review plus QA                                      | `design-review`, `benchmark`, CSO, or `canary` when their conditions apply   |

`prd-review-skill` is the installation collection id. The runtime skill id is
`prd-review`. `gstack-autoplan` is `explicit_only`; it must not become a second
workflow controller.

## Task Plan Schema v2

`task_plan.review` records:

```yaml
mode: ai_auto
roles:
  author: author
  reviewers: [prd-review, engineering-reviewer]
  final_verifier: final-verifier
providers:
  - capability: prd-review
    disposition: selected # selected | native_fallback | not_required
    result: used # used | model_fallback | not_required
    evidence_ref: ""
grill:
  generated_question_count: 0
  closed_question_count: 0
  open_blocking_count: 0
ai_review_status: pending # pending | passed | failed
final_verifier_status: pending # pending | passed | failed
reviewed_plan_sha256: ""
```

Author, reviewers, and Final Verifier must be logically distinct roles. Every
required provider must finish or have an evidenced native fallback.

## Decomposition Review Sequence

1. The author generates a candidate task plan.
2. PRD and applicable gstack specialist reviewers inspect the candidate.
3. Granoflow generates Grill questions in a batch, then automatically
   adjudicates and closes them one by one.
4. An independent Final Verifier checks scope, responsibilities, dependencies,
   acceptance, screens, evidence, and open findings.
5. Compute and compare the canonical digest.
6. Set `ai_review_status: passed` only after every gate passes.

Do not run `grill-finalizer` during decomposition because it writes a temporary
acceptance candidate and would trigger final interaction too early.

The canonical digest is SHA-256 over canonical JSON for `task_plan` after
removing only the top-level `review` property. Object keys are recursively
sorted and JSON uses compact separators. A change to tasks, dependencies,
acceptance, screens, responsibilities, or any other reviewed plan content
invalidates the prior review.

The decomposition gate fails closed unless:

- schema is v2;
- every selected provider has evidence, or an evidenced native fallback exists;
- generated Grill questions equal closed questions;
- open blocking findings equal zero;
- the Final Verifier passed;
- the recorded digest equals the current canonical digest.

Passing this gate permits child-task creation and subsequent Analysis and
Planning only.

## Final Acceptance Sequence

After child-task Analysis and Planning are complete:

1. Build the Milestone Plan Acceptance Pack candidate with the AI decomposition
   review reference and reviewed digest.
2. Run `grill-finalizer`.
3. Persist the temporary candidate.
4. Run `grill-me` against that same digest.
5. Record acceptance for that digest.
6. Promote the pack and read back its App hash.

In interactive mode, `grill-me` asks one question at a time and waits for the
user. Record `grill_me_status: shared_understanding_confirmed`,
`final_acceptance_status: user_accepted`, and `accepted_by: user`.

In unattended mode, `grill-me` still states each question, recommendation, and
reason one at a time. The AI adopts the recommendation without waiting and
records `grill_me_status: recommendations_auto_adopted`,
`final_acceptance_status: unattended_auto_adopted`, and
`accepted_by: unattended_grant`. Never represent this as user acceptance.

In both modes, record `authorization_effect: none`. Execution still requires
the existing independent `execution_authorization` and user-facing `run`.

## Fail-Closed Codes

- `milestone_ai_review_required`
- `milestone_ai_review_blocking_findings`
- `milestone_ai_review_verifier_failed`
- `milestone_ai_review_plan_digest_mismatch`
- `milestone_final_grill_me_required`
- `milestone_final_acceptance_required`
- `milestone_final_acceptance_digest_mismatch`
