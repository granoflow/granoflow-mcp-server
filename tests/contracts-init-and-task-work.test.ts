import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const reference = (name: string) =>
  readFileSync(`skills/granoflow-agent-workflow/references/${name}`, "utf8");

// eslint-disable-next-line max-lines-per-function
describe("contracts-init-and-task-work", () => {
  // eslint-disable-next-line max-lines-per-function
  it("initializes Granoflow with one beginner-facing all-recommended Skill offer", () => {
    const onboarding = readFileSync("skills/granoflow-first-run-import/SKILL.md", "utf8");
    const catalog = readFileSync(
      "skills/granoflow-first-run-import/references/recommended-external-skills.md",
      "utf8",
    );

    expect(onboarding).toContain("Initialize Granoflow");
    expect(onboarding).toContain("初始化 Granoflow");
    const projectDefinition = readFileSync("skills/granoflow-project-definition/SKILL.md", "utf8");
    expect(projectDefinition).toContain("Initialize this project");
    expect(projectDefinition).toMatch(/Not this Skill:[\s\S]*Initialize Granoflow/i);
    expect(projectDefinition).toContain("granoflow-first-run-import");
    expect(projectDefinition).toMatch(/Never route project definition through first-run import/i);
    expect(onboarding).toContain("recommended-external-skills.md");
    expect(onboarding).toContain("approved_all");
    expect(onboarding).toContain("capability_pack_not_ready");
    expect(onboarding).toMatch(/Ask exactly once/i);
    expect(onboarding).toMatch(/does not run[\s\S]*setup-matt-pocock-skills/i);

    for (const capability of [
      "Grill Finalizer",
      "Grill Me",
      "gstack",
      "Matt Pocock Skills",
      "Huashu Design",
      "Impeccable",
      "Apple Design",
      "GSAP Skills",
      "Baoyu Skills",
    ]) {
      expect(catalog).toContain(capability);
    }
    expect(catalog).toContain("granoflow_product_builder_v1");
    expect(catalog).toContain("complete recommended capability pack");
    expect(catalog).toContain("host-native confirmation");
    expect(catalog).toMatch(/runtime[\s\S]*only[\s\S]*relevant/i);
    expect(catalog).toContain("capability_pack_not_ready");

    const externalRouting = reference("external-skill-routing.md");
    expect(externalRouting).toContain("first-run onboarding contract");
    expect(externalRouting).toContain("default all-install choice");
    expect(externalRouting).toMatch(/installation breadth only[\s\S]*Runtime routing/i);
    expect(externalRouting).toContain("capability_pack_drift");
    expect(externalRouting).toMatch(/model_allowed[\s\S]*silently/i);
    expect(externalRouting).toContain("baseline | shell | later_ui");
    expect(externalRouting).toMatch(/never open a style-Skill menu/i);

    const prompt = catalog.match(/## User Prompt\n([\s\S]*?)\n## /)?.[1] ?? "";
    expect(prompt).not.toBe("");
    for (const technicalField of [
      "repository",
      "license",
      "command",
      "scope",
      "reload",
      "network",
    ]) {
      expect(prompt.toLowerCase()).not.toContain(technicalField);
    }
  });

  it("uses one adaptive pre-execution Task Work Document for new tasks", () => {
    const template = reference("task-work-document-template.md");
    const workflow = reference("task-work-document-workflow.md");
    const capture = reference("discussed-requirement-task-capture.md");

    expect(template).toContain("document_type: task_work");
    expect(template).toContain("analysis_status: draft | awaiting_confirmation | confirmed");
    expect(template).toContain(
      "planning_status: not_assessed | not_required | draft | awaiting_confirmation | confirmed",
    );
    expect(template).toContain(
      "analysis_grill_status: not_run | passed | revisions_required | blocked",
    );
    expect(template).toContain(
      "readiness_grill_status: not_run | not_applicable | passed | revisions_required | blocked",
    );
    expect(template).toContain("prototype_requirement: required | not_required | conditional");
    expect(template).toContain("package_attachment_id");
    expect(template).toContain("package_sha256");
    expect(workflow).toContain("executionAdmission.allowed");
    expect(workflow).toContain("assetMode=file");
    expect(workflow).toMatch(/no\s+greater than 600 seconds/);
    expect(workflow).toContain("contract fidelity");
    expect(workflow).toContain("granoflow_project_design_baseline_read");
    expect(workflow).toContain("derivedFrom");
    expect(workflow).toContain("UI Change Prototype Mandate");
    expect(workflow).toContain("ui_prototype_required");
    expect(workflow).toMatch(/prototype_requirement[\s\S]*must[\s\S]*required/i);
    expect(workflow).toMatch(/Do \*\*not\*\* use `not_required`/i);
    expect(template).toContain("UI change => required");
    expect(template).toContain("derived_from_package_sha256");
    expect(template).toContain("ui_prototype_required");
    expect(template).toContain("prototype_option_set:");
    expect(template).toContain("interactive_dual");
    expect(template).toContain("task_prototype_craft_incomplete");
    expect(template).toContain("industry_peer_c");
    expect(template).not.toContain("execution_status:");
    expect(template).toContain("pre-execution governance document");
    expect(template).toContain("five-\ndimension prose contract");
    expect(capture).toContain("Mandatory Description Standard");
    expect(capture).toContain("Title Standard");
    expect(capture).toContain("action verb + clear object or outcome");
    expect(capture).toContain("Do not make `Plan文档`");
    expect(capture).toContain("fluent, readable piece of task copy");
    expect(capture).toContain("not a\nquestionnaire");
    expect(capture).toContain("optional");
    expect(capture).toContain("evidence-based basis");
    expect(capture).not.toContain("Every task description must contain these five headings");
    expect(capture).toContain("历史工时未知");
    for (const core of ["Outcome", "Evidence", "Scope", "Risk", "Next Action"]) {
      expect(template).toContain(`## ${core}`);
    }
    expect(template).toContain("skill_routing: not_triggered");
    expect(template).toContain("card_checkpoint: not_triggered");
    expect(template).not.toContain("## Database / Migration");
    expect(template).not.toContain("## Execution Nodes");

    expect(workflow).toContain("Legal State Matrix");
    expect(workflow).toContain("invalid_task_work_state");
    expect(workflow).toContain("实施这个任务文档");
    expect(workflow).toContain("does not authorize execution");
    expect(workflow).toMatch(/complete, self-contained\s+checkpoint/);
    expect(workflow).toMatch(/App-owned content and\s+SHA-256/);
  });

  it("uses one task authoring quality contract across every creation route", () => {
    const contract = reference("task-authoring-quality-contract.md");
    const routeFiles = [
      "skills/granoflow-agent-workflow/references/discussed-requirement-task-capture.md",
      "skills/granoflow-task-orchestrator/SKILL.md",
      "skills/granoflow-milestone-coordination/references/milestone-collaboration-workflow.md",
      "skills/granoflow-task-authoring/SKILL.md",
      "skills/granoflow-project-definition/SKILL.md",
      "skills/granoflow-first-run-import/references/task-and-card-import.md",
      "skills/granoflow-delegated-authorization/references/host-routing-and-waiting.md",
    ];

    expect(contract).toContain("single semantic owner");
    expect(contract).toContain("non-programmer");
    expect(contract).toContain("one real analogy");
    expect(contract).toContain("one concrete example");
    expect(contract).toContain("task_authoring_quality_failed");
    expect(contract).toContain("old complete text");
    expect(contract).toContain("HTML prototype");
    expect(contract).toContain("Mandatory prototype");
    expect(contract).toMatch(/prototype_requirement: required/i);
    expect(contract).toMatch(/Do not mark `not_required` for a UI/i);
    expect(contract).toContain("two-dimensional Markdown table");
    expect(contract).toContain("bold formatting on every changed field");
    expect(contract).toContain("Mermaid flowchart");
    expect(contract).toContain("at most one such Markdown file per task");
    expect(contract).toContain("Human title-only quick capture");
    for (const path of routeFiles) {
      expect(readFileSync(path, "utf8")).toContain(
        "granoflow-agent-workflow/task-authoring-quality-contract",
      );
    }
  });
});
