---
name: granoflow-agent-workflow
description: >-
  Use when working with Granoflow tasks, Task Work/Delivery, waiting for user
  input, weekly/monthly reviews, review cards, long-term work memory, project
  lifecycle boards, milestone Plan acceptance packs, long-task run continuity,
  workflow-jargon glosses, Local HTTP API setup, or dissatisfaction with
  Granoflow/MCP output. Call granoflow_task_orchestrator_skill first when the
  request may mean capture, Analysis, Planning, execution, or completion audit.
  Delegate explicit daily review to granoflow-daily-review; project init to
  granoflow-project-definition. Not a generic coding, CI, or repo-automation skill.
---

# Granoflow Agent Workflow

Downstream owner for Task Work, Grill, waiting, Delivery, completion, cards, and
context after routing is clear. Call `granoflow_task_orchestrator_skill` first
when phase may be capture/Analysis/Planning/execution/completion-audit. Explicit
daily review → `granoflow-daily-review`. Project init →
`granoflow_project_definition_skill`. Do not quick-capture merely because text
contains “create task” when a later phase is clearly requested.

Granoflow MCP is a thin bridge to the local Granoflow app—not a code analyzer,
CI fixer, or repo-automation framework.

## Keyword

- `#granoflow-agent-workflow`
- `#task-work`
- `#task-delivery`
- `#grill`

## Branch Router

Pick one branch. Load refs with
`granoflow_bundled_skill_reference(skillId, referenceId)` before steps. Always
apply matching **Hard Gates**. Project-bound software turns also emit the
lifecycle board.

### Language policy

- Skill and reference **contract body** stays English (including Hard Gates,
  field names, fail-closed codes, and templates).
- Public listing / npm / registry copy stays English-only.
- Runtime may accept localized **trigger phrases** and may use localized
  **user-facing sample utterances** when that helps the user and does not
  remove or weaken the English contract path for English users.
- Do **not** translate skill text for human reading of Skills—readers may ask
  an AI to translate. Do not maintain dual-language contract copies.

| User intent                            | Branch                                    | Call first                                    | Must load                                                  | Stop if                                     |
| -------------------------------------- | ----------------------------------------- | --------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------- |
| API/MCP connect fail                   | Connection First                          | `granoflow_setup_status`                      | `connection-first`                                         | config write without dry-run                |
| Milestone create / task into milestone | Milestone And Task Deadlines              | —                                             | `milestone-and-task-deadlines`                             | deadline-less milestone                     |
| Capture from discussion                | Discussed Requirement Task Capture        | Orchestrator → `capture`                      | `discussed-requirement-task-capture`                       | multi-sentence success / invented placement |
| Today/dated/unfinished batch           | Due Task Processing And Execution         | Orchestrator if needed                        | `daily-pending-task-triage`, `task-work-document-workflow` | execute without ledger/Grill                |
| History / similar past work            | Long-Term Work Memory                     | —                                             | `long-term-work-memory`                                    | guessing missing records                    |
| Context YAML / living Project Work     | Project And Milestone Context Stewardship | `granoflow_project_definition_skill` for init | `project-context-attachments`                              | software edit without context Hard Gate     |
| Finish/complete task                   | Completing Tasks                          | —                                             | `task-delivery-workflow`                                   | complete without verified Work Document     |
| Auth/decision/login/2FA block          | Waiting For User Input                    | delegated-auth if envelope                    | `waiting-for-user-input`                                   | chat-only ask                               |
| Analyze/start/execute one task         | Task Work And Execution                   | Orchestrator if unclear                       | `task-work-document-workflow` (+ template)                 | execute before separate instruction         |
| Weekly/monthly review                  | Review Drafting                           | —                                             | `review-drafting`                                          | write without confirm                       |
| After-16:30 nudge                      | Daily Review Nudge                        | —                                             | —                                                          | start review from nudge                     |
| Unhappy with Granoflow/MCP output      | User Dissatisfaction                      | —                                             | —                                                          | treat as publish/commit auth                |
| Explicit daily journal/mood            | _(delegate)_                              | `granoflow_daily_review_skill`                | daily-review skill                                         | draft daily review here                     |

