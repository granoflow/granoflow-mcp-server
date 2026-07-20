import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const skill = readFileSync("skills/granoflow-milestone-workflow/SKILL.md", "utf8");
const creation = readFileSync(
  "skills/granoflow-milestone-workflow/references/milestone-portfolio-creation.md",
  "utf8",
);
const toolRegistration = readFileSync("src/tool-registration-foundation.ts", "utf8");

describe("milestone workflow contracts (create-only)", () => {
  it("hard-gates entry on Project Work and frontend Design Baseline plus App Shell", () => {
    expect(skill).toContain("Entry Prerequisites (Hard Gate)");
    expect(skill).toContain("project_milestone_prerequisites_incomplete");
    expect(skill).toContain("granoflow-project-definition");
    expect(skill).toContain("Frontend Detection");
    expect(skill).toContain("Design Baseline");
    expect(skill).toContain("App Shell");
  });

  it("supports single and batch milestone create and stops before tasks", () => {
    expect(skill).toContain("single_create");
    expect(skill).toContain("batch_create");
    expect(skill).toMatch(/Does\s+\*\*not\*\*[\s\S]*create child tasks/i);
    expect(skill).toContain("granoflow-task-authoring");
    expect(skill).toContain("granoflow-portfolio-orchestrator");
    expect(skill).toContain("granoflow-milestone-coordination");
    expect(creation).toContain("Empty Versus Existing");
    expect(creation).toContain("First Ship");
    expect(creation).toContain("create every milestone entity");
    expect(creation).toMatch(/Do not create tasks here/i);
  });

  it("plans the full portfolio when empty and amends only for gaps", () => {
    expect(skill).toMatch(/Empty portfolio:[\s\S]*entire[\s\S]*milestone set/i);
    expect(skill).toContain("active_milestone_limit");
    expect(skill).toMatch(/Existing portfolio:[\s\S]*Do \*\*not\*\* rebuild/i);
    expect(toolRegistration).toContain("granoflow_milestone_workflow_skill");
    expect(toolRegistration).toMatch(/Creates milestones singly or in batch/i);
  });
});
