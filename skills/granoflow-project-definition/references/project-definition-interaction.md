# Project Definition Interaction

Read this before interviewing or recommending Project Work values. It owns Mode
Gate, recommendation provenance, and Step 1 decision batches. Design Spec /
Shell / widgets / task Craft Gate live in `project-artifact-workflows.md`;
fail-closed checklist in `hard-constraints.md`.

Read the shared
`granoflow-agent-workflow/requirement-intake-and-traceability` contract before
extracting user source material. A product document and user stories are the
recommended smallest pair for an individual developer, but their formatting is
never an admission gate. Preserve requirements found under unexpected headings.
During Project Definition, do not silently fill gaps that become confirmed
Project Work values—route them through the Mode Gate and Recommendation
Contract below.

## Mode Gate (interactive vs unattended)

Read
`granoflow-agent-workflow/execution-modes-and-acceptance-reports` for the shared
mode vocabulary. Project Definition applies this hard gate:

1. **Default `executionMode: interactive`.** If the user did not **explicitly**
   declare unattended / hands-off / no-interruption / 无人值守 (or an equivalent
   clear same-run grant) for this initialization, the run is interactive.
2. **Never infer unattended** from activation phrases alone (`Initialize this
project`, `定义这个项目`, document completeness, urgency, or the presence of
   a strong recommendation).
3. At Step 1 start, emit a non-question **mode notice** naming
   `executionMode: interactive` or `unattended` and the evidence (explicit user
   text or “default interactive”).
4. Read `granoflow-agent-workflow/unattended-interaction-contract` **only when**
   `executionMode` is unattended.

### Interactive mode (default)

For every decision batch that would set or lock a Project Work field, dependency
row, data-surface declaration, `skill_routing` / design profile, Project Work
confirm, or Design Baseline + App Shell visual confirmation:

1. **Ask** the decision in plain language (what is being decided and why it
   matters).
2. **Recommend** one `recommended_value` with reason and source (alternatives
   preferred when material).
3. **Wait** for the user’s accept / accept-eligible / customize / reject before
   treating the value as decided.

**Must not** in interactive mode:

- adopt `recommended_value` without an explicit user response to that batch;
- call `granoflow_project_work_confirm` without the user’s confirm decision for
  that Project Work content;
- apply Design Baseline / App Shell `auto_accept_recommendation`;
- use “safe assumption”, soft preference, or structural-budget defaults as a
  reason to skip the ask → recommend → wait loop.

Batches may combine several related fields so the user is not asked one YAML
path per turn. `accept eligible recommendations` is allowed only for items the
Agent listed in that batch—and only after the user explicitly accepts.

### Unattended mode (explicit declaration only)

Adopt `recommended_value` immediately and continue. Do not re-ask for
confirmation of recommendations. Stop only for real blockers defined by
`unattended-interaction-contract` (for example `direction_change`,
`missing_user_only_input`, `forbidden_action`, authorization failures). Soft
preference choices never become wait-for-user loops under unattended.

## Activation Boundary

Treat phrases such as `Initialize this project`, `Define this project`,
`初始化这个项目`, and `定义这个项目` as Project Definition. Treat
`Initialize Granoflow` / `初始化 Granoflow` as `granoflow-first-run-import`
only. Do not merge connection/capability-pack setup into this Skill's three
steps. These activation phrases do **not** switch the run to unattended.

## Recommendation Contract

For each unresolved field or decision batch, present:

```yaml
path: engineering.stack.frameworks
recommended_value: null
reason: null
source:
  type: user_confirmed | repository_fact | official_standard | mainstream_standard | agent_inference
  reference: null
alternatives: []
custom_allowed: true
batch_accept_eligible: true
```

Evidence order:

1. explicit user decision;
2. repository rules and inspected code/configuration;
3. official ecosystem standard or official template;
4. mainstream ecosystem convention;
5. labeled Agent recommendation.

**Every communication** that needs a user decision must include a recommended
option, a short reason, and a source. Alternatives are optional but preferred
when the choice is material.

**Interactive:** ask → recommend → wait (Mode Gate).

**Unattended (explicit only):** adopt `recommended_value` immediately and
continue per Mode Gate.

