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
row, data-surface declaration, `skill_routing` / design profile, directory /
module locks, Engineering Acceptance Pack accept, or Design Baseline + App Shell
visual confirmation:

1. **Ask** the decision in plain language (what is being decided and why it
   matters).
2. **Recommend** one `recommended_value` with reason and source (alternatives
   preferred when material).
3. **Wait** for the user’s accept / accept-eligible / customize / reject before
   treating the value as decided.

**Must not** in interactive mode:

- adopt `recommended_value` without an explicit user response to that batch;
- call `granoflow_project_work_confirm` without **Engineering Acceptance Pack**
  browse accept (or valid unattended adopt)—do **not** treat a YAML read-
  through as user acceptance;
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

### App Icon Source Gate (mobile / desktop App)

When Step 1 evidence shows a **mobile or desktop App**, load
`granoflow-agent-workflow/app-icon-source-gate` and include `product.app_icon`
in a decision batch:

1. Scan user-submitted documents for an application icon.
2. If found → record `document_scan_status: found` and path/provenance.
3. If missing → **interactive:** ask the three-way source choice
   (`user_provided` / `ai_generated` / `downloaded_license_clear`) and wait;
   **unattended:** do not invent a source—residual / fail closed
   `app_icon_source_unresolved`.
4. Lint with `lint_app_icon_source_gate.py` before Project Work confirm.

Pure Web/CLI/library projects set `applicability: not_applicable` with basis.

### Design / Baseline Confirmation Exception

The design-system branch is the deliberate exception to field-by-field
questioning for fonts/Skills menus—not to Mode Gate or random seeds.

- **Interactive:** Design Spec uses the two-round HTML contract in
  `design-spec-two-round-selection.md`, then Shell remains a **Triad**. First
  analyze product fit, show the six-dimension HTML chooser, accept a
  `1a2b...` code, then show three complete HTML Specs by default (two only with
  a recorded insufficient-distinct-third reason). One true-random master seed
  is recorded and candidate seeds are reproducibly derived. Shell lots come from
  `draw_visual_lots.py --kind shell` (chrome deck); all options **embed the
  selected Spec tokens** and present product-near chrome + primary surfaces
  (not grey wireframes); only chrome/structure may diverge—no independent
  palette seed. Option-set Preview Gate. Never a menu of Skills/fonts/palettes.
- **Preview Gate branches (interactive):**
  1. **Pick one** → record selection.
  2. **换新批 / request more** → re-draw with `--dedupe ledger` (machine-local
     history, not same-run-only). Skipping dedupe → `visual_lot_dedupe_required`.
  3. **在某套上改 / revise that option** → edit in place; do not re-draw Spec
     seed or swap Shell chrome primary axis unless the user explicitly asks.
- **User-facing presentation (hard):** Preview Gate messages, hub pages, and
  choice tables Must use **plain-language labels** the product owner can
  understand (e.g. “方案 A · 安静钴蓝阅读”). **Do not** show `seed-127`,
  `spec_match`, `ai_challenger_a`, fail-closed code names, or other agent
  bookkeeping in user-visible copy. Keep seeds / option ids only in Project
  Work `design_spec_selection` / `shell_selection`, HTML `meta` / comments for
  agents, and the lot ledger. Violation → `design_spec_user_facing_jargon`.
- **Unattended (explicit only):** **one** Design Spec `spec_match` via
  true-random draw, then **one** Shell `shell_match` that **embeds that
  Spec**—no triad, no challengers, no Spec-breaking Shell seed. Link notices +
  closing digest; `auto_accept_recommendation` for the imported package only
  when explicitly unattended. Link notices still use plain-language titles.
- Seed / chrome-variant collision inside an interactive triad fails closed
  (`design_spec_seed_collision` / `shell_seed_collision`). Hand-invented lots
  → `design_spec_seed_not_drawn`. Spec-breaking Shell → `shell_spec_mismatch`.
  Spec that is a screen gallery instead of a Style Guide →
  `design_spec_wrong_artifact_type`. Shell that omits Spec tokens or is
  wireframe-only → `shell_spec_tokens_missing` / `shell_wireframe_only`.
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
`granoflow-agent-workflow/requirement-intake-and-traceability`, Project Work
`product_spec_coverage`, and
`granoflow-project-definition/product-spec-flow-decomposition`.

During Step 1, after source intake and before Project Work confirm:

1. Build `journey_coverage` and **key-page** `screen_coverage` from docs
   (`screen_inventory.inventory_role: key_pages_from_sources`,
   `completeness: not_portfolio_complete`). These are not tasks and do not
   promise full milestone page coverage. List every silence that blocks a
   primary journey, key-page inventory, critical state, or acceptance
   condition as a decision-changing gap.
2. For every **adopted** key screen: when product docs or user stories state
   durable UI details, register them under `ui_details[]` with
   `source` / `source_ref` (`from_product_doc` / `from_user_story` /
   `inferred` / `user_confirmed`). Adopt
   `screen_detail_registration` (design-truth priority +
   `init_html_policy: design_spec_and_shell_only`). Do not invent layout as
   `from_product_doc`.