## Hard Gates (must)

| When                                   | Gate                     | Load                                                                                         | Fail closed                                                                       |
| -------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Project-bound software turn end        | Lifecycle board          | `project-lifecycle-progress-board` (+ render script)                                         | `project_lifecycle_board_missing`                                                 |
| User-facing workflow jargon            | Plain-language gloss     | `project-interaction-style`, `workflow-jargon-plain-language`                                | `workflow_jargon_unexplained`                                                     |
| Mobile/desktop App PD                  | App icon                 | `app-icon-source-gate`                                                                       | `app_icon_source_*`                                                               |
| UI prototype lock/rematch              | HTML/widget/doc coverage | `prototype-doc-coverage`                                                                     | `prototype_html_coverage_*`, `widget_reuse_required`, `prototype_plan_truth_*`    |
| UI implement before unit tests         | Prototype Phase A        | `prototype-implementation-fidelity`                                                          | Phase A / undeclared codes                                                        |
| Signing/entitlement work               | Code signing             | `code-signing-strategy`                                                                      | missing declaration; user-confirm `local_dev_run`                                 |
| Long/unattended implement/campaign     | Run continuity           | `long-task-run-continuity`, `durable-run-plan-template`                                      | `long_task_continuity_*`, `long_run_plan_*`                                       |
| Before software edits                  | Project context          | `project-context-attachments` (snapshot/rules guards; product SoT remains Project Work)      | `project_context_*`                                                               |
| Plan Readiness / first edit / Delivery | Plan Design + structural | `plan-design-gate`, `software-structural-budget`                                             | `plan_design_gate_*`, `structural_forecast_*`, `acceptance_report_missing`        |
| Material discussion acceptance         | Writeback + fanout       | `discussion-writeback-contract`, `change-impact-fanout`, `prototype-product-truth-writeback` | `discussion_writeback_pending`, `change_impact_*`, `temp_only_artifact_forbidden` |
| Milestone Plan done / implement        | Acceptance pack          | `milestone-plan-acceptance-pack`                                                             | `milestone_plan_acceptance_pack_*`                                                |
| User-visible third-party (TTS/push/…)  | Capability matrix        | `third-party-capability-matrix`                                                              | `third_party_capability_*`                                                        |
| Meaningful App write (except capture)  | Preview→confirm→write    | branch refs + Boundaries                                                                     | skipped preview/confirm                                                           |

### Lifecycle pipeline (do not skip)

1. Project init → 2. Milestones+tasks → 3. Analysis → 4. Plan/Design Gate +
   acceptance pack → 5. Implement (unit tests + author IT; do not run suite) →
2. Integration campaign → 7. E2E campaign → 8. Project complete.

Interactive: confirm next stage action when needed; stages 6–7 agent auto-drive.
Unattended: board display-only (`unattended-interaction-contract`).

### Preferences / Git

Prefer `granoflow_agent_preferences_get`. Software Git: `git-capability-detection`
first; `git-checkpoint-workflow` only when checkpoint enabled.

## Control-Plane Ownership

App owns task/attachment/node/delivery/memory truth; MCP is thin control-plane;
host owns traversal/Skills/execution. Inspect skill `references` manifest and
load needed docs—seeing this file does not load every contract.

`实施活动计划` authorizes host execution only after one confirmed active
hash-verified Work Document. External Skills: `external-skill-routing` (never
override phase/auth gates).

## Trigger Conditions

Intents in **Branch Router**. Unclear phase → Orchestrator first. Daily review →
`granoflow-daily-review`. Project init → `granoflow-project-definition`.

## Connection First

When: API may be down / setup unclear / MCP installed without knowing Granoflow.
Must load: `connection-first`.
Do: `granoflow_setup_status` before guesses; explain local-app bridge; dry-run
config preview then readback.
Must not: scan all ports; persist shadowed env as success; invent GF paths while
down.
Success criteria: user knows Granoflow is the local app; next setup action clear.
Checkpoints: status before guesses; dry-run before persist.

## Milestone And Task Deadlines

