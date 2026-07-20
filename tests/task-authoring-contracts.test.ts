import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const skill = readFileSync("skills/granoflow-task-authoring/SKILL.md", "utf8");
const modes = readFileSync(
  "skills/granoflow-task-authoring/references/task-authoring-modes.md",
  "utf8",
);
const toolRegistration = readFileSync("src/tool-registration-foundation.ts", "utf8");

describe("task authoring contracts", () => {
  it("requires quality contract and create_one batch size 1", () => {
    expect(skill).toContain("task-authoring-quality-contract");
    expect(skill).toContain("create_one");
    expect(skill).toContain("batch_skeleton");
    expect(skill).toContain("batch_create");
    expect(skill).toMatch(/Full description batch size is \*\*1\*\*/i);
    expect(skill).toMatch(/Never emit[\s\S]*multiple complete descriptions/i);
    expect(modes).toContain("create_one Protocol");
    expect(modes).toContain("Forbidden:");
    expect(modes).toMatch(/multiple complete task[\s\S]*descriptions/i);
  });

  it("requires skeleton coverage before create loops", () => {
    expect(modes).toContain("Coverage Check");
    expect(modes).toContain("task_portfolio_coverage_incomplete");
    expect(modes).toContain("acceptance_ids");
    expect(skill).toMatch(/coverage\s+check/i);
  });

  it("does not own Analysis or execution", () => {
    expect(skill).toMatch(/does\s+\*\*not\*\*[\s\S]*Analysis/i);
    expect(skill).toContain("granoflow-task-orchestrator");
    expect(toolRegistration).toContain("granoflow_task_authoring_skill");
    expect(toolRegistration).toMatch(/create_one loops/i);
  });
});
