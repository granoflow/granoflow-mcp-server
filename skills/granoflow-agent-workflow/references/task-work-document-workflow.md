# Task Work Document Workflow

## Truth layers (must)

- **Project Work** = project **current** product/acceptance truth.
- **Task Work** = this task's **history** and task-local Analysis/Plan contract.
- After any user-accepted **product-truth** change (journeys, screens,
  acceptance, verification mandates, locked product behavior): write back
  **Project Work** in the same batch (`discussion-writeback-contract`). Updating
  only Task Work fails closed as incomplete writeback.
- Implement and fidelity-compare against App **readback** prototype SHA; if Task
  Work refs disagree with App `current`, rewrite refs after writeback before
  Readiness/Execution (`stale_reference_after_discussion`).

Use this owner for every new task Analysis and applicable Planning. Read
`task-work-document-template.md` first. Load other references only after a
specific trigger below fires.

Runtime triggers include `Analyze the first task`, `请分析第一个任务`, and
equivalent requests in the user's language.

Task Work Document is a pre-execution control-plane artifact. Granoflow MCP
provides structured reads/writes and bundled rules; the host Agent owns
reasoning, Skill routing, orchestration, and execution. This workflow does not
add App schema, API endpoints, MCP runtime state, or host filesystem scanning.

When source material contains product requirements or user stories, read
'requirement-intake-and-traceability.md' before Analysis. Treat arbitrary
format and unexpected sections as valid evidence, preserve extra requirements,
surface product-document/user-story omissions and conflicts, and inherit stable
Project Work requirement ids. Do not demand a separate SRS, technical design,
data model, test plan, or Development Plan from an individual developer before
Analysis.

The persisted task description is the user's 30-second recall summary and the
starting source for Task Work. The Work Document is a cold-start execution
manual for an Agent or person who may not have the original thread. It expands
confirmed description facts into reproducible scenarios, scope, actions,
dependencies, verification evidence, and stop conditions. It may repeat the
minimum facts needed for handoff, then add details verified from the Agent
thread, source files, prior plans, or delivery records. It must not merely
paraphrase the description. It must not invent facts. If available evidence is
insufficient, record `待确认` or an explicit unknown and stop before claiming a
complete execution plan.

Author the document in strict phases:

```text
Analysis-only draft -> Analysis confirmation -> MCP-bundled Analysis Grill
-> Planning discussion -> Planning confirmation -> user readiness reminder
-> MCP-bundled Execution Readiness Grill -> attachment upload and hash readback
-> direct execution instruction or a current, valid delegated execution grant
```

Never prewrite the Plan in the initial draft. Neither optional external review
nor a successful upload may skip or reorder these phase gates.

The description and Work Document must each contain at least one concrete
example of the real or plausible case the task addresses. A cold reader should
be able to picture the failure or risk, its affected party, and its consequence;
an internal label or document reference is not an example. If the selected
approach has a meaningful alternative, trade-off, or boundary, the document
must also give one or more concrete examples showing why that approach is
reasonable and why the boundary is set there. Omit this rationale only when the
task has no material choice or boundary to explain.

When a task concerns comics, manga, storyboards, illustration sequences,
animation, video shots, or motion design, load
`visual-narrative-task-work.md` after the generic Task Work owner. It defines
the shared visual-narrative fields and the optional `comic` / `animation` task
modes. It does not replace the generic lifecycle or turn either mode into a
Granoflow `profiles` value.

## Local API Outage And Recovery

If the Local HTTP API becomes unreachable, keep connection facts separate from
host-local draft facts. Report exactly one of:

- `bound_local_draft`: a real local file exists and its task id came from prior
  trusted Granoflow readback;
- `unbound_local_draft`: a real local file exists but its GF task identity is
  currently unverified;
- `no_local_draft`: no local file was created.

When a draft exists, include its real safe path and also report
`upload_blocked_api_unreachable`, `attachment_readback_pending`,
`active_not_established`, and `reconciliation_required`. Never invent a path or
claim that task description, attachment, nodes, or the active pointer changed.
If setup reports `reachable_auth_required`, fix authentication rather than
asking for another port. If it reports `configuration_shadowed_by_env`, explain
the environment override instead of rewriting config.

After recovery, re-read the task, attachments, nodes, and task revision. Resolve
an `unbound_local_draft` to one confirmed task before upload. Reconcile active
versions, hashes, task state, and nodes. Reopen affected confirmation when task
identity, Outcome, Scope, Risk, Decision, or Planning changed. Execution
authorization does not survive an API outage unless a delegated grant is
re-read from its owner attachment and its App-owned receipt is verified after
recovery. Choose the next unused immutable
version with the current revision. Only App-owned content or SHA-256 readback
may establish the active Work Document pointer.

## Resolve And Prefill

Resolve exactly one active task and read the task, current nodes, descriptions,
all Task Work attachments, and available project/milestone context. Reconcile
the two allowed Task Work slots before drafting: `execution` and optional
`post_completion_revision`. Separate confirmed facts,
materials, inference, and unknowns when that distinction can change a core
decision. Use this evidence order:

1. user-confirmed description and current-thread decisions;
2. directly inspected source, screenshots, logs, or runtime state;
3. confirmed prior Analysis, Plan, Delivery, decisions, and project context;
4. labeled inference; and
5. explicit unknown.

A filename, path, title, or completion status proves only that the item exists;
inspect its content before using it as evidence. Do not turn the template into
a blank questionnaire or convert inference into fact to fill a section.

Create one local working copy for the current slot, using
`task-work-<safe-task-id>-execution-v<work_version>.md` while the task is
unfinished. If a completed task already has a post-completion revision, use
`task-work-<safe-task-id>-post-completion-revision-v<work_version>.md` instead.
Only one local version per slot may remain after a successful post-Grill
rewrite. Fill the five core sections and only triggered optional content.
Analysis starts with:

```yaml
analysis_status: draft
analysis_grill_status: not_run
planning_status: not_assessed
readiness_grill_status: not_run
```

At this point render Analysis only. Do not add Recommended Approach, Execution
Plan, Execution Nodes, Verification Plan, Rollback / Stop Conditions, or an
execution-readiness claim. An internal hidden Plan draft also violates this
gate because it prevents the Analysis discussion from changing direction
cleanly.

## Optional Section Triggers