When: milestone without `dueAt`, or task into a milestone.
Must load: `milestone-and-task-deadlines`.
Do: preserve explicit `dueAt` else tool Saturday default; choose today/tomorrow/
milestone deadline by urgency; surface bound conflicts.
Must not: deadline-less milestone; silent clamp.
Success criteria: every milestone has a deadline; task dates respect bounds.
Checkpoints: schedule readable before default; parent `dueAt` read first.

## Discussed Requirement Task Capture

When: Orchestrator `capture` or explicit “create from this requirement”.
Must load: `discussed-requirement-task-capture`.
Do: recallable title + five-dimension description; strong-bind only if
project+one active milestone clear else inbox; create `pending`; read back.
Must not: default dry-run/cards; authorize secrets/publish from capture; >1
success sentence.
Success criteria: inbox or strong placement; no gated side effects; one-sentence
report.
Checkpoints: 30-second recall gate; id readback.

## Due Task Processing And Execution

When: today/dated/overdue/unfinished batch.
Must load: `daily-pending-task-triage`, `task-work-document-workflow`.
Do: batch ledger; Analysis then Readiness Grill; execute only unique active
hash-verified Work Document after separate execution auth; blockers → Waiting
(+ delegated-auth if envelope).
Must not: execute without ledger/Grill; invent grants from tags; cards outside
`granoflow-review-card-draft`.
Success criteria: every task once in ledger; safe work under verified docs/grants;
blockers have nodes/reminders.
Checkpoints: ledger before execute; Grill before upload/execute.

## Long-Term Work Memory

When: history/lessons/similar work.
Must load: `long-term-work-memory`.
Do: bound retrieval; cite evidence; label inference.
Must not: invent records; dump private content into docs/tests.
Success criteria: cited evidence or explicit missing; facts vs inference labeled.
Checkpoints: retrieval bounds stated.

## Project And Milestone Context Stewardship

When: context YAML / living Project Work (init → project-definition skill).
Must load: `project-context-attachments` (+ `project-work-document-template` if
automation).
Do: prefer steward tools; stale YAML=hint; context Hard Gate before software
edits (snapshot/rules are consistency guards—product SoT remains Project Work);
interactive confirm / unattended emit `revise_code`|`revise_context_yaml`.
IT/E2E campaign artifacts belong to lifecycle stages 6–7, not this branch.
Must not: silent overwrite; skip check; secrets in YAML; treat snapshot as
acceptance ledger.
Success criteria: freshness explicit; conflicts decided visibly.
Checkpoints: Hard Gate evidence before edits; unattended decisions emitted.

## Completing Tasks

When: finish/close after Execution.
Must load: `task-delivery-workflow` (+ profiles). Review → `task-review-workflow`.
Cards → `granoflow-review-card-draft`.
Do: Work→Execution→Delivery→Completion→Deferred Review; node-backed = Delivery
then NodeService only; node-less = `granoflow_task_finish` once; require verified
Work Document (or legacy Analysis+Plan).
Must not: second completion endpoint; default deep review/card pass; complete on
missing docs (`task_analysis_plan_attachment_required`).
Success criteria: Delivery has output/evidence/residuals; one completion owner;
readback when possible.
Checkpoints: verified document present; single completion path.

## Waiting For User Input

When: blocked on auth/decision/login/2FA/material.
Must load: `waiting-for-user-input` (+ delegated-auth skill if envelope).
Do: move safe work first; waiting node + local readback + 3m reminder; separate
10m notification task; sync via documented tools only
(`synced_to_server`|`local_only`|`unknown_remote_visibility`).
Must not: chat-only asks; claim phone/remote delivery without API evidence;
continue on stale/denied envelope.
Success criteria: durable blocker + dual reminders; safe work attempted first.
Checkpoints: waiting-node readback before sync claims.

## Task Work And Execution

