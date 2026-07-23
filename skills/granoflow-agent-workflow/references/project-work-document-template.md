# Project Work YAML Template

Use this template as the project-level definition and automation-admission
contract. A project may attach and update this document from the first partial
discussion. Partial content is useful evidence and must never be padded with
invented answers.

## Role: current project truth

Project Work holds the project's **latest current** product and admission
contract—not a change-log narrative and not a full copy of user product docs.

- **Update in place** when product truth, acceptance, boundaries, or quality
  rules change; bump `document.document_version` on material change.
- Put process history in Task Work / Delivery / `change_control.amendment_history`
  pointers—not as growing prose in the Project Work body.
- User product documents and user stories are **evidence** under
  `requirement_intake.source_documents`. Extract dispositioned `R-*` /
  `product_spec_coverage` / `acceptance` rows; **do not paste** full product
  manuals or user-story books into this YAML.

### Layered fill (do not flatten)

| Layer                              | Typical sections                                                                                           | Rule                                                         |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Charter / current product contract | `identity`, `requirement`, `requirement_intake`, `scope`, `product`, `product_spec_coverage`, `acceptance` | Keep as adjudicated current truth with provenance            |
| Engineering locks                  | `repositories`, `engineering.*` (stack, deps, data attachments, theme, quality gates)                      | Lock early; change via reopen/confirm when material          |
| Automation admission               | `automation`, `action_requirements`, `readiness`, `confirmation`                                           | Gate automatic actions; never invent grants                  |
| Companion artifacts                | `artifacts` + named attachments below                                                                      | Current slots with SHA readback; not a second product ledger |

The attachment gate and the automation gate are deliberately different:

- `attachment` may be `ready` while the document is `partial`;
- a manual milestone or task request checks only the fields that the requested
  definition actually depends on;
- automatic milestone creation, task execution or completion, project
  continuation, publishing, and project completion require a complete,
  confirmed, current document;
- missing data returns `project_document_incomplete` with exact field paths,
  reasons, suggested defaults, and confirmation requirements;
- the App and Local HTTP API own the attachment, revision, validation, and
  readback truth. MCP remains a thin interface and must fail closed while that
  app-owned capability is unavailable.

Project Work is a living **current** project contract, not a one-time setup
form. At task completion, milestone review, release preparation, and before a
commit that changes behavior or a quality gate, compare the implementation and
gate output with this document. If the current state, boundary, rationale,
commands, acceptance evidence, or quality rules changed, update the same Project
Work attachment, increment its document version when the change is material, and
obtain the required App-owned validation/readback before relying on it again.
Never restore code to satisfy a stale Project Work rule without first checking
whether the rule itself is obsolete. A mismatch must be reported as a document
refresh or conflict, not silently resolved by reverting the implementation.

### Mid-flight verification upgrades

When discussion discovers a high-risk or error-prone point, or the user states
an extra test mandate: after user confirmation, update
`acceptance.conditions` and `acceptance_coverage` on **this** document (current
truth). Prefer `required_evidence` entries such as `integration_test`,
`e2e_or_manual`, and `screenshot_checkpoint`; set `manual_acceptance_required`
when E2E automation is too hard. Record the discovery and writeback on the
triggering Task Work (history). Do not leave the mandate only in chat.

### Design Baseline pointer

`engineering.theme_and_design_system.prototype_template` holds the **current**
confirmed Design Baseline ids/SHA only. Do not dump per-task prototype history
into Project Work; task `ui_prototype` slots own task-level packages.

Store secret availability or a private reference only. Never store tokens,
passwords, OTPs, recovery codes, auth URLs, or credential values.

## Companion attachments (not a fourth product Work)

These App-owned attachments support engineering and verification. They are
**not** a second product journey/acceptance ledger—that stays in Project Work
above. Task Work / Delivery hold history and evidence.

| Attachment                         | Purpose                                         | Effect on development                                          |
| ---------------------------------- | ----------------------------------------------- | -------------------------------------------------------------- |
| `project_snapshot.yaml`            | Code/module status quo, next step, blockers     | Hard Gate before first software edit (`project_context_*`)     |
| `project_rules.yaml`               | Durable boundaries, prefs, `interaction_style`  | Same Hard Gate; not product acceptance SoT                     |
| Design Baseline (App package)      | Project visual/IA authority + token refs        | Definition Done; task prototypes `derivedFrom` exact SHA       |
| Design Tokens (`token_sources`)    | Color/type/spacing                              | Contract-fidelity basis                                        |
| `widgets.yaml`                     | Reusable widget **contracts** (not full HTML)   | Mandatory after Baseline confirm; reuse or `widget_*`          |
| Task/milestone `ui_prototype`      | Task UI authority (clickable HTML package)      | Ready before Readiness; Phase A/B fidelity                     |
| `data-model.md`                    | Entities/tables when DB applies                 | Update in same task as schema changes or `data_artifact_stale` |
| `data-contracts.yaml`              | JSON/structured file shapes                     | Same                                                           |
| `constants-catalog.yaml`           | Shared constants catalog                        | Same                                                           |
| `workflows.md`                     | Flow diagrams + notes                           | Consistency with data-model / acceptance                       |
| Task Delivery / acceptance reports | Actual outcomes and evidence                    | Completion path                                                |
| IT/E2E campaign artifacts          | Suite plans, coverage, evidence packs, closings | Stages 6–7; incomplete hard rows block bare green              |

See also `project-context-attachments.md` and project-definition
`project-artifact-workflows.md`.

