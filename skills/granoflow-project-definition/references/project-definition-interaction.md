# Project Definition Interaction

Read the shared
`granoflow-agent-workflow/requirement-intake-and-traceability` contract before
extracting user source material. A product document and user stories are the
recommended smallest pair for an individual developer, but their formatting is
never an admission gate. Preserve requirements found under unexpected headings
and ask only for decision-changing gaps.

## Activation Boundary

Treat phrases such as `Initialize this project`, `Define this project`,
`初始化这个项目`, and `定义这个项目` as Project Definition. Treat
`Initialize Granoflow` / `初始化 Granoflow` as `granoflow-first-run-import`
only. Do not merge connection/capability-pack setup into this Skill's three
steps.

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

**Interactive mode:** wait for accept / accept-eligible / customize.

**Unattended mode:** adopt `recommended_value` immediately and continue. Do
not re-ask for confirmation of recommendations. Stop only for real blockers
defined by `unattended-interaction-contract` (for example `direction_change`,
`missing_user_only_input`, `forbidden_action`, authorization failures). Soft
preference choices never become wait-for-user loops.

Product behavior, aesthetics, permissions, security/privacy posture, data
retention, destructive actions, publishing, deployment, payment, external
messages, and materially different architecture are never silently batch
confirmed **in interactive mode**. In unattended mode they still require an
explicit recommendation record and may become blockers if no safe
recommendation exists or the action is forbidden.

### Design / Baseline Confirmation Exception

The design-system branch is the deliberate exception to field-by-field
questioning, not to recording a recommendation. The host proposes one complete
coherent system, one Design Baseline package (including Design Tokens and
landscape/portrait App Shell), and one recommended confirmation action.

- Interactive: the user confirms that whole package once or requests a
  revision. Never turn the proposal into a menu of Skills, fonts, palettes, or
  prototype tools.
- Unattended: default confirmation action is
  `auto_accept_recommendation` for the Baseline+Shell package after App
  import/readback, unless a real blocker applies.

## Style Skill Routing (Not A Menu)

During Step 1, lock `skill_routing` with capability entries that include
`phase`: `baseline`, `shell`, and/or `later_ui`. Example capability names:
`apple-design`, `impeccable`, `gsap-*` only when motion is in scope and
allowed by `stack_capability_profile`.

During Steps 2–3, invoke only listed Skills whose `phase` matches the current
step. Do not ask the user which design Skill to install or pick. Unknown,
`user_only`, install, network/cost, data egress, publish, deploy, and
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

## Vague Request Mode

1. Restate the desired outcome, affected users, and one concrete example.
2. Separate facts, likely assumptions, and unknowns.
3. Generate safe recommendations for technical defaults only after inspecting
   available repository facts.
4. Ask the smallest batch that can change outcome, scope, acceptance, data,
   UI, security, or automation readiness. Prefer grill-me batches over single
   fields. Every question includes a recommendation.
5. After each answer (or unattended auto-accept), rewrite and read back the
   same Project Work slot.
6. Offer `accept eligible recommendations` only for explicitly listed
   low-risk items in interactive mode; keep excluded decisions visible.

## Step-By-Step Mode

- Let the user name any section or field.
- Show its current value, source, unresolved consequences, one recommendation,
  and alternatives.
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
when the App already returned several relevant fields.

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
- write the chosen row into `engineering.dependencies.approved` with
  `capability_critical: true`.

Batch all such library choices in one communication when possible. Unattended
mode adopts recommendations immediately. Leaving a known critical capability
without a named package is `capability_dependency_unselected` and blocks
Project Work confirm / Done.

## Data Persistence Recommendation Batch

During Step 1, always recommend a `data_persistence` value. When the
recommendation is `none`, include the exact `no_database_declaration` text.
When JSON shapes or shared constants exist, recommend attachment file names
(`json_contracts_attachment`, `constants_catalog_attachment`) and create those
YAML attachments before Baseline work. Never leave "probably no DB" implied.

## Engineering Baseline

For a software project, read the bundled
`granoflow-agent-workflow/software-structural-budget` reference and complete its
structural-budget selection during Project Definition or repository
initialization. This is not the `Initialize Granoflow` first-run flow.

When the user has not supplied numeric limits, choose them automatically using
the reference precedence and fallback profile. Show the source and values as an
initialization notice, but do not ask for confirmation. Persist measurement,
selected limits, exclusions, legacy policy, enforcement status, and real gate
commands in Project Work. Never label a recorded policy `configured` until an
executable repository gate has been verified; use
`recorded_pending_enforcement` when the current action cannot write the repo.

When the user has not overridden them, recommend official or mainstream rules
for lint, format, type/static checks, tests, directory ownership, dependency
admission, theme tokens, l10n, constants/configuration, error taxonomy,
observability, security/privacy, accessibility, performance, refactoring,
build/release, migration, backup, sync, and rollback. Record the exact source
and keep unresolved defaults blocked when no reliable standard exists.
