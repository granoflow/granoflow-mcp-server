# Requirement Intake And Traceability

Use this contract when a user supplies product notes, a product document, user
stories, chat exports, screenshots, or any other material that may contain
software requirements. It is the single semantic owner for extracting imperfect
inputs and tracing them through Project Work, Milestone Work, Task Work, and
acceptance evidence.

The inputs are evidence, not forms. Never require the user to rewrite them into
the headings or field order used by Granoflow.

During Project Definition (`granoflow-project-definition`), intake feeds Step 1
Project Work before Design Baseline or App Shell work begins. This is not the
`Initialize Granoflow` first-run import flow.

## Input Expectations

For an individual vibecoding developer, a product document and user stories are
the recommended smallest useful pair because they help the user explain both
intent and real situations. They are not required to use exact filenames,
headings, identifiers, or professional terminology. One document may contain
content normally associated with the other.

Do not require a separate SRS, technical design, data model, UI specification,
test plan, or development plan before intake. Derive proposed engineering,
design, data, verification, milestone, and task contracts from the submitted
evidence, then label every derived statement. A separate team-oriented
Development Plan is not a default user input for an individual developer.

## Source-first Pass

Before filling a template:

1. register each source with a stable id, kind, title or filename, observed
   revision/hash when available, and whether it is user-provided or inspected;
2. extract every material statement regardless of heading or location;
3. retain a short faithful summary and a source locator;
4. classify its epistemic status before deciding where it belongs;
5. compare the sources for omissions, overlap, and contradiction;
6. only then map the requirement to Project, Milestone, or Task Work.

A path, filename, heading, or attachment status proves only identity. It does
not prove content. Read the material before claiming that a requirement exists.

## Requirement Record

Each material requirement uses this semantic shape:

```yaml
- id: R-001
  statement: null
  source_refs: []
  source_locators: []
  epistemic_status: user_stated | inspected_fact | inferred | recommended | unknown
  kind: outcome | user_journey | behavior | design | data | privacy | security | compatibility | performance | accessibility | operational | verification | constraint | non_goal
  disposition: adopted | needs_clarification | conflicting | deferred | out_of_scope | duplicate | inferred
  owner_layer: project | milestone | task | unassigned
  owner_refs: []
  acceptance_ids: []
  conflicts_with: []
  rationale: null
```

- 'user_stated' and 'inspected_fact' may become confirmed evidence.
- 'inferred' and 'recommended' never become user decisions merely because they
  make the document complete.
- 'duplicate' preserves all source refs while naming one canonical record.
- 'out_of_scope' preserves the statement and the confirmed boundary; it is not
  deletion.
- 'conflicting' remains unresolved until a user decision or authoritative
  inspected fact resolves it.

Do not use a numeric confidence score as a substitute for evidence.

## Missing, Extra, And Conflicting Content

Classify gaps into:

- 'decision_changing': missing input could change Outcome, product behavior,
  Scope, acceptance, architecture, data/security semantics, or material risk;
- 'safe_assumption': one reversible evidence-backed default permits bounded
  progress without changing what the user receives;
- 'deferred_unknown': the missing fact is not needed for the current action.

In interactive mode, ask the smallest batch of decision-changing questions;
each batch includes a recommendation and waits for the user to decide. During
Project Definition interactive runs, do not apply `safe_assumption` by writing
confirmed Project Work values—present `recommended_value` and wait (see
`granoflow-project-definition` Mode Gate). In unattended mode (explicit
declaration only), apply the shared unattended interaction contract: continue
with safe assumptions and deferred unknowns, but wait when a real
direction-change or user-only decision remains.

### Product Spec Completeness Hard Gate (initialization)

Product documents and user stories are often thin or uneven. Project Definition
**must** still produce a complete, testable product contract in Project Work
`product_spec_coverage` before Done / `complete_confirmed_current`.

Required coverage (fail closed `product_spec_coverage_incomplete`):

1. Every **primary user journey** is listed under
   `product_spec_coverage.journey_coverage` with adopted
   `requirement_ids` and `acceptance_ids`.
2. Every **Baseline-required screen / critical state** is listed under
   `product_spec_coverage.screen_coverage` with adopted `requirement_ids` and
   `acceptance_ids`, and linked journey ids.
3. `product.primary_user_journeys` and `product.critical_states` match those
   coverage tables (no orphan journeys/screens).
4. Open `needs_clarification` / `conflicting` dispositions that affect
   journeys, screens, or acceptance are resolved before initialization Done.
5. Thin-doc silence is not permission to skip: record each fill in
   `product_spec_coverage.gap_fills` with provenance
   (`user_confirmed` interactive, or `agent_recommendation_adopted`
   unattended). Never relabel invented content as `user_stated`.
6. For these initialization blockers, `deferred_unknown` is **forbidden**.
   Only non-blocking polish or explicitly out-of-scope items may remain
   deferred.

Mode Gate for fills:

- Interactive: ask → recommend → wait for every missing required coverage row.
- Unattended (explicit only): recommend and auto-adopt, emit notices, keep
  provenance honest.

Design Baseline HTML screens Must map to `screen_coverage` rows; unmapped
Baseline screens fail closed as `product_spec_coverage_incomplete`.

Content outside the expected headings is not noise. Preserve extra design
direction, failure behavior, platform limits, privacy promises, examples,
non-goals, and acceptance language as candidate requirements. For example, a
sentence such as “the reading screen should feel as quiet as paper” remains a
design requirement even when it appears under a success-metrics heading.

User stories are scenario evidence and may expose omissions or contradictions
in a product document. They do not automatically override it. When two sources
conflict:

1. record both source refs and the exact incompatible interpretations;
2. explain the user-visible or delivery consequence of each interpretation;
3. recommend one path when evidence supports it;
4. request a decision only when the difference is decision-changing;
5. never silently merge, prioritize, or discard one source.

## Layer Ownership

- Project Work owns durable product outcome, users, primary journeys, global
  design direction, data/privacy promises, supported platforms, non-goals,
  project acceptance, source registry, and the canonical requirement ledger.
- Milestone Work owns the bounded subset of requirement ids, milestone
  acceptance contribution, dependency/handoff coverage, and integration
  evidence. It references canonical records rather than copying their prose.
- Task Work owns the requirement ids implemented or verified by that task,
  task-local interpretation, minimum-change boundary, execution steps, and
  Delivery evidence.

Every adopted requirement has one primary owner layer. Cross-layer tables are
references and coverage, never multiple editable sources of truth.

## Automation Gate

Before automatic decomposition or execution, verify:

- all material source documents were actually read;
- every extracted statement has a disposition;
- every adopted requirement has one owner layer;
- decision-changing conflicts and missing inputs are resolved or represented by
  an explicit interaction boundary;
- `product_spec_coverage.status` is `ready` (journeys, Baseline-required
  screens, acceptance links, and thin-doc gap fills complete);
- milestone/task coverage points to stable requirement and acceptance ids;
- extra requirements remain traceable;
- inferred content is labeled and cannot unlock automation by itself.

Fail closed with the full relevant issue batch, including
`product_spec_coverage_incomplete` when coverage is not ready. Do not ask the
user to complete an entire professional template when only one or two decisions
block the next action—but do not waive the Product Spec Completeness Hard Gate.

## Change And Delivery Reconciliation

When a source changes, mark affected records stale, recompute conflicts and
coverage, and reopen only the decisions whose meaning changed. At Delivery,
report each adopted requirement as delivered, partially delivered, deferred,
superseded, or blocked with actual evidence. A passing test does not prove that
an untraced user requirement was implemented.