```yaml
schema: granoflow_project_work_v1

document:
  document_type: project_work
  project_id: null
  document_version: 1
  supersedes: null
  # partial | complete | confirmed | reopened
  status: partial
  created_at: null
  updated_at: null
  attachment_id: null
  attachment_revision: null
  attachment_sha256: null

schema_contract:
  strict_known_contract: true
  unknown_fields: preserve
  null_means_missing: true
  empty_collection_means_missing_when_required: true
  schema_resource: null
  schema_resource_required_before_live_validation: false
  validation_owner: granoflow_app_action_aware_v1
  enum_policy: reject_unknown_value
  conditional_requirements_are_action_aware: true
  minimum_collection_sizes:
    acceptance.conditions: 1
    repositories: 1
  invariants:
    - "document.document_version must be a positive integer"
    - "confirmed_document_version must equal document.document_version before automation"
    - "App-owned confirmed_content_sha256 metadata must match current App readback before automation"
    - "every acceptance_coverage.acceptance_id must resolve to acceptance.conditions"
    - "product_spec_coverage.status must be ready before complete_confirmed_current"
    - "every product_spec_coverage.journey_coverage adopted row needs requirement_ids and acceptance_ids"
    - "every product_spec_coverage.journey_coverage adopted row needs decomposition pass + conclusion"
    - "every product_spec_coverage.journey_coverage adopted acceptance needs stress_path"
    - "every product_spec_coverage.screen_coverage baseline_required adopted row needs requirement_ids and acceptance_ids"
    - "every accountable milestone must belong to this project"
    - "every automatic action requires a current authorization disposition"
  compatibility:
    backward_read: required
    unknown_future_schema: fail_closed
    unknown_fields_in_current_schema: preserve_without_admission_effect
    migration_required_for_breaking_change: true

project_lifecycle:
  # draft | needs_input | confirmed | active | completion_review | completed | stopped
  state: draft
  allowed_transitions:
    draft:
      - needs_input
      - confirmed
      - stopped
    needs_input:
      - confirmed
      - stopped
    confirmed:
      - active
      - needs_input
      - stopped
    active:
      - needs_input
      - completion_review
      - stopped
    completion_review:
      - active
      - completed
      - stopped
    completed: []
    stopped:
      - needs_input
  transition_evidence_required: true
  completed_requires_final_app_api_readback: true

identity:
  title: null
  summary: null
  project_type: null
  domain: null
  owners: []
  stakeholders: []

agent_preferences:
  # Project values override MCP-local defaults field by field.
  # Missing fields use local defaults, then newcomer-safe defaults.
  audience: beginner
  explanation: detailed
  execution_mode: interactive
  git:
    # Missing Git never creates a mandatory choice or installation request.
    missing_notice: once
    # ask | current_branch | develop | git_flow
    workflow: ask
    checkpoint_enabled: false
    checkpoint_trigger: after_required_tests
    task_owned_files_only: true
    push: false
  safety:
    preferences_never_authorize:
      - push
      - publish
      - deploy
      - delete
      - login
      - secrets
      - destructive_git_history

requirement:
  original_request: null
  problem: null
  target_users: []
  desired_outcome: null
  user_value: null
  success_metrics: []
  constraints: []
  assumptions: []
  unknowns: []

requirement_intake:
  # User inputs are evidence, not forms. Exact filenames/headings are optional.
  contract_reference: granoflow-agent-workflow/requirement-intake-and-traceability
  recommended_minimum_user_inputs:
    - product_document
    - user_stories
  separately_required_user_inputs: []
  team_development_plan_required: false
  source_documents:
    - id: null
      kind: product_document | user_stories | chat | note | screenshot | other
      title_or_filename: null
      source_type: user_provided | inspected
      revision_or_sha256: null
      read_status: unread | partial | complete
      provenance: null
  requirements:
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
  gaps:
    decision_changing: []
    safe_assumptions: []
    deferred_unknowns: []
  extra_content_preserved: []
  conflict_summary: []
  all_material_sources_read: false
  all_material_statements_dispositioned: false
  every_adopted_requirement_has_one_primary_owner: false

scope:
  included: []
  excluded: []
  non_goals: []
  supported_platforms: []
  compatibility_commitments: []
  delivery_surfaces: []

product:
  primary_user_journeys: []
  critical_states: []
  failure_experience: []
  accessibility_standard: null
  privacy_classification: null
  legal_or_store_constraints: []
  # App Icon Source Gate (mobile/desktop App only).
  # Load granoflow-agent-workflow/app-icon-source-gate.
  # Lint: scripts/lint_app_icon_source_gate.py
  # Fail closed: app_icon_source_gate_unread / app_icon_source_unresolved / ...
  app_icon:
    applicability: required | not_applicable
    applicability_basis: null
    document_scan_status: found | missing | not_scanned
    source_choice: user_provided | ai_generated | downloaded_license_clear | unresolved | not_applicable
    asset_path: null
    license_note: null
    user_decision_recorded: false

# Hard gate for thin or uneven product docs. Initialization Done and
# complete_confirmed_current automation require status=ready.
# Fail closed: product_spec_coverage_incomplete (plus nested fail codes below).
# Flow shape: operation flowchart → serial gates vs parallel ops → page count.
# Not risk labels. Detail: granoflow-project-definition/product-spec-flow-decomposition.
product_spec_coverage:
  status: incomplete | ready
  fail_closed_code: product_spec_coverage_incomplete
  # How gaps from thin product docs were closed for initialization.
  fill_policy:
    interactive: ask_recommend_wait_for_every_missing_required_row
    # Unattended must still run decomposition; must not silent-complete thin
    # decision-changing product gaps. Prefer residual / fail closed over fake ready.
    unattended_explicit_only:
      non_decision_changing_gaps: recommend_and_auto_adopt_with_provenance
      decision_changing_gaps: fail_closed_thin_product_doc_gap_requires_user
      flow_decomposition: always_run_pass_and_record_conclusion
    never_invent_as_user_stated: true
    deferred_unknown_forbidden_for_initialization_blockers: true
  # Every primary journey the product must support (from docs or gap-fill).
  journey_coverage:
    - journey_id: J-001
      title: null
      requirement_ids: []
      acceptance_ids: []
      source_refs: []
      # user_stated | recommended_gap_fill | user_confirmed_gap_fill
      provenance: null
      screen_ids: []
      critical_state_ids: []
      disposition: adopted | needs_clarification | out_of_scope
      # Mandatory once disposition=adopted. Operation-flow / serial-gate driven.
      decomposition:
        pass_completed: false
        # Draw first: user ops, waits, decision points.
        operation_flow:
          summary: null
          user_operations: []
          # Groups of ops completable on one surface before a final confirm.
          parallel_groups: []
        # Mid-flow stops that force the next page; empty ⇒ one-page candidates.
        serial_gates: []
        # true when multiple ops need no mid-flow gate (only final confirm).
        parallel_ops_ok: null
        candidate_screens: []
        # split | keep_cohesive | needs_user_decision
        conclusion: null
        concluded_screen_ids: []
        # Required when conclusion=keep_cohesive
        rejected_split_summary: null
        # Required when conclusion=split
        accepted_split_summary: null
      # One stress_path per linked acceptance_id (beginner-walkable).
      stress_paths:
        - acceptance_id: null
          entry: null
          intermediate: []
          success_exit: null
          failure_exit: null
  # Every user-visible screen / critical state Baseline must show.
  screen_coverage:
    - screen_id: S-001
      title: null
      journey_ids: []
      requirement_ids: []
      acceptance_ids: []
      baseline_required: true
      critical_states: []
      source_refs: []
      provenance: null
      disposition: adopted | needs_clarification | out_of_scope
  # Explicit gap fills when product docs were silent or too thin.
  gap_fills:
    - gap_id: G-001
      missing_topic: null
      decision_changing: true
      recommended_value: null
      resolved_value: null
      mode: interactive | unattended
      provenance: user_confirmed | agent_recommendation_adopted
      linked_journey_ids: []
      linked_screen_ids: []
      linked_acceptance_ids: []
  checklist:
    all_primary_journeys_listed: false
    every_journey_has_requirement_and_acceptance: false
    every_adopted_journey_decomposition_pass_completed: false
    every_adopted_journey_has_decomposition_conclusion: false
    every_adopted_acceptance_has_stress_path: false
    every_baseline_required_screen_listed: false
    every_screen_has_requirement_and_acceptance: false
    no_open_decision_changing_gaps: false
    no_conflicting_undisposed_requirements: false
    thin_doc_gap_fills_recorded: false
    no_unattended_decision_changing_thin_gap_auto_accept: false

acceptance:
  conditions:
    - id: A1
      statement: null
      required_evidence: []
      authoritative_surface: null
      integration_check: null
      manual_acceptance_required: false
      result: pending
  false_success_guards: []
  regression_requirements: []
  project_completion_review_required: true

repositories:
  - id: primary
    path: null
    purpose: null
    authoritative_branch: null
    write_ownership: []
    allowed_paths: []
    prohibited_paths: []
    related_repositories: []
    commands:
      inspect: []
      run: []
      lint: []
      format_check: []
      type_or_static_check: []
      test: []
      full_gate: []
      build: []
      release: []

engineering:
  standards_profile:
    resolution_order:
      - user_confirmed
      - existing_project_rule
      - official_standard
      - official_template
      - mainstream_ecosystem_standard
    selected_sources: []
    unresolved_default_policy: block

  stack:
    languages: []
    frameworks: []
    runtimes: []
    package_managers: []
    databases: []
    deployment_targets: []
    version_constraints: []

  architecture:
    style: null
    module_principles:
      - "Each module has one explainable responsibility and one small Interface."
      - "Dependencies cross declared seams through explicit adapters."
      - "Side effects and unique write owners are explicit."
    modules:
      - id: null
        responsibility: null
        owned_data: []
        interface: []
        allowed_dependencies: []
        forbidden_dependencies: []
        side_effects: []
        adapters: []
        verification_surface: null
    dependency_direction: []
    unique_write_owners: []
    external_seams: []
    internal_seams: []

  directory_structure:
    roots: []
    ownership_rules: []
    naming_rules: []
    generated_paths: []
    forbidden_catch_all_names:
      - utils
      - helpers
      - managers
      - coordinators
    exceptions: []

  dependencies:
    # Step 1 (after stack): select every capability-critical third-party library
    # before Project Work confirm. A capability-critical library is one without
    # which a primary product path cannot ship (example: EPUB parse/render for
    # an EPUB reader; crypto for an encrypted-book app). Framework choice alone
    # (e.g. Flutter) is not enough—name the concrete packages.
    # Non-critical helpers may be added later in tasks; do not leave critical
    # capability libraries as "decide during implementation".
    # Missing required selections => capability_dependency_unselected.
    approved:
      - name: null
        # Stable capability id, e.g. epub_rendering | local_encryption | embedded_db
        capability: null
        # true for product-path-critical libraries selected in Project Definition
        capability_critical: true
        purpose: null
        # Packages considered and rejected (name + one-line reason)
        alternatives_considered: []
        selection_rationale: null
        version_policy: null
        license: null
        security_policy: null
        size_or_runtime_cost: null
        owner: null
    # Explicit empty list only when the product truly has no third-party
    # capability libraries beyond the stack itself—and state why in
    # no_capability_dependency_declaration.
    no_capability_dependency_declaration: null
    admission_rules: []
    prohibited_sources: []
    upgrade_policy: null
    deprecation_policy: null

  # Runtime honesty for user-visible third-party capabilities (TTS, push,
  # camera, …). Package selection stays in dependencies.approved above; this
  # matrix owns required_platforms / probe / fallback / ship_bar claims.
  # See third-party-capability-matrix.md. Missing user-visible rows when
  # primary journeys need them => third_party_capability_matrix_incomplete.
  # Claiming “全平台可用” while any required platform is unprobed/unavailable
  # => third_party_capability_overclaim.
  third_party_capabilities:
    schema: granoflow_third_party_capabilities_v1
    contract_loaded: true
    # not_started | incomplete | complete | not_applicable
    status: not_started
    # Required when status=not_applicable
    no_user_visible_third_party_declaration: null
    rows: []
    # Example row:
    # - capability: tts
    #   library: <approved name>
    #   user_visible: true
    #   required_platforms: [ios, android, macos]
    #   probe_method: runtime_call
    #   fallback: "Show TTS-unavailable state; reading continues"
    #   in_ship_bar: true
    #   probe_by_platform: { ios: unprobed, android: unprobed, macos: unprobed }
    #   ao_ids: []
    #   residual_code: null

  data_and_migrations:
    # Set during Project Definition Step 1. none => no business DB / no table
    # design; must set no_database_declaration (explicit prose). Do NOT embed
    # full field schemas, JSON shapes, or constant catalogs in this YAML—
    # those live in project attachments named below / in artifacts.*.
    # data_persistence: none | local_files | embedded_db | server_db | mixed
    data_persistence: null
    no_database_declaration: null
    # When data_persistence is none, use a clear statement such as:
    # "本项目无业务数据库，无需设计表结构。" / "This project has no business
    # database; no table schema design is required."
    # Attachment file names (project-owned). null | not_applicable | <name>
    data_model_attachment: null
    json_contracts_attachment: null
    constants_catalog_attachment: null
    authoritative_sources: []
    # Index-only entity names/owners if useful—never full column dumps here.
    models: []
    storage_boundaries: []
    sync_and_conflict_policy: null
    schema_version_policy: null
    migration_policy: null
    backfill_policy: null
    rollback_policy: null
    deletion_and_archive_policy: null
    old_data_compatibility: null
    time_and_timezone_policy: null
    idempotency_policy: null
    # Code that changes DB / JSON shapes / shared constants MUST update the
    # matching project attachment in the same task before Delivery. Mismatch
    # fails closed as data_artifact_stale.
    code_must_match_data_attachments: true

  theme_and_design_system:
    owner: null
    # Paths to companion Design Tokens (DTCG-oriented JSON or equivalent).
    # Do not embed the full token graph in this YAML.
    token_sources: []
    # Project widget catalog (contract only). Default file: widgets.yaml.
    # Visual truth stays in confirmed prototypes; catalog records reusable
    # chrome/control/pattern contracts + derived_from Baseline/task prototypes.
    # First mandatory write after Baseline confirm; incremental after later
    # confirmed prototypes. Missing after Baseline confirm =>
    # widget_catalog_required.
    widgets_attachment: null
    # Documented fields below (stack_capability_profile, acceptance_fidelity,
    # implementation_notes) are preserved by unknown_fields:preserve when the
    # App schema is older. Prefer writing them during Project Definition.
    # stack_capability_profile example:
    #   allowed: [material_navigation_rail, cupertino_sheet]
    #   high_cost: [custom_shader_blur]
    #   forbidden: [web_only_css_grid_as_primary_shell]
    # Lock stack_capability_profile before authoring Design Baseline HTML.
    stack_capability_profile:
      allowed: []
      high_cost: []
      forbidden: []
    # Acceptance bar for later prototypes/code vs confirmed Design Baseline.
    # Must: Shell IA, tokens, main-path regions. Not pixel/motion 1:1.
    acceptance_fidelity: contract_fidelity
    # Schematic HTML that the target stack will improve with richer widgets.
    # Each note should name the intended component and Must invariants.
    implementation_notes: []
    color_policy: null
    typography_policy: null
    spacing_policy: null
    shape_and_elevation_policy: null
    animation_policy: null
    component_state_policy: null
    dark_and_high_contrast_policy: null
    responsive_breakpoints: []
    shared_component_policy: null
    page_local_override_policy: prohibited_by_default
    design_profile:
      # Stable project-level lock. Interactive: Design Spec triad of Style
      # Guide / Design Tokens boards (distinct random seeds; not full journey
      # screen galleries) then Shell triad fitted to selected Spec (chrome
      # variants only). Unattended: one random-seed Style Guide spec_match +
      # one Spec-fitted shell_match. Journey screens enter Baseline after
      # Spec+Shell. From Shell onward style converges. Never a Skills menu.
      id: null
      version: 1
      # proposed | locked | reopened
      status: proposed
      product_type: null
      platforms: []
      aesthetic:
        direction: null
        decoration: null
      layout:
        approach: null
      color:
        approach: null
      typography:
        display: null
        body: null
        data: null
      spacing:
        base_unit: null
        density: null
      motion:
        approach: null
      safe_choices: []
      deliberate_risks: []
      source_evidence: []
    # After Spec/Shell rounds (see project-artifact-workflows Mode split).
    design_spec_selection:
      mode: interactive_triad | unattended_single
      selected_option_id: null # spec_match | ai_challenger_a | ai_challenger_b | null when single
      seed: null
      candidates: [] # interactive: three entries with distinct seeds
      provenance: user_selected | unattended_spec_match_random_seed | null
    shell_selection:
      mode: interactive_triad | unattended_single
      selected_option_id: null
      # chrome-variant id when interactive; not an independent palette seed
      chrome_variant_id: null
      fitted_to_design_spec_option_id: null
      candidates: []
      provenance: user_selected | unattended_shell_match_fitted_to_spec | null
    skill_routing:
      profile_id: granoflow_product_design_v1
      profile_version: 1
      # capabilities[].phase: baseline | shell | later_ui (plus task phases
      # when reused). Lock in Project Definition Step 1; invoke by phase in
      # Steps 2–3. Never present a style-Skill menu to the user.
      # Example capability entry:
      #   - skill: apple-design
      #     phase: [baseline, shell]
      #     invocation_mode: model_allowed
      capabilities: []
    prototype_template:
      # App-owned Design Baseline exact reference. Never resolve "latest".
      # Package must include Design Tokens refs + landscape/portrait App Shell.
      # Authority for later milestone/task prototypes and code acceptance.
      prototype_id: null
      version_id: null
      package_sha256: null
      manifest_schema: granoflow.prototype
      manifest_schema_version: 1
      manifest_version: null
      entry: null
      link_entity_type: project
    visual_confirmation:
      # Interactive: after Spec triad + Shell triad picks (distinct random
      # seeds). Unattended: after single random-seed spec_match + shell_match;
      # default auto_accept_recommendation only when explicitly unattended.
      status: pending
      proposal_sha256: null
      template_package_sha256: null
      confirmed_at: null

  localization:
    required: true
    framework: null
    source_locale: null
    supported_locales: []
    fallback_locale: null
    user_visible_strings_must_use_l10n: true
    sentence_concatenation_allowed: false
    locale_aware_dates_numbers_currency_units: true
    plural_gender_and_interpolation_policy: null
    rtl_policy: null
    missing_translation_policy: null
    test_locator_policy: semantic_not_copy_literal

  constants_and_configuration:
    magic_values_allowed: false
    domain_values_must_be_typed: true
    shared_values_need_one_owner: true
    centralized_categories:
      - design_tokens
      - routes
      - storage_keys
      - event_names
      - endpoints
      - timeouts
      - retry_policies
      - feature_flags
      - business_thresholds
      - regular_expressions
    environment_configuration_policy: null
    trivial_local_literal_policy: null

  error_and_observability:
    error_taxonomy: []
    user_message_policy: null
    internal_diagnostic_policy: null
    structured_logging_policy: null
    production_print_allowed: false
    redaction_policy: null
    retry_and_backoff_policy: null
    health_checks: []
    metrics_and_traces: []
    correlation_policy: null

  security_and_privacy:
    threat_model_required: false
    data_classification: []
    authentication_owner: null
    authorization_owner: null
    least_privilege_policy: null
    secret_storage_policy: null
    input_validation_policy: null
    output_encoding_policy: null
    filesystem_and_path_policy: null
    retention_export_and_deletion_policy: null
    third_party_data_flows: []
    permission_and_disclosure_gates: []

  accessibility:
    standard: null
    keyboard_policy: null
    focus_policy: null
    screen_reader_policy: null
    touch_target_policy: null
    dynamic_text_policy: null
    reduced_motion_policy: null

  performance_budgets:
    startup: null
    interaction_latency: null
    api_latency: null
    memory: null
    storage: null
    package_size: null
    network: null
    measurement_commands: []
    regression_thresholds: []

  quality_gates:
    lint: []
    format_check: []
    type_or_static_check: []
    unit_tests: []
    module_tests: []
    integration_tests: []
    # User/project special constraints for authoring + campaign IT.
    # Empty list = no extra constraints beyond Task Integration Test Policy.
    # Schema and enforcement: integration-test-special-requirements.md
    # Unknown older App schemas: preserve_without_admission_effect until upgraded.
    integration_test_special_requirements:
      - id: null # e.g. ITR-001
        kind: seed_corpus | fixture_paths | forbidden_substitute | run_constraint | other
        statement: null
        corpus_paths: [] # required when kind=seed_corpus
        not_app_seed: false # true => corpus is NOT production/app seed
        app_seed_paths: [] # production seed paths kept distinct
        forbidden_substitutes: [] # e.g. randomly_generated_fake_epub_as_primary_corpus
        applies_when: [] # multi_book_library_it | folder_import_it | bookshelf_with_real_books_it | campaign_suite | all_authored_it | other:<label>
        product_doc_refs: []
        source_refs: []
        provenance: user_stated | recommended | inferred | null
        enforcement: fail_closed | advisory
    # Stage-6 campaign artifacts (paths or attachment ids):
    # integration_suite_plan: null
    # integration_campaign_change_report: null
    # integration_campaign_closing_summary: null
    # e2e_campaign_coverage_matrix: null
    # e2e_campaign_suite_plan: null
    # e2e_campaign_evidence_pack: null
    # e2e_campaign_closing_summary: null
    # e2e_tests: [] # optional explicit UI entrypoints; coverage still driven by journeys
    #
    # Code signing default for local build/run. Omit => local_dev_run.
    # Agents probe the host and declare code_signing_strategy (never ask the
    # user to confirm). Detail: code-signing-strategy.md
    # default_signing_goal: local_dev_run # local_dev_run | device_debug | distribute_store | distribute_direct
    #
    # Final-stage ship readiness (E2E campaign). Default when omitted at campaign
    # time: market_smoke. Detail: granoflow-e2e-test-campaign/e2e-host-capabilities
    # and e2e-user-flow-coverage (journey × host assignment).
    # ship_bar: market_smoke # market_smoke | form_factor_smoke | full_campaign
    # verification_host_matrix:
    #   schema: granoflow_verification_host_matrix_v1
    #   derived_from: [] # e.g. [scope.supported_platforms]
    #   concurrency: parallel_when_capable # sequential | parallel_when_capable
    #   primary_form_factors: [] # phone_portrait | tablet_landscape | desktop_landscape | web | other:<id>
    #   hosts:
    #     - id: null
    #       kind: desktop | simulator | emulator | physical_device | remote_farm | browser | other
    #       platforms: []
    #       status: unprobed | available | unavailable | deferred_external
    #       residual_code: null
    #   assignment_policy: journey_at_least_one_capable_host
    ui_tests: []
    end_to_end_tests: []
    migration_tests: []
    failure_path_tests: []
    full_gate: []
    required_before:
      task_execution: []
      task_completion: []
      milestone_acceptance: []
      project_completion: []
    evidence_levels:
      implementation: null
      runtime: null
      real_success: null

  structural_budget_and_refactor:
    selection_mode: user | repository | ecosystem | granoflow_fallback
    threshold_source: null
    measurement: physical_lines
    initialization_notice: null
    enforcement_status: unassessed | configured | recorded_pending_enforcement
    enforcement_commands:
      - npm run check
    pre_write_forecast_required: true
    forecast_schema: Structural Change Forecast
    forecast_display: non_confirming_notice_before_first_edit
    # Every planned split must name its responsibility seam.
    forecast_requires_responsibility_seam: true
    # Mechanical line splitting is forbidden.
    file_soft_limits: []
    file_hard_limits: []
    method_soft_limits: []
    method_hard_limits: []
    role_profiles: []
    exclusions: []
    legacy_violation_policy: no_unrelated_cleanup_and_no_touched_growth
    user_confirmation_required_for_technical_defaults: false
    each_file_requires_one_responsibility: true
    each_core_method_requires_one_decision_transformation_or_side_effect: true
    allowed_split_seams:
      - domain_responsibility
      - protocol_or_serialization
      - side_effect
      - storage_or_io
      - ui_composition
      - policy_or_decision
    forbidden_refactors:
      - mechanical_line_split
      - random_helper_extraction
      - threshold_bypass
      - drive_by_refactor
    structural_problem_must_close: true
    minimal_necessary_diff: true

  build_and_release:
    environments: []
    official_run_commands: []
    official_build_commands: []
    ci_gates: []
    hook_gates: []
    version_policy: null
    changelog_policy: null
    artifact_verification: []
    rollback_policy: null
    cloud_truth_readback: []

operations:
  environments:
    - name: development
      purpose: null
      configuration_source: null
      data_policy: null
  configuration_precedence: []
  secret_availability_references: []
  local_setup: []
  health_and_diagnostics: []
  backup_restore_and_disaster_recovery: []

automation:
  allowed_repositories: []
  allowed_actions: []
  prohibited_actions:
    - persist_secret_values
    - infer_external_authorization
    - infer_subjective_acceptance
    - bypass_quality_gates
    - claim_completion_without_readback
  authorization:
    status: not_requested
    confirmed_document_version: null
    grant_reference: null
    granted_by: null
    granted_at: null
    expires_at: null
    commit: not_granted
    push: not_granted
    publish: not_granted
    deploy: not_granted
    permanent_delete: not_granted
    external_message: not_granted
    paid_action: not_granted
  external_capabilities:
    - id: null
      affected_actions: []
      # granted | excluded | interaction_required
      disposition: interaction_required
      availability_reference: null
      interaction_node: null
  budget:
    elapsed_time: null
    monetary_cost: null
    model_or_compute: null
    maximum_parallel_workers: 1
    maximum_attempts_per_strategy: 3
  concurrency:
    default_active_milestones: 1
    conflicting_write_surfaces: []
    lease_policy: null
    heartbeat_policy: null
    optimistic_revision_policy: null
    stale_work_policy: null
  recovery:
    checkpoint_policy: null
    idempotency_policy: null
    bounded_attempt_history: null
    recovery_fingerprint: null
    conflict_reconciliation: reread_authoritative_state
  no_progress_policy:
    attempts_before_replan: 3
    attempts_before_interaction_wait: 4
    require_material_strategy_change: true
    continue_independent_safe_work: true
  stop_conditions: []
  interaction_required_conditions: []
  missing_input_batch_policy: all_currently_relevant_fields_once
  completion_evidence: []

milestone_strategy:
  # Owned with granoflow-portfolio-orchestrator / granoflow-milestone-workflow
  # after Project Definition Done. Empty App portfolio: plan ALL milestones in
  # one pass, persist this section and acceptance_coverage, then create every
  # milestone entity; task authoring is granoflow-task-authoring (create_one).
  # Existing portfolio: amend only for real coverage gaps—do not rebuild.
  # Frontend projects also require confirmed Design Baseline + App Shell before
  # any milestone planning (hard gate).
  outcome_based_decomposition: true
  creation_rules: []
  split_merge_cancel_rules: []
  sequencing_rules: []
  parallelism_rules: []
  # How many milestones may be active for charter/execution at once.
  # Entities for later milestones may still be created while inactive.
  active_milestone_limit: 1
  first_milestone_candidate: null
  first_milestone_analysis_inputs: []
  portfolio_change_policy: null
  charter_change_policy: reopen_project_work
  follow_up_policy: null
  project_completion_conditions: []

acceptance_coverage:
  - acceptance_id: A1
    accountable_milestones: []
    required_evidence: []
    integration_check: null
    authoritative_surface: null
    manual_acceptance_required: false
    result: pending

requirement_coverage:
  - requirement_id: R-001
    primary_owner_layer: project | milestone | task | unassigned
    accountable_milestones: []
    accountable_tasks: []
    acceptance_ids: []
    evidence_refs: []
    result: pending

change_control:
  material_changes:
    - desired_outcome
    - scope
    - non_goals
    - supported_platforms
    - core_stack
    - data_ownership
    - security_or_legal_risk
    - acceptance_conditions
  material_change_effect:
    document_status: reopened
    project_automation_status: blocked
    confirmation_required: true
  non_material_change_policy: null
  conflict_policy: surface_and_request_decision
  amendment_history: []

documentation:
  long_term_documents: []
  decision_records: []
  public_copy_sources: []
  manual_and_user_help: []
  generated_document_policy: null
  backfill_policy: null

defaults:
  resolution_order:
    - user_confirmed
    - existing_project_rule
    - inspected_repository
    - official_standard
    - official_template
    - mainstream_ecosystem_standard
    - agent_recommendation
  unconfirmed_inference_may_unlock_automation: false
  missing_default_policy: block

interaction:
  supported_modes:
    - guided_step_by_step
    - guided_from_vague_request
  current_mode: null
  mode_may_switch_without_new_attachment: true
  ask_smallest_decision_changing_batch: true
  return_all_action_missing_paths_at_once: true
  recommendation_contract:
    value_required: true
    reason_required: true
    source_required: true
    alternatives_required_when_material: true
    custom_allowed_by_default: true
    batch_accept_low_risk_only: true
    excluded_from_batch_accept:
      - product_behavior
      - aesthetics
      - authorization
      - security_and_privacy
      - data_retention_or_deletion
      - publish_or_deploy
      - paid_or_external_action
  pending_decisions: []

artifacts:
  slot_policy: one_current_attachment_per_entity_and_logical_slot
  replacement_requires:
    - optimistic_entity_revision
    - idempotency_key
    - expected_content_sha256
    - app_owned_content_or_hash_readback
  registry: []
  # Each registry row uses:
  # - artifact_id: stable logical id
  # - entity_type: project | milestone | task
  # - entity_id: owning Granoflow entity
  # - logical_slot: project_work | milestone_work | task_work_execution |
  #     task_work_post_completion_revision | task_delivery | ui_prototype |
  #     data_model | json_contracts | constants_catalog | widgets | workflows
  # - attachment_id: App-owned current attachment id
  # - content_sha256: App-owned current content hash
  # - status: partial | current | confirmed | stale | conflicting
  # - source_decision: user-confirmed decision or inspected source reference
  # - related_acceptance_ids: acceptance.conditions ids
  # - file_name: must match data_and_migrations.*_attachment when applicable
  #   or theme_and_design_system.widgets_attachment for widgets
  ui_prototype:
    suggestion_trigger: primary_screens_theme_menu_and_critical_states_are_clear
    preview_surface: host_sidebar_or_browser
    visual_confirmation_required_before_zip_attachment: true
    visual_confirmation_is_implementation_authorization: false
    package_policy:
      root_index_html_required: true
      relative_paths_only: true
      symlinks_allowed: false
      path_traversal_allowed: false
      deterministic_entry_order_and_timestamps: true
      static_resources_must_be_included: true
  data_model:
    owner_entity_type: project
    logical_slot: data_model
    # Default name; Project Work data_and_migrations.data_model_attachment
    # must match when a business database exists. Omit attachment when
    # data_persistence is none (use no_database_declaration instead).
    file_name: data-model.md
    markdown_two_dimensional_tables_required: true
    one_current_attachment: true
    required_when_data_persistence_has_database: true
  json_contracts:
    owner_entity_type: project
    logical_slot: json_contracts
    # YAML (or Markdown embedding YAML) describing JSON / structured file shapes.
    # Not embedded in Project Work body YAML.
    file_name: data-contracts.yaml
    one_current_attachment: true
    required_when_project_defines_json_or_structured_files: true
  constants_catalog:
    owner_entity_type: project
    logical_slot: constants_catalog
    # YAML catalog of shared constant names, values or types, owners, purpose.
    file_name: constants-catalog.yaml
    one_current_attachment: true
    required_when_project_defines_shared_constants: true
  widgets:
    owner_entity_type: project
    logical_slot: widgets
    # Contract catalog only (identity, props, tokens, states, composition,
    # reuse_policy, derived_from confirmed prototypes). Not full visual HTML.
    # theme_and_design_system.widgets_attachment must match when present.
    file_name: widgets.yaml
    one_current_attachment: true
    first_mandatory_after_baseline_confirm: true
    incremental_after_confirmed_prototypes: true
    fail_closed_codes:
      - widget_catalog_required
      - widget_catalog_stale
      - widget_reuse_required
  workflows:
    logical_slot: workflows
    file_name: workflows.md
    one_current_attachment_per_entity: true
    multiple_diagrams_share_one_file: true
    stable_diagram_ids_required: true
    detailed_text_per_diagram_required: true
  consistency:
    registry_sha_must_match_app_readback: true
    prototype_ids_must_resolve_or_be_marked_planned: true
    workflow_data_entities_must_resolve_to_data_model: true
    workflow_acceptance_must_resolve_to_acceptance_conditions: true
    implementation_claims_must_not_exceed_confirmed_artifacts: true
    stale_conflicting_or_missing_artifacts_block_automation: true
    # Code vs data attachments: DB / JSON shapes / shared constants must match
    # the registered project attachments. Drift => data_artifact_stale.
    code_must_match_registered_data_attachments: true
    data_attachment_file_names_must_match_project_work_fields: true

action_requirements:
  attach_partial_project_work:
    document_gate: partial_allowed
    required_fields:
      - schema
      - document.document_type
      - document.document_version
      - identity.title

  create_milestone_manually:
    document_gate: dependency_fields_only
    dependency_resolution: inspect_requested_milestone_semantics
    on_missing: project_document_incomplete

  create_task_manually:
    document_gate: dependency_fields_only
    dependency_resolution: inspect_requested_task_semantics
    on_missing: project_document_incomplete

  create_milestone_automatically:
    document_gate: complete_confirmed_current
    required_sections:
      - requirement
      - scope
      - acceptance
      - repositories
      - engineering
      - automation
      - milestone_strategy
    on_missing: project_document_incomplete

  execute_task_automatically:
    document_gate: complete_confirmed_current
    additional_requirements:
      - automation.authorization
      - engineering.quality_gates.required_before.task_execution
    on_missing: project_document_incomplete

  complete_task_automatically:
    document_gate: complete_confirmed_current
    additional_requirements:
      - engineering.quality_gates.required_before.task_completion
      - automation.completion_evidence
    on_missing: project_document_incomplete

  continue_project_automatically:
    document_gate: complete_confirmed_current
    additional_requirements:
      - automation.authorization
      - automation.stop_conditions
      - automation.recovery
    on_missing: project_document_incomplete

  publish_automatically:
    document_gate: complete_confirmed_current
    additional_requirements:
      - automation.authorization.publish
      - engineering.build_and_release.version_policy
      - engineering.build_and_release.artifact_verification
      - engineering.build_and_release.cloud_truth_readback
    on_missing: project_document_incomplete

  deploy_automatically:
    document_gate: complete_confirmed_current
    additional_requirements:
      - automation.authorization.deploy
      - engineering.build_and_release.ci_gates
      - engineering.build_and_release.rollback_policy
      - automation.completion_evidence
    on_missing: project_document_incomplete

  complete_project_automatically:
    document_gate: complete_confirmed_current
    additional_requirements:
      - acceptance.conditions
      - acceptance_coverage
      - milestone_strategy.project_completion_conditions
      - automation.completion_evidence
      - confirmation
    on_missing: project_document_incomplete

provenance:
  allowed_sources:
    - user_confirmed
    - existing_project_rule
    - inspected_repository
    - official_standard
    - official_template
    - mainstream_ecosystem_standard
    - agent_recommendation
  field_records:
    - path: requirement.problem
      status: unknown
      source: null
      evidence: null
      confirmation_required: true

completeness:
  status: incomplete
  schema_validation: not_run
  required_field_count: 0
  completed_field_count: 0
  missing:
    - path: requirement.problem
      required_for: []
      reason: null
      suggested_default: null
      default_source: null
      requires_user_confirmation: true
  inferred: []
  conflicts: []
  stale_fields: []

readiness:
  attachment:
    status: ready
    blockers: []
  manual_definition:
    status: conditional
    evaluated_action: null
    required_paths: []
    blockers: []
  project_automation:
    status: blocked
    evaluated_document_version: 1
    blockers: []
  schema_validation: not_run
  requirement_completeness: not_run
  product_spec_coverage: not_run
  engineering_baseline: not_run
  acceptance_testability: not_run
  authorization_readiness: not_run
  external_capability_readiness: not_run
  recovery_readiness: not_run

confirmation:
  user_confirmed: false
  confirmed_document_version: null
  confirmed_at: null
  confirmed_by: null
  app_confirmation_metadata_owner: granoflow_app

completion:
  status: not_started
  acceptance_results: []
  cross_milestone_integration_evidence: []
  scope_differences: []
  residuals_and_follow_ups: []
  manual_acceptance_results: []
  final_project_summary: null
  final_app_api_readback: null
  completed_at: null
```

