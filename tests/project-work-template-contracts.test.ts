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
    ]) {
      expect(template).toContain(designLock);
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
});