| Section                       | Trigger                                                                                                                     |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Trigger / Reproduction        | Current/expected behavior or reproduction changes the decision                                                              |
| Context / Unknowns            | Context, provenance, inference, or unknowns can change a core field                                                         |
| Alternatives / Decision       | Multiple real options, split/redefine/defer/abandon, or direction choice                                                    |
| Capability And Skill Routing  | A professional or external Skill is relevant                                                                                |
| Profile Additions             | A domain omission check adds material Evidence or Risk                                                                      |
| Database / Migration          | Schema, old data, migration, sync, or backfill                                                                              |
| UI / Manual Acceptance        | UI, interaction, visual, device-side, or subjective acceptance                                                              |
| API / Compatibility / Release | Public contract, caller, package, registry, deploy, or release surface                                                      |
| Authorization Matrix          | Login, publish, payment, secrets, deletion, sending, or separate authorization                                              |
| Recommended Approach          | Planning has started and implementation direction needs explanation                                                         |
| Structural Change Forecast    | A software Plan will edit code, tests, build files, or engineering workflow contracts                                       |
| Execution Nodes               | A high-cost, error-prone, or user-selectable validation/intervention gate; ordinary deterministic checks remain in the plan |
| Dependencies And Handoffs     | Upstream/downstream startup contracts exist                                                                                 |
| Verification Plan             | Evidence needs multiple gates, runtime checks, or human acceptance                                                          |
| Rollback / Stop Conditions    | Failure is not trivially reversible or risk can expand                                                                      |
| Knowledge / Card Checkpoint   | Card search, candidate, link, update, or create work is triggered                                                           |
| Granoflow References          | Task analysis adopted Evidence, Experience, or Knowledge that materially changes the document                               |
| Visual Narrative Mode         | Comic, manga, storyboard, animation, video shot, or motion-design work                                                      |

Do not render an optional heading merely to say it is unused.

When `UI / Manual Acceptance` is triggered, **Must** load
[`user-visible-copy-boundary.md`](user-visible-copy-boundary.md) via
`granoflow_bundled_skill_reference` (skillId `granoflow-agent-workflow`,
referenceId `user-visible-copy-boundary`) before authoring in-frame copy.
Skipping the load fails closed `user_visible_copy_boundary_unread`. Every
visual Prototype must pass its copy admission test **and**
`scripts/lint_prototype_user_copy.py` (`ok: true`) before visual confirmation;
set `craft_checklist.user_visible_copy_boundary_ok: true` only then. Keep
Prototype-only scenario controls and reviewer explanations outside the
simulated product UI; internal filtering, design rationale, confidence,
quantity, architecture, test, and acceptance language must not become product
copy (`user_visible_copy_boundary_violation`).

### UI Change Prototype Mandate

Any task that changes UI—layout, navigation/shell, visual treatment, interaction
chrome, or user-visible screens—**must** produce a high-fidelity HTML prototype
for that authorized delta before Analysis may be confirmed and before
execution Readiness may pass.

Detection (any one is enough):

- `UI / Manual Acceptance` section is triggered;
- Scope / Outcome / Evidence names UI screens, components, or visual change;
- the task description or title states a UI/frontend change;
- Project Work marks the project as including frontend and the task touches a
  user-facing surface.

Hard rules:

1. Set `prototype_requirement: required`. Do **not** use `not_required` or keep
   `conditional` unresolved after Analysis when a UI change is present.
2. Read the confirmed project Design Baseline
   (`granoflow_project_design_baseline_read` with exact ids/SHA). Accept against
   contract fidelity (契约级一致). Declare `derivedFrom` that exact package.
3. **Do not** apply a new random visual seed (no Spec re-exploration / palette
   re-roll). Task prototypes inherit the locked Spec + Shell. Fail closed
   `task_prototype_seed_forbidden`.
4. Load project `widgets.yaml` (App readback). Reuse widgets with the same role
   before inventing new chrome/controls. Skipping reuse without rationale →
   `widget_reuse_required`. After visual confirmation, extract new/changed
   reusable widgets into the same project `widgets` slot.
5. Apply **Task Prototype Craft Gate And Option Set** from
   `granoflow-project-definition/project-artifact-workflows`:
   - Craft Gate (intent / **Baseline fit** / **confirmed chrome lock** / craft /
     **user-visible copy boundary** / confirm surface) must pass before
     `visualConfirmed=true`
     else `task_prototype_craft_incomplete` /
     `prototype_baseline_fit_*` /
     `prototype_generic_phone_frame` /
     `prototype_confirmed_chrome_lock_*` /
     `user_visible_copy_boundary_unread` /
     `user_visible_copy_boundary_violation`. Load
     `prototype-baseline-fit`; embed locked Spec tokens; match Shell chrome
     language; run `lint_prototype_baseline_fit.py`; set `baseline_fit_ok`.
     When chrome-family siblings are already `visualConfirmed`, load
     `prototype-confirmed-chrome-lock`, record `chrome_lock.authorities`,
     reuse confirmed control vocabulary, run
     `lint_prototype_confirmed_chrome_lock.py --authority …`, and set
     `confirmed_chrome_lock_ok`.
   - **Interactive:** load `prototype-expression-brainstorm`, run
     **mainstream-reference-first** candidates (`scope_mode`
     `same_category`|`capability_match`; default `capability_match` when
     unsure), brainstorm backfill **only** when mainstream `<5`, then promote
     **two page expressions** (`expr_a` + `expr_b`) with **functional parity**
     (same capabilities, same data fields, same required states;
     presentation-only contrast) inside the locked Design System
     (`design_system_locked`), with **≥2** whitelist contrast axes and
     page-local theses; **mix-and-match** per task/page. Run
     `lint_prototype_expression_brainstorm.py` and set
     `expression_brainstorm_ok`. Add a **third** (`industry_peer_c`) only when
     three industry peer patterns all fit inside the locked Design System and
     the host cannot honestly prefer one (else
     `prototype_option_third_unjustified`). Do **not** re-offer Design Spec
     choice (`delta_match` / `ai_challenger` / `spec_match` as task option ids)
     → `prototype_option_design_system_reopened`. Do **not** split features or
     product states across A/B → `prototype_option_function_split` /
     `prototype_option_data_divergence`. Options Must diverge in the **frames**
     (not prose-only). Emit a **side-by-side Contrast Gallery** with candidate
     digest + per-axis visible-diff captions (prefer
     `granoflow-project-definition/scripts/build_option_contrast_gallery.py`);
     separate option links alone are insufficient. Fail closed
     `prototype_option_brainstorm_*` /
     `prototype_option_mainstream_skip` /
     `prototype_option_scope_mode_invalid` /
     `prototype_option_contrast_insufficient` /
     `prototype_option_near_duplicate` /
     `prototype_option_contrast_gallery_required` /
     `prototype_option_diff_unlabeled`. One wait (per-page picks allowed).
   - **Unattended (explicit only):** same mainstream-first protocol then
     **one** `expr_a` only.