3. For every **adopted** journey: **draw the operation flowchart**, mark
   **serial gates** vs parallel ops + final confirm, then record conclusion
   `split` / `keep_cohesive` / `needs_user_decision` and sync
   `screen_ids` / `screen_coverage` when splitting. Attach a beginner-walkable
   `stress_path` per linked acceptance. Do not use risk labels for page count.
4. Interactive: ask → recommend → wait until every required row is adopted or
   explicitly `out_of_scope` with rationale; wait on decision-changing thin-doc
   gaps and on `needs_user_decision` decomposition conclusions.
5. Unattended (explicit only): may recommend and auto-adopt
   **non-decision-changing** missing rows with `agent_recommendation_adopted`;
   must still run the decomposition pass and record a conclusion; must **not**
   silent-auto-accept decision-changing thin-doc gaps → fail closed
   `thin_product_doc_gap_requires_user`. Never invent journeys as `user_stated`.
6. Set `product_spec_coverage.status: ready` only when the checklist is all
   true (including decomposition + stress-path +
   `screen_detail_registration_adopted` flags). Otherwise fail closed
   `product_spec_coverage_incomplete` (or nested decomposition/stress /
   `screen_detail_registration_*` codes) and do not confirm Project Work for
   automation.
7. Steps 2–3 init Baseline package = **Spec Style Guide + App Shell only**.
   Do not author every key page as full-page HTML at init. Any HTML page that
   **is** packaged Must map onto a key-page `screen_coverage` row (or
   Spec/Shell roles). Per-screen hi-fi HTML is task `ui_prototype`; refined
   screens and task summaries are Milestone Work `task_plan`.
8. If product docs or the user state durable **integration-test fixture /
   corpus** rules (fixed seed files, “not app seed”, forbidden substitutes),
   record them under
   `engineering.quality_gates.integration_test_special_requirements` per
   `granoflow-agent-workflow/integration-test-special-requirements`. Empty
   list is valid when no special IT constraints exist. Interactive: ask →
   recommend → wait before inventing corpus paths.
9. Default app signing goal: omit
   `engineering.quality_gates.default_signing_goal` or set `local_dev_run`
   unless the product already requires store / notarized distribution
   (`distribute_store` / `distribute_direct`). Agents follow
   `granoflow-agent-workflow/code-signing-strategy` later (probe host, declare
   scheme, **never ask the user to confirm**).

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

## Directory Structure And Modules Batch

During Step 1, after stack / libraries / data persistence and before AI
self-check, recommend a **skeleton** `engineering.directory_structure` and
`architecture.modules`:

- non-empty `roots` (path + purpose + owner module);
- ownership / naming rules;
- keep `forbidden_catch_all_names` (utils/helpers/managers/coordinators)
  unless the user explicitly grants an exception;
- at least one module with non-null `id` and `responsibility`.

Do **not** invent every leaf file. Empty roots or no valid module →
`directory_structure_unselected` (blocks pack emit and App confirm).

Also set `visual_baseline.applicability` to `required` or `not_applicable`
with basis (align with product type / app-icon Web-CLI-library口径). Unresolved
→ `visual_baseline_applicability_unresolved`.

- Interactive: ask → recommend → wait.
- Unattended (explicit only): adopt and continue.

## AI Self-Check And Engineering Acceptance Pack

Before `granoflow_project_work_confirm`:

1. Load `granoflow-agent-workflow/engineering-acceptance-pack` and
   `markdown-html-acceptance-render`.
2. Run **AI self-check** only (record `init_ai_self_check`). Never dump full
   Project Work YAML as the user acceptance page. Fail →
   `init_ai_self_check_failed`.
3. Project an Engineering Acceptance Pack from YAML / companions
   (`temp/engineering-acceptance-<projectKey>-v<n>.md`). Required sections:
   `frameworks_and_libs`, `directory_structure`, `visual_baseline_plan`.
4. Interactive: render MD→HTML (preferred), emit Engineering Acceptance Link,
   **wait** for browse accept / revise. Unattended: links + digest; Mode Gate
   adopt only.
5. On accept/adopt, record `engineering_acceptance_pack` fields, then
   `granoflow_project_work_confirm` with App hash readback.

Confirm without pack accept → `engineering_acceptance_pack_unconfirmed`.

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
for lint, format, type/static checks, tests, dependency admission, theme
tokens, l10n, constants/configuration, error taxonomy, observability,
security/privacy, accessibility, performance, refactoring, build/release,
migration, backup, sync, and rollback. **Directory ownership** is owned by the
Directory Structure And Modules Batch above (and projected into the Engineering
Acceptance Pack)—do not treat it as an optional soft reminder. Record the exact
source and keep unresolved defaults blocked when no reliable standard exists. In
interactive mode, include these rule recommendations in a decision batch and
wait; in unattended mode, adopt them.
