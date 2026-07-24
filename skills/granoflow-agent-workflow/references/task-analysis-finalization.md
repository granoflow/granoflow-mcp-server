# Task Analysis Finalization

This reference owns UI Task Analysis from pre-prototype technical grounding
through final product-behavior acceptance and technical reconciliation.

Load it for every new, reopened, or still-editable UI software task before
authoring HTML, before confirming a Prototype Bundle, before Analysis closes,
and when accepted prototype feedback changes product behavior.

Historical completed records remain readable. They are not bulk-migrated.

## Authority And Responsibility

- Project Work remains the project-wide product source of truth.
- `analysis_logic_draft` proves that the proposed product behavior is grounded
  in current requirements and technical reality before HTML is authored.
- `screen_content_contract` owns what each task screen shows and does.
- The Responsive Prototype Bundle owns the confirmed visual and interaction
  expression of that Content Contract.
- `analysis_technical_package` owns the final logical data, flow, state,
  permission, and UI-to-data model reconciled against the candidate Bundle.
- Planning owns physical tables, columns, indexes, migrations, API endpoints,
  classes, implementation sequencing, tests, and Structural Change Forecast.
- Prototype or Analysis acceptance never grants implementation, commit, push,
  publish, or deploy authorization.

## Fixed Analysis Sequence

1. Read requirements, Project Work, the platform matrix, Design Baseline,
   Widget Catalog, and applicable current code/schema/API evidence.
2. Author and independently review `granoflow_analysis_logic_draft_v1`.
3. Author `granoflow_screen_content_contract_v1` and render a user-readable
   Page Definition Brief from the same digest.
4. Build bidirectional requirement traceability and run the Granoflow Contract
   Grill. Every requirement, acceptance condition, and contract element must be
   mapped; every Grill axis must close without blockers.
5. Interactive mode waits for Content Contract acceptance. Explicit unattended
   mode states the recommendation and records an unattended grant.
6. Generate two primary-layout expressions by default, or three only under the
   existing permitted reason codes. Every option binds the same Content
   Contract digest.
7. Select one expression and expand it to every required layout family as a
   candidate Responsive Prototype Bundle v2.
8. Run Contract-to-Prototype Semantic Review across every contract element and
   required layout family, including deterministic browser, state-capture,
   interaction, AI semantic, and non-mutating visual-quality evidence.
9. Reconcile the candidate Bundle into
   `granoflow_analysis_technical_package_v1`; run an independent engineering
   review before showing the final acceptance surface.
10. Present all final layouts plus the plain-language behavior summary as one
    final user acceptance. The technical appendix is expandable but is not an
    ordinary-user professional-notation approval gate.
11. Complete Widget Promotion, App SHA readback, and the independent final
    verifier. Only then may Analysis pass.

If feedback changes product behavior, return to the earliest invalidated
contract. Never patch only the HTML.

## Analysis Logic Draft

`granoflow_analysis_logic_draft_v1` records:

- task and requirement source refs;
- whether the task extends an existing system or is greenfield;
- current code, schema, and API evidence when the system already exists;
- domain entities and relationships at logical, not physical, granularity;
- `data_disposition: not_applicable|unchanged|extend|breaking` with basis;
- operation workflows, failure paths, state model, permissions, and platform
  constraints;
- feasibility findings and open blocking findings;
- author/reviewer identities, evidence refs, and reviewed digest.

The draft may name existing physical tables or endpoints as evidence. It must
not design new columns, indexes, DDL, migrations, endpoint signatures, classes,
or implementation sequence. Those are Planning decisions.

The canonical digest excludes `draft_sha256`, `status`, and `review`. Review
must cite the exact resulting digest. Author and reviewer must differ.
`status: prototype_ready` requires zero open blockers and a passed review.

## Screen Content Contract

`granoflow_screen_content_contract_v1` records:

- task, Logic Draft, requirement, and acceptance refs;
- every task-owned screen, its purpose, roles, entry conditions, and
  `read_only|interactive` mode;
- ordered content sections and every displayed field, label, source, format,
  required flag, and visibility rule;
- every action, precondition, result, and failure behavior;
- explicit dispositions for `default`, `loading`, `empty`, `error`, `offline`,
  and `permission_denied`;
- navigation entry/exit routes and back behavior;
- permissions, platform exceptions, cross-screen checks, and out-of-scope
  behavior;
- Page Definition Brief ref/SHA and final acceptance metadata.

`default` must be covered. Other baseline states may be `not_applicable` only
with a non-empty rationale. Interactive screens require at least one action.

The canonical digest excludes `content_contract_sha256`,
`confirmation_status`, `accepted_by`, and `authorization_effect`. Interactive
acceptance is `user_confirmed` / `user`; unattended acceptance is
`unattended_auto_adopted` / `unattended_grant`. Authorization effect is always
`none`.

## Requirement Traceability And Contract Grill

`granoflow_requirement_contract_traceability_v1` provides bidirectional proof:

- every `requirement_ref` and `acceptance_ref` maps to one or more contract
  elements;
- every screen, field, data source, action, state, navigation rule, and
  permission has a requirement, acceptance, or explicit derived-rule basis;
- an independent product reviewer approves the exact traceability digest.

Use `prd-review` as the preferred product reviewer when available. Missing or
declined providers use a native product-review fallback with evidence and never
create authorization.