6. Author the HTML option(s), then apply the **Prototype Preview Gate**:
   interactive waits on the Contrast Gallery (option batch); unattended shows
   the single-link notice, continues, and includes every link in the
   run-closing Prototype Link Digest.
7. Obtain visual confirmation for the **chosen** package hash (interactive
   user accept, or unattended auto-accept only when explicitly unattended),
   upload to the task `ui_prototype` slot with `visualConfirmed=true`, and
   read back SHA/manifest evidence. Apply
   `discussion-writeback-contract` + `change-impact-fanout`: any **later**
   accepted change (page split, craft fix, copy, Outcome/Scope, option rematch)
   Must update App slots **and** close a Change Impact Fan-out ledger (sibling
   tasks/milestones/docs/notes/cards) before the next gate — never leave truth
   only in chat/`temp` → `discussion_writeback_pending` /
   `temp_only_artifact_forbidden` / `change_impact_*`. Later rematches Must
   import a new current package and rewrite Task Work refs in the same batch.
8. Prefer completing the prototype **before Analysis confirmation** so the user
   can see the change before implementation. At latest, the confirmed
   `ui_prototype` must exist before `readiness_grill_status: passed` and before
   any non-dry-run execution.
9. Missing, unconfirmed, stale, or non-`derivedFrom` prototypes return
   `ui_prototype_required` / block Readiness. Stale Task Work refs after a
   discussion change return `stale_reference_after_discussion`. Do not
   implement UI first and "backfill" a prototype after code. Missing
   interactive wait returns `prototype_preview_review_required`. Missing
   unattended closing digest when prototypes were authored returns
   `prototype_link_digest_required`.
10. Keep **design-first** (see
    `granoflow-project-definition/project-artifact-workflows` § Design-first,
    product-truth, and high-risk feasibility). Previews must pass **product
    truth** (`prototype_product_truth_violation` if they invent unauthorized
    states/capabilities). For **high-risk** platform-coupled UI, start a short
    Tech Note as soon as the preview batch exists; before
    `readiness_grill_status: passed`, record a feasibility conclusion
    (as drawn / degraded with `【增强实现】` / revise design). Missing
    conclusion → `high_risk_feasibility_unresolved`. If revise-design is
    required, do not pass Readiness—return to product/prototype change rather
    than faking the UI in code.

### Task Integration Test Policy (campaign runs later)