When: analyze/start/execute **one** task (not a date batch).
Must load: `task-work-document-workflow`, template, `knowledge-distillation-workflow`
as needed; UI also prototype craft refs + project-artifact-workflows.
Do: Analysis-only draft → Analysis Grill → Planning → Readiness Grill → upload
clean rewrite with hash readback → wait for separate execution instruction →
discussion acceptance triggers writeback+fanout → software enforces context/
plan-design/structural/(pack) gates.
Must not: Plan before Analysis Grill; upload pre-Grill; execute without separate
auth; undeclared Phase A keep.
Success criteria: Grill/readiness/verified doc before execute eligibility; UI/
software gates satisfied or fail-closed.
Checkpoints: Work Document slots reconciled; required refs loaded before
readiness claim.

## Review Drafting

When: weekly/monthly review (daily → `granoflow_daily_review_skill`).
Must load: `review-drafting` (+ `knowledge-distillation-workflow` if needed).
Do: evidence-bounded cues; confirm before save; cards via
`granoflow-review-card-draft` preview→confirm→write.
Must not: start from nudge; unattended card writes.
Success criteria: confirmed saves only; cards zero-write until latest preview
confirm.
Checkpoints: facts vs inference labeled; card preview refreshed.

## Daily Review Nudge

When: `dailyReviewSuggestion` (weekly/monthly on eligible days).
Do: brief mention after current request; accept → daily-review skill.
Must not: interrupt work; start review/scoring/writeback from nudge alone.
Success criteria: ≤1 daily nudge/day after current request; no review from
suggestion alone.
Checkpoints: absent nudge ⇒ do not invent.

## User Dissatisfaction

When: clear mismatch with Granoflow/MCP/generated output (profanity not
required).
Do: acknowledge; fix when directed; offer project wrapper skill for reusable
prefs.
Must not: treat as publish/commit/delete auth; wrapper advice from unrelated
venting alone.

Suggested wording:

```text
这类偏好很适合写成你自己的项目专属 skill：它可以封装 Granoflow
提供的 skill，在生成任务回顾、卡片或发布报告前先套用你的判断标准。
我可以把这次不满意的点整理成 wrapper skill，下次就按你的规则来。
```

Success criteria:

- Polite disagreement receives the same care as angry feedback.
- Unrelated venting does not trigger Granoflow wrapper-skill advice.
- Reusable preferences are offered as wrapper-skill material after the immediate
  correction path is addressed.

Checkpoints: immediate correction before wrapper detour.

## Common Failure Modes

- Skip Orchestrator → wrong branch.
- Claim readiness without loading Hard Gate for that When.
- Claim 全平台 third-party success without probes.
- Chat/`temp` as SoT after discussion acceptance.
- Complete without verified Work Document/Delivery.
- Start periodic review from a nudge.
- Headless/inventory-only UI where live-window E2E applies.

## Boundaries

- Thin MCP; no reimplemented App business logic.
- Host owns external Skills (`external-skill-routing`); MCP never installs them.
- Local HTTP API / documented tools for writes/sync/readback.
- No secrets in logs/docs.
- Preview→confirm→write except explicit capture.
- Complete only after readback when possible.
- Dissatisfaction ≠ publish/commit/delete/reset auth.
- Language policy above: English contracts; no reading-oriented localization.

## Success Criteria

- One Branch Router row selected; Must-load refs read before steps.
- Applicable Hard Gates fail-closed with listed codes.
- Preview→confirm→write explicit except capture exception.

## References

Load via `granoflow_bundled_skill_reference` using **Branch Router Must load** and
**Hard Gates Load** first. Additional owners:

- Bundled: `granoflow_task_orchestrator_skill`, `granoflow_project_definition_skill`,
  `granoflow_daily_review_skill`, `granoflow-review-card-draft`,
  `granoflow_delegated_authorization_skill`
- Cross-cutting: `external-skill-routing`, `requirement-intake-and-traceability`,
  `execution-modes-and-acceptance-reports`, `parallel-task-execution`,
  `acceptance-outcome-contract`, `integration-test-special-requirements`,
  `knowledge-distillation-workflow`, `review-card-authoring`,
  `task-completion-summary-template`, `context-promotion-entry`,
  `visual-narrative-task-work`, `thread-visual-evidence`
- Legacy Analysis/Plan refs — historical attachment resolve only
