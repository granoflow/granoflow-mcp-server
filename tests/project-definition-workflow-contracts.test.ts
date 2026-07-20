import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const skill = readFileSync("skills/granoflow-project-definition/SKILL.md", "utf8");
const interaction = readFileSync(
  "skills/granoflow-project-definition/references/project-definition-interaction.md",
  "utf8",
);
const artifacts = readFileSync(
  "skills/granoflow-project-definition/references/project-artifact-workflows.md",
  "utf8",
);
const openaiYaml = readFileSync(
  "skills/granoflow-project-definition/agents/openai.yaml",
  "utf8",
);

describe("project definition bundled workflow", () => {
  it("supports both interaction modes through one project_work slot", () => {
    expect(skill).toContain("guided_step_by_step");
    expect(skill).toContain("guided_from_vague_request");
    expect(skill).toContain("one `project_work` logical slot");
    expect(skill).toContain("project_document_incomplete");
    expect(skill).toContain("granoflow_project_work_confirm");
  });

  it("activates on define/initialize-this-project phrases and not Initialize Granoflow", () => {
    expect(skill).toContain("Initialize this project");
    expect(skill).toContain("Define this project");
    expect(skill).toContain("初始化这个项目");
    expect(skill).toContain("定义这个项目");
    expect(skill).toMatch(/Not this Skill:[\s\S]*Initialize Granoflow/i);
    expect(skill).toContain("granoflow-first-run-import");
    expect(openaiYaml).toContain("Initialize this project");
    expect(openaiYaml).toContain("Not Initialize Granoflow");
    expect(interaction).toContain("Activation Boundary");
    expect(interaction).toContain("Initialize Granoflow");
  });

  it("requires three-step initialization with App Shell and stack capability first", () => {
    expect(skill).toContain("Three-Step Initialization Outcome");
    expect(skill).toContain("Step 1 — Project Work");
    expect(skill).toContain("Step 2 — Design Baseline + Design Tokens");
    expect(skill).toContain("Step 3 — App Shell");
    expect(skill).toContain("stack_capability_profile");
    expect(skill).toMatch(/before any HTML baseline/i);
    expect(skill).toContain("token_sources");
    expect(skill).toContain("landscape and portrait App Shell");
    expect(skill).toMatch(/Missing Shell[\s\S]*Done/i);
    expect(artifacts).toContain("Project Design Baseline Package");
    expect(artifacts).toContain("Landscape App Shell");
    expect(artifacts).toContain("Portrait App Shell");
    expect(artifacts).toContain('Never resolve "current" or "latest"');
  });

  it("states contract fidelity, enhanced implementation, and baseline authority", () => {
    expect(skill).toContain("contract fidelity");
    expect(skill).toContain("契约级一致");
    expect(skill).toContain("【增强实现】");
    expect(skill).toContain("implementation_notes");
    expect(skill).toMatch(/authoritative[\s\S]*reference/i);
    expect(artifacts).toContain("derivedFrom");
    expect(artifacts).toContain("contract fidelity");
    expect(artifacts).toContain("【增强实现】");
  });

  it("requires recommendation provenance; unattended adopts recommendations", () => {
    expect(interaction).toContain("recommended_value");
    expect(interaction).toContain("source:");
    expect(interaction).toContain("batch_accept_eligible");
    expect(interaction).toContain("never silently batch");
    expect(interaction).toMatch(/Unattended mode:[\s\S]*adopt `recommended_value` immediately/i);
    expect(interaction).toContain("auto_accept_recommendation");
    expect(skill).toContain("auto_accept_recommendation");
    expect(skill).toMatch(/unattended[\s\S]*adopt recommendations immediately/i);
  });

  it("selects software structural limits at init without another confirmation", () => {
    expect(interaction).toContain("granoflow-agent-workflow/software-structural-budget");
    expect(interaction).toMatch(/choose them automatically/i);
    expect(interaction).toMatch(/do not ask for confirmation/i);
    expect(interaction).toContain("recorded_pending_enforcement");
    expect(interaction).toMatch(/not the `Initialize Granoflow` first-run flow/i);
  });

  it("locks one coherent project design and exact App-owned baseline package", () => {
    expect(skill).toContain("granoflow_product_builder_v1");
    expect(skill).toContain("capability_pack_not_ready");
    expect(skill).toContain("granoflow_project_design_baseline_import");
    expect(skill).toContain("granoflow_project_design_baseline_read");
    expect(skill).toContain("Baseline+Shell");
    expect(skill).toContain("design_profile");
    expect(skill).toContain("skill_routing");
    expect(skill).toContain("prototype_template");
    expect(interaction).toContain("Automatic Design Proposal Contract");
    expect(interaction).toMatch(/Never turn the proposal into a menu of[\s\S]*Skills/i);
    expect(interaction).toContain("phase");
    expect(interaction).toContain("baseline");
    expect(interaction).toContain("shell");
    expect(interaction).toContain("later_ui");
  });

  it("ends with Done checklist and milestone/task handoff", () => {
    expect(skill).toContain("Done And Handoff");
    expect(skill).toContain("handoff card");
    expect(skill).toContain("granoflow-portfolio-orchestrator");
    expect(skill).toContain("granoflow-milestone-workflow");
    expect(skill).toContain("granoflow-task-authoring");
    expect(skill).toContain("granoflow-milestone-coordination");
    expect(skill).toContain("granoflow-task-orchestrator");
    expect(skill).toMatch(/full\s+milestone\/task tree/i);
    expect(skill).toMatch(/does\s+\*\*not\*\*/i);
  });

  it("keeps prototype, data model, and workflow artifacts in fixed slots", () => {
    expect(artifacts).toContain("`ui_prototype`");
    expect(artifacts).toContain("`data_model`");
    expect(artifacts).toContain("`workflows`");
    expect(artifacts).toContain("two-dimensional Markdown table");
    expect(artifacts).toContain("stable id");
    expect(artifacts).toContain("Artifact Registry");
    expect(artifacts).toContain("package_prototype.py");
    expect(artifacts).toContain("visualConfirmed=true");
    expect(artifacts).toMatch(/task changes UI[\s\S]*mandatory/i);
    expect(artifacts).toMatch(/Missing `derivedFrom`[\s\S]*fails closed/i);
  });

  it("requires Step 1 data persistence declaration and attachment slots", () => {
    expect(skill).toContain("data_persistence");
    expect(skill).toContain("no_database_declaration");
    expect(skill).toContain("json_contracts");
    expect(skill).toContain("constants_catalog");
    expect(skill).toContain("data-contracts.yaml");
    expect(skill).toContain("constants-catalog.yaml");
    expect(skill).toMatch(
      /Done And Handoff[\s\S]*`data_persistence` is set/i,
    );
    expect(artifacts).toContain("Data Persistence And Structured Contracts");
    expect(artifacts).toContain("data_artifact_stale");
    expect(artifacts).toMatch(/本项目无业务数据库，无需设计表结构/);
    expect(artifacts).toContain("`json_contracts`");
    expect(artifacts).toContain("`constants_catalog`");
    expect(interaction).toContain("Data Persistence Recommendation Batch");
    expect(interaction).toContain("data_persistence");
    expect(interaction).toContain("no_database_declaration");
  });

  it("requires Step 1 capability-critical library selection after stack", () => {
    expect(skill).toContain("capability-critical third-party library selection");
    expect(skill).toContain("capability_dependency_unselected");
    expect(skill).toContain("alternatives_considered");
    expect(skill).toContain("no_capability_dependency_declaration");
    expect(skill).toMatch(
      /Done And Handoff[\s\S]*capability-critical third-party libraries are selected/i,
    );
    expect(skill).toMatch(
      /stack capability → capability-critical libraries →/i,
    );
    expect(interaction).toContain(
      "Capability-Critical Dependency Recommendation Batch",
    );
    expect(interaction).toMatch(/immediately after[\s\S]*engineering\.stack/i);
    expect(interaction).toContain("capability_dependency_unselected");
    expect(artifacts).toContain("Capability-Critical Dependencies");
    expect(artifacts).toContain("capability_dependency_unselected");
  });
});
