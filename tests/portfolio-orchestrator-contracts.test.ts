import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const skill = readFileSync("skills/granoflow-portfolio-orchestrator/SKILL.md", "utf8");
const contract = readFileSync(
  "skills/granoflow-portfolio-orchestrator/references/portfolio-orchestration-contract.md",
  "utf8",
);
const toolRegistration = readFileSync("src/tool-registration-foundation.ts", "utf8");

describe("portfolio orchestrator contracts", () => {
  it("orchestrates milestone create then per-milestone task authoring", () => {
    expect(skill).toContain("granoflow-milestone-workflow");
    expect(skill).toContain("granoflow-task-authoring");
    expect(skill).toContain("batch_create");
    expect(skill).toContain("batch_skeleton");
    expect(skill).toContain("create_one");
    expect(skill).toContain("first_ship");
    expect(skill).toContain("Portfolio Ready");
  });

  it("forbids collapsing many full descriptions into one turn", () => {
    expect(skill).toMatch(/Never merge multiple full task descriptions/i);
    expect(contract).toContain("Forbidden Collapses");
    expect(contract).toMatch(/many complete task descriptions/i);
    expect(contract).toContain("Portfolio Ready");
    expect(contract).toContain("milestones_created");
    expect(contract).toContain("current_milestone_id");
  });

  it("hands off coordination and task lifecycle after Portfolio Ready", () => {
    expect(skill).toContain("granoflow-milestone-coordination");
    expect(skill).toContain("granoflow-task-orchestrator");
    expect(toolRegistration).toContain("granoflow_portfolio_orchestrator_skill");
    expect(toolRegistration).toMatch(/Portfolio Ready/i);
  });
});