## Validation Rules

1. `partial` is a valid persisted state. Null, unknown, inferred, stale, and
   conflicting fields remain visible and never become confirmation implicitly.
2. A manual milestone or task request resolves the requested definition's field
   dependencies. It blocks only when one of those fields is missing, stale, or
   conflicting.
3. Every automatic create, execute, finish, continue, publish, deploy, or close
   action requires `complete_confirmed_current`. A matching document version and
   App-owned attachment confirmation hash are part of that predicate. The final
   content hash is not embedded in this YAML because doing so would change the
   bytes being hashed.
4. A material charter change sets the document to `reopened`, blocks project
   automation, and requires confirmation of a new version.
5. Project completion requires acceptance coverage, cross-milestone integration,
   manual acceptance where declared, and final App/API readback. Task or
   milestone counts, process exits, summaries, and filenames are progress only.
6. `project_document_incomplete` reports all currently relevant missing paths in
   one batch. Each entry explains why the action needs the field, recommends a
   default when safe, records its source, and says whether user confirmation is
   required.
7. **Product Spec Completeness Hard Gate** (`product_spec_coverage`): Project
   Definition Done and every `complete_confirmed_current` automation action
   require `product_spec_coverage.status: ready`. Thin or uneven product docs
   do not waive this. Missing journeys, Baseline-required screens, acceptance
   links, open decision-changing gaps, missing **flow decomposition** pass /
   conclusion, or incomplete **stress paths** fail closed as
   `product_spec_coverage_incomplete` (see nested codes in
   `product-spec-flow-decomposition`). Decomposition is **operation-flow
   driven**: draw the user-operation flowchart, detect serial gates vs
   parallel ops + final confirm, then conclude `split` / `keep_cohesive` /
   `needs_user_decision` — do **not** use risk labels to force multi-screen.
   Interactive: ask → recommend → wait for missing required rows and for
   decision-changing thin-doc gaps. Unattended (explicit only): may auto-adopt
   **non-decision-changing** fills with `agent_recommendation_adopted`; must
   still run the decomposition pass; decision-changing thin-doc gaps fail
   closed `thin_product_doc_gap_requires_user` — never silent-complete an
   underspecified product. Never relabel invented content as `user_stated`.
   `deferred_unknown` is forbidden for initialization blockers listed under
   `product_spec_coverage.checklist`.
8. Secret values never enter this document. Authorization and external
   capability rows record disposition and availability references only.

## Current Capability Boundary

Granoflow App and Local HTTP API expose an app-owned `project_work` logical
attachment, bounded YAML/SHA readback, explicit confirmation of the current SHA,
manual dependency evaluation, and automatic-action admission. Agents must still
fail closed when capability discovery does not advertise
`granoflow_project_work_v1` and `granoflow_logical_attachments_v1`, or when the
App returns missing fields, stale artifact registry rows, an unconfirmed current
hash, or an unsupported action. Project Work confirmation never authorizes code
execution or a separately gated external action.