Product behavior, aesthetics, permissions, security/privacy posture, data
retention, destructive actions, publishing, deployment, payment, external
messages, and materially different architecture are never silently batch
confirmed **in interactive mode**. In unattended mode they still require an
explicit recommendation record and may become blockers if no safe
recommendation exists or the action is forbidden.

### Design / Baseline Confirmation Exception

The design-system branch is the deliberate exception to field-by-field
questioning for fonts/Skills menus—not to Mode Gate or random seeds.

- **Interactive:** Design Spec **Triad** then Shell **Triad**. Spec triad:
  **three different random seeds**—one faithful match + two AI challengers.
  Shell triad: all options **perfectly fit the selected Spec** (chrome /
  structure variants only—no independent palette seed). Option-set Preview
  Gate. User may pick / revise / request more. Never a menu of
  Skills/fonts/palettes.
- **Unattended (explicit only):** **one** Design Spec `spec_match` with a
  **random seed**, then **one** Shell `shell_match` **fitted to that Spec**—no
  triad, no challengers, no Spec-breaking Shell seed. Link notices + closing
  digest; `auto_accept_recommendation` for the imported package only when
  explicitly unattended.
- Seed / chrome-variant collision inside an interactive triad fails closed
  (`design_spec_seed_collision` / `shell_seed_collision`). Spec-breaking Shell
  → `shell_spec_mismatch`.
- After Baseline confirm: extract widgets into project `widgets.yaml` (first
  mandatory catalog; `derived_from` = that confirmed Baseline prototype).

## Style Skill Routing (Not A Menu)

During Step 1, recommend one `skill_routing` package with capability entries
that include `phase`: `baseline`, `shell`, and/or `later_ui`. Example capability
names: `apple-design`, `impeccable`, `gsap-*` only when motion is in scope and
allowed by `stack_capability_profile`.

- Interactive: present that single recommended package (not a Skill menu) and
  wait for accept / customize before locking.
- Unattended: adopt the recommendation immediately.

During Steps 2–3, invoke only listed Skills whose `phase` matches the current
step. Do not ask the user which design Skill to install or pick from a menu.
Unknown, `user_only`, install, network/cost, data egress, publish, deploy, and
destructive actions keep their ordinary gates.

## Automatic Design Proposal Contract

For a new project, synthesize one proposal with:

- product type, users, platforms, and real primary journeys;
- `stack_capability_profile` before drawing (allowed / high_cost / forbidden);
- aesthetic direction and decoration level;
- layout and density;
- color approach and Design Token ownership (`token_sources`);
- display, body, data, and code typography roles;
- spacing, shape/elevation, component states, dark/high-contrast behavior;
- motion approach only when stack-allowed;
- App Shell landscape and portrait modes;
- category-safe choices users expect;
- at least two deliberate risks that give this product its own face;
- inspected repository/UI evidence and clearly labeled inference;
- `【增强实现】` notes where HTML is schematic and the target stack will use
  richer widgets.

For an existing product, preserve detected visual language by default. A
material reset is never inferred from missing documentation.

In interactive mode, present this proposal as the recommended design decision
batch and wait before locking Baseline work as user-confirmed. Never turn the
proposal into a menu of Skills, fonts, palettes, or prototype tools.

## Vague Request Mode

1. Restate the desired outcome, affected users, and one concrete example.
2. Separate facts, likely assumptions, and unknowns.
3. Generate safe recommendations for technical defaults only after inspecting
   available repository facts.
4. Ask the smallest batch that can change outcome, scope, acceptance, data,
   UI, security, or automation readiness. Prefer grill-me batches over single
   fields. Every question includes a recommendation. In interactive mode, wait
   after each batch.
5. After each user answer (or unattended auto-accept when explicitly
   unattended), rewrite and read back the same Project Work slot.
6. Offer `accept eligible recommendations` only for explicitly listed
   low-risk items in interactive mode; keep excluded decisions visible; never
   treat the offer itself as acceptance.

## Step-By-Step Mode

- Let the user name any section or field.
- Show its current value, source, unresolved consequences, one recommendation,
  and alternatives; in interactive mode wait for the user’s decision.
- Preserve already confirmed unrelated fields.
- A material change to outcome, scope, acceptance, architecture, data, or
  authorization reopens Project Work and invalidates the prior App confirmation.
- A material change to Shell IA or locked tokens requires a new Design
  Baseline version and fresh visual confirmation.

## Immediate Action Gate