`granoflow_contract_grill_v1` challenges requirements, fields, actions, states,
navigation, permissions, and data sources. Interactive answers come from the
user. Explicit unattended mode states the question, recommendation, and reason,
then records `answer_source: unattended_grant`. Open blocking questions prevent
Content Contract acceptance.

## Responsive Prototype Bundle v2

New and reopened UI tasks use
`granoflow_responsive_prototype_bundle_v2`. It adds:

- `analysis_logic_draft_sha256`;
- `screen_content_contract_sha256`.

Every option and every final layout must preserve the fields, actions, states,
permissions, navigation, and data sources in the bound Content Contract.
Historical v1 Bundles are valid only under `historical_read_only`; continuing
prototype work requires upgrade to v2.

## Contract-To-Prototype Semantic Review

`granoflow_contract_prototype_semantic_review_v1` covers every contract element
in every required layout family. Verified rows include:

- stable HTML `data-contract-ref` markers;
- HTML and screenshot refs with SHA;
- deterministic browser evidence;
- interaction evidence for actions and navigation;
- state captures for states and permission behavior;
- AI semantic review and a distinct final verifier;
- non-mutating visual-quality review.

Use a host plan-design reviewer when it explicitly supports review-only mode;
otherwise use a native visual reviewer. The default gstack `design-review`
workflow may edit and commit, so it must not run in Analysis unless the host
can enforce `mode: review_only` and `mutation_authorization: none`.

`cso` is conditional for authentication, authorization, privacy, secrets,
payments, untrusted input, or sensitive data. It does not replace product or
semantic review. Final `grill-me` remains a user product-behavior acceptance
surface, not technical proof.

## Analysis Technical Package

`granoflow_analysis_technical_package_v1` references the exact Logic Draft,
Content Contract, platform matrix, and candidate Bundle digests. It records:

- final logical data model and schema-impact disposition;
- operation flow, state model, permission model, UI-to-data bindings, and
  platform behavior;
- technical risks;
- reconciliation rows for fields, actions, states, navigation, permissions,
  and data sources;
- a plain-language behavior summary with ref and SHA;
- independent engineering review and independent final verifier evidence;
- final acceptance metadata matching the candidate Bundle.

The package must not contain new physical table/column/index designs, DDL,
migration steps, endpoint signatures, class decomposition, or implementation
sequence. Those belong to Planning.

The canonical digest excludes `technical_package_sha256`, `status`, `review`,
`final_verifier`, `final_acceptance_status`, `accepted_by`, and
`authorization_effect`. Reviewer and verifier must be distinct from the
author, and the verifier must also be distinct from the reviewer.

## Change Classification

| Accepted change                                              | Reopen                                                                                   |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Color, spacing, typography, or presentation-only layout      | Bundle and visual evidence                                                               |
| Field, action, state, navigation, permission, or data source | Content Contract, Bundle, Technical Package                                              |
| Domain relationship, core workflow, or data disposition      | Logic Draft, Content Contract, Bundle, Technical Package                                 |
| Platform matrix, required layout family, or viewport         | Baseline impact review, Content Contract, Bundle, Technical Package, Milestone artifacts |

Each regenerated contract receives a new digest. Old review, acceptance, and
readback evidence remains historical but cannot pass the active gate.

## Planning Handoff

Planning reads the passed Technical Package by SHA. It may reference inherited
operation flows, state models, permissions, and UI-to-data bindings instead of
duplicating them. Planning then adds physical schema/API/class decisions,
verification test cases, external libraries, implementation sequencing, and
Structural Change Forecast.

If Planning discovers the logical package is wrong, it must reopen Analysis
instead of silently overriding product behavior.

## Fail-Closed Codes

- `analysis_logic_draft_required`
- `analysis_logic_draft_incomplete`
- `analysis_logic_draft_blocking_findings`
- `analysis_logic_draft_review_failed`
- `analysis_logic_draft_digest_mismatch`
- `screen_content_contract_required`
- `screen_content_contract_incomplete`
- `screen_content_contract_state_missing`
- `screen_content_contract_acceptance_required`
- `screen_content_contract_digest_mismatch`
- `requirement_contract_traceability_required`
- `requirement_contract_unmapped`
- `contract_element_without_product_basis`
- `requirement_contract_review_failed`
- `requirement_contract_traceability_digest_mismatch`
- `contract_grill_required`
- `contract_grill_open_questions`
- `contract_grill_coverage_incomplete`
- `contract_grill_digest_mismatch`
- `responsive_prototype_bundle_upgrade_required`
- `responsive_prototype_content_mismatch`
- `contract_prototype_semantic_review_required`
- `contract_element_unrendered`
- `contract_state_uncaptured`
- `prototype_interaction_unverified`
- `contract_prototype_layout_coverage_missing`
- `contract_prototype_semantic_mismatch`
- `semantic_reviewer_failed`
- `visual_quality_reviewer_failed`
- `semantic_verifier_failed`
- `contract_prototype_semantic_digest_mismatch`
- `analysis_technical_package_required`
- `analysis_technical_package_physical_design_forbidden`
- `analysis_technical_package_reconciliation_failed`
- `analysis_technical_package_review_failed`
- `analysis_technical_package_verifier_failed`
- `analysis_technical_package_digest_mismatch`
- `analysis_behavior_acceptance_required`
