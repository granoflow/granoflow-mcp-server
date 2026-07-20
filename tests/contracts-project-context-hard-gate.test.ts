import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const context = readFileSync(
  "skills/granoflow-agent-workflow/references/project-context-attachments.md",
  "utf8",
);
const workflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-workflow.md",
  "utf8",
);
const template = readFileSync(
  "skills/granoflow-agent-workflow/references/task-work-document-template.md",
  "utf8",
);
const delivery = readFileSync(
  "skills/granoflow-agent-workflow/references/task-delivery-profile-software-development.md",
  "utf8",
);
const deliveryWorkflow = readFileSync(
  "skills/granoflow-agent-workflow/references/task-delivery-workflow.md",
  "utf8",
);
const unattended = readFileSync(
  "skills/granoflow-agent-workflow/references/unattended-interaction-contract.md",
  "utf8",
);
const agentSkill = readFileSync("skills/granoflow-agent-workflow/SKILL.md", "utf8");
const orchestrator = readFileSync("skills/granoflow-task-orchestrator/SKILL.md", "utf8");

describe("project context hard gate contracts", () => {
  it("requires pre-edit snapshot/rules check with interactive confirm or unattended decision notice", () => {
    expect(context).toContain("Hard Gate: Pre-Change Conflict Check");
    for (const code of [
      "project_context_check_missing",
      "project_context_conflict_unconfirmed",
      "project_context_decision_not_emitted",
      "project_context_check_unreconciled",
    ]) {
      expect(context).toContain(code);
      expect(delivery).toContain(code);
      expect(deliveryWorkflow).toContain(code);
    }
    expect(context).toContain("revise_code");
    expect(context).toContain("revise_context_yaml");
    expect(context).toMatch(/\*\*Interactive:\*\*[\s\S]*user confirmation/i);
    expect(context).toMatch(/\*\*Unattended:\*\*[\s\S]*explicit notice naming the\s+decision/i);

    expect(template).toContain("project_context_check_status:");
    expect(template).toContain("project_context_resolution:");
    expect(template).toContain("project_context_decision_emitted:");

    expect(workflow).toContain("Project context");
    expect(workflow).toContain("project_context_decision_not_emitted");
    expect(workflow).toContain("project_context_check_missing");

    expect(unattended).toMatch(/project_context_resolution/i);
    expect(unattended).toMatch(/do not consume the budget/i);

    expect(agentSkill).toContain("project-context-attachments.md");
    expect(agentSkill).toContain("revise_context_yaml");
    expect(orchestrator).toContain("project_context_check_missing");
    expect(orchestrator).toContain("project_context_decision_not_emitted");
  });
});
