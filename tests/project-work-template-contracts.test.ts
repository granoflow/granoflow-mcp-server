import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const template = readFileSync(
  "skills/granoflow-agent-workflow/references/project-work-document-template.md",
  "utf8",
);

describe("Project Work YAML template", () => {
  it("covers the full project definition and engineering baseline", () => {
    for (const section of [
      "requirement:",
      "schema_contract:",
      "project_lifecycle:",
      "scope:",
      "product:",
      "agent_preferences:",
      "acceptance:",
      "repositories:",
      "engineering:",
      "operations:",
      "automation:",
      "milestone_strategy:",
      "acceptance_coverage:",
      "change_control:",
      "action_requirements:",
      "completeness:",
      "readiness:",
      "confirmation:",
      "completion:",
    ]) {
      expect(template).toContain(section);
    }

    for (const engineeringContract of [
      "architecture:",
      "directory_structure:",
      "dependencies:",
      "data_and_migrations:",
      "theme_and_design_system:",
      "localization:",
      "constants_and_configuration:",
      "error_and_observability:",
      "security_and_privacy:",
      "accessibility:",
      "performance_budgets:",
      "quality_gates:",
      "structural_budget_and_refactor:",
      "build_and_release:",
    ]) {
      expect(template).toContain(engineeringContract);
    }
    for (const designLock of [
      "design_profile:",
      "skill_routing:",
      "prototype_template:",
      "visual_confirmation:",
      "granoflow_product_design_v1",
      "prototype_id:",
      "version_id:",
      "package_sha256:",
      "token_sources: []",
      "stack_capability_profile:",
      "allowed: []",
      "high_cost: []",
      "forbidden: []",
      "acceptance_fidelity: contract_fidelity",
      "implementation_notes: []",
      "phase: [baseline, shell]",
      "auto_accept_recommendation",
      "landscape/portrait App Shell",
    ]) {
      expect(template).toContain(designLock);
    }
    expect(template).toMatch(/Lock stack_capability_profile before authoring Design Baseline/i);
    expect(template).toMatch(/Never resolve "latest"/i);
  });

  it("stores project-specific Agent and Git preferences without granting external actions", () => {
    for (const contract of [
      "execution_mode:",
      "missing_notice:",
      "workflow: ask",
      "checkpoint_enabled: false",
      "checkpoint_trigger: after_required_tests",
      "task_owned_files_only: true",
      "push: false",
      "preferences_never_authorize:",
      "destructive_git_history",
    ]) {
      expect(template).toContain(contract);
    }
  });

  it("persists structural defaults, enforcement truth, and legacy policy", () => {
    for (const contract of [
      "selection_mode:",
      "measurement: physical_lines",
      "initialization_notice:",
      "enforcement_status:",
      "enforcement_commands:",
      "role_profiles:",
      "exclusions:",
      "legacy_violation_policy:",
      "user_confirmation_required_for_technical_defaults: false",
    ]) {
      expect(template).toContain(contract);
    }
  });

  it("treats structural enforcement as an executable pre-write and test gate", () => {
    expect(template).toContain("npm run check");
    expect(template).toContain("Structural Change Forecast");
    expect(template).toMatch(/responsibility seam/i);
    expect(template).toMatch(/mechanical\s+line\s+splitting/i);
  });

  it("allows partial attachment while fail-closing automatic work", () => {
    expect(template).toContain("schema: granoflow_project_work_v1");
    expect(template).toContain("document_gate: partial_allowed");
    expect(template).toContain("document_gate: dependency_fields_only");
    expect(template).toContain("document_gate: complete_confirmed_current");
    expect(template).toContain("project_document_incomplete");
    expect(template).toContain("create_milestone_automatically");
    expect(template).toContain("execute_task_automatically");
    expect(template).toContain("complete_task_automatically");
    expect(template).toContain("complete_project_automatically");
    expect(template).toContain("publish_automatically");
    expect(template).toContain("deploy_automatically");
    expect(template).toContain("unconfirmed_inference_may_unlock_automation: false");
    expect(template).toContain("unknown_fields: preserve");
    expect(template).toContain("validation_owner: granoflow_app_action_aware_v1");
    expect(template).toContain("unknown_future_schema: fail_closed");
    expect(template).toContain("completed_requires_final_app_api_readback: true");
  });

  it("requires versioned authorization recovery evidence and App-owned readback", () => {
    for (const contract of [
      "confirmed_document_version",
      "confirmed_content_sha256",
      "app_confirmation_metadata_owner",
      "external_capabilities:",
      "no_progress_policy:",
      "optimistic_revision_policy",
      "recovery_fingerprint",
      "cross_milestone_integration_evidence",
      "final_app_api_readback",
      "reopened",
    ]) {
      expect(template).toContain(contract);
    }
    expect(template).toMatch(/the App and Local HTTP API own/i);
    expect(template).toContain("MCP remains a thin interface");
    expect(template).toMatch(/must still\s+fail closed/);
    expect(template).toContain("never authorizes code");
    expect(template).toMatch(/Never store tokens,[\s\S]*credential values/);
    expect(template).not.toContain("confirmed_attachment_sha256:");
    expect(template).toContain("doing so would change the");
  });

  it("treats Project Work as living context at completion and commit gates", () => {
    expect(template).toContain("living project contract");
    expect(template).toContain("before a commit that");
    expect(template).toContain("Never restore code to satisfy a stale Project Work rule");
    expect(template).toContain("A mismatch must be reported as a document");
  });

  it("documents holistic milestone portfolio planning under milestone_strategy", () => {
    expect(template).toMatch(/plan ALL milestones in[\s#\n]*one pass/);
    expect(template).toContain("amend only for real coverage gaps");
    expect(template).toContain("Design Baseline + App Shell");
    expect(template).toContain("Entities for later milestones may still be created while inactive");
    expect(template).toContain("active_milestone_limit: 1");
  });

  it("declares data persistence and project-owned data attachments", () => {
    for (const contract of [
      "data_persistence:",
      "no_database_declaration:",
      "data_model_attachment:",
      "json_contracts_attachment:",
      "constants_catalog_attachment:",
      "code_must_match_data_attachments: true",
      "logical_slot: json_contracts",
      "logical_slot: constants_catalog",
      "data_artifact_stale",
      "data-contracts.yaml",
      "constants-catalog.yaml",
    ]) {
      expect(template).toContain(contract);
    }
    expect(template).toMatch(/本项目无业务数据库，无需设计表结构/);
    expect(template).toMatch(/Do NOT embed[\s\S]*full field schemas/i);
  });

  it("requires capability-critical dependency selection fields", () => {
    for (const contract of [
      "capability-critical third-party library",
      "capability_critical: true",
      "alternatives_considered: []",
      "selection_rationale: null",
      "no_capability_dependency_declaration: null",
      "capability_dependency_unselected",
    ]) {
      expect(template).toContain(contract);
    }
    expect(template).toMatch(/Framework choice alone[\s\S]*not enough/i);
  });
});