Do not wait for a full interview when the user requests an action. Evaluate the
action immediately:

- `attach_partial_project_work` permits the minimum attachment fields;
- manual milestone/task actions supply the exact dependent paths;
- automatic actions use their fixed App-owned complete-document contract.

Explain returned missing paths in one batch, recommend defaults where safe, and
continue from `recommendedNextSection`. Never ask one missing field per round
when the App already returned several relevant fields. In interactive mode,
still wait for the user’s decision on that recommended batch before confirming
or locking those paths.

## Product Spec Completeness Hard Gate

Thin or uneven product docs still require a complete Project Work product
contract before initialization Done. See
`granoflow-agent-workflow/requirement-intake-and-traceability` and Project Work
`product_spec_coverage`.

During Step 1, after source intake and before Project Work confirm:

1. Build `journey_coverage` and `screen_coverage` from docs; list every silence
   that blocks a primary journey, Baseline screen, critical state, or
   acceptance condition as a decision-changing gap.
2. Interactive: ask → recommend → wait until every required row is adopted or
   explicitly `out_of_scope` with rationale.
3. Unattended (explicit only): recommend and auto-adopt missing required rows;
   record `gap_fills` with `agent_recommendation_adopted`; never mark them
   `user_stated`.
4. Set `product_spec_coverage.status: ready` only when the checklist is all
   true. Otherwise fail closed `product_spec_coverage_incomplete` and do not
   confirm Project Work for automation.
5. Step 2 Baseline screens Must map 1:1 (or documented many-to-one) onto
   `screen_coverage` rows with `baseline_required: true`.

## Capability-Critical Dependency Recommendation Batch

During Step 1, **immediately after** locking `engineering.stack` / frameworks,
recommend concrete third-party packages for every capability-critical product
path. Do not stop at "use Flutter / React / …".

For each capability (e.g. EPUB rendering, local encryption):

- `recommended_value`: exact package name (and ecosystem, e.g. pub.dev /
  npm);
- at least one `alternatives_considered` entry or an explicit note that no
  viable alternative exists;
- short `selection_rationale` (maintenance, platform support, license, size /
  performance);
- after the Mode Gate decision, write the chosen row into
  `engineering.dependencies.approved` with `capability_critical: true`.

Batch all such library choices in one communication when possible.

- Interactive: present recommended + alternatives and wait for the user’s
  decision before writing approved rows as confirmed.
- Unattended (explicit only): adopt recommendations immediately.

Leaving a known critical capability without a named package is
`capability_dependency_unselected` and blocks Project Work confirm / Done.

## Data Persistence Recommendation Batch

During Step 1, always recommend a `data_persistence` value. When the
recommendation is `none`, include the exact `no_database_declaration` text.
When JSON shapes or shared constants exist, recommend attachment file names
(`json_contracts_attachment`, `constants_catalog_attachment`) and draft those
YAML attachments. Never leave "probably no DB" implied.

- Interactive: ask → recommend → wait before locking persistence and treating
  contract attachments as user-accepted.
- Unattended (explicit only): adopt and continue.

## Engineering Baseline

For a software project, read the bundled
`granoflow-agent-workflow/software-structural-budget` reference and complete its
structural-budget selection during Project Definition or repository
initialization. This is not the `Initialize Granoflow` first-run flow.

When the user has not supplied numeric limits, choose them using the reference
precedence and fallback profile, and present source + values as the recommended
structural-budget decision.

- Interactive: ask → recommend → wait for accept / customize before persisting
  the limits as decided.
- Unattended (explicit only): adopt the recommendation automatically without a
  confirmation round trip.

Persist measurement, selected limits, exclusions, legacy policy, enforcement
status, and real gate commands in Project Work. Never label a recorded policy
`configured` until an executable repository gate has been verified; use
`recorded_pending_enforcement` when the current action cannot write the repo.

When the user has not overridden them, recommend official or mainstream rules
for lint, format, type/static checks, tests, directory ownership, dependency
admission, theme tokens, l10n, constants/configuration, error taxonomy,
observability, security/privacy, accessibility, performance, refactoring,
build/release, migration, backup, sync, and rollback. Record the exact source
and keep unresolved defaults blocked when no reliable standard exists. In
interactive mode, include these rule recommendations in a decision batch and
wait; in unattended mode, adopt them.
