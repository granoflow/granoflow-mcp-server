# Project Definition Interaction

Read the shared
'granoflow-agent-workflow/requirement-intake-and-traceability' contract before
extracting user source material. A product document and user stories are the
recommended smallest pair for an individual developer, but their formatting is
never an admission gate. Preserve requirements found under unexpected headings
and ask only for decision-changing gaps.

## Recommendation Contract

For each unresolved field, prefer evidence in this order:

1. explicit user decision;
2. repository rules and inspected code/configuration;
3. official ecosystem standard or official template;
4. mainstream ecosystem convention;
5. labeled Agent recommendation.

Present a compact batch using this semantic shape:

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

Product behavior, aesthetics, permissions, security/privacy posture, data
retention, destructive actions, publishing, deployment, payment, external
messages, and materially different architecture are never silently batch
confirmed.

The design-system branch is the deliberate exception to field-by-field
questioning, not to confirmation. The host proposes one complete coherent
system and one exact prototype baseline. The user confirms that whole visual
direction once or requests a revision. Never turn the proposal into a menu of
Skills, fonts, palettes, or prototype tools.

## Automatic Design Proposal Contract

For a new project, synthesize one proposal with:

- product type, users, platforms, and real primary journeys;
- aesthetic direction and decoration level;
- layout and density;
- color approach and token ownership;
- display, body, data, and code typography roles;
- spacing, shape/elevation, component states, dark/high-contrast behavior;
- motion approach and conditions for complex web motion;
- category-safe choices users expect;
- at least two deliberate risks that give this product its own face;
- inspected repository/UI evidence and clearly labeled inference.

For an existing product, preserve detected visual language by default. A
material reset is never inferred from missing documentation.

## Vague Request Mode

1. Restate the desired outcome, affected users, and one concrete example.
2. Separate facts, likely assumptions, and unknowns.
3. Generate safe recommendations for technical defaults only after inspecting
   available repository facts.
4. Ask the smallest batch that can change outcome, scope, acceptance, data,
   UI, security, or automation readiness.
5. After each answer, rewrite and read back the same Project Work slot.
6. Offer `accept eligible recommendations` only for explicitly listed
   low-risk items; keep excluded decisions visible.

## Step-By-Step Mode

- Let the user name any section or field.
- Show its current value, source, unresolved consequences, one recommendation,
  and alternatives.
- Preserve already confirmed unrelated fields.
- A material change to outcome, scope, acceptance, architecture, data, or
  authorization reopens Project Work and invalidates the prior App confirmation.

## Immediate Action Gate

Do not wait for a full interview when the user requests an action. Evaluate the
action immediately:

- `attach_partial_project_work` permits the minimum attachment fields.
- manual milestone/task actions supply the exact dependent paths;
- automatic actions use their fixed App-owned complete-document contract.

Explain returned missing paths in one batch, recommend defaults where safe, and
continue from `recommendedNextSection`. Never ask one missing field per round
when the App already returned several relevant fields.

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
