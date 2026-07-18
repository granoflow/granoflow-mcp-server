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

describe("project definition bundled workflow", () => {
  it("supports both interaction modes through one project_work slot", () => {
    expect(skill).toContain("guided_step_by_step");
    expect(skill).toContain("guided_from_vague_request");
    expect(skill).toContain("one `project_work` logical slot");
    expect(skill).toContain("project_document_incomplete");
    expect(skill).toContain("granoflow_project_work_confirm");
  });

  it("requires recommendation provenance and protects subjective decisions", () => {
    expect(interaction).toContain("recommended_value");
    expect(interaction).toContain("source:");
    expect(interaction).toContain("batch_accept_eligible");
    expect(interaction).toContain("never silently batch");
  });

  it("selects software structural limits at init without another confirmation", () => {
    expect(interaction).toContain("granoflow-agent-workflow/software-structural-budget");
    expect(interaction).toMatch(/choose them automatically/i);
    expect(interaction).toMatch(/do not ask for confirmation/i);
    expect(interaction).toContain("recorded_pending_enforcement");
    expect(interaction).toMatch(/not the `Initialize Granoflow` first-run flow/i);
  });

  it("locks one coherent project design and exact App-owned baseline", () => {
    expect(skill).toContain("granoflow_product_builder_v1");
    expect(skill).toContain("capability_pack_not_ready");
    expect(skill).toContain("granoflow_project_design_baseline_import");
    expect(skill).toContain("granoflow_project_design_baseline_read");
    expect(skill).toContain("one visual decision");
    expect(skill).toContain("design_profile");
    expect(skill).toContain("skill_routing");
    expect(skill).toContain("prototype_template");
    expect(interaction).toContain("Automatic Design Proposal Contract");
    expect(interaction).toMatch(/Never turn the proposal into a menu of[\s\S]*Skills/i);
    expect(artifacts).toContain("Project Design Baseline Prototype");
    expect(artifacts).toContain('Never resolve "current" or "latest"');
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
  });
});
