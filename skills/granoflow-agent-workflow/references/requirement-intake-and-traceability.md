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

At Project Definition and requirement review, route through Project Work
`review_routing`. Map `prd-review` findings into the existing requirement
ledger as decisions, gaps, risks, or evidence references. The review report is
evidence only; it must not become a second product source of truth. If the
preferred reviewer is unavailable, record native fallback evidence.

For UI software projects, extract platform and compatibility statements into
Project Work `platform_support_matrix`. Record explicit rows for iOS, Android,
macOS, and Windows even when unsupported. Preserve exact OS/API/SDK versions,
device classes, orientations, window constraints, layout families, and source
refs. Missing values become Project Definition decisions; do not defer them to
Task Analysis.

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
2. Every **adopted** journey has a completed **flow decomposition** pass and an
   explicit conclusion (`split` / `keep_cohesive` / `needs_user_decision`).
   Draw the **operation flowchart** first: one user op, or multiple parallel
   ops with only a final confirm → one page (`keep_cohesive`); required
   step-by-step serial gates → multi-page (`split`). **Not** risk labels. See
   `granoflow-project-definition/product-spec-flow-decomposition`. Nested fail
   codes: `flow_decomposition_pass_missing`,
   `flow_decomposition_operation_flow_missing`,
   `flow_decomposition_conclusion_missing`,
   `flow_decomposition_split_without_screens`,
   `flow_decomposition_split_without_serial_gate`,
   `flow_decomposition_keep_with_serial_gates`,
   `flow_decomposition_keep_without_rejected_split`.
3. Every adopted journey acceptance has a beginner-walkable `stress_path`
   (entry → intermediate* → success_exit + failure_exit when negatives apply)
   or fail `journey_stress_path_incomplete`.
4. Every **key page / critical state** found in product docs (and screens
   adopted after a journey `split` conclusion) is listed under
   `product_spec_coverage.screen_coverage` with adopted `requirement_ids` and
   `acceptance_ids`, and linked journey ids. Set
   `screen_inventory.inventory_role: key_pages_from_sources` and
   `completeness: not_portfolio_complete`. These rows are **not tasks** and do
   **not** promise full milestone page coverage. Listing a screen is **not**
   permission to author that screen's full-page HTML during Project Definition.
5. **Screen detail registration (hard):** while building `screen_coverage`,
   scan product docs and user stories for **durable UI details** (chrome
   regions, control groups, states, density, gestures, empty/error affordances).
   When a detail is present, register it under that screen's `ui_details[]`
   with honest `source` / `source_ref`. Silence → leave `ui_details` empty
   (do not invent layout as `from_product_doc`). Adopt
   `product_spec_coverage.screen_detail_registration` before
   `status: ready`. Fail closed `screen_detail_registration_missing` /
   `screen_ui_details_source_invalid`.
6. **Design truth priority (high → low, hard):** when UI details conflict,
   lower ranks Must not override higher ranks without an explicit
   `user_confirmed` adjudication:
   1. `user_confirmed`
   2. `from_product_doc`
   3. `from_user_story`
   4. `inferred` (recorded gap-fill / recommendation already adopted)
   5. `ai_live_inference` (agent inventing detail in the current turn—ephemeral
      until registered with a higher-rank source or user confirm)
7. `product.primary_user_journeys` and `product.critical_states` match those
   coverage tables (no orphan journeys/screens).
8. Open `needs_clarification` / `conflicting` dispositions that affect
   journeys, screens, or acceptance are resolved before initialization Done.
9. Thin-doc silence is not permission to skip: record each fill in
   `product_spec_coverage.gap_fills` with provenance
   (`user_confirmed` interactive, or `agent_recommendation_adopted` only for
   **non-decision-changing** unattended fills). Never relabel invented content
   as `user_stated`. Unattended decision-changing thin-doc gaps fail closed
   `thin_product_doc_gap_requires_user`.
10. For these initialization blockers, `deferred_unknown` is **forbidden**.
    Only non-blocking polish or explicitly out-of-scope items may remain
    deferred.

Mode Gate for fills:

- Interactive: ask → recommend → wait for every missing required coverage row
  and for decision-changing thin-doc / decomposition judgments.
- Unattended (explicit only): auto-adopt non-decision-changing fills only;
  always run decomposition + record conclusion; emit notices; keep provenance
  honest; never silent-complete an underspecified product.

**Init HTML budget (hard):** when `visual_baseline.applicability: required`,
Project Definition ships **Design Spec (Style Guide) + App Shell only**. Do
**not** author a full journey-screen HTML gallery at init. Per-screen
high-fidelity HTML belongs in task `ui_prototype` during Analysis (fitted to
locked Spec tokens + Shell chrome). Refined screens and task summaries belong
in Milestone Work `task_plan`—not by silently inventing init HTML or binding
tasks on Project Work.

Any HTML page that **does** land in the Design Baseline package Must map to a
key-page `screen_coverage` row (or Shell/Spec artifact roles). Unmapped
Baseline pages fail closed as `product_spec_coverage_incomplete`. Init Does
**not** require every key-page row to already have a full-page HTML file.

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

- **Project Work** owns the **current** durable product outcome, users, primary
  journeys, global design direction, data/privacy promises, supported platforms,
  non-goals, project acceptance, source registry, and the canonical requirement
  ledger. This is the only editable product SoT at project scope.
- **Milestone Work** owns this milestone's **task_plan** (refined screens, page
  journeys, task summaries, screen→task freeze) when UI/software portfolio
  authoring applies, plus thin coverage references, dependency/handoff, and
  integration evidence. It **must not** hold a second editable product ledger
  or rewrite `R-*` statements. Key-page inventory stays on Project Work;
  composition SoT for child tasks is Milestone `task_plan`.
- **Task Work** owns the requirement ids implemented or verified by that task,
  task-local interpretation, minimum-change boundary, execution steps, Delivery
  evidence, and **history** of how this task decided or changed things. Product
  truth that still binds later tasks must be written back to Project Work.

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
  screens, acceptance links, flow decomposition conclusions, stress paths,
  screen_detail_registration + ui_details when sources state them, and
  thin-doc gap fills complete);
- milestone/task coverage points to stable requirement and acceptance ids;
- extra requirements remain traceable;
- inferred content is labeled and cannot unlock automation by itself.

Fail closed with the full relevant issue batch, including
`product_spec_coverage_incomplete` when coverage is not ready. Do not ask the
user to complete an entire professional template when only one or two decisions
block the next action—but do not waive the Product Spec Completeness Hard Gate.

## Change And Delivery Reconciliation

When a source changes, mark affected records stale, recompute conflicts and
coverage, and reopen only the decisions whose meaning changed. **Discussion
accepts are sources:** write them back to App slots (Project / Milestone /
Task Work, `ui_prototype`, etc.) per
`discussion-writeback-contract` and `change-impact-fanout` before
Plan/Readiness/Execution rely on them.
At Delivery, report each adopted requirement as delivered, partially delivered,
deferred, superseded, or blocked with actual evidence. A passing test does not
prove that an untraced user requirement was implemented.