For software tasks that change code, record an explicit unit-test sufficiency
judgment before adding any integration test. This policy is **task-local**
(only cover this task's Outcome) and defaults to **not** adding integration
tests (prefer `service_path` / shared-session I/O metadata). To **run** the
integration suite, use lifecycle stage `integration_campaign` /
`granoflow-integration-test-campaign`. To **run** UI E2E (screenshots under
`temp/`), use stage `e2e_campaign` / `granoflow-e2e-test-campaign` after
integration is green. Do not mix either campaign into an ordinary feature task.

**Copy-only exception (hard):** If Scope is copy-only / 文字验证 (see
`user-visible-copy-boundary.md`), set `copy_change_only: true` and skip this
entire policy—**no** unit, integration, or other automated tests. Violations
fail closed as `copy_change_tests_forbidden`.

Hard rules (non-copy software tasks):

0. **Prototype document coverage (Analysis / prototype lock).** When a
   `ui_prototype` is finalized or rematched, load `prototype-doc-coverage` and:
   - complete `prototype_html_coverage` so **every task-owned user-visible
     surface** (page, dialog/modal, sheet, popover, toast when task-owned) has
     a high-fidelity HTML prototype (`lint_prototype_doc_coverage.py --kind
html_coverage`; no `prototype_html_coverage_gap`);
   - complete `prototype_widget_reuse` against project `widgets.yaml` (same role
     ⇒ Must reuse catalog widget; no near-duplicates;
     `--kind widget_reuse --widgets …`);
   - complete `prototype_doc_coverage` so every material prototype surface is
     `covered` in Task Work and Project Work (no `missing`/`conflict`). Lint
     with `scripts/lint_prototype_doc_coverage.py --kind coverage`.
     0b. **Prototype implementation fidelity (before unit tests).** When the task has
     a UI `ui_prototype` authority, load
     `prototype-implementation-fidelity` and run Phase A
     (`method: code_review_guess` only — **not** screenshot/vision) **before**
     executing unit tests: compare implementation to the HTML prototype by code
     reading, emit an explicit declaration, answer **all three** questions
     (matched or diverged), decide `keep_implementation` /
     `revise_to_prototype`, and persist `prototype_impl_compare` (+ `diffs` when
     diverged). Fail closed as `prototype_impl_compare_unread`,
     `prototype_impl_compare_undeclared`,
     `prototype_impl_compare_three_questions_incomplete`,
     `prototype_diff_ledger_incomplete`, `prototype_impl_compare_wrong_method`, or
     `prototype_impl_compare_lint_failed`. Lint with
     `scripts/lint_prototype_implementation_fidelity.py`. E2E Phase B (inventory
     **every** finalized task-level prototype; AI loop forbids keep until user
     final; screenshot + prototype link shown) is owned by
     `granoflow-e2e-test-campaign` / `e2e-evidence-pack`.
1. **Judge unit tests first.** Set `unit_test_sufficiency` to `sufficient` or
   `insufficient` with a one-sentence reason (what boundary unit tests can or
   cannot prove for this Outcome). Leaving it `unassessed` on a code-changing
   task fails closed as `unit_test_sufficiency_unassessed`.
2. **Prefer unit tests.** When `sufficient`, set
   `integration_test_requirement: not_required` and do **not** add integration
   tests. Adding them anyway fails closed as
   `integration_test_added_without_insufficiency`.
3. **Add only when unit tests are insufficient.** Then set
   `integration_test_requirement: required` and add integration tests that cover
   only this task's gap.
4. **Cap at two.** At most **2** new integration tests (cases or focused test
   files/entrypoints counted as the Plan defines, max 2) per task. If more
   gaps exist, pick the two highest-importance ones and list the rest as
   residuals / follow-ups. Exceeding two fails closed as
   `integration_test_cap_exceeded`.
5. **Do not execute in the feature task.** After adding, leave
   `integration_test_execution: not_run_manual_only` (awaiting stage-6
   campaign). The Agent must not run the new integration tests inside this
   feature task (no `flutter test integration_test`, Playwright e2e, device
   farms, etc. here). Agent-run inside the feature task fails closed as
   `integration_test_executed_by_agent`. Unit/lint/type/build gates still run
   as usual. Campaign stage later auto-drives the orchestrated suite.
6. **Recommend orchestration metadata.** When adding IT, record suggested
   `requires` / `produces` (optional `mutates` / `destroys`) per case so stage
   6 can build a minimal path without rediscovering dependencies from scratch.
7. **Device is user-chosen.** When any integration test is added (or
   `integration_test_requirement: required`), the Agent must recommend
   **the user's local machine** (`integration_test_device_recommendation:
local_machine`) and ask the user to confirm or pick another target
   (simulator/emulator, physical device, remote farm, etc.). Record the
   chosen value in `integration_test_device` (`local_machine` |
   `simulator_or_emulator` | `physical_device` | `remote_farm` |
   `other:<label>`). Do not invent a device, silently assume CI, or run on
   a host-chosen target. Leaving device `unselected` while tests were added
   fails closed as `integration_test_device_unselected`.
8. **Honor Project Work special requirements.** Before adding IT, load
   `engineering.quality_gates.integration_test_special_requirements` (see
   `integration-test-special-requirements.md`). Apply every matching
   `fail_closed` row (corpus paths, forbidden substitutes, `not_app_seed`).
   Set `integration_test_special_requirements_checked` to `checked_none` or
   `applied`, and list applied ids. Skipping the check fails closed as
   `integration_test_special_requirements_unchecked`. Ignoring a matching
   `fail_closed` row fails as `integration_test_special_requirement_ignored`.
   Using a `not_app_seed: true` corpus as create-library app seed fails as
   `integration_test_special_requirement_as_app_seed`.
9. Delivery and acceptance must show the sufficiency judgment, count (0–2),
   paths of any added tests, recommended `requires`/`produces`, selected
   device, special-requirement check/applied ids, and
   `awaiting_campaign_execution` / `awaiting_manual_execution`—never claim
   integration runtime success from unrun tests.

### Data Attachment Sync Mandate

Read Project Work `engineering.data_and_migrations` for
`data_model_attachment`, `json_contracts_attachment`, and
`constants_catalog_attachment` (exact file names).

When a task changes any of the following, it **must** update the matching
**project** attachment in the same task, refresh artifact registry SHA/readback,
and keep code consistent with that attachment:

| Change                                         | Project attachment                                     |
| ---------------------------------------------- | ------------------------------------------------------ |
| Business DB / table schema                     | `data_model` (`data-model.md` or registered name)      |
| JSON / structured file shape or semantics      | `json_contracts` (default `data-contracts.yaml`)       |
| Shared constant names, values/types, or owners | `constants_catalog` (default `constants-catalog.yaml`) |

Fail closed with `data_artifact_stale` when code ships without the attachment
update, or when attachment content no longer matches the implemented surface.
Do not embed full schemas, JSON shapes, or constant catalogs into Project Work
body YAML. If Project Work declared `data_persistence: none`, a task must not
introduce a business database without reopening Project Work and replacing
`no_database_declaration`.

#### Analysis-time schema challenge (required)

Project Definition Step 1 only locks **data shape** (persistence mode +
attachment registry). Field-level table design, JSON shapes, and constant
catalogs are expected to be challenged as tasks learn more.

During **Analysis** (before `analysis_status=confirmed`), when the task
touches or depends on DB / JSON contracts / shared constants:

1. Read the current project data attachment(s) named in Project Work.
2. If the registered schema, JSON shape, or constant set is **unreasonable**
   for the confirmed Outcome—wrong grain, missing relations, unsafe
   nullability, unworkable migration path, contradictory invariants, or
   constants that cannot support the work—**raise it explicitly** in Analysis
   (Context / Unknowns, Alternatives / Decision, and/or Database / Migration).
   Do not silently inherit a bad model into Plan or code.
3. Recommend a concrete revision (tables/fields/invariants/JSON shape/constant
   changes) and treat acceptance of that revision as part of Analysis
   confirmation. The later Plan/Delivery **must** update the same project
   attachment(s); shipping code against an unchallenged-but-known-bad schema
   fails closed as `data_artifact_stale` once the attachment is corrected, or
   as an Analysis Grill / Readiness finding if the issue was ignored.
4. If the current attachment is adequate, say so briefly (no fabricated
   redesign). If `data_persistence: none` and the task still needs a business
   DB, reopen Project Work first—do not invent tables only inside the task.

#### Analysis-time dependency challenge (required)

Capability-critical libraries are selected in Project Definition Step 1
(`engineering.dependencies.approved`). During **Analysis**, when the task
depends on or would introduce a third-party library for a product capability:

1. Read `dependencies.approved` (and admission rules) from Project Work.
2. If the selected package is **unreasonable**—abandoned, missing required
   platform support, license conflict, cannot meet Outcome performance/size,
   or a clearly better maintained alternative exists for the same
   capability—**raise it explicitly** and recommend a replacement or version
   policy change. Do not silently swap libraries in code.
3. Treat acceptance of the dependency revision as part of Analysis
   confirmation; update Project Work `dependencies.approved` in the same
   task before Delivery. Introducing a new capability-critical library that
   was never selected fails closed as `capability_dependency_unselected`
   until Project Work is updated.
4. Non-critical helper packages may be proposed in Plan without reopening
   Project Work, subject to `admission_rules`.

Grill is an authoring gate, not a reader-facing section trigger. Never render
`Grill Review`, `Analysis Grill`, `Execution Readiness Grill`, a reviewer
ledger, raw findings, or provider/tool transcripts in Task Work. Apply every
accepted finding directly to the section it improves, such as Evidence, Scope,
Risk, Decision, Execution Plan, Verification Plan, or Rollback / Stop
Conditions. Keep only the machine-stable phase result in
`analysis_grill_status` or `readiness_grill_status`.

## Progressive Loading And Small-Task Budget

Initially load only the main Agent Workflow plus this workflow and its template.
Read one Profile, external Skill, Card, Delivery, Review, or legacy reference
only after its trigger fires. A manifest is a discovery list, not an instruction
to preload every reference. Never preload all Profiles, lifecycle references,
third-party Skill bodies, or auxiliary-tool instructions.

For `planning_status=not_required`:

- target about 250 Chinese task-specific characters, or about 400 tokens for
  other/mixed languages, excluding fixed metadata and markers;
- treat the budget as a soft complexity signal, not a truncation rule or exact
  tokenizer gate;
- remove repetition and untriggered sections first; never remove Evidence or
  Risk to fit;
- if the task remains materially larger, reassess it as Planning required;
- use at most one directly relevant model-invocable professional Skill by
  default, and use none when model capability is sufficient;
- if diagnosis, architecture, migration, TDD, or multiple specialist methods
  are all needed, enter Planning instead of stacking Skills onto a light task.
- still provide a concrete `Next Action`, named inputs, observable evidence,
  and a stop or handoff condition; `not_required` omits a full Execution Plan,
  not the information needed to act safely.

Task impact and uncertainty determine lightness. Repository size and changed
line count do not.

## Analysis Confirmation

Ask only questions that can change Outcome, Evidence, Scope, Risk, Decision, or
whether Planning is required. For unattended completion, first read
`unattended-interaction-contract.md`; a valid same-run instruction or durable
grant consumes ordinary phase confirmations unless a real blocker exists.

Set `analysis_status=awaiting_confirmation` before final review. Only explicit
user authorization sets `analysis_status=confirmed`; a qualifying current
unattended instruction is explicit authorization, while Agent self-confirmation
is not. Then run the mandatory MCP-bundled Analysis Grill. It checks source discipline, decision-changing
unknowns, Outcome/Evidence/Scope/Risk/Decision consistency, concrete examples,
false-success paths, whether Planning recommendation is justified, and—when the
task depends on DB / JSON / constants or capability-critical libraries—whether
unreasonable project data attachments or dependency selections were challenged
and a revision path was decided (not silently deferred into execution). Set
`analysis_grill_status=passed` only when all material findings are resolved.
Resolve findings by revising the relevant Analysis prose and acceptance
contracts; do not append a Grill section or finding ledger. Material revisions
re-evaluate Analysis under the interaction contract and require another question
only for a real blocker. Analysis confirmation alone does not authorize Planning,
node creation, attachment upload, or execution.

Before confirming Analysis, recommend one Planning outcome:

- `not_required`: one local, directly describable action; clear Outcome,
  Evidence, Scope, Risk, and Next Action; no decision-changing unknowns;
  trivially reversible; no database/migration, public API, auth, security,
  privacy, login, payment, deletion, publish, send, commit, push, product,
  aesthetic, multi-node, or separately authorized work.
- `required`: any criterion above is false or unverified.

Small code size alone never proves `not_required`.

## Legal State Matrix

| Analysis                          | Analysis Grill                               | Planning                          | Readiness Grill                  | Valid                            | Next action                                                                        |
| --------------------------------- | -------------------------------------------- | --------------------------------- | -------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------- |
| `draft` / `awaiting_confirmation` | `not_run` / `revisions_required`             | `not_assessed`                    | `not_run`                        | yes                              | finish and confirm Analysis                                                        |
| `confirmed`                       | `not_run` / `revisions_required` / `blocked` | `not_assessed`                    | `not_run`                        | yes, not plannable               | resolve the Analysis Grill finding                                                 |
| `confirmed`                       | `not_run` / `revisions_required` / `blocked` | anything except `not_assessed`    | any                              | no                               | finish bundled Analysis Grill                                                      |
| `confirmed`                       | `passed`                                     | `not_assessed`                    | `not_run`                        | yes                              | choose `not_required` or request Planning permission                               |
| `confirmed`                       | `passed`                                     | `draft` / `awaiting_confirmation` | `not_run`                        | only after user permits Planning | discuss and confirm Planning                                                       |
| `confirmed`                       | `passed`                                     | `confirmed`                       | `not_run` / `revisions_required` | yes, not uploadable              | remind user and run bundled Readiness Grill                                        |
| `confirmed`                       | `passed`                                     | `not_required` / `confirmed`      | `passed`                         | yes                              | upload, hash-read back, then consume a direct instruction or valid delegated grant |

Reject invalid combinations before upload or active-version selection. Do not
silently repair them into a more permissive state. Return
`invalid_task_work_state` with the failing phase fields.

If Planning is required, explain why. Ask permission in interactive mode; in
unattended mode consume current authorization unless a real blocker exists.
Permission changes only `planning_status=not_assessed -> draft`; it does not by
itself confirm Planning or authorize execution.

## Planning

Planning starts from the clean rewritten Analysis document produced after the
Analysis Grill and adds only triggered Planning sections during discussion. It
does not repeat a second template or candidate-Skill inventory. It may start
only when Analysis is confirmed and
`analysis_grill_status=passed`. Planning confirmation sets:

```yaml
analysis_status: confirmed
analysis_grill_status: passed
planning_status: confirmed
readiness_grill_status: not_run
```

When the Plan discussion is complete and the user has confirmed the Plan as
executable, automatically tell the user: the Plan is entering execution-
readiness review; a passing result will be uploaded to Granoflow; upload does
not authorize execution. This is a notification, not a request for another
approval. Then run the MCP-bundled Execution Readiness Grill before any upload.

The Readiness Grill must determine whether the Plan is sufficient to finish the
work—including, for software code edits, a passed Plan Design Gate per
`plan-design-gate.md`—and whether its prerequisites are actually available:
authorization, accounts and login state, credentials, keys, secret availability,
required data and source materials, upstream outputs, tools and environment,
verification, rollback, stop, and handoff conditions. For UI-changing tasks, also
verify product-truth on the confirmed `ui_prototype` and, when the surface is
high-risk (platform-coupled / easy to overpromise), a written feasibility
conclusion from the Tech Note (`high_risk_feasibility_unresolved` if missing;
revise-design conclusions block `passed`). Record only whether a credential or
secret is available and authorized; never copy its value into Task Work, logs,
or chat. Missing or unverified readiness sets `blocked` or
`revisions_required`, not `passed`.

Analysis-confirmed content remains intact. A material Planning change replaces
the current unfinished `execution` slot and repeats Planning confirmation; it
does not create another active Task Work attachment. A change to Outcome,
Evidence, Scope, Risk, or Decision reopens Analysis and affected Planning.

Write ordinary work as `Execution Plan` steps using the template's `Performer`,
Purpose, Inputs, Action, Output, Verification, Stop / Handoff, and focused-time
fields. Adapt each step to the performer: an Agent step may name files, APIs,
commands, and data boundaries; a user step must use plain instructions and name
materials, people, timing, and what to record. A client visit, for example,
needs preparation, agenda, questions, notes, and follow-up—not software test
terminology.

For software work, reconcile every step against the confirmed minimum-change
budget. Each action must map to a required change through Outcome or Evidence,
remain inside its allowed touchpoints, and preserve the named protected
surfaces. Discovery of a new UI region, module, public API, schema, dependency,
or architectural change is scope drift until confirmed. Stop before performing
that change; do not use a passing test suite, implementation convenience, or
adjacent cleanup as implicit authorization.

For software work that will edit code, tests, or build files, read
`plan-design-gate.md` and complete its minimal sufficient Design Package before
claiming the Plan is executable (also required for light
`planning_status: not_required` software edits). Set
`plan_design_gate_status: pending` while drafting; set `passed` only when the
package is complete and confirmed under the interaction contract. Readiness
Grill fails closed as `plan_design_gate_missing`,
`plan_design_gate_incomplete`, or `plan_test_cases_missing` when the Gate is
absent or hollow (missing/untraced verification test cases, generic
"implement Outcome" steps, missing flowchart when control flow is non-trivial,
missing explicit `data_disposition`, missing task-local libraries, missing
UI↔data binding on UI tasks, or Forecast without concrete paths). Do not request
execution authorization while a required Gate is not `passed`.

For software work, read `software-structural-budget.md` and add its complete
`Structural Change Forecast` before Plan confirmation (also required for light
`planning_status: not_required` software edits). Set
`structural_forecast_status: present_in_plan`. Readiness Grill fails closed as
`structural_forecast_missing` when the section is absent or incomplete. Keep
uncertain symbols labeled `expected` instead of inventing facts.

### Task Work Markdown Quality

The attached Task Work Document follows the same Markdown writing standard as
the task description. Each distinct problem is a separate paragraph; decisive
claims and acceptance results use **bold**; constraints, caveats, and
uncertainty use _italics_; literal commands, APIs, fields, paths, configuration,
logs, and code use inline or fenced code. Use headings, lists, tables,
blockquotes, and Mermaid diagrams when they make analysis, plan dependencies,
evidence, or acceptance easier to inspect. Formatting must remain semantic and
must not replace explanatory prose.
Each distinct problem paragraph must contain at least one concrete example of
the observed or plausible case. Where the plan makes a meaningful choice or
sets a boundary, include concrete rationale examples in the relevant analysis,
scope, alternatives, or risk section; do not force rationale into tasks with no
material choice.
The example must be actionable for a cold-start reader: it should support
reproduction, inspection, or comparison with the expected result. A generic
label such as “处理超时问题” does not pass. If evidence is insufficient to
write a truthful example, record `待确认` or an explicit unknown and do not
claim the Task Work is ready for execution.

### Optional Validation Nodes

Do not create a Granoflow node for every plan step. Keep routine, low-cost,
deterministic checks such as unit tests, lint, formatting, builds, fixed exit
codes, and simple log assertions in the plan's Verification Plan.

Create an optional node only when the validation or intervention is materially
expensive, subjective, error-prone, or requires the user to choose whether the
cost is justified. Typical examples include AI-driven program execution,
automatic screenshot capture and visual inspection, complex log interpretation,
AI quality review of comic or animation output, or manual aesthetic acceptance.

Each such node must state the validation mode, expected cost, evidence required,
pass criteria, and what happens if the user declines or the result is
inconclusive. The node is an explicit opt-in gate, not a duplicate checklist.
Do not use a node merely because a test exists.

## Completed Historical Task Audit

When the task is already complete and the purpose is to reconstruct or improve
its record, set `decision=completion_audit` in the `execution` slot. Read the task review, Delivery,
source changes, runtime evidence, and original discussion that are actually
available. Write the template's `Original Problem Or Event`, `Actual Actions`,
`Actual Evidence`, `Outcome And Differences`, and `Residuals / Unknowns`
sections. Add `Reusable Next Entry Point` only when there is a real future
trigger.

Do not write a prospective Execution Plan, retroactive prerequisites, or an
estimated future duration for work that already happened. Preserve a reliable
recorded focused-work duration when one exists; otherwise use the task-writing
rule's explicit historical unknown. If evidence cannot prove the actual action
or result, keep the audit partial and do not use it to justify task completion.

When a completed task needs a later correction, use
`document_slot: post_completion_revision`. Create that slot only once, link it
to the completed `execution` record with `supersedes`, and then replace that
same slot for every later correction. Do not create another Task Work version
for each correction.

## Quality Gates Before Persistence

Run both checks before upload, active-version selection, or completion:

1. **30-second recall gate.** Read only the task title and description. A user
   must be able to recover the concrete problem or event, affected person or
   system, intended or actual result, and observable acceptance signal. Generic
   prose reusable across tasks, unexplained internal labels, or a restated title
   returns `task_description_recall_gate_failed`.
2. **Cold-handoff gate.** Give Task Work to a hypothetical Agent or person who
   has not seen the thread. They must be able to distinguish facts, inference,
   and unknowns and determine the performer, inputs, actions, outputs,
   verification, and stop/handoff conditions. They must also know which checks
   are ordinary plan verification and which are optional costly nodes. Failure
   returns `task_work_cold_handoff_failed`.

If a material claim lacks an inspected source and is not labeled inference or
unknown, return `task_work_source_evidence_insufficient`. These failures are
content failures: Markdown decoration, attachment creation, HTTP success, or a
matching hash cannot override them. Revise and rerun the checks before any
write. If revision would require a user decision, leave the document in draft
and ask only the decision-changing question.

Before persistence, run the slot reconciliation gate:

- an unfinished task has exactly one active `execution` Task Work document;
- a completed task has one active `execution` document and zero or one active
  `post_completion_revision` document; and
- no other attachment is labeled or treated as the current Task Work document.

If this fails, return `task_work_slot_count_exceeded` or
`task_work_slot_identity_invalid` and stop. Reconcile old attachments before
writing new content. A replacement is transactional: verify the new content
and hash first, then remove or archive the superseded slot record. If the
replacement fails, retain the previous active document.

## Immutable Versions And Active Identity

Every App-owned Task Work content readback is a complete, self-contained
checkpoint. The active logical
slot is replaceable even if the underlying App attachment record is immutable;
the workflow must not expose every historical replacement as an active Task
Work document. `supersedes` points to the immediately replaced record in the
same slot.

Only the latest clean post-Grill rewrite that passes the quality gates, has
`analysis_grill_status=passed`, and has `readiness_grill_status=passed` may be
uploaded through `granoflow_task_attachment_add_markdown` with idempotency key,
latest task revision, and expected local hash. Read the App-owned content and
SHA-256 back. Only verified readback may switch the active slot pointer in the
managed summary. Filename or HTTP success alone is insufficient. After the
pointer switches, reconcile the superseded attachment so the task still has at
most two active Task Work documents.

The built-in post-Grill clean rewrite affects the local working copy first; App
attachments change only through the transactional upload/readback/active-slot
flow. Runtime progress never creates or overwrites a Work Document.

## Prototype Execution Inputs

Apply the **UI Change Prototype Mandate** above whenever the task changes UI.
Record `prototype_requirement`, `prototype_condition_result`,
`prototype_input_status`, and `prototype_inputs` in the stable header.

- If the task changes UI: `prototype_requirement` **must** be `required`,
  `prototype_condition_result` must be `required`, and
  `prototype_input_status` must reach `ready` (exact confirmed package) before
  Readiness passes.
- `not_required` is allowed only when the task explicitly has **no** UI change
  (stated in Task Work). `conditional` may exist only while Detection is still
  unresolved during early draft Analysis; it cannot survive Analysis
  confirmation when Detection is positive.
- A required input must identify the source task or project, prototype, exact
  version and ordinal, package attachment, package SHA-256, visual confirmation,
  `derivedFrom` baseline ids/SHA when a project Design Baseline exists, and
  intended use. Never resolve by filename, current, or latest at export time.
- Record `【增强实现】` / `implementation_notes` where HTML is schematic and the
  stack will use richer widgets.

Before Readiness passes, call `granoflow_task_export` and treat the App-owned
`executionAdmission.allowed` value as authoritative. Missing, ambiguous,
deleted, stale, link-mismatched, unconfirmed, or hash-mismatched references
block execution. For UI-changing tasks, also block when `ui_prototype` is
missing, unconfirmed, or not derived from the confirmed Design Baseline
(document-level gate: return `ui_prototype_required`). When a package changes,
add the new attachment, rewrite every affected exact reference and relevant
prose, upload and hash-read back the new Task Work, then remove the old
attachment. Do not model this as overwrite.

When admitted package bytes are needed, request `assetMode=file` with a TTL no
greater than 600 seconds. Consume only the paths returned under
`prototypeAssets`; the MCP layer does not read SQLite, decrypt packages, or
reimplement admission.

### Discussion Writeback (stable Plan / Execution refs)

Any material adjustment accepted in discussion Must be written back to App
slots **and** close a Change Impact Fan-out ledger before Plan confirm,
Readiness `passed`, or Execution. Full contracts: `discussion-writeback-contract`
and `change-impact-fanout`. Local `temp/` galleries are previews only.
Fail closed: `discussion_writeback_pending`, `temp_only_artifact_forbidden`,
`stale_reference_after_discussion`, `change_impact_*`.

Before uploading a rewritten version and again before Delivery, rebuild its
`Granoflow References` from the App-owned adopted set and run the dedicated
reference-audit preview/apply flow. Removing an unused current reference must
not erase applied, validated, or contradicted Knowledge Usage history. A
considered or rejected search result never enters this section or creates a
relationship.

## Grill

Every new Task Work runs two MCP-bundled phase checks: Analysis Grill before
Planning, and Execution Readiness Grill before upload. For a genuinely
`not_required` task, the second check is still required but may be compact and
must prove the single action's inputs, authorization, evidence, and stop
condition are ready.

Both checks are invisible authoring passes. A finding changes the relevant
body section and, when material, reopens confirmation. The final reader-facing
document must look as though it was written correctly once: no standalone
Grill heading, checklist, reviewer attribution, before/after commentary, or
review-process residue. A blocked result belongs in the relevant unknown,
dependency, authorization, risk, or stop condition as well as the phase status;
it does not justify a separate Grill record.

### Post-Grill Clean Rewrite

When either bundled Grill reaches a phase result, do not finish by patching the
current file. Reconstruct the complete Task Work as a new document from the
confirmed facts, decisions, accepted findings, and still-valid content. Rewrite
transitions and section order for a cold reader; collapse duplicate statements,
remove superseded alternatives and stale questions, and omit all review-process
residue. Copying the old body and appending corrections is not a clean rewrite.

Write the replacement to a new versioned local path with `work_version + 1`,
preserve the logical `document_slot` and original lineage, update `updated_at`,
and set the real Grill status. Validate the replacement's Markdown, metadata,
source discipline, cold-handoff completeness, and content hash before deleting
the prior local file. If creation or validation fails, keep the prior file and
report `post_grill_rewrite_failed`; never leave the slot without a readable
local document. After success, delete the prior local file rather than keeping
it as a parallel draft or archive.

Only the successfully validated replacement path and hash may be selected for
attachment upload. Uploading the pre-Grill file, a patch file, a findings
appendix, or an unvalidated replacement fails with
`post_grill_rewrite_required`. If an older App attachment already occupies the
logical slot, upload/read back the replacement before reconciling that
superseded attachment; local deletion does not authorize App deletion.

An available `model_allowed` `grill-finalizer` may add enhanced evidence before
a bundled gate concludes, but it never replaces the bundled checklist or owns
the phase result. If that path writes a temporary candidate, the host **must**
run the post-finalizer `grill-me` pipeline (`pipeline_required` in
`external-skill-routing.md`): interactive one-question + recommend + wait, or
explicit-unattended one-question + recommend + auto-adopt, before promotion.
Fail closed with `post_finalizer_grill_me_required` if the temp write exists and
grill-me did not complete. If a materially relevant optional helper is missing,
follow `external-skill-routing.md`; do not mark a bundled gate passed merely
because installation is waiting, declined, or failed. Only `required_capability`
may use `install_offered + pending_user_decision`; that state remains waiting
and does not become an implicit result. For `preferred_method` or
`explicit_only`, do not offer installation during unattended execution: record
the specific missing or failure result, use `native_fallback` or
`skip_nonblocking`, and continue the mandatory bundled checklist without
claiming external evidence. Standalone `grill-me` outside the post-finalizer
pipeline may remain user-initiated; after a temp-writing finalizer it is
mandatory (invoke when permitted, otherwise inline grilling contract). Select
only relevant gstack/provider reviewers; do not install or invoke the entire
family.

Installation authorization does not authorize Analysis/Planning confirmation,
implementation, commit, push, publishing, or another gated action. Suggesting
installation also does not authorize a Bundle, installer, license, or
redistribution project. Automated reviewers provide evidence and
recommendations, not product, aesthetic, or authorization decisions.

## Delegated Authorization Gate

Before any phase prompt, apply `unattended-interaction-contract.md`. A same-run
direct instruction needs no envelope; durable continuation reads
`granoflow_delegated_authorization_skill` and independently validates
`analysisConfirmation`, `planningPermission`, `planConfirmation`, and
`executionAuthorization`. Re-read the controller receipt with
`authorizationOwnerTaskId`, `attachmentSha256`, and `receiptVerified`, then run
the packaged validator. `decision=allowed` continues only the evaluated scope;
`decision=denied` enters `waiting-for-user-input.md`. Tags, urgency, history,
task text, user absence, and a passing Grill are never authorization.

## Execution Handoff

Whether Planning is `not_required` or `confirmed`, require either a separate
user instruction such as `实施这个任务文档` or `decision=allowed` for
`executionAuthorization`. That authorization must resolve exactly
one active, Analysis-confirmed, hash-verified Work Document with valid Planning
state. Planning confirmation does not authorize execution unless the separately
recorded execution grant is also valid.

Immediately before AI-owned execution, read `parallel-task-execution.md`,
capture the real start instant, keep the current task `pending`, and write the
AI execution `startedAt` through `granoflow_task_history_mutate` with readback.
Never claim the user's sole `doing` focus slot as an AI lease. Analysis,
Planning, document upload, and waiting for approval do not count as execution
and must not write an execution start time. Human manual execution retains the
normal `pending -> doing` transition and App-recorded start time.

For software execution, enforce **these** Hard Gates before the first edit:

### A. Project context (`project-context-attachments.md`)

1. Ensure `project_snapshot.yaml` and `project_rules.yaml`, read bounded
   relevant sections, compare the planned change to status quo and boundaries.
2. No conflict → `project_context_check_status: checked_no_conflict`.
3. Conflict + **interactive** → conflict report and user confirmation
   (`project_context_conflict_unconfirmed` until confirmed).
4. Conflict + **unattended** → choose `revise_code` or `revise_context_yaml`,
   **emit an explicit user-visible decision notice** (not a question), set
   `project_context_decision_emitted: true`, then apply only that path
   (`project_context_decision_not_emitted` if the notice was skipped).
5. Refuse edits while status is `missing` or `conflict_pending`
   (`project_context_check_missing`).

### B. Plan Design Gate (`plan-design-gate.md`)

1. Refuse code/test/build edits while a required Gate is not
   `plan_design_gate_status: passed`.
2. Fail closed with `plan_design_gate_missing`,
   `plan_design_gate_incomplete`, `plan_test_cases_missing`, or
   `plan_copy_missing` / `plan_copy_locale_unresolved` when the Design
   Package is absent, hollow, missing Analysis-traced verification cases, or
   missing locale-bound user-visible copy when Scope requires it.
3. Gate `passed` does not waive Structural Forecast notice (section C).
4. When the milestone's Plan batch is ready to close, emit one
   `milestone-plan-acceptance-pack` (template + contract) aggregating present
   copy / schema / flowcharts / UML / test cases; interactive acceptance of
   that pack is required before treating milestone Planning as closed.
5. After the pack is accepted (or validly auto-adopted unattended), every
   in-scope software Execution turn and Delivery **Must** load
   `milestone-plan-acceptance-pack` and keep the accepted pack file as the
   primary milestone alignment reference. Fail closed
   `milestone_plan_acceptance_pack_not_used` if implement proceeds without it;
   `milestone_plan_acceptance_pack_delivery_unreconciled` if Delivery omits
   reconciliation of `present: true` pack sections.

### C. Structural forecast (`software-structural-budget.md`)

1. Refuse the first code/test/build edit while
   `structural_forecast_status` is not `notice_emitted` (or `reconciled`).
   Return `structural_forecast_not_shown`—do not partially edit "just this one
   file".
2. In the same turn as the first edit authorization, show the Task Work
   `Structural Change Forecast` as a non-confirming notice, then stamp
   `structural_forecast_status: notice_emitted` and
   `structural_forecast_notice_emitted_at` on the working Task Work copy (upload
   / readback when the host requires document freshness before edits).
3. Unattended / delegated / `gf做` still shows the notice and stamps the status;
   it must not create an artificial confirmation node and must not skip the
   stamp.
4. Reconcile every new touchpoint through the reference before editing it, and
   stop on scope drift.
5. The forecast must include a responsibility seam for each planned split and
   must explicitly reject mechanical line splitting, random helper extraction,
   wrapper-only indirection, and moving code without reducing responsibility.
   If the forecast cannot explain the intended responsibility of a file or
   symbol, do not enter `[dev]`; revise the Plan first
   (`structural_forecast_missing` until fixed).

Legacy `实施这个 Plan` may resolve a legacy confirmed Plan or an unambiguous
active Work Document. Ambiguous, draft, superseded, missing, invalid, or
unverified candidates fail closed.

External Skill instructions never override project rules, the Work Document,
or authorization gates. Commit, push, publish, sending, login, payment, secrets,
deletion, and irreversible actions keep separate authorization.

## Managed Summary

Maintain at most one new block and preserve all text outside it:

```text
<!-- granoflow-task-work-summary:start -->
- 状态: analysis=<status>; planning=<status>; execution=<latest task/node state>
- 结论: <decision>
- Outcome: <one-line outcome>
- Evidence: <strongest evidence>
- 执行边界: <execution method and user action boundary>
- Work Document: execution=<active attachment id/name>; post_completion_revision=<none | active attachment id/name>
- 版本: vNN
- 文档状态: attached | local_reference | attachment_api_unavailable | upload_failed
- 当前节点: 无 | <node>
- 待授权: 无 | <summary>
- 当前阻塞: 无 | <summary>
- 下一步: <state-level action>
<!-- granoflow-task-work-summary:end -->
```

Invalid, duplicated, missing, reversed, or nested markers return
`task_work_summary_markers_invalid` and stop automatic writes. Legacy Analysis
and Plan blocks remain readable and untouched; stop updating them after a new
active Work Document is verified.

## Delivery And Completion

Task Delivery remains a separate immutable actual-outcome record. For a new
Work Document, Delivery records `source_work_document` and Differences From
Work Document. Legacy Delivery may read `source_analysis` and `source_plan`.

For `not_required` work with no nodes, execute and verify the authorized action,
then create, upload, and read back Delivery before using the existing node-less
compatibility completion path. A short document, omitted Planning, or absent
nodes never waives Delivery or completion readback.

## Legacy Compatibility

Historical Task Analysis and Task Plan attachments remain immutable and
readable. Do not migrate, overwrite, or delete them. Their old templates,
workflows, commands, summary markers, and Delivery fields are legacy read and
resolve paths only.

All new task work and material amendments use `document_type: task_work`. A
host running an older package may continue its old workflow; this package must
not claim that old attachments were migrated.
